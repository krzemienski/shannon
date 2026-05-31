# Shannon v0.1.0 — Release checklist (user actions)

The sandbox build is complete. These steps require host-side execution (git, network, real Claude Code, etc.) and are handed off to the release operator.

## Prerequisite: sandbox structural PASS

Verified by Phase 7 PLAN.md and `.planning/phases/07-release/evidence/`:

- [x] `python3 build/embed-skills.py` exits 0
- [x] `python3 build/verify-build.py` reports 0 mismatches
- [x] `python3 scripts/doctor.py` reports 0 mismatches across 8 checks
- [x] `bash scripts/harness/run-all.sh --dry-run` both runners exit 0
- [x] All 6 phase VALIDATION.md files verdict=PASS

## Step 1 — Live release-candidate harness (user action)

Run on a machine with:
- Anthropic API key (`ANTHROPIC_API_KEY`)
- Claude Code CLI installed (`which claude` returns a path)
- `tmux` installed
- The Shannon plugin not yet installed (clean state)

```bash
# Optional: pip install the SDK first
pip install claude-agent-sdk pyyaml

cd v1/shannon
bash scripts/harness/run-all.sh --live
```

Expected: both runners exit 0; per-benchmark verdicts show `PASS` (not `SKIP`) for the 5 pillar benchmarks.

Save the output:

```bash
mkdir -p .planning/phases/07-release/evidence/live
mv .planning/phases/05-harnesses/evidence/sdk-live.json  .planning/phases/07-release/evidence/live/
mv .planning/phases/05-harnesses/evidence/tmux-live.json .planning/phases/07-release/evidence/live/
```

If any benchmark FAILed: do NOT ship. Investigate via `cat REFUSAL.md` (if present) or per-benchmark evidence file under `.planning/phases/05-harnesses/evidence/`. Re-run after fix.

## Step 2 — Git tag v0.1.0

```bash
cd <repo-root>
git add v1/shannon/
git commit -m "Shannon v0.1.0 — first release candidate

7 phases complete: PRD → skill curation → agent embedding → command
consolidation → hook curation → harnesses → docs. Doctor green.

See v1/shannon/RELEASE_NOTES.md."

git tag -a v0.1.0 -m "Shannon v0.1.0

Foundational standalone Claude Code plugin.

- 31 skills (curated from 67 candidates)
- 9 agents with Architecture C embedded skills
- 19 commands (consolidated from 27)
- 7 hooks (consolidated from 16) + required_hooks contract
- 5 pillar benchmarks; SDK + Tmux harnesses
- 8 documentation files
- scripts/doctor.py mechanical contract check
- 0 mismatches across all gates

See v1/shannon/RELEASE_NOTES.md for full notes."
```

## Step 3 — Push to public GitHub

```bash
git push origin main
git push origin v0.1.0
```

Verify on GitHub:

- [ ] Tag `v0.1.0` visible at `https://github.com/<owner>/shannon-framework/releases`
- [ ] `v1/shannon/README.md` renders correctly (table of commands, docs links work)
- [ ] `v1/shannon/docs/ARCHITECTURE.md` renders correctly (5-layer diagram)

## Step 4 — Marketplace publishing (when API supports it)

Until Claude Code marketplace publishing is widely available, document the local-directory install path as the canonical install:

```bash
# In Claude Code:
/plugin marketplace add krzemienski/shannon
/plugin install shannon
```

(The `krzemienski/shannon` GitHub-path-based marketplace declaration is what users will use once GitHub-hosted marketplaces are GA. Until then, `docs/INSTALL.md` documents the local-clone install path.)

## Step 5 — Post-release smoke test (user action)

On a fresh project on a fresh machine:

```bash
# In Claude Code:
/plugin marketplace add /path/to/shannon-framework
/plugin install shannon@shannon-framework

# Restart Claude Code
/shannon:enforce on
/shannon:doctor
```

Expected:

- [ ] All 8 doctor checks PASS
- [ ] mismatches: 0
- [ ] `/shannon:plan "test workflow"` opens the planner agent and produces a plan
- [ ] `/shannon:cook plans/<date>-test/` runs through executor with hooks firing (visible in `~/.claude/logs/shannon/hooks.jsonl`)

If all the above succeed: v0.1.0 is fully shipped.

## Rollback

If any post-release issue surfaces:

```bash
# Git
git tag -d v0.1.0
git push origin :refs/tags/v0.1.0

# Per-user
/plugin uninstall shannon@shannon-framework
```

## Communication

After successful ship:

- [ ] Update repo `README.md` (root) to point to v1/shannon
- [ ] Post a v0.1.0 announcement (Discord / Twitter / blog as relevant)
- [ ] Open the v0.2 milestone with the items from `RELEASE_NOTES.md` "Next" section

## Sign-off

Release operator: __________________
Date: __________________
All steps green: [ ] yes / [ ] no (cite specific failure)
