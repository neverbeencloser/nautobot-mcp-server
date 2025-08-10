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
    ├── <resource>.py         # Nautobot resource CRUD operations 
```

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

**Essential Commands**
- `make start`: Start local Nautobot instance with Docker Compose
- `make lint`: Run linters (flake8, black, mypy)
- `make lint-fix`: Auto-fix linting issues
- `make tests`: Run linting and unit tests with pytest
- `make unittest`: Run only unit tests

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

### Unit Test Standards

- **Test Structure**: Follow `TestClassNameTools` pattern (e.g., `TestDeviceTools`, `TestLocationTools`)
- **Setup Method**: Use `setUp()` to create mock client, context, and common test fixtures
- **Mock Objects**: Use `MockRecord` from `conftest.py` for consistent Nautobot record mocking
- **Function Registration**: Use `_register_and_get_function()` helper to test MCP tool registration
- **Assertions**: Use descriptive assertions and verify both success/error response formats

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
- Support CRUD ops for all core Nautobot resources that have API endpoints

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
- **Test Suite**: Run tests with `make unittest` or `poetry run pytest tests/ -v`
- 

## Git Standards

**Commit Messages:**
- Single-line message; include jira tag at start if branch name includes jira tag: `[PROJECT-##] feat: description`
- Use conventional commit format: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- Include your co-author signature in the commit msg.

**Pull Requests:**
- Title matches most recent commit message
- Put model names and field names in backticks for clarity (e.g., `DeviceType`, `device_type_id`).
- Use this template for the PR description:
  ```markdown
  ### What
  - **Brief** summary (1-2 bullet points)

  ### Why
   - **Brief** explanation of the change and its purpose (1-2 bullet points)

  ### How
  - **Concise** implementation details; limit to 3-5 bullet points
  - Breaking changes/migrations if any
  
  ### Proof
  ```

**Branch Info:**
- Main branch: `main`
- Uses GitHub Actions for CI/CD
