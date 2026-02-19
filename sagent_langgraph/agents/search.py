"""Web search agent implementation using LangGraph and Google Search.

This module provides web search capabilities with grounding metadata
for citations. Equivalent to the ADK search_agent.
"""

import logging
import os
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool

from state import KnowseeState

logger = logging.getLogger(__name__)


# Search instruction
SEARCH_INSTRUCTION = """You are a web search specialist. Your role is to find current information on the internet.

When given a query:
1. Search for relevant, current information
2. Provide accurate, up-to-date answers with proper citations
3. Include source URLs for verification
4. Be concise but comprehensive

Always cite your sources clearly."""


@tool
def google_search(query: str) -> str:
    """Search the web using Google Search.

    Args:
        query: The search query.

    Returns:
        Search results with relevant information.
    """
    # Note: This is a placeholder. In the actual implementation,
    # we would use Google's custom search API or similar service.
    logger.info(f"Executing web search: {query}")
    return f"Search results for: {query}\n\nNo search implementation yet - this is a placeholder."


async def search_agent_node(state: KnowseeState) -> dict[str, Any]:
    """Search agent node for web queries.

    This node handles web search requests using Google Search grounding.
    It's invoked when the root agent delegates a web search task.

    Args:
        state: The current graph state.

    Returns:
        Updated state with search results added to messages.
    """
    logger.info("[search_agent] Processing web search request")

    # Get the last user message to search for
    messages = state.get("messages", [])
    if not messages:
        logger.warning("[search_agent] No messages in state")
        return {"messages": []}

    # Find the search query from the last message
    last_message = messages[-1]
    query = last_message.content if hasattr(last_message, "content") else str(last_message)

    # Initialize the LLM with Google Search grounding
    # Note: Google's LangChain integration supports grounding via tools
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7,
        convert_system_message_to_human=True,
    )

    # Bind the search tool
    llm_with_tools = llm.bind_tools([google_search])

    try:
        # Create the search context
        search_messages = [
            SystemMessage(content=SEARCH_INSTRUCTION),
            HumanMessage(content=f"Search for: {query}"),
        ]

        # Execute search
        response = await llm_with_tools.ainvoke(search_messages)

        # Extract response content
        response_content = response.content if hasattr(response, "content") else str(response)

        # Add response to messages
        return {
            "messages": [AIMessage(content=response_content, name="search_agent")],
            "next_agent": None,  # Return to root
        }

    except Exception as e:
        logger.exception(f"[search_agent] Search failed: {e}")
        error_msg = f"Web search error: {str(e)}"
        return {
            "messages": [AIMessage(content=error_msg, name="search_agent")],
            "next_agent": None,
        }


def create_search_agent():
    """Factory function to create the search agent node.

    Returns:
        The search agent node function.
    """
    return search_agent_node
