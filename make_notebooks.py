"""Génère un notebook Jupyter par module (notebooks/) et les corrigés (notebooks/CORRIGES.md)."""
import json, os, re, sys, importlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "content"))

def md_cell(t): return {"cell_type": "markdown", "metadata": {}, "source": t.strip("\n").splitlines(keepends=True)}
def code_cell(c): return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": c.strip("\n").splitlines(keepends=True)}

def split_body(body):
    cells, parts = [], re.split(r"```(\w+)[ \n](.*?)```", body, flags=re.S)
    for i in range(0, len(parts), 3):
        if parts[i].strip(): cells.append(md_cell(parts[i].strip()))
        if i + 2 < len(parts):
            lang, code = parts[i + 1], parts[i + 2]
            if lang == "python": cells.append(code_cell(code))
            elif lang == "latex": cells.append(md_cell(f"$$\n{code.strip()}\n$$"))
            elif lang == "viz": cells.append(md_cell(f"*Animation interactive « {code.strip()} » : à voir sur la plateforme web.*"))
            else: cells.append(md_cell(f"```{'python' if lang == 'pycode' else lang}\n{code.rstrip()}\n```"))
    return cells

def exercise_cells(ex, n):
    head = md_cell(f"### Exercice {n} · {ex['title']}\n\n{ex['prompt']}\n\n<details><summary>Indice</summary>\n\n{ex['hint']}\n</details>")
    if "_out" in ex["check"]:
        return [head, code_cell(ex["starter"]), md_cell("Vérifie que l'affichage correspond exactement à la consigne.")]
    return [head, code_cell(ex["starter"]), md_cell("Exécute la cellule suivante pour vérifier ta réponse."),
            code_cell(ex["check"] + 'print("Bravo, tout est correct.")')]

ITEMS = {}
for name in sorted(f[:-3] for f in os.listdir(os.path.join(HERE, "content")) if f.endswith(".py") and f != "parcours.py"):
    m = importlib.import_module(name)
    if hasattr(m, "WEEK"):
        for L in m.WEEK["lessons"] + [m.WEEK["project"]]: ITEMS[L["id"]] = L
    for L in getattr(m, "LESSONS", []) + getattr(m, "PROJECTS", []): ITEMS[L["id"]] = L

P = importlib.import_module("parcours")
os.makedirs(os.path.join(HERE, "notebooks"), exist_ok=True)
seen, corr = set(), ["# Corrigés\n\nNe les ouvre qu'après avoir vraiment cherché.\n"]
for T in P.TRACKS:
    for M in T["modules"]:
        ids = [i for s in M["sections"] for i in s["lecons"]] + M["projets"]
        ids = [i for i in dict.fromkeys(ids) if i not in seen]
        if not ids: continue
        seen.update(ids)
        cells = [md_cell(f"# {T['nom']} · {M['titre']}\n\n**Objectif :** {M['objectif']}\n\nLance ce notebook depuis le dossier `notebooks/`."),
                 code_cell('import os, sys\nsys.path.insert(0, os.path.abspath("../labs"))   # brewly, fakeapi\nos.chdir("../data")                               # penguins.csv, titanic.csv, tips.csv')]
        corr.append(f"\n## {T['nom']} · {M['titre']}\n")
        for lid in ids:
            L = ITEMS[lid]
            cells.append(md_cell(f"---\n## {L['title']}"))
            cells += split_body(L.get("body", ""))
            if L.get("tasks"): cells.append(md_cell("**À faire :**\n\n" + "\n".join(f"- [ ] {t}" for t in L["tasks"])))
            for n, ex in enumerate(L.get("exercises", []), 1):
                cells += exercise_cells(ex, n)
                corr.append(f"\n### {L['title']} · {ex['title']}\n\n```python\n{ex['solution'].rstrip()}\n```\n")
        nb = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
        fn = f"{T['id']}-{M['id']}.ipynb"
        json.dump(nb, open(os.path.join(HERE, "notebooks", fn), "w"), ensure_ascii=False, indent=1)
        print(fn, len(cells), "cellules")
open(os.path.join(HERE, "notebooks", "CORRIGES.md"), "w").write("".join(corr))
