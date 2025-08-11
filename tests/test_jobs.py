"""Tests for job management tools."""

import json
import unittest
from unittest.mock import MagicMock

from pynautobot import RequestError

from nautobot_mcp_server.tools.jobs import JobTools

from .conftest import MockRecord


class TestJobTools(unittest.TestCase):
    """Test job management functionality."""

    def setUp(self):
        """Set up test fixtures using simple mocks."""
        # Create mock client
        self.mock_client = MagicMock()

        # Create mock context
        self.mock_context = MagicMock()

        # Create job tools instance
        self.job_tools = JobTools(lambda: self.mock_client)

        # Create simple mock job
        self.mock_job = MockRecord(
            id="job-123", name="test-job", slug="test-job", description="Test job description", enabled=True
        )

        # Create simple mock job result with JSON-serializable fields
        self.mock_job_result = MockRecord(
            id="result-123",
            name="test-result",
            status="Success",
            created="2024-01-01T00:00:00Z",
            job="test-job",
            completed="2024-01-01T00:01:00Z",
            log="Job execution log content",
        )

    def _register_and_get_function(self, function_index):
        """Helper to register tools and get function."""
        mcp_mock = MagicMock()
        tool_decorator_mock = MagicMock()
        mcp_mock.tool.return_value = tool_decorator_mock

        self.job_tools.register(mcp_mock)

        return tool_decorator_mock.call_args_list[function_index][0][0]

    def test_list_jobs_success(self):
        """Test successful job listing."""
        # Create another mock job
        mock_job2 = MockRecord(
            id="job-456", name="another-job", slug="another-job", description="Another job", enabled=False
        )

        self.mock_client.extras.jobs.filter.return_value = [self.mock_job, mock_job2]

        list_jobs_func = self._register_and_get_function(0)
        result = list_jobs_func(self.mock_context, limit=20)

        # Verify result
        parsed = json.loads(result)
        assert len(parsed) == 2
        assert parsed[0]["name"] == "test-job"
        assert parsed[0]["id"] == "job-123"
        assert parsed[1]["name"] == "another-job"

        # Verify client was called correctly
        self.mock_client.extras.jobs.filter.assert_called_once_with(limit=20, depth=1)
        self.mock_context.info.assert_called()

    def test_list_jobs_exception(self):
        """Test job listing with exception."""
        self.mock_client.extras.jobs.filter.side_effect = Exception("API Error")

        list_jobs_func = self._register_and_get_function(0)
        result = list_jobs_func(self.mock_context, limit=20)

        # Verify error response
        parsed = json.loads(result)
        assert "error" in parsed
        assert "API Error" in parsed["error"]
        self.mock_context.error.assert_called_once()

    def test_get_job_success(self):
        """Test successful job retrieval."""
        self.mock_client.extras.jobs.get.return_value = self.mock_job

        get_job_func = self._register_and_get_function(1)
        result = get_job_func(self.mock_context, "job-123")

        # Verify result
        parsed = json.loads(result)
        assert parsed["name"] == "test-job"
        assert parsed["id"] == "job-123"
        assert parsed["slug"] == "test-job"

        # Verify client was called correctly
        self.mock_client.extras.jobs.get.assert_called_with("job-123")

    def test_get_job_not_found(self):
        """Test job not found scenario."""
        self.mock_client.extras.jobs.get.side_effect = Exception("Job not found")
        self.mock_client.extras.jobs.all.return_value = []

        get_job_func = self._register_and_get_function(1)
        result = get_job_func(self.mock_context, "nonexistent-job")

        # Verify error response
        parsed = json.loads(result)
        assert "error" in parsed
        assert "Job not found" in parsed["error"]

    def test_run_job_success(self):
        """Test successful job execution."""
        self.mock_client.extras.jobs.get.return_value = self.mock_job

        run_job_func = self._register_and_get_function(2)
        result = run_job_func(self.mock_context, "test-job")

        # Verify result
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["data"]["name"] == "Job Result"
        assert "started successfully" in parsed["message"]

    def test_run_job_not_found(self):
        """Test running non-existent job."""
        self.mock_client.extras.jobs.get.side_effect = Exception("Not found")
        self.mock_client.extras.jobs.all.return_value = []

        run_job_func = self._register_and_get_function(2)
        result = run_job_func(self.mock_context, "nonexistent-job")

        # Verify error response
        parsed = json.loads(result)
        assert "error" in parsed
        assert "Job not found" in parsed["error"]

    def test_list_job_results_success(self):
        """Test successful job result listing."""
        # Create another mock job result with JSON-serializable fields
        mock_result2 = MockRecord(
            id="result-456",
            name="another-result",
            status="Failed",
            created="2024-01-02T00:00:00Z",
            job="another-job",
            completed="2024-01-02T00:01:00Z",
        )

        self.mock_client.extras.job_results.filter.return_value = [self.mock_job_result, mock_result2]

        list_job_results_func = self._register_and_get_function(3)
        result = list_job_results_func(self.mock_context, limit=10)

        # Verify result
        parsed = json.loads(result)
        assert len(parsed) == 2
        assert parsed[0]["name"] == "test-result"
        assert parsed[0]["id"] == "result-123"
        assert parsed[1]["name"] == "another-result"

        # Verify client was called correctly
        self.mock_client.extras.job_results.filter.assert_called_once_with(limit=10)
        self.mock_context.info.assert_called()

    def test_list_job_results_with_filters(self):
        """Test job result listing with filters."""
        self.mock_client.extras.job_results.filter.return_value = []

        list_job_results_func = self._register_and_get_function(3)
        result = list_job_results_func(self.mock_context, limit=5, job_name="test-job", status="success")

        # Verify client was called with filters
        self.mock_client.extras.job_results.filter.assert_called_once_with(
            limit=5, job_model__name="test-job", status="success"
        )

        # Verify empty result
        parsed = json.loads(result)
        assert parsed == []

    def test_get_job_result_success(self):
        """Test successful job result retrieval."""
        self.mock_client.extras.job_results.get.return_value = self.mock_job_result

        get_job_result_func = self._register_and_get_function(4)
        result = get_job_result_func(self.mock_context, "result-123")

        # Verify result
        parsed = json.loads(result)
        assert parsed["name"] == "test-result"
        assert parsed["id"] == "result-123"
        assert parsed["status"] == "Success"

        # Verify client was called correctly
        self.mock_client.extras.job_results.get.assert_called_with(id="result-123")

    def test_get_job_result_not_found(self):
        """Test job result not found scenario."""
        mock_request = MagicMock()
        mock_request.status_code = 404
        mock_request.url = "https://nautobot.example.com/api/extras/job-results/nonexistent/"
        self.mock_client.extras.job_results.get.side_effect = RequestError(mock_request)

        get_job_result_func = self._register_and_get_function(4)
        result = get_job_result_func(self.mock_context, "nonexistent-result")

        # Verify error response
        parsed = json.loads(result)
        assert "error" in parsed

    def test_get_job_logs_success(self):
        """Test successful job log retrieval."""
        self.mock_client.extras.job_results.get.return_value = self.mock_job_result

        get_job_logs_func = self._register_and_get_function(5)
        result = get_job_logs_func(self.mock_context, "result-123")

        # Verify result
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["data"]["id"] == "result-123"
        assert parsed["data"]["log"] == "Job execution log content"

        # Verify client was called correctly
        self.mock_client.extras.job_results.get.assert_called_with(id="result-123")

    def test_get_job_logs_not_found(self):
        """Test job log retrieval for non-existent result."""
        mock_request = MagicMock()
        mock_request.status_code = 404
        mock_request.url = "https://nautobot.example.com/api/extras/job-results/nonexistent/"
        self.mock_client.extras.job_results.get.side_effect = RequestError(mock_request)

        get_job_logs_func = self._register_and_get_function(5)
        result = get_job_logs_func(self.mock_context, "nonexistent-result")

        # Verify error response
        parsed = json.loads(result)
        assert "error" in parsed
