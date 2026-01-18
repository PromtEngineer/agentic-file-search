# FsExplorer Architecture Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Component Architecture](#component-architecture)
3. [Core Modules](#core-modules)
4. [Workflow Engine](#workflow-engine)
5. [Agent Decision Loop](#agent-decision-loop)
6. [Document Processing Pipeline](#document-processing-pipeline)
7. [Three-Phase Exploration Strategy](#three-phase-exploration-strategy)
8. [Token Tracking & Cost Estimation](#token-tracking--cost-estimation)
9. [CLI Interface](#cli-interface)
10. [Data Flow](#data-flow)
11. [File Structure](#file-structure)
12. [Extension Points](#extension-points)

---

## System Overview

FsExplorer is an AI-powered filesystem exploration agent that answers questions about documents by intelligently navigating directories, parsing files, and synthesizing information with source citations.

```mermaid
graph TB
    subgraph "User Interface"
        CLI[CLI Interface<br/>typer + rich]
    end

    subgraph "Orchestration Layer"
        WF[Workflow Engine<br/>llama-index-workflows]
        EVT[Event System]
    end

    subgraph "Intelligence Layer"
        AGENT[FsExplorer Agent]
        LLM[Claude Sonnet (via ProxyPal)<br/>Structured JSON Output]
        PROMPT[System Prompt<br/>Three-Phase Strategy]
    end

    subgraph "Tools Layer"
        TOOLS[Tool Registry]
        SCAN[scan_folder<br/>Parallel Scan]
        PREVIEW[preview_file<br/>Quick Preview]
        PARSE[parse_file<br/>Deep Read]
        READ[read<br/>Text Files]
        GREP[grep<br/>Pattern Search]
        GLOB[glob<br/>File Search]
    end

    subgraph "Document Processing"
        DOCLING[Docling<br/>Document Converter]
        CACHE[Document Cache]
    end

    subgraph "Filesystem"
        FS[(Local Filesystem)]
        PDF[PDF Files]
        DOCX[DOCX Files]
        MD[Markdown Files]
        OTHER[Other Formats]
    end

    CLI --> WF
    WF --> EVT
    EVT --> AGENT
    AGENT --> LLM
    AGENT --> PROMPT
    AGENT --> TOOLS
    
    TOOLS --> SCAN
    TOOLS --> PREVIEW
    TOOLS --> PARSE
    TOOLS --> READ
    TOOLS --> GREP
    TOOLS --> GLOB
    
    SCAN --> DOCLING
    PREVIEW --> DOCLING
    PARSE --> DOCLING
    
    DOCLING --> CACHE
    CACHE --> FS
    
    FS --> PDF
    FS --> DOCX
    FS --> MD
    FS --> OTHER

    style LLM fill:#4285f4,color:#fff
    style DOCLING fill:#ff6b6b,color:#fff
    style CACHE fill:#ffd93d,color:#000
    style AGENT fill:#6bcb77,color:#fff
```

---

## Component Architecture

### High-Level Component Diagram

```mermaid
graph LR
    subgraph "Entry Point"
        MAIN[main.py<br/>CLI Entry]
    end

    subgraph "Workflow"
        WORKFLOW[workflow.py<br/>Event Orchestration]
    end

    subgraph "Agent"
        AGENT_MOD[agent.py<br/>AI Decision Making]
    end

    subgraph "Models"
        MODELS[models.py<br/>Pydantic Schemas]
    end

    subgraph "Filesystem"
        FS_MOD[fs.py<br/>File Operations]
    end

    MAIN --> WORKFLOW
    WORKFLOW --> AGENT_MOD
    AGENT_MOD --> MODELS
    AGENT_MOD --> FS_MOD
    WORKFLOW --> MODELS

    style MAIN fill:#e1f5fe
    style WORKFLOW fill:#f3e5f5
    style AGENT_MOD fill:#e8f5e9
    style MODELS fill:#fff3e0
    style FS_MOD fill:#fce4ec
```

### Module Dependencies

```mermaid
graph TD
    subgraph "fs_explorer package"
        INIT[__init__.py<br/>Public API Exports]
        MAIN[main.py]
        WORKFLOW[workflow.py]
        AGENT[agent.py]
        MODELS[models.py]
        FS[fs.py]
    end

    subgraph "External Dependencies"
        TYPER[typer<br/>CLI Framework]
        RICH[rich<br/>Terminal UI]
        WORKFLOWS[llama-index-workflows<br/>Event System]
        GENAI[openai<br/>ProxyPal API]
        PYDANTIC[pydantic<br/>Data Validation]
        DOCLING[docling<br/>Document Parsing]
    end

    INIT --> AGENT
    INIT --> WORKFLOW
    INIT --> MODELS
    
    MAIN --> TYPER
    MAIN --> RICH
    MAIN --> WORKFLOW
    
    WORKFLOW --> WORKFLOWS
    WORKFLOW --> AGENT
    WORKFLOW --> MODELS
    WORKFLOW --> FS
    
    AGENT --> GENAI
    AGENT --> MODELS
    AGENT --> FS
    
    MODELS --> PYDANTIC
    
    FS --> DOCLING

    style GENAI fill:#4285f4,color:#fff
    style DOCLING fill:#ff6b6b,color:#fff
```

---

## Core Modules

### models.py - Data Schemas

Defines the structured output format for the AI agent using Pydantic models.

```mermaid
classDiagram
    class Action {
        +action: ToolCallAction | GoDeeperAction | StopAction | AskHumanAction
        +reason: str
        +to_action_type() ActionType
    }

    class ToolCallAction {
        +tool_name: Tools
        +tool_input: list[ToolCallArg]
        +to_fn_args() dict
    }

    class ToolCallArg {
        +parameter_name: str
        +parameter_value: Any
    }

    class GoDeeperAction {
        +directory: str
    }

    class StopAction {
        +final_result: str
    }

    class AskHumanAction {
        +question: str
    }

    Action --> ToolCallAction
    Action --> GoDeeperAction
    Action --> StopAction
    Action --> AskHumanAction
    ToolCallAction --> ToolCallArg

    note for Action "Main container returned by LLM"
    note for ToolCallAction "Invokes filesystem tools"
    note for StopAction "Contains final answer with citations"
```

### agent.py - AI Agent

The core intelligence component that interacts with Google Gemini.

```mermaid
classDiagram
    class FsExplorerAgent {
        -_client: AsyncOpenAI
        -_chat_history: list[Content]
        +token_usage: TokenUsage
        +__init__(api_key: str)
        +configure_task(task: str) void
        +take_action() tuple[Action, ActionType]
        +call_tool(tool_name: Tools, tool_input: dict) void
        +reset() void
    }

    class TokenUsage {
        +prompt_tokens: int
        +completion_tokens: int
        +total_tokens: int
        +api_calls: int
        +tool_result_chars: int
        +documents_parsed: int
        +documents_scanned: int
        +add_api_call(prompt_tokens, completion_tokens) void
        +add_tool_result(result, tool_name) void
        +summary() str
    }

    class TOOLS {
        <<dictionary>>
        +read: read_file
        +grep: grep_file_content
        +glob: glob_paths
        +scan_folder: scan_folder
        +preview_file: preview_file
        +parse_file: parse_file
    }

    FsExplorerAgent --> TokenUsage
    FsExplorerAgent --> TOOLS
```

### fs.py - Filesystem Operations

All filesystem and document parsing utilities.

```mermaid
classDiagram
    class FilesystemModule {
        <<module>>
        +SUPPORTED_EXTENSIONS: frozenset
        +DEFAULT_PREVIEW_CHARS: int = 3000
        +DEFAULT_SCAN_PREVIEW_CHARS: int = 1500
        +DEFAULT_MAX_WORKERS: int = 4
    }

    class DocumentCache {
        <<singleton>>
        -_DOCUMENT_CACHE: dict[str, str]
        +clear_document_cache() void
        +_get_cached_or_parse(file_path) str
    }

    class DirectoryOps {
        <<functions>>
        +describe_dir_content(directory) str
        +glob_paths(directory, pattern) str
    }

    class FileOps {
        <<functions>>
        +read_file(file_path) str
        +grep_file_content(file_path, pattern) str
    }

    class DocumentOps {
        <<functions>>
        +preview_file(file_path, max_chars) str
        +parse_file(file_path) str
        +scan_folder(directory, max_workers, preview_chars) str
    }

    FilesystemModule --> DocumentCache
    FilesystemModule --> DirectoryOps
    FilesystemModule --> FileOps
    FilesystemModule --> DocumentOps
    DocumentOps --> DocumentCache
```

---

## Workflow Engine

The workflow engine uses an event-driven architecture based on `llama-index-workflows`.

### Workflow State Machine

```mermaid
stateDiagram-v2
    [*] --> StartExploration: InputEvent(task)
    
    StartExploration --> ToolCall: ToolCallEvent
    StartExploration --> GoDeeper: GoDeeperEvent
    StartExploration --> AskHuman: AskHumanEvent
    StartExploration --> End: StopAction
    
    ToolCall --> ToolCall: ToolCallEvent
    ToolCall --> GoDeeper: GoDeeperEvent
    ToolCall --> AskHuman: AskHumanEvent
    ToolCall --> End: StopAction
    
    GoDeeper --> ToolCall: ToolCallEvent
    GoDeeper --> GoDeeper: GoDeeperEvent
    GoDeeper --> AskHuman: AskHumanEvent
    GoDeeper --> End: StopAction
    
    AskHuman --> WaitForHuman: InputRequiredEvent
    WaitForHuman --> ProcessHumanResponse: HumanAnswerEvent
    ProcessHumanResponse --> ToolCall: ToolCallEvent
    ProcessHumanResponse --> GoDeeper: GoDeeperEvent
    ProcessHumanResponse --> AskHuman: AskHumanEvent
    ProcessHumanResponse --> End: StopAction
    
    End --> [*]: ExplorationEndEvent

    note right of StartExploration
        Initial task processing
        Describes current directory
        Asks LLM for first action
    end note

    note right of ToolCall
        Executes filesystem tool
        Adds result to chat history
        Asks LLM for next action
    end note

    note right of GoDeeper
        Updates current directory
        Describes new directory
        Asks LLM for next action
    end note
```

### Event Types

```mermaid
graph TB
    subgraph "Start Events"
        IE[InputEvent<br/>task: str]
    end

    subgraph "Intermediate Events"
        TCE[ToolCallEvent<br/>tool_name, tool_input, reason]
        GDE[GoDeeperEvent<br/>directory, reason]
        AHE[AskHumanEvent<br/>question, reason]
        HAE[HumanAnswerEvent<br/>response]
    end

    subgraph "End Events"
        EEE[ExplorationEndEvent<br/>final_result, error]
    end

    IE --> TCE
    IE --> GDE
    IE --> AHE
    IE --> EEE

    TCE --> TCE
    TCE --> GDE
    TCE --> AHE
    TCE --> EEE

    GDE --> TCE
    GDE --> GDE
    GDE --> AHE
    GDE --> EEE

    AHE --> HAE
    HAE --> TCE
    HAE --> GDE
    HAE --> AHE
    HAE --> EEE

    style IE fill:#4caf50,color:#fff
    style EEE fill:#f44336,color:#fff
    style TCE fill:#2196f3,color:#fff
    style GDE fill:#9c27b0,color:#fff
    style AHE fill:#ff9800,color:#fff
```

### Workflow Steps

```mermaid
sequenceDiagram
    participant CLI as CLI (main.py)
    participant WF as Workflow
    participant Agent as FsExplorerAgent
    participant LLM as ProxyPal API
    participant Tools as Tool Registry
    participant FS as Filesystem

    CLI->>WF: InputEvent(task)
    
    WF->>Agent: configure_task(initial_prompt)
    Agent->>LLM: generate_content(chat_history)
    LLM-->>Agent: Action JSON
    
    alt ToolCallAction
        Agent->>Tools: call_tool(name, args)
        Tools->>FS: execute operation
        FS-->>Tools: result
        Tools-->>Agent: tool result
        Agent->>Agent: add to chat_history
        WF-->>CLI: ToolCallEvent (stream)
        WF->>Agent: configure_task("next action?")
        Note over WF,Agent: Loop continues
    else GoDeeperAction
        WF->>WF: update current_directory
        WF-->>CLI: GoDeeperEvent (stream)
        WF->>Agent: configure_task("next action?")
        Note over WF,Agent: Loop continues
    else AskHumanAction
        WF-->>CLI: AskHumanEvent (stream)
        CLI->>CLI: Wait for user input
        CLI->>WF: HumanAnswerEvent(response)
        WF->>Agent: configure_task(response)
        Note over WF,Agent: Loop continues
    else StopAction
        WF-->>CLI: ExplorationEndEvent(final_result)
    end
```

---

## Agent Decision Loop

### Single Decision Cycle

```mermaid
flowchart TB
    subgraph "Agent.take_action()"
        START([Start]) --> SEND[Send chat_history to Gemini]
        SEND --> RECEIVE[Receive JSON response]
        RECEIVE --> TRACK[Track token usage]
        TRACK --> PARSE[Parse Action from JSON]
        PARSE --> CHECK{Action Type?}
        
        CHECK -->|toolcall| EXEC[Execute Tool]
        EXEC --> RESULT[Get tool result]
        RESULT --> ADD[Add result to chat_history]
        ADD --> RETURN1[Return Action, ActionType]
        
        CHECK -->|godeeper| RETURN2[Return Action, ActionType]
        CHECK -->|askhuman| RETURN3[Return Action, ActionType]
        CHECK -->|stop| RETURN4[Return Action, ActionType]
        
        RETURN1 --> END([End])
        RETURN2 --> END
        RETURN3 --> END
        RETURN4 --> END
    end

    style START fill:#4caf50,color:#fff
    style END fill:#f44336,color:#fff
    style CHECK fill:#ff9800,color:#000
```

### Chat History Evolution

```mermaid
sequenceDiagram
    participant User
    participant Agent
    participant LLM

    Note over Agent: chat_history = []

    User->>Agent: configure_task("Initial prompt + directory listing")
    Note over Agent: chat_history = [user: initial_prompt]

    Agent->>LLM: generate_content(chat_history)
    LLM-->>Agent: {action: scan_folder, reason: "..."}
    Note over Agent: chat_history = [user: initial_prompt, model: action1]

    Agent->>Agent: Execute scan_folder, add result
    Note over Agent: chat_history = [user: initial_prompt, model: action1, user: tool_result1]

    User->>Agent: configure_task("What's next?")
    Note over Agent: chat_history = [..., user: "What's next?"]

    Agent->>LLM: generate_content(chat_history)
    LLM-->>Agent: {action: parse_file, reason: "..."}
    Note over Agent: chat_history = [..., model: action2]

    Note over Agent: Pattern continues until StopAction
```

---

## Document Processing Pipeline

### Docling Integration

```mermaid
flowchart LR
    subgraph "Input Formats"
        PDF[PDF]
        DOCX[DOCX]
        PPTX[PPTX]
        XLSX[XLSX]
        HTML[HTML]
        MD[Markdown]
    end

    subgraph "Docling"
        DC[DocumentConverter]
        DETECT[Format Detection]
        PIPELINE[Processing Pipeline]
        EXPORT[Markdown Export]
    end

    subgraph "Output"
        MARKDOWN[Markdown Text]
    end

    PDF --> DC
    DOCX --> DC
    PPTX --> DC
    XLSX --> DC
    HTML --> DC
    MD --> DC

    DC --> DETECT
    DETECT --> PIPELINE
    PIPELINE --> EXPORT
    EXPORT --> MARKDOWN

    style DC fill:#ff6b6b,color:#fff
```

### Caching Strategy

```mermaid
flowchart TB
    subgraph "Cache Key Generation"
        PATH[file_path] --> ABS[os.path.abspath]
        ABS --> MTIME[os.path.getmtime]
        MTIME --> KEY["cache_key = f'{abs_path}:{mtime}'"]
    end

    subgraph "Cache Lookup"
        KEY --> CHECK{Key in cache?}
        CHECK -->|Yes| HIT[Return cached content]
        CHECK -->|No| MISS[Parse with Docling]
        MISS --> STORE[Store in cache]
        STORE --> RETURN[Return content]
    end

    subgraph "_DOCUMENT_CACHE"
        CACHE[(dict: str → str)]
    end

    HIT --> CACHE
    STORE --> CACHE

    style CACHE fill:#ffd93d,color:#000
```

### Parallel Document Scanning

```mermaid
flowchart TB
    subgraph "scan_folder(directory)"
        START([Start]) --> LIST[List directory files]
        LIST --> FILTER[Filter by SUPPORTED_EXTENSIONS]
        FILTER --> POOL[Create ThreadPoolExecutor<br/>max_workers=4]
        
        subgraph "Parallel Processing"
            POOL --> T1[Thread 1<br/>_preview_single_file]
            POOL --> T2[Thread 2<br/>_preview_single_file]
            POOL --> T3[Thread 3<br/>_preview_single_file]
            POOL --> T4[Thread 4<br/>_preview_single_file]
        end

        T1 --> COLLECT[Collect Results]
        T2 --> COLLECT
        T3 --> COLLECT
        T4 --> COLLECT

        COLLECT --> SORT[Sort by filename]
        SORT --> FORMAT[Format output report]
        FORMAT --> END([Return summary])
    end

    style START fill:#4caf50,color:#fff
    style END fill:#4caf50,color:#fff
    style POOL fill:#2196f3,color:#fff
```

---

## Three-Phase Exploration Strategy

### Phase Overview

```mermaid
flowchart TB
    subgraph "PHASE 1: Parallel Scan"
        P1_START([User Query]) --> P1_SCAN[scan_folder]
        P1_SCAN --> P1_PREVIEW[Get previews of ALL documents]
        P1_PREVIEW --> P1_CATEGORIZE[Categorize documents]
        
        P1_CATEGORIZE --> REL[RELEVANT<br/>Directly related]
        P1_CATEGORIZE --> MAYBE[MAYBE<br/>Potentially useful]
        P1_CATEGORIZE --> SKIP[SKIP<br/>Not relevant]
    end

    subgraph "PHASE 2: Deep Dive"
        REL --> P2_PARSE[parse_file on RELEVANT docs]
        MAYBE -.->|If needed| P2_PARSE
        P2_PARSE --> P2_EXTRACT[Extract key information]
        P2_EXTRACT --> P2_CROSS{Cross-references<br/>found?}
    end

    subgraph "PHASE 3: Backtracking"
        P2_CROSS -->|Yes| P3_CHECK{Referenced doc<br/>was SKIPPED?}
        P3_CHECK -->|Yes| P3_BACKTRACK[Go back and parse<br/>referenced document]
        P3_BACKTRACK --> P2_EXTRACT
        P3_CHECK -->|No| P3_CONTINUE[Continue analysis]
        P2_CROSS -->|No| P3_CONTINUE
    end

    subgraph "Final Answer"
        P3_CONTINUE --> ANSWER[Generate answer<br/>with citations]
        ANSWER --> SOURCES[List sources consulted]
        SOURCES --> END([Return to user])
    end

    style P1_START fill:#4caf50,color:#fff
    style END fill:#4caf50,color:#fff
    style REL fill:#4caf50,color:#fff
    style MAYBE fill:#ff9800,color:#000
    style SKIP fill:#9e9e9e,color:#fff
    style P3_BACKTRACK fill:#e91e63,color:#fff
```

### Cross-Reference Detection

```mermaid
flowchart LR
    subgraph "Document Content"
        DOC[Parsed Document]
    end

    subgraph "Pattern Matching"
        DOC --> P1["'See Exhibit A/B/C...'"]
        DOC --> P2["'As stated in [Document]...'"]
        DOC --> P3["'Refer to [filename]...'"]
        DOC --> P4["'per Document: [name]'"]
        DOC --> P5["'[Doc #XX]'"]
    end

    subgraph "Action"
        P1 --> FOUND[Cross-reference found]
        P2 --> FOUND
        P3 --> FOUND
        P4 --> FOUND
        P5 --> FOUND
        
        FOUND --> CHECK{Was referenced<br/>doc SKIPPED?}
        CHECK -->|Yes| BACKTRACK[Backtrack and parse]
        CHECK -->|No| CONTINUE[Continue]
    end

    style BACKTRACK fill:#e91e63,color:#fff
```

---

## Token Tracking & Cost Estimation

### TokenUsage Class

```mermaid
flowchart TB
    subgraph "Input Tracking"
        API[API Call] --> PROMPT[prompt_token_count]
        API --> COMPLETION[candidates_token_count]
        PROMPT --> ADD_API[add_api_call]
        COMPLETION --> ADD_API
    end

    subgraph "Tool Tracking"
        TOOL[Tool Execution] --> RESULT[result string]
        RESULT --> ADD_TOOL[add_tool_result]
        ADD_TOOL --> CHARS[tool_result_chars += len]
        ADD_TOOL --> PARSED{tool_name?}
        PARSED -->|parse_file| INC_PARSED[documents_parsed++]
        PARSED -->|preview_file| INC_PARSED
        PARSED -->|scan_folder| INC_SCANNED[documents_scanned += count]
    end

    subgraph "Cost Calculation"
        ADD_API --> TOTALS[Update totals]
        TOTALS --> CALC[_calculate_cost]
        CALC --> INPUT_COST["input_cost = prompt_tokens × $3.00/1M"]
        CALC --> OUTPUT_COST["output_cost = completion_tokens × $15.00/1M"]
        INPUT_COST --> TOTAL_COST[total_cost]
        OUTPUT_COST --> TOTAL_COST
    end

    subgraph "Summary Output"
        TOTAL_COST --> SUMMARY[summary]
        CHARS --> SUMMARY
        INC_PARSED --> SUMMARY
        INC_SCANNED --> SUMMARY
    end
```

### Cost Estimation Formula

```mermaid
graph LR
    subgraph "Gemini 2.0 Flash Pricing"
        INPUT["Input: $3.00 / 1M tokens"]
        OUTPUT["Output: $15.00 / 1M tokens"]
    end

    subgraph "Calculation"
        PROMPT[prompt_tokens] --> DIV1[÷ 1,000,000]
        DIV1 --> MULT1[× $3.00]
        MULT1 --> INPUT_COST[Input Cost]

        COMP[completion_tokens] --> DIV2[÷ 1,000,000]
        DIV2 --> MULT2[× $15.00]
        MULT2 --> OUTPUT_COST[Output Cost]

        INPUT_COST --> SUM[+]
        OUTPUT_COST --> SUM
        SUM --> TOTAL[Total Estimated Cost]
    end

    style TOTAL fill:#4caf50,color:#fff
```

---

## CLI Interface

### Output Formatting

```mermaid
flowchart TB
    subgraph "Event Handling"
        EVENT{Event Type}
        
        EVENT -->|ToolCallEvent| TOOL_PANEL[format_tool_panel]
        EVENT -->|GoDeeperEvent| NAV_PANEL[format_navigation_panel]
        EVENT -->|AskHumanEvent| HUMAN_PANEL[Human Input Panel]
        EVENT -->|ExplorationEndEvent| FINAL_PANEL[Final Answer Panel]
    end

    subgraph "Tool Panel Components"
        TOOL_PANEL --> ICON[Tool Icon 📂📖👁️🔍]
        TOOL_PANEL --> STEP[Step Number]
        TOOL_PANEL --> PHASE[Phase Label]
        TOOL_PANEL --> TARGET[Target File/Directory]
        TOOL_PANEL --> REASON[Agent's Reasoning]
    end

    subgraph "Final Panel Components"
        FINAL_PANEL --> ANSWER[Answer with Citations]
        FINAL_PANEL --> SOURCES[Sources Consulted]
    end

    subgraph "Summary Panel"
        SUMMARY[Workflow Summary]
        SUMMARY --> STEPS[Total Steps]
        SUMMARY --> CALLS[API Calls]
        SUMMARY --> DOCS[Documents Scanned/Parsed]
        SUMMARY --> TOKENS[Token Usage]
        SUMMARY --> COST[Estimated Cost]
    end

    FINAL_PANEL --> SUMMARY
```

### Visual Elements

```mermaid
graph TB
    subgraph "Panel Styles"
        TOOL["📂 Tool Call<br/>border: yellow"]
        NAV["📁 Navigation<br/>border: magenta"]
        HUMAN["❓ Human Input<br/>border: red"]
        FINAL["✅ Final Answer<br/>border: green"]
        SUMMARY["📊 Summary<br/>border: blue"]
    end

    subgraph "Tool Icons"
        I1["📂 scan_folder"]
        I2["👁️ preview_file"]
        I3["📖 parse_file"]
        I4["📄 read"]
        I5["🔍 grep"]
        I6["🔎 glob"]
    end

    subgraph "Phase Labels"
        PH1["Phase 1: Parallel Document Scan"]
        PH2["Phase 2: Deep Dive"]
        PH3["Phase 1/2: Quick Preview"]
    end

    style TOOL fill:#ffeb3b,color:#000
    style NAV fill:#e1bee7,color:#000
    style HUMAN fill:#ffcdd2,color:#000
    style FINAL fill:#c8e6c9,color:#000
    style SUMMARY fill:#bbdefb,color:#000
```

---

## Data Flow

### Complete Request Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI as main.py
    participant WF as Workflow
    participant Agent as FsExplorerAgent
    participant LLM as ProxyPal API
    participant Tools as Tool Registry
    participant Docling
    participant Cache
    participant FS as Filesystem

    User->>CLI: uv run explore --task "..."
    CLI->>CLI: print_workflow_header()
    CLI->>WF: workflow.run(InputEvent)

    loop Until StopAction
        WF->>Agent: configure_task()
        Agent->>LLM: generate_content()
        LLM-->>Agent: Action JSON
        Agent->>Agent: Track tokens

        alt ToolCallAction
            Agent->>Tools: TOOLS[name](**args)
            
            alt Document Tool
                Tools->>Cache: Check cache
                alt Cache Hit
                    Cache-->>Tools: Cached content
                else Cache Miss
                    Cache->>Docling: Convert document
                    Docling->>FS: Read file
                    FS-->>Docling: Raw bytes
                    Docling-->>Cache: Markdown content
                    Cache-->>Tools: Content
                end
            else Filesystem Tool
                Tools->>FS: Execute operation
                FS-->>Tools: Result
            end
            
            Tools-->>Agent: Tool result
            Agent->>Agent: Track tool metrics
            WF-->>CLI: ToolCallEvent
            CLI->>CLI: format_tool_panel()
        else GoDeeperAction
            WF->>WF: Update directory state
            WF-->>CLI: GoDeeperEvent
            CLI->>CLI: format_navigation_panel()
        else AskHumanAction
            WF-->>CLI: AskHumanEvent
            CLI->>User: Display question
            User->>CLI: Enter response
            CLI->>WF: HumanAnswerEvent
        else StopAction
            WF-->>CLI: ExplorationEndEvent
        end
    end

    CLI->>CLI: Display final answer
    CLI->>CLI: print_workflow_summary()
    CLI-->>User: Complete output
```

---

## File Structure

```
fs-explorer/
├── src/
│   └── fs_explorer/
│       ├── __init__.py      # Public API exports
│       ├── main.py          # CLI entry point (typer)
│       ├── workflow.py      # Event-driven workflow orchestration
│       ├── agent.py         # AI agent + Gemini integration
│       ├── models.py        # Pydantic action schemas
│       └── fs.py            # Filesystem + Docling operations
├── tests/
│   ├── conftest.py          # Test fixtures and mocks
│   ├── test_agent.py        # Agent unit tests
│   ├── test_fs.py           # Filesystem function tests
│   ├── test_models.py       # Model tests
│   ├── test_e2e.py          # End-to-end integration tests
│   └── testfiles/           # Test data
├── data/
│   ├── large_acquisition/   # Sample PDF documents
│   └── test_acquisition/    # Test document set
├── scripts/
│   ├── generate_test_docs.py
│   └── generate_large_docs.py
├── pyproject.toml           # Project configuration
├── Makefile                 # Development commands
├── README.md                # User documentation
└── ARCHITECTURE.md          # This file
```

---

## Extension Points

### Adding New Tools

```mermaid
flowchart LR
    subgraph "Step 1: Define Function"
        FUNC[def new_tool(args) -> str]
    end

    subgraph "Step 2: Register Tool"
        TOOLS["TOOLS dict in agent.py"]
        FUNC --> TOOLS
    end

    subgraph "Step 3: Update Types"
        TYPES["Tools TypeAlias in models.py"]
        TOOLS --> TYPES
    end

    subgraph "Step 4: Update Prompt"
        PROMPT["SYSTEM_PROMPT in agent.py"]
        TYPES --> PROMPT
    end

    style FUNC fill:#e3f2fd
    style TOOLS fill:#f3e5f5
    style TYPES fill:#fff3e0
    style PROMPT fill:#e8f5e9
```

### Adding New Document Formats

```mermaid
flowchart LR
    subgraph "Docling Supported"
        PDF[PDF] --> DOCLING[Docling]
        DOCX[DOCX] --> DOCLING
        PPTX[PPTX] --> DOCLING
        XLSX[XLSX] --> DOCLING
        HTML[HTML] --> DOCLING
        MD[Markdown] --> DOCLING
    end

    subgraph "To Add New Format"
        NEW[New Format] --> CHECK{Docling<br/>supports?}
        CHECK -->|Yes| ADD["Add to SUPPORTED_EXTENSIONS"]
        CHECK -->|No| CUSTOM["Create custom handler<br/>in fs.py"]
    end

    DOCLING --> OUTPUT[Markdown]
    ADD --> OUTPUT
    CUSTOM --> OUTPUT
```

### Customizing the System Prompt

The system prompt in `agent.py` can be modified to:

1. **Add new exploration strategies**
2. **Change citation format**
3. **Adjust categorization criteria**
4. **Add domain-specific instructions**

```python
SYSTEM_PROMPT = """
# Customize this prompt to change agent behavior

## Your custom instructions here
...
"""
```

---

## Performance Characteristics

| Metric | Typical Value | Notes |
|--------|---------------|-------|
| Parallel scan threads | 4 | Configurable via `DEFAULT_MAX_WORKERS` |
| Preview size | 1500 chars | ~1 page of content |
| Full preview size | 3000 chars | ~2-3 pages |
| Document cache | In-memory | Keyed by path + mtime |
| Workflow timeout | 300 seconds | 5 minutes for complex queries |
| API model | claude-sonnet-4-20250514 | Via ProxyPal |

---

## Security Considerations

1. **API Key**: Stored in environment variable `PROXYPAL_API_KEY`
2. **Local Processing**: Documents parsed locally via Docling (no cloud upload)
3. **Filesystem Access**: Limited to current working directory
4. **No Persistent Storage**: Document cache is in-memory only

---

*Last updated: 2026-01-18*
