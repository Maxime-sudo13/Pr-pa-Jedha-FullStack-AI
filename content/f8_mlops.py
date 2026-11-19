"""FullStack · Ingénierie ML (vague 6) : terminal, Streamlit, Docker, EC2, MLflow, asynchrone, FastAPI, et le projet d'infrastructure (F9)."""
from f4_ml import IMMO_PRE

def E(id, title, prompt, starter, solution, check, hint):
    return {"id": id, "title": title, "prompt": prompt, "starter": starter, "solution": solution, "check": check, "hint": hint}

SUIVI = r'''from contextlib import contextmanager
import pandas as pd

class Run:
    def __init__(self, nom):
        self.nom, self.params, self.metriques, self.tags, self.statut = nom, {}, {}, {}, "RUNNING"
    def log_param(self, cle, valeur):
        self.params[cle] = valeur
    def log_metric(self, cle, valeur, step=None):
        self.metriques.setdefault(cle, []).append((step, float(valeur)))
    def set_tag(self, cle, valeur):
        self.tags[cle] = valeur

class Suivi:
    def __init__(self):
        self.runs = []
    @contextmanager
    def run(self, nom):
        r = Run(nom)
        self.runs.append(r)
        try:
            yield r
            r.statut = "FINISHED"
        except Exception:
            r.statut = "FAILED"
            raise
    def tableau(self):
        lignes = []
        for r in self.runs:
            ligne = {"run": r.nom, "statut": r.statut}
            ligne.update({f"params.{k}": v for k, v in r.params.items()})
            ligne.update({f"metrics.{k}": v[-1][1] for k, v in r.metriques.items()})
            lignes.append(ligne)
        return pd.DataFrame(lignes)
    def meilleur(self, metrique, mode="max"):
        ok = [r for r in self.runs if r.statut == "FINISHED" and metrique in r.metriques]
        cle = lambda r: r.metriques[metrique][-1][1]
        return max(ok, key=cle) if mode == "max" else min(ok, key=cle)
'''

PAIE_PRE = r'''import numpy as np
import pandas as pd
from paiements import charger
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

def preparer(df):
    return pd.DataFrame({
        "pays_diff": (df["pays_carte"] != df["pays_ip"]).astype(int),
        "log_montant": np.log1p(df["montant"] / 100),
        "nb_tx_24h": df["nb_tx_24h"],
        "compte_recent": (df["anciennete_compte_j"] < 30).astype(int),
        "appareil_nouveau": df["appareil_nouveau"],
        "nuit": (df["heure"] < 6).astype(int),
        "cat_risque": df["categorie"].isin(["électronique", "jeux"]).astype(int),
    }, index=df.index)
'''

PAIE_SPLIT = r'''
df = charger()
X, y = preparer(df), df["fraude"]
X_train, X_test, y_train, y_test, m_train, m_test = train_test_split(
    X, y, df["montant"], test_size=0.25, stratify=y, random_state=0)
'''

