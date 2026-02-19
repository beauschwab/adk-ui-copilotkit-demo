"""Team knowledge RAG agent implementation using LangGraph and Vertex AI RAG.

This module provides document retrieval from team knowledge bases with
permission-based access control. Equivalent to the ADK team_knowledge_agent.
"""

import logging
import os
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from state import KnowseeState

logger = logging.getLogger(__name__)

# RAG configuration
RAG_SIMILARITY_TOP_K = int(os.getenv("RAG_SIMILARITY_TOP_K", "10"))

# Team knowledge instruction
TEAM_KNOWLEDGE_INSTRUCTION = """You are a team knowledge specialist. Your role is to search and retrieve information from internal team documents.

When given a query:
1. Search the team's knowledge bases for relevant documents
2. Provide accurate information with proper citations
3. Include source document names and excerpts
4. Be thorough but concise

Always cite your sources from the knowledge base."""


def _ensure_vertexai_init():
    """Ensure Vertex AI is initialised with correct project and location."""
    import vertexai

    vertexai.init(
        project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION"),
    )


async def search_knowledge(query: str, user_corpora: list[str]) -> str:
    """Search team knowledge bases for documents matching the query.

    Args:
        query: The search query.
        user_corpora: List of corpus names accessible to the user.

    Returns:
        Relevant document excerpts with source citations.
    """
    if not user_corpora:
        return "No knowledge bases accessible to you. Contact your administrator."

    try:
        _ensure_vertexai_init()

        from vertexai import rag
        from vertexai.rag import RagResource, RagRetrievalConfig

        # Build RAG resources for all accessible corpora
        rag_resources = [RagResource(rag_corpus=corpus) for corpus in user_corpora]

        logger.debug(f"Searching {len(rag_resources)} corpora for: {query[:50]}...")

        # Query all accessible corpora
        response = rag.retrieval_query(
            rag_resources=rag_resources,
            text=query,
            rag_retrieval_config=RagRetrievalConfig(top_k=RAG_SIMILARITY_TOP_K),
        )

        # Format results with citations
        if not response.contexts or not response.contexts.contexts:
            return f"No relevant documents found for: {query}"

        results = []
        for i, ctx in enumerate(response.contexts.contexts, 1):
            source = getattr(ctx, "source_uri", "Unknown source")
            text = getattr(ctx, "text", "")
            if text:
                source_name = source.split("/")[-1] if "/" in source else source
                results.append(f"[Source {i}: {source_name}]\n{text}")

        if not results:
            return f"No relevant documents found for: {query}"

        return "\n\n---\n\n".join(results)

    except ImportError as e:
        logger.warning(f"vertexai.rag not available: {e}")
        return "Knowledge search is temporarily unavailable. RAG service not configured."
    except Exception as e:
        logger.exception(f"RAG retrieval failed: {e}")
        return f"Error searching knowledge base: {str(e)}"


async def list_knowledge_files(user_corpora: list[str]) -> str:
    """List files available in the user's team knowledge bases.

    Args:
        user_corpora: List of corpus names accessible to the user.

    Returns:
        A formatted list of available files.
    """
    if not user_corpora:
        return "No knowledge bases accessible to you. Contact your administrator."

    try:
        _ensure_vertexai_init()

        from vertexai import rag

        max_files = 50
        total_count = 0
        displayed_count = 0
        corpus_sections = []

        for corpus_name in user_corpora:
            try:
                files = list(rag.list_files(corpus_name=corpus_name))
                corpus_file_count = len(files)
                total_count += corpus_file_count

                if files and displayed_count < max_files:
                    corpus_display = corpus_name.split("/")[-1]
                    file_entries = []

                    for f in files:
                        if displayed_count >= max_files:
                            break
                        name = getattr(f, "display_name", None) or f.name.split("/")[-1]
                        file_entries.append(f"  - {name}")
                        displayed_count += 1

                    corpus_sections.append(
                        f"**Knowledge Base** (corpus {corpus_display}):\n"
                        + "\n".join(file_entries)
                    )

            except Exception as e:
                logger.warning(f"Failed to list files for corpus {corpus_name}: {e}")
                corpus_sections.append(
                    f"**Corpus {corpus_name.split('/')[-1]}**: Unable to list files"
                )

        if total_count == 0:
            return "No files found in your team knowledge bases."

        header = f"Found {displayed_count} file(s) in your knowledge bases:\n\n"
        return header + "\n\n".join(corpus_sections)

    except ImportError as e:
        logger.warning(f"vertexai.rag not available: {e}")
        return "Knowledge base browsing is temporarily unavailable."
    except Exception as e:
        logger.exception(f"Failed to list knowledge files: {e}")
        return f"Error listing knowledge base files: {str(e)}"


async def rag_agent_node(state: KnowseeState) -> dict[str, Any]:
    """RAG agent node for team knowledge retrieval.

    This node handles queries about internal team documents using Vertex AI RAG.
    Access is controlled by team membership loaded in user context.

    Args:
        state: The current graph state.

    Returns:
        Updated state with knowledge retrieval results.
    """
    logger.info("[rag_agent] Processing team knowledge request")

    # Get user corpora from state
    user_corpora = state.get("user_corpora", [])
    user_teams = state.get("user_teams", [])

    if not state.get("_user_context_loaded"):
        error_msg = "User context not loaded. Please try again."
        return {
            "messages": [AIMessage(content=error_msg, name="rag_agent")],
            "next_agent": None,
        }

    if not user_corpora:
        if not user_teams:
            error_msg = "No team memberships found. Contact your administrator."
        else:
            error_msg = f"Your teams ({', '.join(user_teams)}) don't have knowledge bases configured."
        return {
            "messages": [AIMessage(content=error_msg, name="rag_agent")],
            "next_agent": None,
        }

    # Get the last user message as the query
    messages = state.get("messages", [])
    if not messages:
        logger.warning("[rag_agent] No messages in state")
        return {"messages": []}

    last_message = messages[-1]
    query = last_message.content if hasattr(last_message, "content") else str(last_message)

    # Determine if this is a list request or search request
    query_lower = query.lower()
    is_list_request = any(
        keyword in query_lower
        for keyword in ["list files", "show files", "what files", "available documents"]
    )

    try:
        if is_list_request:
            result = await list_knowledge_files(user_corpora)
        else:
            result = await search_knowledge(query, user_corpora)

        # Initialize LLM for response formatting
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.7,
            convert_system_message_to_human=True,
        )

        # Format the response with the LLM
        format_messages = [
            SystemMessage(content=TEAM_KNOWLEDGE_INSTRUCTION),
            HumanMessage(content=f"User query: {query}\n\nKnowledge base results:\n{result}"),
        ]

        response = await llm.ainvoke(format_messages)
        response_content = response.content if hasattr(response, "content") else str(response)

        return {
            "messages": [AIMessage(content=response_content, name="rag_agent")],
            "next_agent": None,
        }

    except Exception as e:
        logger.exception(f"[rag_agent] RAG query failed: {e}")
        error_msg = f"Knowledge base query error: {str(e)}"
        return {
            "messages": [AIMessage(content=error_msg, name="rag_agent")],
            "next_agent": None,
        }


def create_rag_agent():
    """Factory function to create the RAG agent node.

    Returns:
        The RAG agent node function.
    """
    return rag_agent_node
