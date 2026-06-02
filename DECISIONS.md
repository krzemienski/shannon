# Shannon v1 — DECISIONS

> Captures the user decisions made at PRD approval (Phase 0). Future planning references these. Changes to any decision require revising the PRD and BRIEF.

## Decisions made on 2026-05-28 (PRD Section 13 sign-off)

### D1 — Architecture: **Hybrid (Architecture C)**

Sub-agents at `agents/<name>/` carry their skills inline via embedded skill bundles produced by a build step. Skills remain canonical at `skills/<name>/SKILL.md` as the single source of truth.

| Rejected | Why |
|---|---|
| A (heavy agents, thin skills) | Too disruptive — 80% of skill content moves into agents/; duplication management problems |
| B (current v7 model, skill cascade only) | Doesn't solve the silent-invocation-failure mode the user explicitly raised |

**Implication for v1:** Phase 2 builds the embedding mechanism. Agents reliably load their skills at spawn time.

### D2 — Component reductions: **Accept and tune during Phase 1 audit**

| Component | Current count | v1 target | Tune during |
|---|---|---|---|
| Skills (canonical) | 67 | ~30 | Phase 1 |
| Agents | 14 | 8-12 | Phase 1 + 2 |
| Commands | 27 | 15-18 | Phase 3 |
| Hooks | 14 | 6-8 | Phase 4 |
| Core docs | 9 | 5-7 | Phase 6 |

Targets are approximate. Phase 1 audit may discover the right number is 25 or 35 for skills, etc. The reductions are intent; the exact landing point comes from the audit.

### D3 — MCP set: **Context7 + sequential-thinking only (no Memory)**

User's rationale: "Memory MCP is for state files. We never explicitly use it. I've never seen things actually getting done. Memory is on state files, so no, we don't want it as memory."

Default-recommended MCPs in the plugin manifest:
- **Context7** — fresh library/API documentation
- **sequential-thinking** — systematic problem decomposition

Memory MCP is explicitly NOT in the recommended set. State persistence in Shannon happens via on-disk state files (`.shannon/state/`, `.planning/`, `.evidence/`), not via Memory MCP.

Additional MCPs may be added in v0.x if research during a phase surfaces a concrete need. Each addition requires:
1. Documented justification (which skill / capability needs it)
2. Graceful-degradation pattern (skill must work — possibly degraded — when MCP is absent)
3. Recommended-not-required status (no MCP becomes hard-required)

### D4 — Tmux harness scope: **Full coverage**

All 5 pillars get ≥1 Tmux benchmark, not just pillar 5 (self-instrumentation). User's rationale: properly test that hooks fire, slash commands resolve, status line behaves, color codes render, every functionality works end-to-end in a real Claude Code session.

SDK harness ALSO covers all 5 pillars. They're complementary, not substitutes.

### D5 — Naming and version: **Keep `shannon` name; start at v0.x**

Plugin name: `shannon` (preserves any existing community recognition; no rename overhead).

Starting version: **0.1.0** (NOT v1.0.0 or v7).

User's rationale:
- "Star version zero" — start at v0.x to signal early/development; users should expect breaking changes through v0.x
- "Shannon deck plugin" — possibly "Shannon dev plugin" or just keeping the Shannon name with subtitle
- Calling this "v7" misrepresents maturity; calling it "v1.0" claims stability that isn't there yet
- v0.x lets us iterate publicly without compatibility promises

## Decisions deferred to later phases

These came up in PRD discussion but don't need to be resolved at Phase 0:

| Question | Deferred to | Tentative position |
|---|---|---|
| Whether Shannon ships its own CLI alongside the plugin | v1.x (post-0.1.0) | Plugin-only at v0.1.0; CLI wrapper if research justifies |
| Whether to publish to a marketplace OR distribute via GitHub `marketplace add` | Phase 7 | Try Claude Code marketplace; fall back to GitHub if API doesn't exist yet |
| Whether `agents/*/_built/` is .gitignored OR committed | Already decided in Phase 0 | .gitignored (already in `.gitignore`); committed if reproducibility issues surface |
| Whether to deprecate the `skill-creator` skill since Architecture C changes skill authorship | Phase 1 | Likely kept; updated to write to both `skills/` (canonical) AND optionally register with an agent's manifest.yml |
| Whether the Tmux harness drives the user's actual `claude` binary OR a stub | Decided | Real `claude` binary; Iron Rule applies to the harness itself |

