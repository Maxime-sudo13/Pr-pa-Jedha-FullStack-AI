# Instructions pour Claude Code

**Prépa AI** : plateforme de préparation aux formations de Jedha, dans l'ordre Essentials AI (en premier, en bonus), puis **FullStack AI** et **Lead AI**. L'apprenant est francophone, adulte, en reconversion, et vise un très haut niveau. On le tutoie.

## Architecture

| Chemin | Rôle |
| --- | --- |
| `content/parcours.py` | La carte des 3 programmes Jedha : modules, sections officielles, leçons qui les couvrent, plan de 11 semaines |
| `content/w1.py` … `w4.py` | Les 25 premières leçons (format `WEEK`) |
| `content/f1_poo.py`, `f3_infra.py`, `e_genai.py`, `f4_ml.py`, `f5_dl.py`, `f6_gen.py`, `f7_adapt.py`, `f8_mlops.py`, `f10_aieng.py` | Les leçons des vagues 1 à 6 (format `LESSONS`, `PROJECTS`, `QUIZZES`) |
| `labs/` | `brewly` (base SQLite), `fakeapi` (fausse API), `cloudsync` (base de connaissances RAG), `immo` (ventes d'appartements pour le ML), `paiements` (transactions et fraudes), `minifast` (imitation de FastAPI avec TestClient), `llm` (appel d'un vrai LLM depuis Python, ou réponse simulée hors plateforme) |
| `runner.py`, `pxshim.py` | Exécution des cellules et version simplifiée de plotly.express (navigateur) |
| `web/src/` | L'application : `app.js` (vues, progression, Pyodide, tuteur), `viz.js` (animations), CSS |
| `web/assemble.py` | Assemble `web/src/` en un seul `web/index.html` |
| `build.py` | Construit `dist/` : markdown → HTML, LaTeX → SVG, blocs ```` ```viz nom ```` → animations |
| `test_all.py` | Teste tous les blocs de code et tous les exercices |
| `make_notebooks.py` | Génère un notebook par module et `CORRIGES.md` |

## Ajouter une vague de contenu

1. Crée `content/<module>_<sujet>.py` avec `LESSONS`, `PROJECTS` et `QUIZZES` (même format que `f3_infra.py`).
2. Référence les nouvelles leçons dans les `sections` du module concerné dans `content/parcours.py`.
3. Pour une animation, ajoute une fonction `VIZ.<nom> = el => {...}` dans `web/src/viz.js` et un bloc ```` ```viz <nom> ```` dans la leçon.
4. Lance `python test_all.py`, `python web/assemble.py`, `python build.py`, `python make_notebooks.py`.

## Règles de contenu

- Français, tutoiement, phrases courtes, exemples concrets. Les noms de modules suivent ceux de Jedha.
- Chaque exercice : `prompt`, `starter`, `solution`, `check` (des `assert` dont le message aide à corriger), `hint`. La vérification doit passer avec la solution **et échouer** avec le code de départ. Recalcule la valeur attendue dans `check` quand c'est possible.
- Blocs de code : ```` ```python ```` exécutable dans le navigateur, ```` ```pycode ```` affiché seulement, ```` ```latex ```` formule, ```` ```viz nom ```` animation.
- Disponible dans le navigateur : bibliothèque standard, numpy, pandas, scikit-learn, scipy, matplotlib, sqlite3, `plotly.express` simplifié, `brewly`, `fakeapi`, `cloudsync`, `immo`, `paiements`, `minifast`, pydantic, `llm` (avec `await` au premier niveau). Les modules locaux importés sont listés dans `LOCAL` (`web/src/app.js`) : ajoute-y tout nouveau module de `labs/`. Pas de réseau, pas de PyTorch : ce qui en a besoin passe en `pycode` et en tâches « sur ton ordinateur ».

## Vagues publiées

1. Parcours Jedha, POO avancée, API, SQL, ETL, AWS.
2. Essentials : LLM, prompts, tokens, agents, workflows, évaluation, n8n, RAG, projet Demo Day.
3. Machine learning : prétraitement avancé, Ridge et Lasso, grid search, arbres et forêts, boosting, séries temporelles, K-means, projet immobilier.
4. Deep learning : neurone et activations, perceptron, rétropropagation, PyTorch, convolutions, embeddings, MLP from scratch.
5. Architectures génératives et adaptation (F6, F7) : attention, Transformer en NumPy, tokenisation, Hugging Face, CLIP, diffusion, projet mini-GPT avec cache KV, LoRA et QLoRA, apprentissage par renforcement, RLHF et DPO.
6. Ingénierie ML et IA (F8, F9, F10) : terminal, Streamlit, Docker, EC2, MLflow, asynchrone, FastAPI (avec `minifast`), projet anti-fraude, LangChain et LangGraph, observabilité, vLLM, MCP.

## Prochaines vagues prévues

7. Lead : gouvernance, tests et CI/CD, surveillance de la dérive, LLMOps, sécurité.
