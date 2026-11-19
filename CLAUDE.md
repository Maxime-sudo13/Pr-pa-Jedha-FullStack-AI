# Instructions pour Claude Code

**Prépa AI** : plateforme de préparation aux formations de Jedha, dans l'ordre Essentials AI (en premier, en bonus), puis **FullStack AI** et **Lead AI**. L'apprenant est francophone, adulte, en reconversion, et vise un très haut niveau. On le tutoie.

## Architecture

| Chemin | Rôle |
| --- | --- |
| `content/parcours.py` | La carte des 3 programmes Jedha : modules, sections officielles, leçons qui les couvrent, plan de 11 semaines |
| `content/w1.py` … `w4.py` | Les 25 premières leçons (format `WEEK`) |
| `content/f1_poo.py`, `f3_infra.py`, `e_genai.py`, `f4_ml.py`, `f5_dl.py`, `f6_gen.py`, `f7_adapt.py`, `f8_mlops.py`, `f10_aieng.py`, `f11_carriere.py`, `l_infra.py`, `l_ops.py` | Les leçons des vagues 1 à 7 (format `LESSONS`, `PROJECTS`, `QUIZZES`) |
| `labs/` | `brewly` (base SQLite), `fakeapi` (fausse API), `cloudsync` (base de connaissances RAG), `immo` (ventes d'appartements pour le ML), `paiements` (transactions et fraudes, avec dérive mensuelle via `mois=`), `minifast` (imitation de FastAPI avec TestClient), `llm` (appel d'un vrai LLM depuis Python, ou réponse simulée hors plateforme) |
| `runner.py`, `pxshim.py` | Exécution des cellules et version simplifiée de plotly.express (navigateur) |
| `web/src/` | L'application : `app.js` (vues, progression, Pyodide, tuteur), `viz.js` (animations), `base.css` et `extra.css` (mise en page), `cyber.css` (thème, chargé en dernier) |
| `web/assemble.py` | Assemble `web/src/` en un seul `web/index.html` |
| `build.py` | Construit `dist/` : markdown → HTML, LaTeX → SVG, blocs ```` ```viz nom ```` → animations |
| `test_all.py` | Teste tous les blocs de code et tous les exercices |
| `make_notebooks.py` | Génère un notebook par module et `CORRIGES.md` |

## Ajouter une vague de contenu

1. Crée `content/<module>_<sujet>.py` avec `LESSONS`, `PROJECTS` et `QUIZZES` (même format que `f3_infra.py`).
2. Référence les nouvelles leçons dans les `sections` du module concerné dans `content/parcours.py`.
3. Pour une animation, ajoute une fonction `VIZ.<nom> = el => {...}` dans `web/src/viz.js` et un bloc ```` ```viz <nom> ```` dans la leçon.
4. Lance `python test_all.py`, `python web/assemble.py`, `python build.py`, `python make_notebooks.py`.
5. Toute nouvelle bibliothèque utilisée par une leçon doit être ajoutée à la ligne `pip install` de `.github/workflows/pages.yml` (et à `requirements.txt`) : sinon les tests échouent sur GitHub et le site n'est pas publié.

## Règles de contenu

- Français, tutoiement, phrases courtes, exemples concrets. Les noms de modules suivent ceux de Jedha.
- Chaque exercice : `prompt`, `starter`, `solution`, `check` (des `assert` dont le message aide à corriger), `hint`. La vérification doit passer avec la solution **et échouer** avec le code de départ. Recalcule la valeur attendue dans `check` quand c'est possible.
- Blocs de code : ```` ```python ```` exécutable dans le navigateur, ```` ```pycode ```` affiché seulement, ```` ```latex ```` formule, ```` ```viz nom ```` animation.
- Disponible dans le navigateur : bibliothèque standard, numpy, pandas, scikit-learn, scipy, matplotlib, sqlite3, `plotly.express` simplifié, `brewly`, `fakeapi`, `cloudsync`, `immo`, `paiements`, `minifast`, pydantic, `llm` (avec `await` au premier niveau). Les modules locaux importés sont listés dans `LOCAL` (`web/src/app.js`) : ajoute-y tout nouveau module de `labs/`. Pas de réseau, pas de PyTorch : ce qui en a besoin passe en `pycode` et en tâches « sur ton ordinateur ».

## Règles de style

- Thème sombre unique, « cyber » : noir profond, bleu électrique (`--accent`), cyan (`--accent-2`), dégradé `--grad`, lueurs `--glow`. Tout est dans `web/src/cyber.css`, qui redéfinit les variables de `base.css`.
- Utilise toujours les variables CSS (`--ink`, `--muted`, `--line`, `--surface`, `--accent`, `--mark`, `--ok`, `--err`) plutôt que des couleurs en dur, y compris dans les animations (`vz-*`).
- Les animations d'apparition respectent `prefers-reduced-motion`.
- Vérifie le rendu par des captures à 400 px de large (téléphone) et à 1 280 px.

## Vagues publiées

1. Parcours Jedha, POO avancée, API, SQL, ETL, AWS.
2. Essentials : LLM, prompts, tokens, agents, workflows, évaluation, n8n, RAG, projet Demo Day.
3. Machine learning : prétraitement avancé, Ridge et Lasso, grid search, arbres et forêts, boosting, séries temporelles, K-means, projet immobilier.
4. Deep learning : neurone et activations, perceptron, rétropropagation, PyTorch, convolutions, embeddings, MLP from scratch.
5. Architectures génératives et adaptation (F6, F7) : attention, Transformer en NumPy, tokenisation, Hugging Face, CLIP, diffusion, projet mini-GPT avec cache KV, LoRA et QLoRA, apprentissage par renforcement, RLHF et DPO.
6. Ingénierie ML et IA (F8, F9, F10) : terminal, Streamlit, Docker, EC2, MLflow, asynchrone, FastAPI (avec `minifast`), projet anti-fraude, LangChain et LangGraph, observabilité, vLLM, MCP.
7. Lead AI (L1 à L6) et coaching de carrière (F11) : gouvernance et qualité des données, catalogue et lignage, GPU, Kubernetes et Helm, Ray et ZeRO, Terraform et réseau AWS, Airflow, tests et mutation, CI/CD, entraînement continu et canary, dérive (PSI, KS), évaluation continue des RAG, GraphRAG, garde-fous, Demo Day, projet MLOps de surveillance, CV et entretiens.

Toutes les sections des trois programmes sont couvertes. Les évolutions possibles : approfondir une section, ajouter des projets, ou mettre à jour le contenu quand Jedha fait évoluer ses programmes.