## What this DECISIONS.md is NOT

- Not a contract with users (v0.x explicitly disclaims stability)
- Not a blocker on future architecture changes; if v0.2 needs Architecture A characteristics for some agents, the PRD gets revised
- Not the place to track per-phase decisions; those go in each phase's `SUMMARY.md`

## Provenance

- User decisions transcribed from voice input on 2026-05-28
- PRD Section 13 (`../docs/PRD-V1.md`) is the document these answered
- BRIEF.md (this directory) cites these
- ROADMAP.md (this directory) operationalizes them across 7 phases

## Updating this file

Per the Iron Rule applied to Shannon's own development:
- Changes require updated PRD reference + dated entry
- A unilateral edit to DECISIONS.md without companion PRD update = REFUSED
- Companion documents (BRIEF, ROADMAP) update in the same change

---

## Amendments made on 2026-06-01 (Approval Gate sign-off — Phase 1 close)

> Source: `plans/260601-1712-shannon-consolidation/APPROVAL-SIGNED.md`. Five decisions signed by the user. Two reverse prior commitments (surfaced with original-decision + audit-reasoning + tradeoff, explicitly chosen — authorized reversals, not silent drift). Recorded here per the decision-guard "document drift" rule.

### D5 — SUPERSEDED (version reconciliation)

D5 originally said "keep `shannon` name; start at v0.x (0.1.0, NOT v1.0.0)." That is now **superseded**.

- **Reality:** Shannon shipped as v1.0.0 (tag + manifest + commit `1e39c61`). The v1.0.0 tag is the truth — it is the actual first stable release.
- **New call:** the v1.x line is canonical. This consolidation edition ships as **v1.1**. The `shannon` name is retained (unchanged from D5).
- **Implication:** version manifests move to `1.1.0-dev` during the consolidation; v1.0.0 tag/ancestry is never rewritten.

### D6 — Forge restored in v1.1 (reverses the cut-commands deferral)

- **Prior decision:** `.planning/phases/03-commands/cut-commands.md` logged `forge` (the 10-phase Crucible pipeline) as "deliberately deferred to v1.x"; its oracle role was absorbed into critic/reviewer/validator and `cook` (5-phase) was the v1 path.
- **New call (2026-06-01):** restore the forge 10-phase pipeline **now**, in v1.1. Forge gets its own phase.
- **Implication:** `cut-commands.md` is amended (forge moves from "deferred" to "restored in v1.1"). Forge-vs-cook recommended-workflow guidance must be clarified to avoid confusion between the two overlapping pipelines.

### D7 — UI runtime re-included as v0.2.0 scope (reverses BRIEF "must NOT do")

- **Prior decision:** BRIEF "What v1 must NOT do" — no server at runtime, don't replace Claude Code, don't compete with IDEs.
- **New call (2026-06-01):** re-include the React + WebSocket human-in-the-loop approval UI.
- **Implication:** this is a PRD/BRIEF amendment, not a plan-level change. It lands in a **separate v0.2.0 train AFTER the v1.1 consolidation edition ships**. The BRIEF "must NOT do" list is amended to carve out the **opt-in approval UI**, which **MUST stay non-required** so the "function with zero MCPs / no required server" install promise still holds for users who do not enable it.

### D8 — Adopt native `skills:` frontmatter; retire `_built/` + `build/embed-skills.py` (reverses D1 mechanism, preserves D1 intent)

- **Prior decision:** D1 (Architecture C) embedded sub-agent skills via a build step producing `agents/<name>/_built/` bundles.
- **New call (2026-06-01):** adopt the official native `skills:` frontmatter field on agents — it does exactly what `_built/` did — and retire `_built/` + `build/embed-skills.py`.
- **Implication:** D1's intent is preserved (agents carry skills, cannot fail to load); only the mechanism changes. Change is **parity-gated** in Phase 2 Part B — a B0 parity preflight protects each cascade's `references/` before any deletion; Hybrid-fallback keeps `_built/` for cascade-heavy agents if native parity is not proven.

### D9 — Add `researcher` agent (native-`skills:` preloads research set; no reversal)

- **Finding:** the Phase 1 audit found 9/9 agents skill-loaded but NO dedicated research specialist; research piggybacked on the executor.
- **New call (2026-06-01):** add a `researcher` agent that preloads the research set via native `skills:` frontmatter (embeds `library-docs-fetch` + `codebase-analysis` + `observability-report`); `commands/research.md` is re-pointed to it.
