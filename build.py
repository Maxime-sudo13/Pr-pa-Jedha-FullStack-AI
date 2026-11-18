"""Construit dist/ (content.json, index.html, data/) à partir des sources de contenu."""
import json, re, subprocess, sys, os, importlib, shutil
import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "content"))
TEX2SVG = os.environ.get("TEX2SVG", os.path.join(HERE, "tools", "tex2svg.js"))

MD = markdown.Markdown(extensions=["fenced_code", "tables", "sane_lists"])
tex_list = []


def md(text):
    def grab(m):
        tex_list.append(m.group(1).strip())
        return f'\n<div class="math" data-tex="{len(tex_list) - 1}"></div>\n'
    text = re.sub(r"```latex\n(.*?)```", grab, text, flags=re.S)
    text = re.sub(r"```viz[ \n](\w[\w-]*)\s*\n?```", lambda m: f'\n<div class="viz" data-viz="{m.group(1)}"></div>\n', text)
    MD.reset()
    return MD.convert(text.strip()).replace("<blockquote>", '<blockquote class="callout">')


def md_inline(text):
    MD.reset()
    return MD.convert(text.strip())


def plain(body):
    t = re.sub(r"```.*?```", " ", body or "", flags=re.S)
    return t


def ex(e):
    return {"id": e["id"], "title": e["title"], "prompt": md_inline(e["prompt"]), "starter": e["starter"],
            "solution": e["solution"], "check": e["check"], "hint": e.get("hint", "")}


def item(L, kind):
    return {"id": L["id"], "kind": kind, "title": L["title"], "minutes": L.get("minutes"),
            "body": md(L.get("body", "")), "text": plain(L.get("body", "")),
            "tasks": L.get("tasks", []), "exercises": [ex(e) for e in L.get("exercises", [])]}


ITEMS, QUIZ = {}, {}
OLD_QUIZ_TITLES = {1: "Quiz · Python et Git", 2: "Quiz · NumPy, pandas et visualisation",
                   3: "Quiz · Les maths du ML", 4: "Quiz · Premiers modèles et IA générative"}
for name in sorted(f[:-3] for f in os.listdir(os.path.join(HERE, "content")) if f.endswith(".py") and f != "parcours.py"):
    m = importlib.import_module(name)
    if hasattr(m, "WEEK"):
        W = m.WEEK
        for L in W["lessons"]:
            ITEMS[L["id"]] = item(L, "lesson")
        ITEMS[W["project"]["id"]] = item(W["project"], "project")
        QUIZ[f"quiz-{W['num']}"] = {"id": f"quiz-{W['num']}", "kind": "quiz", "title": OLD_QUIZ_TITLES[W["num"]], "questions": W["quiz"]}
    for L in getattr(m, "LESSONS", []):
        ITEMS[L["id"]] = item(L, "lesson")
    for L in getattr(m, "PROJECTS", []):
        ITEMS[L["id"]] = item(L, "project")
    for k, q in getattr(m, "QUIZZES", {}).items():
        QUIZ[k] = {"id": k, "kind": "quiz", "title": q["title"], "questions": q["questions"]}

P = importlib.import_module("parcours")
for T in P.TRACKS:
    for M in T["modules"]:
        for s in M["sections"]:
            for lid in s["lecons"]:
                assert lid in ITEMS, f"Leçon inconnue {lid} dans {M['id']}"
        for q in M["quiz"]:
            assert q in QUIZ, f"Quiz inconnu {q}"
        for p in M["projets"]:
            assert p in ITEMS, f"Projet inconnu {p}"

# LaTeX → SVG
svgs = []
if tex_list:
    p = subprocess.run(["node", TEX2SVG], input=json.dumps(tex_list), capture_output=True, text=True, check=True)
    svgs = json.loads(p.stdout)
for it in ITEMS.values():
    it["body"] = re.sub(r'<div class="math" data-tex="(\d+)"></div>',
                        lambda m: f'<div class="math">{svgs[int(m.group(1))]}</div>', it["body"])

labs = {f: open(os.path.join(HERE, "labs", f)).read() for f in sorted(os.listdir(os.path.join(HERE, "labs"))) if f.endswith(".py")}
labs["pxshim.py"] = open(os.path.join(HERE, "pxshim.py")).read()

