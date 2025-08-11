"""Base class for Nautobot MCP resources."""

import json
from typing import Any

import yaml


class NautobotResourceBase:
    """Base class for Nautobot resource implementations."""

    def format_yaml(self, data: Any) -> str:
        """Format data as YAML string.

        Args:
            data: Data to format

        Returns:
            YAML-formatted string
        """
        return yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True, indent=2)

    def format_json(self, data: Any) -> str:
        """Format data as JSON string.

        Args:
            data: Data to format

        Returns:
            JSON-formatted string
        """
        return json.dumps(data, indent=2, ensure_ascii=False)