LESSONS = [
# ================================================================ Terminal
{"id": "l-shell", "title": "Le terminal et un vrai projet Python", "minutes": 90,
"body": r'''
Un notebook est parfait pour explorer. Mais un modèle qui tourne en production vit dans un **projet** : des fichiers Python, des dépendances figées, une configuration, des journaux, et un terminal pour tout piloter. C'est le quotidien d'un ingénieur ML, et la première chose qu'on te demandera de faire chez Jedha.

## Les commandes à connaître par cœur

```pycode
pwd                       # où suis-je ?
ls -la                    # que contient ce dossier (fichiers cachés compris) ?
cd projets/fraude         # aller dans un dossier ;  cd ..  pour remonter
mkdir -p src/api          # créer un dossier (et ses parents)
cp a.py b.py ; mv b.py c.py ; rm c.py
cat requirements.txt      # afficher un fichier ;  less pour les longs
head -n 5 data.csv        # les 5 premières lignes ;  tail -f app.log pour suivre un journal en direct
grep -rn "TODO" src/      # chercher un texte dans tous les fichiers
wc -l data.csv            # compter les lignes
python train.py --seuil 0.3 > sortie.txt 2>&1   # rediriger la sortie et les erreurs
history | grep docker     # retrouver une commande passée
```

Le **pipe** `|` envoie la sortie d'une commande dans la suivante : `cat app.log | grep ERROR | wc -l` compte les erreurs.

## Un environnement par projet

Chaque projet a ses propres versions de bibliothèques. On les isole dans un **environnement virtuel** :

```pycode
python -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install pandas scikit-learn fastapi
pip freeze > requirements.txt      # figer les versions exactes
```

L'outil **uv** fait la même chose, en beaucoup plus rapide : `uv venv`, `uv pip install`, ou `uv add` dans un projet géré par `pyproject.toml`.

## La structure d'un projet

```pycode
fraude/
├── pyproject.toml        # nom, version, dépendances
├── README.md
├── .env                  # secrets locaux : JAMAIS dans Git
├── .gitignore            # .venv, .env, __pycache__, données lourdes
├── src/fraude/
│   ├── __init__.py
│   ├── features.py       # préparation des données
│   ├── train.py          # entraînement, point d'entrée en ligne de commande
│   └── api.py            # l'API FastAPI
└── tests/
    └── test_features.py  # lancé par pytest
```

## Trois réflexes de pro

- **Des arguments en ligne de commande** avec `argparse`, plutôt que des valeurs écrites en dur : `python train.py data.csv --seuil 0.3`.
- **La configuration dans l'environnement** : chemins, ports et clés d'API viennent de variables d'environnement (`os.environ`), pas du code. C'est le principe des applications « twelve-factor ».
- **Des journaux, pas des `print`** : le module `logging` donne un niveau (DEBUG, INFO, WARNING, ERROR), l'heure et la source de chaque message, et s'envoie où l'on veut.

```python
import argparse
p = argparse.ArgumentParser(description="Entraîne le modèle de fraude")
p.add_argument("donnees")
p.add_argument("--seuil", type=float, default=0.5)
args = p.parse_args(["transactions.csv", "--seuil", "0.3"])   # sur ton ordinateur : p.parse_args()
print(args.donnees, args.seuil)
```

> **À retenir** : un environnement virtuel par projet, des dépendances figées, une structure claire, des arguments, une configuration par variables d'environnement et des journaux. Les secrets restent hors de Git.
''',
"tasks": [
  "Créer le dossier d'un projet avec un environnement virtuel, un requirements.txt et un .gitignore",
  "Écrire un script train.py qui prend ses paramètres avec argparse et l'exécuter depuis le terminal",
  "Retrouver avec grep toutes les lignes ERROR d'un fichier de journal et les compter avec wc -l",
  "Installer uv et recréer le même environnement avec uv venv et uv pip install",
],
"exercises": [
 E("e-sh-a", "Une ligne de commande avec argparse",
   "Écris `creer_parser()` qui renvoie un `argparse.ArgumentParser` avec : un argument positionnel `donnees` ; une option `--seuil` (float, 0.5 par défaut) ; une option `--modele` limitée aux choix `logreg` et `foret` (`logreg` par défaut) ; un drapeau `--verbeux` (False par défaut, True s'il est présent).",
   r'''import argparse

def creer_parser():
    pass
''',
   r'''import argparse

def creer_parser():
    p = argparse.ArgumentParser(description="Entraîne le modèle de fraude")
    p.add_argument("donnees")
    p.add_argument("--seuil", type=float, default=0.5)
    p.add_argument("--modele", choices=["logreg", "foret"], default="logreg")
    p.add_argument("--verbeux", action="store_true")
    return p

print(creer_parser().parse_args(["tx.csv", "--seuil", "0.3", "--verbeux"]))
''',
   r'''p = creer_parser()
a = p.parse_args(["tx.csv"])
assert a.donnees == "tx.csv" and a.seuil == 0.5 and a.modele == "logreg" and a.verbeux is False, "Vérifie les valeurs par défaut : seuil 0.5, modele logreg, verbeux False."
b = p.parse_args(["x.csv", "--seuil", "0.25", "--modele", "foret", "--verbeux"])
assert b.seuil == 0.25 and isinstance(b.seuil, float), "--seuil doit être converti en float (type=float)."
assert b.modele == "foret" and b.verbeux is True, "--modele foret et --verbeux doivent être pris en compte (action='store_true')."
import io, contextlib
try:
    with contextlib.redirect_stderr(io.StringIO()):
        p.parse_args(["x.csv", "--modele", "svm"])
    refuse = False
except SystemExit:
    refuse = True
assert refuse, "--modele doit refuser une valeur hors de logreg et foret (choices=...)."
''',
   "add_argument(\"--modele\", choices=[...], default=...) et add_argument(\"--verbeux\", action=\"store_true\")."),
 E("e-sh-b", "La configuration par l'environnement",
   "Écris `charger_config(env)` : `env` est un dictionnaire comme `os.environ`. Renvoie un dictionnaire avec `modele` (variable `MODELE_CHEMIN`, obligatoire : lève une `ValueError` qui la nomme si elle manque), `port` (variable `PORT`, entier, 8000 par défaut), `debug` (variable `DEBUG`, True si elle vaut « 1 », « true » ou « oui », sans tenir compte des majuscules ; False par défaut) et `seuil` (variable `SEUIL`, float, 0.5 par défaut).",
   r'''def charger_config(env):
    pass
''',
   r'''def charger_config(env):
    if "MODELE_CHEMIN" not in env:
        raise ValueError("La variable d'environnement MODELE_CHEMIN est obligatoire.")
    return {
        "modele": env["MODELE_CHEMIN"],
        "port": int(env.get("PORT", 8000)),
        "debug": env.get("DEBUG", "").lower() in ("1", "true", "oui"),
        "seuil": float(env.get("SEUIL", 0.5)),
    }

import os
print(charger_config({"MODELE_CHEMIN": "modeles/fraude.joblib", "DEBUG": "True"}))
''',
   r'''c = charger_config({"MODELE_CHEMIN": "m.joblib"})
assert c == {"modele": "m.joblib", "port": 8000, "debug": False, "seuil": 0.5}, f"Valeurs par défaut attendues : port 8000, debug False, seuil 0.5 ; tu as {c}."
c2 = charger_config({"MODELE_CHEMIN": "m", "PORT": "9000", "DEBUG": "OUI", "SEUIL": "0.3"})
assert c2["port"] == 9000 and c2["debug"] is True and c2["seuil"] == 0.3, "Les variables d'environnement sont des chaînes : convertis PORT en int, SEUIL en float, et DEBUG sans tenir compte des majuscules."
assert charger_config({"MODELE_CHEMIN": "m", "DEBUG": "0"})["debug"] is False, "DEBUG=0 doit donner False."
try:
    charger_config({}); ok = False
except ValueError as e:
    ok = "MODELE_CHEMIN" in str(e)
assert ok, "Sans MODELE_CHEMIN, lève une ValueError dont le message nomme la variable."
''',
   "env.get(\"PORT\", 8000) donne une valeur par défaut ; .lower() in (\"1\", \"true\", \"oui\") pour le booléen."),
 E("e-sh-c", "Des journaux plutôt que des print",
   "Écris `creer_logger(flux)` qui renvoie le logger nommé `fraude`, de niveau INFO, avec **un seul** gestionnaire qui écrit dans `flux` au format `%(levelname)s | %(name)s | %(message)s` (vide les gestionnaires existants d'abord, et mets `propagate` à False). Puis `journaliser(logger, id_tx, score)` : écris `transaction <id> : score <score avec 2 décimales>` en INFO si le score est inférieur à 0.5, en WARNING sinon.",
   r'''import io
import logging

def creer_logger(flux):
    pass

def journaliser(logger, id_tx, score):
    pass
''',
   r'''import io
import logging

def creer_logger(flux):
    logger = logging.getLogger("fraude")
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    h = logging.StreamHandler(flux)
    h.setFormatter(logging.Formatter("%(levelname)s | %(name)s | %(message)s"))
    logger.addHandler(h)
    logger.propagate = False
    return logger

def journaliser(logger, id_tx, score):
    niveau = logging.INFO if score < 0.5 else logging.WARNING
    logger.log(niveau, f"transaction {id_tx} : score {score:.2f}")

flux = io.StringIO()
log = creer_logger(flux)
journaliser(log, 101, 0.12); journaliser(log, 102, 0.87)
print(flux.getvalue())
''',
   r'''import io, logging
f = io.StringIO()
lg = creer_logger(f)
assert lg is not None and lg.name == "fraude", "creer_logger doit renvoyer le logger nommé « fraude »."
journaliser(lg, 7, 0.123); journaliser(lg, 8, 0.9)
lg.debug("invisible")
lignes = f.getvalue().strip().splitlines()
assert lignes == ["INFO | fraude | transaction 7 : score 0.12", "WARNING | fraude | transaction 8 : score 0.90"], f"Journal attendu sur deux lignes au bon format ; tu as {lignes}."
f2 = io.StringIO(); lg2 = creer_logger(f2); journaliser(lg2, 1, 0.1)
assert len(lg2.handlers) == 1, "Appeler creer_logger deux fois ne doit pas empiler les gestionnaires : vide-les d'abord."
assert f2.getvalue().count("transaction 1") == 1, "Chaque message ne doit apparaître qu'une fois."
''',
   "logging.getLogger(\"fraude\"), handlers.clear(), StreamHandler(flux), setFormatter(...), puis logger.log(niveau, message)."),
]},
# ================================================================ Streamlit
{"id": "l-streamlit", "title": "Tableaux de bord avec Streamlit", "minutes": 70,
"body": r'''
**Streamlit** transforme un script Python en application web, sans HTML ni JavaScript. C'est l'outil standard pour montrer un modèle à des collègues, faire une démo, ou explorer des données de façon interactive. Il demande un serveur : tout se fait **sur ton ordinateur**.

## Une application en 15 lignes

```pycode
# app.py   →   streamlit run app.py
import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Détection de fraude")
seuil = st.slider("Seuil d'alerte", 0.0, 1.0, 0.5)
fichier = st.file_uploader("Transactions (CSV)", type="csv")
if fichier:
    df = pd.read_csv(fichier)
    df["alerte"] = df["score"] >= seuil
    col1, col2 = st.columns(2)
    col1.metric("Transactions", len(df))
    col2.metric("Alertes", int(df["alerte"].sum()))
    st.plotly_chart(px.histogram(df, x="score", color="alerte"))
    st.dataframe(df[df["alerte"]])
```

## Le modèle d'exécution : tout se relance

Le point clé à comprendre : **à chaque interaction** (un curseur déplacé, un bouton cliqué), Streamlit **réexécute tout le script**, de haut en bas. C'est ce qui rend le code si simple, mais ça a deux conséquences :

1. Un calcul lent (charger un modèle, lire un gros fichier) serait refait à chaque clic. On le met en **cache** avec `@st.cache_data` (pour des données) ou `@st.cache_resource` (pour un modèle, une connexion).
2. Une variable Python normale est remise à zéro à chaque exécution. Pour garder une valeur entre deux interactions, on utilise `st.session_state`.

```pycode
@st.cache_resource
def charger_modele():
    return joblib.load("modeles/fraude.joblib")     # une seule fois

@st.cache_data(ttl=600)
def lire_transactions(chemin):
    return pd.read_parquet(chemin)                 # remis à jour toutes les 10 minutes

if "historique" not in st.session_state:
    st.session_state.historique = []
if st.button("Analyser"):
    st.session_state.historique.append(seuil)
```

## Déployer

- **Streamlit Community Cloud** : gratuit, relié à un dépôt GitHub public, en deux clics.
- **Hugging Face Spaces** : idéal pour une démo de modèle.
- **Docker** sur un serveur : la méthode des leçons suivantes, pour un usage d'entreprise.

> **À retenir** : un script = une application. Tout se réexécute à chaque interaction : cache pour ce qui est lent, `session_state` pour ce qui doit durer.
''',
"tasks": [
  "Installer streamlit et lancer streamlit hello pour voir les exemples",
  "Construire un tableau de bord sur le jeu Immo : filtres par quartier, carte des prix, histogramme",
  "Charger un modèle entraîné avec @st.cache_resource et ajouter un formulaire de prédiction",
  "Déployer l'application sur Streamlit Community Cloud depuis GitHub",
],
"exercises": [
 E("e-st-a", "Coder son propre cache",
   "Pour comprendre `@st.cache_data`, écris le décorateur `cache_donnees(ttl=None, horloge=time.time)`. La fonction décorée garde ses résultats dans un dictionnaire indexé par ses arguments (utilise `repr((args, sorted(kwargs.items())))` comme clé). Si `ttl` est donné, un résultat plus vieux que `ttl` secondes (mesuré avec `horloge()`) est recalculé. La fonction décorée a aussi une méthode `clear()` qui vide le cache.",
   r'''import time

def cache_donnees(ttl=None, horloge=time.time):
    pass
''',
   r'''import time

def cache_donnees(ttl=None, horloge=time.time):
    def decorateur(f):
        memoire = {}
        def enveloppe(*args, **kwargs):
            cle = repr((args, sorted(kwargs.items())))
            maintenant = horloge()
            if cle in memoire:
                valeur, quand = memoire[cle]
                if ttl is None or maintenant - quand < ttl:
                    return valeur
            valeur = f(*args, **kwargs)
            memoire[cle] = (valeur, maintenant)
            return valeur
        enveloppe.clear = memoire.clear
        return enveloppe
    return decorateur

@cache_donnees()
def lent(n):
    time.sleep(0.2)
    return n * 2

t = time.perf_counter(); lent(21); lent(21); print(f"{time.perf_counter() - t:.2f} s pour deux appels")
''',
   r'''appels = []
@cache_donnees()
def f(a, b=1):
    appels.append((a, b)); return a + b
assert f(1) == 2 and f(1) == 2 and len(appels) == 1, "Le deuxième appel avec les mêmes arguments doit venir du cache."
f(1, b=5); f(2)
assert len(appels) == 3, "Des arguments différents doivent déclencher un nouveau calcul."
f.clear(); f(1)
assert len(appels) == 4, "Après clear(), le cache est vide."
t = [0.0]; vus = []
@cache_donnees(ttl=10, horloge=lambda: t[0])
def g(x):
    vus.append(x); return x
g(3); t[0] = 5; g(3)
assert len(vus) == 1, "Avant l'expiration du ttl, le résultat vient du cache."
t[0] = 12; g(3)
assert len(vus) == 2, "Après ttl secondes, le résultat doit être recalculé."
''',
   "Trois niveaux de fonctions : cache_donnees(ttl, horloge) → decorateur(f) → enveloppe(*args, **kwargs). Stocke (valeur, instant) dans un dictionnaire."),
]},
# ================================================================ Docker
{"id": "l-docker", "title": "Docker pour l'IA", "minutes": 110,
"body": r'''
« Ça marche sur ma machine » : c'est le problème que règle **Docker**. Une **image** contient ton code, Python, les bibliothèques et la configuration système. Un **conteneur** est une image en cours d'exécution. La même image tourne à l'identique sur ton portable, sur le serveur de test et en production, sur AWS ou ailleurs.

## Le vocabulaire

| Terme | C'est quoi |
| --- | --- |
| **Dockerfile** | La recette, ligne par ligne, pour construire l'image |
| **Image** | Le résultat, figé et versionné (`fraude-api:1.2.0`) |
| **Conteneur** | Une image lancée ; on peut en lancer plusieurs |
| **Registre** | Le dépôt d'images : Docker Hub, AWS ECR, GitHub Container Registry |
| **Volume** | Un dossier qui survit au conteneur (données, modèles) |

## Un bon Dockerfile pour une API de modèle

```pycode
FROM python:3.12-slim

WORKDIR /app

# 1. Les dépendances d'abord : cette couche reste en cache tant que requirements.txt ne change pas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Le code ensuite : il change souvent
COPY . .

# 3. Ne pas tourner en root
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
CMD ["uvicorn", "src.fraude.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Chaque instruction crée une **couche**. Au build suivant, Docker réutilise les couches dont rien n'a changé. Dès qu'une couche change, toutes celles qui suivent sont reconstruites. D'où la règle d'or : **ce qui change rarement en haut, ce qui change souvent en bas**. Si tu copies tout le code avant d'installer les dépendances, la moindre modification d'un fichier relance l'installation complète.

```viz dockercache
```

## Les commandes du quotidien

```pycode
docker build -t fraude-api:1.0 .                         # construire
docker run -d -p 8000:8000 --env-file .env fraude-api:1.0  # lancer en arrière-plan
docker ps                                                # conteneurs actifs
docker logs -f <id>                                      # suivre les journaux
docker exec -it <id> bash                                # entrer dans le conteneur
docker stop <id>
docker images ; docker system prune                      # lister, faire le ménage
```

## Les spécificités de l'IA

- **La taille** : PyTorch avec CUDA pèse plusieurs Go. Utilise les images `-slim`, un fichier `.dockerignore` (ni données, ni `.venv`, ni `.git`), et les **builds multi-étapes** : on compile dans une image complète, on copie seulement le résultat dans une image légère.
- **Les modèles** : un modèle de quelques Mo peut être copié dans l'image. Un gros modèle se télécharge au démarrage depuis un stockage (S3, Hugging Face Hub) ou se monte en volume.
- **Le GPU** : il faut une image de base CUDA (`nvidia/cuda:12.4.1-runtime-ubuntu22.04` ou `pytorch/pytorch`) et `docker run --gpus all`.
- **Les secrets** : jamais dans l'image. On les passe au lancement (`--env-file`, variables d'environnement du service cloud).

## Docker Compose : plusieurs services

Une vraie application, c'est souvent une API, une base de données, un cache et un tableau de bord. **Docker Compose** les décrit dans un seul fichier et les lance ensemble avec `docker compose up`.

```pycode
# compose.yaml
services:
  api:
    build: .
    ports: ["8000:8000"]
    env_file: .env
    depends_on: [db]
  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes: ["pgdata:/var/lib/postgresql/data"]
  dashboard:
    build: ./dashboard
    ports: ["8501:8501"]
volumes:
  pgdata:
```

Dans ce réseau, l'API joint la base par son nom de service : `postgresql://...@db:5432/...`.

> **À retenir** : Dockerfile → image → conteneur. Dépendances avant le code pour profiter du cache. Image slim, `.dockerignore`, utilisateur non root, secrets hors de l'image. Compose pour plusieurs services.
''',
"tasks": [
  "Installer Docker Desktop et lancer docker run hello-world",
  "Écrire un Dockerfile pour une petite API FastAPI, la construire et l'appeler sur localhost:8000",
  "Modifier une ligne de code, reconstruire et observer quelles couches viennent du cache",
  "Écrire un compose.yaml avec l'API et une base PostgreSQL, et les lancer avec docker compose up",
],
"exercises": [
 E("e-dk-a", "Un Dockerfile propre",
   "Remplis la chaîne `dockerfile` avec un Dockerfile pour l'API `main:app` qui respecte les bonnes pratiques : image de base `python:3.12-slim` ; `WORKDIR /app` ; copier `requirements.txt` seul, puis `RUN pip install --no-cache-dir -r requirements.txt`, **avant** de copier le reste du code avec `COPY . .` ; créer un utilisateur avec `useradd` et passer dessus avec `USER` ; `EXPOSE 8000` ; et un `CMD` en forme JSON qui lance uvicorn sur `0.0.0.0` et le port 8000.",
   r'''dockerfile = """
FROM python:3.12
COPY . .
RUN pip install -r requirements.txt
CMD uvicorn main:app
"""
''',
   r'''dockerfile = """
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd --create-home appuser
USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
print(dockerfile)
''',
   r'''import json
L = [l.strip() for l in dockerfile.strip().splitlines() if l.strip() and not l.strip().startswith("#")]
I = [l.split(None, 1)[0].upper() for l in L]
pos = lambda pred: next((i for i, l in enumerate(L) if pred(l)), None)
assert L[0].lower().startswith("from python:3.12-slim"), "La première instruction doit être FROM python:3.12-slim : une image légère."
assert "WORKDIR /app" in L, "Fixe le dossier de travail avec WORKDIR /app."
i_req = pos(lambda l: l.upper().startswith("COPY") and "requirements.txt" in l and " . ." not in l + " ")
i_pip = pos(lambda l: l.upper().startswith("RUN") and "pip install" in l)
i_all = pos(lambda l: l.upper().startswith("COPY") and l.split()[1:] == [".", "."])
assert None not in (i_req, i_pip, i_all), "Il faut trois étapes : COPY requirements.txt ., RUN pip install ..., puis COPY . ."
assert i_req < i_pip < i_all, "Ordre attendu : copier requirements.txt, installer, puis copier tout le code (pour profiter du cache)."
assert "--no-cache-dir" in L[i_pip] and "-r requirements.txt" in L[i_pip], "pip install doit utiliser --no-cache-dir et -r requirements.txt."
i_user = pos(lambda l: l.upper().startswith("USER"))
assert pos(lambda l: "useradd" in l) is not None and i_user is not None and L[i_user].split()[1] != "root", "Crée un utilisateur avec useradd et passe dessus avec USER (pas root)."
assert "EXPOSE 8000" in L, "Documente le port avec EXPOSE 8000."
assert I[-1] == "CMD", "La dernière instruction doit être CMD."
cmd = json.loads(L[-1][3:].strip())
assert isinstance(cmd, list) and cmd[0] == "uvicorn" and "main:app" in cmd and "0.0.0.0" in cmd and "8000" in cmd, "CMD doit être en forme JSON : [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]."
''',
   "Reprends le Dockerfile de la leçon : FROM, WORKDIR, COPY requirements.txt ., RUN pip install --no-cache-dir -r requirements.txt, COPY . ., useradd, USER, EXPOSE, CMD [...]."),
 E("e-dk-b", "Ce qui ne doit pas entrer dans l'image",
   "Remplis la liste `dockerignore` (une entrée par ligne du futur fichier `.dockerignore`) pour exclure au moins : le dossier `.git`, l'environnement virtuel `.venv`, les caches `__pycache__`, le fichier de secrets `.env`, et le dossier de données brutes `data/`. Puis écris `est_ignore(chemin, motifs)` qui renvoie True si le chemin est exclu : un motif finissant par `/` exclut tout ce qui commence par ce dossier ; sinon, utilise `fnmatch` sur le chemin complet **et** sur chacune de ses parties séparées par `/`.",
   r'''from fnmatch import fnmatch

dockerignore = []

def est_ignore(chemin, motifs):
    pass
''',
   r'''from fnmatch import fnmatch

dockerignore = [".git", ".venv", "__pycache__", "*.pyc", ".env", "data/", "notebooks/"]

def est_ignore(chemin, motifs):
    for m in motifs:
        if m.endswith("/"):
            if chemin.startswith(m) or chemin == m.rstrip("/"):
                return True
        elif fnmatch(chemin, m) or any(fnmatch(p, m) for p in chemin.split("/")):
            return True
    return False

for c in ["src/api.py", ".env", "data/brut.csv", "src/__pycache__/api.cpython-312.pyc"]:
    print(c, "→", "exclu" if est_ignore(c, dockerignore) else "copié")
''',
   r'''for m in [".git", ".venv", "__pycache__", ".env", "data/"]:
    assert m in dockerignore, f"Ajoute « {m} » à dockerignore."
assert est_ignore(".env", dockerignore), ".env contient des secrets : il doit être exclu."
assert est_ignore("data/brut/tx.csv", dockerignore), "Tout ce qui est sous data/ doit être exclu."
assert est_ignore("src/__pycache__/x.pyc", dockerignore), "Un dossier __pycache__ doit être exclu où qu'il soit."
assert est_ignore(".git/config", ["*.tmp", ".git"]) or est_ignore(".git", [".git"]), "Le dossier .git doit être exclu."
assert not est_ignore("src/api.py", dockerignore) and not est_ignore("requirements.txt", dockerignore), "Le code et requirements.txt doivent être copiés."
assert est_ignore("rapport.tmp", ["*.tmp"]) and not est_ignore("rapport.txt", ["*.tmp"]), "Les motifs avec * doivent fonctionner (fnmatch)."
''',
   "chemin.split(\"/\") donne les parties du chemin ; fnmatch(partie, motif) teste chacune."),
]},
# ================================================================ EC2
{"id": "l-ec2", "title": "Déployer sur un serveur EC2", "minutes": 80,
"body": r'''
Ton image Docker fonctionne en local. Il faut maintenant la faire tourner sur une machine accessible depuis Internet. Sur AWS, la brique de base est **EC2** : une machine virtuelle louée à l'heure. Le module Cloud de la vague 1 t'a donné les bases d'AWS ; ici, on déploie pour de vrai.

## Les étapes

1. **Lancer une instance** : choisir une image (Ubuntu 24.04 ou Amazon Linux 2023), un type (`t3.small` suffit pour une API scikit-learn ; `g5.xlarge` pour un GPU), une **paire de clés** SSH et un **groupe de sécurité**.
2. **Se connecter** : `ssh -i ma-cle.pem ubuntu@<ip-publique>`.
3. **Installer Docker**, récupérer l'image (depuis ECR ou Docker Hub) et la lancer avec `--restart unless-stopped` pour qu'elle redémarre avec la machine.
4. **Mettre un proxy devant** : Nginx ou Caddy reçoit le trafic sur les ports 80 et 443, gère le HTTPS, et le transmet à l'API sur le port 8000.

```pycode
# sur l'instance
sudo apt update && sudo apt install -y docker.io
sudo usermod -aG docker ubuntu        # puis se reconnecter
docker run -d --restart unless-stopped -p 8000:8000 --env-file .env monregistre/fraude-api:1.0
curl localhost:8000/sante
```

## Le groupe de sécurité : le pare-feu

Le **groupe de sécurité** décide qui peut joindre quel port. C'est là que se font la plupart des erreurs graves :

| Port | Service | Ouvert à |
| --- | --- | --- |
| 22 | SSH | **Ton adresse IP seulement** (`x.x.x.x/32`), jamais 0.0.0.0/0 |
| 80, 443 | HTTP, HTTPS | Tout le monde (0.0.0.0/0) |
| 8000 | L'API directement | Personne : elle passe par le proxy |
| 5432, 3306, 6379, 27017 | Bases de données | Jamais Internet : seulement le réseau interne |

Des robots scannent Internet en permanence. Une base de données ouverte à 0.0.0.0/0 est trouvée et attaquée en quelques heures.

## Ce qu'il faut surveiller

- **Le coût** : une instance tourne et se paie 24 h sur 24 ; une `t3.small` coûte environ 15 € par mois, une instance GPU `g5.xlarge` environ 750 €. Arrête ce qui ne sert pas, et règle une **alerte de budget**.
- **Les secrets** : dans un fichier `.env` lisible seulement par toi, ou mieux dans AWS Secrets Manager.
- **Les mises à jour** : déployer une nouvelle version, c'est construire, pousser l'image, puis `docker pull` et relancer sur le serveur. Un pipeline CI/CD (GitHub Actions) automatise tout ça : tu le verras dans le Lead.

## Et sans gérer de serveur ?

EC2 apprend les bases, mais on peut aussi déléguer : **AWS App Runner**, **Google Cloud Run** ou **Render** lancent directement une image Docker et gèrent le HTTPS et la montée en charge. **SageMaker** est la plateforme ML gérée d'AWS.

> **À retenir** : instance + clé SSH + groupe de sécurité + Docker + proxy HTTPS. SSH limité à ton IP, bases jamais exposées, budget surveillé.
''',
"tasks": [
  "Lancer une instance t3.micro (offre gratuite) avec Ubuntu, s'y connecter en SSH",
  "Y installer Docker, lancer ton image d'API et l'appeler depuis ton ordinateur",
  "Mettre Caddy devant l'API pour avoir HTTPS automatiquement avec un nom de domaine",
  "Créer une alerte de budget AWS à 10 € et arrêter l'instance après l'exercice",
],
"exercises": [
 E("e-ec2-a", "Auditer un groupe de sécurité",
   "Écris `auditer(regles)` : `regles` est une liste de dictionnaires `{\"port\": int, \"source\": str}`. Renvoie la liste des problèmes, dans l'ordre des règles, sous forme de chaînes : `\"SSH ouvert à Internet\"` pour le port 22 depuis `0.0.0.0/0` ; `\"Base de données <port> ouverte à Internet\"` pour les ports 5432, 3306, 6379 et 27017 depuis `0.0.0.0/0` ; `\"Port <port> ouvert à Internet\"` pour tout autre port depuis `0.0.0.0/0`, **sauf** 80 et 443, qui sont normaux.",
   r'''def auditer(regles):
    pass
''',
   r'''BASES = {5432, 3306, 6379, 27017}

def auditer(regles):
    problemes = []
    for r in regles:
        if r["source"] != "0.0.0.0/0" or r["port"] in (80, 443):
            continue
        if r["port"] == 22:
            problemes.append("SSH ouvert à Internet")
        elif r["port"] in BASES:
            problemes.append(f"Base de données {r['port']} ouverte à Internet")
        else:
            problemes.append(f"Port {r['port']} ouvert à Internet")
    return problemes

print(auditer([{"port": 22, "source": "0.0.0.0/0"}, {"port": 443, "source": "0.0.0.0/0"}, {"port": 5432, "source": "0.0.0.0/0"}]))
''',
   r'''R = [{"port": 22, "source": "0.0.0.0/0"}, {"port": 80, "source": "0.0.0.0/0"}, {"port": 443, "source": "0.0.0.0/0"},
     {"port": 5432, "source": "0.0.0.0/0"}, {"port": 8000, "source": "0.0.0.0/0"}, {"port": 22, "source": "81.2.3.4/32"},
     {"port": 6379, "source": "10.0.0.0/16"}]
r = auditer(R)
assert r == ["SSH ouvert à Internet", "Base de données 5432 ouverte à Internet", "Port 8000 ouvert à Internet"], f"Problèmes attendus : SSH, base 5432, port 8000 ; tu as {r}."
assert auditer([{"port": 443, "source": "0.0.0.0/0"}, {"port": 22, "source": "1.2.3.4/32"}]) == [], "HTTPS ouvert et SSH limité à une IP ne posent pas de problème."
''',
   "Ignore d'abord les règles qui ne viennent pas de 0.0.0.0/0, et les ports 80 et 443. Ensuite, trois cas."),
]},
# ================================================================ MLflow
{"id": "l-mlflow", "title": "MLflow : suivre et packager ses modèles", "minutes": 90,
"body": r'''
Après une semaine d'essais, la question arrive toujours : « quel modèle avait le meilleur score, avec quels paramètres, sur quelles données ? ». Des noms de fichiers comme `modele_final_v3_vraiment_final.pkl` ne suffisent pas. **MLflow** est l'outil open source standard pour **suivre les expériences** et **gérer les modèles**.

## Les briques

| Brique | Rôle |
| --- | --- |
| **Tracking** | Chaque entraînement est un **run** : on y enregistre des paramètres, des métriques (éventuellement par époque), des tags et des fichiers (graphiques, modèle) |
| **Expériences** | Des groupes de runs, par exemple « fraude-v2 » |
| **Models** | Un format standard pour enregistrer un modèle avec sa signature et ses dépendances, et le recharger n'importe où |
| **Registry** | Le registre des versions de modèles, avec des **alias** (`champion`, `challenger`) pour savoir lequel est en production |

## Suivre un entraînement

```pycode
import mlflow
mlflow.set_tracking_uri("http://localhost:5000")       # ou un serveur partagé
mlflow.set_experiment("fraude")

for C in [0.01, 0.1, 1, 10]:
    with mlflow.start_run(run_name=f"logreg-C{C}"):
        mlflow.log_param("C", C)
        modele = make_pipeline(StandardScaler(), LogisticRegression(C=C)).fit(X_train, y_train)
        mlflow.log_metric("auc", roc_auc_score(y_test, modele.predict_proba(X_test)[:, 1]))
        mlflow.sklearn.log_model(modele, name="modele", input_example=X_test.head(3))

meilleurs = mlflow.search_runs(order_by=["metrics.auc DESC"])   # un DataFrame pandas
```

`mlflow ui` ouvre une interface web pour comparer les runs, tracer les courbes et filtrer. `mlflow.autolog()` enregistre automatiquement les paramètres et les métriques de scikit-learn, XGBoost ou PyTorch.

## Le registre et le passage en production

```pycode
version = mlflow.register_model(f"runs:/{run_id}/modele", "fraude")
client = mlflow.MlflowClient()
client.set_registered_model_alias("fraude", "champion", version.version)

modele = mlflow.pyfunc.load_model("models:/fraude@champion")   # dans l'API
```

L'API charge toujours `@champion` : passer un nouveau modèle en production, c'est déplacer l'alias, sans toucher au code. Revenir en arrière aussi.

## Pourquoi c'est important

- **Reproductibilité** : chaque modèle en production est relié au run, au code (commit Git) et aux données qui l'ont produit.
- **Comparaison** : on choisit sur des chiffres, pas sur des souvenirs.
- **Collaboration** : toute l'équipe voit les mêmes expériences.

Des alternatives existent (Weights & Biases, très utilisé en deep learning ; DVC pour versionner les données), mais les concepts sont les mêmes.

> **À retenir** : un run = paramètres + métriques + fichiers + modèle. Le registre versionne les modèles, et un alias désigne celui qui est en production.
''',
"tasks": [
  "Installer mlflow, lancer mlflow ui et ouvrir http://localhost:5000",
  "Suivre 10 entraînements du jeu Immo avec des hyperparamètres différents et les comparer dans l'interface",
  "Enregistrer le meilleur modèle dans le registre avec l'alias champion et le recharger avec models:/...@champion",
  "Essayer mlflow.autolog() sur une recherche par grille de scikit-learn",
],
"exercises": [
 E("e-mlf-a", "Ton propre suivi d'expériences",
   "Écris une classe `Run(nom)` avec les attributs `nom`, `params` (dict), `metriques` (dict : nom → liste de tuples `(step, valeur)`), `statut` (\"RUNNING\" au départ) et les méthodes `log_param(cle, valeur)` et `log_metric(cle, valeur, step=None)`. Puis une classe `Suivi` avec une liste `runs` et une méthode `run(nom)`, un **gestionnaire de contexte** (`@contextmanager`) qui crée le run, l'ajoute à la liste, le fournit au bloc `with`, et met son statut à \"FINISHED\" à la fin, ou à \"FAILED\" si une exception survient (qu'il laisse ensuite remonter). Ajoute `meilleur(metrique, mode=\"max\")` qui renvoie le run terminé dont la **dernière** valeur de cette métrique est la plus grande (ou la plus petite si `mode=\"min\"`).",
   r'''from contextlib import contextmanager

class Run:
    pass

class Suivi:
    pass
''',
   SUIVI + r'''
suivi = Suivi()
for C in [0.1, 1, 10]:
    with suivi.run(f"logreg-C{C}") as r:
        r.log_param("C", C)
        r.log_metric("auc", 0.8 + C / 100)
print(suivi.meilleur("auc").nom)
suivi.tableau()
''',
   r'''s = Suivi()
with s.run("a") as r:
    r.log_param("C", 1); r.log_metric("auc", 0.7, step=0); r.log_metric("auc", 0.9, step=1)
assert len(s.runs) == 1 and s.runs[0] is r, "Le run doit être ajouté à suivi.runs et fourni au bloc with."
assert r.statut == "FINISHED", "À la fin du bloc with, le statut doit être FINISHED."
assert r.params == {"C": 1} and r.metriques["auc"] == [(0, 0.7), (1, 0.9)], "log_metric garde l'historique : une liste de (step, valeur)."
with s.run("b") as r2:
    r2.log_metric("auc", 0.85)
try:
    with s.run("c") as r3:
        r3.log_metric("auc", 0.99); raise RuntimeError("panne")
    remonte = False
except RuntimeError:
    remonte = True
assert remonte and r3.statut == "FAILED", "Si le bloc lève une exception, le statut devient FAILED et l'exception remonte."
assert s.meilleur("auc").nom == "a", "meilleur doit comparer la dernière valeur, et ignorer les runs FAILED."
assert s.meilleur("auc", mode="min").nom == "b", "Avec mode='min', on prend la plus petite."
''',
   "Avec @contextmanager : crée le run, yield r dans un try ; après le yield, FINISHED ; dans except, FAILED puis raise."),
 E("e-mlf-b", "Suivre une recherche d'hyperparamètres",
   "La classe `Suivi` (avec une méthode `tableau()` qui renvoie un DataFrame façon `mlflow.search_runs`) est fournie, ainsi que les données Immo. Pour chaque `alpha` dans `[0.1, 1, 10, 100, 1000]`, ouvre un run nommé `ridge-<alpha>`, enregistre le paramètre `alpha`, entraîne `make_pipeline(pre, Ridge(alpha=alpha))`, et enregistre la métrique `mae`, l'erreur absolue moyenne en validation croisée à 5 plis (`cross_val_score` avec `scoring=\"neg_mean_absolute_error\"`, puis le signe opposé de la moyenne). Mets dans `meilleur_alpha` l'alpha du meilleur run.",
   IMMO_PRE + SUIVI + r'''from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score

suivi = Suivi()
meilleur_alpha = None
''',
   IMMO_PRE + SUIVI + r'''from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score

suivi = Suivi()
for alpha in [0.1, 1, 10, 100, 1000]:
    with suivi.run(f"ridge-{alpha}") as r:
        r.log_param("alpha", alpha)
        scores = cross_val_score(make_pipeline(pre, Ridge(alpha=alpha)), X, y, cv=5, scoring="neg_mean_absolute_error")
        r.log_metric("mae", -scores.mean())
meilleur_alpha = suivi.meilleur("mae", mode="min").params["alpha"]
print("meilleur alpha :", meilleur_alpha)
suivi.tableau().sort_values("metrics.mae")
''',
   r'''from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score
assert len(suivi.runs) == 5 and [r.nom for r in suivi.runs] == [f"ridge-{a}" for a in [0.1, 1, 10, 100, 1000]], "Il faut 5 runs nommés ridge-0.1, ridge-1, …, ridge-1000."
assert all(r.statut == "FINISHED" for r in suivi.runs), "Tous les runs doivent être terminés."
t = suivi.tableau()
assert "params.alpha" in t and "metrics.mae" in t, "Chaque run doit enregistrer le paramètre alpha et la métrique mae."
ref = {a: -cross_val_score(make_pipeline(pre, Ridge(alpha=a)), X, y, cv=5, scoring="neg_mean_absolute_error").mean() for a in [1, 1000]}
m = dict(zip(t["params.alpha"], t["metrics.mae"]))
assert abs(m[1] - ref[1]) < 1, f"La MAE pour alpha = 1 devrait valoir {ref[1]:.0f} € ; tu as {m[1]:.0f}. Prends l'opposé de la moyenne des scores."
assert meilleur_alpha == min(m, key=m.get), "meilleur_alpha doit être l'alpha de plus petite MAE."
''',
   "with suivi.run(f\"ridge-{alpha}\") as r: … r.log_metric(\"mae\", -scores.mean()). Puis suivi.meilleur(\"mae\", mode=\"min\").params[\"alpha\"]."),
]},
# ================================================================ Async
{"id": "l-async", "title": "Le développement asynchrone", "minutes": 100,
"body": r'''
Une application d'IA passe l'essentiel de son temps à **attendre** : la réponse d'un LLM (plusieurs secondes), une base de données, une API externe. Pendant ce temps, le processeur ne fait rien. La **programmation asynchrone** permet de lancer d'autres tâches pendant l'attente. C'est ce qui permet à une API FastAPI de servir des centaines d'utilisateurs avec un seul processus, ou à un pipeline RAG d'interroger dix sources en même temps.

## Synchrone contre asynchrone

```viz async
```

Imagine un serveur de restaurant. En synchrone, il prend une commande, attend en cuisine que le plat soit prêt, le sert, puis passe à la table suivante. En asynchrone, il transmet la commande et va prendre les autres pendant que la cuisine travaille.

## Les mots-clés

- `async def` déclare une **coroutine** : une fonction qui peut se mettre en pause.
- `await` met la coroutine en pause jusqu'au résultat, et rend la main à la **boucle d'événements** (*event loop*), qui fait avancer les autres tâches.
- `asyncio.gather(...)` lance plusieurs coroutines **en même temps** et attend tous les résultats, dans l'ordre.

Dans la plateforme, comme dans Jupyter, `await` s'utilise directement dans une cellule. Dans un script, on lance tout avec `asyncio.run(main())`.

```python
import asyncio, time

async def appeler_llm(question):
    await asyncio.sleep(0.3)               # simule 0,3 s d'attente réseau
    return f"réponse à « {question} »"

questions = ["Qu'est-ce qu'un RAG ?", "Et un agent ?", "Et MCP ?"]

t = time.perf_counter()
for q in questions:
    await appeler_llm(q)                   # l'une après l'autre
print(f"séquentiel : {time.perf_counter() - t:.2f} s")

t = time.perf_counter()
reponses = await asyncio.gather(*(appeler_llm(q) for q in questions))   # en même temps
print(f"concurrent : {time.perf_counter() - t:.2f} s")
reponses
```

## Ne pas tout lancer d'un coup

Envoyer 1 000 requêtes simultanées à une API de LLM déclenche des erreurs 429 (trop de requêtes). Un **sémaphore** limite le nombre de tâches en cours :

```pycode
limite = asyncio.Semaphore(5)
async def appel_limite(q):
    async with limite:              # au plus 5 à la fois
        return await appeler_llm(q)
```

Et une requête qui ne répond jamais ne doit pas bloquer tout le reste : `asyncio.wait_for(coro, timeout=10)` lève une `TimeoutError` au bout de 10 secondes.

## Les pièges

- **Un appel bloquant dans une coroutine bloque tout** : `time.sleep`, `requests.get` ou un gros calcul NumPy arrêtent la boucle entière. Utilise les versions asynchrones (`asyncio.sleep`, `httpx.AsyncClient`, les clients `AsyncAnthropic` ou `AsyncOpenAI`), ou envoie le calcul dans un fil séparé avec `await asyncio.to_thread(fonction, ...)`.
- **L'asynchrone n'accélère pas le calcul** : il aide quand on attend (entrées-sorties), pas quand le processeur travaille. Pour le calcul, on utilise plusieurs processus.
- **Oublier `await`** : la coroutine n'est jamais exécutée, et Python affiche un avertissement « coroutine was never awaited ».

> **À retenir** : `async def` + `await` + `asyncio.gather` pour attendre en parallèle. Un sémaphore pour limiter, `wait_for` pour ne pas attendre indéfiniment. Jamais d'appel bloquant dans une coroutine.
''',
"exercises": [
 E("e-as-a", "Lancer les appels en même temps",
   "La coroutine `appel_api(i)` est fournie : elle attend 0,05 s et renvoie un dictionnaire. Écris `async def recuperer_tout(ids)` qui appelle `appel_api` pour chaque identifiant **en même temps** et renvoie la liste des résultats dans l'ordre des identifiants.",
   r'''import asyncio

async def appel_api(i):
    await asyncio.sleep(0.05)
    return {"id": i, "statut": "ok"}

async def recuperer_tout(ids):
    pass
''',
   r'''import asyncio, time

async def appel_api(i):
    await asyncio.sleep(0.05)
    return {"id": i, "statut": "ok"}

async def recuperer_tout(ids):
    return list(await asyncio.gather(*(appel_api(i) for i in ids)))

t = time.perf_counter()
res = await recuperer_tout(range(8))
print(f"{len(res)} résultats en {time.perf_counter() - t:.2f} s")
''',
   r'''import time
t = time.perf_counter()
r = await recuperer_tout([3, 1, 2, 5, 4, 9])
duree = time.perf_counter() - t
assert isinstance(r, list) and [x["id"] for x in r] == [3, 1, 2, 5, 4, 9], "Les résultats doivent être dans l'ordre des identifiants (asyncio.gather le garantit)."
assert duree < 0.2, f"6 appels de 0,05 s ont pris {duree:.2f} s : ils sont faits l'un après l'autre. Lance-les ensemble avec asyncio.gather."
''',
   "await asyncio.gather(*(appel_api(i) for i in ids)) ; l'étoile déplie la liste de coroutines en arguments."),
 E("e-as-b", "Limiter la concurrence",
   "La coroutine `appel_api(i)` fournie mesure combien d'appels sont en cours en même temps (dans `etat[\"max\"]`). Écris `async def recuperer_limite(ids, max_simultanes)` qui fait tous les appels en parallèle, mais jamais plus de `max_simultanes` à la fois, grâce à un `asyncio.Semaphore`. Les résultats restent dans l'ordre.",
   r'''import asyncio

etat = {"en_cours": 0, "max": 0}

async def appel_api(i):
    etat["en_cours"] += 1
    etat["max"] = max(etat["max"], etat["en_cours"])
    await asyncio.sleep(0.03)
    etat["en_cours"] -= 1
    return i * 10

async def recuperer_limite(ids, max_simultanes):
    pass
''',
   r'''import asyncio

etat = {"en_cours": 0, "max": 0}

async def appel_api(i):
    etat["en_cours"] += 1
    etat["max"] = max(etat["max"], etat["en_cours"])
    await asyncio.sleep(0.03)
    etat["en_cours"] -= 1
    return i * 10

async def recuperer_limite(ids, max_simultanes):
    limite = asyncio.Semaphore(max_simultanes)
    async def un(i):
        async with limite:
            return await appel_api(i)
    return list(await asyncio.gather(*(un(i) for i in ids)))

print(await recuperer_limite(range(10), 3), "· au plus", etat["max"], "en même temps")
''',
   r'''import time
etat["max"] = 0
t = time.perf_counter()
r = await recuperer_limite(list(range(12)), 3)
d = time.perf_counter() - t
assert r == [i * 10 for i in range(12)], "Les résultats doivent être dans l'ordre."
assert etat["max"] <= 3, f"Il y a eu jusqu'à {etat['max']} appels simultanés : la limite est 3 (asyncio.Semaphore)."
assert etat["max"] == 3, "Les appels doivent quand même se faire en parallèle, 3 par 3."
assert d < 0.3, "12 appels par groupes de 3 doivent prendre environ 4 × 0,03 s."
''',
   "Crée le sémaphore dans la fonction, puis une petite coroutine interne qui fait async with limite: return await appel_api(i)."),
 E("e-as-c", "Délai maximal et nouvelles tentatives",
   "Écris `async def avec_retry(fabrique, essais=3, delai_max=0.1)` : `fabrique()` crée une nouvelle coroutine à chaque appel. Attends-la au plus `delai_max` secondes avec `asyncio.wait_for`. En cas de `TimeoutError`, recommence, jusqu'à `essais` tentatives au total ; si toutes échouent, relève la dernière `TimeoutError`. Le service lent `service()` est fourni : ses deux premiers appels prennent 0,3 s, les suivants 0,01 s.",
   r'''import asyncio

compteur = {"n": 0}

async def service():
    compteur["n"] += 1
    await asyncio.sleep(0.3 if compteur["n"] <= 2 else 0.01)
    return "ok"

async def avec_retry(fabrique, essais=3, delai_max=0.1):
    pass
''',
   r'''import asyncio

compteur = {"n": 0}

async def service():
    compteur["n"] += 1
    await asyncio.sleep(0.3 if compteur["n"] <= 2 else 0.01)
    return "ok"

async def avec_retry(fabrique, essais=3, delai_max=0.1):
    for tentative in range(essais):
        try:
            return await asyncio.wait_for(fabrique(), delai_max)
        except TimeoutError:
            if tentative == essais - 1:
                raise

print(await avec_retry(service), "après", compteur["n"], "tentatives")
''',
   r'''import asyncio
compteur["n"] = 0
r = await avec_retry(service, essais=3, delai_max=0.1)
assert r == "ok" and compteur["n"] == 3, f"Avec 3 essais, le service répond à la 3e tentative ; tu as fait {compteur['n']} appels et obtenu {r!r}."
compteur["n"] = 0
try:
    await avec_retry(service, essais=2, delai_max=0.1); echoue = False
except (TimeoutError, asyncio.TimeoutError):
    echoue = True
assert echoue and compteur["n"] == 2, "Avec 2 essais seulement, les deux tentatives expirent : relève la TimeoutError."
''',
   "Une boucle for sur range(essais), un try autour de await asyncio.wait_for(fabrique(), delai_max), et raise à la dernière tentative."),
]},
# ================================================================ FastAPI
{"id": "l-fastapi", "title": "FastAPI : servir un modèle", "minutes": 120,
"body": r'''
Un modèle dans un notebook ne sert à personne. Pour que le site web, l'application mobile ou un autre service l'utilisent, on l'expose derrière une **API HTTP**. **FastAPI** est devenu le framework de référence en Python pour ça : rapide, asynchrone, et il valide automatiquement les données grâce aux annotations de type.

Dans la plateforme, on utilise **`minifast`**, un mini-framework qui reprend la syntaxe de FastAPI pour les bases (routes, paramètres, validation par pydantic, erreurs, client de test). Sur ton ordinateur, remplace `from minifast import ...` par `from fastapi import ...` et `from fastapi.testclient import TestClient` : le reste du code est le même.

## Une première API

```python
from minifast import FastAPI, HTTPException, TestClient

app = FastAPI(title="API Livres")
LIVRES = {1: {"titre": "Fondation", "auteur": "Asimov"}, 2: {"titre": "Dune", "auteur": "Herbert"}}

@app.get("/sante")
def sante():
    return {"statut": "ok"}

@app.get("/livres/{livre_id}")            # paramètre de chemin, converti en int
def lire(livre_id: int):
    if livre_id not in LIVRES:
        raise HTTPException(status_code=404, detail="Livre introuvable")
    return LIVRES[livre_id]

client = TestClient(app)                   # des requêtes sans lancer de serveur
print(client.get("/livres/2").json())
print(client.get("/livres/9").status_code, client.get("/livres/9").json())
print(client.get("/livres/abc").status_code, "← « abc » n'est pas un entier : erreur 422")
```

Les paramètres de la fonction qui ne sont pas dans le chemin deviennent des **paramètres de requête** : `def chercher(auteur: str | None = None, limite: int = 10)` répond à `/livres?auteur=Asimov&limite=5`.

## Valider les entrées avec pydantic

Pour recevoir des données en JSON (le corps d'une requête POST), on décrit leur forme avec un modèle **pydantic**. FastAPI vérifie les types et les contraintes **avant** d'appeler ta fonction, et renvoie une erreur **422** détaillée sinon. Ton code de prédiction ne reçoit jamais de données invalides.

```python
from pydantic import BaseModel, Field

class Appartement(BaseModel):
    surface: float = Field(gt=0, description="en m²")
    pieces: int = Field(ge=1, le=10)

@app.post("/estimer")
def estimer(appart: Appartement):
    return {"prix": round(appart.surface * 4200 + appart.pieces * 9000)}

print(client.post("/estimer", json={"surface": 52, "pieces": 2}).json())
r = client.post("/estimer", json={"surface": -3, "pieces": 2})
print(r.status_code, r.json()["detail"][0]["msg"])
```

```viz fastapi
```

## Servir un vrai modèle : les bonnes pratiques

- **Charger le modèle une seule fois**, au démarrage, pas à chaque requête (avec `joblib.load` au niveau du module, ou l'événement `lifespan`).
- **Une route `/sante`** (*health check*) : le load balancer et Docker s'en servent pour savoir si le service est vivant.
- **Versionner** : renvoyer la version du modèle dans chaque réponse, et préfixer les routes (`/v1/predire`) pour pouvoir changer le contrat sans casser les clients.
- **Prédire par lots** : une route qui accepte une liste d'exemples évite des centaines d'allers-retours.
- **`async def` seulement si on attend** (appel à un LLM, à une base). Une prédiction scikit-learn est du calcul : une fonction normale `def`, que FastAPI exécute dans un fil séparé.
- **La documentation est gratuite** : FastAPI génère `/docs` (Swagger) à partir des types. Dans `minifast`, `app.openapi()` en donne un aperçu.

```pycode
# main.py   →   uvicorn main:app --reload
from contextlib import asynccontextmanager
from fastapi import FastAPI
import joblib

modeles = {}

@asynccontextmanager
async def lifespan(app):
    modeles["fraude"] = joblib.load("modeles/fraude.joblib")    # au démarrage
    yield
    modeles.clear()                                              # à l'arrêt

app = FastAPI(lifespan=lifespan)
```

> **À retenir** : un décorateur par route, les types font la conversion et la validation, pydantic pour les corps JSON, `HTTPException` pour les erreurs. Modèle chargé une fois, route de santé, version dans la réponse. Tester avec `TestClient`.
''',
"tasks": [
  "Installer fastapi et uvicorn, recopier l'API Livres dans main.py et la lancer avec uvicorn main:app --reload",
  "Ouvrir http://localhost:8000/docs et tester les routes depuis l'interface générée",
  "Écrire trois tests avec pytest et fastapi.testclient.TestClient",
  "Servir le modèle Immo entraîné en vague 3 (sauvegardé avec joblib) derrière une route /v1/estimer",
],
"exercises": [
 E("e-fa-a", "Des routes et des erreurs",
   "Crée `app = FastAPI()` avec trois routes sur les données `LIVRES` fournies : `GET /sante` renvoie `{\"statut\": \"ok\"}` ; `GET /livres/{livre_id}` renvoie le livre (avec son `id`) ou une erreur 404 de détail `\"Livre introuvable\"` ; `GET /livres` accepte les paramètres de requête facultatifs `auteur` (str ou None) et `limite` (int, 10 par défaut) et renvoie la liste des livres (chacun avec son `id`) de cet auteur s'il est donné, triés par id, limitée à `limite` éléments.",
   r'''from minifast import FastAPI, HTTPException, TestClient

LIVRES = {
    1: {"titre": "Fondation", "auteur": "Asimov"},
    2: {"titre": "Dune", "auteur": "Herbert"},
    3: {"titre": "Les Robots", "auteur": "Asimov"},
    4: {"titre": "Hypérion", "auteur": "Simmons"},
    5: {"titre": "La Fin de l'éternité", "auteur": "Asimov"},
}

app = FastAPI()
''',
   r'''from minifast import FastAPI, HTTPException, TestClient

LIVRES = {
    1: {"titre": "Fondation", "auteur": "Asimov"},
    2: {"titre": "Dune", "auteur": "Herbert"},
    3: {"titre": "Les Robots", "auteur": "Asimov"},
    4: {"titre": "Hypérion", "auteur": "Simmons"},
    5: {"titre": "La Fin de l'éternité", "auteur": "Asimov"},
}

app = FastAPI()

@app.get("/sante")
def sante():
    return {"statut": "ok"}

@app.get("/livres/{livre_id}")
def lire(livre_id: int):
    if livre_id not in LIVRES:
        raise HTTPException(status_code=404, detail="Livre introuvable")
    return {"id": livre_id, **LIVRES[livre_id]}

@app.get("/livres")
def lister(auteur: str | None = None, limite: int = 10):
    res = [{"id": i, **l} for i, l in sorted(LIVRES.items()) if auteur is None or l["auteur"] == auteur]
    return res[:limite]

client = TestClient(app)
print(client.get("/livres", params={"auteur": "Asimov", "limite": 2}).json())
''',
   r'''c = TestClient(app)
assert c.get("/sante").json() == {"statut": "ok"}, "GET /sante doit renvoyer {'statut': 'ok'}."
r = c.get("/livres/2")
assert r.status_code == 200 and r.json() == {"id": 2, "titre": "Dune", "auteur": "Herbert"}, f"GET /livres/2 doit renvoyer le livre avec son id ; tu renvoies {r.json()}."
r = c.get("/livres/42")
assert r.status_code == 404 and r.json() == {"detail": "Livre introuvable"}, "Un livre absent doit donner une erreur 404 avec detail « Livre introuvable » (HTTPException)."
assert c.get("/livres/abc").status_code == 422, "livre_id doit être annoté int : « abc » donne alors une erreur 422."
assert [l["id"] for l in c.get("/livres").json()] == [1, 2, 3, 4, 5], "Sans paramètre, GET /livres renvoie tous les livres, triés par id."
assert [l["id"] for l in c.get("/livres?auteur=Asimov").json()] == [1, 3, 5], "Le paramètre auteur doit filtrer."
assert [l["id"] for l in c.get("/livres", params={"auteur": "Asimov", "limite": 2}).json()] == [1, 3], "Le paramètre limite doit couper la liste."
''',
   "Trois fonctions décorées. {\"id\": i, **livre} ajoute l'identifiant au dictionnaire. La route /livres prend deux paramètres avec des valeurs par défaut."),
 E("e-fa-b", "Une route de prédiction validée",
   "Crée un modèle pydantic `Appartement` avec `surface` (float, strictement positif), `pieces` (int, de 1 à 10) et `quartier` (str). Crée `app` avec : `GET /sante` ; `POST /v1/estimer` qui reçoit un `Appartement` et renvoie `{\"prix\": <estimer(...) arrondi à l'euro>, \"version\": VERSION}` en utilisant la fonction `estimer` fournie ; et `POST /v1/estimer/lot` qui reçoit un `Lot` (un modèle avec un champ `appartements: list[Appartement]`) et renvoie `{\"prix\": [...], \"version\": VERSION}`. Si le quartier est inconnu, `estimer` lève une `KeyError` : renvoie alors une erreur 400 de détail `\"Quartier inconnu\"`.",
   r'''from minifast import FastAPI, HTTPException, TestClient
from pydantic import BaseModel, Field

VERSION = "immo-1.2.0"
PRIX_M2 = {"Centre": 9800, "Gare": 7600, "Université": 6900, "Port": 6400, "Périphérie": 4700}

def estimer(surface, pieces, quartier):
    return surface * PRIX_M2[quartier] + 6000 * pieces

app = FastAPI()
''',
   r'''from minifast import FastAPI, HTTPException, TestClient
from pydantic import BaseModel, Field

VERSION = "immo-1.2.0"
PRIX_M2 = {"Centre": 9800, "Gare": 7600, "Université": 6900, "Port": 6400, "Périphérie": 4700}

def estimer(surface, pieces, quartier):
    return surface * PRIX_M2[quartier] + 6000 * pieces

class Appartement(BaseModel):
    surface: float = Field(gt=0)
    pieces: int = Field(ge=1, le=10)
    quartier: str

class Lot(BaseModel):
    appartements: list[Appartement]

app = FastAPI(title="Estimation Immo")

def _prix(a):
    try:
        return round(estimer(a.surface, a.pieces, a.quartier))
    except KeyError:
        raise HTTPException(status_code=400, detail="Quartier inconnu")

@app.get("/sante")
def sante():
    return {"statut": "ok", "version": VERSION}

@app.post("/v1/estimer")
def estimer_un(appart: Appartement):
    return {"prix": _prix(appart), "version": VERSION}

@app.post("/v1/estimer/lot")
def estimer_lot(lot: Lot):
    return {"prix": [_prix(a) for a in lot.appartements], "version": VERSION}

client = TestClient(app)
print(client.post("/v1/estimer", json={"surface": 45.5, "pieces": 2, "quartier": "Gare"}).json())
''',
   r'''c = TestClient(app)
assert c.get("/sante").status_code == 200, "Ajoute la route GET /sante."
r = c.post("/v1/estimer", json={"surface": 45.5, "pieces": 2, "quartier": "Gare"})
assert r.status_code == 200 and r.json() == {"prix": round(45.5 * 7600 + 12000), "version": VERSION}, f"Réponse attendue : prix arrondi et version ; tu as {r.json()}."
assert c.post("/v1/estimer", json={"surface": -5, "pieces": 2, "quartier": "Gare"}).status_code == 422, "Une surface négative doit être refusée par pydantic (Field(gt=0)) : erreur 422."
assert c.post("/v1/estimer", json={"surface": 40, "pieces": 0, "quartier": "Gare"}).status_code == 422, "pieces doit être entre 1 et 10 (Field(ge=1, le=10))."
assert c.post("/v1/estimer", json={"surface": 40, "pieces": 2}).status_code == 422, "Un champ manquant doit donner une erreur 422."
r = c.post("/v1/estimer", json={"surface": 40, "pieces": 2, "quartier": "Lune"})
assert r.status_code == 400 and r.json() == {"detail": "Quartier inconnu"}, "Un quartier inconnu doit donner une erreur 400 « Quartier inconnu »."
lot = {"appartements": [{"surface": 30, "pieces": 1, "quartier": "Centre"}, {"surface": 80, "pieces": 4, "quartier": "Port"}]}
r = c.post("/v1/estimer/lot", json=lot)
assert r.status_code == 200 and r.json()["prix"] == [round(30 * 9800 + 6000), round(80 * 6400 + 24000)], "La route /v1/estimer/lot renvoie une liste de prix, dans l'ordre."
''',
   "class Appartement(BaseModel) avec Field(gt=0) et Field(ge=1, le=10). Attrape KeyError autour de estimer et lève HTTPException(status_code=400, ...)."),
]},
]

