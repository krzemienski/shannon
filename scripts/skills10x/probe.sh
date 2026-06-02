#!/usr/bin/env bash
# probe.sh — One real headless `claude -p --debug` activation probe, under tmux.
#
# Vendored + adapted from skill-sentinel/skills/skill-activation-audit/scripts/
# run_headless_probe.sh. Self-contained inside the Shannon plugin repo: no atlas
# runner, no v6 native-activation regex engine, no external-framework dependency.
#
# WHY tmux: headless `claude -p` can buffer/stall on some shells and CI; running
# it inside a detached tmux pane gives a reliable PTY, lets us time it, and lets
# the harness run many probes without interleaving output.
#
# Usage:
#   probe.sh --prompt "PROMPT TEXT" --label probe1 --outdir DIR [extra claude args...]
#   probe.sh --help
#
# Output files (in OUTDIR):
#   <label>.stdout        full model stdout (the visible reply)
#   <label>.debug.log     full stderr/--debug stream (skill load + activation traces)
#   <label>.meta.json     exit code, duration, prompt, claude version, session jsonl path
#   <label>.session-id    the deterministic session UUID used for this probe
#
# READ-ONLY SAFETY (D8): this probe NEVER passes --dangerously-skip-permissions
# and refuses to run if the caller smuggles it into EXTRA_ARGS. The loop fans out
# over many skills autonomously; a permission-bypassed claude could execute
# arbitrary Write/Edit/Bash with no human gate. We pin an explicit minimal
# read-only posture instead. The exact flag string is asserted below and
# documented in RUNBOOK.md.
#
# Iron Rule: this runs the REAL claude binary against REAL skills. No mock model,
# no fixture logs. If claude/tmux isn't installed/authed, the probe FAILS loudly.
set -uo pipefail

usage() {
  sed -n '2,40p' "$0" | sed 's/^# \{0,1\}//'
}

PROMPT=""
LABEL="probe"
OUTDIR="./.skills10x/probes"
EXTRA_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h) usage; exit 0 ;;
    --prompt) PROMPT="$2"; shift 2 ;;
    --label)  LABEL="$2"; shift 2 ;;
    --outdir) OUTDIR="$2"; shift 2 ;;
    --) shift; EXTRA_ARGS+=("$@"); break ;;
    *) EXTRA_ARGS+=("$1"); shift ;;
  esac
done

if [[ -z "$PROMPT" ]]; then
  echo "ERROR: --prompt is required (try --help)" >&2
  exit 64
fi

# --- D8 read-only guard: refuse any permission-bypass in caller args ---------
for a in "${EXTRA_ARGS[@]:-}"; do
  case "$a" in
    --dangerously-skip-permissions|--permission-mode=bypassPermissions|bypassPermissions)
      echo "ERROR: refusing to run — permission-bypass flag '$a' is forbidden in probe.sh." >&2
      echo "  The skills-10x loop runs autonomously; probes MUST stay read-only." >&2
      exit 77 ;;
  esac
done

# --- preflight: prove the real system exists --------------------------------
if ! command -v claude >/dev/null 2>&1; then
  echo "ERROR: 'claude' CLI not found on PATH. Install Claude Code first." >&2
  echo "  npm install -g @anthropic-ai/claude-code" >&2
  exit 69
fi
if ! command -v tmux >/dev/null 2>&1; then
  echo "ERROR: 'tmux' not found on PATH. Install tmux first (brew/apt install tmux)." >&2
  exit 69
fi

mkdir -p "$OUTDIR"
OUTDIR="$(cd "$OUTDIR" && pwd)"
STDOUT_FILE="$OUTDIR/$LABEL.stdout"
DEBUG_FILE="$OUTDIR/$LABEL.debug.log"
META_FILE="$OUTDIR/$LABEL.meta.json"
DONE_FILE="$OUTDIR/$LABEL.done"
rm -f "$STDOUT_FILE" "$DEBUG_FILE" "$META_FILE" "$DONE_FILE"

CLAUDE_VERSION="$(claude --version 2>/dev/null | head -n1)"
SESSION="skills10x_${LABEL}_$$"
START_TS="$(date +%s)"

