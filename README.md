# Prépa AI

**🌐 Le site : https://maxime-sudo13.github.io/Pr-pa-Jedha-FullStack-AI/**

J'ai créé une plateforme d'apprentissage pour me préparer à la formation FullStack AI chez Jedha 💻🚀

Elle suit les modules officiels des programmes **Essentials AI**, **FullStack AI** et **Lead AI** de Jedha, avec un plan de 11 semaines à 20 h et plus.

- **92 leçons** avec du code exécutable dans le navigateur et **47 animations interactives**
- **220 exercices** corrigés automatiquement (Python, pandas, SQL, machine learning, deep learning, Transformers, CLIP, diffusion, LoRA, RL, FastAPI, asyncio, MLflow, Docker, LangGraph, MCP, Kubernetes, Terraform, Airflow, dérive, garde-fous, GraphRAG, LLM, agents, RAG)
- **11 projets** pour le portfolio, dont un mini-GPT avec cache KV, une API anti-fraude et un pipeline MLOps de surveillance, et **17 quiz**, dont un de préparation à l'AWS Cloud Practitioner
- de vrais appels à un LLM depuis Python, et un tuteur IA dans chaque leçon
- une lecture audio de chaque leçon : un bouton ▶ sur chaque paragraphe, une barre de lecture (pause, paragraphe suivant, vitesse) et le passage lu surligné
- la carte complète des 3 programmes, dont toutes les sections sont couvertes

## Le style

Thème sombre unique, « cyber » : noir profond, bleu électrique et cyan, panneaux de verre, titres en dégradé lumineux, apparitions animées (désactivées si le système demande moins d'animations). Polices Space Grotesk, IBM Plex Sans et JetBrains Mono.

## Deux façons de l'utiliser

1. **La plateforme web** (`web/` → `dist/`) : Python tourne dans le navigateur grâce à Pyodide.
2. **Les notebooks Jupyter** (`notebooks/`) : un par module, pour travailler avec du vrai Python. Les corrigés sont dans `notebooks/CORRIGES.md`.

## Démarrer avec les notebooks

```bash
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
cd notebooks
jupyter notebook
```

## Construire la plateforme web

Il faut Python 3.10+ et Node.js 18+.

```bash
pip install markdown numpy pandas scikit-learn scipy matplotlib pydantic
cd tools && npm install && cd ..
python web/assemble.py     # assemble l'application
python build.py            # génère dist/
python test_all.py         # vérifie que chaque corrigé passe sa vérification
python -m http.server -d dist 8000
```

## Publier sur GitHub Pages

Le workflow `.github/workflows/pages.yml` construit, teste et publie la plateforme à chaque push sur `main`. Pour l'activer : **Settings → Pages → Source : GitHub Actions**.

Si un seul test échoue, rien n'est publié et le site garde sa version précédente : vérifie l'onglet **Actions** après chaque fusion (coche verte = site à jour, en 1 à 2 minutes).

## Structure

| Chemin | Rôle |
| --- | --- |
| `content/parcours.py` | La carte des programmes Jedha et le plan de 11 semaines |
| `content/*.py` | Les leçons, exercices (code de départ, corrigé, vérification, indice), projets et quiz |
| `labs/` | Base SQLite Brewly, fausse API de livres, base de connaissances CloudSync, ventes immobilières Immo, paiements et fraudes (avec dérive mensuelle), mini-FastAPI `minifast`, accès au LLM |
| `runner.py`, `pxshim.py` | Exécution des cellules et version simplifiée de plotly.express |
| `web/src/` | L'application (`app.js`), ses 47 animations (`viz.js`) et ses styles (`base.css`, `extra.css`, puis `cyber.css` pour le thème), assemblés en `web/index.html` |
| `build.py` | Transforme le contenu en `dist/content.json` (markdown, formules LaTeX, animations) |
| `test_all.py` | Teste tous les corrigés et tous les blocs de code des leçons |
| `make_notebooks.py` | Génère un notebook par module et `CORRIGES.md` |
| `CLAUDE.md` | Les instructions pour faire évoluer le projet avec Claude Code |

## Données

Penguins, Titanic et Tips viennent du dépôt [mwaskom/seaborn-data](https://github.com/mwaskom/seaborn-data).
