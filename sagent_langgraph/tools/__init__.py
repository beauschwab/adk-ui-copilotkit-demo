"""File attachment tools for LangGraph implementation.

These tools allow the agent to discover and read files uploaded by users.
Adapted from the ADK implementation to work with LangGraph's tool pattern.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def create_list_files_tool(artifact_service: Any):
    """Create a list_files tool with access to the artifact service.

    Args:
        artifact_service: The artifact service instance for file storage.

    Returns:
        A callable tool function for LangGraph.
    """

    async def list_files() -> list[dict]:
        """List all files uploaded to this conversation.

        Returns a list of available files that can be read using read_file().
        Use this to discover what files the user has shared before reading them.

        Returns:
            List of file metadata dicts with 'filename' key.
            Empty list if no files have been uploaded.
        """
        try:
            # Note: We'll need to adapt this to work with LangGraph's state
            # For now, this is a placeholder that needs session context
            logger.debug("[list_files] Artifact service integration needed")
            return []
        except Exception as e:
            logger.error(f"[list_files] unexpected error: {e}")
            return []

    list_files.__name__ = "list_files"
    list_files.__doc__ = """List all files uploaded to this conversation.

Returns a list of available files that can be read using read_file().
Use this to discover what files the user has shared before reading them."""

    return list_files


def create_read_file_tool(artifact_service: Any):
    """Create a read_file tool with access to the artifact service.

    Args:
        artifact_service: The artifact service instance for file storage.

    Returns:
        A callable tool function for LangGraph.
    """

    async def read_file(filename: str) -> dict:
        """Read the contents of an uploaded file.

        Use list_files() first to discover available filenames.
        This tool loads the file content so you can analyse, summarise,
        or answer questions about it.

        Args:
            filename: The name of the file to read (from list_files output).

        Returns:
            Dict with file metadata and content.
        """
        try:
            # Note: We'll need to adapt this to work with LangGraph's state
            logger.debug(f"[read_file] Reading file: {filename}")
            return {
                "filename": filename,
                "found": False,
                "error": "File reading not yet implemented for LangGraph backend",
            }
        except Exception as e:
            logger.error(f"[read_file] unexpected error: {e}")
            return {
                "filename": filename,
                "found": False,
                "error": f"Failed to read file: {e}",
            }

    read_file.__name__ = "read_file"
    read_file.__doc__ = """Read the contents of an uploaded file.

Use list_files() first to discover available filenames.
This tool loads the file content so you can analyse, summarise,
or answer questions about it."""

    return read_file
