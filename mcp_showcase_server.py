#!/usr/bin/env python3
"""
MCP Showcase Server with Gradio Interface

A comprehensive demonstration of MCP server capabilities with:
- FastMCP tools, resources, and prompts
- Gradio web interface for interactive testing
- REST API endpoints for programmatic access
- SSE transport for real-time communication

This server demonstrates best practices for building MCP servers
that can be consumed by any MCP-compatible client.
"""

import asyncio
import json
import logging
import math
import os
import random
import re
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from enum import Enum
from typing import Annotated, Any, Dict, List, Optional

import gradio as gr
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP
from pydantic import BaseModel, Field

# =============================================================================
# Configuration & Setup
# =============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8080"))
SERVER_HOST = os.getenv("MCP_SERVER_HOST", "0.0.0.0")

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# =============================================================================
# MCP Server Initialization
# =============================================================================

mcp = FastMCP(
    name="MCP Showcase Server",
    version="1.0.0",
)

# =============================================================================
# Enums for Type-Safe Parameters
# =============================================================================


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DataFormat(str, Enum):
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    YAML = "yaml"


class MathOperation(str, Enum):
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"
    POWER = "power"
    SQRT = "sqrt"


# =============================================================================
# Pydantic Models for Complex Input/Output
# =============================================================================


