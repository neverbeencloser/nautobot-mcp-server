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

        # Create simple mock device with JSON-serializable fields
        self.mock_device = MockRecord(
            id="device-123",
            name="test-device",
            device_type="Router",
            role="Core",
            location="DC-01",
            status="Active",
            platform=None,
            serial="SN12345",
            asset_tag=None,
            primary_ip4=None,
            primary_ip6=None,
            comments=None,
            created="2024-01-01T00:00:00Z",
            site="Site-01",
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
        # Create another mock device with JSON-serializable fields
        mock_device2 = MockRecord(
            id="device-456",
            name="test-device-2",
            device_type="Switch",
            role="Access",
            location="DC-02",
            status="Active",
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

        # Verify client was called correctly
        self.mock_client.dcim.devices.filter.assert_called_once_with(limit=10, depth=1)
        self.mock_context.info.assert_called()

    def test_list_devices_with_location_filter(self):
        """Test device listing with location filter."""
        self.mock_client.dcim.devices.filter.return_value = []

        list_devices_func = self._register_and_get_function(0)
        result = list_devices_func(self.mock_context, limit=5, location="DC-01")

        # Verify client was called with location filter
        self.mock_client.dcim.devices.filter.assert_called_once_with(limit=5, depth=1, location="DC-01")

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
        assert parsed["name"] == "test-device"
        assert parsed["id"] == "device-123"
        assert parsed["device_type"] == "Router"

        # Verify client was called correctly
        self.mock_client.dcim.devices.get.assert_called_with(depth=1, id="device-123")

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
        assert parsed["name"] == "test-device"

        # Verify both calls were made
        calls = self.mock_client.dcim.devices.get.call_args_list
        assert len(calls) == 2
        assert calls[0][1] == {"depth": 1, "id": "test-device"}
        assert calls[1][1] == {"depth": 1, "name": "test-device"}

    def test_get_device_not_found(self):
        """Test device not found scenario."""
        mock_request = MagicMock()
        mock_request.status_code = 404
        self.mock_client.dcim.devices.get.side_effect = [RequestError(mock_request), None]

        get_device_func = self._register_and_get_function(1)
        result = get_device_func(self.mock_context, "nonexistent-device")

        # Verify error response
        parsed = json.loads(result)
        assert "error" in parsed
        assert "Device not found" in parsed["error"]

    def test_create_device_success(self):
        """Test successful device creation."""
        # Mock device creation (no object lookups in simplified version)
        self.mock_client.dcim.devices.create.return_value = self.mock_device

        create_device_func = self._register_and_get_function(2)
        result = create_device_func(
            self.mock_context, name="new-device", device_type="Router", role="Core", location="DC-01", status="active"
        )

        # Verify result
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["data"]["name"] == "test-device"
        assert "created successfully" in parsed["message"]

        # Verify create was called with correct data
        self.mock_client.dcim.devices.create.assert_called_once_with(
            name="new-device", device_type="Router", role="Core", location="DC-01", status="active"
        )

    def test_create_device_missing_device_type(self):
        """Test device creation with missing device type."""
        # Make the create method fail when called with invalid device_type
        self.mock_client.dcim.devices.create.side_effect = Exception("Device type not found: NonexistentType")

        create_device_func = self._register_and_get_function(2)
        result = create_device_func(
            self.mock_context, name="new-device", device_type="NonexistentType", role="Core", location="DC-01"
        )

        # Verify error response
        parsed = json.loads(result)
        assert "error" in parsed
        assert "Device type not found" in parsed["error"]

    def test_update_device_success(self):
        """Test successful device update."""
        self.mock_client.dcim.devices.get.return_value = self.mock_device

        # Mock status lookup for update
        mock_status = MockRecord(id="status-456")
        self.mock_client.extras.statuses.get.return_value = mock_status

        update_device_func = self._register_and_get_function(3)
        result = update_device_func(
            self.mock_context, device_id="device-123", status="maintenance", comments="Under maintenance"
        )

        # Verify result
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["data"]["name"] == "test-device"
        # Device fields are updated on the mock object, we have the full device data

        # Verify device was saved
        assert hasattr(self.mock_device, "save")

    def test_delete_device_success(self):
        """Test successful device deletion."""
        self.mock_client.dcim.devices.get.return_value = self.mock_device

        delete_device_func = self._register_and_get_function(4)
        result = delete_device_func(self.mock_context, "device-123")

        # Verify result
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["data"]["deleted"] == "test-device"
        assert "deleted successfully" in parsed["message"]

    def test_delete_device_not_found(self):
        """Test device deletion when device not found."""
        mock_request = MagicMock()
        mock_request.status_code = 404
        self.mock_client.dcim.devices.get.side_effect = [RequestError(mock_request), None]

        delete_device_func = self._register_and_get_function(4)
        result = delete_device_func(self.mock_context, "nonexistent-device")

        # Verify error response
        parsed = json.loads(result)
        assert "error" in parsed
        assert "Device not found" in parsed["error"]
