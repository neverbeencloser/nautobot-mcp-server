"""Main entry point for Nautobot MCP Server."""

import argparse
import logging

from .server import NautobotMCPServer


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Nautobot MCP Server for API operations")
    parser.add_argument(
        "--url",
        required=False,
        help="Nautobot API URL (e.g., https://nautobot.example.com)",
        default="http://localhost:8080",
    )
    parser.add_argument(
        "--token",
        required=False,
        help="Nautobot API token",
        default="0123456789abcdef0123456789abcdef01234567",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    server = NautobotMCPServer(url=args.url, token=args.token)
    mcp = server.get_fastmcp_instance()

    try:
        # FastMCP handles the async loop internally
        mcp.run()
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
    except Exception as e:
        logging.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()
