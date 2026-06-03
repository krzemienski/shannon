import importlib.util
spec = importlib.util.spec_from_file_location("ev", "scripts/skills10x/eval_skill.py")
ev = importlib.util.module_from_spec(spec); spec.loader.exec_module(ev)

cases = {
 "plan this": False, "validate it": False, "remember this": False,
 "this": False, "it": False, "": False,
 "run this plan by decomposing it into dependency-ordered waves": True,
 "decompose this": False, "audit the website": True, "fix": True,
 "review this code thoroughly": True, "do it": False, "commit": True,
}
print("== _is_self_sufficient ==")
bad = 0
for p, exp in cases.items():
    got = ev._is_self_sufficient(p); ok = got == exp; bad += (not ok)
    print(f"  {'OK ' if ok else 'XX '} got={got!s:5} exp={exp!s:5} | {p!r}")
print("unit fails:", bad)

print("\n== synth partition + no-fabrication ==")
sk = {"description": "Use when you need to ship a release."}
trigs = ["plan this", "decompose the plan into ordered waves", "fix it", "audit the website"]
out = ev.synth_should_prompts(sk, trigs, 8)
prefixes = ["", "Can you ", "Please ", "I'd like you to "]
def strip_pref(s):
    for pf in sorted(prefixes, key=len, reverse=True):
        if pf and s.startswith(pf): return s[len(pf):]
    return s
allowed = set(t.strip() for t in trigs) | {"I need to ship a release"}
fab = 0
for o in out:
    base = strip_pref(o); hit = base in allowed; fab += (not hit)
    print(f"  {'OK ' if hit else 'FAB'} {o!r}")
print("fabrication fails:", fab)
print("self_suff seq:", [ev._is_self_sufficient(strip_pref(o)) for o in out])

print("\n== edges ==")
print("  empty triggers ->", ev.synth_should_prompts({"description": ""}, [], 3))
print("  only-desc ->", ev.synth_should_prompts({"description": "Use when you debug a crash."}, [], 3))
we = ["decompose this", "run this plan by decomposing it into dependency-ordered waves"]
print("  wave-exec lead ->", ev.synth_should_prompts({"description": ""}, we, 2))
r1 = ev.synth_should_prompts(sk, trigs, 8)
print("  deterministic ->", r1 == out)
