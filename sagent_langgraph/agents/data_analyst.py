"""Data analyst agent for BigQuery queries and visualizations.

This module provides data analytics capabilities with chart/widget creation.
Equivalent to the ADK data_analyst_agent.
"""

import logging
import os
import re
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any
from uuid import uuid4

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from google.cloud import bigquery

from state import KnowseeState

logger = logging.getLogger(__name__)

# Data analyst instruction
DATA_ANALYST_INSTRUCTION = """You are a data analyst specialist. Your role is to query BigQuery datasets and create visualizations.

When given a data request:
1. List available datasets and tables to understand what's available
2. Describe table schemas to understand column types and structure
3. Write efficient SQL queries to retrieve the requested data
4. Create appropriate visualizations (charts) for the results
5. Provide insights from the data

Always use fully-qualified table names (project.dataset.table) in your queries.
For visualizations, choose the most appropriate chart type based on the data."""

# Display limit for tabular view
TABLE_DISPLAY_LIMIT = 1000


def _to_json_safe(value: Any) -> Any:
    """Convert BigQuery values to JSON-serializable types."""
    if value is None:
        return None
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, time):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, (list, tuple)):
        return [_to_json_safe(v) for v in value]
    if isinstance(value, dict):
        return {k: _to_json_safe(v) for k, v in value.items()}
    return value


def _row_to_json_safe(row: Any) -> list:
    """Convert a BigQuery row to JSON-serializable list."""
    return [_to_json_safe(v) for v in row.values()]


def _suggest_chart_type(
    columns: list[dict], row_count: int, rows: list[list] | None = None
) -> str:
    """Suggest chart type based on result shape and data characteristics."""
    if row_count == 1 and len(columns) == 1:
        return "metric"

    if len(columns) < 2:
        return "table"

    first_col_type = columns[0].get("type", "").upper()

    # Time-series data → line chart
    if first_col_type in ("DATE", "TIMESTAMP", "DATETIME"):
        return "line"

    # Small categorical data → pie chart
    if row_count <= 7 and len(columns) == 2:
        return "pie"

    # Check for long text strings → table
    if first_col_type in ("STRING", "BYTES") and rows and len(rows) > 0:
        sample_values = [row[0] for row in rows[:20] if row[0] is not None]
        if sample_values:
            avg_len = sum(len(str(v)) for v in sample_values) / len(sample_values)
            if avg_len > 30:
                return "table"

    return "bar"


def _get_client() -> bigquery.Client:
    """Get BigQuery client with project from environment."""
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable required")
    return bigquery.Client(project=project)


@tool
async def query_data(query: str, title: str = "") -> dict[str, Any]:
    """Execute a BigQuery SQL query and create a visualization widget.

    Args:
        query: SQL query string with fully-qualified table names.
        title: Optional title for the chart widget.

    Returns:
        Query results with widget metadata.
    """
    try:
        client = _get_client()
        logger.info(f"Executing BigQuery: {query[:200]}...")

        query_job = client.query(query)
        result = query_job.result()

        # Extract schema
        columns = [
            {"name": field.name, "type": field.field_type} for field in result.schema
        ]

        # Fetch all rows
        rows = [_row_to_json_safe(row) for row in result]
        total_rows = len(rows)

        suggested_chart = _suggest_chart_type(columns, total_rows, rows)
        bytes_processed = query_job.total_bytes_processed or 0

        logger.info(
            f"Query complete: {total_rows} rows, "
            f"{bytes_processed / 1024**3:.2f} GB processed"
        )

        # Create widget metadata
        widget_id = str(uuid4())
        widget = {
            "id": widget_id,
            "title": title if title else f"Query Result ({total_rows} rows)",
            "chart_type": suggested_chart,
            "data": {
                "columns": [c["name"] for c in columns],
                "rows": rows,
            },
            "query": query,
            "total_rows": total_rows,
            "bytes_processed": bytes_processed,
        }

        return {
            "success": True,
            "widget": widget,
            "row_count": total_rows,
            "suggested_chart": suggested_chart,
        }

    except Exception as e:
        logger.exception(f"Query execution failed: {e}")
        return {
            "error": f"Query failed: {str(e)}",
            "success": False,
        }


@tool
async def list_datasets() -> dict[str, Any]:
    """List BigQuery datasets accessible to the application.

    Returns:
        List of accessible datasets with their tables.
    """
    try:
        client = _get_client()
        project = os.getenv("GOOGLE_CLOUD_PROJECT")

        datasets = []
        for dataset in client.list_datasets():
            dataset_id = dataset.dataset_id
            tables = []

            try:
                for table in client.list_tables(dataset.reference):
                    tables.append(
                        {
                            "table_id": f"{project}.{dataset_id}.{table.table_id}",
                            "type": table.table_type,
                        }
                    )
            except Exception as e:
                logger.warning(f"Could not list tables in {dataset_id}: {e}")

            datasets.append(
                {
                    "dataset_id": dataset_id,
                    "full_id": f"{project}.{dataset_id}",
                    "tables": tables,
                }
            )

        return {
            "success": True,
            "project": project,
            "datasets": datasets,
        }

    except Exception as e:
        logger.exception(f"Failed to list datasets: {e}")
        return {
            "error": f"Failed to list datasets: {e!s}",
            "success": False,
        }


