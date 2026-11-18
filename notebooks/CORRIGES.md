# Corrigés

Ne les ouvre qu'après avoir vraiment cherché.

## Essentials AI · Python pour l'IA

### Ton environnement de travail · Premier programme

```python
print("Je deviens AI Engineer")
```

### Variables, types et opérations · Prix TTC

```python
prix_ht = 6250
prix_ttc = prix_ht * 1.2
print(prix_ttc)
```

### Variables, types et opérations · Heures par jour

```python
heures = 450
jours = 60
heures_par_jour = heures / jours
message = f"{heures_par_jour:.1f} heures par jour"
print(message)
```

### Variables, types et opérations · Pair ou impair

```python
n = 17
est_pair = n % 2 == 0
```

### Conditions et boucles · Somme des pairs

```python
somme = 0
for i in range(1, 101):
    if i % 2 == 0:
        somme += i
print(somme)
```

### Conditions et boucles · Catégoriser des scores

```python
scores = [0.12, 0.55, 0.91, 0.79, 0.5, 0.8]
categories = []
for s in scores:
    if s < 0.5:
        categories.append("faible")
    elif s < 0.8:
        categories.append("moyen")
    else:
        categories.append("fort")
print(categories)
```

### Conditions et boucles · Combien d'époques ?

```python
erreur = 10
epoques = 0
while erreur >= 1:
    erreur *= 0.8
    epoques += 1
print(epoques, erreur)
```

### Listes, dictionnaires, tuples et sets · Compter les mots

```python
phrase = "data science data engineering ia data ia"
frequences = {}
for mot in phrase.split():
    frequences[mot] = frequences.get(mot, 0) + 1
print(frequences)
```

### Listes, dictionnaires, tuples et sets · Filtrer avec une compréhension

```python
temperatures = [18, 27, 31, 22, 26, 15]
chaudes = [c * 9 / 5 + 32 for c in temperatures if c > 25]
print(chaudes)
```

### Listes, dictionnaires, tuples et sets · Fusionner sans doublons

```python
a = ["python", "sql", "git"]
b = ["git", "docker", "python", "mlflow"]
competences = sorted(set(a) | set(b))
print(competences)
```

### Fonctions · Écart à la moyenne

```python
def ecarts(valeurs):
    m = sum(valeurs) / len(valeurs)
    return [v - m for v in valeurs]

print(ecarts([1, 2, 3]))
```

### Fonctions · Résumé statistique

```python
def resume(valeurs):
    return {
        "n": len(valeurs),
        "min": min(valeurs),
        "max": max(valeurs),
        "moyenne": round(sum(valeurs) / len(valeurs), 2),
    }

print(resume([3, 7, 8, 12]))
```

### Fonctions · Normaliser avec un paramètre par défaut

```python
def normaliser(valeurs, bas=0, haut=1):
    mn, mx = min(valeurs), max(valeurs)
    return [bas + (v - mn) / (mx - mn) * (haut - bas) for v in valeurs]

print(normaliser([10, 15, 20]))
print(normaliser([10, 15, 20], bas=-1, haut=1))
```

### Fichiers, CSV, JSON et erreurs · Compter les espèces

```python
import csv

with open("penguins.csv") as f:
    lignes = list(csv.DictReader(f))

especes = {}
for l in lignes:
    especes[l["species"]] = especes.get(l["species"], 0) + 1
print(especes)
```

### Fichiers, CSV, JSON et erreurs · Masse moyenne en ignorant les vides

```python
import csv

def en_nombre(texte):
    try:
        return float(texte)
    except ValueError:
        return None

with open("penguins.csv") as f:
    lignes = list(csv.DictReader(f))

masses = [en_nombre(l["body_mass_g"]) for l in lignes]
masses = [m for m in masses if m is not None]
masse_moyenne = sum(masses) / len(masses)
print(round(masse_moyenne, 1))
```

### API web : HTTP, JSON et requests · Extraire des champs imbriqués

```python
import fakeapi as requests
BASE = "https://api.biblio.test"
livre = requests.get(f"{BASE}/books/6").json()
resume = {
    "titre": livre["titre"],
    "annee": livre["annee"],
    "note": livre["note"]["moyenne"],
    "premier_sujet": livre["sujets"][0],
}
resume
```

### API web : HTTP, JSON et requests · Une fonction robuste

```python
import fakeapi as requests
BASE = "https://api.biblio.test"

def titre_du_livre(livre_id):
    r = requests.get(f"{BASE}/books/{livre_id}")
    if r.status_code != 200:
        return None
    return r.json()["titre"]

print(titre_du_livre(1), titre_du_livre(999))
```

### API web : HTTP, JSON et requests · Joindre deux ressources

```python
import fakeapi as requests
BASE = "https://api.biblio.test"
requests.reset()

livres = requests.get(f"{BASE}/books", params={"page": 1, "limit": 5}).json()["resultats"]
cache = {}
lignes = []
for l in livres:
    aid = l["auteur_id"]
    if aid not in cache:
        cache[aid] = requests.get(f"{BASE}/authors/{aid}").json()
    lignes.append(f"{l['titre']} — {cache[aid]['nom']} ({l['annee']})")
lignes
```

### Collecter des données : pagination, reprises, pipeline · Une fonction de pagination

```python
import fakeapi as requests
BASE = "https://api.biblio.test"

def recuperer_tout(limit):
    tous, page = [], 1
    while page is not None:
        donnees = requests.get(f"{BASE}/books", params={"page": page, "limit": limit}).json()
        tous.extend(donnees["resultats"])
        page = donnees["page_suivante"]
    return tous

print(len(recuperer_tout(4)))
```

### Collecter des données : pagination, reprises, pipeline · Reprises intelligentes

```python
import time
import fakeapi as requests
BASE = "https://api.biblio.test"

def get_avec_reprises(url, essais=5):
    for i in range(essais):
        r = requests.get(url)
        if r.status_code == 429 or r.status_code >= 500:
            time.sleep(0.001 * 2 ** i)
            continue
        return r
    raise RuntimeError("Trop d'échecs")

requests.reset()
print(get_avec_reprises(f"{BASE}/flaky").json())
```

### Collecter des données : pagination, reprises, pipeline · Collecter, aplatir, analyser

