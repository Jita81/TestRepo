# Agent context retrieval: semantic search + indexed text search

**Status:** Platform policy · March 2026  
**Related:** [context-platform-process-architecture.md](context-platform-process-architecture.md) · Epic **G** (codebase intelligence) in [roadmap-github-issues.md](roadmap-github-issues.md) · **Phase 11 MVP index:** [codebase-index-phase11.md](codebase-index-phase11.md)

This document states **how we treat “context” for agentic workflows** in the Automated Agile / Context Engineering Platform: **structured human decisions** (this repo’s spine) sit alongside **machine retrieval** from code and text. For the latter, we explicitly endorse **two complementary modes**:

1. **Semantic retrieval** — embeddings / nearest-neighbour search for “what is this about?”
2. **Fast text / regex retrieval** — pattern search over raw source, which agents still rely on heavily (e.g. ripgrep-style tools)

State-of-the-art agent harnesses improve quality with semantic indexes, but **many tasks can only be closed with regular expressions** over the actual bytes on disk. In large monorepos, **unindexed** full-repository scans become a dominant latency (e.g. multi-second `rg` runs), which stalls human–agent pairing.

---

## What the research converges on

The following is a condensed synthesis of well-known work (inverted indexes for text, trigram decomposition for regex, suffix arrays, sparse n-grams, client-side freshness). A readable modern treatment appears in **Vicent Martí**, *Fast regex search: indexing text for agent tools* (Cursor Research, Mar 2026).

| Idea | Role |
|------|------|
| **Inverted index** | Map tokens → posting lists (documents/locations); intersect or join lists at query time. |
| **Trigram tokenization** | Split corpus and queries into overlapping 3-grams so regex literals decompose to index lookups; **candidates** are then verified by real regex match (false positives OK). |
| **Query decomposition trade-off** | Too few trigrams → huge candidate sets; too many → index I/O as slow as scanning. Heuristics matter. |
| **Suffix arrays** | Alternative corpus index (e.g. livegrep-style); powerful but costly to update; hard for huge moving workspaces. |
| **Augmented trigrams / Bloom-style masks** | Narrow candidates (e.g. next-character / position hints); still ends in deterministic verification. |
| **Sparse n-grams** | Deterministic “important” substrings (e.g. edge-weighted segmentation); **covering** queries use fewer lookups than full trigram enumeration. |
| **Client-side indexes** | Keep index **local** to avoid file sync round-trips, preserve privacy, and keep **freshness** high when the agent reads its own writes; base state on **Git commits** plus a layer for uncommitted edits. |
| **On-disk layout** | e.g. mmap lookup table + postings file — tight memory footprint in the editor/agent host. |

**Conclusion we adopt:** For agent tooling, **invest in indexed regex search** (whatever generation of the above fits your stack) **in addition to** semantic indexes — especially for **enterprise-scale** repositories.

---

## Implications for this platform (MVP + roadmap)

| Layer | Guidance |
|-------|----------|
| **Context packages (B1/B2)** | Prefer **stable, grep-friendly literals** where appropriate: canonical error strings, route paths, env var names, feature flags, and file paths in `technical_approach.files_to_touch`. That helps agents *and* humans align search with approved context. |
| **Manufacturing (D9)** | The git adapter runs in a **bounded clone**; without a product-side index, search inside that tree is still **linear scan**. Keep **`MANUFACTURING_RUN_CMD`** and workspace scope **bounded** for predictability. |
| **Codebase intelligence (Epic G)** | When we add intel, plan **regex-oriented indexes** (trigram / sparse n-gram family) **alongside** any embedding pipeline — not as a replacement for LSP, but as the fast path for “find this pattern everywhere.” |
| **Traceability** | Audit and artifacts remain **structured**; they do not replace **live code search**. Agents resolve “what did we decide?” here and “where is it in the repo?” via search tools. |

---

## What this repo does *not* implement today

The reference implementation is **SQLite + REST + dashboard**. It does **not** ship a trigram index, ripgrep integration, or client-side mmap store. This file is **policy and architecture**: implementation belongs in the agent host, IDE, or a future **G** epic service.

---

## References

- Vicent Martí, *Fast regex search: indexing text for agent tools* (Cursor Research, Mar 2026) — trigram history, GitHub Code Search evolution, sparse n-grams, client-side indexing.
- J. Zobel, A. Moffat, R. Sacks-Davis, *Searching Large Lexicons for Partially Specified Terms using Compressed Inverted Files* (1993).
- Russ Cox, Google Code Search / trigram articles (~2012).
- Nelson Elhage, livegrep / suffix-array approach (~2015).
- `google/codesearch`, `sourcegraph/zoekt` — trigram inverted-index search engines.
