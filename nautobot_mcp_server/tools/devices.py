"""Device-related tools for Nautobot MCP Server."""

from typing import Any, Literal

from mcp.server.fastmcp import Context, FastMCP
from pynautobot import RequestError

from .base import NautobotToolBase


class DeviceTools(NautobotToolBase):
    """Tools for managing devices in Nautobot."""

    def register(self, mcp: FastMCP):
        """Register device tools with the MCP server.

        Args:
            mcp: FastMCP instance to register tools with
        """

        @mcp.tool()
        def nautobot_list_devices(
            ctx: Context,
            depth: int = 1,
            limit: int = 50,
            offset: int | None = None,
            location: str | None = None,
            role: str | None = None,
            status: str | None = None,
        ) -> str:
            """List all devices in Nautobot.

            Note that this returns a limited number of device fields to help with potential token size limitations.
            If token limit is reached, you can use limit and offset to paginate through results.

            Args:
                ctx: MCP context for logging and progress
                depth: Depth of the device details to return; default returns 1 level of nested objects.
                limit: Number of devices per page; pynautobot will return all devices unless offset is used.
                offset: Offset for pagination; if None, will return all devices.
                location: Optional location filter to apply (name or UUID).
                role: Optional device role filter to apply (name or UUID).
                status: Optional device status filter to apply (name or UUID).

            Returns:
                YAML string of device list
            """
            ctx.info(
                f"Listing devices (depth={depth}, limit={limit}, "
                "offset={offset}, location={location}, role={role}, status={status})"
            )

            try:
                client = self._get_client()
                devices = client.dcim.devices

                kwargs: dict[str, Any] = {
                    "depth": depth,
                    "limit": limit,
                    "offset": offset,
                }
                if location:
                    kwargs["location"] = location
                if role:
                    kwargs["role"] = role
                if status:
                    kwargs["status"] = status

                device_list = devices.filter(**kwargs)

                # Build abbreviated list to help with potential token size limitations
                result = []
                for device in device_list:
                    device_info = {
                        "id": str(device.id),
                        "name": device.name,
                        "device_type": str(device.device_type) if device.device_type else None,
                        "role": str(device.role) if device.role else None,
                        "location": str(device.location) if device.location else None,
                        "status": str(device.status) if device.status else None,
                        "primary_ip4": str(device.primary_ip4)
                        if hasattr(device, "primary_ip4") and device.primary_ip4
                        else None,
                        "primary_ip6": str(device.primary_ip6)
                        if hasattr(device, "primary_ip6") and device.primary_ip6
                        else None,
                    }
                    result.append(device_info)

                ctx.info(f"Found {len(result)} devices")
                return self.format_success(result)

            except Exception as e:
                return self.log_and_return_error(ctx, "listing devices", e)

        @mcp.tool()
        def nautobot_get_device(ctx: Context, device_id: str, depth: int = 1) -> str:
            """Get a specific device by ID or name.

            Args:
                ctx: MCP context for logging and progress
                device_id: Device ID (UUID) or name
                depth: Depth of the device details to return; default returns 1 level of nested objects.

            Returns:
                YAML string of device details
            """
            ctx.info(f"Getting device: {device_id}")

            try:
                client = self._get_client()
                devices = client.dcim.devices

                # Try to get by ID first (UUID)
                try:
                    device = devices.get(id=device_id, depth=depth)
                    ctx.debug(f"Found device by ID: {device_id}")
                except RequestError:
                    # If not found by ID, try by name
                    ctx.debug(f"Searching device by name: {device_id}")
                    device = devices.get(name=device_id, depth=depth)

                if device:
                    ctx.info(f"Successfully retrieved device: {device.name}")
                    return self.format_success(dict(device), message="Device retrieved successfully")
                else:
                    ctx.warning(f"Device not found: {device_id}")
                    return self.format_error(f"Device not found: {device_id}")

            except Exception as e:
                return self.log_and_return_error(ctx, "getting device", e)

        @mcp.tool()
        def nautobot_create_device(
            ctx: Context,
            name: str,
            device_type: str,
            location: str,
            role: str,
            status: str,
            asset_tag: str | None = None,
            cluster: str | None = None,
            comments: str | None = None,
            custom_fields: dict[str, str] | None = None,
            device_redundancy_group: str | None = None,
            device_redundancy_group_priority: int | None = None,
            face: Literal["Front", "Rear"] | None = None,
            parent_bay: str | None = None,
            platform: str | None = None,
            position: int | None = None,
            primary_ip4: str | None = None,
            primary_ip6: str | None = None,
            rack: str | None = None,
            relationships: dict | None = None,
            serial: str | None = None,
            secrets_group: str | None = None,
            software_image_files: list[str] | None = None,
            software_version: str | None = None,
            tags: list[str] | None = None,
            tenant: str | None = None,
            vc_position: int | None = None,
            vc_priority: int | None = None,
            virtual_chassis: str | None = None,
        ) -> str:
            """
            Create a new device in Nautobot.

            Args:
                ctx: MCP context for logging and progress
                name: Device name (required)
                device_type: Device type (UUID; required)
                location: Device location (UUID or name; required)
                role: Device role (UUID or name; required)
                status: Device status (UUID or name; name should be capitalized; required)
                asset_tag: Optional asset tag for the device
                cluster: Optional cluster (UUID or name)
                comments: Optional comments for the device
                custom_fields: Optional custom fields as a dictionary
                device_redundancy_group: Optional device redundancy group (UUID or name)
                device_redundancy_group_priority: Optional priority for redundancy group
                face: Optional face of the device
                parent_bay: Optional parent bay (UUID or name)
                platform: Optional platform (UUID or name)
                position: Optional position in the rack
                primary_ip4: Optional primary IPv4 address
                primary_ip6: Optional primary IPv6 address
                rack: Optional rack (UUID or name)
                relationships: Optional relationships as a dictionary
                serial: Optional serial number for the device
                secrets_group: Optional secrets group (UUID or name)
                software_image_files: Optional list of software image files
                software_version: Optional software version (UUID or name)
                tags: Optional list of tags (names)
                tenant: Optional tenant (UUID or name)
                vc_position: Optional virtual chassis position
                vc_priority: Optional virtual chassis priority
                virtual_chassis: Optional virtual chassis (UUID or name)

            Returns:
                YAML string of created device details or error message
            """
            ctx.info(f"Creating device: {name}")

            try:
                # Capture function parameters before defining other locals
                params = locals().copy()
                params.pop("ctx")
                params.pop("self")

                client = self._get_client()

                if not name:
                    return self.format_error("Device name is required")
                if not location:
                    return self.format_error("Device location is required")
                if not role:
                    return self.format_error("Device role is required")
                if not status:
                    return self.format_error("Device status is required")

                # Build device payload from non-None parameters
                device_payload = {k: v for k, v in params.items() if v is not None}
                ctx.info(f"Creating device: {device_payload['name']}")

                ctx.info(f"Creating device with data: {device_payload}")
                new_device = client.dcim.devices.create(**device_payload)

                device_info = {
                    "id": str(new_device.id),
                    "name": new_device.name,
                    "device_type": str(new_device.device_type) if new_device.device_type else None,
                    "role": str(new_device.role) if new_device.role else None,
                    "location": str(new_device.location) if new_device.location else None,
                    "status": str(new_device.status) if new_device.status else None,
                    "created": str(new_device.created) if new_device.created else None,
                    "url": new_device.url if hasattr(new_device, "url") else None,
                }

                ctx.info(f"Successfully created device: {new_device.name}")
                return self.format_success(device_info, message="Device created successfully")

            except Exception as e:
                return self.log_and_return_error(ctx, "creating device", e)

        @mcp.tool()
        def nautobot_update_device(
            ctx: Context,
            device_id: str,
            updates: dict[str, Any],
        ) -> str:
            """
            Update device fields for an existing device.

            Read 'schema://device/fields' MCP Resource to see possible update fields.

            Args:
                ctx: MCP context for logging and progress
                device_id: Device ID (UUID); must GET device first if you don't know the ID.
                updates: Field updates dict. Set None to clear fields.

            Returns:
                YAML string of updated device details or error message
            """
            ctx.info(f"Updating device: {device_id}")

            try:
                client = self._get_client()
                devices = client.dcim.devices

                # Get the device
                try:
                    device = devices.get(id=device_id)
                    ctx.debug(f"Found device by ID: {device_id}")
                except RequestError:
                    ctx.warning(f"Device not found: {device_id}")
                    return self.format_error(f"Device not found: {device_id}")

                # Validate that updates is a dictionary
                if not isinstance(updates, dict):
                    return self.format_error("Updates parameter must be a dictionary")

                # Log fields being updated, including None values
                fields_to_update = list(updates.keys())
                fields_to_clear = [k for k, v in updates.items() if v is None]

                if fields_to_clear:
                    ctx.info(f"Clearing fields: {fields_to_clear}")
                ctx.info(f"Updating fields: {fields_to_update}")

                # Normalize status field if present
                if "status" in updates and updates["status"] is not None:
                    updates["status"] = updates["status"].capitalize()

                ctx.info(f"Updating device with data: {updates}")
                device.update(updates)

                device_info = {
                    "id": str(device.id),
                    "name": device.name,
                    "device_type": str(device.device_type) if device.device_type else None,
                    "role": str(device.role) if device.role else None,
                    "location": str(device.location) if device.location else None,
                    "status": str(device.status) if device.status else None,
                    "updated_fields": fields_to_update,
                    "cleared_fields": fields_to_clear,
                }

                ctx.info(f"Successfully updated device: {device.name}")
                return self.format_success(device_info, message="Device updated successfully")

            except Exception as e:
                return self.log_and_return_error(ctx, "updating device", e)

        @mcp.tool()
        def nautobot_delete_device(ctx: Context, device_id: str) -> str:
            """Delete a device from Nautobot.

            Args:
                ctx: MCP context for logging and progress
                device_id: Device ID (UUID)

            Returns:
                YAML string confirming deletion
            """
            ctx.info(f"Deleting device: {device_id}")

            try:
                client = self._get_client()
                devices = client.dcim.devices

                # Get the device
                try:
                    device = devices.get(id=device_id)
                    ctx.debug(f"Found device by ID: {device_id}")
                except Exception:
                    ctx.warning(f"Device not found: {device_id}")
                    return self.format_error(f"Device not found: {device_id}")

                device_name = device.name
                device.delete()

                ctx.info(f"Successfully deleted device: {device_id}:{device_name}")
                return self.format_success(
                    {"deleted": device_name}, message=f"Device '{device_id}:{device_name}' deleted successfully"
                )

            except Exception as e:
                return self.log_and_return_error(ctx, "deleting device", e)