```python
import pandas as pd
import fakeapi as requests
BASE = "https://api.biblio.test"

tous, page = [], 1
while page:
    d = requests.get(f"{BASE}/books", params={"page": page, "limit": 20}).json()
    tous += d["resultats"]
    page = d["page_suivante"]

df = pd.json_normalize(tous)
top_auteurs = df.groupby("auteur_id")["note.moyenne"].mean().sort_values(ascending=False)
top_auteurs
```

### ETL : extraire, transformer, charger · Une étape de validation

```python
import pandas as pd

def valider(df):
    manquantes = {"id", "titre", "note"} - set(df.columns)
    if manquantes:
        raise ValueError(f"Colonnes manquantes : {manquantes}")
    if df["id"].duplicated().any():
        raise ValueError("Des id sont en double")
    if not df["note"].between(0, 5).all():
        raise ValueError("Des notes sont hors de [0, 5]")
    return df

ok = pd.DataFrame({"id": [1, 2], "titre": ["a", "b"], "note": [4.2, 3.0]})
valider(ok)
```

### Projet 1 · Statistiques du Titanic en Python pur · Taux de survie global

```python
import csv

with open("titanic.csv") as f:
    passagers = list(csv.DictReader(f))

survivants = sum(int(p["survived"]) for p in passagers)
taux_global = survivants / len(passagers)
print(f"{len(passagers)} passagers, taux de survie : {taux_global:.1%}")
```

### Projet 1 · Statistiques du Titanic en Python pur · Taux de survie par groupe

```python
import csv

with open("titanic.csv") as f:
    passagers = list(csv.DictReader(f))

def taux_par(passagers, colonne):
    total, survie = {}, {}
    for p in passagers:
        v = p[colonne]
        total[v] = total.get(v, 0) + 1
        survie[v] = survie.get(v, 0) + int(p["survived"])
    return {v: survie[v] / total[v] for v in total}

print(taux_par(passagers, "sex"))
print(taux_par(passagers, "pclass"))
```

### Projet 1 · Statistiques du Titanic en Python pur · Âge moyen des survivants

```python
import csv

with open("titanic.csv") as f:
    passagers = list(csv.DictReader(f))

def age_moyen(groupe):
    ages = [float(p["age"]) for p in groupe if p["age"] != ""]
    return sum(ages) / len(ages)

age_survivants = age_moyen([p for p in passagers if p["survived"] == "1"])
age_victimes = age_moyen([p for p in passagers if p["survived"] == "0"])
print(round(age_survivants, 1), round(age_victimes, 1))
```

## Essentials AI · IA générative

### Le paysage de l'IA et des LLM · Softmax avec température

```python
import numpy as np

def softmax(logits, temperature=1.0):
    z = np.asarray(logits, dtype=float) / temperature
    z = z - z.max()
    e = np.exp(z)
    return e / e.sum()

print(softmax([2.0, 1.0, 0.1]).round(3))
print(softmax([2.0, 1.0, 0.1], temperature=0.1).round(3))
```

### Le paysage de l'IA et des LLM · Un mini-modèle de langue

```python
modele = {
    "le": {"chat": 0.5, "chien": 0.3, "modèle": 0.2},
    "chat": {"dort": 0.6, "mange": 0.4},
    "dort": {"sur": 0.7, "bien": 0.3},
    "sur": {"le": 1.0},
    "chien": {"court": 1.0},
}

def generer(modele, debut, n):
    mots = [debut]
    for _ in range(n):
        suites = modele.get(mots[-1])
        if not suites:
            break
        mots.append(max(suites, key=suites.get))
    return " ".join(mots)

print(generer(modele, "le", 6))
```

### Le paysage de l'IA et des LLM · Échantillonner avec top-k

```python
import numpy as np

def echantillonner(probas, k, rng):
    top = sorted(probas, key=probas.get, reverse=True)[:k]
    p = np.array([probas[t] for t in top])
    p = p / p.sum()
    return str(rng.choice(top, p=p))

rng = np.random.default_rng(0)
print([echantillonner({"a": 0.5, "b": 0.3, "c": 0.2}, 2, rng) for _ in range(10)])
```

### Le prompt comme interface · Un template de prompt few-shot

```python
exemples = [("Ma carte a été débitée deux fois", "facturation"), ("L'appli plante au démarrage", "technique")]

def construire_prompt(texte, exemples):
    lignes = ["Classe le ticket dans une catégorie : facturation, technique ou compte. Réponds par un seul mot.", ""]
    for t, c in exemples:
        lignes += [f"Ticket : {t}", f"Catégorie : {c}", ""]
    lignes += [f"Ticket : {texte}", "Catégorie :"]
    return "\n".join(lignes)

print(construire_prompt("Je n'arrive plus à me connecter", exemples))
```

### Le prompt comme interface · Valider une sortie structurée

```python
import json, re

def analyser(reponse):
    bloc = re.search(r"\{.*\}", reponse, re.S)
    if not bloc:
        raise ValueError("Aucun JSON trouvé")
    try:
        d = json.loads(bloc.group(0))
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON invalide : {e}")
    if d.get("sentiment") not in {"positif", "negatif", "mitige"}:
        raise ValueError("sentiment manquant ou invalide")
    if not isinstance(d.get("problemes"), list):
        raise ValueError("problemes doit être une liste")
    return d

analyser('Résultat : {"sentiment": "mitige", "problemes": ["retard"]}')
```

### Ce qu'est vraiment un agent · Exécuter un appel d'outil sans planter

```python
def meteo(ville):
    donnees = {"Paris": "12 °C, nuageux", "Lyon": "15 °C, soleil"}
    if ville not in donnees:
        raise KeyError(f"Ville inconnue : {ville}")
    return donnees[ville]

OUTILS = {"meteo": meteo}

def executer(appel, outils):
    nom = appel.get("nom")
    if nom not in outils:
        return {"ok": False, "erreur": f"Outil inconnu : {nom}"}
    try:
        return {"ok": True, "resultat": outils[nom](**appel.get("args", {}))}
    except Exception as e:
        return {"ok": False, "erreur": f"{type(e).__name__} : {e}"}

print(executer({"nom": "meteo", "args": {"ville": "Lyon"}}, OUTILS))
print(executer({"nom": "meteo", "args": {"ville": "Brest"}}, OUTILS))
```

