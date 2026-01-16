# FsExplorer Demo Slides (Condensed)

> 3 slides to insert after the n8n demo (slides 17-18)
> Theme: AI Agents are transforming how we approach classic AI problems

---

## Slide 1: RAG - Remember & Limits

### Title
**RAG: What We Learned Last Year**
*(Et pourquoi ça ne suffit pas toujours)*

### Left Side: The RAG Pipeline (Quick Visual)
```
[Documents] → [Chunks] → [Embeddings] → [Vector DB] → [Similar Chunks] → [LLM]
```
**DELL Romandie Day 2025**: Embed your documents, ask questions, get answers.

### Right Side: Where It Falls Short

| Problem | Impact |
|---------|--------|
| **Chunking destroys context** | "Purchase price" chunk doesn't know about "Exhibit B" 3 pages later |
| **Cross-references invisible** | Can't follow "see Section 4.2" |
| **Similarity ≠ Relevance** | Finds similar text, not useful text |

### Bottom Quote
> "RAG is pattern matching. It doesn't **understand** your document."

### Speaker Notes
"For those who attended last year - RAG works for simple cases. But when documents reference each other, like legal or technical docs, RAG can't follow the chain. It retrieves, it doesn't reason."

---

## Slide 2: The Agent Paradigm Shift

### Title
**From Retrieval to Reasoning**

### Two Columns Comparison

| RAG | Agentic AI |
|-----|------------|
| Pre-computed embeddings | Dynamic exploration |
| Fixed chunks | Intelligent navigation |
| Pattern matching | Active reasoning |
| "Find similar text" | "Understand the document" |

### Center Quote (Large)
> **"What if we let AI navigate documents like a human would?"**

### Why Now? (Three Quick Points)
- LLMs can **reason** about next steps
- Structured outputs = reliable tool use
- Inference cost dropped 100x in 2 years

### Speaker Notes
"This is the shift: instead of pre-computing and hoping, we let the AI actively explore. It's the difference between a search engine and a research assistant."

---

## Slide 3: The Three-Phase Strategy

### Title
**How Agentic Document Search Works**

### Visual: Three Connected Boxes
```
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│   1. SCAN     │      │  2. DEEP DIVE │      │  3. BACKTRACK │
│               │      │               │      │               │
│  Preview ALL  │ ──►  │ Read RELEVANT │ ──►  │ Follow CROSS- │
│  in parallel  │      │ fully         │      │ REFERENCES    │
└───────────────┘      └───────────────┘      └───────────────┘
                                                     │
                                    ┌────────────────┘
                                    ▼
                          "I skipped Exhibit B,
                           but Document A needs it.
                           Going back."
```

### Key Point (Highlighted)
**This is genuine autonomous reasoning** - not pre-programmed "if X then Y"

### Speaker Notes
"Scan everything to understand the landscape. Deep-dive into relevant docs. And critically - if it finds a reference to something it skipped, it backtracks. Let me show you."

---

## LIVE DEMO

### Introduction (10 seconds)
"6 IT project documents - the kind you deal with every day. One question about project dependencies."

### Query
```
What are all the dependencies blocking Phase 2 launch?
```

### What to Point Out

| Step | What Happens | Say This |
|------|--------------|----------|
| **Scan** | Previews all 6 PDFs | "Categorizing: RELEVANT, MAYBE, SKIP - it identified schedule.pdf as key" |
| **Deep Dive** | Reads schedule.pdf | "Found Phase 2 dependencies... sees references to vendor_agreement and security_policy" |
| **Backtrack** | Goes to vendor_agreement.pdf | "Following the cross-reference - checking delivery dates" |
| **Backtrack** | Goes to security_policy.pdf | "Another reference - checking security sign-off requirements" |
| **Answer** | Complete dependency list with dates and owners | "Connected 4 documents. Every fact has a source." |

### Expected Answer (Summary)
The agent should find:
1. **Vendor Delivery** - StreamTech module due Jan 25, 2026 (from vendor_agreement.pdf)
2. **Security Sign-off** - Penetration tests, API review, James Morton approval (from security_policy.pdf)
3. **Database Readiness** - Schemas must comply with db_conventions.pdf
4. **Phase 1 Completion** - All batch pipelines operational (from schedule.pdf)

### Closing Line
"RAG retrieves. Agents reason. That's the evolution."

---

## Quick Stats (If Asked)

| Metric | Value |
|--------|-------|
| Documents | 6 |
| Fully parsed | 3-4 |
| Steps | 4-5 |
| Cost | ~$0.10 |

---

## Q&A Talking Points

**"Different from last year's RAG?"**
RAG hopes the right chunk appears. This agent decides what to read and follows references.

**"Slower?"**
Yes. RAG = speed. Agents = accuracy. Use agents when cross-references matter.

**"Cost?"**
~$0.10 vs ~$0.001. Worth it for legal/financial where accuracy matters.

**"Privacy?"**
Docling parses locally. Only text goes to LLM.

---

## Slide Flow Summary

1. **RAG Reminder + Limits** (callback to 2025, why it's not enough)
2. **Paradigm Shift** (retrieval → reasoning)
3. **Three-Phase Strategy** (scan → dive → backtrack)
4. **LIVE DEMO**

### Key Narrative
> "Last year: how to give AI access to documents. This year: how AI can understand them."

