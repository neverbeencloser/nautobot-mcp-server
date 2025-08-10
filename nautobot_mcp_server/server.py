"""Nautobot MCP Server implementation using FastMCP."""

from typing import Optional

import pynautobot
from mcp.server.fastmcp import FastMCP

from .tools import register_all_tools


class NautobotMCPServer:
    """MCP Server for Nautobot API operations."""

    def __init__(self, url: str, token: str):
        """Initialize Nautobot MCP Server.

        Args:
            url: The Nautobot API URL
            token: The Nautobot API token
        """
        self.url = url
        self.token = token
        self.nautobot_client: Optional[pynautobot.api] = None
        self.mcp = FastMCP("nautobot-mcp-server")

        # Register all tools from the tools submodule
        register_all_tools(self.mcp, self._get_client)

    def _get_client(self) -> pynautobot.api:
        """Get or create Nautobot client."""
        if not self.nautobot_client:
            self.nautobot_client = pynautobot.api(self.url, token=self.token, threading=True, retries=3)
        return self.nautobot_client

    def get_fastmcp_instance(self) -> FastMCP:
        """Get the FastMCP instance for running the server."""
        return self.mcp
