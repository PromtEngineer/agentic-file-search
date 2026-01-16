# UI Improvements - Remaining Work

## Current State (Committed)

The following features are **working**:

1. **Phase Stepper** - Shows SCAN → DEEP DIVE → BACKTRACK progression with visual states (pending/active/done)

2. **Flag Highlighting** - RELEVANT (green), MAYBE (yellow), SKIP (red) badges appear inline in execution log

3. **Tool Icons** - Each tool has an icon (📂 scan, 📄 parse, 🔍 grep, 📖 read, 🔎 glob)

4. **Tool-specific Styling** - Different border colors per tool type

5. **Compact Markdown** - Response text renders with proper headers, lists, bold

6. **Citation Badges** - `[Source: filename]` patterns styled as orange badges

7. **Stats Bar** - Shows steps, scanned, parsed, API calls, tokens, cost

## Issues to Fix

### 1. BACKTRACK Badge Not Triggering

**Problem**: The agent goes back to previously skipped documents (e.g., db_conventions.pdf marked as SKIP gets parsed later) but the BACKTRACK badge doesn't appear.

**Root Cause**: The backtrack pattern requires explicit language like "backtrack", "going back", "revisit", but the agent often says things like "Need to parse X to understand..." without explicit backtrack keywords.

**Current Pattern** (line ~1171 in ui.html):
```javascript
const backtrackPattern = /backtrack|going back|need to (check|parse|read).*([A-Za-z_]+\.(pdf|md)).*skip|previously skipped|revisit/i;
```

**Possible Solutions**:
- A) Make the pattern less strict (risk: false positives)
- B) Modify the agent's SYSTEM_PROMPT to use explicit backtrack language more consistently
- C) Track which files were marked SKIP in the decision block, then auto-detect when those files are parsed later
- D) Accept that backtrack badge is best-effort and won't always trigger

### 2. Decision Block Feature (Deferred)

**What it was**: A visual block between SCAN and PARSE showing the categorization (RELEVANT/MAYBE/SKIP files in a structured layout).

**Why removed**: Multiple bugs:
- Appeared before scan instead of after
- Wrong files extracted from reason text
- Complex timing/ordering issues

**If resuming**: The code for `parseCategorization()`, `createDecisionBlock()`, etc. is still in ui.html but not being called. Key insight: the categorization text appears in the FIRST parse_file step's reason, not in scan_folder's reason.

### 3. Phase Stepper - BACKTRACK Phase Never Activates

**Problem**: The phase stepper shows BACKTRACK as pending (gray) even when the agent is actually backtracking.

**Root Cause**: Same as #1 - the `updatePhase()` function uses the same `backtrackPattern` to detect when to transition to phase 3.

**Location**: `updatePhase()` function in ui.html

## Files

- `src/fs_explorer/ui.html` - All UI code (single file)
- `src/fs_explorer/agent.py` - Agent's SYSTEM_PROMPT defines the three-phase strategy and expected language

## Test Data

- Folder: `./data/demo_project` (6 PDF files)
- Query: "What are all the dependencies blocking Phase 2 launch?"
- Note: Documents were originally .md files converted to .pdf, so cross-references mention ".md" extensions

## Demo Notes

For the DELL Romandie Day 2026 presentation:
- The flag highlighting (RELEVANT/MAYBE/SKIP) is the key visual that shows the agent reasoning
- Phase stepper shows the three-phase strategy clearly
- Even without BACKTRACK badge, the execution log shows the agent parsing previously skipped documents
- The response with citation badges shows the final answer with sources