### Ce qu'est vraiment un agent · Ta propre boucle d'agent

```python
def executer(appel, outils):
    nom = appel.get("nom")
    if nom not in outils:
        return {"ok": False, "erreur": f"Outil inconnu : {nom}"}
    try:
        return {"ok": True, "resultat": outils[nom](**appel.get("args", {}))}
    except Exception as e:
        return {"ok": False, "erreur": f"{type(e).__name__} : {e}"}

def agent(question, modele, outils, max_etapes=5):
    historique = [{"role": "user", "content": question}]
    for _ in range(max_etapes):
        action = modele(historique)
        if action["type"] == "final":
            return action["texte"]
        historique.append({"role": "outil", "content": str(executer(action, outils))})
    return "Abandon : trop d'étapes"

def modele_test(historique):
    n_obs = sum(1 for m in historique if m["role"] == "outil")
    if n_obs == 0:
        return {"type": "outil", "nom": "meteo", "args": {"ville": "Paris"}}
    if n_obs == 1:
        return {"type": "outil", "nom": "meteo", "args": {"ville": "Lyon"}}
    return {"type": "final", "texte": "Il fait plus chaud à Lyon."}

OUTILS = {"meteo": lambda ville: {"Paris": 12, "Lyon": 15}[ville]}
print(agent("Où fait-il le plus chaud ?", modele_test, OUTILS))
```

### Modèles de conception : outils et workflows · Évaluateur et optimiseur

```python
def ameliorer(tache, generer, evaluer, seuil=8, max_tours=4):
    brouillon = generer(tache, None)
    meilleur = None
    for tour in range(1, max_tours + 1):
        note, critique = evaluer(brouillon)
        if meilleur is None or note > meilleur[1]:
            meilleur = (brouillon, note)
        if note >= seuil:
            return brouillon, note, tour
        brouillon = generer(tache, critique)
    return meilleur[0], meilleur[1], max_tours

def generer_test(tache, critique):
    return tache if critique is None else tache + " !"

def evaluer_test(texte):
    note = 5 + texte.count("!")
    return note, "Plus d'enthousiasme."

print(ameliorer("Bonjour", generer_test, evaluer_test))
```

### Tokens, fenêtre de contexte et coûts · Une étape de BPE

```python
from collections import Counter

corpus = ["l o w", "l o w e r", "n e w e s t", "w i d e s t"]

def fusion_bpe(corpus):
    paires = Counter()
    for mot in corpus:
        s = mot.split()
        paires.update(zip(s, s[1:]))
    (a, b), _ = paires.most_common(1)[0]
    nouveau = []
    for mot in corpus:
        s, sortie, i = mot.split(), [], 0
        while i < len(s):
            if i + 1 < len(s) and s[i] == a and s[i + 1] == b:
                sortie.append(a + b)
                i += 2
            else:
                sortie.append(s[i])
                i += 1
        nouveau.append(" ".join(sortie))
    return nouveau

c = corpus
for _ in range(3):
    c = fusion_bpe(c)
    print(c)
```

### Tokens, fenêtre de contexte et coûts · Tenir dans le budget de contexte

```python
def tokens(texte):
    return len(texte) // 4 + 1

def tronquer(messages, budget):
    systeme, reste = messages[0], messages[1:]
    total = tokens(systeme["content"])
    gardes = []
    for m in reversed(reste):
        t = tokens(m["content"])
        if total + t > budget:
            break
        gardes.append(m)
        total += t
    return [systeme] + gardes[::-1]
```

### Évaluer un système d'IA · Un banc d'évaluation

```python
jeu = [("Douleur thoracique", "urgent"), ("Facture", "non urgent"), ("Bébé fièvre 40", "urgent"),
       ("Ordonnance", "non urgent"), ("Saignement abondant", "urgent")]

def modele_test(texte):
    return "urgent" if any(m in texte for m in ["Douleur", "Saignement"]) else "non urgent"

def evaluer(modele, jeu):
    predits = [(x, y, modele(x)) for x, y in jeu]
    urgents = [p for p in predits if p[1] == "urgent"]
    return {
        "exactitude": sum(y == p for _, y, p in predits) / len(jeu),
        "rappel_urgent": sum(p == "urgent" for _, _, p in urgents) / len(urgents),
        "erreurs": [x for x, y, p in predits if y != p],
    }

evaluer(modele_test, jeu)
```

### Évaluer un système d'IA · Lire la note d'un LLM juge

```python
import re

def lire_note(verdict):
    notes = re.findall(r"note\s*:\s*([1-5])\s*/\s*5", verdict, re.I)
    if not notes:
        raise ValueError("Aucune note trouvée")
    return int(notes[-1])

print(lire_note("La réponse est exacte et concise.\nNote : 5/5"))
```

## Essentials AI · Applications de l'IA et automatisation

### Automatiser avec n8n et l'IA · Un nœud Code en Python

```python
items = [
    {"json": {"client": "Ada", "montant": 900, "statut": "nouveau"}},
    {"json": {"client": "Linus", "montant": 80, "statut": "nouveau"}},
    {"json": {"client": "Grace", "montant": 2500, "statut": "traité"}},
    {"json": {"client": "Alan", "montant": 150, "statut": "nouveau"}},
]

def noeud_code(items):
    sortie = []
    for it in items:
        d = it["json"]
        if d["statut"] == "nouveau" and d["montant"] > 100:
            ttc = round(d["montant"] * 1.2, 2)
            sortie.append({"json": {"client": d["client"], "montant_ttc": ttc, "priorite": "haute" if ttc > 1000 else "normale"}})
    return sortie

noeud_code(items)
```

### Découvrir l'IA générative et le RAG · Construire le prompt d'un RAG

