#!/usr/bin/env bash
# run-skills10x.sh — Orchestrator for the self-contained skills-10x improvement loop.
#
# Grades and improves Shannon's skills using REAL `claude -p` activation probes
# (probe.sh) + a fresh judge sub-agent (judge_rubric.md), then atomically commits
# each genuinely-improved SKILL.md onto a dedicated branch. No external atlas
# runner, no v6 native-activation regex engine — the SOLE activation-truth source
# is eval_skill.py (real probes). See RUNBOOK.md for the human run procedure.
#
# THE LOOP (per skill S, worst-first):
#   baseline  : eval_skill.py (real F1) + judge sub-agent (rubric) -> grade-before
#   improve   : edit S's OWN SKILL.md (sharpen description/triggers, deepen
#               workflow, add examples + MUST/MUST-NOT gates, tighten tokens)
#   re-grade  : eval_skill.py (FRESH probes) + FRESH judge -> grade-after
#   guard     : regression_guards.py (full-corpus BEFORE vs AFTER) must PASS
#   commit    : ONE atomic git commit of S's SKILL.md onto skills/10x-<UTC-DATE>
#   on regression OR no lift: revert S, retry (cap --max-passes-per-skill)
#
# SAFETY INVARIANTS (hard):
#   - REFUSES to run on main/master without creating skills/10x-<UTC-DATE> first.
#   - NEVER pushes. NEVER touches the v1.0.0 tag. NEVER edits main.
#   - Every claude -p probe is READ-ONLY (probe.sh pins --allowedTools Read Grep
#     Glob and refuses --dangerously-skip-permissions). [D8]
#   - Pre-commit gate (D9): each commit diff must touch ONLY S's own SKILL.md and
#     must pass a secret / prompt-injection scan, else STOP-and-report (no commit).
#   - .skills10x/ must be gitignored before the first probe writes (D10).
#   - Improvement edits the REAL SKILL.md; NEVER weakens the rubric/probe to pass.
#
# Usage:
#   run-skills10x.sh [--only SKILL] [--dry-run] [--max-passes-per-skill N]
#                    [--max-global-passes N] [--skills-scope shannon|all]
#                    [--trials N] [--controls N] [--help]
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
HERE="$REPO_ROOT/scripts/skills10x"
STATE_DIR="$REPO_ROOT/.skills10x"
PASS_F1=0.90
# Minimum F1 lift that counts as a real improvement (must exceed judge/probe
# run-to-run noise; +0.001 noise is NOT an improvement). [D2]
MIN_LIFT=0.10

usage() { sed -n '2,52p' "$0" | sed 's/^# \{0,1\}//'; }

ONLY=""
DRY_RUN=0
MAX_PASSES_PER_SKILL=4
MAX_GLOBAL_PASSES=3
SKILLS_SCOPE="shannon"   # shannon = canonical skills/ only; all = every discovered skill
TRIALS=3
CONTROLS=3

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h) usage; exit 0 ;;
    --only) ONLY="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    --max-passes-per-skill) MAX_PASSES_PER_SKILL="$2"; shift 2 ;;
    --max-global-passes) MAX_GLOBAL_PASSES="$2"; shift 2 ;;
    --skills-scope) SKILLS_SCOPE="$2"; shift 2 ;;
    --trials) TRIALS="$2"; shift 2 ;;
    --controls) CONTROLS="$2"; shift 2 ;;
    *) echo "ERROR: unknown arg '$1' (try --help)" >&2; exit 64 ;;
  esac
done

log()  { printf '[skills10x] %s\n' "$*"; }
die()  { printf '[skills10x] FATAL: %s\n' "$*" >&2; exit 1; }

