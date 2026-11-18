# Prépa FullStack AI

J'ai créé une plateforme d'apprentissage pour me préparer à la formation FullStack AI chez Jedha 💻🚀

Elle suit les modules officiels des programmes **Essentials AI**, **FullStack IA** et **Lead AI** de Jedha, avec un plan de 11 semaines à 20 h et plus.

- **43 leçons** avec du code exécutable dans le navigateur et **16 animations interactives**
- **98 exercices** corrigés automatiquement (Python, pandas, SQL, ML, LLM, agents, RAG)
- **6 projets** pour le portfolio et **9 quiz**, dont un de préparation à l'AWS Cloud Practitioner
- de vrais appels à un LLM depuis Python, et un tuteur IA dans chaque leçon
- la carte complète des 3 programmes : ce qui est préparé, ce qui arrive

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
pip install markdown numpy pandas scikit-learn
cd tools && npm install && cd ..
python web/assemble.py     # assemble l'application
python build.py            # génère dist/
python test_all.py         # vérifie que chaque corrigé passe sa vérification
python -m http.server -d dist 8000
```

## Publier sur GitHub Pages

Le workflow `.github/workflows/pages.yml` construit, teste et publie la plateforme à chaque push sur `main`. Pour l'activer : **Settings → Pages → Source : GitHub Actions**.

## Structure

| Chemin | Rôle |
| --- | --- |
| `content/parcours.py` | La carte des programmes Jedha et le plan de 11 semaines |
| `content/*.py` | Les leçons, exercices (code de départ, corrigé, vérification, indice), projets et quiz |
| `labs/` | Base SQLite Brewly, fausse API de livres, base de connaissances CloudSync, accès au LLM |
| `runner.py`, `pxshim.py` | Exécution des cellules et version simplifiée de plotly.express |
| `web/src/` | L'application et ses animations, assemblées en `web/index.html` |
| `build.py` | Transforme le contenu en `dist/content.json` (markdown, formules LaTeX, animations) |
| `test_all.py` | Teste tous les corrigés et tous les blocs de code des leçons |
| `make_notebooks.py` | Génère un notebook par module et `CORRIGES.md` |
| `CLAUDE.md` | Les instructions pour faire évoluer le projet avec Claude Code |

## Données

Penguins, Titanic et Tips viennent du dépôt [mwaskom/seaborn-data](https://github.com/mwaskom/seaborn-data).
