"""Location schema resources for Nautobot MCP Server."""

from mcp.server.fastmcp import FastMCP

from .base import NautobotResourceBase


class LocationSchemaResource(NautobotResourceBase):
    """Resources for exposing location schemas to AI agents."""

    # Location field definitions - optimized for token efficiency
    LOCATION_FIELDS = {
        "name": {"type": "string", "required_for_create": True},
        "location_type": {"type": "string", "required_for_create": True},
        "status": {"type": "string", "required_for_create": False, "default": "active"},
        "parent": {"type": "string"},
        "description": {"type": "string"},
        "facility": {"type": "string"},
        "asn": {"type": "integer"},
        "time_zone": {"type": "string"},
        "physical_address": {"type": "string"},
        "shipping_address": {"type": "string"},
        "latitude": {"type": "string"},
        "longitude": {"type": "string"},
        "contact_name": {"type": "string"},
        "contact_phone": {"type": "string"},
        "contact_email": {"type": "string"},
    }

    def register(self, mcp: FastMCP):
        """Register location schema resources with the MCP server.

        Args:
            mcp: FastMCP instance to register resources with
        """

        @mcp.resource("schema://location/fields")
        def get_location_fields() -> str:
            """Get all available location fields with their types and descriptions.

            Returns a YAML string describing all location fields that can be used
            in create and update operations.
            """
            return self.format_json(self.LOCATION_FIELDS)

        @mcp.resource("schema://location/required-for-create")
        def get_location_required_fields() -> str:
            """Get required location fields for CREATE operations only.

            Returns a YAML list of field names that are required when creating a location.
            Note: Updates do not require any specific fields.
            """
            required_fields = [
                name for name, spec in self.LOCATION_FIELDS.items() if spec.get("required_for_create", False)
            ]
            data = {
                "required_for_create": required_fields,
                "note": "These fields are ONLY required when creating a new location. Updates can modify any subset of fields.",
            }
            return self.format_json(data)

        @mcp.resource("schema://location/examples")
        def get_location_examples() -> str:
            """Location operation examples."""
            examples = {
                "create": {
                    "name": "datacenter-01",
                    "location_type": "datacenter",
                    "status": "active",
                    "facility": "DC01",
                },
                "update_single": {"status": "maintenance"},
                "update_multi": {
                    "description": "Updated datacenter",
                    "facility": "DC01-NEW",
                    "contact_name": "Jane Doe",
                },
                "update_clear_fields": {"contact_phone": None, "contact_email": None},
            }
            return self.format_json(examples)
