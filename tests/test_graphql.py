"""Tests for GraphQL tools."""

import json
import unittest
from unittest.mock import MagicMock

from pynautobot import RequestError

from nautobot_mcp_server.tools.graphql import GraphQLTools


class TestGraphQLTools(unittest.TestCase):
    """Test GraphQL functionality."""

    def setUp(self):
        """Set up test fixtures using simple mocks."""
        # Create mock client
        self.mock_client = MagicMock()

        # Create mock GraphQL client
        self.mock_graphql_client = MagicMock()
        self.mock_client.graphql = self.mock_graphql_client

        # Create mock context
        self.mock_context = MagicMock()

        # Create GraphQL tools instance
        self.graphql_tools = GraphQLTools(lambda: self.mock_client)

        # Sample GraphQL response data
        self.sample_graphql_response = {
            "data": {
                "devices": [
                    {
                        "id": "device-123",
                        "name": "test-device",
                        "deviceType": {"name": "Router"},
                        "location": {"name": "DC-01"},
                    },
                    {
                        "id": "device-456",
                        "name": "test-device-2",
                        "deviceType": {"name": "Switch"},
                        "location": {"name": "DC-02"},
                    },
                ]
            }
        }

    def _register_and_get_function(self, function_index):
        """Helper to register tools and get function."""
        mcp_mock = MagicMock()
        tool_decorator_mock = MagicMock()
        mcp_mock.tool.return_value = tool_decorator_mock

        self.graphql_tools.register(mcp_mock)

        return tool_decorator_mock.call_args_list[function_index][0][0]

    def test_graphql_query_success(self):
        """Test successful GraphQL query execution."""
        # Mock GraphQL response
        mock_response = MagicMock()
        mock_response.json = self.sample_graphql_response
        self.mock_graphql_client.query.return_value = mock_response

        graphql_query_func = self._register_and_get_function(0)

        query = """
        query {
            devices {
                id
                name
                deviceType {
                    name
                }
                location {
                    name
                }
            }
        }
        """

        result = graphql_query_func(self.mock_context, query)

        # Verify result
        parsed = json.loads(result)
        self.assertTrue(parsed["success"])
        self.assertEqual(parsed["message"], "Results retrieved successfully")
        self.assertEqual(parsed["data"], self.sample_graphql_response)

        # Verify GraphQL client was called correctly
        self.mock_graphql_client.query.assert_called_once_with(query=query, variables=None)
        self.mock_context.info.assert_called()

    def test_graphql_query_with_variables_success(self):
        """Test successful GraphQL query execution with variables."""
        # Mock GraphQL response
        mock_response = MagicMock()
        mock_response.json = self.sample_graphql_response
        self.mock_graphql_client.query.return_value = mock_response

        graphql_query_func = self._register_and_get_function(0)

        query = """
        query GetDevicesByLocation($locationName: String!) {
            devices(location: $locationName) {
                id
                name
                deviceType {
                    name
                }
            }
        }
        """
        variables = {"locationName": "DC-01"}

        result = graphql_query_func(self.mock_context, query, variables)

        # Verify result
        parsed = json.loads(result)
        self.assertTrue(parsed["success"])
        self.assertEqual(parsed["message"], "Results retrieved successfully")
        self.assertEqual(parsed["data"], self.sample_graphql_response)

        # Verify GraphQL client was called correctly with variables
        self.mock_graphql_client.query.assert_called_once_with(query=query, variables=variables)
        self.mock_context.info.assert_called()

    def test_graphql_query_request_error(self):
        """Test GraphQL query with RequestError."""
        mock_request = MagicMock()
        mock_request.status_code = 400
        self.mock_graphql_client.query.side_effect = RequestError(mock_request)

        graphql_query_func = self._register_and_get_function(0)

        query = "query { invalid_field }"

        result = graphql_query_func(self.mock_context, query)

        # Verify error response
        parsed = json.loads(result)
        self.assertIn("error", parsed)
        self.assertIn("Error retrieving GraphQL results", parsed["error"])
        self.mock_context.warning.assert_called_once()

    def test_graphql_query_generic_exception(self):
        """Test GraphQL query with generic exception."""
        self.mock_graphql_client.query.side_effect = Exception("Network error")

        graphql_query_func = self._register_and_get_function(0)

        query = "query { devices { id name } }"

        result = graphql_query_func(self.mock_context, query)

        # Verify error response
        parsed = json.loads(result)
        self.assertIn("error", parsed)
        self.assertIn("Network error", parsed["error"])
        self.mock_context.error.assert_called_once()

    def test_graphql_query_empty_response(self):
        """Test GraphQL query with empty response."""
        # Mock empty GraphQL response
        mock_response = MagicMock()
        mock_response.json = {"data": {}}
        self.mock_graphql_client.query.return_value = mock_response

        graphql_query_func = self._register_and_get_function(0)

        query = "query { devices { id } }"

        result = graphql_query_func(self.mock_context, query)

        # Verify result
        parsed = json.loads(result)
        self.assertTrue(parsed["success"])
        self.assertEqual(parsed["message"], "Results retrieved successfully")
        self.assertEqual(parsed["data"], {"data": {}})

        # Verify GraphQL client was called correctly
        self.mock_graphql_client.query.assert_called_once_with(query=query, variables=None)

    def test_graphql_query_complex_variables(self):
        """Test GraphQL query with complex variables structure."""
        # Mock GraphQL response
        mock_response = MagicMock()
        mock_response.json = self.sample_graphql_response
        self.mock_graphql_client.query.return_value = mock_response

        graphql_query_func = self._register_and_get_function(0)

        query = """
        query FilterDevices($filters: DeviceFiltersInput, $limit: Int) {
            devices(filters: $filters, limit: $limit) {
                id
                name
            }
        }
        """
        variables = {"filters": {"location": "DC-01", "status": "active"}, "limit": 10}

        result = graphql_query_func(self.mock_context, query, variables)

        # Verify result
        parsed = json.loads(result)
        self.assertTrue(parsed["success"])
        self.assertEqual(parsed["data"], self.sample_graphql_response)

        # Verify GraphQL client was called correctly with complex variables
        self.mock_graphql_client.query.assert_called_once_with(query=query, variables=variables)
