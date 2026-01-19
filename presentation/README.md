# Presentation: Agentic AI Demo

This folder contains materials for demonstrating Agentic AI concepts using the FsExplorer application.

## Target Audience

IT professionals, not necessarily AI-literate.

## Presentation Flow

1. **n8n Workflow** (simple, visual) - Shows predefined automation with parent/child agents for Email, Calendar, Contacts
2. **Agentic File Search** (advanced) - Shows autonomous reasoning, dynamic tool selection, backtracking

## Key Contrast

| Aspect | n8n Workflow | Agentic File Search |
|--------|--------------|---------------------|
| Flow design | You draw connections | Agent decides the path |
| Logic | "If X then Y" conditions | "What should I do next?" reasoning |
| Tool usage | Triggered by conditions | Chosen by reasoning |
| Behavior | Deterministic | Emergent, adaptive |
| Backtracking | Not possible | Agent can revise its approach |

## Git Setup

This branch (`presentation`) is for demo preparation work.

### Remote Configuration

```
upstream = https://github.com/PromtEngineer/agentic-file-search.git (original repo)
origin   = (to be added when forking to personal GitHub)
```

### Sync with Upstream

To pull updates from the original repo:

```bash
git checkout main
git pull upstream main
git checkout presentation
git merge main
```

### Fork to Personal GitHub

When ready to fork:

1. Fork on github.com
2. Add your fork as origin:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/agentic-file-search.git
   ```
3. Push your branch:
   ```bash
   git push -u origin presentation
   ```

## Demo Scenario: TechCorp Event Planning

**Query:** "Can we accommodate everyone's dietary needs at the venue?"

**Data:** `data/event_demo/` (5 PDFs)
- guest_list.pdf - 25 guests with dietary requirements
- catering_menu.pdf - Menu options and pricing
- venue_info.pdf - Venue catering capabilities
- event_details.pdf - General event info
- finance_approval.pdf - Budget constraints (the "eureka" document!)

**Key Demo Moment:** Agent initially skips `finance_approval.pdf`, then backtracks when it discovers a cross-reference, revealing a critical budget constraint.

## Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | This overview |
| `SLIDE_CONTENT.md` | Slide content for the 3 demo slides |
| `DEMO_EXPLANATION.md` | Detailed walkthrough of the three-phase strategy |
| `PREP_NOTES.md` | Living document with setup, talking points, Q&A |
| `UI_IMPROVEMENTS_TODO.md` | Tracks UI features and fixes |

## Quick Start

```bash
# Start the web server
uv run uvicorn fs_explorer.server:app --host 127.0.0.1 --port 8000

# Open browser to http://127.0.0.1:8000
# Set folder to: data/event_demo
# Query: Can we accommodate everyone's dietary needs at the venue?
```
