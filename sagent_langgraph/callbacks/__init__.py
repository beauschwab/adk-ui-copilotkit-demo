"""Callback implementations for LangGraph.

In LangGraph, callbacks are implemented differently from ADK. We use middleware
and state preprocessing rather than before/after model callbacks.
"""

import logging
from typing import Any

from state import KnowseeState

logger = logging.getLogger(__name__)


async def inject_user_context(state: KnowseeState) -> dict[str, Any]:
    """Inject user context into state before processing.

    This loads user's team memberships and accessible corpora.
    Unlike ADK's callback, this is called explicitly in the graph.

    Args:
        state: The current graph state.

    Returns:
        State updates with user context.
    """
    # Skip if already loaded
    if state.get("_user_context_loaded"):
        return {}

    user_id = state.get("user_id")
    if not user_id:
        logger.debug("[inject_user_context] No user_id in state")
        return {}

    try:
        # Import here to avoid circular imports
        from services.rag import corpus_registry, team_service

        # Get user's teams
        teams = team_service.get_user_teams(user_id)

        if teams:
            # Get corpus names for those teams
            corpus_names = corpus_registry.get_corpus_names_for_teams(teams)
            logger.debug(
                f"User {user_id} context: teams={teams}, corpora={len(corpus_names)}"
            )
        else:
            corpus_names = []
            logger.debug(f"User {user_id} has no team memberships")

        return {
            "user_teams": teams,
            "user_corpora": corpus_names,
            "_user_context_loaded": True,
        }

    except Exception as e:
        logger.warning(f"Failed to load user context for {user_id}: {e}")
        return {
            "user_teams": [],
            "user_corpora": [],
            "_user_context_loaded": True,
        }


async def generate_session_title(state: KnowseeState) -> dict[str, Any]:
    """Generate a session title from the first message.

    Args:
        state: The current graph state.

    Returns:
        State updates with session title.
    """
    # Skip if already generated
    if state.get("_title_generated") or state.get("session_title"):
        return {}

    messages = state.get("messages", [])
    if not messages:
        return {}

    # Only generate after first user message
    user_messages = [m for m in messages if hasattr(m, "type") and m.type == "human"]
    if len(user_messages) < 1:
        return {}

    try:
        from services.titles import generate_title

        first_message = user_messages[0]
        message_text = first_message.content if hasattr(first_message, "content") else str(first_message)

        title = generate_title(message_text)

        # Save to database
        session_id = state.get("session_id")
        if session_id:
            from services.titles import save_title
            save_title(session_id, title)

        logger.info(f"[generate_session_title] Generated: {title}")

        return {
            "session_title": title,
            "_title_generated": True,
        }

    except Exception as e:
        logger.warning(f"Failed to generate session title: {e}")
        return {"_title_generated": True}
