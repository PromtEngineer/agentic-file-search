# Presentation Preparation Notes

> Living document capturing our discussion and planning for the Agentic AI demo.

## Presentation Context

**Topic:** Agentic AI
**Audience:** Heterogeneous, mainly IT-related, but not AI-literate
**Goal:** Show the evolution from workflow automation to autonomous AI agents

---

## Presentation Structure

### Part 1: n8n Workflow (Simple, Visual)

- Quick demo of n8n workflow
- Triggers actions in email and calendar from Telegram
- Visual flow that's easy to follow
- Shows: Parent Agent with Children Sub-Workflows (Email Agent, Calendar Agent, Contact Agent, Content Creator Agent)
- **Purpose:** Establish baseline understanding of "agents" as automated workflows

### Part 2: Agentic File Search (Advanced, Autonomous)

- Transition message: "But what if the agent could decide its own path?"
- Demo the FsExplorer with web UI
- Show real-time reasoning and tool selection
- **Purpose:** Demonstrate genuine autonomous behavior

---

## Why This App Demonstrates "True" Agentic AI

1. **Visible reasoning** - Web UI shows each step with the agent's explanation
   - "I'm scanning this folder because..."
   - "This document mentions Exhibit B, I need to backtrack..."

2. **Dynamic tool selection** - Agent picks from 6 tools based on context:
   - `scan_folder` - parallel preview of all documents
   - `preview_file` - quick look at a specific file
   - `parse_file` - full extraction
   - `read` - text files
   - `grep` - pattern search
   - `glob` - file search

3. **The backtracking moment** (this is the "aha!" for audiences)
   - Agent reads Document A
   - Sees "see Exhibit B"
   - Realizes it skipped Exhibit B earlier
   - Goes back to read it
   - This is genuine autonomous reasoning, not pre-programmed

4. **Non-deterministic behavior**
   - Same query might take different paths
   - Agent adapts to what it finds

---

## Key Contrast Table

| Aspect | n8n Workflow | Agentic File Search |
|--------|--------------|---------------------|
| Flow design | You draw the connections | Agent decides the path |
| Logic | "If X then Y" conditions | "What should I do next?" reasoning |
| Tool usage | Triggered by predefined conditions | Chosen by reasoning |
| Behavior | Deterministic, predictable | Emergent, adaptive |
| Error recovery | Must be designed in | Agent can revise approach |
| Cross-references | Would need explicit handling | Discovered and followed dynamically |

---

## Suggested Demo

### Prerequisites

- ProxyPal running on `http://localhost:8317/v1`
- `.env` configured with ProxyPal credentials

### Setup

```bash
# CLI demo (simpler for presentation)
PYTHONIOENCODING=utf-8 uv run explore --task "Look in data/test_acquisition/. What is the purchase price?"

# Or Web UI (more interactive)
uv run uvicorn fs_explorer.server:app --host 127.0.0.1 --port 8000
# Open browser to http://127.0.0.1:8000
```

### Demo Option 1: IT Project Documents (Recommended for IT audience)

**Folder:** `data/demo_project/`
**Documents:** 6 professional PDF documents (DataFlow Corp branding)

| File | Purpose |
|------|---------|
| project_overview.pdf | Main project doc, references architecture and schedule |
| architecture.pdf | Technical specs, references db_conventions, vendor_agreement, security_policy |
| schedule.pdf | Timeline with Phase 2 dependencies, references vendor_agreement and security_policy |
| db_conventions.pdf | Database standards, references security_policy |
| vendor_agreement.pdf | StreamTech contract with delivery dates |
| security_policy.pdf | Security requirements and Phase 2 sign-off checklist |

**Query:**
```
What are all the dependencies blocking Phase 2 launch?
```

**Why this query?**
- IT audience relates to project management docs
- Clear cross-references between documents
- Agent must follow chains: schedule → vendor → security → db_conventions
- Demonstrates backtracking when discovering references

### Demo Option 2: Acquisition Documents (Original)

**Folder:** `data/test_acquisition/`

**Query:**
```
Look in data/test_acquisition/. What is the purchase price?
```

**Why this query?**
- Requires cross-reference following
- Agent must connect information from multiple documents
- Will trigger the three-phase strategy visibly

### What the Audience Will See

1. **Phase 1: Navigate + Scan**
   - Agent navigates to the directory
   - Uses `scan_folder` to preview ALL 11 documents in parallel
   - Categorizes: RELEVANT / MAYBE / SKIP

2. **Phase 2: Deep Dive**
   - Full extraction on relevant documents (acquisition_agreement, financial_adjustments)
   - Agent explains its reasoning at each step

3. **Final Answer with Citations**
   - Complete answer: Original $45M → Adjusted $43.33M
   - Detailed breakdown with section citations
   - Sources consulted list

### Tested Results (2026-01-16)

**CLI Test:**
| Metric | Value |
|--------|-------|
| Total Steps | 4 |
| API Calls | 5 |
| Documents Scanned | 13 |
| Documents Parsed | 2 |
| Total Tokens | ~29K |
| Est. Cost | $0.11 |

