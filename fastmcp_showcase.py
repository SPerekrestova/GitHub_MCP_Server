#!/usr/bin/env python3
"""
FastMCP Core Components Showcase
================================

A comprehensive demonstration of all FastMCP core functionalities.
This file showcases every major feature available in FastMCP 2.x.

Documentation: https://gofastmcp.com/getting-started/welcome

Run Instructions:
    # Install dependencies
    pip install "fastmcp>=2.14.0" fastapi uvicorn pydantic aiohttp

    # Run as MCP server (stdio mode - for Claude Desktop)
    python fastmcp_showcase.py

    # Run as HTTP server (for remote access)
    python fastmcp_showcase.py --http

    # Run with FastAPI integration
    python fastmcp_showcase.py --fastapi

Author: FastMCP Showcase
"""

import asyncio
import base64
import sys
from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Dict, List, Optional

from fastmcp import Context, FastMCP
from fastmcp.utilities.types import Image
from pydantic import BaseModel, Field

# =============================================================================
# SECTION 1: Basic Server Initialization
# =============================================================================

# Create the main FastMCP server instance
# The name parameter identifies your server to MCP clients
mcp = FastMCP(
    name="FastMCP Showcase Server",
    version="1.0.0",
)


# =============================================================================
# SECTION 2: TOOLS - Functions that LLMs can execute
# =============================================================================

# --- 2.1 Simple Synchronous Tool ---
@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """
    Add two numbers together.

    A simple synchronous tool demonstrating basic parameter handling.
    FastMCP automatically generates the schema from type hints.

    Args:
        a: First number to add
        b: Second number to add

    Returns:
        The sum of a and b
    """
    return a + b


# --- 2.2 Simple Asynchronous Tool ---
@mcp.tool()
async def multiply_numbers(a: float, b: float) -> float:
    """
    Multiply two numbers asynchronously.

    Demonstrates async tool support - ideal for I/O operations.

    Args:
        a: First number to multiply
        b: Second number to multiply

    Returns:
        The product of a and b
    """
    # Simulate async operation
    await asyncio.sleep(0.01)
    return a * b


# --- 2.3 Tool with Pydantic Model Input ---
class UserProfile(BaseModel):
    """Pydantic model for user data input validation."""

    name: str = Field(..., description="User's full name")
    email: str = Field(..., description="User's email address")
    age: Optional[int] = Field(None, description="User's age (optional)")
    tags: List[str] = Field(default_factory=list, description="User tags")


class UserResponse(BaseModel):
    """Response model for user operations."""

    id: str
    profile: UserProfile
    created_at: str
    message: str


@mcp.tool()
def create_user(profile: UserProfile) -> UserResponse:
    """
    Create a new user from a Pydantic model.

    Demonstrates complex input validation using Pydantic models.
    FastMCP automatically handles serialization/deserialization.

    Args:
        profile: User profile data with validation

    Returns:
        Created user response with generated ID
    """
    return UserResponse(
        id=f"user_{hash(profile.email) % 10000:04d}",
        profile=profile,
        created_at=datetime.now().isoformat(),
        message=f"User '{profile.name}' created successfully",
    )


# --- 2.4 Tool with Enum Parameters ---
class Priority(str, Enum):
    """Task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(str, Enum):
    """Task status options."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


@mcp.tool()
def create_task(
    title: str,
    description: str,
    priority: Priority = Priority.MEDIUM,
    status: TaskStatus = TaskStatus.PENDING,
) -> Dict[str, Any]:
    """
    Create a task with enum-based priority and status.

    Demonstrates enum parameter support with default values.

    Args:
        title: Task title
        description: Task description
        priority: Task priority level (default: medium)
        status: Initial task status (default: pending)

    Returns:
        Created task dictionary
    """
    return {
        "id": f"task_{hash(title) % 10000:04d}",
        "title": title,
        "description": description,
        "priority": priority.value,
        "status": status.value,
        "created_at": datetime.now().isoformat(),
    }


