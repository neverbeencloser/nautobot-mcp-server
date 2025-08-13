"""Base class for Nautobot MCP resources."""

import json
from typing import Any

import yaml


class NautobotResourceBase:
    """Base class for Nautobot resource implementations."""

    @staticmethod
    def format_yaml(data: Any) -> str:
        """Format data as YAML string.

        Args:
            data: Data to format

        Returns:
            YAML-formatted string
        """
        return yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True, indent=2)

    @staticmethod
    def format_json(data: Any) -> str:
        """Format data as JSON string.

        Args:
            data: Data to format

        Returns:
            JSON-formatted string
        """
        return json.dumps(data, ensure_ascii=False, separators=(",", ":"))
