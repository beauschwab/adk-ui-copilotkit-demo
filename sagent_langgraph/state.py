"""State definitions for the LangGraph agent.

Defines the shared state structure used across all nodes in the agent graph.
State management uses reducers for proper accumulation and merging of data.
"""

from typing import Annotated, Any, TypedDict

from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


def merge_dicts(left: dict | None, right: dict | None) -> dict:
    """Reducer for merging dictionaries (new values overwrite old)."""
    if left is None:
        return right or {}
    if right is None:
        return left
    return {**left, **right}


def extend_list(left: list | None, right: list | None) -> list:
    """Reducer for extending lists (accumulate)."""
    if left is None:
        return right or []
    if right is None:
        return left
    return left + right


class KnowseeState(TypedDict):
    """State for the Knowsee multi-agent graph.

    This state is shared across all nodes and maintains context throughout
    the conversation. Reducers handle proper accumulation of messages,
    widgets, and other data structures.
    """

    # Messages (user, assistant, system) - uses add_messages reducer
    messages: Annotated[list[BaseMessage], add_messages]

    # User context (loaded once per session)
    user_id: str | None
    user_teams: list[str] | None
    user_corpora: list[str] | None
    _user_context_loaded: bool

    # File artifacts
    artifacts: dict[str, Any] | None  # filename -> artifact data
    pending_artifact_ids: list[str] | None

    # Session metadata
    session_id: str | None
    session_title: str | None
    _title_generated: bool

    # Data analyst tracking
    query_attempts: Annotated[list[dict], extend_list]  # SQL query attempts
    pending_widgets: Annotated[list[dict], extend_list]  # Chart/viz widgets

    # Grounding metadata (for search citations)
    grounding_metadata: Annotated[list[dict], extend_list]

    # Thought tracking (for extended thinking simulation)
    thoughts: Annotated[list[str], extend_list]

    # Routing state
    next_agent: str | None  # Which sub-agent to route to
    iteration_count: int  # Safety counter to prevent infinite loops