# --- 2.5 Tool with Annotated Parameters ---
@mcp.tool()
def calculate_discount(
    original_price: Annotated[float, Field(gt=0, description="Original price (must be positive)")],
    discount_percent: Annotated[
        float, Field(ge=0, le=100, description="Discount percentage (0-100)")
    ],
) -> Dict[str, float]:
    """
    Calculate discounted price with validated parameters.

    Uses Annotated types with Field constraints for validation.

    Args:
        original_price: The original price (must be > 0)
        discount_percent: Discount percentage (0-100)

    Returns:
        Dictionary with original, discount amount, and final price
    """
    discount_amount = original_price * (discount_percent / 100)
    final_price = original_price - discount_amount

    return {
        "original_price": original_price,
        "discount_percent": discount_percent,
        "discount_amount": round(discount_amount, 2),
        "final_price": round(final_price, 2),
    }


# --- 2.6 Tool with Custom Metadata ---
@mcp.tool(
    name="advanced_search",
    description="Perform an advanced search with multiple filters",
    tags={"search", "query", "advanced"},
)
async def search_with_filters(
    query: str,
    max_results: int = 10,
    include_archived: bool = False,
    categories: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Advanced search tool with custom name and metadata.

    Demonstrates tool customization with name override, description,
    and tags for categorization.

    Args:
        query: Search query string
        max_results: Maximum results to return (default: 10)
        include_archived: Include archived items (default: False)
        categories: Filter by categories (optional)

    Returns:
        Search results with metadata
    """
    # Simulated search results
    results = [
        {"id": i, "title": f"Result {i} for '{query}'", "score": 0.9 - (i * 0.05)}
        for i in range(min(max_results, 5))
    ]

    return {
        "query": query,
        "total_results": len(results),
        "filters": {
            "max_results": max_results,
            "include_archived": include_archived,
            "categories": categories or [],
        },
        "results": results,
    }


# --- 2.7 Tool with Context (Logging, Progress, etc.) ---
@mcp.tool()
async def process_data_with_context(
    data_items: List[str],
    ctx: Context,
) -> Dict[str, Any]:
    """
    Process data items with context for logging and progress reporting.

    Demonstrates Context usage for:
    - Logging messages to MCP client (info, debug, warning, error)
    - Reporting progress during long operations
    - Accessing request metadata

    Args:
        data_items: List of data items to process
        ctx: MCP Context (automatically injected by FastMCP)

    Returns:
        Processing results with statistics
    """
    total = len(data_items)
    processed = []

    # Log start of processing
    await ctx.info(f"Starting to process {total} items")

    for i, item in enumerate(data_items):
        # Report progress to client
        await ctx.report_progress(
            progress=i,
            total=total,
            message=f"Processing item {i + 1}/{total}",
        )

        # Debug logging
        await ctx.debug(f"Processing: {item}")

        # Simulate processing
        await asyncio.sleep(0.05)
        processed.append({"item": item, "processed": True, "index": i})

    # Final progress update
    await ctx.report_progress(progress=total, total=total, message="Complete")

    # Log completion
    await ctx.info(f"Successfully processed {total} items")

    return {
        "total_processed": total,
        "items": processed,
        "status": "completed",
    }


# --- 2.8 Tool that Reads Other Resources ---
@mcp.tool()
async def analyze_config_with_context(
    config_name: str,
    ctx: Context,
) -> Dict[str, Any]:
    """
    Analyze a configuration by reading from server resources.

    Demonstrates ctx.read_resource() to access other resources
    registered on the same server.

    Args:
        config_name: Name of the config to analyze
        ctx: MCP Context for resource access

    Returns:
        Analysis results
    """
    await ctx.info(f"Analyzing configuration: {config_name}")

    try:
        # Read from a resource defined on this server
        resource_data = await ctx.read_resource(f"config://{config_name}")
        content = resource_data[0].content if resource_data else None

        return {
            "config_name": config_name,
            "found": content is not None,
            "content": content,
            "analysis": "Configuration loaded successfully" if content else "Configuration not found",
        }
    except Exception as e:
        await ctx.warning(f"Failed to read config: {e}")
        return {
            "config_name": config_name,
            "found": False,
            "error": str(e),
        }


# --- 2.9 Tool Returning Different Content Types ---
@mcp.tool()
def get_sample_data(format: str = "json") -> Any:
    """
    Return sample data in different formats.

    Demonstrates various return types:
    - dict/list -> JSON serialized
    - str -> TextContent
    - Pydantic model -> JSON serialized

    Args:
        format: Output format (json, text, model)

    Returns:
        Sample data in requested format
    """
    if format == "text":
        return "This is plain text content returned from the tool."
    elif format == "model":
        return UserProfile(name="Sample User", email="sample@example.com", age=30, tags=["demo"])
    else:  # json (default)
        return {
            "type": "sample_data",
            "items": [1, 2, 3, 4, 5],
            "metadata": {"format": format, "generated_at": datetime.now().isoformat()},
        }


# =============================================================================
# SECTION 3: RESOURCES - Read-only data sources (like GET endpoints)
# =============================================================================

# --- 3.1 Static Resource ---
@mcp.resource("config://version")
def get_version() -> str:
    """
    Static resource returning server version.

    URI: config://version

    Returns the current server version string.
    """
    return "1.0.0"


# --- 3.2 Static Resource with JSON Data ---
@mcp.resource("config://settings")
def get_settings() -> Dict[str, Any]:
    """
    Static resource returning server settings as JSON.

    URI: config://settings

    Resources can return dictionaries that get serialized to JSON.
    """
    return {
        "max_connections": 100,
        "timeout_seconds": 30,
        "features": {
            "async_processing": True,
            "caching": True,
            "logging": True,
        },
        "supported_formats": ["json", "xml", "csv"],
    }


# --- 3.3 Dynamic Resource Template (Single Parameter) ---
@mcp.resource("user://{user_id}/profile")
def get_user_profile(user_id: str) -> Dict[str, Any]:
    """
    Dynamic resource template for user profiles.

    URI Template: user://{user_id}/profile
    Example: user://12345/profile

    Parameters in curly braces become function arguments.

    Args:
        user_id: User ID from the URI

    Returns:
        User profile data
    """
    # Simulated user data
    return {
        "user_id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com",
        "created_at": "2024-01-01T00:00:00Z",
        "preferences": {
            "theme": "dark",
            "language": "en",
        },
    }


# --- 3.4 Dynamic Resource Template (Multiple Parameters) ---
@mcp.resource("data://{category}/{item_id}")
def get_data_item(category: str, item_id: str) -> Dict[str, Any]:
    """
    Dynamic resource with multiple URI parameters.

    URI Template: data://{category}/{item_id}
    Examples:
        - data://products/123
        - data://orders/456
        - data://users/789

    Args:
        category: Data category from URI
        item_id: Item ID within the category

    Returns:
        Item data
    """
    return {
        "category": category,
        "item_id": item_id,
        "data": f"Sample data for {category}/{item_id}",
        "fetched_at": datetime.now().isoformat(),
    }


# --- 3.5 Async Dynamic Resource ---
@mcp.resource("api://{endpoint}/status")
async def get_api_status(endpoint: str) -> Dict[str, Any]:
    """
    Async resource for checking API endpoint status.

    URI Template: api://{endpoint}/status
    Example: api://users/status

    Resources can be async for I/O operations.

    Args:
        endpoint: API endpoint name

    Returns:
        Endpoint status information
    """
    # Simulate async status check
    await asyncio.sleep(0.01)

    return {
        "endpoint": endpoint,
        "status": "healthy",
        "latency_ms": 45,
        "last_check": datetime.now().isoformat(),
    }


# --- 3.6 Resource with Typed Parameters ---
@mcp.resource("metrics://{service}/last/{count}")
def get_service_metrics(service: str, count: int) -> Dict[str, Any]:
    """
    Resource template with typed parameters.

    URI Template: metrics://{service}/last/{count}
    Example: metrics://api-gateway/last/10

    Parameters are automatically converted to their type hints.

    Args:
        service: Service name
        count: Number of metrics to return (converted to int)

    Returns:
        Service metrics data
    """
    # Generate sample metrics
    metrics = [
        {"timestamp": f"2024-01-{i + 1:02d}T00:00:00Z", "value": 100 + i * 5, "unit": "ms"}
        for i in range(min(count, 10))
    ]

    return {
        "service": service,
        "requested_count": count,
        "actual_count": len(metrics),
        "metrics": metrics,
    }


# =============================================================================
# SECTION 4: PROMPTS - Reusable message templates for LLM interactions
# =============================================================================

# --- 4.1 Simple Prompt ---
@mcp.prompt()
def greeting_prompt(name: str) -> str:
    """
    Simple greeting prompt template.

    Prompts return strings that guide LLM interactions.

    Args:
        name: Name of the person to greet

    Returns:
        Greeting prompt string
    """
    return f"Please write a warm, friendly greeting for someone named {name}."


# --- 4.2 Prompt with Multiple Parameters ---
@mcp.prompt()
def code_review_prompt(
    language: str,
    code_snippet: str,
    focus_areas: Optional[List[str]] = None,
) -> str:
    """
    Code review prompt with multiple parameters.

    Args:
        language: Programming language of the code
        code_snippet: The code to review
        focus_areas: Specific areas to focus on (optional)

    Returns:
        Code review prompt
    """
    focus_text = ""
    if focus_areas:
        focus_text = f"\n\nPlease focus specifically on: {', '.join(focus_areas)}"

    return f"""Please review the following {language} code and provide feedback on:
1. Code quality and readability
2. Potential bugs or issues
3. Performance considerations
4. Best practices{focus_text}

Code to review:
```{language}
{code_snippet}
```"""


# --- 4.3 Prompt with Custom Metadata ---
@mcp.prompt(
    name="data_analysis_request",
    description="Creates a structured request for data analysis",
    tags={"analysis", "data", "structured"},
)
def data_analysis_prompt(
    data_description: str,
    analysis_type: str = "summary",
    output_format: str = "markdown",
) -> str:
    """
    Data analysis prompt with custom name and metadata.

    Demonstrates prompt customization with tags for categorization.

    Args:
        data_description: Description of the data to analyze
        analysis_type: Type of analysis (summary, detailed, statistical)
        output_format: Desired output format (markdown, json, plain)

    Returns:
        Data analysis request prompt
    """
    return f"""Please perform a '{analysis_type}' analysis on the following data.

Data Description:
{data_description}

Requirements:
- Analysis Type: {analysis_type}
- Output Format: {output_format}
- Include key insights and recommendations
- Highlight any anomalies or patterns

Please structure your response in {output_format} format."""


# --- 4.4 Prompt Returning Structured Messages ---
@mcp.prompt()
def conversation_starter_prompt(
    topic: str,
    expertise_level: str = "intermediate",
) -> List[Dict[str, str]]:
    """
    Prompt returning structured message list.

    Prompts can return a list of message dictionaries
    for more complex conversation setups.

    Args:
        topic: Topic for the conversation
        expertise_level: User's expertise level

    Returns:
        List of message dictionaries
    """
    return [
        {
            "role": "system",
            "content": f"You are an expert assistant helping with {topic}. "
            f"Adjust your explanations for a {expertise_level} level audience.",
        },
        {
            "role": "user",
            "content": f"I'd like to learn more about {topic}. "
            f"Please start with an overview appropriate for my {expertise_level} level.",
        },
    ]


# =============================================================================
# SECTION 5: SERVER COMPOSITION - Combining Multiple Servers
# =============================================================================

# --- 5.1 Create a Sub-Server for Math Operations ---
math_server = FastMCP(name="Math Operations Server")


@math_server.tool()
def add(x: int, y: int) -> int:
    """Add two integers."""
    return x + y


@math_server.tool()
def subtract(x: int, y: int) -> int:
    """Subtract y from x."""
    return x - y


@math_server.tool()
def divide(x: float, y: float) -> float:
    """Divide x by y."""
    if y == 0:
        raise ValueError("Cannot divide by zero")
    return x / y


@math_server.resource("math://constants/pi")
def get_pi() -> float:
    """Return the value of pi."""
    return 3.14159265359


@math_server.resource("math://constants/e")
def get_e() -> float:
    """Return the value of e (Euler's number)."""
    return 2.71828182845


# --- 5.2 Create a Sub-Server for String Operations ---
string_server = FastMCP(name="String Operations Server")


@string_server.tool()
def reverse_string(text: str) -> str:
    """Reverse a string."""
    return text[::-1]


@string_server.tool()
def count_words(text: str) -> int:
    """Count words in a string."""
    return len(text.split())


@string_server.tool()
def to_uppercase(text: str) -> str:
    """Convert string to uppercase."""
    return text.upper()


@string_server.resource("string://stats/{text}")
def get_string_stats(text: str) -> Dict[str, Any]:
    """Get statistics about a string."""
    return {
        "length": len(text),
        "words": len(text.split()),
        "characters_no_spaces": len(text.replace(" ", "")),
        "uppercase_count": sum(1 for c in text if c.isupper()),
        "lowercase_count": sum(1 for c in text if c.islower()),
    }


# --- 5.3 Import Sub-Servers into Main Server ---
# import_server() copies all components with optional prefix
# This is "static composition" - one-time copy at startup

mcp.import_server(math_server, prefix="math")
# Tools become: math_add, math_subtract, math_divide
# Resources become: math://math/constants/pi, math://math/constants/e

mcp.import_server(string_server, prefix="str")
# Tools become: str_reverse_string, str_count_words, str_to_uppercase
# Resources become: str://string/stats/{text}


# --- 5.4 Mount Sub-Server (Alternative to import_server) ---
# Note: mount() creates a live link vs import_server() which copies
# Uncomment to use mount instead:
# mcp.mount(math_server, prefix="live_math")

# =============================================================================
# SECTION 6: FASTAPI INTEGRATION
# =============================================================================


def create_fastapi_app():
    """
    Create a FastAPI application with mounted MCP server.

    This demonstrates the integration between FastMCP and FastAPI,
    allowing you to serve MCP alongside REST endpoints.
    """
    from contextlib import asynccontextmanager

    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    # Create combined lifespan for FastAPI and MCP
    @asynccontextmanager
    async def combined_lifespan(app: FastAPI):
        """Combined lifespan manager for FastAPI and MCP."""
        # Startup
        print("Starting FastAPI application with MCP server...")
        yield
        # Shutdown
        print("Shutting down...")

    # Create FastAPI app
    fastapi_app = FastAPI(
        title="FastMCP Showcase API",
        description="A demonstration of FastMCP integrated with FastAPI",
        version="1.0.0",
        lifespan=combined_lifespan,
    )

    # Add CORS middleware
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- REST Endpoints ---
    @fastapi_app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "name": "FastMCP Showcase API",
            "version": "1.0.0",
            "mcp_endpoint": "/mcp",
            "docs": "/docs",
            "health": "/health",
        }

    @fastapi_app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}

    @fastapi_app.get("/api/tools")
    async def list_available_tools():
        """List all available MCP tools (REST wrapper)."""
        tools = await mcp.get_tools()
        return {
            "count": len(tools),
            "tools": [
                {"name": name, "description": tool.description} for name, tool in tools.items()
            ],
        }

    @fastapi_app.get("/api/resources")
    async def list_available_resources():
        """List all available MCP resources (REST wrapper)."""
        resources = await mcp.get_resources()
        templates = await mcp.get_resource_templates()
        return {
            "resources_count": len(resources),
            "templates_count": len(templates),
            "resources": [
                {"uri": str(r.uri), "name": r.name, "description": r.description}
                for r in resources.values()
            ],
            "templates": [
                {"uri_template": str(t.uri_template), "name": t.name, "description": t.description}
                for t in templates.values()
            ],
        }

    @fastapi_app.get("/api/prompts")
    async def list_available_prompts():
        """List all available MCP prompts (REST wrapper)."""
        prompts = await mcp.get_prompts()
        return {
            "count": len(prompts),
            "prompts": [
                {"name": name, "description": prompt.description} for name, prompt in prompts.items()
            ],
        }

    # --- Mount MCP Server ---
    # Get the MCP ASGI application and mount it
    mcp_asgi_app = mcp.http_app(path="/mcp")
    fastapi_app.mount("/mcp", mcp_asgi_app)

    return fastapi_app


