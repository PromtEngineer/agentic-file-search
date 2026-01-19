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

### 2. Decision Block Feature - IMPLEMENTED

**What it is**: A visual block showing the agent's document categorization (RELEVANT/MAYBE/SKIP files in a structured grid layout).

**Implementation**:
- Grid layout with 3 columns (RELEVANT/MAYBE/SKIP)
- Shows file counts per category
- File items with hover states
- Distinctive orange border and header styling
- Appears after scan_folder showing how agent categorized documents

**Related changes**:
- Cross-reference notification blocks (blue styling)
- Thinking indicator with animated dots
- Result panel completion states (success/error/uncertain)

### 3. Phase Stepper - BACKTRACK Phase Never Activates - FIXED

**Problem**: The phase stepper shows BACKTRACK as pending (gray) even when the agent is actually backtracking.

**Solution**: Fixed along with #1 - `updatePhase()` now receives the `isBacktracking` flag directly from `addStep()`, which uses the improved detection logic (explicit keywords + auto-detection of parsing skipped files).

## Files

- `src/fs_explorer/ui.html` - All UI code (single file)
- `src/fs_explorer/agent.py` - Agent's SYSTEM_PROMPT defines the three-phase strategy and expected language

## Test Data

- Folder: `./data/event_demo` (5 PDF files)
- Query: "Can we accommodate everyone's dietary needs at the venue?"
- Scenario: TechCorp team building event for 25 employees

## Demo Notes

For the DELL Romandie Day 2026 presentation:
- The flag highlighting (RELEVANT/MAYBE/SKIP) is the key visual that shows the agent reasoning
- Phase stepper shows the three-phase strategy clearly
- BACKTRACK badge appears when agent revisits `finance_approval.pdf`
- **Eureka highlights** (orange) call attention to key discoveries: "cross-reference", "backtracking", "$0 available"
- **Bold filenames** make document names easy to scan in execution log
- The response with citation badges shows the final answer with sources
