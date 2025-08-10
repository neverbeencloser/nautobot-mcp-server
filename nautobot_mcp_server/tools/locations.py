"""Location-related tools for Nautobot MCP Server."""

from typing import Optional

from mcp.server.fastmcp import Context, FastMCP

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
            limit: int = 10,
            status: Optional[str] = None
        ) -> str:
            """List all locations in Nautobot.
            
            Args:
                ctx: MCP context for logging and progress
                limit: Number of locations to return (default: 10)
                status: Filter locations by status (optional)
            
            Returns:
                JSON string of location list
            """
            ctx.info(f"Listing locations (limit={limit}, status={status})")

            try:
                client = self._get_client()
                locations_query = client.dcim.locations

                if status:
                    ctx.debug(f"Filtering by status: {status}")
                    locations = locations_query.filter(status=status, limit=limit)
                else:
                    locations = locations_query.filter(limit=limit)

                result = []
                for location in locations:
                    location_info = {
                        "id": str(location.id),
                        "name": location.name,
                        "natural_slug": location.natural_slug if hasattr(location, 'natural_slug') else None,
                        "tree_depth": location.tree_depth if hasattr(location, 'tree_depth') else None,
                        "status": str(location.status),
                        "location_type": str(location.location_type) if hasattr(location, 'location_type') and location.location_type else None,
                        "parent": str(location.parent) if hasattr(location, 'parent') and location.parent else None,
                        "facility": location.facility if hasattr(location, 'facility') else None,
                        "description": location.description if hasattr(location, 'description') else None,
                        "time_zone": location.time_zone if hasattr(location, 'time_zone') else None,
                        "physical_address": location.physical_address if hasattr(location, 'physical_address') else None
                    }
                    result.append(location_info)

                ctx.info(f"Found {len(result)} locations")
                return self.format_success(result)

            except Exception as e:
                return self.log_and_return_error(ctx, "listing locations", e)

        @mcp.tool()
        def nautobot_get_location(
            ctx: Context,
            location_id: str
        ) -> str:
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
                    location = locations.get(location_id)
                    ctx.debug(f"Found location by ID: {location_id}")
                except Exception:
                    # If not found by ID, try by name
                    try:
                        location = locations.get(name=location_id)
                        ctx.debug(f"Found location by name: {location_id}")
                    except Exception:
                        # If not found by name, try by natural_slug
                        location = locations.get(natural_slug=location_id)
                        ctx.debug(f"Found location by natural_slug: {location_id}")

                if location:
                    location_info = {
                        "id": str(location.id),
                        "name": location.name,
                        "natural_slug": location.natural_slug if hasattr(location, 'natural_slug') else None,
                        "tree_depth": location.tree_depth if hasattr(location, 'tree_depth') else None,
                        "time_zone": location.time_zone if hasattr(location, 'time_zone') else None,
                        "circuit_count": location.circuit_count if hasattr(location, 'circuit_count') else 0,
                        "device_count": location.device_count if hasattr(location, 'device_count') else 0,
                        "prefix_count": location.prefix_count if hasattr(location, 'prefix_count') else 0,
                        "rack_count": location.rack_count if hasattr(location, 'rack_count') else 0,
                        "virtual_machine_count": location.virtual_machine_count if hasattr(location, 'virtual_machine_count') else 0,
                        "vlan_count": location.vlan_count if hasattr(location, 'vlan_count') else 0,
                        "status": str(location.status),
                        "location_type": str(location.location_type) if hasattr(location, 'location_type') and location.location_type else None,
                        "parent": str(location.parent) if hasattr(location, 'parent') and location.parent else None,
                        "tenant": str(location.tenant) if hasattr(location, 'tenant') and location.tenant else None,
                        "facility": location.facility if hasattr(location, 'facility') else None,
                        "asn": location.asn if hasattr(location, 'asn') else None,
                        "description": location.description if hasattr(location, 'description') else None,
                        "physical_address": location.physical_address if hasattr(location, 'physical_address') else None,
                        "shipping_address": location.shipping_address if hasattr(location, 'shipping_address') else None,
                        "latitude": str(location.latitude) if hasattr(location, 'latitude') and location.latitude else None,
                        "longitude": str(location.longitude) if hasattr(location, 'longitude') and location.longitude else None,
                        "contact_name": location.contact_name if hasattr(location, 'contact_name') else None,
                        "contact_phone": location.contact_phone if hasattr(location, 'contact_phone') else None,
                        "contact_email": location.contact_email if hasattr(location, 'contact_email') else None,
                        "comments": location.comments if hasattr(location, 'comments') else None,
                        "created": str(location.created) if hasattr(location, 'created') else None,
                        "last_updated": str(location.last_updated) if hasattr(location, 'last_updated') else None
                    }

                    ctx.info(f"Successfully retrieved location: {location.name}")
                    return self.format_success(location_info)
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
            contact_email: Optional[str] = None
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
                try:
                    location_type_obj = client.dcim.location_types.get(location_type)
                except Exception:
                    try:
                        location_type_obj = client.dcim.location_types.get(name=location_type)
                    except Exception:
                        ctx.error(f"Location type not found: {location_type}")
                        return self.format_error(f"Location type not found: {location_type}")

                # Get parent location if specified
                parent_obj = None
                if parent:
                    ctx.debug(f"Looking up parent location: {parent}")
                    try:
                        parent_obj = client.dcim.locations.get(parent)
                    except Exception:
                        try:
                            parent_obj = client.dcim.locations.get(name=parent)
                        except Exception:
                            ctx.error(f"Parent location not found: {parent}")
                            return self.format_error(f"Parent location not found: {parent}")

                # Create the location
                location_data = {
                    "name": name,
                    "location_type": location_type_obj.id,
                    "status": status_obj.id
                }

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

                location_info = {
                    "id": str(new_location.id),
                    "name": new_location.name,
                    "natural_slug": new_location.natural_slug if hasattr(new_location, 'natural_slug') else None,
                    "status": str(new_location.status),
                    "location_type": str(new_location.location_type),
                    "created": str(new_location.created),
                    "url": new_location.url
                }

                ctx.info(f"Successfully created location: {new_location.name}")
                return self.format_success(
                    location_info,
                    message="Location created successfully"
                )

            except Exception as e:
                return self.log_and_return_error(ctx, "creating location", e)

        @mcp.tool()
        def nautobot_update_location(
            ctx: Context,
            location_id: str,
            **kwargs
        ) -> str:
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

                # Process update fields
                update_data = {}

                # Handle status field
                if "status" in kwargs:
                    status_obj = client.extras.statuses.get(name=kwargs["status"])
                    if status_obj:
                        update_data["status"] = status_obj.id
                    else:
                        ctx.warning(f"Status not found: {kwargs['status']}")

                # Handle location_type field
                if "location_type" in kwargs:
                    try:
                        location_type_obj = client.dcim.location_types.get(kwargs["location_type"])
                    except Exception:
                        try:
                            location_type_obj = client.dcim.location_types.get(name=kwargs["location_type"])
                        except Exception:
                            location_type_obj = None
                    
                    if location_type_obj:
                        update_data["location_type"] = location_type_obj.id
                    else:
                        ctx.warning(f"Location type not found: {kwargs['location_type']}")

                # Handle parent field
                if "parent" in kwargs:
                    if kwargs["parent"]:  # Non-empty parent
                        try:
                            parent_obj = client.dcim.locations.get(kwargs["parent"])
                        except Exception:
                            try:
                                parent_obj = client.dcim.locations.get(name=kwargs["parent"])
                            except Exception:
                                parent_obj = None
                        
                        if parent_obj:
                            update_data["parent"] = parent_obj.id
                        else:
                            ctx.warning(f"Parent location not found: {kwargs['parent']}")
                    else:  # Empty parent means remove parent
                        update_data["parent"] = None

                # Handle simple fields
                simple_fields = [
                    "description", "facility", "asn", "time_zone", "physical_address",
                    "shipping_address", "latitude", "longitude", "contact_name", 
                    "contact_phone", "contact_email", "comments"
                ]
                for field in simple_fields:
                    if field in kwargs:
                        update_data[field] = kwargs[field]

                # Update the location
                ctx.info(f"Updating location with data: {update_data}")
                for key, value in update_data.items():
                    setattr(location, key, value)
                location.save()

                location_info = {
                    "id": str(location.id),
                    "name": location.name,
                    "natural_slug": location.natural_slug if hasattr(location, 'natural_slug') else None,
                    "status": str(location.status),
                    "updated_fields": list(update_data.keys())
                }

                ctx.info(f"Successfully updated location: {location.name}")
                return self.format_success(
                    location_info,
                    message="Location updated successfully"
                )

            except Exception as e:
                return self.log_and_return_error(ctx, "updating location", e)

        @mcp.tool()
        def nautobot_delete_location(
            ctx: Context,
            location_id: str
        ) -> str:
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
                    {"deleted": location_name},
                    message=f"Location '{location_name}' deleted successfully"
                )

            except Exception as e:
                return self.log_and_return_error(ctx, "deleting location", e)