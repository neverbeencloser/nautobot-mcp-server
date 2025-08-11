"""Location-related tools for Nautobot MCP Server."""

from typing import Any, Optional

from mcp.server.fastmcp import Context, FastMCP
from pynautobot import RequestError

from .base import NautobotToolBase


class LocationTools(NautobotToolBase):
    """Tools for managing locations in Nautobot."""

    def register(self, mcp: FastMCP):
        """Register location tools with the MCP server.

        Args:
            mcp: FastMCP instance to register tools with
        """

        @mcp.tool()
        def nautobot_list_locations(
            ctx: Context,
            depth: int = 1,
            limit: int = 50,
            offset: int | None = None,
            location_type: str = None,
        ) -> str:
            """List all locations in Nautobot.

            Note that this returns a limited number of device fields to help with potential token size limitations.
            If token limit is reached, you can use limit and offset to paginate through results.

            Args:
                ctx: MCP context for logging and progress
                depth: Depth of the device details to return; default returns 1 level of nested objects.
                limit: Number of devices per page; pynautobot will return all devices unless offset is used.
                offset: Offset for pagination; if None, will return all devices.
                location_type: Location type name or ID to filter by (optional).

            Returns:
                JSON string of location list
            """
            ctx.info(
                f"Listing locations (depth={depth}, limit={limit}, offset={offset}, location_type={location_type})"
            )

            try:
                client = self._get_client()
                locations_query = client.dcim.locations

                kwargs = {}
                if location_type:
                    kwargs["location_type"] = location_type
                locations = locations_query.filter(depth=depth, limit=limit, offset=offset, **kwargs)

                # Build abbreviated list to help with potential token size limitations
                result = []
                for location in locations:
                    location_info = {
                        "id": str(location.id),
                        "name": location.name,
                        "natural_slug": location.natural_slug if hasattr(location, "natural_slug") else None,
                        "tree_depth": location.tree_depth if hasattr(location, "tree_depth") else None,
                        "status": str(location.status),
                        "location_type": str(location.location_type)
                        if hasattr(location, "location_type") and location.location_type
                        else None,
                        "parent": str(location.parent) if hasattr(location, "parent") and location.parent else None,
                        "facility": location.facility if hasattr(location, "facility") else None,
                        "description": location.description if hasattr(location, "description") else None,
                        "time_zone": location.time_zone if hasattr(location, "time_zone") else None,
                        "physical_address": location.physical_address
                        if hasattr(location, "physical_address")
                        else None,
                    }
                    result.append(location_info)

                ctx.info(f"Found {len(result)} locations")
                return self.format_success(result)

            except Exception as e:
                return self.log_and_return_error(ctx, "listing locations", e)

        @mcp.tool()
        def nautobot_get_location(ctx: Context, location_id: str, depth: int = 1) -> str:
            """Get a specific location by ID or name.

            Args:
                ctx: MCP context for logging and progress
                location_id: Location ID (UUID), name, or natural_slug
                depth: Depth of the device details to return; default returns 1 level of nested objects.

            Returns:
                JSON string of location details
            """
            ctx.info(f"Getting location: {location_id}")

            try:
                client = self._get_client()
                locations = client.dcim.locations

                # Try to get by ID first (UUID)
                try:
                    location = locations.get(id=location_id, depth=depth)
                    ctx.debug(f"Found location by ID: {location_id}")
                except Exception:
                    location = locations.get(name=location_id, depth=depth)
                    ctx.debug(f"Found location by name: {location_id}")

                if location:
                    ctx.info(f"Successfully retrieved location: {location.name}")
                    return self.format_success(dict(location), message="Location retrieved successfully")
                else:
                    ctx.warning(f"Location not found: {location_id}")
                    return self.format_error(f"Location not found: {location_id}")

            except Exception as e:
                return self.log_and_return_error(ctx, "getting location", e)

        @mcp.tool()
        def nautobot_create_location(
            ctx: Context,
            name: str,
            location_type: str,
            status: str = "active",
            parent: Optional[str] = None,
            description: Optional[str] = None,
            facility: Optional[str] = None,
            asn: Optional[int] = None,
            time_zone: Optional[str] = None,
            physical_address: Optional[str] = None,
            shipping_address: Optional[str] = None,
            latitude: Optional[str] = None,
            longitude: Optional[str] = None,
            contact_name: Optional[str] = None,
            contact_phone: Optional[str] = None,
            contact_email: Optional[str] = None,
        ) -> str:
            """Create a new location in Nautobot.

            Args:
                ctx: MCP context for logging and progress
                name: Location name
                location_type: Location type name or ID
                status: Location status (default: "active")
                parent: Parent location name or ID (optional)
                description: Location description (optional)
                facility: Facility identifier (optional)
                asn: Autonomous System Number (optional)
                time_zone: Time zone (optional)
                physical_address: Physical address (optional)
                shipping_address: Shipping address (optional)
                latitude: Latitude coordinate (optional)
                longitude: Longitude coordinate (optional)
                contact_name: Contact name (optional)
                contact_phone: Contact phone (optional)
                contact_email: Contact email (optional)

            Returns:
                JSON string of created location details
            """
            ctx.info(f"Creating location: {name}")

            try:
                # Capture function parameters before defining other locals
                params = locals().copy()
                params.pop("ctx")
                params.pop("self")

                client = self._get_client()

                # Get status object
                ctx.debug(f"Looking up status: {status}")
                status_obj = client.extras.statuses.get(name=status)
                if not status_obj:
                    ctx.error(f"Status not found: {status}")
                    return self.format_error(f"Status not found: {status}")

                # Get location type object
                ctx.debug(f"Looking up location type: {location_type}")
                location_type_obj = None
                try:
                    location_type_obj = client.dcim.location_types.get(id=location_type)
                except Exception:
                    try:
                        location_type_obj = client.dcim.location_types.get(name=location_type)
                    except Exception:
                        ctx.debug(f"Location type lookup failed for: {location_type}")

                if not location_type_obj:
                    ctx.error(f"Location type not found: {location_type}")
                    return self.format_error(f"Location type not found: {location_type}")

                # Get parent location if specified
                parent_obj = None
                if parent:
                    ctx.debug(f"Looking up parent location: {parent}")
                    try:
                        parent_obj = client.dcim.locations.get(id=parent)
                    except Exception:
                        try:
                            parent_obj = client.dcim.locations.get(name=parent)
                        except Exception:
                            ctx.error(f"Parent location not found: {parent}")
                            return self.format_error(f"Parent location not found: {parent}")

                # Build location data from non-None parameters
                location_data = {k: v for k, v in params.items() if v is not None}

                # Override with resolved objects
                location_data["location_type"] = location_type_obj.id
                location_data["status"] = status_obj.id
                if parent_obj:
                    location_data["parent"] = parent_obj.id

                ctx.info(f"Creating location with data: {location_data}")
                new_location = client.dcim.locations.create(**location_data)

                location_info = {
                    "id": str(new_location.id),
                    "name": new_location.name,
                    "natural_slug": new_location.natural_slug if hasattr(new_location, "natural_slug") else None,
                    "status": str(new_location.status),
                    "location_type": str(new_location.location_type),
                    "created": str(new_location.created),
                    "url": new_location.url,
                }

                ctx.info(f"Successfully created location: {new_location.name}")
                return self.format_success(location_info, message="Location created successfully")

            except Exception as e:
                return self.log_and_return_error(ctx, "creating location", e)

        @mcp.tool()
        def nautobot_update_location(
            ctx: Context,
            location_id: str,
            updates: dict[str, Any],
        ) -> str:
            """
            Update location fields for an existing location.

            Use 'schema://location/fields' MCP Resource to get available fields.

            Args:
                ctx: MCP context for logging and progress
                location_id: Location ID (UUID); must GET location first if you don't know the ID.
                updates: Field updates dict. Set None to clear fields.

            Returns:
                JSON string of updated location details or error message
            """
            ctx.info(f"Updating location: {location_id}")

            try:
                client = self._get_client()
                locations = client.dcim.locations

                # Get the location
                try:
                    location = locations.get(id=location_id)
                    ctx.debug(f"Found location by ID: {location_id}")
                except RequestError:
                    ctx.warning(f"Location not found: {location_id}")
                    return self.format_error(f"Location not found: {location_id}")

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

                ctx.info(f"Updating location with data: {updates}")
                location.update(updates)

                location_info = {
                    "id": str(location.id),
                    "name": location.name,
                    "natural_slug": location.natural_slug if hasattr(location, "natural_slug") else None,
                    "status": str(location.status),
                    "updated_fields": fields_to_update,
                    "cleared_fields": fields_to_clear,
                }

                ctx.info(f"Successfully updated location: {location.name}")
                return self.format_success(location_info, message="Location updated successfully")

            except Exception as e:
                return self.log_and_return_error(ctx, "updating location", e)

        @mcp.tool()
        def nautobot_delete_location(ctx: Context, location_id: str) -> str:
            """Delete a location from Nautobot.

            Args:
                ctx: MCP context for logging and progress
                location_id: Location ID (UUID)

            Returns:
                JSON string confirming deletion
            """
            ctx.info(f"Deleting location: {location_id}")

            try:
                client = self._get_client()
                locations = client.dcim.locations

                # Get the location
                try:
                    location = locations.get(location_id)
                    ctx.debug(f"Found location by ID: {location_id}")
                except Exception:
                    ctx.warning(f"Location not found: {location_id}")
                    return self.format_error(f"Location not found: {location_id}")

                location_name = location.name
                location.delete()

                ctx.info(f"Successfully deleted location: {location_id}:{location_name}")
                return self.format_success(
                    {"deleted": location_name}, message=f"Location '{location_id}:{location_name}' deleted successfully"
                )

            except Exception as e:
                return self.log_and_return_error(ctx, "deleting location", e)
