"""Tests for device management tools."""

import json
import unittest
from unittest.mock import MagicMock

from pynautobot import RequestError

from nautobot_mcp_server.tools.devices import DeviceTools

from .conftest import MockRecord


class TestDeviceTools(unittest.TestCase):
    """Test device management functionality."""

    def setUp(self):
        """Set up test fixtures using simple mocks."""
        # Create mock client
        self.mock_client = MagicMock()

        # Create mock context
        self.mock_context = MagicMock()

        # Create device tools instance
        self.device_tools = DeviceTools(lambda: self.mock_client)

        # Create simple mock device
        self.mock_device = MockRecord(
            id="device-123",
            name="test-device",
            device_type=MagicMock(__str__=lambda self: "Router"),
            role=MagicMock(__str__=lambda self: "Core"),
            location=MagicMock(__str__=lambda self: "DC-01"),
            status=MagicMock(__str__=lambda self: "Active"),
            platform=None,
            serial="SN12345",
            asset_tag=None,
            primary_ip4=None,
            primary_ip6=None,
            comments=None,
            created="2024-01-01T00:00:00Z",
            site=MagicMock(__str__=lambda self: "Site-01"),
            url="https://nautobot.example.com/device/123",
        )

    def _register_and_get_function(self, function_index):
        """Helper to register tools and get function."""
        mcp_mock = MagicMock()
        tool_decorator_mock = MagicMock()
        mcp_mock.tool.return_value = tool_decorator_mock

        self.device_tools.register(mcp_mock)

        return tool_decorator_mock.call_args_list[function_index][0][0]

    def test_list_devices_success(self):
        """Test successful device listing."""
        # Create another mock device
        mock_device2 = MockRecord(
            id="device-456",
            name="test-device-2",
            device_type=MagicMock(__str__=lambda self: "Switch"),
            role=MagicMock(__str__=lambda self: "Access"),
            location=MagicMock(__str__=lambda self: "DC-02"),
            status=MagicMock(__str__=lambda self: "Active"),
            platform=None,
            serial=None,
            primary_ip4=None,
            primary_ip6=None,
        )

        self.mock_client.dcim.devices.filter.return_value = [self.mock_device, mock_device2]

        list_devices_func = self._register_and_get_function(0)
        result = list_devices_func(self.mock_context, limit=10)

        # Verify result
        parsed = json.loads(result)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["name"], "test-device")
        self.assertEqual(parsed[0]["id"], "device-123")
        self.assertEqual(parsed[1]["name"], "test-device-2")

        # Verify client was called correctly with depth and offset parameters
        self.mock_client.dcim.devices.filter.assert_called_once_with(depth=1, limit=10, offset=None)
        self.mock_context.info.assert_called()

    def test_list_devices_with_location_filter(self):
        """Test device listing with location filter."""
        self.mock_client.dcim.devices.filter.return_value = []

        list_devices_func = self._register_and_get_function(0)
        result = list_devices_func(self.mock_context, limit=5, location="DC-01")

        # Verify client was called with location filter and default parameters
        self.mock_client.dcim.devices.filter.assert_called_once_with(depth=1, limit=5, offset=None, location="DC-01")

        # Verify empty result
        parsed = json.loads(result)
        self.assertEqual(parsed, [])

    def test_list_devices_exception(self):
        """Test device listing with exception."""
        self.mock_client.dcim.devices.filter.side_effect = Exception("API Error")

        list_devices_func = self._register_and_get_function(0)
        result = list_devices_func(self.mock_context, limit=10)

        # Verify error response
        parsed = json.loads(result)
        self.assertIn("error", parsed)
        self.assertIn("API Error", parsed["error"])
        self.mock_context.error.assert_called_once()

    def test_get_device_by_id_success(self):
        """Test successful device retrieval by ID."""
        self.mock_client.dcim.devices.get.return_value = self.mock_device

        get_device_func = self._register_and_get_function(1)
        result = get_device_func(self.mock_context, "device-123")

        # Verify result
        parsed = json.loads(result)
        self.assertTrue(parsed["success"])
        self.assertEqual(parsed["message"], "Device retrieved successfully")
        self.assertEqual(parsed["data"]["name"], "test-device")
        self.assertEqual(parsed["data"]["id"], "device-123")
        self.assertEqual(parsed["data"]["device_type"], "Router")

        # Verify client was called correctly with depth parameter
        self.mock_client.dcim.devices.get.assert_called_with(id="device-123", depth=1)

    def test_get_device_by_name_fallback(self):
        """Test device retrieval by name when ID lookup fails."""
        # Mock ID lookup failure, then success by name
        mock_request = MagicMock()
        mock_request.status_code = 404
        self.mock_client.dcim.devices.get.side_effect = [RequestError(mock_request), self.mock_device]

        get_device_func = self._register_and_get_function(1)
        result = get_device_func(self.mock_context, "test-device")

        # Verify result
        parsed = json.loads(result)
        self.assertTrue(parsed["success"])
        self.assertEqual(parsed["message"], "Device retrieved successfully")
        self.assertEqual(parsed["data"]["name"], "test-device")

        # Verify both calls were made with depth parameter
        calls = self.mock_client.dcim.devices.get.call_args_list
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0][1], {"id": "test-device", "depth": 1})
        self.assertEqual(calls[1][1], {"name": "test-device", "depth": 1})

    def test_get_device_not_found(self):
        """Test device not found scenario."""
        mock_request = MagicMock()
        mock_request.status_code = 404
        self.mock_client.dcim.devices.get.side_effect = [RequestError(mock_request), None]

        get_device_func = self._register_and_get_function(1)
        result = get_device_func(self.mock_context, "nonexistent-device")

        # Verify error response
        parsed = json.loads(result)
        self.assertIn("error", parsed)
        self.assertIn("Device not found", parsed["error"])

    def test_create_device_success(self):
        """Test successful device creation."""
        # Mock device creation
        self.mock_client.dcim.devices.create.return_value = self.mock_device

        create_device_func = self._register_and_get_function(2)
        result = create_device_func(
            self.mock_context, name="new-device", device_type="Router", role="Core", location="DC-01", status="active"
        )

        # Verify result
        parsed = json.loads(result)
        self.assertTrue(parsed["success"])
        self.assertEqual(parsed["data"]["name"], "test-device")
        self.assertIn("created successfully", parsed["message"])

        # Verify device creation was called with correct parameters
        self.mock_client.dcim.devices.create.assert_called_once_with(
            name="new-device", device_type="Router", role="Core", location="DC-01", status="active"
        )

    def test_create_device_missing_device_type(self):
        """Test device creation with invalid device type."""
        # Mock device creation failure due to invalid device type
        from pynautobot import RequestError

        mock_request = MagicMock()
        mock_request.status_code = 400
        self.mock_client.dcim.devices.create.side_effect = RequestError(mock_request)

        create_device_func = self._register_and_get_function(2)
        result = create_device_func(
            self.mock_context,
            name="new-device",
            device_type="NonexistentType",
            role="Core",
            location="DC-01",
            status="active",
        )

        # Verify error response
        parsed = json.loads(result)
        self.assertIn("error", parsed)

    def test_update_device_success(self):
        """Test successful device update."""
        self.mock_client.dcim.devices.get.return_value = self.mock_device

        # Mock status lookup for update
        mock_status = MockRecord(id="status-456")
        self.mock_client.extras.statuses.get.return_value = mock_status

        update_device_func = self._register_and_get_function(3)
        result = update_device_func(
            self.mock_context,
            device_id="device-123",
            updates={"status": "maintenance", "comments": "Under maintenance"},
        )

        # Verify result
        parsed = json.loads(result)
        self.assertTrue(parsed["success"])
        self.assertEqual(parsed["data"]["name"], "test-device")
        self.assertIn("status", parsed["data"]["updated_fields"])
        self.assertIn("comments", parsed["data"]["updated_fields"])

        # Verify device was saved
        self.assertTrue(hasattr(self.mock_device, "update"))

    def test_update_device_with_none_values(self):
        """Test device update with None values to clear fields."""
        # Create a mock device with a mocked update method
        from unittest.mock import MagicMock

        mock_device = MockRecord(
            id="device-123",
            name="test-device",
            device_type="test-type",
            role="test-role",
            location="test-location",
            status="active",
            url="http://nautobot/devices/device-123",
        )
        # Replace update method with a MagicMock to track calls
        mock_device.update = MagicMock(side_effect=mock_device.update)

        self.mock_client.dcim.devices.get.return_value = mock_device

        update_device_func = self._register_and_get_function(3)
        result = update_device_func(
            self.mock_context,
            device_id="device-123",
            updates={"asset_tag": None, "serial": None, "comments": "Cleared some fields"},
        )

        # Verify result
        parsed = json.loads(result)
        self.assertTrue(parsed["success"])
        self.assertEqual(parsed["data"]["name"], "test-device")
        self.assertIn("asset_tag", parsed["data"]["updated_fields"])
        self.assertIn("serial", parsed["data"]["updated_fields"])
        self.assertIn("comments", parsed["data"]["updated_fields"])
        self.assertIn("asset_tag", parsed["data"]["cleared_fields"])
        self.assertIn("serial", parsed["data"]["cleared_fields"])
        self.assertNotIn("comments", parsed["data"]["cleared_fields"])

        # Verify update was called with None values
        mock_device.update.assert_called_once()
        update_args = mock_device.update.call_args[0][0]
        self.assertIsNone(update_args["asset_tag"])
        self.assertIsNone(update_args["serial"])
        self.assertEqual(update_args["comments"], "Cleared some fields")

    def test_update_device_invalid_updates_parameter(self):
        """Test device update with invalid updates parameter."""
        self.mock_client.dcim.devices.get.return_value = self.mock_device

        update_device_func = self._register_and_get_function(3)
        result = update_device_func(
            self.mock_context,
            device_id="device-123",
            updates="not a dictionary",  # Invalid parameter type
        )

        # Verify error response
        parsed = json.loads(result)
        self.assertIn("error", parsed)
        self.assertIn("dictionary", parsed["error"])

    def test_delete_device_success(self):
        """Test successful device deletion."""
        self.mock_client.dcim.devices.get.return_value = self.mock_device

        delete_device_func = self._register_and_get_function(4)
        result = delete_device_func(self.mock_context, "device-123")

        # Verify result
        parsed = json.loads(result)
        self.assertTrue(parsed["success"])
        self.assertEqual(parsed["data"]["deleted"], "test-device")
        self.assertIn("deleted successfully", parsed["message"])

    def test_delete_device_not_found(self):
        """Test device deletion when device not found."""
        mock_request = MagicMock()
        mock_request.status_code = 404
        self.mock_client.dcim.devices.get.side_effect = [RequestError(mock_request), None]

        delete_device_func = self._register_and_get_function(4)
        result = delete_device_func(self.mock_context, "nonexistent-device")

        # Verify error response
        parsed = json.loads(result)
        self.assertIn("error", parsed)
        self.assertIn("Device not found", parsed["error"])
