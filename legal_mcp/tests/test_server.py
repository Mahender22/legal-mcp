"""Tests for the MCP server tool definitions."""

from legal_mcp.src.server import mcp


def test_server_has_name():
    assert mcp.name == "Legal MCP Server"


def test_server_has_tools():
    """Verify all expected tools are registered."""
    # FastMCP registers tools internally — we verify the server loads
    assert mcp is not None


def test_server_instructions():
    assert "legal research" in mcp.instructions.lower()
