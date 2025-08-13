"""Tests for NautobotToolBase class."""

import json
import unittest
from unittest.mock import Mock

from nautobot_mcp_server.tools.base import NautobotToolBase


class TestNautobotToolBase(unittest.TestCase):
    """Test the base tool class functionality."""

    def test_init(self):
        """Test tool initialization."""
        mock_client_getter = Mock()
        tool = NautobotToolBase(mock_client_getter)

        self.assertEqual(tool._get_client, mock_client_getter)

    def test_format_error(self):
        """Test error message formatting."""
        error_msg = "Test error message"
        result = NautobotToolBase.format_error(error_msg)

        expected = json.dumps({"error": error_msg}, separators=(",", ":"))
        self.assertEqual(result, expected)

        # Verify it's valid JSON
        parsed = json.loads(result)
        self.assertEqual(parsed["error"], error_msg)

    def test_format_success_with_message(self):
        """Test success response formatting with message."""
        data = {"id": "test-id", "name": "test-name"}
        message = "Operation successful"

        result = NautobotToolBase.format_success(data, message)

        expected = json.dumps({"success": True, "message": message, "data": data}, separators=(",", ":"))
        self.assertEqual(result, expected)

        # Verify it's valid JSON
        parsed = json.loads(result)
        self.assertTrue(parsed["success"])
        self.assertEqual(parsed["message"], message)
        self.assertEqual(parsed["data"], data)

    def test_format_success_without_message(self):
        """Test success response formatting without message."""
        data = {"id": "test-id", "name": "test-name"}

        result = NautobotToolBase.format_success(data)

        expected = json.dumps(data, separators=(",", ":"))
        self.assertEqual(result, expected)

        # Verify it's valid JSON
        parsed = json.loads(result)
        self.assertEqual(parsed, data)

    def test_format_success_with_list_data(self):
        """Test success response formatting with list data."""
        data = [{"id": "1", "name": "item1"}, {"id": "2", "name": "item2"}]

        result = NautobotToolBase.format_success(data)

        expected = json.dumps(data, separators=(",", ":"))
        self.assertEqual(result, expected)

        # Verify it's valid JSON
        parsed = json.loads(result)
        self.assertEqual(parsed, data)

    def test_log_and_return_error(self):
        """Test error logging and response formatting."""
        mock_client_getter = Mock()
        tool = NautobotToolBase(mock_client_getter)
        mock_context = Mock()

        operation = "testing operation"
        error = Exception("Test exception")

        result = tool.log_and_return_error(mock_context, operation, error)

        # Verify error was logged
        mock_context.error.assert_called_once_with(f"Error {operation}: {str(error)}")

        # Verify correct error response format
        expected_error_msg = f"Error {operation}: {str(error)}"
        expected = json.dumps({"error": expected_error_msg}, separators=(",", ":"))
        self.assertEqual(result, expected)

    def test_log_and_return_error_with_complex_exception(self):
        """Test error logging with complex exception messages."""
        mock_client_getter = Mock()
        tool = NautobotToolBase(mock_client_getter)
        mock_context = Mock()

        operation = "complex operation"
        error = ValueError("Complex error with special chars:!@#$%^&*()")

        result = tool.log_and_return_error(mock_context, operation, error)

        # Verify error was logged with full message
        expected_log_msg = f"Error {operation}: {str(error)}"
        mock_context.error.assert_called_once_with(expected_log_msg)

        # Verify JSON response is valid despite special characters
        parsed = json.loads(result)
        self.assertIn("error", parsed)
        self.assertIn(str(error), parsed["error"])
