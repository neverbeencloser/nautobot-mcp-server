"""Device-related tools for Nautobot MCP Server."""

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
        def nautobot_list_devices(ctx: Context, limit: int = 10, **kwargs) -> str:
            """List all devices in Nautobot.

            Args:
                ctx: MCP context for logging and progress
                limit: Number of devices to return (default: 10)
                kwargs: Filter devices by kwargs (optional)

            Returns:
                JSON string of device list
            """
            ctx.info(f"Listing devices (limit={limit}, kwargs={kwargs})")

            try:
                client = self._get_client()
                devices = client.dcim.devices
                filter_kwargs = {}

                if "location" in kwargs:
                    ctx.debug(f"Filtering by location: {kwargs['location']}")
                    filter_kwargs["location"] = kwargs["location"]

                device_list = devices.filter(limit=limit, depth=1, **filter_kwargs)

                ctx.info(f"Found {len(device_list)} devices")
                return self.format_success([dict(device) for device in device_list])

            except Exception as e:
                return self.log_and_return_error(ctx, "listing devices", e)

        @mcp.tool()
        def nautobot_get_device(ctx: Context, device_id: str) -> str:
            """Get a specific device by ID or name.

            Args:
                ctx: MCP context for logging and progress
                device_id: Device ID (UUID) or name

            Returns:
                JSON string of device details
            """
            ctx.info(f"Getting device: {device_id}")

            try:
                client = self._get_client()
                devices = client.dcim.devices

                # Try to get by ID first (UUID)
                try:
                    device = devices.get(depth=1, id=device_id)
                    ctx.debug(f"Found device by ID: {device_id}")
                except RequestError:
                    # If not found by ID, try by name
                    ctx.debug(f"Searching device by name: {device_id}")
                    device = devices.get(depth=1, name=device_id)

                if device:
                    ctx.info(f"Successfully retrieved device: {device.name}")
                    return self.format_success(dict(device))
                else:
                    ctx.warning(f"Device not found: {device_id}")
                    return self.format_error(f"Device not found: {device_id}")

            except Exception as e:
                return self.log_and_return_error(ctx, "getting device", e)

        @mcp.tool()
        def nautobot_create_device(
            ctx: Context, name: str, device_type: str, role: str, location: str, status: str = "active"
        ) -> str:
            """Create a new device in Nautobot.

            Args:
                ctx: MCP context for logging and progress
                name: Device name or uuid
                device_type: Device type name or uuid
                role: Device role name or uuid
                location: Location name or uuid
                status: Device status (default: "active")

            Returns:
                JSON string of created device details
            """
            ctx.info(f"Creating device: {name}")

            try:
                client = self._get_client()

                # Create the device
                device_data = {
                    "name": name,
                    "device_type": device_type,
                    "role": role,
                    "location": location,
                    "status": status,
                }

                ctx.info(f"Creating device with data: {device_data}")
                new_device = client.dcim.devices.create(**device_data)

                ctx.info(f"Successfully created device: {new_device.name}")
                return self.format_success(dict(new_device), message="Device created successfully")

            except Exception as e:
                return self.log_and_return_error(ctx, "creating device", e)

        @mcp.tool()
        def nautobot_update_device(ctx: Context, device_id: str, **kwargs) -> str:
            """Update an existing device in Nautobot.

            Args:
                ctx: MCP context for logging and progress
                device_id: Device ID (UUID) or name
                **kwargs: Fields to update (e.g., status, role, location, comments)

            Returns:
                JSON string of updated device details
            """
            ctx.info(f"Updating device: {device_id}")

            try:
                client = self._get_client()
                devices = client.dcim.devices

                # Get the device
                try:
                    device = devices.get(device_id)
                    ctx.debug(f"Found device by ID: {device_id}")
                except Exception:
                    ctx.debug(f"Searching device by name: {device_id}")
                    device = devices.get(name=device_id)

                if not device:
                    ctx.warning(f"Device not found: {device_id}")
                    return self.format_error(f"Device not found: {device_id}")

                # Update the device
                ctx.info(f"Updating device with data: {kwargs}")
                for key, value in kwargs.items():
                    setattr(device, key, value)
                device.save()

                ctx.info(f"Successfully updated device: {device.name}")
                return self.format_success(dict(device), message="Device updated successfully")

            except Exception as e:
                return self.log_and_return_error(ctx, "updating device", e)

        @mcp.tool()
        def nautobot_delete_device(ctx: Context, device_id: str) -> str:
            """Delete a device from Nautobot.

            Args:
                ctx: MCP context for logging and progress
                device_id: Device ID (UUID) or name

            Returns:
                JSON string confirming deletion
            """
            ctx.info(f"Deleting device: {device_id}")

            try:
                client = self._get_client()
                devices = client.dcim.devices

                # Get the device
                try:
                    device = devices.get(device_id)
                    ctx.debug(f"Found device by ID: {device_id}")
                except Exception:
                    ctx.debug(f"Searching device by name: {device_id}")
                    device = devices.get(name=device_id)

                if not device:
                    ctx.warning(f"Device not found: {device_id}")
                    return self.format_error(f"Device not found: {device_id}")

                device_name = device.name
                device.delete()

                ctx.info(f"Successfully deleted device: {device_name}")
                return self.format_success(
                    {"deleted": device_name}, message=f"Device '{device_name}' deleted successfully"
                )

            except Exception as e:
                return self.log_and_return_error(ctx, "deleting device", e)