# =============================================================================
# SECTION 7: MAIN ENTRY POINT
# =============================================================================


def print_showcase_info():
    """Print information about the showcase server."""
    print("=" * 60)
    print("FastMCP Core Components Showcase")
    print("=" * 60)
    print()
    print("This server demonstrates all FastMCP core features:")
    print()
    print("TOOLS (Functions LLMs can execute):")
    print("  - add_numbers: Simple sync tool")
    print("  - multiply_numbers: Async tool")
    print("  - create_user: Pydantic model input")
    print("  - create_task: Enum parameters")
    print("  - calculate_discount: Annotated validation")
    print("  - advanced_search: Custom metadata")
    print("  - process_data_with_context: Context usage")
    print("  - analyze_config_with_context: Resource access")
    print("  - get_sample_data: Multiple return types")
    print("  - math_add, math_subtract, math_divide: Composed from sub-server")
    print("  - str_reverse_string, str_count_words, str_to_uppercase: Composed")
    print()
    print("RESOURCES (Read-only data sources):")
    print("  - config://version: Static resource")
    print("  - config://settings: JSON data resource")
    print("  - user://{user_id}/profile: Dynamic template")
    print("  - data://{category}/{item_id}: Multi-param template")
    print("  - api://{endpoint}/status: Async resource")
    print("  - metrics://{service}/last/{count}: Typed params")
    print("  - math://math/constants/pi: Composed resource")
    print("  - math://math/constants/e: Composed resource")
    print()
    print("PROMPTS (Reusable LLM templates):")
    print("  - greeting_prompt: Simple prompt")
    print("  - code_review_prompt: Multi-param prompt")
    print("  - data_analysis_request: Custom metadata")
    print("  - conversation_starter_prompt: Structured messages")
    print()
    print("=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="FastMCP Showcase Server")
    parser.add_argument(
        "--http",
        action="store_true",
        help="Run as HTTP server (default: stdio for MCP)",
    )
    parser.add_argument(
        "--fastapi",
        action="store_true",
        help="Run with FastAPI integration",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for HTTP/FastAPI server (default: 8000)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host for HTTP/FastAPI server (default: 0.0.0.0)",
    )

    args = parser.parse_args()

    if args.fastapi:
        # Run with FastAPI integration
        import uvicorn

        print_showcase_info()
        print()
        print(f"Starting FastAPI server at http://{args.host}:{args.port}")
        print(f"MCP endpoint: http://{args.host}:{args.port}/mcp")
        print(f"API docs: http://{args.host}:{args.port}/docs")
        print("=" * 60)

        app = create_fastapi_app()
        uvicorn.run(app, host=args.host, port=args.port)

    elif args.http:
        # Run as HTTP server (streamable-http transport)
        import uvicorn

        print_showcase_info()
        print()
        print(f"Starting HTTP MCP server at http://{args.host}:{args.port}")
        print("=" * 60)

        # Get the HTTP app directly from FastMCP
        http_app = mcp.http_app()
        uvicorn.run(http_app, host=args.host, port=args.port)

    else:
        # Run as stdio server (default for Claude Desktop)
        print_showcase_info()
        print()
        print("Starting MCP server in stdio mode...")
        print("(Use --http or --fastapi for HTTP modes)")
        print("=" * 60)

        mcp.run()
