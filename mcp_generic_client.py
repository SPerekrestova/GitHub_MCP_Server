#!/usr/bin/env python3
"""
Generic MCP Client

A vendor-agnostic client for communicating with MCP servers.
Uses standard HTTP libraries (httpx) - NO vendor-specific SDKs.

Features:
- REST API communication for simple operations
- SSE transport support for MCP protocol
- Interactive CLI mode
- Programmatic Python API

This client demonstrates how to interact with MCP servers without
depending on any specific AI vendor's SDK.
"""

import argparse
import asyncio
import json
import sys
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union
from urllib.parse import quote, urljoin

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Install with: pip install httpx")
    sys.exit(1)

try:
    import httpx_sse
    SSE_AVAILABLE = True
except ImportError:
    SSE_AVAILABLE = False


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class Tool:
    """Represents an MCP tool."""
    name: str
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Resource:
    """Represents an MCP resource."""
    uri: str
    description: str = ""


@dataclass
class Prompt:
    """Represents an MCP prompt."""
    name: str
    description: str = ""
    parameters: List[str] = field(default_factory=list)


@dataclass
class ToolResult:
    """Result from a tool execution."""
    success: bool
    result: Any = None
    error: Optional[str] = None


# =============================================================================
# Generic MCP Client (REST API)
# =============================================================================


