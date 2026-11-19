"""FullStack · Coaching de carrière (vague 7) : CV, LinkedIn, portfolio et entretiens techniques."""

def E(id, title, prompt, starter, solution, check, hint):
    return {"id": id, "title": title, "prompt": prompt, "starter": starter, "solution": solution, "check": check, "hint": hint}

LESSONS = [
# ================================================================ Préparer ses entretiens
{"id": "l-carriere", "title": "CV, LinkedIn et portfolio d'un ingénieur IA", "minutes": 60,
"body": r'''
En reconversion, ton atout n'est pas un diplôme d'ingénieur : ce sont **des preuves**. Un recruteur passe moins d'une minute sur un CV et quelques minutes sur un GitHub. Tout doit montrer, vite, que tu sais livrer de l'IA qui fonctionne.

## Le CV : une page, des résultats

- **Un titre clair** : « Ingénieur IA » ou « AI Engineer », pas « en reconversion ».
- **Trois à quatre projets** en tête, chacun en deux lignes : le problème, ce que tu as construit, un **résultat chiffré**. Par exemple : « API de détection de fraude (FastAPI, Docker, AWS) : AUC 0,96, seuil choisi au coût métier, coût des erreurs divisé par 3,4 ».
- **Les compétences**, regroupées : langages, ML et deep learning, LLM et agents, MLOps et cloud. Seulement ce que tu peux défendre en entretien.
- **Ton parcours précédent est une force** : 10 ans en logistique, en finance ou en santé, c'est une connaissance métier que les profils purement techniques n'ont pas. Fais le lien explicitement.

## LinkedIn

Le titre (« AI Engineer · LLM, RAG, MLOps »), un résumé de trois lignes, les projets en section « Projets » avec un lien, et une activité régulière : partager un projet terminé, ce que tu as appris, une démonstration vidéo. Les recruteurs cherchent par mots-clés : « LLM », « RAG », « FastAPI », « Docker », « AWS », « PyTorch ».

## Le portfolio GitHub

- Un **README de profil** qui présente tes 3 meilleurs projets.
- Pour chaque projet : un README avec le problème, une capture ou une vidéo, l'architecture (un schéma), comment le lancer en une commande, les résultats, et les limites.
- Du code propre : structure de projet, tests, un workflow de CI qui passe (le badge vert compte).
- Une **démo en ligne** quand c'est possible (Streamlit Cloud, Hugging Face Spaces) : un recruteur clique plus volontiers qu'il ne clone.

> **À retenir** : des preuves plutôt que des promesses. Des projets chiffrés en tête du CV, un LinkedIn riche en mots-clés et actif, des dépôts GitHub soignés avec README, tests et démo.
''',
"tasks": [
  "Réécrire ton CV sur une page avec 3 projets chiffrés issus de cette plateforme",
  "Créer le README de ton profil GitHub et épingler tes 3 meilleurs dépôts",
  "Mettre à jour ton titre et ton résumé LinkedIn, et publier un post sur un projet terminé",
  "Mettre en ligne une démo (Streamlit Cloud ou Hugging Face Spaces) d'un de tes projets",
]},
# ================================================================ Entretiens techniques
{"id": "l-entretien", "title": "Réussir les entretiens techniques", "minutes": 90,
"body": r'''
Un processus de recrutement en IA comporte en général quatre types d'épreuves. Chacune se prépare.

## 1. Le code (Python et SQL)

Des exercices de 20 à 45 minutes : manipuler des listes et des dictionnaires, une requête SQL avec jointures et fonctions de fenêtre, parfois un petit algorithme. **Parle à voix haute** : explique ta démarche, commence par une solution simple qui marche, puis améliore-la, et teste-la sur un exemple. Les deux exercices de cette page sont des classiques.

## 2. Les connaissances en ML et en IA

Des questions ouvertes : « Comment gérer des classes déséquilibrées ? », « Différence entre fine-tuning et RAG ? », « Comment évalues-tu un LLM ? », « Qu'est-ce que le surapprentissage, et comment le détecter ? ». Les quiz de cette plateforme couvrent l'essentiel : refais-les, et entraîne-toi à répondre à voix haute en deux minutes.

## 3. La conception de système ML

« Conçois un système de recommandation pour une plateforme de vidéos. » Il n'y a pas de réponse unique ; on évalue ta démarche. Une trame qui marche :

1. **Clarifier** : l'objectif métier, les utilisateurs, les volumes, les contraintes de latence et de coût.
2. **La métrique** : hors ligne (précision, AUC…) et en ligne (taux de clic, revenu), et le lien entre les deux.
3. **Les données** : sources, étiquettes, variables, fraîcheur.
4. **Le modèle** : une référence simple d'abord, puis mieux, en justifiant.
5. **Le service** : batch ou temps réel, API, mise en cache, montée en charge.
6. **La surveillance** : dérive, retours, réentraînement, tests A/B.
7. **Les risques** : biais, sécurité, vie privée, coûts.

## 4. L'entretien comportemental

« Parle-moi d'un échec », « d'un désaccord dans une équipe ». Réponds avec la méthode **STAR** : **S**ituation, **T**âche, **A**ction (ce que **toi** tu as fait), **R**ésultat (chiffré si possible, et ce que tu en as appris). Prépare 5 histoires, dont certaines tirées de ton ancien métier.

## Les questions à poser à la fin

« Comment mesurez-vous le succès de ce poste à six mois ? », « Quels modèles sont en production, et comment sont-ils surveillés ? », « Comment l'équipe choisit-elle entre construire et acheter (API de LLM ou modèle maison) ? ». Elles montrent que tu penses déjà comme un ingénieur de production.

> **À retenir** : code à voix haute, simple d'abord ; connaissances en deux minutes ; conception de système avec une trame en 7 étapes ; histoires STAR ; et de bonnes questions à la fin.
''',
"tasks": [
  "Refaire tous les quiz de la plateforme et viser 100 %",
  "Faire à voix haute, chronométré, l'exercice de conception « système de détection de fraude en temps réel »",
  "Écrire 5 histoires STAR, dont 2 tirées de ton parcours précédent",
  "Passer un entretien blanc avec un pair de ta promotion Jedha ou sur un site d'entraînement",
],
"exercises": [
 E("e-int-a", "Un classique de code : les k mots les plus fréquents",
   "Écris `top_k(texte, k)` qui renvoie la liste des `k` mots les plus fréquents du texte, sous forme de tuples `(mot, nombre)`. Les mots sont en minuscules et formés de lettres (accents compris) : utilise `re.findall(r\"[a-zà-öø-ÿ]+\", texte.lower())`. En cas d'égalité de fréquence, l'ordre alphabétique départage.",
   r'''import re
from collections import Counter

def top_k(texte, k):
    pass
''',
   r'''import re
from collections import Counter

def top_k(texte, k):
    mots = re.findall(r"[a-zà-öø-ÿ]+", texte.lower())
    return sorted(Counter(mots).items(), key=lambda t: (-t[1], t[0]))[:k]

texte = "Le modèle apprend. Le modèle généralise, le modèle se trompe parfois ; apprend encore."
print(top_k(texte, 3))
''',
   r'''t = "Le modèle apprend. Le modèle généralise, le modèle se trompe parfois ; apprend encore."
assert top_k(t, 3) == [("le", 3), ("modèle", 3), ("apprend", 2)], f"Attendu [('le', 3), ('modèle', 3), ('apprend', 2)] ; tu as {top_k(t, 3)}. À égalité, l'ordre alphabétique départage."
assert top_k("b a c b a", 2) == [("a", 2), ("b", 2)], "À fréquence égale, ordre alphabétique."
assert top_k("Été ÉTÉ été", 1) == [("été", 3)], "Les mots sont mis en minuscules, accents compris."
assert top_k("", 3) == [], "Un texte vide donne une liste vide."
''',
   "Counter(mots).items(), puis sorted avec la clé (-nombre, mot) : le signe moins trie les fréquences de la plus grande à la plus petite."),
 E("e-int-b", "Un classique SQL : le classement par groupe",
   "Sur la base Brewly, écris la requête `requete` qui renvoie, pour chaque ville, les **2 clients** qui ont le plus dépensé : colonnes `ville`, `client_id`, `depense` (somme de quantité × prix, arrondie à 2 décimales) et `rang` (1 ou 2). Utilise une fonction de fenêtre `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)` ; à dépense égale, le plus petit `client_id` passe devant. Trie le résultat par ville puis par rang.",
   r'''import pandas as pd
from brewly import connecter
con = connecter()

requete = """
SELECT 1
"""
res = pd.read_sql_query(requete, con)
res
''',
   r'''import pandas as pd
from brewly import connecter
con = connecter()

requete = """
WITH depenses AS (
    SELECT cl.ville, cl.id AS client_id, ROUND(SUM(l.quantite * p.prix), 2) AS depense
    FROM clients cl
    JOIN commandes c ON c.client_id = cl.id
    JOIN lignes l ON l.commande_id = c.id
    JOIN produits p ON p.id = l.produit_id
    GROUP BY cl.ville, cl.id
),
classes AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY ville ORDER BY depense DESC, client_id) AS rang
    FROM depenses
)
SELECT ville, client_id, depense, rang FROM classes WHERE rang <= 2 ORDER BY ville, rang
"""
res = pd.read_sql_query(requete, con)
res
''',
   r'''import pandas as pd
q = """SELECT cl.ville, cl.id AS client_id, l.quantite * p.prix AS m FROM clients cl JOIN commandes c ON c.client_id = cl.id
       JOIN lignes l ON l.commande_id = c.id JOIN produits p ON p.id = l.produit_id"""
d = pd.read_sql_query(q, con).groupby(["ville", "client_id"], as_index=False)["m"].sum()
d["depense"] = d["m"].round(2)
d = d.sort_values(["ville", "depense", "client_id"], ascending=[True, False, True])
d["rang"] = d.groupby("ville").cumcount() + 1
attendu = d[d["rang"] <= 2][["ville", "client_id", "depense", "rang"]].reset_index(drop=True)
res = pd.read_sql_query(requete, con)
assert list(res.columns) == ["ville", "client_id", "depense", "rang"], f"Colonnes attendues : ville, client_id, depense, rang ; tu as {list(res.columns)}."
assert len(res) == 10, f"5 villes × 2 clients = 10 lignes ; tu en as {len(res)}."
assert res["ville"].tolist() == attendu["ville"].tolist() and res["rang"].tolist() == attendu["rang"].tolist(), "Trie par ville puis par rang."
assert res["client_id"].tolist() == attendu["client_id"].tolist(), "Les clients ne sont pas les bons : ROW_NUMBER() OVER (PARTITION BY ville ORDER BY depense DESC, client_id)."
assert (res["depense"].round(2) == attendu["depense"]).all(), "La dépense est la somme de quantité × prix, arrondie à 2 décimales."
''',
   "Deux CTE (WITH) : la première calcule la dépense par ville et client (jointure des 4 tables, GROUP BY), la seconde ajoute ROW_NUMBER() ; puis WHERE rang <= 2."),
]},
]
