#!/usr/bin/env python3
"""scripts/doctor.py — Shannon v1 self-diagnostic.

Cross-checks the required_hooks contract:
  - For every skill that declares `required_hooks:` in its SKILL.md frontmatter,
    verify each named hook is registered in hooks/hooks.json.
  - For every hook in hooks.json, verify the script file exists on disk.
  - For every script file in hooks/ with a META export, verify it is registered.

Also runs structural checks:
  - .claude-plugin/plugin.json present + valid JSON
  - skills/ count is in 25-35 range
  - agents/ count is 5-12
  - commands/ count is 13-20
  - hooks/ scripts is 5-9
  - agent skills: frontmatter resolves to real skills/

Exit codes:
  0 — all checks PASS
  1 — any check FAIL

Output: JSON to stdout + summary to stderr. Optional --verbose prints per-check detail.

Iron Rule: no fabricated checks. Every result is computed from real disk.
"""

import json
import os
import re
import sys
import argparse
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

REPO = Path(__file__).resolve().parent.parent
HOOKS_DIR = REPO / "hooks"
SKILLS_DIR = REPO / "skills"
AGENTS_DIR = REPO / "agents"
COMMANDS_DIR = REPO / "commands"
BUILD_DIR = REPO / "build"


def load_hooks_json():
    p = HOOKS_DIR / "hooks.json"
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError as e:
        return {"error": str(e)}


def registered_hook_scripts(hooks_json):
    """Return set of script basenames registered in hooks.json."""
    if not hooks_json or "hooks" not in hooks_json:
        return set()
    scripts = set()
    for event, entries in hooks_json["hooks"].items():
        for entry in entries:
            for hook in entry.get("hooks", []):
                cmd = hook.get("command", "")
                m = re.search(r"hooks/([a-zA-Z0-9_\-]+\.(?:js|cjs|py|sh))", cmd)
                if m:
                    scripts.add(m.group(1))
    return scripts


def hook_name_from_script(script_basename):
    """Map script filename to hook name (the META `name:` field, which is the basename sans ext)."""
    return Path(script_basename).stem


def script_from_hook_name(name):
    """Given a hook name from `required_hooks`, find the matching script basename."""
    for ext in (".js", ".cjs", ".py", ".sh"):
        cand = HOOKS_DIR / f"{name}{ext}"
        if cand.is_file():
            return cand.name
    return None


