"""Teste tout le contenu : blocs python des leçons, corrigés (doivent passer) et codes de départ (doivent échouer)."""
import sys, os, re, json, importlib, tempfile, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "content"))
work = tempfile.mkdtemp()
for d in ["data", "labs"]:
    for f in os.listdir(os.path.join(HERE, d)):
        if f.endswith((".csv", ".py")): shutil.copy(os.path.join(HERE, d, f), work)
os.chdir(work); sys.path.insert(0, work)
import pxshim, runner  # noqa

def collect(names):
    items, quizzes = [], {}
    for n in names:
        m = importlib.import_module(n)
        if hasattr(m, "WEEK"):
            items += m.WEEK["lessons"] + [m.WEEK["project"]]
            quizzes[f"quiz-{m.WEEK['num']}"] = m.WEEK["quiz"]
        items += getattr(m, "LESSONS", []) + getattr(m, "PROJECTS", [])
        for k, q in getattr(m, "QUIZZES", {}).items(): quizzes[k] = q["questions"]
    return items, quizzes

names = sys.argv[1:] or [f[:-3] for f in sorted(os.listdir(os.path.join(HERE, "content"))) if f.endswith(".py") and f != "parcours.py"]
items, quizzes = collect(names)
fails = 0
for L in items:
    key = L["id"]; runner.reset(key)
    for blk in re.findall(r"```python\n(.*?)```", L.get("body", ""), re.S):
        r = json.loads(runner.run(blk, key))
        if r["error"]: fails += 1; print(f"[BODY ERR] {key}: {r['error']}\n---\n{blk[:300]}")
    for ex in L.get("exercises", []):
        r = json.loads(runner.run(ex["solution"], ex["id"], check=ex["check"], fresh=True))
        if not (r["check"] and r["check"]["ok"]):
            fails += 1; print(f"[SOL FAIL] {ex['id']}: {r['check']} {r['error']}\n{r['stdout'][:300]}")
        r2 = json.loads(runner.run(ex["starter"], ex["id"], check=ex["check"], fresh=True))
        if r2["check"] and r2["check"]["ok"]: fails += 1; print(f"[STARTER PASSES] {ex['id']}")
for k, qs in quizzes.items():
    for q in qs: assert 0 <= q["answer"] < len(q["options"]), (k, q["q"])
n_ex = sum(len(L.get("exercises", [])) for L in items)
print(f"{len(items)} leçons/projets, {n_ex} exercices, {len(quizzes)} quiz :", "ok" if not fails else f"{fails} problème(s)")
sys.exit(1 if fails else 0)
