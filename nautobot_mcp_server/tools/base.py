"""Base class for Nautobot MCP tools."""

import json
from typing import Any, Optional

from mcp.server.fastmcp import Context


class NautobotToolBase:
    """Base class for Nautobot tool implementations."""

    def __init__(self, client_getter):
        """Initialize the tool base.

        Args:
            client_getter: Callable that returns a pynautobot client
        """
        self._get_client = client_getter

    @staticmethod
    def format_error(error_msg: str) -> str:
        """Format an error message as JSON.

        Args:
            error_msg: The error message

        Returns:
            JSON formatted error string
        """
        return json.dumps({"error": error_msg}, separators=(",", ":"))

    @staticmethod
    def format_success(data: Any, message: Optional[str] = None) -> str:
        """Format a success response as JSON.

        Args:
            data: The data to return
            message: Optional success message

        Returns:
            JSON formatted success response
        """
        if message:
            return json.dumps({"success": True, "message": message, "data": data}, separators=(",", ":"))
        return json.dumps(data, separators=(",", ":"))

    def log_and_return_error(self, ctx: Context, operation: str, error: Exception) -> str:
        """Log an error and return formatted error response.

        Args:
            ctx: MCP context
            operation: Description of the operation that failed
            error: The exception that occurred

        Returns:
            JSON formatted error string
        """
        error_msg = f"Error {operation}: {str(error)}"
        ctx.error(error_msg)
        return self.format_error(error_msg)