# Read-only posture (D8): allowlist Read/Grep/Glob only. Skill REGISTRATION
# traces go to --debug-file; skill ACTIVATION (Skill tool-use) is recorded in the
# session JSONL keyed by --session-id, which parse_probe.py reads. -p = headless
# print mode. We DO NOT pass --dangerously-skip-permissions; --allowedTools pins
# a minimal read-only set so an autonomous probe can never mutate the repo.
#
# SUBAGENT CONTAINMENT (safety fix 2026-06-02): --allowedTools bounds the MAIN
# agent, but a probed AUTONOMY skill (autopilot/ralph/team/cook/loop/dispatch)
# can instruct the model to spawn Task/Agent subagents whose own tool scope is
# NOT inherited from the parent allowlist — those workers then run Edit/Write/Bash
# and mutate real state in an unbounded loop. We therefore explicitly DENY the
# mutation + subagent-spawn tools. Activation is still measured (debug log +
# session JSONL Skill tool-use); denying the *consequence* tools does not change
# whether the skill fires, only whether it can act. PROBE_DENY is overridable but
# defaults to the full hazardous set.
SESSION_UUID="$(python3 -c 'import uuid; print(uuid.uuid4())')"
echo "$SESSION_UUID" > "$OUTDIR/$LABEL.session-id"
PROBE_DENY="${PROBE_DENY:-Edit Write MultiEdit NotebookEdit Bash Task Agent Workflow Monitor}"
read -r -d '' RUNNER <<EOF
claude -p $(printf '%q' "$PROMPT") \
  --debug-file $(printf '%q' "$DEBUG_FILE") \
  --debug skills \
  --session-id $(printf '%q' "$SESSION_UUID") \
  --allowedTools Read Grep Glob \
  --disallowedTools ${PROBE_DENY} \
  ${EXTRA_ARGS[*]:-} \
  > $(printf '%q' "$STDOUT_FILE") 2>> $(printf '%q' "$DEBUG_FILE")
echo \$? > $(printf '%q' "$DONE_FILE")
EOF

# Launch detached so we can monitor and time it.
tmux new-session -d -s "$SESSION" "bash -lc $(printf '%q' "$RUNNER")"

# Poll for completion with a hard ceiling (default 120s; override PROBE_TIMEOUT).
# An activation probe only needs the skill to FIRE (seconds), not to complete any
# work — so a tight ceiling is correct and also caps the blast radius if a probed
# skill tries to do real work despite the deny-list above.
TIMEOUT="${PROBE_TIMEOUT:-120}"
ELAPSED=0
while [[ ! -f "$DONE_FILE" ]]; do
  sleep 2
  ELAPSED=$((ELAPSED + 2))
  if [[ $ELAPSED -ge $TIMEOUT ]]; then
    tmux kill-session -t "$SESSION" 2>/dev/null
    echo "-1" > "$DONE_FILE"
    echo "TIMEOUT after ${TIMEOUT}s" >> "$DEBUG_FILE"
    break
  fi
  # Bail early if the tmux session died without writing DONE (crash).
  if ! tmux has-session -t "$SESSION" 2>/dev/null && [[ ! -f "$DONE_FILE" ]]; then
    echo "127" > "$DONE_FILE"
    echo "SESSION DIED before completion" >> "$DEBUG_FILE"
    break
  fi
done

EXIT_CODE="$(cat "$DONE_FILE" 2>/dev/null || echo "??")"
END_TS="$(date +%s)"
DURATION=$((END_TS - START_TS))
tmux kill-session -t "$SESSION" 2>/dev/null

# Emit metadata as JSON. Includes session JSONL path so parse_probe.py can read
# Skill tool-use events (the real activation signal in claude 2.1.x).
python3 - "$META_FILE" "$LABEL" "$EXIT_CODE" "$DURATION" "$CLAUDE_VERSION" "$PROMPT" "$SESSION_UUID" <<'PYEOF'
import json, sys, os, glob
meta_file, label, exit_code, duration, version, prompt, session_uuid = sys.argv[1:8]
home = os.path.expanduser("~")
candidates = glob.glob(f"{home}/.claude/projects/*/{session_uuid}.jsonl")
session_jsonl = candidates[0] if candidates else ""
json.dump({
    "label": label,
    "exit_code": exit_code,
    "duration_seconds": int(duration),
    "claude_version": version,
    "prompt": prompt,
    "session_uuid": session_uuid,
    "session_jsonl": session_jsonl,
    "read_only": True,
}, open(meta_file, "w"), indent=2)
PYEOF

echo "PROBE '$LABEL' done: exit=$EXIT_CODE duration=${DURATION}s"
echo "  stdout: $STDOUT_FILE"
echo "  debug:  $DEBUG_FILE"
echo "  meta:   $META_FILE"
[[ "$EXIT_CODE" == "0" ]] || exit 1