jourj = [
    "Python, VS Code, Jupyter, Git et Docker installés et fonctionnels sur ton ordinateur",
    "Un compte GitHub avec au moins 4 dépôts publiés et un README de profil",
    "Un compte AWS sécurisé (double authentification, alerte de budget, utilisateur IAM)",
    "Savoir expliquer à voix haute le surapprentissage, la descente de gradient et l'attention",
    "Des comptes créés sur Kaggle et Hugging Face",
    "Ton profil LinkedIn mis à jour avec ta reconversion vers l'IA",
    "Tes questions notées pour l'équipe Jedha, dont la définition exacte du taux de 98 %",
    "Tous les quiz de la plateforme réussis avec au moins 75 % de bonnes réponses",
]
resources = [
    {"name": "Tutoriel officiel Python", "url": "https://docs.python.org/fr/3/tutorial/", "module": "Fondation", "lang": "FR", "why": "La référence sur les bases du langage"},
    {"name": "Kaggle Learn", "url": "https://www.kaggle.com/learn", "module": "Fondation à ML", "lang": "EN", "why": "Cours courts avec exercices : Python, pandas, SQL, ML"},
    {"name": "Livre Pro Git", "url": "https://git-scm.com/book/fr/v2", "module": "Fondation", "lang": "FR", "why": "Chapitres 1 et 2 pour les commandes de base"},
    {"name": "10 minutes to pandas", "url": "https://pandas.pydata.org/docs/user_guide/10min.html", "module": "Analyse exploratoire", "lang": "EN", "why": "Le tour officiel de pandas"},
    {"name": "SQLBolt", "url": "https://sqlbolt.com/", "module": "Infrastructure de données", "lang": "EN", "why": "Leçons SQL interactives"},
    {"name": "AWS Skill Builder, Cloud Practitioner Essentials", "url": "https://skillbuilder.aws/", "module": "Infrastructure de données", "lang": "EN/FR", "why": "Le cours officiel gratuit pour la certification CLF-C02"},
    {"name": "Khan Academy", "url": "https://fr.khanacademy.org", "module": "Maths", "lang": "FR", "why": "Statistiques, probabilités et dérivées"},
    {"name": "3Blue1Brown", "url": "https://www.3blue1brown.com/", "module": "Maths et deep learning", "lang": "EN", "why": "Algèbre linéaire, réseaux de neurones et Transformers en animation"},
    {"name": "StatQuest", "url": "https://www.youtube.com/@statquest", "module": "ML", "lang": "EN", "why": "Statistiques et algorithmes de ML expliqués simplement"},
    {"name": "Guide utilisateur scikit-learn", "url": "https://scikit-learn.org/stable/user_guide.html", "module": "ML", "lang": "EN", "why": "Documentation officielle des modèles et métriques"},
    {"name": "Hugging Face LLM Course", "url": "https://huggingface.co/learn", "module": "IA générative", "lang": "EN", "why": "Transformers, fine-tuning et agents, gratuit"},
    {"name": "Formation AI Engineer de Jedha", "url": "https://www.jedha.co/formations/formation-ai-engineer", "module": "—", "lang": "FR", "why": "Le programme détaillé de ta formation"},
]

out = {"version": 2, "items": ITEMS, "quizzes": QUIZ, "tracks": P.TRACKS, "plan": P.PLAN,
       "jourj": jourj, "resources": resources, "runner": open(os.path.join(HERE, "runner.py")).read(), "labs": labs}
dist = os.path.join(HERE, "dist")
os.makedirs(os.path.join(dist, "data"), exist_ok=True)
with open(os.path.join(dist, "content.json"), "w") as f:
    json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
shutil.copy(os.path.join(HERE, "web", "index.html"), os.path.join(dist, "index.html"))
for f in os.listdir(os.path.join(HERE, "data")):
    if f.endswith(".csv"):
        shutil.copy(os.path.join(HERE, "data", f), os.path.join(dist, "data", f))
n_ex = sum(len(i["exercises"]) for i in ITEMS.values())
print(f"{sum(1 for i in ITEMS.values() if i['kind'] == 'lesson')} leçons, "
      f"{sum(1 for i in ITEMS.values() if i['kind'] == 'project')} projets, {n_ex} exercices, {len(QUIZ)} quiz, "
      f"{len(tex_list)} formules, {os.path.getsize(os.path.join(dist, 'content.json')) // 1024} Ko")
