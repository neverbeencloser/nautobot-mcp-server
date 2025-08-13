"""Device schema resources for Nautobot MCP Server."""

from mcp.server.fastmcp import FastMCP

from .base import NautobotResourceBase


class DeviceSchemaResource(NautobotResourceBase):
    """Resources for exposing device schemas to AI agents."""

    # Device field definitions - optimized for token efficiency
    DEVICE_FIELDS = {
        "name": {"type": "string", "required_for_create": True},
        "device_type": {"type": "string", "required_for_create": True},
        "location": {"type": "string", "required_for_create": True},
        "role": {"type": "string", "required_for_create": True},
        "status": {"type": "string", "required_for_create": True},
        "asset_tag": {"type": "string"},
        "cluster": {"type": "string"},
        "comments": {"type": "string"},
        "custom_fields": {"type": "dict"},
        "device_redundancy_group": {"type": "string"},
        "device_redundancy_group_priority": {"type": "integer"},
        "face": {"type": "string", "choices": ["Front", "Rear"]},
        "parent_bay": {"type": "string"},
        "platform": {"type": "string"},
        "position": {"type": "integer"},
        "primary_ip4": {"type": "string"},
        "primary_ip6": {"type": "string"},
        "rack": {"type": "string"},
        "relationships": {"type": "dict"},
        "serial": {"type": "string"},
        "secrets_group": {"type": "string"},
        "software_image_files": {"type": "list"},
        "software_version": {"type": "string"},
        "tags": {"type": "list"},
        "tenant": {"type": "string"},
        "vc_position": {"type": "integer"},
        "vc_priority": {"type": "integer"},
        "virtual_chassis": {"type": "string"},
    }

    def register(self, mcp: FastMCP):
        """Register device schema resources with the MCP server.

        Args:
            mcp: FastMCP instance to register resources with
        """

        @mcp.resource("schema://device/fields")
        def get_device_fields() -> str:
            """Get all available device fields with their types and descriptions.

            Returns a YAML string describing all device fields that can be used
            in create and update operations.
            """
            return self.format_json(self.DEVICE_FIELDS)

        @mcp.resource("schema://device/required-for-create")
        def get_device_required_fields() -> str:
            """Get required device fields for CREATE operations only.

            Returns a YAML list of field names that are required when creating a device.
            Note: Updates do not require any specific fields.
            """
            required_fields = [
                name for name, spec in self.DEVICE_FIELDS.items() if spec.get("required_for_create", False)
            ]
            data = {
                "required_for_create": required_fields,
                "note": "These fields are ONLY required when creating a new device. Updates can modify any subset of fields.",
            }
            return self.format_json(data)

        @mcp.resource("schema://device/examples")
        def get_device_examples() -> str:
            """Device operation examples."""
            examples = {
                "create": {
                    "name": "switch01",
                    "device_type": "Catalyst",
                    "location": "dc1",
                    "role": "access",
                    "status": "active",
                },
                "update_single": {"status": "maintenance"},
                "update_multi": {"location": "dc2", "rack": "R05", "position": 10},
                "update_clear_fields": {"asset_tag": None, "serial": None},
            }
            return self.format_json(examples)
