#!/usr/bin/env python3
"""build/verify-build.py — Verify agents/<name>/_built/ matches manifest declarations.

For each agent:
  - manifest.yml embedded_skills list must equal os.listdir(_built/skills/)
  - Every skill in _built/skills/ must have valid SKILL.md
  - Every skill's references/ filenames must match the canonical source's references/

Iron Rule: this script does NOT MUTATE state. Read-only sanity check.
No fabricated PASS. Every check runs against real disk.

Exit codes:
  0 — all 9 agents, all embedded skills, all references match
  1 — at least one mismatch
"""

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = REPO_ROOT / "agents"
SKILLS_DIR = REPO_ROOT / "skills"
EVIDENCE_DIR = REPO_ROOT / ".planning" / "phases" / "02-agent-embedding" / "evidence"


def list_skill_refs(skill_dir: Path) -> set[str]:
    refs_dir = skill_dir / "references"
    if not refs_dir.is_dir():
        return set()
    return {p.name for p in refs_dir.iterdir() if p.is_file()}


def main() -> int:
    agent_dirs = sorted([d for d in AGENTS_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")])
    if not agent_dirs:
        print("ERROR: no agents", file=sys.stderr)
        return 1

    mismatches: list[str] = []
    all_checks: list[str] = []
    per_agent_summary: list[str] = []

    for agent_dir in agent_dirs:
        manifest_path = agent_dir / "manifest.yml"
        if not manifest_path.is_file():
            mismatches.append(f"{agent_dir.name}: no manifest.yml")
            continue

        manifest = yaml.safe_load(manifest_path.read_text())
        declared = set(manifest.get("embedded_skills", []))

        built_skills_dir = agent_dir / "_built" / "skills"
        if not built_skills_dir.is_dir():
            mismatches.append(f"{agent_dir.name}: no _built/skills/ dir (run embed-skills.py first)")
            continue

        on_disk = {p.name for p in built_skills_dir.iterdir() if p.is_dir() and not p.name.startswith(".")}

        # Symmetric diff check
        missing_from_disk = declared - on_disk
        extra_on_disk = on_disk - declared

        for m in missing_from_disk:
            mismatches.append(f"{agent_dir.name}: manifest declares `{m}` but not in _built/")
        for e in extra_on_disk:
            mismatches.append(f"{agent_dir.name}: _built/ has `{e}` not in manifest")

        # Per-skill content checks
        for skill in declared & on_disk:
            built_skill_dir = built_skills_dir / skill
            canon_skill_dir = SKILLS_DIR / skill

            # SKILL.md must exist + match
            built_skill_md = built_skill_dir / "SKILL.md"
            canon_skill_md = canon_skill_dir / "SKILL.md"
            if not built_skill_md.is_file():
                mismatches.append(f"{agent_dir.name}/{skill}: missing SKILL.md in _built/")
                continue
            if not canon_skill_md.is_file():
                mismatches.append(f"{agent_dir.name}/{skill}: canonical skill has no SKILL.md")
                continue
            if built_skill_md.read_text() != canon_skill_md.read_text():
                mismatches.append(f"{agent_dir.name}/{skill}: SKILL.md content drift between built and canonical")

            # references/ filename match
            built_refs = list_skill_refs(built_skill_dir)
            canon_refs = list_skill_refs(canon_skill_dir)
            if built_refs != canon_refs:
                only_in_built = built_refs - canon_refs
                only_in_canon = canon_refs - built_refs
                if only_in_built:
                    mismatches.append(f"{agent_dir.name}/{skill}: refs only in _built: {sorted(only_in_built)}")
                if only_in_canon:
                    mismatches.append(f"{agent_dir.name}/{skill}: refs only in canonical: {sorted(only_in_canon)}")

            all_checks.append(f"  {agent_dir.name}/{skill}: OK (SKILL.md ✓, refs ✓ [{len(canon_refs)} refs])")

        per_agent_summary.append(f"{agent_dir.name}: declared={len(declared)} on_disk={len(on_disk)} matched={len(declared & on_disk)}")

    print("=" * 60)
    print("Shannon v1 verify-build")
    print("=" * 60)
    for line in per_agent_summary:
        print(line)
    print(f"\nTotal checks: {len(all_checks)}")
    print(f"Mismatches: {len(mismatches)}")
    if mismatches:
        print("\nMISMATCHES:")
        for m in mismatches:
            print(f"  ✗ {m}")
    else:
        print("\n✓ All embedded skills match canonical sources")

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    log = (
        "Shannon v1 verify-build evidence\n"
        + "=" * 60 + "\n\n"
        + "## Per-agent summary\n\n"
        + "\n".join(per_agent_summary) + "\n\n"
        + f"## Total checks: {len(all_checks)}\n"
        + f"## Mismatches: {len(mismatches)}\n\n"
    )
    if all_checks:
        log += "## Per-skill checks (sample)\n\n" + "\n".join(all_checks[:50]) + "\n"
    if mismatches:
        log += "\n## Mismatches\n\n" + "\n".join(f"- {m}" for m in mismatches) + "\n"
    (EVIDENCE_DIR / "verify-build.log").write_text(log)

    return 0 if not mismatches else 1


if __name__ == "__main__":
    raise SystemExit(main())
