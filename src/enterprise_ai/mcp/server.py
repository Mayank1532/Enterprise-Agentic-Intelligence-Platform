"""MCP v2 server foundation for the Enterprise AI platform."""

from mcp.server import MCPServer

from enterprise_ai.mcp.prompts import register_prompts
from enterprise_ai.mcp.resources import register_resources
from enterprise_ai.mcp.tools import register_tools


def create_mcp_server() -> MCPServer:
    """Create and configure the platform MCP server."""
    server = MCPServer("enterprise-ai")
    register_tools(server)
    register_resources(server)
    register_prompts(server)
    return server


mcp_server = create_mcp_server()