class MCPClient:
    """
    A generic MCP client that communicates via REST API.

    This client uses standard HTTP requests and doesn't depend on any
    vendor-specific SDK. It works with any MCP server that exposes
    REST API endpoints.

    Example usage:
        async with MCPClient("http://localhost:8080") as client:
            # List tools
            tools = await client.list_tools()
            for tool in tools:
                print(f"Tool: {tool.name}")

            # Call a tool
            result = await client.call_tool("hello_world", {"name": "User"})
            print(result)

            # Read a resource
            content = await client.read_resource("config://server/info")
            print(content)
    """

    def __init__(
        self,
        base_url: str,
        api_prefix: str = "/api",
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
    ):
        """
        Initialize the MCP client.

        Args:
            base_url: Base URL of the MCP server (e.g., "http://localhost:8080")
            api_prefix: Prefix for REST API endpoints (default: "/api")
            headers: Optional headers to include in requests
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.api_prefix = api_prefix
        self.headers = headers or {}
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "MCPClient":
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None

    def _api_url(self, endpoint: str) -> str:
        """Build API URL."""
        return f"{self.api_prefix}/{endpoint.lstrip('/')}"

    # =========================================================================
    # Health & Server Info
    # =========================================================================

    async def health_check(self) -> Dict[str, Any]:
        """
        Check server health.

        Returns:
            Health status information
        """
        response = await self._client.get(self._api_url("health"))
        response.raise_for_status()
        return response.json()

    # =========================================================================
    # Tools
    # =========================================================================

    async def list_tools(self) -> List[Tool]:
        """
        List all available tools.

        Returns:
            List of Tool objects
        """
        response = await self._client.get(self._api_url("tools"))
        response.raise_for_status()
        data = response.json()

        return [
            Tool(
                name=t.get("name", ""),
                description=t.get("description", ""),
                parameters=t.get("parameters", {}),
            )
            for t in data.get("tools", [])
        ]

    async def call_tool(
        self,
        name: str,
        arguments: Optional[Dict[str, Any]] = None,
    ) -> ToolResult:
        """
        Execute a tool by name.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            ToolResult with success status and result/error
        """
        try:
            response = await self._client.post(
                self._api_url(f"tools/{name}"),
                json=arguments or {},
            )
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                return ToolResult(success=False, error=data["error"])

            return ToolResult(success=True, result=data.get("result"))

        except httpx.HTTPStatusError as e:
            return ToolResult(success=False, error=f"HTTP {e.response.status_code}: {e.response.text}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    # =========================================================================
    # Resources
    # =========================================================================

    async def list_resources(self) -> List[Resource]:
        """
        List all available resources.

        Returns:
            List of Resource objects
        """
        response = await self._client.get(self._api_url("resources"))
        response.raise_for_status()
        data = response.json()

        return [
            Resource(
                uri=r.get("uri", ""),
                description=r.get("description", ""),
            )
            for r in data.get("resources", [])
        ]

    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """
        Read a resource by URI.

        Args:
            uri: Resource URI (e.g., "config://server/info")

        Returns:
            Resource content
        """
        encoded_uri = quote(uri, safe="")
        response = await self._client.get(self._api_url(f"resources/{encoded_uri}"))
        response.raise_for_status()
        return response.json()

    # =========================================================================
    # Prompts
    # =========================================================================

    async def list_prompts(self) -> List[Prompt]:
        """
        List all available prompts.

        Returns:
            List of Prompt objects
        """
        response = await self._client.get(self._api_url("prompts"))
        response.raise_for_status()
        data = response.json()

        return [
            Prompt(
                name=p.get("name", ""),
                description=p.get("description", ""),
                parameters=p.get("parameters", []),
            )
            for p in data.get("prompts", [])
        ]


# =============================================================================
# SSE Transport Client (for MCP Protocol)
# =============================================================================


class MCPSSEClient:
    """
    MCP client using Server-Sent Events transport.

    This client communicates using the MCP protocol over SSE,
    which is the standard transport for remote MCP servers.

    Note: Requires httpx-sse package: pip install httpx-sse
    """

    def __init__(
        self,
        mcp_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
    ):
        """
        Initialize SSE client.

        Args:
            mcp_url: MCP endpoint URL (e.g., "http://localhost:8080/mcp")
            headers: Optional headers for authentication
            timeout: Request timeout
        """
        if not SSE_AVAILABLE:
            raise ImportError(
                "SSE support requires httpx-sse. Install with: pip install httpx-sse"
            )

        self.mcp_url = mcp_url.rstrip("/")
        self.headers = headers or {}
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
        self._message_id = 0

    async def __aenter__(self) -> "MCPSSEClient":
        self._client = httpx.AsyncClient(
            headers=self.headers,
            timeout=self.timeout,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    def _next_id(self) -> int:
        self._message_id += 1
        return self._message_id

    async def send_message(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Send a JSON-RPC message over SSE.

        Args:
            method: MCP method name
            params: Method parameters

        Returns:
            Response data
        """
        message = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
            "params": params or {},
        }

        # For SSE transport, we POST the message and get response via SSE
        async with httpx_sse.aconnect_sse(
            self._client,
            "POST",
            self.mcp_url,
            json=message,
        ) as event_source:
            async for sse in event_source.aiter_sse():
                if sse.data:
                    return json.loads(sse.data)

        return {"error": "No response received"}

    async def initialize(self) -> Dict[str, Any]:
        """Initialize the MCP connection."""
        return await self.send_message("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "generic-mcp-client",
                "version": "1.0.0",
            },
        })

    async def list_tools_mcp(self) -> List[Dict[str, Any]]:
        """List tools via MCP protocol."""
        response = await self.send_message("tools/list")
        return response.get("result", {}).get("tools", [])

    async def call_tool_mcp(
        self,
        name: str,
        arguments: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Call a tool via MCP protocol."""
        return await self.send_message("tools/call", {
            "name": name,
            "arguments": arguments or {},
        })


# =============================================================================
# Interactive CLI
# =============================================================================


class InteractiveCLI:
    """Interactive command-line interface for the MCP client."""

    def __init__(self, client: MCPClient):
        self.client = client
        self.commands: Dict[str, Callable] = {
            "help": self.cmd_help,
            "health": self.cmd_health,
            "tools": self.cmd_list_tools,
            "call": self.cmd_call_tool,
            "resources": self.cmd_list_resources,
            "read": self.cmd_read_resource,
            "prompts": self.cmd_list_prompts,
            "exit": self.cmd_exit,
            "quit": self.cmd_exit,
        }

    def print_header(self):
        print("""
╔══════════════════════════════════════════════════════════════════╗
║              Generic MCP Client - Interactive Mode                ║
╠══════════════════════════════════════════════════════════════════╣
║  Type 'help' for available commands                               ║
║  Type 'exit' or 'quit' to exit                                    ║
╚══════════════════════════════════════════════════════════════════╝
        """)

    async def cmd_help(self, _args: List[str]):
        """Show help message."""
        print("""
Available Commands:
  help              - Show this help message
  health            - Check server health
  tools             - List available tools
  call <name> [json] - Call a tool (json args optional)
  resources         - List available resources
  read <uri>        - Read a resource by URI
  prompts           - List available prompts
  exit/quit         - Exit the client

Examples:
  call hello_world {"name": "Developer"}
  call calculate {"operation": "add", "a": 10, "b": 5}
  read config://server/info
        """)

    async def cmd_health(self, _args: List[str]):
        """Check server health."""
        try:
            result = await self.client.health_check()
            print(f"Server Status: {json.dumps(result, indent=2)}")
        except Exception as e:
            print(f"Error: {e}")

    async def cmd_list_tools(self, _args: List[str]):
        """List available tools."""
        try:
            tools = await self.client.list_tools()
            print(f"\nAvailable Tools ({len(tools)}):")
            print("-" * 40)
            for tool in tools:
                print(f"  - {tool.name}")
                if tool.description:
                    print(f"    {tool.description}")
        except Exception as e:
            print(f"Error: {e}")

    async def cmd_call_tool(self, args: List[str]):
        """Call a tool."""
        if not args:
            print("Usage: call <tool_name> [json_arguments]")
            return

        tool_name = args[0]
        arguments = {}

        if len(args) > 1:
            json_str = " ".join(args[1:])
            try:
                arguments = json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"Invalid JSON: {e}")
                return

        try:
            result = await self.client.call_tool(tool_name, arguments)
            if result.success:
                print(f"\nResult:")
                print(json.dumps(result.result, indent=2, default=str))
            else:
                print(f"\nError: {result.error}")
        except Exception as e:
            print(f"Error: {e}")

    async def cmd_list_resources(self, _args: List[str]):
        """List available resources."""
        try:
            resources = await self.client.list_resources()
            print(f"\nAvailable Resources ({len(resources)}):")
            print("-" * 40)
            for resource in resources:
                print(f"  - {resource.uri}")
                if resource.description:
                    print(f"    {resource.description}")
        except Exception as e:
            print(f"Error: {e}")

    async def cmd_read_resource(self, args: List[str]):
        """Read a resource."""
        if not args:
            print("Usage: read <resource_uri>")
            return

        uri = args[0]
        try:
            result = await self.client.read_resource(uri)
            print(f"\nResource: {uri}")
            print("-" * 40)
            content = result.get("content", result)
            if isinstance(content, str):
                print(content)
            else:
                print(json.dumps(content, indent=2, default=str))
        except Exception as e:
            print(f"Error: {e}")

    async def cmd_list_prompts(self, _args: List[str]):
        """List available prompts."""
        try:
            prompts = await self.client.list_prompts()
            print(f"\nAvailable Prompts ({len(prompts)}):")
            print("-" * 40)
            for prompt in prompts:
                print(f"  - {prompt.name}")
                if prompt.description:
                    print(f"    {prompt.description}")
                if prompt.parameters:
                    print(f"    Parameters: {', '.join(prompt.parameters)}")
        except Exception as e:
            print(f"Error: {e}")

    async def cmd_exit(self, _args: List[str]):
        """Exit the client."""
        print("Goodbye!")
        sys.exit(0)

    async def run(self):
        """Run the interactive CLI loop."""
        self.print_header()

        while True:
            try:
                line = input("\nmcp> ").strip()
                if not line:
                    continue

                parts = line.split(maxsplit=1)
                cmd = parts[0].lower()
                args = parts[1].split() if len(parts) > 1 else []

                # Special handling for call command (preserve JSON)
                if cmd == "call" and len(parts) > 1:
                    call_parts = parts[1].split(maxsplit=1)
                    args = call_parts if len(call_parts) == 1 else [call_parts[0], call_parts[1]]

                if cmd in self.commands:
                    await self.commands[cmd](args)
                else:
                    print(f"Unknown command: {cmd}. Type 'help' for available commands.")

            except KeyboardInterrupt:
                print("\nUse 'exit' or 'quit' to exit.")
            except EOFError:
                print("\nGoodbye!")
                break


# =============================================================================
# Demo Functions
# =============================================================================


async def run_demo(base_url: str):
    """Run a demonstration of the client capabilities."""
    print(f"\n{'='*60}")
    print("MCP Generic Client - Demo")
    print(f"Server: {base_url}")
    print(f"{'='*60}\n")

    async with MCPClient(base_url) as client:
        # Health check
        print("1. Health Check")
        print("-" * 40)
        try:
            health = await client.health_check()
            print(f"   Status: {health.get('status', 'unknown')}")
            print(f"   Server: {health.get('server', 'unknown')}")
        except Exception as e:
            print(f"   Error: {e}")

        # List tools
        print("\n2. Available Tools")
        print("-" * 40)
        try:
            tools = await client.list_tools()
            for tool in tools:
                print(f"   - {tool.name}")
        except Exception as e:
            print(f"   Error: {e}")

        # Call hello_world tool
        print("\n3. Call 'hello_world' Tool")
        print("-" * 40)
        try:
            result = await client.call_tool("hello_world", {"name": "Demo User"})
            if result.success:
                print(f"   Result: {result.result}")
            else:
                print(f"   Error: {result.error}")
        except Exception as e:
            print(f"   Error: {e}")

        # Call calculate tool
        print("\n4. Call 'calculate' Tool (10 + 5)")
        print("-" * 40)
        try:
            result = await client.call_tool("calculate", {
                "operation": "add",
                "a": 10,
                "b": 5,
            })
            if result.success:
                calc_result = result.result
                print(f"   Operation: {calc_result.get('operation')}")
                print(f"   Result: {calc_result.get('result')}")
            else:
                print(f"   Error: {result.error}")
        except Exception as e:
            print(f"   Error: {e}")

        # List resources
        print("\n5. Available Resources")
        print("-" * 40)
        try:
            resources = await client.list_resources()
            for resource in resources:
                print(f"   - {resource.uri}")
        except Exception as e:
            print(f"   Error: {e}")

        # Read a resource
        print("\n6. Read 'config://server/info' Resource")
        print("-" * 40)
        try:
            resource = await client.read_resource("config://server/info")
            content = resource.get("content", {})
            print(f"   Name: {content.get('name')}")
            print(f"   Version: {content.get('version')}")
            print(f"   Status: {content.get('status')}")
        except Exception as e:
            print(f"   Error: {e}")

        # Generate sample data
        print("\n7. Generate Sample Data (3 users)")
        print("-" * 40)
        try:
            result = await client.call_tool("generate_sample_data", {
                "data_type": "users",
                "count": 3,
                "seed": 42,
            })
            if result.success:
                records = result.result.get("records", [])
                for user in records:
                    print(f"   - {user.get('name')} ({user.get('email')})")
            else:
                print(f"   Error: {result.error}")
        except Exception as e:
            print(f"   Error: {e}")

        # Analyze text
        print("\n8. Analyze Text")
        print("-" * 40)
        try:
            result = await client.call_tool("analyze_text", {
                "text": "This is a great example of text analysis. The results are amazing and wonderful!",
                "include_sentiment": True,
                "include_keywords": True,
            })
            if result.success:
                stats = result.result.get("statistics", {})
                insights = result.result.get("insights", [])
                print(f"   Word count: {stats.get('word_count')}")
                print(f"   Insights: {', '.join(insights)}")
            else:
                print(f"   Error: {result.error}")
        except Exception as e:
            print(f"   Error: {e}")

        # List prompts
        print("\n9. Available Prompts")
        print("-" * 40)
        try:
            prompts = await client.list_prompts()
            for prompt in prompts:
                print(f"   - {prompt.name}: {prompt.description}")
        except Exception as e:
            print(f"   Error: {e}")

        print(f"\n{'='*60}")
        print("Demo Complete!")
        print(f"{'='*60}\n")


# =============================================================================
# Programmatic Usage Example
# =============================================================================


async def programmatic_example():
    """
    Example of programmatic usage.

    This shows how to use the client in your own Python code.
    """
    # Example 1: Basic usage with context manager
    async with MCPClient("http://localhost:8080") as client:
        # Check health
        health = await client.health_check()
        print(f"Server healthy: {health['status'] == 'healthy'}")

        # List and call tools
        tools = await client.list_tools()
        print(f"Found {len(tools)} tools")

        # Call a specific tool
        result = await client.call_tool("hello_world", {"name": "Python"})
        if result.success:
            print(f"Tool result: {result.result}")

    # Example 2: Custom headers for authentication
    async with MCPClient(
        "http://localhost:8080",
        headers={"Authorization": "Bearer your-token"},
    ) as client:
        tools = await client.list_tools()
        print(f"Authenticated - found {len(tools)} tools")


# =============================================================================
# Main Entry Point
# =============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Generic MCP Client - communicate with any MCP server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run demo against local server
  python mcp_generic_client.py --demo

  # Interactive mode
  python mcp_generic_client.py --interactive

  # Custom server URL
  python mcp_generic_client.py --url http://remote-server:8080 --demo

  # Single tool call
  python mcp_generic_client.py --tool hello_world --args '{"name": "User"}'

  # Read a resource
  python mcp_generic_client.py --resource "config://server/info"
        """,
    )

    parser.add_argument(
        "--url", "-u",
        default="http://localhost:8080",
        help="MCP server URL (default: http://localhost:8080)",
    )
    parser.add_argument(
        "--demo", "-d",
        action="store_true",
        help="Run demonstration of client features",
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Start interactive CLI mode",
    )
    parser.add_argument(
        "--tool", "-t",
        help="Tool name to execute",
    )
    parser.add_argument(
        "--args", "-a",
        default="{}",
        help="JSON arguments for tool (default: {})",
    )
    parser.add_argument(
        "--resource", "-r",
        help="Resource URI to read",
    )
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="List all available tools",
    )
    parser.add_argument(
        "--list-resources",
        action="store_true",
        help="List all available resources",
    )

    args = parser.parse_args()

    async def run():
        if args.demo:
            await run_demo(args.url)

        elif args.interactive:
            async with MCPClient(args.url) as client:
                cli = InteractiveCLI(client)
                await cli.run()

        elif args.tool:
            async with MCPClient(args.url) as client:
                try:
                    tool_args = json.loads(args.args)
                except json.JSONDecodeError as e:
                    print(f"Invalid JSON arguments: {e}")
                    sys.exit(1)

                result = await client.call_tool(args.tool, tool_args)
                if result.success:
                    print(json.dumps(result.result, indent=2, default=str))
                else:
                    print(f"Error: {result.error}", file=sys.stderr)
                    sys.exit(1)

        elif args.resource:
            async with MCPClient(args.url) as client:
                result = await client.read_resource(args.resource)
                print(json.dumps(result, indent=2, default=str))

        elif args.list_tools:
            async with MCPClient(args.url) as client:
                tools = await client.list_tools()
                for tool in tools:
                    print(f"{tool.name}: {tool.description}")

        elif args.list_resources:
            async with MCPClient(args.url) as client:
                resources = await client.list_resources()
                for resource in resources:
                    print(f"{resource.uri}: {resource.description}")

        else:
            # Default: run demo
            await run_demo(args.url)

    asyncio.run(run())


if __name__ == "__main__":
    main()