```python
import numpy as np

documents = [
    "Le RAG combine une recherche de documents et un modèle de langage.",
    "Une base vectorielle stocke des embeddings pour la recherche par similarité.",
    "Les crêpes se préparent avec de la farine, des œufs et du lait.",
    "Un embedding est un vecteur qui représente le sens d'un texte.",
]
vocab = sorted({m.strip(".,").lower() for d in documents for m in d.split()})

def vectoriser(texte):
    mots = [m.strip(".,?").lower() for m in texte.split()]
    return np.array([mots.count(v) for v in vocab], dtype=float)

def cosinus(u, v):
    n = np.linalg.norm(u) * np.linalg.norm(v)
    return 0.0 if n == 0 else u @ v / n

def construire_prompt(question, documents, k=2):
    q = vectoriser(question)
    tries = sorted(documents, key=lambda d: cosinus(q, vectoriser(d)), reverse=True)
    contexte = "\n".join(tries[:k])
    return f"Contexte :\n{contexte}\nQuestion : {question}"

print(construire_prompt("Qu'est-ce qu'un embedding dans une base vectorielle ?", documents))
```

### Un RAG de A à Z en Python · Découper avec chevauchement

```python
def decouper(texte, taille, chevauchement):
    if chevauchement >= taille:
        raise ValueError("Le chevauchement doit être plus petit que la taille")
    mots = texte.split()
    pas = taille - chevauchement
    morceaux = []
    for debut in range(0, len(mots), pas):
        morceaux.append(" ".join(mots[debut:debut + taille]))
        if debut + taille >= len(mots):
            break
    return morceaux

print(decouper("un deux trois quatre cinq six sept", 3, 1))
```

### Un RAG de A à Z en Python · Un moteur de recherche réutilisable

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from cloudsync import DOCS

class Recherche:
    def fit(self, docs):
        self.docs = docs
        self.vect = TfidfVectorizer()
        self.matrice = self.vect.fit_transform([d["titre"] + ". " + d["texte"] for d in docs])
        return self

    def chercher(self, question, k=2):
        scores = cosine_similarity(self.vect.transform([question]), self.matrice)[0]
        return [self.docs[i]["id"] for i in scores.argsort()[::-1][:k]]

r = Recherche().fit(DOCS)
r.chercher("Comment récupérer un fichier supprimé ?")
```

### Un RAG de A à Z en Python · Mesurer le rappel@k

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from cloudsync import DOCS, QUESTIONS_TEST

vect = TfidfVectorizer()
mat = vect.fit_transform([d["titre"] + ". " + d["texte"] for d in DOCS])

def recherche(question, k):
    s = cosine_similarity(vect.transform([question]), mat)[0]
    return [DOCS[i]["id"] for i in s.argsort()[::-1][:k]]

def rappel_at_k(recherche, questions, k):
    trouves = sum(any(p in recherche(q["question"], k) for p in q["pertinents"]) for q in questions)
    return trouves / len(questions)

r1 = rappel_at_k(recherche, QUESTIONS_TEST, 1)
r3 = rappel_at_k(recherche, QUESTIONS_TEST, 3)
print(r1, r3)
```

## Essentials AI · Demo Day

### Projet Demo Day · Un assistant de support intelligent · Le pipeline de l'assistant

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from cloudsync import DOCS

vect = TfidfVectorizer()
mat = vect.fit_transform([d["titre"] + ". " + d["texte"] for d in DOCS])

def recherche(question, k):
    s = cosine_similarity(vect.transform([question]), mat)[0]
    return [DOCS[i]["id"] for i in s.argsort()[::-1][:k]]

def modele_test(prompt):
    return "Réponse fondée sur " + str(prompt.count("[")) + " documents."

def assistant(question, recherche, modele):
    q = question.lower()
    if "résilier" in q or "réclamation" in q:
        return {"route": "humain", "reponse": "Je transmets ta demande à un conseiller.", "sources": []}
    ids = recherche(question, 2)
    textes = {d["id"]: d["texte"] for d in DOCS}
    contexte = "\n".join(f"[{i}] {textes[i]}" for i in ids)
    prompt = f"Réponds à partir des documents et cite tes sources.\n\n{contexte}\n\nQuestion : {question}"
    return {"route": "rag", "reponse": modele(prompt), "sources": ids}

print(assistant("Combien coûte l'offre Plus ?", recherche, modele_test))
print(assistant("Je veux RÉSILIER", recherche, modele_test))
```

### Projet Demo Day · Un assistant de support intelligent · Le tableau de bord d'évaluation

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from cloudsync import DOCS, QUESTIONS_TEST

vect = TfidfVectorizer()
mat = vect.fit_transform([d["titre"] + ". " + d["texte"] for d in DOCS])

def recherche(question, k):
    s = cosine_similarity(vect.transform([question]), mat)[0]
    return [DOCS[i]["id"] for i in s.argsort()[::-1][:k]]

modele_test = lambda prompt: "ok"

def assistant(question, recherche, modele):
    q = question.lower()
    if "résilier" in q or "réclamation" in q:
        return {"route": "humain", "reponse": "Je transmets ta demande à un conseiller.", "sources": []}
    ids = recherche(question, 2)
    textes = {d["id"]: d["texte"] for d in DOCS}
    contexte = "\n".join(f"[{i}] {textes[i]}" for i in ids)
    return {"route": "rag", "reponse": modele(f"{contexte}\n\nQuestion : {question}"), "sources": ids}

resultats = [(q, assistant(q["question"], recherche, modele_test)) for q in QUESTIONS_TEST]
taux_sources = sum(any(p in r["sources"] for p in q["pertinents"]) for q, r in resultats) / len(resultats)
taux_humain = sum(r["route"] == "humain" for _, r in resultats) / len(resultats)
print(taux_sources, taux_humain)
```

## FullStack IA · Préparer ta formation

## FullStack IA · Fondation d'ingénierie en IA

### Classes et objets · Un modèle médiane

```python
class ModeleMediane:
    def fit(self, y):
        s = sorted(y)
        k = len(s) // 2
        if len(s) % 2 == 1:
            self.mediane_ = s[k]
        else:
            self.mediane_ = (s[k - 1] + s[k]) / 2
        return self

    def predict(self, n):
        return [self.mediane_] * n

print(ModeleMediane().fit([5, 1, 9]).predict(3))
```

### Programmation orientée objet · Un compte bancaire

```python
class Compte:
    def __init__(self, titulaire, solde=0):
        self.titulaire = titulaire
        self.solde = float(solde)

    def deposer(self, montant):
        self.solde += montant

    def retirer(self, montant):
        if montant > self.solde:
            raise ValueError("Solde insuffisant")
        self.solde -= montant

    def __repr__(self):
        return f"Compte({self.titulaire}, {self.solde} €)"

c = Compte("Sam", 100)
c.deposer(20)
c
```

