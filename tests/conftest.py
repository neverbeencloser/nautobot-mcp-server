"""Shared test utilities and fixtures."""

from unittest.mock import MagicMock


class MockRecord:
    """Unified mock for pynautobot Record objects.

    Supports all common operations: save, delete, run (for jobs).
    """

    def __init__(self, **kwargs):
        """Initialize mock record with given attributes."""
        self._data = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def update(self, data=None):
        """Mock update method that accepts data dict like pynautobot Records."""
        if data:
            # Update internal data and attributes
            self._data.update(data)
            for key, value in data.items():
                setattr(self, key, value)

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

    def __iter__(self):
        """Make MockRecord iterable for dict() conversion."""
        return iter(self._data.items())

    def keys(self):
        """Return keys for dict-like access."""
        return self._data.keys()

    def values(self):
        """Return values for dict-like access."""
        return self._data.values()

    def items(self):
        """Return items for dict-like access."""
        # Convert MagicMock objects to strings for JSON serialization
        result = []
        for key, value in self._data.items():
            if hasattr(value, "__str__") and hasattr(value, "_mock_name"):
                result.append((key, str(value)))
            else:
                result.append((key, value))
        return result

    def __getitem__(self, key):
        """Get item by key for dict-like access."""
        value = self._data[key]
        # Convert MagicMock objects to strings for JSON serialization
        if hasattr(value, "__str__") and hasattr(value, "_mock_name"):
            return str(value)
        return value
