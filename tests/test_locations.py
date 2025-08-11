"""Tests for location management tools."""

import json
import unittest
from unittest.mock import MagicMock

from pynautobot import RequestError

from nautobot_mcp_server.tools.locations import LocationTools

from .conftest import MockRecord


class TestLocationTools(unittest.TestCase):
    """Test location management functionality."""

    def setUp(self):
        """Set up test fixtures using simple mocks."""
        # Create mock client
        self.mock_client = MagicMock()

        # Create mock context
        self.mock_context = MagicMock()

        # Create location tools instance
        self.location_tools = LocationTools(lambda: self.mock_client)

        # Create simple mock location
        self.mock_location = MockRecord(
            id="location-123",
            name="test-location",
            location_type=MagicMock(__str__=lambda self: "Site"),
            status=MagicMock(__str__=lambda self: "Active"),
            parent=None,
            description="Test location",
            natural_slug="test-location",
            created="2024-01-01T00:00:00Z",
            url="https://nautobot.example.com/location/123",
        )

    def _register_and_get_function(self, function_index):
        """Helper to register tools and get function."""
        mcp_mock = MagicMock()
        tool_decorator_mock = MagicMock()
        mcp_mock.tool.return_value = tool_decorator_mock

        self.location_tools.register(mcp_mock)

        return tool_decorator_mock.call_args_list[function_index][0][0]

    def test_list_locations_success(self):
        """Test successful location listing."""
        # Create another mock location
        mock_location2 = MockRecord(
            id="location-456",
            name="test-location-2",
            location_type=MagicMock(__str__=lambda self: "Building"),
            status=MagicMock(__str__=lambda self: "Active"),
            parent=MagicMock(__str__=lambda self: "test-location"),
            description="Another location",
        )

        self.mock_client.dcim.locations.filter.return_value = [self.mock_location, mock_location2]

        list_locations_func = self._register_and_get_function(0)
        result = list_locations_func(self.mock_context, limit=10)

        # Verify result
        parsed = json.loads(result)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["name"], "test-location")
        self.assertEqual(parsed[0]["id"], "location-123")
        self.assertEqual(parsed[1]["name"], "test-location-2")

        # Verify client was called correctly with depth and offset parameters
        self.mock_client.dcim.locations.filter.assert_called_once_with(depth=1, limit=10, offset=None)
        self.mock_context.info.assert_called()

    def test_list_locations_with_status_filter(self):
        """Test location listing with location_type filter."""
        self.mock_client.dcim.locations.filter.return_value = []

        list_locations_func = self._register_and_get_function(0)
        result = list_locations_func(self.mock_context, limit=5, location_type="datacenter")

        # Verify client was called with location_type filter and default parameters
        self.mock_client.dcim.locations.filter.assert_called_once_with(
            depth=1, limit=5, offset=None, location_type="datacenter"
        )

        # Verify empty result
        parsed = json.loads(result)
        self.assertEqual(parsed, [])

    def test_list_locations_exception(self):
        """Test location listing with exception."""
        self.mock_client.dcim.locations.filter.side_effect = Exception("API Error")

        list_locations_func = self._register_and_get_function(0)
        result = list_locations_func(self.mock_context, limit=10)

        # Verify error response
        parsed = json.loads(result)
        self.assertIn("error", parsed)
        self.assertIn("API Error", parsed["error"])
        self.mock_context.error.assert_called_once()

    def test_get_location_success(self):
        """Test successful location retrieval."""
        self.mock_client.dcim.locations.get.return_value = self.mock_location

        get_location_func = self._register_and_get_function(1)
        result = get_location_func(self.mock_context, "location-123")

        # Verify result
        parsed = json.loads(result)
        self.assertEqual(parsed["data"]["name"], "test-location")
        self.assertEqual(parsed["data"]["id"], "location-123")
        self.assertEqual(parsed["data"]["location_type"], "Site")

        # Verify client was called correctly with depth parameter
        self.mock_client.dcim.locations.get.assert_called_with(id="location-123", depth=1)

    def test_get_location_not_found(self):
        """Test location not found scenario."""
        mock_request = MagicMock()
        mock_request.status_code = 404
        self.mock_client.dcim.locations.get.side_effect = [RequestError(mock_request), None]

        get_location_func = self._register_and_get_function(1)
        result = get_location_func(self.mock_context, "nonexistent-location")

        # Verify error response
        parsed = json.loads(result)
        self.assertIn("error", parsed)
        self.assertIn("Location not found", parsed["error"])

    def test_create_location_success(self):
        """Test successful location creation."""
        # Mock related object lookups - first try ID lookup fails, then name lookup succeeds
        mock_location_type = MockRecord(id="type-123")
        self.mock_client.dcim.location_types.get.side_effect = [Exception("Not found by ID"), mock_location_type]

        mock_status = MockRecord(id="status-123")
        self.mock_client.extras.statuses.get.return_value = mock_status

        # Mock location creation
        self.mock_client.dcim.locations.create.return_value = self.mock_location

        create_location_func = self._register_and_get_function(2)
        result = create_location_func(self.mock_context, name="new-location", location_type="Site", status="active")

        # Verify result
        parsed = json.loads(result)
        self.assertTrue(parsed["success"])
        self.assertEqual(parsed["data"]["name"], "test-location")
        self.assertIn("created successfully", parsed["message"])

        # Verify lookups were performed - first ID, then name
        calls = self.mock_client.dcim.location_types.get.call_args_list
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0][1], {"id": "Site"})
        self.assertEqual(calls[1][1], {"name": "Site"})
        self.mock_client.extras.statuses.get.assert_called_once_with(name="active")

    def test_create_location_missing_location_type(self):
        """Test location creation with missing location type."""
        self.mock_client.dcim.location_types.get.return_value = None

        create_location_func = self._register_and_get_function(2)
        result = create_location_func(self.mock_context, name="new-location", location_type="NonexistentType")

        # Verify error response
        parsed = json.loads(result)
        self.assertIn("error", parsed)
        self.assertIn("Location type not found", parsed["error"])

    def test_update_location_success(self):
        """Test successful location update."""
        self.mock_client.dcim.locations.get.return_value = self.mock_location

        # Mock status lookup for update
        mock_status = MockRecord(id="status-456")
        self.mock_client.extras.statuses.get.return_value = mock_status

        update_location_func = self._register_and_get_function(3)
        result = update_location_func(
            self.mock_context, location_id="location-123", status="maintenance", description="Updated description"
        )

        # Verify result
        parsed = json.loads(result)
        self.assertTrue(parsed["success"])
        self.assertEqual(parsed["data"]["name"], "test-location")
        self.assertIn("status", parsed["data"]["updated_fields"])
        self.assertIn("description", parsed["data"]["updated_fields"])

        # Verify location was saved
        self.assertTrue(hasattr(self.mock_location, "update"))

    def test_delete_location_success(self):
        """Test successful location deletion."""
        self.mock_client.dcim.locations.get.return_value = self.mock_location

        delete_location_func = self._register_and_get_function(4)
        result = delete_location_func(self.mock_context, "location-123")

        # Verify result
        parsed = json.loads(result)
        self.assertTrue(parsed["success"])
        self.assertEqual(parsed["data"]["deleted"], "test-location")
        self.assertIn("deleted successfully", parsed["message"])

    def test_delete_location_not_found(self):
        """Test location deletion when location not found."""
        mock_request = MagicMock()
        mock_request.status_code = 404
        self.mock_client.dcim.locations.get.side_effect = [RequestError(mock_request), None]

        delete_location_func = self._register_and_get_function(4)
        result = delete_location_func(self.mock_context, "nonexistent-location")

        # Verify error response
        parsed = json.loads(result)
        self.assertIn("error", parsed)
        self.assertIn("Location not found", parsed["error"])
