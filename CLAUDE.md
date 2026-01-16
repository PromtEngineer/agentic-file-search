# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FsExplorer is an AI-powered document search agent that navigates filesystems like a human would—scanning, reasoning, and following cross-references. It uses a three-phase strategy (parallel scan → deep dive → backtrack) rather than traditional RAG embeddings.

## Development Commands

```bash
# Install dependencies
uv pip install -e ".[dev]"

# Run all tests
uv run pytest tests

# Run a single test file
uv run pytest tests/test_fs.py

# Run a specific test
uv run pytest tests/test_fs.py::test_function_name -v

# Lint (runs pre-commit hooks)
uv run pre-commit run -a

# Format code
uv run ruff format

# Check formatting without modifying
uv run ruff format --check

# Type check
uv run ty check src/fs_explorer/

# Build package
uv build
```

## Running the Application

```bash
# CLI query
uv run explore --task "What is the purchase price in data/test_acquisition/?"

# Web UI server
uv run uvicorn fs_explorer.server:app --host 127.0.0.1 --port 8000
```

## Architecture

The system uses an event-driven workflow with LlamaIndex Workflows:

- **workflow.py**: Event orchestration - handles `InputEvent`, `ToolCallEvent`, `GoDeeperEvent`, `AskHumanEvent`, `ExplorationEndEvent`
- **agent.py**: Claude Opus client (via ProxyPal) with structured JSON output, token tracking, and the `SYSTEM_PROMPT` that defines the three-phase exploration strategy
- **models.py**: Pydantic schemas for agent actions (`ToolCallAction`, `GoDeeperAction`, `StopAction`, `AskHumanAction`)
- **fs.py**: File operations with Docling for document parsing. Includes in-memory document cache keyed by `path:mtime`
- **main.py**: CLI entry point using Typer + Rich
- **server.py**: FastAPI + WebSocket server for the web UI

### Agent Tools

Six tools defined in `agent.py` TOOLS dict: `scan_folder`, `preview_file`, `parse_file`, `read`, `grep`, `glob`

### Three-Phase Strategy

1. **Parallel Scan**: `scan_folder` previews all documents concurrently (4 threads)
2. **Deep Dive**: `parse_file` for full extraction on relevant documents
3. **Backtrack**: Follow cross-references to previously skipped documents

### Document Processing

Docling handles PDF, DOCX, PPTX, XLSX, HTML, Markdown → Markdown conversion. Supported extensions defined in `fs.py` `SUPPORTED_EXTENSIONS`.

## Configuration

Requires `PROXYPAL_API_KEY` environment variable (set in `.env` file). Uses Claude Opus via ProxyPal.

## Test Data

- `data/test_acquisition/` - 10 interconnected legal documents
- `data/large_acquisition/` - 25 documents with cross-references
- `data/demo_project/` - 6 IT project documents for DELL Romandie Day 2026 demo

## DELL Romandie Day 2026 Presentation

Materials in `presentation/material/`:
- `MS_Presentation-DELL Romandie Day 2026_v1.pdf` - Main presentation (needs new slides for the demo)
- `YT-This is the new RAG-Transcritption.txt` - YouTube transcript from original demo author explaining the agentic approach

Demo query: "What are all the dependencies blocking Phase 2 launch?"

Slide content outline in `presentation/SLIDE_CONTENT.md`
