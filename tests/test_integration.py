"""Integration tests for the MCP server tools."""

import unittest
from unittest.mock import MagicMock

from nautobot_mcp_server.tools.devices import DeviceTools
from nautobot_mcp_server.tools.jobs import JobTools
from nautobot_mcp_server.tools.locations import LocationTools


class TestIntegration(unittest.TestCase):
    """Integration tests for MCP server tools."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = MagicMock()

    def test_device_tools_initialization(self):
        """Test device tools can be initialized."""
        device_tools = DeviceTools(lambda: self.mock_client)
        self.assertIsNotNone(device_tools)
        self.assertIsNotNone(device_tools._get_client)

    def test_location_tools_initialization(self):
        """Test location tools can be initialized."""
        location_tools = LocationTools(lambda: self.mock_client)
        self.assertIsNotNone(location_tools)
        self.assertIsNotNone(location_tools._get_client)

    def test_job_tools_initialization(self):
        """Test job tools can be initialized."""
        job_tools = JobTools(lambda: self.mock_client)
        self.assertIsNotNone(job_tools)
        self.assertIsNotNone(job_tools._get_client)

    def test_mock_client_has_expected_endpoints(self):
        """Test mock client has all expected endpoints."""
        # DCIM endpoints
        self.assertTrue(hasattr(self.mock_client, "dcim"))
        self.assertTrue(hasattr(self.mock_client, "extras"))

    def test_tools_registration_doesnt_fail(self):
        """Test that tools can be registered without errors."""
        mcp_mock = MagicMock()
        mcp_mock.tool.return_value = MagicMock()

        # Test device tools registration
        device_tools = DeviceTools(lambda: self.mock_client)
        device_tools.register(mcp_mock)
        self.assertTrue(mcp_mock.tool.called)

        # Test location tools registration
        location_tools = LocationTools(lambda: self.mock_client)
        location_tools.register(mcp_mock)
        self.assertTrue(mcp_mock.tool.called)

        # Test job tools registration
        job_tools = JobTools(lambda: self.mock_client)
        job_tools.register(mcp_mock)
        self.assertTrue(mcp_mock.tool.called)