**Web UI Test:**
| Metric | Value |
|--------|-------|
| Total Steps | 3 |
| Documents Scanned | 12 |
| Documents Parsed | 2 |
| API Calls | 4 |
| Total Tokens | 25.8K |
| Est. Cost | $0.09 |

---

## Web UI Walkthrough (for Demo)

### Step-by-Step Guide

1. **Start the server:**
   ```bash
   PYTHONIOENCODING=utf-8 uv run uvicorn fs_explorer.server:app --host 127.0.0.1 --port 8001
   ```

2. **Open browser:** http://localhost:8001

3. **UI Components:**
   - Header: "fs-explorer v0.1.0" with status indicator (● READY)
   - TARGET FOLDER: Shows current path with BROWSE button
   - QUERY: Text input for questions
   - EXECUTE: Button to start exploration
   - EXECUTION LOG: Real-time steps with agent reasoning
   - Stats bar at bottom

4. **Demo Flow:**
   - Click BROWSE → navigate to `data` → `test_acquisition` → SELECT THIS FOLDER
   - Type query: "What is the purchase price?"
   - Click EXECUTE
   - Watch the execution log fill in real-time

5. **What Audience Sees:**
   - **Step #1: SCAN_FOLDER** - Agent explains it's scanning all documents
   - **Step #2: PARSE_FILE** - Shows RELEVANT/MAYBE/SKIP categorization
   - **Step #3: PARSE_FILE** - Agent follows cross-references
   - **RESPONSE** - Final answer with highlighted inline citations
   - **Stats bar** - Steps, scanned, parsed, API calls, tokens, cost

### Key Demo Moments

1. **Categorization reasoning** - Agent explains why each doc is RELEVANT/MAYBE/SKIP
2. **Cross-reference detection** - "I noticed cross-references to exhibits (B and C)"
3. **Inline citations** - Every number has a `[Source: filename, Section]` tag
4. **Sources Consulted** - Clean list at the end
5. **Cost transparency** - ~$0.09 per query visible in stats

---

## Talking Points to Prepare

- [ ] What is an "agent" vs a "workflow"?
- [ ] Why embeddings/RAG isn't enough for cross-references
- [ ] The three-phase strategy (scan → deep dive → backtrack)
- [ ] Cost efficiency (~$0.10 per query with Claude Sonnet via ProxyPal)
- [ ] When to use agentic vs traditional approaches

---

## Questions to Anticipate

- "How is this different from ChatGPT?"
- "Can it make mistakes?"
- "How do you control what it does?"
- "What about security/privacy?" (Docling parses locally, no cloud upload)
- "How much does it cost?"

---

## Slide Content

See **SLIDE_CONTENT.md** for:
- 3 slides to insert after n8n demo (slides 17-18)
- Callback to DELL Romandie Day 2025 RAG presentation
- RAG limitations → Agent paradigm shift narrative
- Three-phase strategy explanation
- Demo script with step-by-step narration
- Q&A talking points

### Slide Flow (3 slides + demo)
1. **RAG Reminder + Limits** - Callback to 2025 + why it's not enough
2. **Paradigm Shift** - Retrieval → Reasoning, why now
3. **Three-Phase Strategy** - Scan → Deep Dive → Backtrack
4. **LIVE DEMO** - FsExplorer in action

### Key Narrative
> "Last year we showed you how to give AI access to your documents. This year, we're showing you how AI can actually understand them."

---

## Open Items

- [x] Create slide content for FsExplorer demo
- [ ] Decide on exact timing for each part
- [ ] Prepare backup if live demo fails
- [ ] Test the demo query multiple times to understand variations
- [ ] Consider creating custom test documents for clearer demo

---

## Session Log

**2026-01-16 (continued):** Slide content creation
- Read YouTube transcript (`YT-This is the new RAG-Transcritption.txt`)
- Created SLIDE_CONTENT.md (condensed to 3 slides):
  1. RAG Reminder + Limits (callback to 2025)
  2. Paradigm Shift (retrieval → reasoning)
  3. Three-Phase Strategy (scan → dive → backtrack)
- Includes demo script with narration table and Q&A talking points
- Key narrative: "Last year: access to documents. This year: understanding them."
- Key closing: "RAG retrieves. Agents reason. That's the evolution."

**2026-01-16:** Initial setup and testing
- Defined audience and presentation flow
- Identified key contrasts between n8n and agentic approach
- Set up git branch (`presentation`) and folder structure
- Created this living document
- Migrated from Google Gemini API to ProxyPal/Claude Sonnet
  - Modified `agent.py` to use OpenAI-compatible client
  - Updated `.env` with ProxyPal credentials
  - Added `openai` dependency
- Successfully tested CLI demo:
  - Query: "What is the purchase price?"
  - Result: Agent found $45M original → $43.33M adjusted
  - 4 steps, 5 API calls, ~$0.11 cost
- Fixed server.py UTF-8 encoding issue for Windows
- Successfully tested Web UI demo:
  - Same query, real-time execution log
  - 3 steps, 4 API calls, ~$0.09 cost
  - Documented complete walkthrough for presentation
