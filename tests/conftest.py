"""Shared test utilities and fixtures."""

from unittest.mock import MagicMock


class MockRecord:
    """Unified mock for pynautobot Record objects.

    Supports all common operations: save, delete, run (for jobs).
    """

    def __init__(self, **kwargs):
        """Initialize mock record with given attributes."""
        for key, value in kwargs.items():
            setattr(self, key, value)

    def save(self):
        """Mock save method."""
        pass

    def delete(self):
        """Mock delete method."""
        pass

    def run(self, **kwargs):
        """Mock run method for jobs."""
        # Return a mock job result
        return MockRecord(
            id="job-result-123",
            name="Job Result",
            status=MagicMock(__str__=lambda self: "Success"),
            created="2024-01-01T00:00:00Z",
        )