PROJECTS = [
{"id": "p-stripe", "title": "Projet · Infrastructure d'IA anti-fraude", "minutes": 180,
"body": r'''
L'équivalent du projet « Infrastructure d'IA Stripe » : tu construis le service qui décide, en quelques millisecondes, si un paiement en ligne est frauduleux. Du jeu de données à l'API, avec les vraies questions d'un ingénieur ML : quelles variables, quelle métrique, quel seuil, et comment servir le modèle.

Le jeu `paiements` contient 10 000 transactions, dont environ 1 % de fraudes :

```python
from paiements import charger
df = charger()
print(df.shape, f"{df['fraude'].mean():.2%} de fraudes")
df.head()
```

## Trois difficultés réelles

1. **Le déséquilibre** : avec 1 % de fraudes, un modèle qui dit toujours « pas de fraude » a 99 % d'exactitude, et ne sert à rien. On regarde l'**AUC** (capacité à classer les fraudes au-dessus des autres) et la **précision moyenne** (*average precision*, l'aire sous la courbe précision-rappel).
2. **Les variables** : le montant brut ou l'heure brute disent peu. « La carte et l'adresse IP viennent de pays différents », « le compte a moins de 30 jours », « il est entre minuit et 6 h » disent beaucoup. C'est l'**ingénierie des variables**.
3. **Le seuil** : laisser passer une fraude coûte son montant ; bloquer un client honnête coûte une vente et sa confiance (on l'estime ici à 5 €). Le bon seuil est celui qui **minimise le coût total**, pas 0,5.

La fonction `preparer(df)` qui construit ces variables est fournie dans les exercices 2 et 3.
''',
"exercises": [
 E("e-pst-a", "Construire les variables",
   "Écris `preparer(df)` qui renvoie un DataFrame (même index que `df`) avec 7 colonnes : `pays_diff` (1 si `pays_carte` ≠ `pays_ip`), `log_montant` (log(1 + montant / 100)), `nb_tx_24h` (inchangé), `compte_recent` (1 si `anciennete_compte_j` < 30), `appareil_nouveau` (inchangé), `nuit` (1 si `heure` < 6) et `cat_risque` (1 si la catégorie est « électronique » ou « jeux »). Les indicateurs sont des entiers 0 ou 1.",
   r'''import numpy as np
import pandas as pd
from paiements import charger

df = charger()

def preparer(df):
    pass
''',
   r'''import numpy as np
import pandas as pd
from paiements import charger

df = charger()

def preparer(df):
    return pd.DataFrame({
        "pays_diff": (df["pays_carte"] != df["pays_ip"]).astype(int),
        "log_montant": np.log1p(df["montant"] / 100),
        "nb_tx_24h": df["nb_tx_24h"],
        "compte_recent": (df["anciennete_compte_j"] < 30).astype(int),
        "appareil_nouveau": df["appareil_nouveau"],
        "nuit": (df["heure"] < 6).astype(int),
        "cat_risque": df["categorie"].isin(["électronique", "jeux"]).astype(int),
    }, index=df.index)

X = preparer(df)
X.assign(fraude=df["fraude"]).groupby("pays_diff")["fraude"].mean()
''',
   r'''import numpy as np
X = preparer(df)
attendues = ["pays_diff", "log_montant", "nb_tx_24h", "compte_recent", "appareil_nouveau", "nuit", "cat_risque"]
assert X is not None and sorted(X.columns) == sorted(attendues), f"Colonnes attendues : {attendues}."
assert len(X) == len(df) and (X.index == df.index).all(), "Garde le même index que df."
assert (X["pays_diff"] == (df["pays_carte"] != df["pays_ip"]).astype(int)).all(), "pays_diff vaut 1 quand les pays diffèrent."
assert np.allclose(X["log_montant"], np.log1p(df["montant"] / 100)), "log_montant = log(1 + montant / 100) : np.log1p."
assert (X["compte_recent"] == (df["anciennete_compte_j"] < 30)).all() and (X["nuit"] == (df["heure"] < 6)).all(), "compte_recent : moins de 30 jours ; nuit : avant 6 h."
assert X["cat_risque"].sum() == df["categorie"].isin(["électronique", "jeux"]).sum(), "cat_risque : électronique ou jeux (isin)."
assert set(X["pays_diff"].unique()) <= {0, 1} and X["nuit"].dtype.kind == "i", "Les indicateurs doivent être des entiers 0 ou 1 (.astype(int))."
''',
   "Construis un dictionnaire de colonnes, puis pd.DataFrame(..., index=df.index). (condition).astype(int) donne 0 ou 1."),
 E("e-pst-b", "Entraîner, évaluer, choisir le seuil",
   "Le découpage est fourni. Entraîne `modele = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))` sur l'entraînement, calcule `proba_test` (probabilités de fraude sur le test), `auc` (`roc_auc_score`) et `ap` (`average_precision_score`). Puis écris `cout(seuil)` : somme des montants (`m_test`) des fraudes **non** détectées (proba < seuil) + 5 € par transaction honnête bloquée (proba ≥ seuil). Mets dans `seuil` la valeur de `np.linspace(0.01, 0.99, 99)` qui minimise ce coût.",
   PAIE_PRE + PAIE_SPLIT + r'''from sklearn.metrics import roc_auc_score, average_precision_score

modele = None
proba_test = None
auc = ap = None

def cout(seuil):
    pass

seuil = None
''',
   PAIE_PRE + PAIE_SPLIT + r'''from sklearn.metrics import roc_auc_score, average_precision_score

modele = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(X_train, y_train)
proba_test = modele.predict_proba(X_test)[:, 1]
auc = roc_auc_score(y_test, proba_test)
ap = average_precision_score(y_test, proba_test)

def cout(seuil):
    alerte = proba_test >= seuil
    fraudes_ratees = m_test[(y_test == 1).to_numpy() & ~alerte].sum()
    fausses_alertes = ((y_test == 0).to_numpy() & alerte).sum()
    return fraudes_ratees + 5 * fausses_alertes

seuils = np.linspace(0.01, 0.99, 99)
couts = [cout(s) for s in seuils]
seuil = seuils[int(np.argmin(couts))]
print(f"AUC {auc:.3f} · AP {ap:.3f} · seuil optimal {seuil:.2f} · coût {min(couts):.0f} € (contre {cout(0.5):.0f} € au seuil 0,5)")
''',
   r'''import numpy as np
from sklearn.metrics import roc_auc_score
assert proba_test is not None and len(proba_test) == len(y_test), "proba_test doit contenir une probabilité par transaction du test (predict_proba(...)[:, 1])."
assert abs(auc - roc_auc_score(y_test, proba_test)) < 1e-12 and auc > 0.9, f"Avec ces variables, l'AUC doit dépasser 0,9 ; tu as {auc}."
assert 0 < ap < 1, "ap doit être la précision moyenne (average_precision_score)."
pt = np.asarray(proba_test); yt = np.asarray(y_test); mt = np.asarray(m_test)
ref = lambda s: mt[(yt == 1) & (pt < s)].sum() + 5 * ((yt == 0) & (pt >= s)).sum()
assert abs(cout(0.3) - ref(0.3)) < 1e-6, f"cout(0.3) devrait valoir {ref(0.3):.2f} € ; tu as {cout(0.3)}."
grille = np.linspace(0.01, 0.99, 99)
assert seuil is not None and abs(ref(seuil) - min(ref(s) for s in grille)) < 1e-6, "seuil doit minimiser le coût sur np.linspace(0.01, 0.99, 99)."
assert seuil < 0.5, "Le coût d'une fraude ratée est bien plus grand que celui d'une fausse alerte : le seuil optimal est bas."
''',
   "Masques booléens : (y_test == 1).to_numpy() & (proba_test < seuil). np.argmin sur la liste des coûts donne l'indice du meilleur seuil."),
 E("e-pst-c", "Servir le modèle",
   "Le modèle entraîné et le `SEUIL` sont fournis. Crée un modèle pydantic `Transaction` avec les 8 colonnes brutes (`montant` float > 0, `heure` int de 0 à 23, `pays_carte` et `pays_ip` str, `nb_tx_24h` et `anciennete_compte_j` int ≥ 0, `appareil_nouveau` int de 0 à 1, `categorie` str). Crée `app` avec `GET /sante` et `POST /v1/score`, qui transforme la transaction en DataFrame d'une ligne, la passe dans `preparer` puis dans le modèle, et renvoie `{\"score\": <proba arrondie à 4 décimales>, \"fraude\": <score ≥ SEUIL>, \"version\": VERSION}`.",
   PAIE_PRE + PAIE_SPLIT + r'''from minifast import FastAPI, TestClient
from pydantic import BaseModel, Field

modele = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(X_train, y_train)
SEUIL = 0.07
VERSION = "fraude-1.0.0"

app = FastAPI()
''',
   PAIE_PRE + PAIE_SPLIT + r'''from minifast import FastAPI, TestClient
from pydantic import BaseModel, Field

modele = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(X_train, y_train)
SEUIL = 0.07
VERSION = "fraude-1.0.0"

class Transaction(BaseModel):
    montant: float = Field(gt=0)
    heure: int = Field(ge=0, le=23)
    pays_carte: str
    pays_ip: str
    nb_tx_24h: int = Field(ge=0)
    anciennete_compte_j: int = Field(ge=0)
    appareil_nouveau: int = Field(ge=0, le=1)
    categorie: str

app = FastAPI(title="Anti-fraude")

@app.get("/sante")
def sante():
    return {"statut": "ok", "version": VERSION}

@app.post("/v1/score")
def scorer(tx: Transaction):
    ligne = preparer(pd.DataFrame([tx.model_dump()]))
    score = float(modele.predict_proba(ligne)[0, 1])
    return {"score": round(score, 4), "fraude": score >= SEUIL, "version": VERSION}

client = TestClient(app)
suspecte = {"montant": 900, "heure": 3, "pays_carte": "FR", "pays_ip": "NG", "nb_tx_24h": 6,
            "anciennete_compte_j": 2, "appareil_nouveau": 1, "categorie": "électronique"}
print(client.post("/v1/score", json=suspecte).json())
''',
   r'''import pandas as pd
c = TestClient(app)
assert c.get("/sante").status_code == 200, "Ajoute GET /sante."
sus = {"montant": 900, "heure": 3, "pays_carte": "FR", "pays_ip": "NG", "nb_tx_24h": 6, "anciennete_compte_j": 2, "appareil_nouveau": 1, "categorie": "électronique"}
sain = {"montant": 25, "heure": 14, "pays_carte": "FR", "pays_ip": "FR", "nb_tx_24h": 1, "anciennete_compte_j": 900, "appareil_nouveau": 0, "categorie": "alimentaire"}
r1, r2 = c.post("/v1/score", json=sus), c.post("/v1/score", json=sain)
assert r1.status_code == 200 and set(r1.json()) == {"score", "fraude", "version"}, f"La réponse doit contenir score, fraude et version ; tu as {r1.json()}."
attendu = float(modele.predict_proba(preparer(pd.DataFrame([sus])))[0, 1])
assert abs(r1.json()["score"] - round(attendu, 4)) < 1e-9, "Le score doit être la probabilité du modèle, après preparer, arrondie à 4 décimales."
assert r1.json()["fraude"] is True and r2.json()["fraude"] is False, "La transaction suspecte doit être bloquée et la transaction normale acceptée."
assert c.post("/v1/score", json={**sain, "montant": -10}).status_code == 422, "Un montant négatif doit être refusé (422)."
assert c.post("/v1/score", json={**sain, "heure": 25}).status_code == 422, "heure doit être entre 0 et 23."
''',
   "pd.DataFrame([tx.model_dump()]) crée un DataFrame d'une ligne avec les colonnes brutes ; preparer s'occupe du reste."),
],
"tasks": [
  "Sauvegarder le modèle avec joblib et l'API dans un main.py FastAPI, avec la vraie bibliothèque",
  "Suivre 5 variantes du modèle avec MLflow (régression logistique, forêt, boosting, avec et sans les variables construites) et enregistrer le champion",
  "Écrire le Dockerfile, construire l'image et la lancer en local",
  "Déployer l'image sur une instance EC2 derrière Caddy, et mesurer la latence de /v1/score avec 100 requêtes",
  "Écrire un README avec l'architecture, la métrique choisie, le seuil et son coût",
]},
]

