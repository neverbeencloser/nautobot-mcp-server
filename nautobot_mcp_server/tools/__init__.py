"""Tools package for Nautobot MCP Server."""

from .devices import DeviceTools
from .graphql import GraphQLTools
from .jobs import JobTools
from .locations import LocationTools

__all__ = ["DeviceTools", "GraphQLTools", "LocationTools", "JobTools", "register_all_tools"]


def register_all_tools(mcp, client_getter):
    """Register all available tools with the MCP server.

    Args:
        mcp: FastMCP instance
        client_getter: Callable that returns a pynautobot client
    """
    # Initialize tool classes
    device_tools = DeviceTools(client_getter)
    graphql_tools = GraphQLTools(client_getter)
    location_tools = LocationTools(client_getter)
    job_tools = JobTools(client_getter)

    # Register all tools
    device_tools.register(mcp)
    graphql_tools.register(mcp)
    location_tools.register(mcp)
    job_tools.register(mcp)