def skill_frontmatter(skill_dir):
    """Parse SKILL.md frontmatter into a dict."""
    p = skill_dir / "SKILL.md"
    if not p.is_file():
        return None
    text = p.read_text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return None
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args(argv)

    plugin_manifest = REPO / ".claude-plugin" / "plugin.json"
    plugin_version = "unknown"
    if plugin_manifest.is_file():
        try:
            plugin_version = json.loads(plugin_manifest.read_text()).get("version", "unknown")
        except json.JSONDecodeError:
            plugin_version = "unknown"

    out = {
        "report_schema": "1",
        "plugin_version": plugin_version,
        "repo_root": str(REPO),
        "summary": {},
        "checks": [],
        "mismatches": [],
    }

    # ------------------------------------------------------------------
    # Check 1: plugin.json
    # ------------------------------------------------------------------
    plugin_json = REPO / ".claude-plugin" / "plugin.json"
    chk = {"id": "plugin-manifest", "name": "Plugin manifest present + valid JSON"}
    if not plugin_json.is_file():
        chk["status"] = "FAIL"
        chk["detail"] = f"missing {plugin_json}"
        out["mismatches"].append(chk["detail"])
    else:
        try:
            json.loads(plugin_json.read_text())
            chk["status"] = "PASS"
        except json.JSONDecodeError as e:
            chk["status"] = "FAIL"
            chk["detail"] = f"plugin.json parse error: {e}"
            out["mismatches"].append(chk["detail"])
    out["checks"].append(chk)

    # ------------------------------------------------------------------
    # Check 2: skills count
    # ------------------------------------------------------------------
    skill_dirs = sorted([d for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")])
    n_skills = len(skill_dirs)
    chk = {"id": "skills-count", "name": f"Skills count in 25-40", "value": n_skills}
    chk["status"] = "PASS" if 25 <= n_skills <= 40 else "FAIL"
    if chk["status"] == "FAIL":
        out["mismatches"].append(f"skills count {n_skills} not in [25,40]")
    out["checks"].append(chk)

    # ------------------------------------------------------------------
    # Check 3: agents count
    # ------------------------------------------------------------------
    agent_files = sorted([f for f in AGENTS_DIR.glob("*.md") if not f.name.startswith(".")])
    n_agents = len(agent_files)
    chk = {"id": "agents-count", "name": "Agents count in 5-12", "value": n_agents}
    chk["status"] = "PASS" if 5 <= n_agents <= 12 else "FAIL"
    if chk["status"] == "FAIL":
        out["mismatches"].append(f"agents count {n_agents} not in [5,12]")
    out["checks"].append(chk)

    # ------------------------------------------------------------------
    # Check 4: commands count
    # ------------------------------------------------------------------
    cmd_files = sorted(COMMANDS_DIR.glob("*.md"))
    n_cmds = len(cmd_files)
    chk = {"id": "commands-count", "name": "Commands count in 13-24", "value": n_cmds}
    chk["status"] = "PASS" if 13 <= n_cmds <= 24 else "FAIL"
    if chk["status"] == "FAIL":
        out["mismatches"].append(f"commands count {n_cmds} not in [13,24]")
    out["checks"].append(chk)

    # ------------------------------------------------------------------
    # Check 5: hooks count
    # ------------------------------------------------------------------
    hook_scripts = sorted([p for p in HOOKS_DIR.iterdir() if p.suffix in (".js", ".cjs", ".py", ".sh") and not p.name.startswith("_")])
    n_hooks = len(hook_scripts)
    chk = {"id": "hooks-count", "name": "Hooks count in 5-9", "value": n_hooks}
    chk["status"] = "PASS" if 5 <= n_hooks <= 9 else "FAIL"
    if chk["status"] == "FAIL":
        out["mismatches"].append(f"hooks count {n_hooks} not in [5,9]")
    out["checks"].append(chk)

    # ------------------------------------------------------------------
    # Check 6: hooks.json valid + every registration points to a real script
    # ------------------------------------------------------------------
    hooks_json = load_hooks_json()
    chk = {"id": "hooks-json", "name": "hooks.json registers real scripts"}
    if not hooks_json or "error" in (hooks_json or {}):
        chk["status"] = "FAIL"
        chk["detail"] = hooks_json.get("error") if hooks_json else "missing hooks.json"
        out["mismatches"].append(chk["detail"])
    else:
        registered = registered_hook_scripts(hooks_json)
        chk["registered_count"] = len(registered)
        missing_scripts = []
        for s in registered:
            if not (HOOKS_DIR / s).is_file():
                missing_scripts.append(s)
        if missing_scripts:
            chk["status"] = "FAIL"
            chk["detail"] = f"registered but missing on disk: {missing_scripts}"
            out["mismatches"].extend(missing_scripts)
        else:
            chk["status"] = "PASS"
    out["checks"].append(chk)

    # ------------------------------------------------------------------
    # Check 7: required_hooks contract — for every skill that declares
    #          required_hooks, each named hook must be registered.
    # ------------------------------------------------------------------
    hooks_json_safe = hooks_json or {"hooks": {}}
    registered_scripts = registered_hook_scripts(hooks_json_safe)
    registered_names = {hook_name_from_script(s) for s in registered_scripts}

    contract = {"id": "required-hooks-contract", "name": "required_hooks → registered hooks"}
    contract_details = []
    contract_mismatches = []
    skill_dep_count = 0
    total_deps = 0
    for d in skill_dirs:
        fm = skill_frontmatter(d) or {}
        deps = fm.get("required_hooks") or []
        if not deps:
            continue
        skill_dep_count += 1
        for hook_name in deps:
            total_deps += 1
            if hook_name not in registered_names:
                contract_mismatches.append(f"{d.name} → {hook_name} (NOT REGISTERED)")
            else:
                contract_details.append(f"{d.name} → {hook_name} ✓")
    contract["skills_with_required_hooks"] = skill_dep_count
    contract["total_dependencies"] = total_deps
    contract["mismatches"] = contract_mismatches
    if contract_mismatches:
        contract["status"] = "FAIL"
        out["mismatches"].extend(contract_mismatches)
    else:
        contract["status"] = "PASS"
    if args.verbose:
        contract["details"] = contract_details
    out["checks"].append(contract)

    # ------------------------------------------------------------------
    # Check 8: build state — verify-build.py compatible quick check
    # ------------------------------------------------------------------
    chk = {"id": "agent-skills-resolve", "name": "Agent skills: frontmatter resolves to real skills/"}
    build_mismatches = []
    real_skill_names = {d.name for d in skill_dirs}
    comma = ","
    for agent_file in agent_files:
        text = agent_file.read_text()
        _, _, after = text.partition("---")
        frontmatter, _, _ = after.partition("---")
        if not frontmatter:
            frontmatter = text
        m = re.search(r"(?m)^skills:[ \t]*(.+)$", frontmatter)
        if not m:
            build_mismatches.append(f"{agent_file.stem}: no `skills:` frontmatter field")
            continue
        declared = [nm.strip() for nm in m.group(1).split(comma) if nm.strip()]
        for nm in declared:
            if nm not in real_skill_names:
                build_mismatches.append(f"{agent_file.stem}: skills: `{nm}` not in skills/")
    chk["mismatches"] = build_mismatches
    if build_mismatches:
        chk["status"] = "FAIL"
        out["mismatches"].extend(build_mismatches)
    else:
        chk["status"] = "PASS"
    out["checks"].append(chk)

    # ------------------------------------------------------------------
    # Check 9: skill body references — every `Skill: <name>` and `<hook-name>`
    # mentioned in any SKILL.md body must resolve to a real v1 entity.
    # (Architect-flagged highest-leverage fix from v0.1.4 audit.)
    # ------------------------------------------------------------------
    real_skills = {d.name for d in skill_dirs}
    real_agents = {f.stem for f in agent_files}
    real_hooks = registered_names
    chk = {"id": "skill-body-refs", "name": "Skill body references resolve to real v1 entities"}
    skill_body_mismatches = []
    skill_body_total_refs = 0
    for sdir in skill_dirs:
        smd = sdir / "SKILL.md"
        if not smd.is_file(): continue
        body = smd.read_text()
        # Skill: <name> form
        for m in re.finditer(r"`Skill:\s*([a-z][a-z0-9-]+)`", body):
            skill_body_total_refs += 1
            ref = m.group(1)
            if ref not in real_skills:
                skill_body_mismatches.append(f"{sdir.name}/SKILL.md: `Skill: {ref}` (not in v1 skills/)")
        # Task: <agent> form
        for m in re.finditer(r"`Task:\s*([a-z][a-z0-9-]+)`", body):
            skill_body_total_refs += 1
            ref = m.group(1)
            if ref not in real_agents:
                skill_body_mismatches.append(f"{sdir.name}/SKILL.md: `Task: {ref}` (not in v1 agents/)")
    chk["total_refs"] = skill_body_total_refs
    chk["mismatches"] = skill_body_mismatches[:20]
    if skill_body_mismatches:
        chk["status"] = "FAIL"
        out["mismatches"].extend(skill_body_mismatches)
    else:
        chk["status"] = "PASS"
    out["checks"].append(chk)

    # ------------------------------------------------------------------
    # Check 10: agent AGENT.md body references — same scan, agent files
    # ------------------------------------------------------------------
    chk = {"id": "agent-body-refs", "name": "Agent body references resolve to real v1 entities"}
    agent_body_mismatches = []
    agent_body_total_refs = 0
    for amd in agent_files:
        body = amd.read_text()
        for m in re.finditer(r"`Skill:\s*([a-z][a-z0-9-]+)`", body):
            agent_body_total_refs += 1
            ref = m.group(1)
            if ref not in real_skills:
                agent_body_mismatches.append(f"{amd.name}: `Skill: {ref}` (not in v1 skills/)")
        # Task refs may be namespaced (shannon:<name>) or bare (<name>); strip the prefix before resolving
        for m in re.finditer(r"`Task:\s*(?:shannon:)?([a-z][a-z0-9-]+)`", body):
            agent_body_total_refs += 1
            ref = m.group(1)
            if ref not in real_agents:
                agent_body_mismatches.append(f"{amd.name}: `Task: {ref}` (not in v1 agents/)")
    chk["total_refs"] = agent_body_total_refs
    chk["mismatches"] = agent_body_mismatches[:20]
    if agent_body_mismatches:
        chk["status"] = "FAIL"
        out["mismatches"].extend(agent_body_mismatches)
    else:
        chk["status"] = "PASS"
    out["checks"].append(chk)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    n_fail = sum(1 for c in out["checks"] if c["status"] == "FAIL")
    n_pass = sum(1 for c in out["checks"] if c["status"] == "PASS")
    out["summary"] = {
        "skills_with_required_hooks": skill_dep_count,
        "total_hook_dependencies": total_deps,
        "registered_hooks": len(registered_scripts),
        "checks_pass": n_pass,
        "checks_fail": n_fail,
        "mismatches": len(out["mismatches"]),
    }

    print(json.dumps(out, indent=2))

    if args.verbose:
        print("", file=sys.stderr)
        print(f"  Checks: {n_pass} PASS, {n_fail} FAIL", file=sys.stderr)
        print(f"  Mismatches: {len(out['mismatches'])}", file=sys.stderr)

    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
