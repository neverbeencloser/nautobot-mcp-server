# Nautobot MCP Server

An MCP (Model Context Protocol) server for interfacing with Nautobot API, enabling AI agents to perform CRUD operations on Nautobot objects and manage jobs.

## Features

Built with FastMCP for:
- Clean decorator-based tool registration
- Built-in context logging and debugging
- Structured error handling

## Installation

```bash
# Install dependencies using Poetry
poetry install

# Or install directly with pip
pip install mcp-server pynautobot
```

## Usage

### Running the MCP Server
- url and token will default to dev locals if not provided

You can run the server directly with Python:

```bash
python -m nautobot_mcp_server --url http://your-nautobot-url --token your-api-token
```

Or use environment variables with the provided shell script:

```bash
export NAUTOBOT_URL=http://localhost:8080
export NAUTOBOT_TOKEN=your-api-token
./run_server.sh
```

### Claude Code (from repo root)
```shell
% claude mcp add nautobot -- poetry run python -m nautobot_mcp_server [--url http://your-nautobot-url --token your-api-token]
```

### Available Tools

The MCP server currently supports CRUD and get/list operations for:
 - Devices
 - Locations

It also supports the following operations for Nautobot Jobs:
 - `get_job`
 - `list_jobs`
 - `run_job`
 - `list_job_results`
 - `get_job_result`
 - `get_job_logs`

### Testing

Use the provided test client to verify the MCP server is working:

```bash
# Update the URL and token in test_mcp_client.py first
python test_mcp_client.py
```

### Development Stack

The `development/` folder contains a Docker Compose setup for running a local Nautobot instance:

```bash
make start
```

This will start Nautobot on `http://localhost:8080` with default credentials.

Run `make help` for available commands.

To fill your local dev Nautobot instance with sample data:
```bash
make cli
nautobot-server generate_test_data
```

## Architecture

The MCP server uses:
- **FastMCP**: High-level MCP server framework with decorator-based tool registration
- **pynautobot**: Python client for Nautobot API
- **Context**: Built-in logging and progress reporting for each tool execution
- **JSON**: Structured response format for all tool outputs

## Configuration

The server accepts two parameters:
- `--url`: The Nautobot API URL (e.g., https://nautobot.example.com), default: `http://localhost:8080`
- `--token`: A valid Nautobot API token, default: 0123456789abcdef0123456789abcdef01234567

### Debug Mode

Enable debug logging with the `--debug` flag:

```bash
python nautobot_mcp_server.py --url http://localhost:8080 --token your-token --debug
```

## Contributing

To add new Nautobot resources or operations:

1. Add new tool definitions in the `list_tools()` handler
2. Implement the corresponding async methods (e.g., `_list_resources`, `_get_resource`)
3. Add the tool case to the `call_tool()` handler
4. Update tests and documentation

## To-Do
- Containerize the MCP server for flexible deployment
- Add support for core Nautobot resources
- Improve search, filtering functionality

## License

MIT
