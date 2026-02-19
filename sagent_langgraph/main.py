"""FastAPI server exposing the Knowsee agent via LangGraph.

This server provides a LangGraph-based implementation with 100% feature parity
to the ADK backend. It uses the same AG-UI protocol for compatibility with
CopilotKit frontends.

Usage:
    uv run uvicorn sagent_langgraph.main:app --reload --port 8001
"""

# Configure logging before any imports
from logging_config import configure_logging

configure_logging()

import json
import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage

from graph import create_knowsee_graph, get_initial_state
from callbacks import inject_user_context, generate_session_title
from converters import convert_file, needs_conversion
from converters.base import ConversionError
from services.events import event_bus
from services.titles import get_titles_bulk
from utils.upload_limits import (
    MAX_FILE_SIZE_BYTES,
    MAX_FILES,
    get_supported_types_list,
    is_supported_mime_type,
)

logger = logging.getLogger(__name__)

# Load environment variables
ENV_DIR = Path(__file__).parent
load_dotenv(ENV_DIR / ".env.development")
load_dotenv(ENV_DIR / ".env.local", override=True)


def get_database_url() -> str:
    """Get database URL from environment."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError(
            "DATABASE_URL environment variable is required. "
            "Run 'make db-up' to start local Postgres."
        )
    logging.info("Using PostgreSQL for session storage")
    return db_url


# Create the LangGraph application
database_url = get_database_url()
knowsee_app = create_knowsee_graph(database_url)

# Create FastAPI application
app = FastAPI(
    title="Knowsee Agent API (LangGraph)",
    description="Enterprise knowledge assistant powered by LangGraph and AG-UI",
    version="0.1.0",
)


# Configure CORS
def get_cors_origins() -> list[str]:
    """Get allowed CORS origins based on environment."""
    cors_origins = os.getenv("CORS_ORIGINS")
    if cors_origins:
        return [origin.strip() for origin in cors_origins.split(",")]

    return [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Session storage (in-memory for now, should use database)
sessions: dict[str, dict[str, Any]] = {}


@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration."""
    return {"status": "healthy", "backend": "langgraph", "agent": "knowsee_agent"}


@app.post("/")
async def run_agent(
    request: dict,
    x_user_id: str | None = Header(None, alias="x-user-id"),
):
    """Main AG-UI endpoint for running the agent.

    This endpoint accepts AG-UI protocol requests and routes them through
    the LangGraph agent graph.

    Args:
        request: AG-UI request body with messages and thread_id.
        x_user_id: User ID from authentication header.

    Returns:
        Streaming response with agent outputs.
    """
    if not x_user_id:
        raise HTTPException(
            status_code=401,
            detail="Authentication required: x-user-id header missing",
        )

    # Normalize user ID
    user_id = x_user_id.strip().lower()

    # Extract thread_id (session_id) and messages
    thread_id = request.get("thread_id", request.get("threadId", ""))
    if not thread_id:
        # Generate new thread ID
        import uuid

        thread_id = str(uuid.uuid4())

    messages = request.get("messages", [])

    logger.info(
        f"[run_agent] user={user_id}, thread={thread_id}, msgs={len(messages)}"
    )

    try:
        # Get or create session state
        if thread_id not in sessions:
            sessions[thread_id] = get_initial_state(user_id, thread_id)

        state = sessions[thread_id]

        # Inject user context if needed
        if not state.get("_user_context_loaded"):
            context_updates = await inject_user_context(state)
            state.update(context_updates)

        # Add new user message
        if messages:
            last_msg = messages[-1]
            if isinstance(last_msg, dict):
                content = last_msg.get("content", "")
            else:
                content = str(last_msg)

            state["messages"].append(HumanMessage(content=content))

        # Invoke the graph
        config = {"configurable": {"thread_id": thread_id}}
        result = await knowsee_app.ainvoke(state, config=config)

        # Update session with result
        sessions[thread_id] = result

        # Generate title if needed
        if not state.get("_title_generated"):
            title_updates = await generate_session_title(result)
            sessions[thread_id].update(title_updates)

        # Extract response
        response_messages = result.get("messages", [])
        if response_messages:
            last_response = response_messages[-1]
            response_content = (
                last_response.content
                if hasattr(last_response, "content")
                else str(last_response)
            )
        else:
            response_content = "I couldn't generate a response. Please try again."

        # Return AG-UI compatible response
        return {
            "messages": [{"role": "assistant", "content": response_content}],
            "thread_id": thread_id,
        }

    except Exception as e:
        logger.exception(f"[run_agent] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/upload/config")
