"""Resources module for Nautobot MCP Server."""

from mcp.server.fastmcp import FastMCP

from .devices import DeviceSchemaResource
from .locations import LocationSchemaResource


def register_all_resources(mcp: FastMCP):
    """Register all resources with the MCP server.

    Args:
        mcp: FastMCP instance to register resources with
    """
    resources = [
        DeviceSchemaResource(),
        LocationSchemaResource(),
    ]

    for resource in resources:
        resource.register(mcp)


__all__ = [
    "register_all_resources",
    "DeviceSchemaResource",
    "LocationSchemaResource",
]
