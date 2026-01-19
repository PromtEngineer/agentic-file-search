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

### Demo Option 1: Event Planning (Recommended for presentation)

**Folder:** `data/event_demo/`
**Documents:** 5 professional PDF documents (TechCorp branding)

| File | Purpose |
|------|---------|
| guest_list.pdf | 25 guests with dietary requirements |
| catering_menu.pdf | Menu options and pricing, references finance_approval |
| venue_info.pdf | Venue catering capabilities |
| event_details.pdf | General event information |
| finance_approval.pdf | Budget constraints (critical - initially skipped!) |

**Query:**
```
Can we accommodate everyone's dietary needs at the venue?
```

**Why this query?**
- Relatable scenario - everyone understands event planning
- Clear backtracking moment: finance doc initially skipped, then discovered via cross-reference
- Eureka moment: $0 budget for add-ons but nut-free costs $375
- Shows real business impact of the agent's reasoning

### Demo Option 2: Acquisition Documents (Alternative)

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
   - Uses `scan_folder` to preview ALL 5 documents in parallel
   - Categorizes: RELEVANT / MAYBE / SKIP
   - Note: `finance_approval.pdf` gets SKIP'd - seems unrelated to dietary needs

2. **Phase 2: Deep Dive**
   - Full extraction on relevant documents (catering_menu, guest_list)
   - Agent discovers cross-reference to finance document
   - Agent explains its reasoning at each step

3. **Phase 3: Backtrack**
   - Agent goes back to parse `finance_approval.pdf`
   - Discovers the critical budget constraint
   - BACKTRACK badge appears on the step

4. **Final Answer with Citations**
   - Which dietary needs CAN be accommodated (vegetarian, gluten-free)
   - Which CANNOT due to budget (nut-free preparation)
   - Clear recommendation for additional budget approval

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
   - Click BROWSE → navigate to `data` → `event_demo` → SELECT THIS FOLDER
   - Type query: "Can we accommodate everyone's dietary needs at the venue?"
   - Click EXECUTE
   - Watch the execution log fill in real-time

5. **What Audience Sees:**
   - **Step #1: SCAN_FOLDER** - Agent explains it's scanning all documents, categorizes them
   - **Step #2: PARSE_FILE** - Deep dive into catering_menu, discovers cross-reference
   - **Step #3: PARSE_FILE** - Parses guest_list, finds dietary requirements
   - **Step #4: PARSE_FILE (BACKTRACK)** - Goes back to finance_approval.pdf
   - **RESPONSE** - Final answer with highlighted inline citations
   - **Stats bar** - Steps, scanned, parsed, API calls, tokens, cost

### Key Demo Moments

1. **Categorization reasoning** - Agent explains why finance_approval is SKIP'd (not dietary-related)
2. **Cross-reference detection** - "catering_menu references finance_approval for pricing impact"
3. **Backtrack moment** - Agent goes back to the SKIP'd document
4. **Eureka highlight** - "$0 available" appears in orange, showing the budget constraint
5. **Bold filenames** - All document names are bold for easy scanning
6. **Cost transparency** - ~$0.10 per query visible in stats

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
