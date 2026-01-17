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

### 1. BACKTRACK Badge Not Triggering - FIXED

**Problem**: The agent goes back to previously skipped documents (e.g., db_conventions.pdf marked as SKIP gets parsed later) but the BACKTRACK badge doesn't appear.

**Solution Implemented**: Option C - Track skipped files and auto-detect when they get parsed

**Changes made** (in ui.html):
1. Added `skippedFiles` Set to track files marked as SKIP
2. Added `extractSkippedFiles(reason)` function to parse SKIP markers from categorization
3. Added `wasSkipped(filePath)` function to check if a file was previously skipped
4. Modified `addStep()` to:
   - Extract and track skipped files from each reason
   - Detect backtracking via explicit keywords OR parsing a previously skipped file
5. Updated `updatePhase()` to accept `isBacktracking` parameter directly
6. Reset `skippedFiles` on new exploration

**Now triggers when**:
- Explicit backtrack language is used (backtrack, going back, revisit, etc.)
- A file that was marked SKIP is later parsed/read/previewed

### 2. Decision Block Feature (Deferred)

**What it was**: A visual block between SCAN and PARSE showing the categorization (RELEVANT/MAYBE/SKIP files in a structured layout).

**Why removed**: Multiple bugs:
- Appeared before scan instead of after
- Wrong files extracted from reason text
- Complex timing/ordering issues

**If resuming**: The code for `parseCategorization()`, `createDecisionBlock()`, etc. is still in ui.html but not being called. Key insight: the categorization text appears in the FIRST parse_file step's reason, not in scan_folder's reason.

### 3. Phase Stepper - BACKTRACK Phase Never Activates - FIXED

**Problem**: The phase stepper shows BACKTRACK as pending (gray) even when the agent is actually backtracking.

**Solution**: Fixed along with #1 - `updatePhase()` now receives the `isBacktracking` flag directly from `addStep()`, which uses the improved detection logic (explicit keywords + auto-detection of parsing skipped files).

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
