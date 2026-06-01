# skills10x — RUNBOOK (the exact thing you run)

Self-contained skill grading + improvement harness for the Shannon plugin. Grades
each skill with **real `claude -p` activation probes** + a fresh judge sub-agent,
improves the real `SKILL.md`, re-grades, proves non-regression, and atomically
commits each genuine win onto a dedicated branch. No external runner, no v6
native-activation regex engine — everything lives under `scripts/skills10x/`.

> The SOLE activation-truth source is `eval_skill.py` (real probes). The v6
> native-activation regex engine is deliberately NOT consulted.

---

## 1. Prerequisites (all hard — the harness fails loudly if any is missing)

| need | check |
|------|-------|
| `claude` CLI **authed** | `claude --version` then a 1-line `claude -p "say PONG"` returns `PONG` exit 0 |
| `tmux` | `tmux -V` |
| `python3` (stdlib only) | `python3 --version` |
| `jq` | `jq --version` |
| `git` repo, clean-ish | `git -C /Users/nick/Documents/shannon status` |
| `.skills10x/` gitignored | `git -C /Users/nick/Documents/shannon check-ignore .skills10x` prints `.skills10x` |

The orchestrator's `preflight` re-asserts every one of these and **refuses to
start** if `.skills10x/` is not gitignored (D10) — probe transcripts can contain
auth tokens / env vars / session secrets and must never become trackable.

---

## 2. The files

| file | role |
|------|------|
| `run-skills10x.sh`     | **the orchestrator you run** — worst-first loop, branch-safety, D9 pre-commit gate, atomic commits |
| `probe.sh`             | ONE real headless `claude -p --debug` probe under tmux → `.stdout`+`.debug.log`+`.meta.json` |
| `parse_probe.py`       | reads a probe's debug+stdout (+ session JSONL); `--expect S` → `{registered, activated, verdict}` |
| `discover_skills.py`   | enumerate every visible skill + frontmatter (pure stdlib) |
| `eval_skill.py`        | per-skill `{recall, precision, fp, f1}` from real probes; SOLE activation-truth source |
| `judge_rubric.md`      | 8-dimension design-quality rubric the judge sub-agent grades against |
| `skill_grade.py`       | merge eval F1 + judge JSON → grade; PASS = `f1≥0.90 AND rubric_min≥0.90 AND benched` |
| `regression_guards.py` | full-corpus BEFORE/AFTER non-regression gate; **FAIL-CLOSED** if baseline missing |

All run-time state + evidence lands under `.skills10x/` (gitignored).

---

## 3. Run commands (copy-paste)

```bash
cd /Users/nick/Documents/shannon

# A. DRY-RUN — baseline-grade every skill, write the worst-first SCOREBOARD.
#    No edits, no commits. Use this first to see where the floor is.
bash scripts/skills10x/run-skills10x.sh --dry-run
#    -> .skills10x/SCOREBOARD.md  (ranked low-F1 first)

# B. ONE skill end-to-end (recommended first real run — proves the loop).
#    Picks a real worst-first TRIGGER-BEARING skill (NOT a trigger-less one).
bash scripts/skills10x/run-skills10x.sh --only <skill>
#    -> branch skills/10x-<UTC-DATE>, ONE atomic commit if it genuinely improves

# C. FULL loop — improve every skill worst-first until all PASS or caps hit.
bash scripts/skills10x/run-skills10x.sh \
     --max-passes-per-skill 4 --max-global-passes 3
```

### Flags

| flag | default | meaning |
|------|---------|---------|
| `--only SKILL`              | (all)     | improve just one skill |
| `--dry-run`                 | off       | baseline-grade + SCOREBOARD only; no edits/commits |
| `--max-passes-per-skill N`  | 4         | retry cap per skill (revert+retry on regression / no-lift) |
| `--max-global-passes N`     | 3         | global convergence cap |
| `--skills-scope shannon\|all` | shannon | `shannon` = canonical `skills/` (33); `all` = every discovered skill |
| `--trials N`                | 3         | should-trigger probes per skill |
| `--controls N`              | 3         | should-NOT-fire probes per skill |

**Model:** inherits your default model. The harness passes **no** `--model` — it
matches the atlas `MODEL=inherit` lesson. Whatever your `claude` is configured to
use (e.g. the 1M model) is what probes/judge/improver run on.

---

## 4. What "improve" means (and what it must never do)

A pass is accepted **only** when, on the post-edit measurement:

```
grade_pass == true           # f1 ≥ 0.90 AND rubric_min ≥ 0.90 AND benched
AND  (f1_after - f1_before) ≥ MIN_LIFT (0.10)   # a real lift, not +0.001 noise
AND  regression_guards.py == PASS               # full-corpus, no sibling dropped
AND  D9 pre-commit gate == PASS                 # diff touches only this SKILL.md;
                                                # no secret / injection in the diff
```