# ----------------------------------------------------------------------------
# Preflight: tools, repo, gitignore (D10), permission posture, branch safety.
# ----------------------------------------------------------------------------
preflight() {
  command -v claude  >/dev/null 2>&1 || die "'claude' CLI not on PATH (npm i -g @anthropic-ai/claude-code)"
  command -v tmux    >/dev/null 2>&1 || die "'tmux' not on PATH (brew/apt install tmux)"
  command -v python3 >/dev/null 2>&1 || die "'python3' not on PATH"
  command -v jq      >/dev/null 2>&1 || die "'jq' not on PATH (brew/apt install jq)"
  command -v git     >/dev/null 2>&1 || die "'git' not on PATH"
  [[ -f "$HERE/probe.sh" ]]          || die "probe.sh missing at $HERE"
  [[ -f "$HERE/eval_skill.py" ]]     || die "eval_skill.py missing at $HERE"
  [[ -f "$HERE/regression_guards.py" ]] || die "regression_guards.py missing at $HERE"
  [[ -f "$HERE/skill_grade.py" ]]    || die "skill_grade.py missing at $HERE"
  [[ -f "$HERE/judge_rubric.md" ]]   || die "judge_rubric.md missing at $HERE"

  git -C "$REPO_ROOT" rev-parse --git-dir >/dev/null 2>&1 || die "$REPO_ROOT is not a git repo"

  # D10: .skills10x/ MUST be gitignored before any probe writes secrets there.
  mkdir -p "$STATE_DIR"
  if ! git -C "$REPO_ROOT" check-ignore -q .skills10x; then
    die ".skills10x/ is NOT gitignored. Add '.skills10x/' to .gitignore before running (D10). Refusing to write probe transcripts that could leak auth tokens/secrets into a tracked dir."
  fi
  log ".skills10x/ is gitignored (D10 OK)"
}

# Create / switch to the dedicated improvement branch. REFUSE to run the
# mutating loop on main/master without branching. [branch-safety]
ensure_branch() {
  local utc_date branch cur
  utc_date="$(date -u +%Y-%m-%d)"
  branch="skills/10x-${utc_date}"
  cur="$(git -C "$REPO_ROOT" branch --show-current)"

  if [[ $DRY_RUN -eq 1 ]]; then
    log "dry-run: no branch change (current=$cur)"
    BRANCH="$cur"
    return 0
  fi

  if [[ "$cur" == "$branch" ]]; then
    log "already on $branch"
  elif git -C "$REPO_ROOT" show-ref --verify --quiet "refs/heads/$branch"; then
    git -C "$REPO_ROOT" switch "$branch" || die "could not switch to existing $branch"
    log "switched to existing $branch"
  else
    if [[ "$cur" == "main" || "$cur" == "master" ]]; then
      log "on $cur — creating $branch from HEAD (refuse to mutate $cur directly)"
    fi
    git -C "$REPO_ROOT" switch -c "$branch" || die "could not create $branch"
    log "created $branch from HEAD"
  fi
  BRANCH="$branch"
}

