"""
FastAPI server for FsExplorer web UI.

Provides a WebSocket endpoint for real-time workflow streaming
and serves the single-page HTML interface.
"""

import json
import asyncio
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .workflow import (
    workflow,
    InputEvent,
    ToolCallEvent,
    GoDeeperEvent,
    AskHumanEvent,
    HumanAnswerEvent,
    ExplorationEndEvent,
    get_agent,
    reset_agent,
)

app = FastAPI(title="FsExplorer", description="AI-powered filesystem exploration")


class TaskRequest(BaseModel):
    """Request model for task submission."""
    task: str
    folder: str = "."


@app.get("/", response_class=HTMLResponse)
async def get_ui():
    """Serve the main UI HTML file."""
    html_path = Path(__file__).parent / "ui.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding='utf-8'), status_code=200)
    return HTMLResponse(content="<h1>UI not found</h1>", status_code=404)


@app.get("/api/folders")
async def list_folders(path: str = "."):
    """
    List folders in the given path.
    Returns list of folder names and current path info.
    """
    try:
        base_path = Path(path).resolve()
        if not base_path.exists():
            return JSONResponse({"error": "Path not found"}, status_code=404)
        if not base_path.is_dir():
            return JSONResponse({"error": "Not a directory"}, status_code=400)
        
        # Get folders (non-hidden)
        folders = sorted([
            f.name for f in base_path.iterdir()
            if f.is_dir() and not f.name.startswith('.')
        ])
        
        # Get parent path (if not at root)
        parent = str(base_path.parent) if base_path != base_path.parent else None
        
        return {
            "current": str(base_path),
            "parent": parent,
            "folders": folders,
            "files_count": len([f for f in base_path.iterdir() if f.is_file()]),
        }
    except PermissionError:
        return JSONResponse({"error": "Permission denied"}, status_code=403)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.websocket("/ws/explore")
async def websocket_explore(websocket: WebSocket):
    """
    WebSocket endpoint for real-time exploration streaming.
    
    Protocol:
    1. Client sends: {"task": "user question"}
    2. Server streams events: {"type": "...", "data": {...}}
    3. Final event: {"type": "complete", "data": {...}}
    """
    await websocket.accept()
    
    try:
        # Receive the task
        data = await websocket.receive_json()
        task = data.get("task", "")
        folder = data.get("folder", ".")
        
        if not task:
            await websocket.send_json({
                "type": "error",
                "data": {"message": "No task provided"}
            })
            return
        
        # Validate folder
        folder_path = Path(folder).resolve()
        if not folder_path.exists() or not folder_path.is_dir():
            await websocket.send_json({
                "type": "error",
                "data": {"message": f"Invalid folder: {folder}"}
            })
            return
        
        # Change to target folder
        original_cwd = os.getcwd()
        os.chdir(folder_path)
        
        # Reset agent for fresh state
        reset_agent()
        
        # Send start event
        await websocket.send_json({
            "type": "start",
            "data": {"task": task, "folder": str(folder_path)}
        })
        
        # Run the workflow
        step_number = 0
        handler = workflow.run(start_event=InputEvent(task=task))
        
        async for event in handler.stream_events():
            if isinstance(event, ToolCallEvent):
                step_number += 1
                await websocket.send_json({
                    "type": "tool_call",
                    "data": {
                        "step": step_number,
                        "tool_name": event.tool_name,
                        "tool_input": event.tool_input,
                        "reason": event.reason,
                    }
                })
                
            elif isinstance(event, GoDeeperEvent):
                step_number += 1
                await websocket.send_json({
                    "type": "go_deeper",
                    "data": {
                        "step": step_number,
                        "directory": event.directory,
                        "reason": event.reason,
                    }
                })
                
            elif isinstance(event, AskHumanEvent):
                step_number += 1
                await websocket.send_json({
                    "type": "ask_human",
                    "data": {
                        "step": step_number,
                        "question": event.question,
                        "reason": event.reason,
                    }
                })
                
                # Wait for human response
                response_data = await websocket.receive_json()
                if response_data.get("type") == "human_response":
                    handler.ctx.send_event(
                        HumanAnswerEvent(response=response_data.get("response", ""))
                    )
        
        # Get final result
        result = await handler

        # Get token usage
        agent = get_agent()
        usage = agent.token_usage
        input_cost, output_cost, total_cost = usage._calculate_cost()

        await websocket.send_json({
            "type": "complete",
            "data": {
                "final_result": result.final_result,
                "error": result.error,
                "stats": {
                    "steps": step_number,
                    "api_calls": usage.api_calls,
                    "documents_scanned": usage.documents_scanned,
                    "documents_parsed": usage.documents_parsed,
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens,
                    "tool_result_chars": usage.tool_result_chars,
                    "estimated_cost": round(total_cost, 6),
                }
            }
        })
        
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "data": {"message": str(e)}
        })
    finally:
        # Restore original working directory
        if 'original_cwd' in locals():
            os.chdir(original_cwd)


def run_server(host: str = "127.0.0.1", port: int = 8000):
    """Run the FastAPI server."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()