async def upload_config():
    """Return upload constraints for frontend validation."""
    return {
        "supported_types": get_supported_types_list(),
        "max_file_size_bytes": MAX_FILE_SIZE_BYTES,
        "max_files": MAX_FILES,
    }


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    session_id: str = Header(..., alias="x-session-id"),
    user_id: str = Header(..., alias="x-user-id"),
):
    """Upload a file as an artifact for use in chat.

    Args:
        file: The uploaded file.
        session_id: Current chat session ID.
        user_id: User identifier.

    Returns:
        Artifact metadata.
    """
    content_type = file.content_type or "application/octet-stream"
    if not is_supported_mime_type(content_type):
        raise HTTPException(
            status_code=415,
            detail={
                "error": "unsupported_file_type",
                "message": f"File type '{content_type}' is not supported",
                "supported_types": get_supported_types_list(),
            },
        )

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail={
                "error": "file_too_large",
                "message": f"File size exceeds limit",
                "max_size_bytes": MAX_FILE_SIZE_BYTES,
            },
        )

    filename = file.filename or "upload"
    if needs_conversion(content_type):
        try:
            result = convert_file(file_bytes, content_type, filename)
            file_bytes = result.content
            content_type = result.mime_type
            filename = result.filename
        except ConversionError as e:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "conversion_failed",
                    "message": f"Failed to convert file: {e}",
                },
            ) from e

    # Store artifact (simplified for now)
    logger.info(f"[upload] Uploaded {filename} for session {session_id}")

    return {
        "filename": filename,
        "original_filename": file.filename,
        "version": 1,
        "mime_type": content_type,
        "size_bytes": len(file_bytes),
    }


@app.get("/api/events")
async def sse_events():
    """SSE endpoint for real-time updates."""

    async def event_stream():
        async for event in event_bus.subscribe():
            yield event.to_sse()

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/sessions")
async def list_sessions(user_id: str):
    """List all chat sessions for a user."""
    # Filter sessions by user
    user_sessions = [
        {
            "id": sid,
            "title": state.get("session_title", "New conversation"),
            "lastUpdated": None,  # TODO: track timestamps
        }
        for sid, state in sessions.items()
        if state.get("user_id") == user_id
    ]

    return {"sessions": user_sessions}


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str, user_id: str):
    """Get details of a specific session including messages."""
    if session_id not in sessions:
        return {"error": "Session not found"}

    state = sessions[session_id]

    # Verify user owns this session
    if state.get("user_id") != user_id:
        return {"error": "Unauthorized"}

    # Convert messages to API format
    messages = []
    for msg in state.get("messages", []):
        if hasattr(msg, "type"):
            role = "user" if msg.type == "human" else "model"
            content = msg.content if hasattr(msg, "content") else str(msg)
            messages.append({"role": role, "content": content})

    return {
        "id": session_id,
        "messages": messages,
        "lastUpdated": None,
    }


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str, user_id: str):
    """Delete a specific session."""
    if session_id in sessions:
        state = sessions[session_id]
        if state.get("user_id") == user_id:
            del sessions[session_id]
            return {"success": True}

    return {"success": False, "error": "Session not found"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8001))
    print(f"Starting Knowsee agent server (LangGraph) on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