# Resolve the target skill list. shannon scope = canonical skills/ dir names.
target_skills() {
  if [[ -n "$ONLY" ]]; then echo "$ONLY"; return; fi
  if [[ "$SKILLS_SCOPE" == "shannon" ]]; then
    ls -d "$REPO_ROOT"/skills/*/ 2>/dev/null | xargs -n1 basename
  else
    python3 "$HERE/discover_skills.py" | jq -r '.skills[] | (.name // .dir_name)' | sort -u
  fi
}

# Build the `--only a,b,c` comma list for a full-corpus eval over the scope.
scope_only_csv() {
  if [[ "$SKILLS_SCOPE" == "shannon" ]]; then
    target_skills | paste -sd, -
  else
    echo ""   # empty = eval everything discover finds
  fi
}

# Dispatch a fresh judge sub-agent (read-only headless claude -p) to score ONE
# SKILL.md against judge_rubric.md. Writes STRICT JSON to $2. The judge is a
# Task-style grader; in headless mode the Skill tool is disabled, so we feed the
# rubric inline and require JSON-only output. [no rubric weakening]
judge_skill() {
  local skill_md="$1" out_json="$2" label="$3"
  local scratch promptf
  scratch="$(mktemp)"
  promptf="$(mktemp)"
  # Build the prompt in a tempfile (avoids $(cat <<EOF) apostrophe-parsing
  # pitfalls). Header is a quoted heredoc; rubric + SKILL.md are appended raw.
  cat > "$promptf" <<'HDR'
You are a STRICT skill-design judge. Score the SKILL.md below against the 8-dimension
rubric. Return ONLY strict minified JSON in the exact shape the rubric specifies
(keys: dimensions{8}, min, composite, notes). No prose, no markdown fences.

===== RUBRIC =====
HDR
  cat "$HERE/judge_rubric.md" >> "$promptf"
  printf '\n\n===== SKILL.md UNDER REVIEW =====\n' >> "$promptf"
  cat "$skill_md" >> "$promptf"
  # Read-only judge: allow Read/Grep/Glob only; no permission bypass. Capture the
  # raw reply, then extract the JSON object defensively.
  perl -e 'alarm 240; exec @ARGV' claude -p "$(cat "$promptf")" \
       --allowedTools Read Grep Glob >"$scratch" 2>>"$STATE_DIR/judge.$label.err" || true
  rm -f "$promptf"
  python3 - "$scratch" "$out_json" <<'PYEOF'
import sys, json, re
raw = open(sys.argv[1]).read()
m = re.search(r"\{.*\}", raw, re.DOTALL)
if not m:
    print("JUDGE_PARSE_FAIL", file=sys.stderr); sys.exit(3)
obj = json.loads(m.group(0))
# Normalize: ensure min/composite present.
dims = obj.get("dimensions", {})
if dims and "min" not in obj:
    obj["min"] = min(dims.values())
json.dump(obj, open(sys.argv[2], "w"), indent=2)
print("judge ok ->", sys.argv[2])
PYEOF
  rm -f "$scratch"
}

# D9 pre-commit gate: the staged diff must touch ONLY the target skill's own
# SKILL.md, and must pass a secret / prompt-injection scan. Returns 0 to allow,
# non-zero to STOP (no commit).
precommit_gate() {
  local skill="$1" skill_md_rel="skills/$skill/SKILL.md"
  local changed
  changed="$(git -C "$REPO_ROOT" diff --cached --name-only)"
  if [[ "$changed" != "$skill_md_rel" ]]; then
    log "D9 STOP: staged diff touches more than '$skill_md_rel':"
    printf '    %s\n' $changed
    return 2
  fi
  # Secret / injection scan over the staged additions only.
  local added
  added="$(git -C "$REPO_ROOT" diff --cached -- "$skill_md_rel" | grep '^+' | grep -v '^+++')"
  local hits
  hits="$(printf '%s\n' "$added" | grep -niE \
    'sk-[a-z0-9]{16,}|api[_-]?key|secret[_-]?key|password[[:space:]]*[:=]|bearer[[:space:]]+[a-z0-9._-]{12,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|ignore (all )?previous instructions|disregard (the )?(system|above)|--dangerously-skip-permissions' \
    || true)"
  if [[ -n "$hits" ]]; then
    log "D9 STOP: secret/injection scan flagged the diff:"
    printf '    %s\n' "$hits"
    return 3
  fi
  return 0
}

# Run a full-corpus eval (BEFORE or AFTER) for regression_guards. Honors scope.
corpus_eval() {
  local phase="$1" out_basename="$2"
  local csv; csv="$(scope_only_csv)"
  log "corpus eval phase=$phase scope=$SKILLS_SCOPE (this runs real probes; slow)"
  if [[ -n "$csv" ]]; then
    python3 "$HERE/eval_skill.py" --outdir "$STATE_DIR" --phase "$phase" \
            --only "$csv" --trials "$TRIALS" --controls "$CONTROLS"
  else
    python3 "$HERE/eval_skill.py" --outdir "$STATE_DIR" --phase "$phase" \
            --trials "$TRIALS" --controls "$CONTROLS"
  fi
  # eval_skill.py writes eval_summary.<phase>[-only_tag].json; normalize to a
  # stable corpus filename the guards consume.
  local produced
  produced="$(ls -t "$STATE_DIR"/eval_summary."$phase"*.json 2>/dev/null | head -1)"
  [[ -n "$produced" ]] || die "corpus eval produced no summary for phase=$phase"
  cp "$produced" "$STATE_DIR/$out_basename"
  log "corpus $phase -> $STATE_DIR/$out_basename"
}

# Grade ONE skill: eval (scoped to it) + judge -> grade-<phase>.json. Echoes the
# F1 to stdout (last line) for the caller.
grade_one() {
  local skill="$1" phase="$2"
  local sdir="$STATE_DIR/$skill"
  mkdir -p "$sdir"
  python3 "$HERE/eval_skill.py" --only "$skill" --outdir "$STATE_DIR" \
          --phase "$phase" --trials "$TRIALS" --controls "$CONTROLS" >/dev/null
  local evalsum
  evalsum="$(ls -t "$STATE_DIR"/eval_summary."$phase"-*"$skill"*.json 2>/dev/null | head -1)"
  [[ -n "$evalsum" ]] || evalsum="$(ls -t "$STATE_DIR"/eval_summary."$phase"*.json 2>/dev/null | head -1)"
  [[ -n "$evalsum" ]] || die "grade_one: no eval summary for $skill/$phase"

  judge_skill "$REPO_ROOT/skills/$skill/SKILL.md" "$sdir/rubric-$phase.json" "${skill}-${phase}"
  [[ -s "$sdir/rubric-$phase.json" ]] || die "grade_one: judge produced no rubric JSON for $skill/$phase"

  python3 "$HERE/skill_grade.py" "$skill" "$evalsum" \
          "$sdir/rubric-$phase.json" "$sdir/grade-$phase.json" >/dev/null
  jq -r '.activation.f1' "$sdir/grade-$phase.json"
}

# ----------------------------------------------------------------------------
# DRY-RUN: baseline-grade every target skill, write ranked SCOREBOARD. No edits,
# no commits. This is the worst-first planning pass.
# ----------------------------------------------------------------------------
dry_run() {
  log "DRY-RUN baseline over scope=$SKILLS_SCOPE (real probes, no edits/commits)"
  local skills; skills="$(target_skills)"
  : > "$STATE_DIR/scoreboard.tsv"
  while read -r s; do
    [[ -n "$s" ]] || continue
    local f1; f1="$(grade_one "$s" before || echo 0.0)"
    printf '%s\t%s\n' "$f1" "$s" >> "$STATE_DIR/scoreboard.tsv"
    log "baseline $s f1=$f1"
  done <<< "$skills"

  {
    echo "# SCOREBOARD — worst-first baseline (real claude -p F1)"
    echo "_generated: $(date -u +%Y-%m-%dT%H:%M:%SZ) — scope: $SKILLS_SCOPE_"
    echo
    echo "| rank | f1 | skill |"
    echo "|------|----|-------|"
    sort -n "$STATE_DIR/scoreboard.tsv" | nl -w2 -s'|' | \
      awk -F'\t' '{split($1,a,"|"); printf "| %s | %s | %s |\n", a[1], a[2], $2}'
  } > "$STATE_DIR/SCOREBOARD.md"
  log "SCOREBOARD -> $STATE_DIR/SCOREBOARD.md"
  cat "$STATE_DIR/SCOREBOARD.md"
}

# ----------------------------------------------------------------------------
# IMPROVE ONE skill end-to-end. Returns 0 on a committed improvement, 1 if it
# could not be improved (left clean), 2 on a hard stop (D9 / regression).
# NOTE: the actual SKILL.md rewrite is performed by the human operator or a
# dedicated improver sub-agent BETWEEN baseline and re-grade. This orchestrator
# drives the measurement, gates, and atomic commit; it does not invent prose.
# When run unattended it invokes an improver claude -p (read+write to the single
# SKILL.md only) — see improve_skill_md().
# ----------------------------------------------------------------------------
improve_one() {
  local skill="$1"
  local sdir="$STATE_DIR/$skill"
  local skill_md="$REPO_ROOT/skills/$skill/SKILL.md"
  mkdir -p "$sdir"
  [[ -f "$skill_md" ]] || { log "skip $skill: no SKILL.md"; return 1; }

  cp "$skill_md" "$sdir/before.md"
  log "[$skill] baseline grade…"
  local f1_before; f1_before="$(grade_one "$skill" before)"
  local pass_before; pass_before="$(jq -r '.grade_pass' "$sdir/grade-before.json")"
  log "[$skill] before: f1=$f1_before pass=$pass_before"
  if [[ "$pass_before" == "true" ]]; then
    log "[$skill] already PASSes — nothing to do"
    return 1
  fi

  # D3: capture the full-corpus BEFORE baseline NOW, while the ORIGINAL SKILL.md is
  # still on disk (before any edit). Capturing it after the edit would compare
  # edited-vs-edited and silently defeat the non-regression guard.
  log "[$skill] capturing full-corpus BEFORE baseline (pre-edit)…"
  corpus_eval before corpus_before.json

  local pass=0
  while [[ $pass -lt $MAX_PASSES_PER_SKILL ]]; do
    pass=$((pass + 1))
    log "[$skill] improve pass $pass/$MAX_PASSES_PER_SKILL"
    improve_skill_md "$skill" "$skill_md" "$sdir" || { log "[$skill] improver produced no change"; continue; }

    if ! diff -q "$sdir/before.md" "$skill_md" >/dev/null; then
      diff -u "$sdir/before.md" "$skill_md" > "$sdir/diff.patch" || true
    else
      log "[$skill] no diff after pass $pass"; continue
    fi

    cp "$skill_md" "$sdir/after.md"
    log "[$skill] re-grade (fresh probes)…"
    local f1_after; f1_after="$(grade_one "$skill" after)"
    local pass_after; pass_after="$(jq -r '.grade_pass' "$sdir/grade-after.json")"
    local lift; lift="$(python3 -c "print(round(${f1_after}-${f1_before},3))")"
    log "[$skill] after: f1=$f1_after pass=$pass_after lift=$lift (min_lift=$MIN_LIFT)"

    # Require a real measured lift exceeding noise floor, AND a PASS grade. [D2]
    local lift_ok; lift_ok="$(python3 -c "print(1 if ${lift} >= ${MIN_LIFT} else 0)")"
    if [[ "$pass_after" != "true" || "$lift_ok" != "1" ]]; then
      log "[$skill] pass $pass did not clear PASS+min_lift — revert + retry"
      cp "$sdir/before.md" "$skill_md"
      continue
    fi

    # Full-corpus non-regression gate (D3). The BEFORE corpus was captured pre-edit
    # above; capture the AFTER corpus now (reflects the edited skill on disk).
    log "[$skill] regression guards (full-corpus before/after)…"
    corpus_eval after corpus_after.json
    if ! python3 "$HERE/regression_guards.py" \
           --before "$STATE_DIR/corpus_before.json" \
           --after  "$STATE_DIR/corpus_after.json" \
           --edited "$skill" --json > "$sdir/regression_guards.json"; then
      log "[$skill] REGRESSION detected — revert + retry"
      cp "$sdir/before.md" "$skill_md"
      continue
    fi
    log "[$skill] regression guards PASS"

    # Atomic commit — D9 gate first.
    git -C "$REPO_ROOT" add "skills/$skill/SKILL.md"
    if ! precommit_gate "$skill"; then
      log "[$skill] D9 pre-commit gate FAILED — STOP (no commit). Unstaging."
      git -C "$REPO_ROOT" reset -q HEAD "skills/$skill/SKILL.md"
      cp "$sdir/before.md" "$skill_md"
      return 2
    fi
    git -C "$REPO_ROOT" commit -q -m "skills(10x): improve ${skill} (f1 ${f1_before}->${f1_after}, +${lift})

Activation F1 measured via real claude -p probes (eval_skill.py); design rubric
re-scored by fresh judge. Non-regression verified full-corpus (regression_guards).
Read-only probes; no rubric/probe weakening." || { log "[$skill] commit failed"; return 2; }
    log "[$skill] COMMITTED on $BRANCH (f1 $f1_before->$f1_after, +$lift)"
    return 0
  done

  log "[$skill] exhausted $MAX_PASSES_PER_SKILL passes without a clean improvement"
  cp "$sdir/before.md" "$skill_md"
  return 1
}

# Unattended improver: a read+write claude -p scoped to a SINGLE SKILL.md. It may
# ONLY edit that one file. Honors the 8 rubric dimensions; never weakens any
# probe/rubric. If you prefer an attended edit, edit the SKILL.md by hand between
# `grade_one before` and re-grade — improve_one detects the diff either way.
improve_skill_md() {
  local skill="$1" skill_md="$2" sdir="$3"
  local promptf; promptf="$(mktemp)"
  # Header via a quoted heredoc with a placeholder for the skill path, then the
  # rubric appended raw. Avoids $(cat <<EOF) apostrophe-parsing pitfalls.
  cat > "$promptf" <<HDR
Improve EXACTLY this one skill file and NOTHING else: $skill_md
You may use Read on $skill_md and 2-3 sibling SKILL.md files for house-style
calibration, then Edit/Write ONLY $skill_md. Do not touch any other file.

Goal: raise this skills design grade so every one of the 8 rubric dimensions
scores >= 0.90 AND its real activation F1 rises. Concretely:
 - Make the frontmatter description third-person, directive, trigger-forward
   (ALWAYS use when ...), naming concrete trigger phrases a user would type.
 - Ensure a real, comprehensive triggers: block (terse + natural phrasings),
   disambiguated from sibling skills. Never invent junk triggers to game a probe.
 - Tighten workflow steps, add a concrete example incl. one edge case, add
   explicit MUST / MUST-NOT gates, and cut filler.
 - Keep the frontmatter name == directory name ($skill). Valid YAML. No broken links.
NEVER weaken any rubric or probe. Output a short summary of what you changed.

===== RUBRIC (target) =====
HDR
  cat "$HERE/judge_rubric.md" >> "$promptf"
  # Improver gets Edit/Write but ONLY because precommit_gate (D9) enforces the
  # single-file invariant before any commit. Still NO permission bypass.
  perl -e 'alarm 360; exec @ARGV' claude -p "$(cat "$promptf")" \
       --allowedTools "Read" "Grep" "Glob" "Edit" "Write" \
       >"$sdir/improver.log" 2>>"$sdir/improver.err" || true
  rm -f "$promptf"
  return 0
}

# ----------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------
preflight
ensure_branch

if [[ $DRY_RUN -eq 1 ]]; then
  dry_run
  log "dry-run complete. SCOREBOARD at $STATE_DIR/SCOREBOARD.md"
  exit 0
fi

# Determine worst-first order. If --only, that is the single target. Otherwise
# run a dry-run baseline first to rank, then improve worst-first.
declare -a ORDER
if [[ -n "$ONLY" ]]; then
  ORDER=("$ONLY")
else
  dry_run
  while read -r line; do
    s="$(printf '%s' "$line" | cut -f2)"
    [[ -n "$s" ]] && ORDER+=("$s")
  done < <(sort -n "$STATE_DIR/scoreboard.tsv")
fi

GLOBAL=0
IMPROVED=()
STOPPED=()
while [[ $GLOBAL -lt $MAX_GLOBAL_PASSES ]]; do
  GLOBAL=$((GLOBAL + 1))
  log "=== global pass $GLOBAL/$MAX_GLOBAL_PASSES ==="
  any_change=0
  for s in "${ORDER[@]}"; do
    # Capture improve_one's exit without aborting the loop. The script runs under
    # `set -uo pipefail` (no -e), so a non-zero rc here is already non-fatal; we
    # just record it. Do NOT flip on errexit.
    improve_one "$s"; rc=$?
    case $rc in
      0) IMPROVED+=("$s"); any_change=1 ;;
      2) STOPPED+=("$s") ;;
    esac
  done
  [[ $any_change -eq 0 ]] && { log "no changes this global pass — converged"; break; }
done

# Reporting. SUMMARY.md only on full success (no stops, at least one improvement
# and every target now PASSes); otherwise BLOCKER.md.
{
  echo "# SKILLS_10X_REPORT"
  echo "_generated: $(date -u +%Y-%m-%dT%H:%M:%SZ) — branch: $BRANCH_"
  echo
  echo "## Improved (committed)"
  printf '  - %s\n' "${IMPROVED[@]:-（none）}"
  echo
  echo "## Stopped (D9 / regression — NOT committed)"
  printf '  - %s\n' "${STOPPED[@]:-（none）}"
  echo
  echo "See .skills10x/SCOREBOARD.md for the worst-first baseline and"
  echo "per-skill grade-before.json / grade-after.json for measured F1 lift."
} > "$STATE_DIR/SKILLS_10X_REPORT.md"
log "report -> $STATE_DIR/SKILLS_10X_REPORT.md"

if [[ ${#STOPPED[@]} -eq 0 && ${#IMPROVED[@]} -gt 0 ]]; then
  {
    echo "# SUMMARY — skills-10x run on $BRANCH"
    echo
    echo "Improved + committed (atomic, one commit each):"
    printf '  - %s\n' "${IMPROVED[@]}"
    echo
    echo "All commits on $BRANCH. main + v1.0.0 untouched. Nothing pushed."
    echo "Merge after review per RUNBOOK.md."
  } > "$STATE_DIR/SUMMARY.md"
  log "SUCCESS — SUMMARY at $STATE_DIR/SUMMARY.md"
  exit 0
else
  {
    echo "# BLOCKER — skills-10x run did not fully succeed"
    echo
    echo "Improved: ${IMPROVED[*]:-none}"
    echo "Stopped (D9/regression): ${STOPPED[*]:-none}"
    echo
    echo "Inspect .skills10x/<skill>/{grade-before,grade-after,regression_guards}.json"
    echo "and improver.log. No SUMMARY.md is written unless the run fully succeeds."
  } > "$STATE_DIR/BLOCKER.md"
  log "INCOMPLETE — BLOCKER at $STATE_DIR/BLOCKER.md"
  exit 1
fi
