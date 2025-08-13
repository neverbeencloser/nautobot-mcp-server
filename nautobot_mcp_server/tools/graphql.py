"""GraphQL-related tools for Nautobot MCP Server."""

from mcp.server.fastmcp import Context, FastMCP
from pynautobot import RequestError

from .base import NautobotToolBase


class GraphQLTools(NautobotToolBase):
    """Tools for the graphql endpoint in Nautobot."""

    def register(self, mcp: FastMCP):
        """Register graphql tools with the MCP server.

        Args:
            mcp: FastMCP instance to register tools with
        """

        @mcp.tool()
        def nautobot_graphql_query(ctx: Context, query: str, variables: dict | None = None) -> str:
            """
            Get results from Nautobot GraphQL query.

            Args:
                ctx: MCP context for logging and progress
                query: GraphQL query string to execute
                variables: Optional dictionary of variables for the query

            Returns:
                YAML string of GraphQL results
            """
            ctx.info(f"Running GraphQL query: {query}, variables: {variables}")

            try:
                client = self._get_client()
                response = client.graphql.query(query=query, variables=variables)

                ctx.info("Successfully retrieved graphql results")
                return self.format_success(response.json, message="Results retrieved successfully")
            except RequestError as e:
                ctx.warning(f"RequestError: {e}")
                return self.format_error(f"Error retrieving GraphQL results: {e}")

            except Exception as e:
                return self.log_and_return_error(ctx, "getting GraphQL results", e)