### Programmation orientée objet · Un dataset itérable

```python
class MiniDataset:
    def __init__(self, X, y):
        if len(X) != len(y):
            raise ValueError("X et y doivent avoir la même longueur")
        self.X, self.y = X, y

    def __len__(self):
        return len(self.X)

    def __getitem__(self, i):
        return self.X[i], self.y[i]

ds = MiniDataset([[1, 2], [3, 4], [5, 6]], [0, 1, 0])
print(len(ds), ds[1])
for x, cible in ds:
    print(x, cible)
```

### Programmation orientée objet · Polymorphisme : des formes

```python
import math

class Forme:
    def aire(self):
        raise NotImplementedError

class Rectangle(Forme):
    def __init__(self, largeur, hauteur):
        self.largeur, self.hauteur = largeur, hauteur

    def aire(self):
        return self.largeur * self.hauteur

class Cercle(Forme):
    def __init__(self, rayon):
        self.rayon = rayon

    def aire(self):
        return math.pi * self.rayon ** 2

formes = [Rectangle(2, 3), Cercle(1), Rectangle(1, 1)]
aire_totale = sum(f.aire() for f in formes)
print(round(aire_totale, 3))
```

### POO avancée : dataclasses, propriétés, classes abstraites · Une commande en dataclass

```python
from dataclasses import dataclass, field

@dataclass
class Ligne:
    produit: str
    prix: float
    quantite: int = 1

    @property
    def total(self) -> float:
        return self.prix * self.quantite

@dataclass
class Commande:
    client: str
    lignes: list[Ligne] = field(default_factory=list)

    @property
    def montant(self) -> float:
        return round(sum(l.total for l in self.lignes), 2)

c = Commande("Sam", [Ligne("Clavier", 49.9), Ligne("Souris", 19.95, 2)])
print(c, c.montant)
```

### POO avancée : dataclasses, propriétés, classes abstraites · Valider avec une propriété

```python
class Probabilite:
    def __init__(self, valeur):
        self.valeur = valeur

    @property
    def valeur(self):
        return self._valeur

    @valeur.setter
    def valeur(self, v):
        if not 0 <= v <= 1:
            raise ValueError("Une probabilité doit être entre 0 et 1")
        self._valeur = v

    @property
    def cote(self):
        return self._valeur / (1 - self._valeur)

print(Probabilite(0.75).cote)
```

### POO avancée : dataclasses, propriétés, classes abstraites · Ton propre estimateur

```python
from abc import ABC, abstractmethod
import math

class Estimateur(ABC):
    @abstractmethod
    def fit(self, X, y): ...
    @abstractmethod
    def predict(self, X): ...

class PlusProcheMoyenne(Estimateur):
    def fit(self, X, y):
        self.centres_ = {}
        for classe in set(y):
            points = [x for x, c in zip(X, y) if c == classe]
            self.centres_[classe] = [sum(col) / len(points) for col in zip(*points)]
        return self

    def predict(self, X):
        return [min(self.centres_, key=lambda c: math.dist(x, self.centres_[c])) for x in X]

X = [[1, 1], [1, 2], [8, 8], [9, 8]]
y = ["bas", "bas", "haut", "haut"]
m = PlusProcheMoyenne().fit(X, y)
print(m.centres_, m.predict([[2, 2], [7, 9]]))
```

## FullStack IA · Analyse exploratoire des données

### NumPy : calculer sur des tableaux · Normalisation min-max vectorisée

```python
import numpy as np
x = np.array([4.0, 10.0, 7.0, 1.0, 13.0])
x_norm = (x - x.min()) / (x.max() - x.min())
x_norm
```

### NumPy : calculer sur des tableaux · Filtrer avec un masque

```python
import numpy as np
latences = np.array([120, 340, 95, 210, 180, 600, 150, 205])
lentes = latences[latences > 200]
part_lentes = (latences > 200).mean()
print(lentes, part_lentes)
```

### NumPy : calculer sur des tableaux · Standardiser les colonnes

```python
import numpy as np
X = np.array([[170, 65], [180, 80], [160, 55], [175, 72]], dtype=float)
X_std = (X - X.mean(axis=0)) / X.std(axis=0)
print(X_std.mean(axis=0).round(6), X_std.std(axis=0))
```

### pandas : charger et explorer · Premiers chiffres

```python
import pandas as pd
df = pd.read_csv("penguins.csv")
n_lignes = len(df)
n_gentoo = (df["species"] == "Gentoo").sum()
ile_max = df["island"].value_counts().idxmax()
print(n_lignes, n_gentoo, ile_max)
```

### pandas : charger et explorer · Filtre combiné

```python
import pandas as pd
df = pd.read_csv("penguins.csv")
selection = (
    df[(df["island"] == "Dream") & (df["bill_length_mm"] > 45)]
    [["species", "bill_length_mm", "sex"]]
    .sort_values("bill_length_mm", ascending=False)
)
selection.head()
```

### Nettoyer les données · Nettoyer penguins

```python
import pandas as pd
df = pd.read_csv("penguins.csv")
propre = df.dropna(subset=["sex"]).copy()
for col in ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]:
    propre[col] = propre[col].fillna(propre[col].median())
print(propre.isna().sum().sum(), len(propre))
```

### Nettoyer les données · Uniformiser du texte

```python
import pandas as pd
clients = pd.DataFrame({"ville": ["paris", " Lyon", "PARIS ", "lyon", "Marseille", "marseille  "]})
clients["ville_propre"] = clients["ville"].str.strip().str.title()
n_villes = clients["ville_propre"].nunique()
print(clients, n_villes)
```

### Transformer : colonnes, groupby, pivot, merge · Pourboire moyen par jour

```python
import pandas as pd
tips = pd.read_csv("tips.csv")
tips["tip_pct"] = tips["tip"] / tips["total_bill"] * 100
par_jour = tips.groupby("day")["tip_pct"].mean().sort_values(ascending=False)
meilleur_jour = par_jour.index[0]
par_jour
```

### Transformer : colonnes, groupby, pivot, merge · Tableau de synthèse

```python
import pandas as pd
tips = pd.read_csv("tips.csv")
synthese = tips.groupby("time").agg(
    nb=("total_bill", "size"),
    addition_moy=("total_bill", "mean"),
    table_moy=("size", "mean"),
)
synthese.round(2)
```

