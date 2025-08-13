"""Base class for Nautobot MCP tools."""

from typing import Any, Optional

import yaml
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
        """Format an error message as YAML.

        Args:
            error_msg: The error message

        Returns:
            YAML formatted error string
        """
        return yaml.dump(
            {"error": error_msg},
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
            indent=2,
        )

    @staticmethod
    def format_success(data: Any, message: Optional[str] = None) -> str:
        """Format a success response as YAML.

        Args:
            data: The data to return
            message: Optional success message

        Returns:
            YAML formatted success response
        """
        ret = {"success": True, "data": data}
        if message:
            ret["message"] = message
        return yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True, indent=2)

    def log_and_return_error(self, ctx: Context, operation: str, error: Exception) -> str:
        """Log an error and return formatted error response.

        Args:
            ctx: MCP context
            operation: Description of the operation that failed
            error: The exception that occurred

        Returns:
            YAML formatted error string
        """
        error_msg = f"Error {operation}: {str(error)}"
        ctx.error(error_msg)
        return self.format_error(error_msg)
