# Nautobot MCP Server - Project Context

## Project Overview

This is a Model Context Protocol (MCP) server for Nautobot, built to enable AI agents to interface with Nautobot API for performing CRUD operations on network infrastructure objects and managing jobs. The server acts as a bridge between AI systems and Nautobot's Source of Truth capabilities.

## Architecture

### Technology Stack
- **FastMCP**: High-level MCP server framework with decorator-based tool registration
- **pynautobot**: Official Python SDK for Nautobot API interactions
- **Poetry**: Dependency management and virtual environment handling
- **Docker**: Containerized development environment with local Nautobot instance

### Project Structure
```
nautobot_mcp_server/
├── __init__.py                 # Package exports
├── __main__.py                # Module entry point
├── server.py                  # Main MCP server class (simplified)
└── tools/                     # Modular tools implementation
    ├── __init__.py           # Tool registration and exports
    ├── base.py               # Shared NautobotToolBase class
    ├── devices.py            # Device CRUD operations (5 tools)
    ├── jobs.py               # Job management (6 tools)
    └── sites.py              # Site CRUD operations (5 tools)
```

## Key Features

### Device Management (5 tools)
- `nautobot_list_devices`: List devices with optional site filtering
- `nautobot_get_device`: Retrieve specific device by ID/name
- `nautobot_create_device`: Create new devices with validation
- `nautobot_update_device`: Update existing devices with field validation
- `nautobot_delete_device`: Remove devices from Nautobot

### Site Management (5 tools)
- `nautobot_list_sites`: List sites with optional status filtering
- `nautobot_get_site`: Get site by ID/name/slug with full details
- `nautobot_create_site`: Create sites with auto-slug generation
- `nautobot_update_site`: Update site properties
- `nautobot_delete_site`: Remove sites from Nautobot

### Job Management (6 tools)
- `nautobot_list_jobs`: List available jobs in Nautobot
- `nautobot_get_job`: Get detailed job information
- `nautobot_run_job`: Execute jobs with parameters and commit/dryrun support
- `nautobot_list_job_results`: List job execution results with filtering
- `nautobot_get_job_result`: Get specific job result details
- `nautobot_get_job_logs`: Retrieve job execution logs and tracebacks

## Development Architecture Decisions

### Modular Design
- **Separation of Concerns**: Each Nautobot resource type (devices, sites, jobs) has its own dedicated module
- **Base Class Pattern**: `NautobotToolBase` provides consistent error handling, response formatting, and logging
- **Auto-Registration**: Tools are automatically registered via `register_all_tools()` function
- **Context Logging**: All operations use structured logging with FastMCP's Context for debugging

### Code Quality Features
- **Type Safety**: Full type hints with FastMCP decorators
- **Error Handling**: Consistent error responses with JSON formatting
- **Response Formatting**: Standardized success/error response structure
- **Client Management**: Singleton pattern for pynautobot client with threading and retry support

## Configuration

### Required Parameters
- `--url`: Nautobot API URL (e.g., https://nautobot.example.com)
- `--token`: Valid Nautobot API token with appropriate permissions
- `--debug`: Optional debug logging

### Environment Variables (Alternative)
- `NAUTOBOT_URL`: Nautobot API URL
- `NAUTOBOT_TOKEN`: API token

## Usage Examples

### Running the Server
```bash
# Direct execution
poetry run python -m nautobot_mcp_server --url http://localhost:8080 --token your-token

# Using environment variables
export NAUTOBOT_URL=http://localhost:8080
export NAUTOBOT_TOKEN=your-api-token
./run_server.sh

# With debug logging
poetry run python -m nautobot_mcp_server --url http://localhost:8080 --token your-token --debug
```

### Development Environment
```bash
# Start local Nautobot instance
make start

# View logs
make logs

# Access Nautobot shell
make shell

# Run tests and linting
make tests

# Build new container
make build
```

## API Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    "id": "uuid",
    "name": "device-name",
    "...": "other fields"
  }
}
```

### Error Response
```json
{
  "error": "Error description with context"
}
```

## Development Notes

### Adding New Resources
1. Create new file in `tools/` directory (e.g., `interfaces.py`)
2. Implement class inheriting from `NautobotToolBase`
3. Add `register()` method with `@mcp.tool()` decorated functions
4. Import and register in `tools/__init__.py`
5. Update documentation

### Testing Strategy
- **Local Testing**: Use `test_mcp_client.py` with actual Nautobot instance
- **Development Stack**: Docker Compose provides isolated Nautobot environment
- **Integration Testing**: Can test against multiple Nautobot versions

## Integration Patterns

### MCP Client Usage
```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="python",
    args=["-m", "nautobot_mcp_server", "--url", "...", "--token", "..."]
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        
        # List available tools
        tools = await session.list_tools()
        
        # Execute tools
        result = await session.call_tool("nautobot_list_devices", {"limit": 5})
```

### Claude Code Integration
This MCP server is designed to work seamlessly with Claude Code for infrastructure management tasks, allowing AI agents to:
- Query current network device states
- Create and update infrastructure objects
- Execute Nautobot jobs for data imports and validations
- Monitor job execution and retrieve results

## Future Enhancements

### Planned Resources
- **Interfaces**: Network interface management
- **IP Addresses**: IP address and subnet management  
- **Cables**: Physical and logical connections
- **Circuits**: Provider circuit management
- **Config Contexts**: Configuration context management

### Advanced Features
- **Bulk Operations**: Multi-object CRUD operations
- **Relationships**: Cross-resource relationship management
- **Custom Fields**: Support for Nautobot custom fields
- **GraphQL**: Alternative query interface for complex operations
- **Webhooks**: Event-driven notifications

## Security Considerations

- **API Token Management**: Secure token storage and rotation
- **Permission Validation**: Ensure tokens have minimal required permissions
- **Input Validation**: All user inputs are validated before API calls
- **Error Sanitization**: Sensitive information is not exposed in error messages

## Testing Notes

- **Python Testing**: Always use `poetry run python` when testing Python code in this project to ensure proper dependency management