### Transformer : colonnes, groupby, pivot, merge · Jointure

```python
import pandas as pd
commandes = pd.DataFrame({"produit_id": [1, 2, 1, 3, 2], "quantite": [2, 1, 5, 3, 2]})
produits = pd.DataFrame({"produit_id": [1, 2, 3], "categorie": ["livre", "cours", "livre"], "prix": [30, 200, 45]})
fusion = commandes.merge(produits, on="produit_id")
fusion["ca"] = fusion["quantite"] * fusion["prix"]
ca_par_categorie = fusion.groupby("categorie")["ca"].sum()
ca_par_categorie
```

### Visualiser avec Plotly Express · Pourboire contre addition

```python
import pandas as pd
import plotly.express as px
tips = pd.read_csv("tips.csv")
fig = px.scatter(tips, x="total_bill", y="tip", color="time",
                 title="Le pourboire augmente avec l'addition")
fig.show()
```

### Visualiser avec Plotly Express · Taux de survie par classe

```python
import pandas as pd
import plotly.express as px
titanic = pd.read_csv("titanic.csv")
taux = titanic.groupby("pclass", as_index=False)["survived"].mean()
fig = px.bar(taux, x="pclass", y="survived", title="La 1re classe a le meilleur taux de survie",
             labels={"pclass": "Classe", "survived": "Taux de survie"})
fig.show()
```

### Repérer anomalies et biais · Une fonction de détection

```python
import pandas as pd
tips = pd.read_csv("tips.csv")

def outliers_iqr(serie):
    q1, q3 = serie.quantile([0.25, 0.75])
    iqr = q3 - q1
    return (serie < q1 - 1.5 * iqr) | (serie > q3 + 1.5 * iqr)

n_outliers = outliers_iqr(tips["tip"]).sum()
print(n_outliers)
```

### Repérer anomalies et biais · Repérer la fuite de données

```python
import pandas as pd
titanic = pd.read_csv("titanic.csv")
colonne_fuite = "alive"
features_ok = [c for c in titanic.columns if c not in ["survived", colonne_fuite]]
print(features_ok)
```

### Statistiques descriptives · Variance à la main

```python
import numpy as np
x = np.array([12.0, 15.0, 9.0, 14.0, 10.0])
moyenne = x.sum() / len(x)
variance = ((x - moyenne) ** 2).sum() / len(x)
ecart_type = variance ** 0.5
print(variance, ecart_type)
```

### Statistiques descriptives · Quelle variable est la plus liée à la masse ?

```python
import pandas as pd
df = pd.read_csv("penguins.csv").dropna()
num = df[["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]]
correlations = num.corr()["body_mass_g"].drop("body_mass_g")
meilleure = correlations.abs().idxmax()
print(correlations.round(3), meilleure)
```

### Probabilités et lois usuelles · Une fonction Bayes

```python
def bayes(prior, sensibilite, faux_positifs):
    p_pos = sensibilite * prior + faux_positifs * (1 - prior)
    return sensibilite * prior / p_pos

print(bayes(0.01, 0.99, 0.05))
```

### Probabilités et lois usuelles · Simuler deux dés

```python
import numpy as np
rng = np.random.default_rng(1)
de1 = rng.integers(1, 7, size=100_000)
de2 = rng.integers(1, 7, size=100_000)
p_sept = np.mean(de1 + de2 == 7)
print(p_sept, 1 / 6)
```

### Projet 2 · Analyse exploratoire du Titanic · Audit de qualité

```python
import pandas as pd
df = pd.read_csv("titanic.csv")
manquants = (df.isna().mean() * 100).sort_values(ascending=False)
manquants = manquants[manquants > 0].round(1)
manquants
```

### Projet 2 · Analyse exploratoire du Titanic · Survie par sexe et par classe

```python
import pandas as pd
df = pd.read_csv("titanic.csv")
tableau = pd.pivot_table(df, values="survived", index="sex", columns="pclass", aggfunc="mean").round(3)
tableau
```

### Projet 2 · Analyse exploratoire du Titanic · L'âge des survivants

```python
import pandas as pd
import plotly.express as px
df = pd.read_csv("titanic.csv")
fig = px.histogram(df, x="age", color="alive", barmode="overlay", nbins=40,
                   title="Les enfants ont davantage survécu")
fig.show()
taux_enfants = df[df["age"] < 12]["survived"].mean()
print(f"Taux de survie des moins de 12 ans : {taux_enfants:.1%}")
```

## FullStack IA · Infrastructure de données

### SQL : interroger une base de données · Les thés abordables

```python
import pandas as pd
from brewly import connecter
con = connecter()

requete = """
SELECT nom, prix
FROM produits
WHERE categorie = 'thé' AND prix < 4.3
ORDER BY prix
"""
res = pd.read_sql_query(requete, con)
res
```

### SQL : interroger une base de données · Les premières commandes de Bastille

```python
import pandas as pd
from brewly import connecter
con = connecter()

requete = """
SELECT id, date
FROM commandes
WHERE magasin = 'Bastille'
ORDER BY date, id
LIMIT 5
"""
res = pd.read_sql_query(requete, con)
res
```

### SQL : agréger avec GROUP BY · Les magasins par mois

```python
import pandas as pd
from brewly import connecter
con = connecter()

requete = """
SELECT magasin, COUNT(*) AS nb
FROM commandes
WHERE date BETWEEN '2026-03-01' AND '2026-03-31'
GROUP BY magasin
ORDER BY nb DESC, magasin
"""
res = pd.read_sql_query(requete, con)
res
```

### SQL : agréger avec GROUP BY · Les clients fidèles

```python
import pandas as pd
from brewly import connecter
con = connecter()

requete = """
SELECT client_id, COUNT(*) AS nb, COUNT(DISTINCT magasin) AS nb_magasins
FROM commandes
GROUP BY client_id
HAVING COUNT(*) >= 13
ORDER BY nb DESC, client_id
"""
res = pd.read_sql_query(requete, con)
res
```

### SQL : jointures et sous-requêtes · Chiffre d'affaires par ville