class TaskInput(BaseModel):
    """Input model for task creation."""
    title: str = Field(..., description="Task title", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Task description")
    priority: Priority = Field(Priority.MEDIUM, description="Task priority level")
    tags: List[str] = Field(default_factory=list, description="Optional tags")
    due_date: Optional[str] = Field(None, description="Due date in YYYY-MM-DD format")


class TaskOutput(BaseModel):
    """Output model for task responses."""
    id: str
    title: str
    description: Optional[str]
    priority: str
    tags: List[str]
    due_date: Optional[str]
    created_at: str
    status: str


class AnalysisResult(BaseModel):
    """Output model for data analysis."""
    summary: Dict[str, Any]
    statistics: Dict[str, float]
    insights: List[str]
    timestamp: str


# =============================================================================
# In-Memory Storage (for demonstration)
# =============================================================================

task_storage: Dict[str, TaskOutput] = {}
note_storage: Dict[str, Dict[str, Any]] = {}
counter_storage: Dict[str, int] = {"global_counter": 0}


# =============================================================================
# MCP TOOLS
# =============================================================================


@mcp.tool()
def hello_world(name: str = "World") -> str:
    """
    A simple greeting tool.

    This is the most basic tool example - takes a name and returns a greeting.

    Args:
        name: The name to greet (default: "World")

    Returns:
        A friendly greeting message
    """
    return f"Hello, {name}! Welcome to the MCP Showcase Server."


@mcp.tool()
def calculate(
    operation: MathOperation,
    a: Annotated[float, Field(description="First operand")],
    b: Annotated[Optional[float], Field(description="Second operand (not needed for sqrt)")] = None,
) -> Dict[str, Any]:
    """
    Perform mathematical calculations.

    Supports basic arithmetic operations with proper error handling.

    Args:
        operation: The math operation to perform
        a: First operand
        b: Second operand (not needed for sqrt)

    Returns:
        Result with operation details
    """
    operations = {
        MathOperation.ADD: lambda x, y: x + y,
        MathOperation.SUBTRACT: lambda x, y: x - y,
        MathOperation.MULTIPLY: lambda x, y: x * y,
        MathOperation.DIVIDE: lambda x, y: x / y if y != 0 else float("inf"),
        MathOperation.POWER: lambda x, y: x ** y,
        MathOperation.SQRT: lambda x, _: math.sqrt(x) if x >= 0 else float("nan"),
    }

    result = operations[operation](a, b or 0)

    return {
        "operation": operation.value,
        "operands": {"a": a, "b": b},
        "result": result,
        "timestamp": datetime.now().isoformat(),
    }


@mcp.tool()
async def create_task(task: TaskInput) -> TaskOutput:
    """
    Create a new task with Pydantic validation.

    Demonstrates complex input validation using Pydantic models.

    Args:
        task: Task details including title, description, priority, and tags

    Returns:
        Created task with generated ID and timestamps
    """
    task_id = f"task_{len(task_storage) + 1:04d}"

    output = TaskOutput(
        id=task_id,
        title=task.title,
        description=task.description,
        priority=task.priority.value,
        tags=task.tags,
        due_date=task.due_date,
        created_at=datetime.now().isoformat(),
        status="pending",
    )

    task_storage[task_id] = output
    logger.info(f"Created task: {task_id}")

    return output


@mcp.tool()
def list_tasks(
    priority_filter: Optional[Priority] = None,
    limit: Annotated[int, Field(ge=1, le=100, description="Max tasks to return")] = 10,
) -> Dict[str, Any]:
    """
    List all tasks with optional filtering.

    Args:
        priority_filter: Filter by priority level
        limit: Maximum number of tasks to return

    Returns:
        List of tasks matching the criteria
    """
    tasks = list(task_storage.values())

    if priority_filter:
        tasks = [t for t in tasks if t.priority == priority_filter.value]

    tasks = tasks[:limit]

    return {
        "total": len(task_storage),
        "filtered_count": len(tasks),
        "tasks": [t.model_dump() for t in tasks],
    }


@mcp.tool()
async def analyze_text(
    text: str,
    include_sentiment: bool = True,
    include_keywords: bool = True,
) -> AnalysisResult:
    """
    Analyze text content and extract insights.

    Provides word count, character statistics, and basic text analysis.

    Args:
        text: The text to analyze
        include_sentiment: Whether to include sentiment analysis
        include_keywords: Whether to extract keywords

    Returns:
        Analysis result with statistics and insights
    """
    # Basic statistics
    words = text.split()
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    statistics = {
        "word_count": len(words),
        "character_count": len(text),
        "sentence_count": len(sentences),
        "avg_word_length": sum(len(w) for w in words) / len(words) if words else 0,
        "avg_sentence_length": len(words) / len(sentences) if sentences else 0,
    }

    insights = []

    # Simple keyword extraction (most frequent words > 4 chars)
    if include_keywords:
        word_freq = {}
        for word in words:
            clean_word = re.sub(r"[^\w]", "", word.lower())
            if len(clean_word) > 4:
                word_freq[clean_word] = word_freq.get(clean_word, 0) + 1

        top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        if top_keywords:
            insights.append(f"Top keywords: {', '.join(k for k, _ in top_keywords)}")

    # Simple sentiment (very basic)
    if include_sentiment:
        positive_words = {"good", "great", "excellent", "amazing", "wonderful", "happy", "love"}
        negative_words = {"bad", "terrible", "awful", "hate", "sad", "poor", "wrong"}

        lower_words = set(w.lower() for w in words)
        pos_count = len(lower_words & positive_words)
        neg_count = len(lower_words & negative_words)

        if pos_count > neg_count:
            sentiment = "positive"
        elif neg_count > pos_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        insights.append(f"Sentiment: {sentiment}")
        statistics["positive_word_count"] = pos_count
        statistics["negative_word_count"] = neg_count

    return AnalysisResult(
        summary={
            "text_preview": text[:100] + "..." if len(text) > 100 else text,
            "analysis_type": "full" if include_sentiment and include_keywords else "partial",
        },
        statistics=statistics,
        insights=insights,
        timestamp=datetime.now().isoformat(),
    )


@mcp.tool()
def convert_data(
    data: str,
    from_format: DataFormat,
    to_format: DataFormat,
) -> Dict[str, Any]:
    """
    Convert data between different formats.

    Demonstrates format handling and data transformation.
    Note: This is a simplified demonstration - real implementation would use proper parsers.

    Args:
        data: The input data string
        from_format: Source data format
        to_format: Target data format

    Returns:
        Converted data with metadata
    """
    # Simplified conversion demonstration
    result = {
        "original_format": from_format.value,
        "target_format": to_format.value,
        "input_size": len(data),
        "timestamp": datetime.now().isoformat(),
    }

    if from_format == DataFormat.JSON:
        try:
            parsed = json.loads(data)
            if to_format == DataFormat.CSV:
                if isinstance(parsed, list) and parsed:
                    headers = list(parsed[0].keys()) if isinstance(parsed[0], dict) else ["value"]
                    csv_lines = [",".join(headers)]
                    for item in parsed:
                        if isinstance(item, dict):
                            csv_lines.append(",".join(str(item.get(h, "")) for h in headers))
                        else:
                            csv_lines.append(str(item))
                    result["converted"] = "\n".join(csv_lines)
                else:
                    result["converted"] = str(parsed)
            elif to_format == DataFormat.YAML:
                # Simple YAML-like output
                def to_yaml(obj, indent=0):
                    lines = []
                    if isinstance(obj, dict):
                        for k, v in obj.items():
                            if isinstance(v, (dict, list)):
                                lines.append("  " * indent + f"{k}:")
                                lines.extend(to_yaml(v, indent + 1))
                            else:
                                lines.append("  " * indent + f"{k}: {v}")
                    elif isinstance(obj, list):
                        for item in obj:
                            lines.append("  " * indent + f"- {item}" if not isinstance(item, (dict, list)) else "  " * indent + "-")
                            if isinstance(item, (dict, list)):
                                lines.extend(to_yaml(item, indent + 1))
                    return lines
                result["converted"] = "\n".join(to_yaml(parsed))
            else:
                result["converted"] = json.dumps(parsed, indent=2)
            result["status"] = "success"
        except json.JSONDecodeError as e:
            result["status"] = "error"
            result["error"] = f"Invalid JSON: {e}"
    else:
        result["status"] = "partial"
        result["note"] = f"Conversion from {from_format.value} is simplified for this demo"
        result["converted"] = data

    return result


@mcp.tool()
def generate_sample_data(
    data_type: str = "users",
    count: Annotated[int, Field(ge=1, le=100, description="Number of records")] = 5,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Generate sample data for testing and demonstration.

    Args:
        data_type: Type of data to generate (users, products, events)
        count: Number of records to generate
        seed: Random seed for reproducibility

    Returns:
        Generated sample data
    """
    if seed is not None:
        random.seed(seed)

    generators = {
        "users": lambda i: {
            "id": f"user_{i:04d}",
            "name": f"User {i}",
            "email": f"user{i}@example.com",
            "age": random.randint(18, 65),
            "active": random.choice([True, False]),
        },
        "products": lambda i: {
            "id": f"prod_{i:04d}",
            "name": f"Product {i}",
            "price": round(random.uniform(10, 500), 2),
            "category": random.choice(["electronics", "clothing", "food", "books"]),
            "stock": random.randint(0, 100),
        },
        "events": lambda i: {
            "id": f"evt_{i:04d}",
            "type": random.choice(["click", "view", "purchase", "signup"]),
            "timestamp": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
            "user_id": f"user_{random.randint(1, 100):04d}",
            "metadata": {"source": random.choice(["web", "mobile", "api"])},
        },
    }

    generator = generators.get(data_type, generators["users"])
    data = [generator(i + 1) for i in range(count)]

    return {
        "data_type": data_type,
        "count": count,
        "records": data,
        "generated_at": datetime.now().isoformat(),
    }


@mcp.tool()
def increment_counter(
    counter_name: str = "global_counter",
    amount: int = 1,
) -> Dict[str, int]:
    """
    Increment a named counter (demonstrates stateful operations).

    Args:
        counter_name: Name of the counter to increment
        amount: Amount to increment by

    Returns:
        Updated counter value
    """
    if counter_name not in counter_storage:
        counter_storage[counter_name] = 0

    counter_storage[counter_name] += amount

    return {
        "counter": counter_name,
        "previous": counter_storage[counter_name] - amount,
        "current": counter_storage[counter_name],
        "increment": amount,
    }


# =============================================================================
# MCP RESOURCES
# =============================================================================


@mcp.resource("config://server/info")
def get_server_info() -> Dict[str, Any]:
    """
    Get server configuration and status information.

    URI: config://server/info
    """
    return {
        "name": "MCP Showcase Server",
        "version": "1.0.0",
        "status": "running",
        "uptime": "N/A",  # Would track actual uptime in production
        "features": ["tools", "resources", "prompts", "gradio-ui", "rest-api"],
        "timestamp": datetime.now().isoformat(),
    }


@mcp.resource("config://server/stats")
def get_server_stats() -> Dict[str, Any]:
    """
    Get server statistics.

    URI: config://server/stats
    """
    return {
        "tasks_created": len(task_storage),
        "notes_created": len(note_storage),
        "counters": counter_storage.copy(),
        "timestamp": datetime.now().isoformat(),
    }


@mcp.resource("tasks://{task_id}")
def get_task_resource(task_id: str) -> Dict[str, Any]:
    """
    Get a specific task by ID.

    URI Template: tasks://{task_id}
    Example: tasks://task_0001
    """
    if task_id in task_storage:
        return task_storage[task_id].model_dump()
    return {"error": f"Task {task_id} not found"}


@mcp.resource("data://samples/{data_type}")
def get_sample_data_resource(data_type: str) -> Dict[str, Any]:
    """
    Get sample data by type.

    URI Template: data://samples/{data_type}
    Examples: data://samples/users, data://samples/products
    """
    return generate_sample_data(data_type=data_type, count=3, seed=42)


@mcp.resource("docs://api/tools")
def get_tools_documentation() -> str:
    """
    Get documentation for all available tools.

    URI: docs://api/tools
    """
    tools_info = []
    tools_info.append("# MCP Showcase Server - Available Tools\n")
    tools_info.append("This server provides the following tools:\n")

    tool_list = [
        ("hello_world", "Simple greeting tool"),
        ("calculate", "Mathematical calculations (add, subtract, multiply, divide, power, sqrt)"),
        ("create_task", "Create a new task with Pydantic validation"),
        ("list_tasks", "List tasks with filtering"),
        ("analyze_text", "Analyze text content"),
        ("convert_data", "Convert between data formats"),
        ("generate_sample_data", "Generate sample test data"),
        ("increment_counter", "Increment named counters"),
    ]

    for name, desc in tool_list:
        tools_info.append(f"- **{name}**: {desc}")

    return "\n".join(tools_info)


@mcp.resource("docs://api/resources")
def get_resources_documentation() -> str:
    """
    Get documentation for all available resources.

    URI: docs://api/resources
    """
    resources_info = []
    resources_info.append("# MCP Showcase Server - Available Resources\n")

    resource_list = [
        ("config://server/info", "Server configuration and status"),
        ("config://server/stats", "Server statistics"),
        ("tasks://{task_id}", "Get task by ID"),
        ("data://samples/{data_type}", "Sample data by type"),
        ("docs://api/tools", "Tools documentation"),
        ("docs://api/resources", "Resources documentation (this page)"),
    ]

    for uri, desc in resource_list:
        resources_info.append(f"- `{uri}`: {desc}")

    return "\n".join(resources_info)


# =============================================================================
# MCP PROMPTS
# =============================================================================


@mcp.prompt()
def task_creation_prompt(
    project_name: str,
    task_type: str = "feature",
) -> str:
    """
    Generate a prompt for creating well-structured tasks.

    Args:
        project_name: Name of the project
        task_type: Type of task (feature, bug, improvement)

    Returns:
        A structured prompt for task creation
    """
    return f"""You are helping to create a {task_type} task for the project "{project_name}".

Please provide the following information:
1. Task title (clear and concise)
2. Description (detailed explanation of what needs to be done)
3. Priority (low, medium, high, critical)
4. Any relevant tags
5. Due date if applicable

Format the response as a structured task that can be used with the create_task tool."""


@mcp.prompt()
def data_analysis_prompt(
    data_description: str,
    analysis_goals: List[str],
) -> str:
    """
    Generate a prompt for data analysis tasks.

    Args:
        data_description: Description of the data to analyze
        analysis_goals: List of analysis goals

    Returns:
        A structured prompt for data analysis
    """
    goals_text = "\n".join(f"- {goal}" for goal in analysis_goals)

    return f"""Analyze the following data:

{data_description}

Analysis Goals:
{goals_text}

Please provide:
1. Summary of key findings
2. Relevant statistics
3. Insights and recommendations
4. Any anomalies or concerns

Use the analyze_text and generate_sample_data tools as needed."""


@mcp.prompt()
def code_review_prompt(
    language: str,
    focus_areas: Optional[List[str]] = None,
) -> List[Dict[str, str]]:
    """
    Generate a multi-turn prompt for code review.

    Args:
        language: Programming language of the code
        focus_areas: Specific areas to focus on

    Returns:
        List of messages for a code review conversation
    """
    focus_text = ""
    if focus_areas:
        focus_text = f"\n\nFocus particularly on: {', '.join(focus_areas)}"

    return [
        {
            "role": "user",
            "content": f"I need help reviewing {language} code.{focus_text}",
        },
        {
            "role": "assistant",
            "content": f"""I'll help you review your {language} code. Please share the code and I'll analyze it for:

1. **Code Quality**: Readability, maintainability, and best practices
2. **Potential Bugs**: Logic errors, edge cases, and error handling
3. **Performance**: Efficiency and optimization opportunities
4. **Security**: Common vulnerabilities and security best practices
5. **Documentation**: Comments and documentation completeness

Please paste your code.""",
        },
    ]


# =============================================================================
# GRADIO INTERFACE
# =============================================================================


def create_gradio_interface() -> gr.Blocks:
    """Create the Gradio web interface for the MCP server."""

    with gr.Blocks(
        title="MCP Showcase Server",
        theme=gr.themes.Soft(),
    ) as demo:
        gr.Markdown("""
        # MCP Showcase Server

        Interactive interface for testing MCP tools, resources, and prompts.

        This server demonstrates how to build a comprehensive MCP server with:
        - **Tools**: Executable functions with validated inputs
        - **Resources**: URI-based data access
        - **Prompts**: Reusable prompt templates
        - **REST API**: HTTP endpoints for programmatic access
        - **SSE Transport**: Real-time communication for clients
        """)

        with gr.Tabs():
            # =================================================================
            # Tools Tab
            # =================================================================
            with gr.Tab("Tools"):
                gr.Markdown("## Test MCP Tools")

                with gr.Accordion("Hello World", open=True):
                    with gr.Row():
                        hello_name = gr.Textbox(label="Name", value="World")
                        hello_btn = gr.Button("Say Hello", variant="primary")
                    hello_output = gr.Textbox(label="Result", interactive=False)

                    hello_btn.click(
                        fn=hello_world,
                        inputs=[hello_name],
                        outputs=[hello_output],
                    )

                with gr.Accordion("Calculator", open=False):
                    with gr.Row():
                        calc_op = gr.Dropdown(
                            choices=[e.value for e in MathOperation],
                            label="Operation",
                            value="add",
                        )
                        calc_a = gr.Number(label="A", value=10)
                        calc_b = gr.Number(label="B (optional for sqrt)", value=5)
                    calc_btn = gr.Button("Calculate", variant="primary")
                    calc_output = gr.JSON(label="Result")

                    def run_calculate(op, a, b):
                        return calculate(MathOperation(op), a, b)

                    calc_btn.click(
                        fn=run_calculate,
                        inputs=[calc_op, calc_a, calc_b],
                        outputs=[calc_output],
                    )

                with gr.Accordion("Create Task", open=False):
                    with gr.Row():
                        task_title = gr.Textbox(label="Title")
                        task_desc = gr.Textbox(label="Description")
                    with gr.Row():
                        task_priority = gr.Dropdown(
                            choices=[e.value for e in Priority],
                            label="Priority",
                            value="medium",
                        )
                        task_tags = gr.Textbox(label="Tags (comma-separated)")
                        task_due = gr.Textbox(label="Due Date (YYYY-MM-DD)")
                    task_btn = gr.Button("Create Task", variant="primary")
                    task_output = gr.JSON(label="Created Task")

                    async def run_create_task(title, desc, priority, tags, due):
                        tags_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
                        task_input = TaskInput(
                            title=title,
                            description=desc or None,
                            priority=Priority(priority),
                            tags=tags_list,
                            due_date=due or None,
                        )
                        result = await create_task(task_input)
                        return result.model_dump()

                    task_btn.click(
                        fn=run_create_task,
                        inputs=[task_title, task_desc, task_priority, task_tags, task_due],
                        outputs=[task_output],
                    )

                with gr.Accordion("Text Analysis", open=False):
                    text_input = gr.Textbox(
                        label="Text to Analyze",
                        lines=5,
                        placeholder="Enter text to analyze...",
                    )
                    with gr.Row():
                        include_sentiment = gr.Checkbox(label="Include Sentiment", value=True)
                        include_keywords = gr.Checkbox(label="Include Keywords", value=True)
                    analyze_btn = gr.Button("Analyze", variant="primary")
                    analyze_output = gr.JSON(label="Analysis Result")

                    async def run_analyze(text, sentiment, keywords):
                        result = await analyze_text(text, sentiment, keywords)
                        return result.model_dump()

                    analyze_btn.click(
                        fn=run_analyze,
                        inputs=[text_input, include_sentiment, include_keywords],
                        outputs=[analyze_output],
                    )

                with gr.Accordion("Generate Sample Data", open=False):
                    with gr.Row():
                        data_type = gr.Dropdown(
                            choices=["users", "products", "events"],
                            label="Data Type",
                            value="users",
                        )
                        data_count = gr.Slider(
                            minimum=1,
                            maximum=20,
                            value=5,
                            step=1,
                            label="Count",
                        )
                        data_seed = gr.Number(label="Seed (optional)", value=None)
                    generate_btn = gr.Button("Generate", variant="primary")
                    generate_output = gr.JSON(label="Generated Data")

                    def run_generate(dtype, count, seed):
                        return generate_sample_data(
                            dtype,
                            int(count),
                            int(seed) if seed else None,
                        )

                    generate_btn.click(
                        fn=run_generate,
                        inputs=[data_type, data_count, data_seed],
                        outputs=[generate_output],
                    )

            # =================================================================
            # Resources Tab
            # =================================================================
            with gr.Tab("Resources"):
                gr.Markdown("## Access MCP Resources")

                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Server Info")
                        server_info_btn = gr.Button("Get Server Info")
                        server_info_output = gr.JSON()

                        server_info_btn.click(
                            fn=get_server_info,
                            outputs=[server_info_output],
                        )

                    with gr.Column():
                        gr.Markdown("### Server Stats")
                        server_stats_btn = gr.Button("Get Server Stats")
                        server_stats_output = gr.JSON()

                        server_stats_btn.click(
                            fn=get_server_stats,
                            outputs=[server_stats_output],
                        )

                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Task Resource")
                        task_id_input = gr.Textbox(label="Task ID", placeholder="task_0001")
                        task_resource_btn = gr.Button("Get Task")
                        task_resource_output = gr.JSON()

                        task_resource_btn.click(
                            fn=get_task_resource,
                            inputs=[task_id_input],
                            outputs=[task_resource_output],
                        )

                    with gr.Column():
                        gr.Markdown("### Sample Data Resource")
                        sample_type_input = gr.Dropdown(
                            choices=["users", "products", "events"],
                            label="Data Type",
                            value="users",
                        )
                        sample_resource_btn = gr.Button("Get Samples")
                        sample_resource_output = gr.JSON()

                        sample_resource_btn.click(
                            fn=get_sample_data_resource,
                            inputs=[sample_type_input],
                            outputs=[sample_resource_output],
                        )

                with gr.Row():
                    gr.Markdown("### Documentation")
                    docs_type = gr.Radio(
                        choices=["tools", "resources"],
                        label="Documentation Type",
                        value="tools",
                    )
                    docs_btn = gr.Button("Get Documentation")
                    docs_output = gr.Markdown()

                    def get_docs(doc_type):
                        if doc_type == "tools":
                            return get_tools_documentation()
                        return get_resources_documentation()

                    docs_btn.click(
                        fn=get_docs,
                        inputs=[docs_type],
                        outputs=[docs_output],
                    )

            # =================================================================
            # Prompts Tab
            # =================================================================
            with gr.Tab("Prompts"):
                gr.Markdown("## MCP Prompts")
                gr.Markdown("Prompts are reusable templates that help structure LLM interactions.")

                with gr.Accordion("Task Creation Prompt", open=True):
                    with gr.Row():
                        project_name = gr.Textbox(label="Project Name", value="My Project")
                        task_type = gr.Dropdown(
                            choices=["feature", "bug", "improvement"],
                            label="Task Type",
                            value="feature",
                        )
                    prompt_btn = gr.Button("Generate Prompt", variant="primary")
                    prompt_output = gr.Textbox(label="Generated Prompt", lines=10)

                    prompt_btn.click(
                        fn=task_creation_prompt,
                        inputs=[project_name, task_type],
                        outputs=[prompt_output],
                    )

                with gr.Accordion("Data Analysis Prompt", open=False):
                    data_desc = gr.Textbox(
                        label="Data Description",
                        value="Sales data from Q4 2024",
                        lines=2,
                    )
                    analysis_goals_input = gr.Textbox(
                        label="Analysis Goals (one per line)",
                        value="Identify trends\nFind top performers\nDetect anomalies",
                        lines=4,
                    )
                    analysis_prompt_btn = gr.Button("Generate Prompt", variant="primary")
                    analysis_prompt_output = gr.Textbox(label="Generated Prompt", lines=15)

                    def run_analysis_prompt(desc, goals_text):
                        goals = [g.strip() for g in goals_text.split("\n") if g.strip()]
                        return data_analysis_prompt(desc, goals)

                    analysis_prompt_btn.click(
                        fn=run_analysis_prompt,
                        inputs=[data_desc, analysis_goals_input],
                        outputs=[analysis_prompt_output],
                    )

            # =================================================================
            # API Info Tab
            # =================================================================
            with gr.Tab("API & MCP Endpoints"):
                gr.Markdown("""
                ## API Endpoints

                This server exposes multiple interfaces for communication:

                ### MCP Endpoint (SSE Transport)
                ```
                URL: http://localhost:8080/mcp
                Transport: Server-Sent Events (SSE)
                ```

                Use this endpoint with any MCP-compatible client.

                ### REST API Endpoints

                | Endpoint | Method | Description |
                |----------|--------|-------------|
                | `/api/health` | GET | Health check |
                | `/api/tools` | GET | List available tools |
                | `/api/tools/{name}` | POST | Execute a tool |
                | `/api/resources` | GET | List available resources |
                | `/api/resources/{uri}` | GET | Read a resource |
                | `/api/prompts` | GET | List available prompts |

                ### Example: Call a tool via REST
                ```bash
                curl -X POST http://localhost:8080/api/tools/hello_world \\
                  -H "Content-Type: application/json" \\
                  -d '{"name": "Developer"}'
                ```

                ### Example: Read a resource via REST
                ```bash
                curl http://localhost:8080/api/resources/config%3A%2F%2Fserver%2Finfo
                ```
                """)

            # =================================================================
            # About Tab
            # =================================================================
            with gr.Tab("About"):
                gr.Markdown("""
                ## About MCP Showcase Server

                This server demonstrates best practices for building MCP (Model Context Protocol) servers
                that can be consumed by any MCP-compatible client.

                ### Features

                - **Tools**: 8 demonstration tools with various input types
                - **Resources**: 6 URI-based resources with dynamic parameters
                - **Prompts**: 3 reusable prompt templates
                - **Gradio UI**: Interactive web interface for testing
                - **REST API**: HTTP endpoints for programmatic access
                - **SSE Transport**: Real-time MCP communication

                ### Technology Stack

                - **FastMCP**: MCP server framework
                - **FastAPI**: REST API framework
                - **Gradio**: Web UI framework
                - **Pydantic**: Data validation

                ### Client Compatibility

                This server is designed to work with ANY MCP-compatible client:
                - Claude Desktop
                - Custom MCP clients
                - Generic HTTP/SSE clients

                No vendor lock-in - use standard protocols and libraries!

                ### Resources

                - [FastMCP Documentation](https://gofastmcp.com)
                - [MCP Specification](https://spec.modelcontextprotocol.io)
                - [Gradio Documentation](https://www.gradio.app/docs)
                """)

        return demo


# =============================================================================
# FASTAPI APPLICATION
# =============================================================================


def create_app() -> FastAPI:
    """Create the FastAPI application with MCP and Gradio mounted."""

    # Create MCP HTTP app
    mcp_app = mcp.http_app(path="/mcp")

    # Combined lifespan
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        async with mcp_app.lifespan(app):
            logger.info("MCP Showcase Server starting...")
            yield
            logger.info("MCP Showcase Server shutting down...")

    # Create main FastAPI app
    app = FastAPI(
        title="MCP Showcase Server",
        description="A comprehensive MCP server with Gradio interface and REST API",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount MCP
    app.mount("/mcp", mcp_app)

    # ==========================================================================
    # REST API Endpoints
    # ==========================================================================

    @app.get("/api/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "server": "MCP Showcase Server",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
        }

    @app.get("/api/tools")
    async def list_tools_endpoint():
        """List all available tools."""
        # Get tools from MCP server
        tools = []
        for tool_name in ["hello_world", "calculate", "create_task", "list_tasks",
                         "analyze_text", "convert_data", "generate_sample_data",
                         "increment_counter"]:
            tools.append({
                "name": tool_name,
                "endpoint": f"/api/tools/{tool_name}",
            })
        return {"tools": tools}

    @app.post("/api/tools/{tool_name}")
    async def execute_tool_endpoint(tool_name: str, params: Dict[str, Any] = None):
        """Execute a tool by name."""
        params = params or {}

        tool_map = {
            "hello_world": lambda p: hello_world(p.get("name", "World")),
            "calculate": lambda p: calculate(
                MathOperation(p.get("operation", "add")),
                p.get("a", 0),
                p.get("b"),
            ),
            "list_tasks": lambda p: list_tasks(
                Priority(p["priority_filter"]) if p.get("priority_filter") else None,
                p.get("limit", 10),
            ),
            "generate_sample_data": lambda p: generate_sample_data(
                p.get("data_type", "users"),
                p.get("count", 5),
                p.get("seed"),
            ),
            "increment_counter": lambda p: increment_counter(
                p.get("counter_name", "global_counter"),
                p.get("amount", 1),
            ),
        }

        # Async tools
        async_tool_map = {
            "create_task": lambda p: create_task(TaskInput(**p)),
            "analyze_text": lambda p: analyze_text(
                p.get("text", ""),
                p.get("include_sentiment", True),
                p.get("include_keywords", True),
            ),
        }

        if tool_name in tool_map:
            result = tool_map[tool_name](params)
            return {"result": result}
        elif tool_name in async_tool_map:
            result = await async_tool_map[tool_name](params)
            if hasattr(result, "model_dump"):
                result = result.model_dump()
            return {"result": result}
        else:
            return {"error": f"Tool '{tool_name}' not found"}

    @app.get("/api/resources")
    async def list_resources_endpoint():
        """List all available resources."""
        resources = [
            {"uri": "config://server/info", "description": "Server info"},
            {"uri": "config://server/stats", "description": "Server stats"},
            {"uri": "tasks://{task_id}", "description": "Task by ID"},
            {"uri": "data://samples/{data_type}", "description": "Sample data"},
            {"uri": "docs://api/tools", "description": "Tools documentation"},
            {"uri": "docs://api/resources", "description": "Resources documentation"},
        ]
        return {"resources": resources}

    @app.get("/api/resources/{uri:path}")
    async def read_resource_endpoint(uri: str):
        """Read a resource by URI."""
        from urllib.parse import unquote
        uri = unquote(uri)

        resource_map = {
            "config://server/info": get_server_info,
            "config://server/stats": get_server_stats,
            "docs://api/tools": get_tools_documentation,
            "docs://api/resources": get_resources_documentation,
        }

        if uri in resource_map:
            return {"uri": uri, "content": resource_map[uri]()}

        # Handle dynamic resources
        if uri.startswith("tasks://"):
            task_id = uri.replace("tasks://", "")
            return {"uri": uri, "content": get_task_resource(task_id)}

        if uri.startswith("data://samples/"):
            data_type = uri.replace("data://samples/", "")
            return {"uri": uri, "content": get_sample_data_resource(data_type)}

        return {"error": f"Resource '{uri}' not found"}

    @app.get("/api/prompts")
    async def list_prompts_endpoint():
        """List all available prompts."""
        prompts = [
            {
                "name": "task_creation_prompt",
                "description": "Generate a prompt for creating tasks",
                "parameters": ["project_name", "task_type"],
            },
            {
                "name": "data_analysis_prompt",
                "description": "Generate a prompt for data analysis",
                "parameters": ["data_description", "analysis_goals"],
            },
            {
                "name": "code_review_prompt",
                "description": "Generate a prompt for code review",
                "parameters": ["language", "focus_areas"],
            },
        ]
        return {"prompts": prompts}

    # Mount Gradio
    gradio_app = create_gradio_interface()
    app = gr.mount_gradio_app(app, gradio_app, path="/")

    return app


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

app = create_app()

if __name__ == "__main__":
    import uvicorn

    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║                    MCP Showcase Server                            ║
╠══════════════════════════════════════════════════════════════════╣
║  Gradio UI:    http://{SERVER_HOST}:{SERVER_PORT}/                          ║
║  MCP Endpoint: http://{SERVER_HOST}:{SERVER_PORT}/mcp                       ║
║  REST API:     http://{SERVER_HOST}:{SERVER_PORT}/api/                      ║
║  API Docs:     http://{SERVER_HOST}:{SERVER_PORT}/docs                      ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    uvicorn.run(
        "mcp_showcase_server:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=False,
        log_level=LOG_LEVEL.lower(),
    )