If any conjunct fails → **revert the SKILL.md and retry** (up to the cap). The
loop edits the REAL `SKILL.md`; it **never** weakens a probe or the rubric to make
a number go up (Iron Rule + Shannon's own `no-fakes-discipline`).

**Trigger-less skills** (`create-meta-prompts`, `full-functional-audit`,
`gepetto`, `prompt-engineering-patterns`) score `f1=0, benched=false`. They are
**not** valid 1-skill proof targets: a `0 → anything` lift is meaningless and
"fixing" them means authoring `triggers:` into a shipped v1 product skill — a
deliberate, separately-reviewed content edit, not a smoke-test side effect.

---

## 5. Read-only & evidence safety (the exact flag string)

Every `claude -p` (probe AND judge) runs **read-only**:

```
claude -p "<prompt>" --debug-file <f> --debug skills --session-id <uuid> \
       --allowedTools Read Grep Glob
```

- **NO** `--dangerously-skip-permissions`, **NO** `--permission-mode=bypassPermissions`.
- `probe.sh` **refuses (exit 77)** if any bypass flag appears in caller args (D8).
- The improver step gets `Read Grep Glob Edit Write`, but the **D9 pre-commit
  gate** in `run-skills10x.sh` re-stages nothing until it confirms the diff
  touches **only** the target skill's own `SKILL.md` and passes a
  secret/prompt-injection scan. A wider diff → STOP, no commit.
- `.skills10x/` is gitignored. **Never** `git add -f .skills10x`. Verify with
  `git check-ignore .skills10x` before any run (D10).

---

## 6. Evidence locations

```
.skills10x/
  SCOREBOARD.md                 # worst-first baseline ranking (from --dry-run)
  scoreboard.tsv                # raw f1<TAB>skill rows
  eval_summary.before*.json     # eval_skill.py outputs (per phase / per --only)
  eval_summary.after*.json
  corpus_before.json            # full-corpus BEFORE (regression_guards input)
  corpus_after.json             # full-corpus AFTER
  <skill>/
    before.md  after.md         # SKILL.md before/after the edit
    diff.patch                  # unified diff of the accepted edit (non-empty)
    rubric-before.json          # judge sub-agent STRICT JSON
    rubric-after.json
    grade-before.json           # skill_grade.py merge (f1 + rubric → grade)
    grade-after.json            # shows the measured lift
    regression_guards.json      # PASS/FAIL per guard
    improver.log / improver.err # the improver sub-agent transcript
  SKILLS_10X_REPORT.md          # what improved / what stopped (always written)
  SUMMARY.md                    # ONLY on full success
  BLOCKER.md                    # written when the run did not fully succeed
  probes/ , *.stdout/.debug.log/.meta.json   # raw probe transcripts (secrets!)
```

Read a single skill's win:

```bash
jq '{f1:.activation.f1, pass:.grade_pass}' .skills10x/<skill>/grade-before.json
jq '{f1:.activation.f1, pass:.grade_pass}' .skills10x/<skill>/grade-after.json
cat .skills10x/<skill>/diff.patch
```

---

## 7. After the run — review & merge

Commits land on **`skills/10x-<UTC-DATE>` only**. `main` and the `v1.0.0` tag are
never touched, and **nothing is pushed**.

```bash
# inspect the per-skill atomic commits
git -C /Users/nick/Documents/shannon log --oneline main..skills/10x-$(date -u +%Y-%m-%d)

# review each diff (only SKILL.md files should appear)
git -C /Users/nick/Documents/shannon diff main..skills/10x-$(date -u +%Y-%m-%d) -- 'skills/**/SKILL.md'

# re-run doctor to confirm the plugin is still healthy
python3 /Users/nick/Documents/shannon/scripts/doctor.py; echo "doctor exit=$?"

# merge ONLY after human review (fast-forward or PR — your call). NOT automated.
git -C /Users/nick/Documents/shannon switch main
git -C /Users/nick/Documents/shannon merge --no-ff skills/10x-$(date -u +%Y-%m-%d)
```

The harness will **never** merge or push for you — the human gates the merge
(atlas 005/006 convention).

---

## 8. Troubleshooting

| symptom | cause / fix |
|---------|-------------|
| `refusing to run — .skills10x/ is NOT gitignored` | add `.skills10x/` to `.gitignore`, commit, re-run (D10) |
| `'claude' CLI not found` / probe exit≠0 | `claude` not authed or not on PATH; run `claude -p "say PONG"` to confirm |
| `regression_guards` FAIL-CLOSED | `corpus_before.json`/`corpus_after.json` missing or single-skill — a full-corpus eval must exist BEFORE and AFTER (D3) |
| improver made no change | the skill may already PASS, or the improver declined; check `improver.log` |
| `D9 STOP: staged diff touches more than` | the improver edited a second file; the loop refuses to commit and reverts — investigate `improver.log` |
| run is slow | each skill = `--trials + --controls` real probes × ~20-40 s; lower `--trials`/`--controls` for a faster (noisier) pass |
