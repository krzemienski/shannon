# Inventory Template

> Format for the structured inventory that drives every later phase of full-ui-experience-audit. Each row is one interaction; each interaction has a stable ID across cycles.

## The inventory format

```markdown
# Cycle-NN Inventory

Generated: 2026-05-28T10:00:00Z
Source: audit-evidence/codebase.xml (or repomix output)
Total interactions: 47

| ID | Screen / View | Interaction | Trigger | Backend dep | Priority |
|----|---------------|-------------|---------|-------------|----------|
| I001 | Dashboard | Click "New Session" button | tap/click | POST /api/sessions | P0 |
| I002 | Dashboard | View session list | render | GET /api/sessions | P0 |
| I003 | Dashboard | Delete session (swipe action) | swipe left | DELETE /api/sessions/:id | P1 |
| I004 | Dashboard | Pull-to-refresh | gesture | GET /api/sessions | P1 |
| I005 | Dashboard | Tap session card | tap | GET /api/sessions/:id | P0 |
| ... |
```

The columns:
- **ID**: stable across cycles (I001 in cycle 1 = I001 in cycle 5)
- **Screen / View**: which top-level UI surface
- **Interaction**: what the user does
- **Trigger**: input modality (tap, click, hover, gesture, keyboard, deep-link)
- **Backend dep**: API endpoint if the interaction hits the backend
- **Priority**: P0 (core flow) / P1 (secondary) / P2 (edge case)

## ID stability rules

**Once assigned, an ID never changes.** This is what makes stuck-state
detection work across cycles.

- Cycle 1: discovers I001-I047
- Cycle 2: discovers new interaction I048; existing I001-I047 keep their numbers
- Cycle 3: existing interaction I013 was removed by Phase 4 fix; mark it
  REMOVED but don't renumber
- Cycle 4: another new interaction I049

Inventory diffs across cycles use `+` (added), `-` (removed), `~` (modified):

```
| I048 | Settings | Toggle dark mode | tap | none | P1 | +cycle-2 |
| I013 | Dashboard | (removed: feature flag X disabled) | | | | -cycle-3 |
| I007 | Dashboard | Filter sessions | tap | GET /api/sessions?filter=... | P1 | ~cycle-2 (backend dep updated) |
```

## Priority assignment

| P | Criterion |
|---|-----------|
| P0 | Core user flow — task is incomplete without this working |
| P1 | Secondary flow — important but not blocking |
| P2 | Edge case / power-user / admin |

Priority drives Phase 4 fix order: P0 findings fixed first.

## Discovery sources

The inventory is discovered from:

1. **Top-level view / route map** — every `View`, `Page`, `Route`, `URL path`
2. **In-view grep** — find `Button`, `Tappable`, `onClick`, `onPress`, action handlers
3. **Backend route registry** — every route the backend exposes, cross-referenced with frontend calls
4. **Gesture handlers** — swipe, drag, long-press, double-tap
5. **Deep links / URL schemes** — anything reachable via URL
6. **Context menus / right-click / long-press menus**

Use `repomix` output OR direct `grep`/`Glob` to scan. The discovery is the same as `full-functional-audit`'s Phase 1.

## findings.json (companion file)

Alongside `inventory.md`, open a `findings.json` for the cycle. Each Phase 2
(UX audit) and Phase 3 (functional) finding gets an entry:

```json
{
  "cycle": 1,
  "findings": [
    {
      "id": "F-c01-001",
      "interaction_id": "I007",
      "phase": "ux | functional | discovery",
      "severity": "CRITICAL | HIGH | MEDIUM | LOW",
      "category": "visual | interactive | content | functional | accessibility",
      "summary": "Filter dropdown clips off-screen on narrow viewports",
      "evidence": ["audit-evidence/cycle-01/dashboard-filter-clipped.png"],
      "discovered_at": "2026-05-28T10:15:00Z",
      "status": "open | remediated | confirmed-fixed",
      "remediation_commit": null
    },
    ...
  ]
}
```

Finding IDs are also stable across cycles: F-c01-001 in cycle 1 stays
F-c01-001 even if remediated in cycle 2.

## Stuck-state detection (uses inventory IDs)

A stuck state = same set of open finding IDs for 2 consecutive cycles.

```
Cycle 5: open findings = [F-c01-003, F-c02-008, F-c03-014]
Cycle 6: open findings = [F-c01-003, F-c02-008, F-c03-014]  ← same set
        → STUCK STATE → escalate to user
```

If IDs weren't stable, this check would fail to detect stuck-state.

## Inventory hygiene

Per cycle:
1. Don't redo discovery from scratch — refresh the prior inventory
2. New interactions get NEW IDs (next available number)
3. Removed interactions stay in the inventory with REMOVED marker (don't delete)
4. Modified interactions update the row but keep the ID
5. Save `cycle-NN/inventory.md` AND `cycle-NN/findings.json` per cycle

## Example: 3-cycle inventory progression

```
Cycle 1 inventory (47 interactions, all newly discovered):
  I001..I047

Cycle 1 findings (12):
  F-c01-001..F-c01-012  (10 in Phase 2, 2 in Phase 3)

Cycle 1 Phase 4 remediates 10 of 12, leaving 2 carried to cycle 2.

Cycle 2 inventory (48 interactions: I001-I047 retained, I048 new from a Phase 4 fix):
  I001..I048

Cycle 2 findings (5 new + 2 carried = 7 open):
  F-c02-001..F-c02-005 (new)
  F-c01-008, F-c01-011 (carried)

Cycle 2 Phase 4 remediates 6 of 7, leaving 1 carried to cycle 3.

Cycle 3 inventory (48, no change):
  I001..I048

Cycle 3 findings (0 new + 1 carried = 1 open):
  F-c01-011 (carried — second cycle in a row)

Cycle 3 Phase 4 remediates F-c01-011.

Cycle 4 = clean confirmation pass:
  No new findings → PASS verdict.
```

## Cross-references

- `skills/full-ui-experience-audit/` — parent skill
- `references/phase-0-setup.md` — what runs before inventory
- `references/visual-experience-audit.md` — what reads inventory in Phase 2
- `references/fix-loop-protocol.md` — what closes findings in Phase 4
- `skills/full-functional-audit/` — companion skill with similar inventory pattern