```python
import pandas as pd
from brewly import connecter
con = connecter()

requete = """
SELECT cl.ville, ROUND(SUM(l.quantite * p.prix), 2) AS ca
FROM lignes l
JOIN produits p ON p.id = l.produit_id
JOIN commandes c ON c.id = l.commande_id
JOIN clients cl ON cl.id = c.client_id
GROUP BY cl.ville
ORDER BY ca DESC
"""
res = pd.read_sql_query(requete, con)
res
```

### SQL : jointures et sous-requêtes · Les clients jamais venus

```python
import pandas as pd
from brewly import connecter
con = connecter()

requete = """
SELECT cl.id, cl.prenom
FROM clients cl
LEFT JOIN commandes c ON c.client_id = cl.id
WHERE c.id IS NULL
ORDER BY cl.id
"""
res = pd.read_sql_query(requete, con)
res
```

### SQL : jointures et sous-requêtes · Le produit star de chaque magasin

```python
import pandas as pd
from brewly import connecter
con = connecter()

requete = """
WITH ventes AS (
    SELECT c.magasin, p.nom AS produit, SUM(l.quantite) AS qte
    FROM lignes l
    JOIN commandes c ON c.id = l.commande_id
    JOIN produits p ON p.id = l.produit_id
    GROUP BY c.magasin, p.nom
)
SELECT v.magasin, v.produit, v.qte
FROM ventes v
WHERE v.qte = (SELECT MAX(qte) FROM ventes w WHERE w.magasin = v.magasin)
ORDER BY v.magasin
"""
res = pd.read_sql_query(requete, con)
res
```

### Projet · Un mini-entrepôt de données Brewly · La table de faits

```python
import pandas as pd
from brewly import connecter
con = connecter()

faits = pd.read_sql_query("""
SELECT l.commande_id, c.date, SUBSTR(c.date, 1, 7) AS mois, c.magasin,
       cl.ville AS ville_client, p.nom AS produit, p.categorie,
       l.quantite, l.quantite * p.prix AS montant
FROM lignes l
JOIN commandes c ON c.id = l.commande_id
JOIN clients cl ON cl.id = c.client_id
JOIN produits p ON p.id = l.produit_id
""", con)
faits.head()
```

### Projet · Un mini-entrepôt de données Brewly · Le tableau de bord du lundi

```python
import pandas as pd
from brewly import connecter
con = connecter()
faits = pd.read_sql_query("""
SELECT l.commande_id, c.date, SUBSTR(c.date, 1, 7) AS mois, c.magasin,
       cl.ville AS ville_client, p.nom AS produit, p.categorie,
       l.quantite, l.quantite * p.prix AS montant
FROM lignes l
JOIN commandes c ON c.id = l.commande_id
JOIN clients cl ON cl.id = c.client_id
JOIN produits p ON p.id = l.produit_id
""", con)

ca_mensuel = faits.groupby("mois")["montant"].sum().round(2).sort_index()
croissance = round((ca_mensuel["2026-04"] / ca_mensuel["2026-03"] - 1) * 100, 1)
top_categorie = faits.groupby("categorie")["montant"].sum().idxmax()
print(ca_mensuel, croissance, top_categorie)
```

## FullStack IA · Apprentissage automatique

### Le vocabulaire du machine learning · Préparer X et y

```python
import pandas as pd
from sklearn.model_selection import train_test_split
tips = pd.read_csv("tips.csv")
X = tips[["total_bill", "size"]]
y = tips["tip"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)
print(X_train.shape, X_test.shape)
```

### Le vocabulaire du machine learning · Le score à battre

```python
import pandas as pd
t = pd.read_csv("titanic.csv")
baseline = t["survived"].value_counts(normalize=True).max()
print(f"Baseline : {baseline:.1%}")
```

### Classification et métriques · Ajouter le port d'embarquement

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

t = pd.read_csv("titanic.csv")
t["femme"] = (t["sex"] == "female").astype(int)
t["age"] = t["age"].fillna(t["age"].median())
base = ["pclass", "femme", "age", "fare", "sibsp", "parch"]

