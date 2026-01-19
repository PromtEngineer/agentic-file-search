# FsExplorer Demo Explanation

## The Three-Phase Document Exploration Strategy

FsExplorer uses an **agentic approach** to document search - instead of traditional RAG (embedding all documents into vectors), the AI agent navigates the filesystem like a human researcher would: scanning, reasoning, and following cross-references.

---

## Demo Scenario: TechCorp Team Building Event

**Query:** "Can we accommodate everyone's dietary needs at the venue?"

**Context:** TechCorp is planning a team building event for 25 employees. The agent must determine if all dietary requirements can be met within the approved budget.

**Documents:** 5 PDFs in `data/event_demo/`

| File | Content | Initial Category |
|------|---------|------------------|
| guest_list.pdf | 25 guests with dietary requirements | RELEVANT |
| catering_menu.pdf | Menu options and pricing | RELEVANT |
| venue_info.pdf | Venue catering capabilities | MAYBE |
| event_details.pdf | General event information | SKIP |
| finance_approval.pdf | Budget constraints | SKIP |

---

## Phase 1: SCAN (Parallel Scan)

**What it does:** Scans ALL documents in the folder simultaneously to get a quick preview of each one.

**In this demo:**
- The agent scanned all 5 PDF files in `event_demo/`
- It categorized each document based on relevance to the query:
  - **RELEVANT** (green): `guest_list.pdf`, `catering_menu.pdf` - directly related to dietary needs
  - **MAYBE** (yellow): `venue_info.pdf` - might have catering capability info
  - **SKIP** (red): `event_details.pdf` - general event info, `finance_approval.pdf` - "financial policies, not dietary-related"

**Key insight:** The agent makes intelligent triage decisions, not blindly reading everything. Note that it skips the finance document - this becomes important later!

---

## Phase 2: DEEP DIVE (Detailed Parsing)

**What it does:** Fully parses the RELEVANT and MAYBE documents to extract detailed information.

**In this demo:**
- Parsed `catering_menu.pdf` - Found dietary options:
  - Vegetarian: included in base price
  - Vegan: +$5/person
  - Gluten-free: included in base price
  - Nut-free: +$15/person for ENTIRE event
- Parsed `guest_list.pdf` - Found critical dietary requirements:
  - 3 vegetarian guests (Lisa Anderson, Rachel Green, Megan Young)
  - 2 vegan guests (+$10 total)
  - 1 gluten-free guest (Sarah Chen with celiac disease)
  - 1 SEVERE nut allergy (Tom Rodriguez) - requires nut-free preparation for all food

**Key insight:** While reading `catering_menu.pdf`, the agent notices it specifically references `finance_approval.pdf` for nut-free pricing impact.

---

## Phase 3: BACKTRACK (Follow Cross-References)

**What it does:** Goes back to previously skipped documents when cross-references reveal they're actually relevant.

**In this demo:**
- While reading `catering_menu.pdf`, the agent found a reference to budget constraints in `finance_approval.pdf`
- It realized `finance_approval.pdf` (which it had SKIPPED) contains critical budget information
- The agent **backtracked** to parse `finance_approval.pdf`
- **Eureka moment:** Discovered the budget is $1,125 for base catering only, with **$0 available for add-ons**

**The BACKTRACK badge appears** on the step, showing the agent revisiting a document it initially skipped.

**Key insight:** This is what makes agentic search powerful - it can change its mind based on new information, just like a human researcher would.

---

## The "Aha Moment" for the Audience

> "Notice how the agent initially skipped `finance_approval.pdf` - it seemed unrelated to dietary needs. But while reading the catering menu, it discovered a cross-reference about pricing impact. The agent **changed its mind** and went back to check that document. That's where it found the critical budget constraint: $0 available for add-ons, but nut-free preparation costs $375. This is something traditional RAG search cannot do - it would have either missed the budget document entirely or retrieved it without understanding the context."

---

## How to Explain the UI Elements

| UI Element | What It Shows |
|------------|---------------|
| **Phase Stepper** (top) | Visual progress through the 3 phases - gray (pending) → orange (active) → green (done) |
| **RELEVANT/MAYBE/SKIP badges** | Agent's real-time categorization decisions |
| **BACKTRACK badge** | Agent revisiting a previously skipped document |
| **Eureka highlights** (orange text) | Key discoveries like "cross-reference", "backtracking", "$0 available" |
| **Bold filenames** | All document names appear bold for easy scanning |
| **Citation badges** (orange, in response) | Sources for each fact in the final answer |
| **Stats bar** (bottom) | Steps taken, documents scanned/parsed, API calls, tokens, cost |

---

## Why This Matters (vs Traditional RAG)

| Traditional RAG | Agentic Search (FsExplorer) |
|-----------------|----------------------------|
| Embeds all docs upfront | Scans and triages intelligently |
| Returns "top K" similar chunks | Reasons about document relevance |
| No cross-reference following | Follows references between documents |
| Static retrieval | Dynamic, iterative exploration |
| Can miss context | Builds understanding progressively |
| Would miss the budget constraint | Discovers it through backtracking |

---

## Demo Script Summary

1. **Start**: "Can we accommodate everyone's dietary needs at the venue?"
2. **Phase 1**: Watch the SCAN phase categorize 5 documents (point out the SKIP on finance_approval.pdf)
3. **Phase 2**: Watch DEEP DIVE parse the relevant docs (point out the cross-reference discovery)
4. **Phase 3**: **Key moment** - BACKTRACK badge appears when parsing finance_approval.pdf
5. **Eureka**: "$0 available" highlighted - the budget constraint that changes everything
6. **Result**: Comprehensive answer showing which needs CAN be met and which CANNOT due to budget

---

## Demo Commands

```bash
# Start the web server
uv run uvicorn fs_explorer.server:app --host 127.0.0.1 --port 8000

# Open browser to http://127.0.0.1:8000
# Set folder to: data/event_demo
# Query: Can we accommodate everyone's dietary needs at the venue?
```
