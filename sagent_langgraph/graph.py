"""Main LangGraph agent graph construction.

This module builds the complete multi-agent graph with proper routing
and state management. Equivalent to the ADK agent setup.
"""

import logging
from typing import Any

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver

from state import KnowseeState
from agents.root import create_root_agent
from agents.search import create_search_agent
from agents.rag import create_rag_agent
from agents.data_analyst import create_data_analyst

logger = logging.getLogger(__name__)


def should_continue(state: KnowseeState) -> str:
    """Routing function to determine next node.

    Args:
        state: The current graph state.

    Returns:
        The name of the next node to execute, or END.
    """
    next_agent = state.get("next_agent")

    if next_agent == "search_agent":
        return "search_agent"
    elif next_agent == "rag_agent":
        return "rag_agent"
    elif next_agent == "data_analyst":
        return "data_analyst"
    else:
        # No delegation needed, end the conversation turn
        return END


def create_knowsee_graph(database_url: str | None = None) -> Any:
    """Create the complete Knowsee agent graph.

    This builds a multi-agent system with:
    - Root agent (orchestrator)
    - Search agent (web search)
    - RAG agent (team knowledge)
    - Data analyst agent (BigQuery + visualizations)

    Args:
        database_url: Optional PostgreSQL connection string for persistence.

    Returns:
        Compiled LangGraph application ready to invoke.
    """
    logger.info("[create_graph] Building Knowsee LangGraph agent")

    # Create the state graph
    graph = StateGraph(KnowseeState)

    # Add nodes
    graph.add_node("root_agent", create_root_agent())
    graph.add_node("search_agent", create_search_agent())
    graph.add_node("rag_agent", create_rag_agent())
    graph.add_node("data_analyst", create_data_analyst())

    # Set entry point
    graph.set_entry_point("root_agent")

    # Add conditional routing from root agent
    graph.add_conditional_edges(
        "root_agent",
        should_continue,
        {
            "search_agent": "search_agent",
            "rag_agent": "rag_agent",
            "data_analyst": "data_analyst",
            END: END,
        },
    )

    # All sub-agents return to root for synthesis
    graph.add_edge("search_agent", "root_agent")
    graph.add_edge("rag_agent", "root_agent")
    graph.add_edge("data_analyst", "root_agent")

    # Compile with optional persistence
    checkpointer = None
    if database_url:
        try:
            # Use PostgreSQL checkpointer for session persistence
            checkpointer = PostgresSaver.from_conn_string(database_url)
            logger.info("[create_graph] PostgreSQL checkpointer configured")
        except Exception as e:
            logger.warning(f"[create_graph] Failed to create checkpointer: {e}")

    app = graph.compile(checkpointer=checkpointer)

    logger.info("[create_graph] Knowsee graph compiled successfully")
    return app


def get_initial_state(user_id: str, session_id: str) -> KnowseeState:
    """Create initial state for a new session.

    Args:
        user_id: The authenticated user ID.
        session_id: The session identifier.

    Returns:
        Initial state dict with defaults.
    """
    return {
        "messages": [],
        "user_id": user_id,
        "user_teams": None,
        "user_corpora": None,
        "_user_context_loaded": False,
        "artifacts": None,
        "pending_artifact_ids": None,
        "session_id": session_id,
        "session_title": None,
        "_title_generated": False,
        "query_attempts": [],
        "pending_widgets": [],
        "grounding_metadata": [],
        "thoughts": [],
        "next_agent": None,
        "iteration_count": 0,
    }
