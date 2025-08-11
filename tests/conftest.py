"""Shared test utilities and fixtures."""


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
        # Return a mock job result with JSON-serializable fields
        return MockRecord(
            id="job-result-123",
            name="Job Result",
            status="Success",
            created="2024-01-01T00:00:00Z",
        )

    def __iter__(self):
        """Support dict() conversion by making object iterable of its attributes."""
        return iter(self.__dict__.items())

    def __getitem__(self, key):
        """Support dict-like access."""
        return getattr(self, key)

    def __setitem__(self, key, value):
        """Support dict-like assignment."""
        setattr(self, key, value)

    def keys(self):
        """Support dict() conversion."""
        return self.__dict__.keys()

    def values(self):
        """Support dict() conversion."""
        return self.__dict__.values()

    def items(self):
        """Support dict() conversion."""
        return self.__dict__.items()