ports = pd.get_dummies(t["embarked"].fillna("S"), prefix="port", dtype=int)
X = pd.concat([t[base], ports], axis=1)
y = t["survived"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
clf = LogisticRegression(max_iter=1000).fit(X_train, y_train)
acc = accuracy_score(y_test, clf.predict(X_test))
print(X.columns.tolist(), round(acc, 3))
```

### Classification et métriques · Précision et rappel à la main

```python
import numpy as np
cm = np.array([[95, 15],
               [20, 49]])
vn, fp, fn, vp = cm.ravel()
precision = vp / (vp + fp)
rappel = vp / (vp + fn)
f1 = 2 * precision * rappel / (precision + rappel)
print(round(precision, 3), round(rappel, 3), round(f1, 3))
```

### Régression avec scikit-learn · Prédire le pourboire

```python
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

tips = pd.read_csv("tips.csv")
X = tips[["total_bill", "size"]]
y = tips["tip"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)

modele = LinearRegression().fit(X_train, y_train)
mae = mean_absolute_error(y_test, modele.predict(X_test))
mae_baseline = mean_absolute_error(y_test, np.full(len(y_test), y_train.mean()))
print(f"MAE modèle : {mae:.3f} $  |  MAE baseline : {mae_baseline:.3f} $")
```

### Surapprentissage et validation croisée · Trouver la meilleure profondeur

```python
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score

t = pd.read_csv("titanic.csv")
t["femme"] = (t["sex"] == "female").astype(int)
t["age"] = t["age"].fillna(t["age"].median())
X = t[["pclass", "femme", "age", "fare", "sibsp", "parch"]]
y = t["survived"]

scores_cv = {}
for d in range(1, 11):
    arbre = DecisionTreeClassifier(max_depth=d, random_state=0)
    scores_cv[d] = cross_val_score(arbre, X, y, cv=5).mean()
meilleure_profondeur = max(scores_cv, key=scores_cv.get)
print({d: round(s, 3) for d, s in scores_cv.items()}, meilleure_profondeur)
```

### Projet final · Classifier les espèces de manchots · Préparer les données

```python
import pandas as pd
from sklearn.model_selection import train_test_split

df = pd.read_csv("penguins.csv").dropna()
df["male"] = (df["sex"] == "MALE").astype(int)
X = df[["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g", "male"]]
y = df["species"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
print(X_train.shape, X_test.shape)
print(y_train.value_counts(normalize=True).round(2))
```

### Projet final · Classifier les espèces de manchots · Entraîner et évaluer

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix

df = pd.read_csv("penguins.csv").dropna()
df["male"] = (df["sex"] == "MALE").astype(int)
X = df[["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g", "male"]]
y = df["species"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

modele = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
modele.fit(X_train, y_train)
pred = modele.predict(X_test)
acc = accuracy_score(y_test, pred)
cm = confusion_matrix(y_test, pred)
print(f"Exactitude : {acc:.3f}")
pd.DataFrame(cm, index=modele.classes_, columns=modele.classes_)
```

### Projet final · Classifier les espèces de manchots · Prédire un nouveau manchot

```python
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

df = pd.read_csv("penguins.csv").dropna()
df["male"] = (df["sex"] == "MALE").astype(int)
cols = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g", "male"]
modele = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)).fit(df[cols], df["species"])

nouveau = pd.DataFrame([{
    "bill_length_mm": 50, "bill_depth_mm": 15, "flipper_length_mm": 220,
    "body_mass_g": 5500, "male": 1,
}])
espece = modele.predict(nouveau)[0]
confiance = modele.predict_proba(nouveau).max()
print(f"{espece} ({confiance:.1%})")
```

## FullStack IA · Fondation pour l'apprentissage profond

### Vecteurs et matrices · Prédire avec des poids

```python
import numpy as np
X = np.array([[30, 1], [55, 3], [80, 4]], dtype=float)
b = 20000
w = np.array([3000, 15000])
prix = X @ w + b
print(prix)
```

### Vecteurs et matrices · Similarité cosinus

```python
import numpy as np
docs = {
    "cours_python": np.array([0.9, 0.1, 0.0]),
    "recette_crepes": np.array([0.0, 0.2, 0.9]),
    "tuto_pandas": np.array([0.7, 0.6, 0.1]),
}
requete = np.array([0.8, 0.5, 0.0])

def cosinus(u, v):
    return u @ v / (np.linalg.norm(u) * np.linalg.norm(v))

scores = {nom: cosinus(requete, vec) for nom, vec in docs.items()}
plus_proche = max(scores, key=scores.get)
print(scores, plus_proche)
```

### Dérivées et gradient · Dérivée numérique

```python
def f(x):
    return x ** 3 - 2 * x

def derivee(f, x, h=1e-5):
    return (f(x + h) - f(x - h)) / (2 * h)

pente = derivee(f, 2)
print(pente)
```

### Dérivées et gradient · Gradient exact

```python
def grad_perte(a, b):
    return 2 * (a - 1), 2 * (b + 2)

print(grad_perte(0, 0))
```

### La descente de gradient · Minimiser une parabole

```python
def L(x):
    return (x + 4) ** 2 + 1

def dL(x):
    return 2 * (x + 4)

x = 0.0
for _ in range(100):
    x -= 0.1 * dL(x)
x_min = x
print(x_min, L(x_min))
```

### La descente de gradient · Régression sur les manchots

```python
import numpy as np
import pandas as pd
import plotly.express as px
df = pd.read_csv("penguins.csv").dropna()
x = df["flipper_length_mm"].to_numpy()
y = df["body_mass_g"].to_numpy()
xs = (x - x.mean()) / x.std()
ys = (y - y.mean()) / y.std()

w, b = 0.0, 0.0
pertes = []
for _ in range(200):
    erreur = w * xs + b - ys
    pertes.append((erreur ** 2).mean())
    w -= 0.1 * 2 * (erreur * xs).mean()
    b -= 0.1 * 2 * erreur.mean()

print("w =", round(w, 4), " polyfit :", round(np.polyfit(xs, ys, 1)[0], 4))
px.line(y=pertes, title="Courbe de perte")
```

### Projet 3 · Ta régression linéaire de A à Z · La classe RegressionGD

```python
import numpy as np

class RegressionGD:
    def __init__(self, eta=0.1, n_epoques=500):
        self.eta = eta
        self.n_epoques = n_epoques

    def fit(self, X, y):
        n, k = X.shape
        self.coef_ = np.zeros(k)
        self.intercept_ = 0.0
        self.pertes_ = []
        for _ in range(self.n_epoques):
            erreur = X @ self.coef_ + self.intercept_ - y
            self.pertes_.append((erreur ** 2).mean())
            self.coef_ -= self.eta * 2 / n * (X.T @ erreur)
            self.intercept_ -= self.eta * 2 * erreur.mean()
        return self

    def predict(self, X):
        return X @ self.coef_ + self.intercept_

rng = np.random.default_rng(0)
X = rng.normal(size=(200, 3))
y = X @ np.array([2.0, -1.0, 0.5]) + 3 + rng.normal(0, 0.1, 200)
m = RegressionGD().fit(X, y)
print(m.coef_.round(2), round(m.intercept_, 2))
```

### Projet 3 · Ta régression linéaire de A à Z · Appliquer aux manchots

```python
import numpy as np
import pandas as pd

class RegressionGD:
    def __init__(self, eta=0.1, n_epoques=500):
        self.eta = eta
        self.n_epoques = n_epoques

    def fit(self, X, y):
        n, k = X.shape
        self.coef_ = np.zeros(k)
        self.intercept_ = 0.0
        self.pertes_ = []
        for _ in range(self.n_epoques):
            erreur = X @ self.coef_ + self.intercept_ - y
            self.pertes_.append((erreur ** 2).mean())
            self.coef_ -= self.eta * 2 / n * (X.T @ erreur)
            self.intercept_ -= self.eta * 2 * erreur.mean()
        return self

    def predict(self, X):
        return X @ self.coef_ + self.intercept_

df = pd.read_csv("penguins.csv").dropna()
cols = ["flipper_length_mm", "bill_length_mm", "bill_depth_mm"]
X = df[cols].to_numpy()
X = (X - X.mean(axis=0)) / X.std(axis=0)
y = df["body_mass_g"].to_numpy()

modele = RegressionGD(eta=0.1, n_epoques=1000).fit(X, y)
rmse = np.sqrt(((modele.predict(X) - y) ** 2).mean())
print(f"RMSE : {rmse:.0f} g")
```