@tool
async def describe_table(table_id: str) -> dict[str, Any]:
    """Get detailed schema for a specific BigQuery table.

    Args:
        table_id: Full table ID (project.dataset.table).

    Returns:
        Table schema with column types and sample data.
    """
    try:
        parts = table_id.split(".")
        if len(parts) != 3:
            return {
                "error": f"Invalid table_id format. Expected 'project.dataset.table'",
                "success": False,
            }

        project, dataset, table = parts
        client = _get_client()

        # Get schema
        schema_query = f"""
            SELECT column_name, data_type, is_nullable
            FROM `{project}.{dataset}.INFORMATION_SCHEMA.COLUMNS`
            WHERE table_name = '{table}'
            ORDER BY ordinal_position
        """

        schema_job = client.query(schema_query)
        schema_result = schema_job.result()

        columns = [
            {
                "name": row.column_name,
                "type": row.data_type,
                "nullable": row.is_nullable == "YES",
            }
            for row in schema_result
        ]

        # Get sample data
        sample_query = f"SELECT * FROM `{table_id}` LIMIT 5"
        sample_job = client.query(sample_query)
        sample_result = sample_job.result()

        sample_columns = [field.name for field in sample_result.schema]
        sample_rows = [_row_to_json_safe(row) for row in sample_result]

        return {
            "success": True,
            "table_id": table_id,
            "columns": columns,
            "sample_data": {
                "columns": sample_columns,
                "rows": sample_rows,
            },
        }

    except Exception as e:
        logger.exception(f"Failed to describe table {table_id}: {e}")
        return {
            "error": f"Failed to describe table: {e!s}",
            "success": False,
        }


@tool
async def create_chart(
    title: str,
    columns: list[str],
    rows: list[list],
    chart_type: str = "",
) -> dict[str, Any]:
    """Create a chart widget from pre-structured data.

    Args:
        title: Human-readable title for the chart.
        columns: List of column names.
        rows: List of rows (each row is a list of values).
        chart_type: Optional chart type ("bar", "line", "pie", "table", "metric").

    Returns:
        Widget metadata including assigned widget ID and chart type.
    """
    valid_types = {"bar", "line", "pie", "table", "metric"}

    if not columns or not rows:
        return {"success": False, "error": "columns and rows must be non-empty"}

    col_schema = [{"name": c, "type": "STRING"} for c in columns]

    if chart_type and chart_type in valid_types:
        resolved_chart = chart_type
    else:
        resolved_chart = _suggest_chart_type(col_schema, len(rows), rows)

    widget_id = str(uuid4())
    widget = {
        "id": widget_id,
        "title": title,
        "chart_type": resolved_chart,
        "data": {
            "columns": columns,
            "rows": rows,
        },
        "total_rows": len(rows),
    }

    return {
        "success": True,
        "widget": widget,
        "row_count": len(rows),
    }


async def data_analyst_node(state: KnowseeState) -> dict[str, Any]:
    """Data analyst agent node for BigQuery queries and visualizations.

    This node handles data analytics requests including querying BigQuery
    and creating interactive charts/widgets.

    Args:
        state: The current graph state.

    Returns:
        Updated state with query results and widgets.
    """
    logger.info("[data_analyst] Processing analytics request")

    # Get the last user message
    messages = state.get("messages", [])
    if not messages:
        logger.warning("[data_analyst] No messages in state")
        return {"messages": []}

    last_message = messages[-1]
    query = last_message.content if hasattr(last_message, "content") else str(last_message)

    # Initialize LLM with tools
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",  # Pro for better SQL generation
        temperature=0.7,
        convert_system_message_to_human=True,
    )

    # Bind data analyst tools
    tools = [query_data, list_datasets, describe_table, create_chart]
    llm_with_tools = llm.bind_tools(tools)

    try:
        # Create analyst context
        analyst_messages = [
            SystemMessage(content=DATA_ANALYST_INSTRUCTION),
            HumanMessage(content=query),
        ]

        # Execute with tools
        response = await llm_with_tools.ainvoke(analyst_messages)

        # Extract widgets from tool calls if any
        widgets = []
        query_attempts = []

        if hasattr(response, "tool_calls") and response.tool_calls:
            for tool_call in response.tool_calls:
                # Track query attempts and widgets
                if tool_call["name"] == "query_data":
                    query_attempts.append(
                        {
                            "query": tool_call["args"].get("query", ""),
                            "success": True,  # Will be updated based on result
                        }
                    )

        response_content = response.content if hasattr(response, "content") else str(response)

        return {
            "messages": [AIMessage(content=response_content, name="data_analyst")],
            "pending_widgets": widgets,
            "query_attempts": query_attempts,
            "next_agent": None,
        }

    except Exception as e:
        logger.exception(f"[data_analyst] Analytics failed: {e}")
        error_msg = f"Data analytics error: {str(e)}"
        return {
            "messages": [AIMessage(content=error_msg, name="data_analyst")],
            "next_agent": None,
        }


def create_data_analyst():
    """Factory function to create the data analyst agent node.

    Returns:
        The data analyst agent node function.
    """
    return data_analyst_node
