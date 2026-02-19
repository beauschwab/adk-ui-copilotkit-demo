"""Root agent implementation for LangGraph.

This is the main orchestrator that delegates to sub-agents (search, RAG, data analyst)
and manages the conversation flow. Equivalent to the ADK root_agent.
"""

import logging
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool

from state import KnowseeState

logger = logging.getLogger(__name__)

# Root agent instruction
ROOT_INSTRUCTION = """You are Knowsee, an enterprise knowledge assistant powered by Google AI.

You help users by:
1. Answering questions using uploaded files and documents
2. Searching the web for current information
3. Querying internal team knowledge bases
4. Analyzing business data and creating visualizations

You have access to specialized sub-agents:
- **search_agent**: For web searches and current information
- **rag_agent**: For searching internal team knowledge bases
- **data_analyst**: For querying BigQuery datasets and creating charts

You also have file tools to work with uploaded documents.

When a user asks a question:
1. Determine which specialized agent or tool is best suited
2. Delegate to that agent/tool
3. Synthesize the results into a coherent response
4. Always cite sources and provide context

Be helpful, accurate, and concise."""


@tool
def delegate_to_search() -> str:
    """Delegate the current query to the web search agent.

    Use this when the user needs current information from the internet,
    recent news, or facts that change frequently.

    Returns:
        A signal to route to the search agent.
    """
    return "Routing to search agent..."


@tool
def delegate_to_rag() -> str:
    """Delegate the current query to the team knowledge agent.

    Use this when the user asks about internal documents, company policies,
    team knowledge bases, or wants to browse available documents.

    Returns:
        A signal to route to the RAG agent.
    """
    return "Routing to team knowledge agent..."


@tool
def delegate_to_analyst() -> str:
    """Delegate the current query to the data analyst agent.

    Use this when the user wants to query databases, analyze data,
    create charts, or explore business metrics.

    Returns:
        A signal to route to the data analyst agent.
    """
    return "Routing to data analyst agent..."


async def root_agent_node(state: KnowseeState) -> dict[str, Any]:
    """Root agent node that orchestrates the conversation.

    This is the main entry point for user messages. It analyzes the request
    and either handles it directly or delegates to a specialized sub-agent.

    Args:
        state: The current graph state.

    Returns:
        Updated state with response and routing decision.
    """
    logger.info("[root_agent] Processing user message")

    # Safety check for infinite loops
    iteration_count = state.get("iteration_count", 0)
    if iteration_count > 20:
        logger.error("[root_agent] Maximum iteration count exceeded")
        return {
            "messages": [
                AIMessage(
                    content="I apologize, but I've encountered an issue and need to stop. Please try rephrasing your question."
                )
            ],
            "next_agent": None,
            "iteration_count": 0,
        }

    # Get messages
    messages = state.get("messages", [])
    if not messages:
        logger.warning("[root_agent] No messages in state")
        return {"messages": []}

    # Check if we just returned from a sub-agent
    last_message = messages[-1]
    if hasattr(last_message, "name") and last_message.name in [
        "search_agent",
        "rag_agent",
        "data_analyst",
    ]:
        # Sub-agent has responded, synthesize the final response
        logger.info(f"[root_agent] Synthesizing response from {last_message.name}")

        # Initialize LLM for synthesis
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            temperature=0.7,
            convert_system_message_to_human=True,
        )

        synthesis_messages = [
            SystemMessage(content=ROOT_INSTRUCTION),
            *messages,  # Include full conversation history
            SystemMessage(
                content="Please synthesize a final response based on the sub-agent's answer. Be clear, concise, and helpful."
            ),
        ]

        response = await llm.ainvoke(synthesis_messages)
        response_content = response.content if hasattr(response, "content") else str(response)

        return {
            "messages": [AIMessage(content=response_content)],
            "next_agent": None,
            "iteration_count": iteration_count + 1,
        }

    # New user query - determine routing
    logger.info("[root_agent] Analyzing new query for routing")

    # Initialize LLM with delegation tools
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        temperature=0.7,
        convert_system_message_to_human=True,
    )

    # Bind delegation tools
    tools = [delegate_to_search, delegate_to_rag, delegate_to_analyst]
    llm_with_tools = llm.bind_tools(tools)

    # Analyze the query
    analysis_messages = [
        SystemMessage(content=ROOT_INSTRUCTION),
        *messages,
        SystemMessage(
            content="""Analyze this query and decide if you need to delegate to a specialized agent:
            
- Use delegate_to_search() for web searches, current events, recent news
- Use delegate_to_rag() for internal documents, company knowledge, policies
- Use delegate_to_analyst() for data queries, charts, business metrics

If the query is simple (greetings, clarifications) or you can answer directly with general knowledge,
respond without delegating.

Think carefully about which tool is most appropriate."""
        ),
    ]

    try:
        response = await llm_with_tools.ainvoke(analysis_messages)

        # Check if delegation was requested via tool calls
        next_agent = None
        if hasattr(response, "tool_calls") and response.tool_calls:
            for tool_call in response.tool_calls:
                if tool_call["name"] == "delegate_to_search":
                    next_agent = "search_agent"
                    break
                elif tool_call["name"] == "delegate_to_rag":
                    next_agent = "rag_agent"
                    break
                elif tool_call["name"] == "delegate_to_analyst":
                    next_agent = "data_analyst"
                    break

        if next_agent:
            logger.info(f"[root_agent] Delegating to {next_agent}")
            # Add a routing message
            return {
                "messages": [
                    AIMessage(
                        content=f"Let me check that for you...", name="root_agent"
                    )
                ],
                "next_agent": next_agent,
                "iteration_count": iteration_count + 1,
            }
        else:
            # Direct response without delegation
            response_content = (
                response.content if hasattr(response, "content") else str(response)
            )
            return {
                "messages": [AIMessage(content=response_content)],
                "next_agent": None,
                "iteration_count": iteration_count + 1,
            }

    except Exception as e:
        logger.exception(f"[root_agent] Error processing query: {e}")
        return {
            "messages": [
                AIMessage(content=f"I encountered an error: {str(e)}. Please try again.")
            ],
            "next_agent": None,
            "iteration_count": iteration_count + 1,
        }


def create_root_agent():
    """Factory function to create the root agent node.

    Returns:
        The root agent node function.
    """
    return root_agent_node
