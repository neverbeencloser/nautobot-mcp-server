"""Location-related tools for Nautobot MCP Server."""

from typing import Optional

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
        def nautobot_list_locations(ctx: Context, limit: int = 10, **kwargs) -> str:
            """List all locations in Nautobot.

            Args:
                ctx: MCP context for logging and progress
                limit: Number of locations to return (default: 10)
                kwargs: Filter locations by kwargs (optional)

            Returns:
                JSON string of location list
            """
            ctx.info(f"Listing locations (limit={limit}, kwargs={kwargs})")

            try:
                client = self._get_client()
                locations = client.dcim.locations
                filter_kwargs = {}

                if "status" in kwargs:
                    ctx.debug(f"Filtering by status: {kwargs['status']}")
                    filter_kwargs["status"] = kwargs["status"]

                location_list = locations.filter(limit=limit, depth=1, **filter_kwargs)

                ctx.info(f"Found {len(location_list)} locations")
                return self.format_success([dict(location) for location in location_list])

            except Exception as e:
                return self.log_and_return_error(ctx, "listing locations", e)

        @mcp.tool()
        def nautobot_get_location(ctx: Context, location_id: str) -> str:
            """Get a specific location by ID or name.

            Args:
                ctx: MCP context for logging and progress
                location_id: Location ID (UUID), name, or natural_slug

            Returns:
                JSON string of location details
            """
            ctx.info(f"Getting location: {location_id}")

            try:
                client = self._get_client()
                locations = client.dcim.locations

                # Try to get by ID first (UUID)
                try:
                    location = locations.get(id=location_id)
                    ctx.debug(f"Found location by ID: {location_id}")
                except RequestError:
                    # If not found by ID, try by name
                    try:
                        location = locations.get(name=location_id)
                        ctx.debug(f"Found location by name: {location_id}")
                    except RequestError:
                        # If not found by name, try by natural_slug
                        location = locations.get(natural_slug=location_id)
                        ctx.debug(f"Found location by natural_slug: {location_id}")

                if location:
                    ctx.info(f"Successfully retrieved location: {location.name}")
                    return self.format_success(dict(location))
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

                # Create the location
                location_data = {"name": name, "location_type": location_type_obj.id, "status": status_obj.id}

                # Add optional fields
                if parent_obj:
                    location_data["parent"] = parent_obj.id
                if description:
                    location_data["description"] = description
                if facility:
                    location_data["facility"] = facility
                if asn is not None:
                    location_data["asn"] = asn
                if time_zone:
                    location_data["time_zone"] = time_zone
                if physical_address:
                    location_data["physical_address"] = physical_address
                if shipping_address:
                    location_data["shipping_address"] = shipping_address
                if latitude:
                    location_data["latitude"] = latitude
                if longitude:
                    location_data["longitude"] = longitude
                if contact_name:
                    location_data["contact_name"] = contact_name
                if contact_phone:
                    location_data["contact_phone"] = contact_phone
                if contact_email:
                    location_data["contact_email"] = contact_email

                ctx.info(f"Creating location with data: {location_data}")
                new_location = client.dcim.locations.create(**location_data)

                ctx.info(f"Successfully created location: {new_location.name}")
                return self.format_success(dict(new_location), message="Location created successfully")

            except Exception as e:
                return self.log_and_return_error(ctx, "creating location", e)

        @mcp.tool()
        def nautobot_update_location(ctx: Context, location_id: str, **kwargs) -> str:
            """Update an existing location in Nautobot.

            Args:
                ctx: MCP context for logging and progress
                location_id: Location ID (UUID), name, or natural_slug
                **kwargs: Fields to update (e.g., status, description, facility, parent)

            Returns:
                JSON string of updated location details
            """
            ctx.info(f"Updating location: {location_id}")

            try:
                client = self._get_client()
                locations = client.dcim.locations

                # Get the location
                try:
                    location = locations.get(location_id)
                    ctx.debug(f"Found location by ID: {location_id}")
                except Exception:
                    try:
                        location = locations.get(name=location_id)
                        ctx.debug(f"Found location by name: {location_id}")
                    except Exception:
                        location = locations.get(natural_slug=location_id)
                        ctx.debug(f"Found location by natural_slug: {location_id}")

                if not location:
                    ctx.warning(f"Location not found: {location_id}")
                    return self.format_error(f"Location not found: {location_id}")

                # Update the location
                ctx.info(f"Updating location with data: {kwargs}")
                for key, value in kwargs.items():
                    setattr(location, key, value)
                location.save()

                ctx.info(f"Successfully updated location: {location.name}")
                return self.format_success(dict(location), message="Location updated successfully")

            except Exception as e:
                return self.log_and_return_error(ctx, "updating location", e)

        @mcp.tool()
        def nautobot_delete_location(ctx: Context, location_id: str) -> str:
            """Delete a location from Nautobot.

            Args:
                ctx: MCP context for logging and progress
                location_id: Location ID (UUID), name, or natural_slug

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
                    try:
                        location = locations.get(name=location_id)
                        ctx.debug(f"Found location by name: {location_id}")
                    except Exception:
                        location = locations.get(natural_slug=location_id)
                        ctx.debug(f"Found location by natural_slug: {location_id}")

                if not location:
                    ctx.warning(f"Location not found: {location_id}")
                    return self.format_error(f"Location not found: {location_id}")

                location_name = location.name
                location.delete()

                ctx.info(f"Successfully deleted location: {location_name}")
                return self.format_success(
                    {"deleted": location_name}, message=f"Location '{location_name}' deleted successfully"
                )

            except Exception as e:
                return self.log_and_return_error(ctx, "deleting location", e)
