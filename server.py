#!/usr/bin/env python3
"""
MCP Server for Command Execution Tools

This server provides tools for executing commands and managing project directories.
"""

import asyncio
import subprocess
import os
import sys
from pathlib import Path
from typing import Any, Sequence

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio


# Global configuration
WORKING_DIRECTORY = r"C:\Users\User\Desktop\LineBot"
ALLOWED_COMMANDS = [
    "python",
    "pip", 
    "git",
    "dir",
    "ls", 
    "cd",
    "mkdir",
    "copy",
    "move",
    "del",
    "type",
    "cat"
]

server = Server("command-execution-server")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available command execution tools."""
    return [
        types.Tool(
            name="execute_command",
            description="Execute a command in the specified working directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command to execute"
                    },
                    "working_directory": {
                        "type": "string", 
                        "description": f"Working directory (default: {WORKING_DIRECTORY})",
                        "default": WORKING_DIRECTORY
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Command timeout in seconds (default: 30)",
                        "default": 30
                    }
                },
                "required": ["command"]
            }
        ),
        types.Tool(
            name="run_python_script",
            description="Run a Python script in the LineBot project directory",
            inputSchema={
                "type": "object", 
                "properties": {
                    "script_name": {
                        "type": "string",
                        "description": "Name of the Python script to run (e.g., 'test_architecture.py')"
                    },
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Command line arguments for the script",
                        "default": []
                    }
                },
                "required": ["script_name"]
            }
        ),
        types.Tool(
            name="change_directory",
            description="Change the working directory for subsequent commands",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "New working directory path"
                    }
                },
                "required": ["path"]
            }
        ),
        types.Tool(
            name="get_directory_info",
            description="Get information about the current working directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path to inspect (default: current working directory)",
                        "default": WORKING_DIRECTORY
                    }
                }
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    """Handle tool execution requests."""
    
    if name == "execute_command":
        return await execute_command(arguments)
    elif name == "run_python_script":
        return await run_python_script(arguments)
    elif name == "change_directory":
        return await change_directory(arguments)
    elif name == "get_directory_info":
        return await get_directory_info(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def execute_command(arguments: dict[str, Any]) -> list[types.TextContent]:
    """Execute a system command."""
    command = arguments["command"]
    working_dir = arguments.get("working_directory", WORKING_DIRECTORY)
    timeout = arguments.get("timeout", 30)
    
    # Security check - only allow whitelisted commands
    command_parts = command.split()
    if command_parts and command_parts[0] not in ALLOWED_COMMANDS:
        return [types.TextContent(
            type="text",
            text=f"❌ Command '{command_parts[0]}' is not allowed. Allowed commands: {', '.join(ALLOWED_COMMANDS)}"
        )]
    
    try:
        # Ensure working directory exists
        Path(working_dir).mkdir(parents=True, exist_ok=True)
        
        # Execute command
        result = subprocess.run(
            command,
            shell=True,
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='replace'
        )
        
        output = []
        if result.stdout:
            output.append(f"📤 Output:\n{result.stdout}")
        if result.stderr:
            output.append(f"⚠️ Errors:\n{result.stderr}")
        
        output.append(f"🔄 Exit code: {result.returncode}")
        output.append(f"📁 Working directory: {working_dir}")
        
        return [types.TextContent(
            type="text", 
            text="\n\n".join(output) if output else "✅ Command completed successfully (no output)"
        )]
        
    except subprocess.TimeoutExpired:
        return [types.TextContent(
            type="text",
            text=f"⏰ Command timed out after {timeout} seconds"
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Error executing command: {str(e)}"
        )]


async def run_python_script(arguments: dict[str, Any]) -> list[types.TextContent]:
    """Run a Python script in the LineBot directory."""
    script_name = arguments["script_name"]
    args = arguments.get("args", [])
    
    # Build the full command
    command_parts = ["python", script_name] + args
    command = " ".join(command_parts)
    
    # Use the execute_command function
    return await execute_command({
        "command": command,
        "working_directory": WORKING_DIRECTORY,
        "timeout": 60  # Python scripts might take longer
    })


async def change_directory(arguments: dict[str, Any]) -> list[types.TextContent]:
    """Change the working directory."""
    global WORKING_DIRECTORY
    
    new_path = arguments["path"]
    
    try:
        # Resolve the path
        resolved_path = str(Path(new_path).resolve())
        
        # Check if directory exists
        if not Path(resolved_path).exists():
            return [types.TextContent(
                type="text",
                text=f"❌ Directory does not exist: {resolved_path}"
            )]
        
        if not Path(resolved_path).is_dir():
            return [types.TextContent(
                type="text", 
                text=f"❌ Path is not a directory: {resolved_path}"
            )]
        
        # Update working directory
        WORKING_DIRECTORY = resolved_path
        
        return [types.TextContent(
            type="text",
            text=f"✅ Changed working directory to: {WORKING_DIRECTORY}"
        )]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Error changing directory: {str(e)}"
        )]


async def get_directory_info(arguments: dict[str, Any]) -> list[types.TextContent]:
    """Get information about a directory."""
    path = arguments.get("path", WORKING_DIRECTORY)
    
    try:
        path_obj = Path(path)
        
        if not path_obj.exists():
            return [types.TextContent(
                type="text",
                text=f"❌ Directory does not exist: {path}"
            )]
        
        # Get directory contents
        contents = []
        for item in sorted(path_obj.iterdir()):
            if item.is_dir():
                contents.append(f"📁 {item.name}/")
            else:
                size = item.stat().st_size
                contents.append(f"📄 {item.name} ({size} bytes)")
        
        info = [
            f"📁 Current directory: {path}",
            f"📊 Total items: {len(contents)}",
            "",
            "📋 Contents:"
        ] + contents
        
        return [types.TextContent(
            type="text",
            text="\n".join(info)
        )]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Error getting directory info: {str(e)}"
        )]


async def main():
    """Main entry point for the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="command-execution-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
