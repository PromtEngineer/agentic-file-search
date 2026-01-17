# FsExplorer Demo Explanation

## The Three-Phase Document Exploration Strategy

FsExplorer uses an **agentic approach** to document search - instead of traditional RAG (embedding all documents into vectors), the AI agent navigates the filesystem like a human researcher would: scanning, reasoning, and following cross-references.

---

## Phase 1: SCAN (Parallel Scan)

**What it does:** Scans ALL documents in the folder simultaneously to get a quick preview of each one.

**In this demo:**
- The agent scanned all 6 PDF files in `demo_project/`
- It categorized each document based on relevance to the query:
  - **RELEVANT** (green): `schedule.pdf`, `project_overview.pdf` - clearly related to dependencies
  - **MAYBE** (yellow): `architecture.pdf`, `vendor_agreement.pdf`, `security_policy.pdf` - might have useful info
  - **SKIP** (red): `db_conventions.pdf` - "database naming conventions unlikely to contain phase dependencies"

**Key insight:** The agent makes intelligent triage decisions, not blindly reading everything.

---

## Phase 2: DEEP DIVE (Detailed Parsing)

**What it does:** Fully parses the RELEVANT and MAYBE documents to extract detailed information.

**In this demo:**
- Parsed `schedule.pdf` - Found Phase 2 dependencies and timelines
- Parsed `vendor_agreement.pdf` - Found StreamTech delivery date (Jan 25, 2026)
- Parsed `security_policy.pdf` - Found security certification requirements
- Parsed `architecture.pdf` - Found infrastructure specs, BUT also discovered a **cross-reference** to database performance benchmarks

**Key insight:** While reading, the agent watches for cross-references to other documents.

---

## Phase 3: BACKTRACK (Follow Cross-References)

**What it does:** Goes back to previously skipped documents when cross-references reveal they're actually relevant.

**In this demo:**
- While reading `architecture.pdf` and `security_policy.pdf`, the agent found references to database requirements
- It realized `db_conventions.pdf` (which it had SKIPPED) might contain the "Database Readiness" dependency details
- The agent **backtracked** to parse `db_conventions.pdf`

**The BACKTRACK badge appears** on step #6, showing the agent revisiting a document it initially skipped.

**Key insight:** This is what makes agentic search powerful - it can change its mind based on new information, just like a human researcher would.

---

## How to Explain the UI Elements

| UI Element | What It Shows |
|------------|---------------|
| **Phase Stepper** (top) | Visual progress through the 3 phases - gray (pending) → orange (active) → green (done) |
| **RELEVANT/MAYBE/SKIP badges** | Agent's real-time categorization decisions |
| **BACKTRACK badge** | Agent revisiting a previously skipped document |
| **Citation badges** (orange, in response) | Sources for each fact in the final answer |
| **Stats bar** (bottom) | Steps taken, documents scanned/parsed, API calls, tokens, cost |

---

## The "Aha Moment" for the Audience

> "Notice how the agent initially skipped `db_conventions.pdf` - it seemed irrelevant. But while reading other documents, it discovered cross-references to database requirements. The agent **changed its mind** and went back to check that document. This is something traditional RAG search cannot do - it would have either missed the document entirely or retrieved it without understanding the context."

---

## Why This Matters (vs Traditional RAG)

| Traditional RAG | Agentic Search (FsExplorer) |
|-----------------|----------------------------|
| Embeds all docs upfront | Scans and triages intelligently |
| Returns "top K" similar chunks | Reasons about document relevance |
| No cross-reference following | Follows references between documents |
| Static retrieval | Dynamic, iterative exploration |
| Can miss context | Builds understanding progressively |

---

## Demo Script Summary

1. **Start**: "What are all the dependencies blocking Phase 2 launch?"
2. **Phase 1**: Watch the SCAN phase categorize 6 documents (point out the SKIP on db_conventions.pdf)
3. **Phase 2**: Watch DEEP DIVE parse the relevant docs (point out cross-references being discovered)
4. **Phase 3**: **Key moment** - BACKTRACK badge appears on db_conventions.pdf
5. **Result**: Comprehensive answer with citations from multiple documents, including the one initially skipped

---

## Demo Commands

```bash
# Start the web server
uv run uvicorn fs_explorer.server:app --host 127.0.0.1 --port 8000

# Open browser to http://127.0.0.1:8000
# Set folder to: ./data/demo_project
# Query: What are all the dependencies blocking Phase 2 launch?
```
