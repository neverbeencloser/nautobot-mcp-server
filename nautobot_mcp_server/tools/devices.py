"""Device-related tools for Nautobot MCP Server."""

from typing import Optional

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
        def nautobot_list_devices(ctx: Context, limit: int = 10, location: Optional[str] = None) -> str:
            """List all devices in Nautobot.

            Args:
                ctx: MCP context for logging and progress
                limit: Number of devices to return (default: 10)
                location: Filter devices by location name (optional)

            Returns:
                JSON string of device list
            """
            ctx.info(f"Listing devices (limit={limit}, location={location})")

            try:
                client = self._get_client()
                devices = client.dcim.devices

                if location:
                    ctx.debug(f"Filtering by location: {location}")
                    device_list = devices.filter(location=location, limit=limit)
                else:
                    device_list = devices.filter(limit=limit)

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
                    device = devices.get(id=device_id)
                    ctx.debug(f"Found device by ID: {device_id}")
                except RequestError:
                    # If not found by ID, try by name
                    ctx.debug(f"Searching device by name: {device_id}")
                    device = devices.get(name=device_id)

                if device:
                    device_info = {
                        "id": str(device.id),
                        "name": device.name,
                        "device_type": str(device.device_type) if device.device_type else None,
                        "role": str(device.role) if device.role else None,
                        "location": str(device.location) if device.location else None,
                        "status": str(device.status) if device.status else None,
                        "platform": str(device.platform) if device.platform else None,
                        "serial": device.serial if device.serial else None,
                        "asset_tag": device.asset_tag if device.asset_tag else None,
                        "primary_ip4": str(device.primary_ip4) if device.primary_ip4 else None,
                        "primary_ip6": str(device.primary_ip6) if device.primary_ip6 else None,
                        "comments": device.comments if device.comments else None,
                    }

                    ctx.info(f"Successfully retrieved device: {device.name}")
                    return self.format_success(device_info)
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
                name: Device name
                device_type: Device type name
                role: Device role name
                location: Location name
                status: Device status (default: "active")

            Returns:
                JSON string of created device details
            """
            ctx.info(f"Creating device: {name}")

            try:
                client = self._get_client()

                # Get the related objects first
                ctx.debug(f"Looking up device type: {device_type}")
                device_type_obj = client.dcim.device_types.get(model=device_type)
                if not device_type_obj:
                    ctx.error(f"Device type not found: {device_type}")
                    return self.format_error(f"Device type not found: {device_type}")

                ctx.debug(f"Looking up role: {role}")
                role_obj = client.extras.roles.get(name=role)
                if not role_obj:
                    ctx.error(f"Role not found: {role}")
                    return self.format_error(f"Role not found: {role}")

                ctx.debug(f"Looking up location: {location}")
                location_obj = client.dcim.locations.get(name=location)
                if not location_obj:
                    ctx.error(f"Location not found: {location}")
                    return self.format_error(f"Location not found: {location}")

                ctx.debug(f"Looking up status: {status}")
                status_obj = client.extras.statuses.get(name=status)
                if not status_obj:
                    ctx.error(f"Status not found: {status}")
                    return self.format_error(f"Status not found: {status}")

                # Create the device
                device_data = {
                    "name": name,
                    "device_type": device_type_obj.id,
                    "role": role_obj.id,
                    "location": location_obj.id,
                    "status": status_obj.id,
                }

                ctx.info(f"Creating device with data: {device_data}")
                new_device = client.dcim.devices.create(**device_data)

                device_info = {
                    "id": str(new_device.id),
                    "name": new_device.name,
                    "device_type": str(new_device.device_type) if new_device.device_type else None,
                    "role": str(new_device.role) if new_device.role else None,
                    "site": str(new_device.site) if new_device.site else None,
                    "status": str(new_device.status) if new_device.status else None,
                    "created": str(new_device.created) if new_device.created else None,
                    "url": new_device.url if hasattr(new_device, "url") else None,
                }

                ctx.info(f"Successfully created device: {new_device.name}")
                return self.format_success(device_info, message="Device created successfully")

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

                # Process update fields
                update_data = {}

                # Handle special fields that need object lookups
                if "status" in kwargs:
                    status_obj = client.extras.statuses.get(name=kwargs["status"])
                    if status_obj:
                        update_data["status"] = status_obj.id
                    else:
                        ctx.warning(f"Status not found: {kwargs['status']}")

                if "role" in kwargs:
                    role_obj = client.extras.roles.get(name=kwargs["role"])
                    if role_obj:
                        update_data["role"] = role_obj.id
                    else:
                        ctx.warning(f"Role not found: {kwargs['role']}")

                if "location" in kwargs:
                    location_obj = client.dcim.locations.get(name=kwargs["location"])
                    if location_obj:
                        update_data["location"] = location_obj.id
                    else:
                        ctx.warning(f"Location not found: {kwargs['location']}")

                # Handle simple fields
                simple_fields = ["comments", "serial", "asset_tag"]
                for field in simple_fields:
                    if field in kwargs:
                        update_data[field] = kwargs[field]

                # Update the device
                ctx.info(f"Updating device with data: {update_data}")
                for key, value in update_data.items():
                    setattr(device, key, value)
                device.save()

                device_info = {
                    "id": str(device.id),
                    "name": device.name,
                    "device_type": str(device.device_type) if device.device_type else None,
                    "role": str(device.role) if device.role else None,
                    "site": str(device.site) if device.site else None,
                    "status": str(device.status) if device.status else None,
                    "updated_fields": list(update_data.keys()),
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