QUIZZES = {
"quiz-mlops": {"title": "Quiz · Ingénierie ML", "questions": [
 {"q": "Où mettre la clé d'API d'un service en production ?", "options": ["Dans le code, en constante", "Dans le Dockerfile", "Dans une variable d'environnement ou un gestionnaire de secrets", "Dans le README"], "answer": 2,
  "explain": "Les secrets ne vont ni dans Git ni dans l'image : on les injecte au lancement."},
 {"q": "Dans Streamlit, que se passe-t-il quand l'utilisateur bouge un curseur ?", "options": ["Seule la ligne du curseur est réexécutée", "Tout le script est réexécuté de haut en bas", "Rien, il faut cliquer sur un bouton", "La page est rechargée depuis le serveur web"], "answer": 1,
  "explain": "D'où l'importance de @st.cache_data et @st.cache_resource pour les opérations lentes."},
 {"q": "Pourquoi copier requirements.txt et installer les dépendances avant de copier le code dans un Dockerfile ?", "options": ["C'est obligatoire", "Pour que la couche des dépendances reste en cache quand seul le code change", "Pour réduire la sécurité", "Pour lancer les tests"], "answer": 1,
  "explain": "Une modification du code n'invalide alors que les couches suivantes : le build passe de minutes à secondes."},
 {"q": "Quelle règle de groupe de sécurité est dangereuse ?", "options": ["Port 443 ouvert à 0.0.0.0/0", "Port 22 ouvert à ton IP /32", "Port 5432 ouvert à 0.0.0.0/0", "Port 80 ouvert à 0.0.0.0/0"], "answer": 2,
  "explain": "Une base PostgreSQL exposée à Internet est trouvée et attaquée très vite."},
 {"q": "Dans MLflow, à quoi sert un alias comme « champion » dans le registre ?", "options": ["À nommer une expérience", "À désigner la version du modèle utilisée en production, sans changer le code", "À compresser le modèle", "À lancer l'interface"], "answer": 1,
  "explain": "L'API charge models:/fraude@champion ; promouvoir ou revenir en arrière = déplacer l'alias."},
 {"q": "Quand l'asynchrone accélère-t-il vraiment un programme ?", "options": ["Pour un gros calcul NumPy", "Quand il passe son temps à attendre des réponses réseau ou disque", "Toujours", "Jamais en Python"], "answer": 1,
  "explain": "L'asynchrone utilise le temps d'attente. Pour du calcul, il faut plusieurs processus."},
 {"q": "Que renvoie FastAPI si le JSON reçu ne respecte pas le modèle pydantic ?", "options": ["Une erreur 500", "Une erreur 422 détaillant les champs invalides", "Une erreur 404", "Il appelle quand même la fonction"], "answer": 1,
  "explain": "La validation a lieu avant ton code : ta fonction ne reçoit que des données valides."},
 {"q": "Avec 1 % de fraudes, pourquoi l'exactitude est-elle une mauvaise métrique ?", "options": ["Elle est trop lente à calculer", "Un modèle qui ne détecte jamais de fraude a 99 % d'exactitude", "Elle ne fonctionne pas avec la régression logistique", "Elle est toujours de 50 %"], "answer": 1,
  "explain": "Sur des classes déséquilibrées, on regarde l'AUC, la précision moyenne, et le coût métier des erreurs."},
]},
}
