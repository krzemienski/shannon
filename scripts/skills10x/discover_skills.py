#!/usr/bin/env python3
"""
discover_skills.py — Enumerate every Claude Code skill visible to the current user.

Vendored from skill-sentinel/skills/skill-activation-audit/scripts/discover_skills.py.
Pure stdlib, no third-party deps and no external engine — fully
self-contained inside this plugin repo. The universal substrate eval_skill.py builds on.

Scans, in order:
  1. Personal : ~/.claude/skills/<name>/SKILL.md
  2. Project  : <cwd>/.claude/skills/<name>/SKILL.md (walks up to git root)
  3. Plugins  : ~/.claude/plugins/**/skills/<name>/SKILL.md (marketplace + local)

Emits a JSON inventory to stdout.
"""
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(text):
    """Return (frontmatter_dict, body_str, raw_frontmatter_str, parse_ok)."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text, "", False
    raw = m.group(1)
    body = text[m.end():]
    fm = {}
    current_key = None
    for line in raw.splitlines():
        if not line.strip():
            continue
        km = re.match(r"^([A-Za-z0-9_-]+):\s?(.*)$", line)
        if km and not line.startswith((" ", "\t")):
            current_key = km.group(1)
            val = km.group(2).strip()
            fm[current_key] = val
        elif current_key is not None:
            fm[current_key] = (fm[current_key] + " " + line.strip()).strip()
    for k, v in list(fm.items()):
        if isinstance(v, str) and len(v) >= 2 and v[0] in "\"'" and v[-1] == v[0]:
            fm[k] = v[1:-1]
    return fm, body, raw, True


def git_root(start):
    p = Path(start).resolve()
    for parent in [p, *p.parents]:
        if (parent / ".git").exists():
            return parent
    return None


def scan_dir(skills_dir, source_label, namespace=None):
    found = []
    if not skills_dir.is_dir():
        return found
    for entry in sorted(skills_dir.iterdir()):
        skill_md = entry / "SKILL.md"
        if not (entry.is_dir() and skill_md.is_file()):
            continue
        try:
            text = skill_md.read_text(encoding="utf-8", errors="replace")
        except Exception as e:  # noqa: BLE001
            found.append({
                "dir_name": entry.name, "source": source_label,
                "path": str(skill_md), "read_error": str(e),
            })
            continue
        fm, body, raw_fm, ok = parse_frontmatter(text)
        name = fm.get("name", "")
        desc = fm.get("description", "")
        record = {
            "dir_name": entry.name,
            "name": name,
            "source": source_label,
            "namespace": namespace,
            "path": str(skill_md),
            "description": desc,
            "description_chars": len(desc),
            "body_lines": body.count("\n") + 1,
            "frontmatter_parse_ok": ok,
            "raw_frontmatter_first_line": raw_fm.splitlines()[0] if raw_fm else "",
            "disable_model_invocation": str(fm.get("disable-model-invocation", "")).lower() in ("true", "yes", "1"),
            "user_invocable": str(fm.get("user-invocable", "true")).lower() not in ("false", "no", "0"),
            "name_matches_dir": (name == entry.name),
            "has_triggers": bool(re.search(r"^triggers:\s*$", text, re.MULTILINE)),
            "slash_token": f"/{namespace}:{entry.name}" if namespace else f"/{entry.name}",
        }
        found.append(record)
    return found


def main():
    home = Path(os.path.expanduser("~"))
    cwd = Path.cwd()
    inventory = []

    # 1. Personal
    inventory += scan_dir(home / ".claude" / "skills", "personal")

    # 2. Project (cwd and git root if different)
    seen_project = set()
    for base in {cwd, git_root(cwd) or cwd}:
        pdir = base / ".claude" / "skills"
        if str(pdir) not in seen_project:
            inventory += scan_dir(pdir, "project")
            seen_project.add(str(pdir))

    # 3. Plugins (marketplace + local). Plugin name is the namespace.
    plugins_root = home / ".claude" / "plugins"
    if plugins_root.is_dir():
        for plugin_json in plugins_root.rglob(".claude-plugin/plugin.json"):
            plugin_dir = plugin_json.parent.parent
            try:
                pname = json.loads(plugin_json.read_text(encoding="utf-8")).get("name", plugin_dir.name)
            except Exception:  # noqa: BLE001
                pname = plugin_dir.name
            inventory += scan_dir(plugin_dir / "skills", f"plugin:{pname}", namespace=pname)

    token_counts = Counter(r.get("slash_token") for r in inventory if r.get("slash_token"))
    bare_name_counts = Counter(r.get("name") for r in inventory if r.get("name"))
    for r in inventory:
        r["slash_token_collision"] = token_counts.get(r.get("slash_token"), 0) > 1
        r["bare_name_collision"] = bare_name_counts.get(r.get("name"), 0) > 1

    out = {
        "scanned_at": __import__("datetime").datetime.now().isoformat(),
        "cwd": str(cwd),
        "home": str(home),
        "total_skills": len(inventory),
        "by_source": dict(Counter(r["source"] for r in inventory)),
        "skills": inventory,
    }
    json.dump(out, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
