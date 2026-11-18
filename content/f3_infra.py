LESSONS = [
# ---------------------------------------------------------------- API 1
{"id": "l-api-1", "title": "API web : HTTP, JSON et requests", "minutes": 80,
"body": r'''
Une **API web** permet à deux programmes de communiquer par Internet. C'est par une API que tu récupères des données (météo, finance, livres) et que tu appelles un modèle de langage. L'Essentials y consacre une demi-journée, et le FullStack y revient dans le module Infrastructure de données (« API et Python »).

```viz http
```

## Le protocole HTTP

Une requête HTTP contient :
- une **méthode** : `GET` pour lire, `POST` pour créer ou envoyer, `PUT`/`PATCH` pour modifier, `DELETE` pour supprimer ;
- une **URL** : `https://api.exemple.com/books/42?langue=fr`, avec un chemin (`/books/42`) et des **paramètres** (`?langue=fr`) ;
- des **en-têtes** (*headers*) : par exemple la clé d'API dans `Authorization` ;
- éventuellement un **corps** (*body*), souvent en JSON, pour POST et PUT.

La réponse contient un **code de statut** et un corps :

| Code | Signification | Que faire |
| --- | --- | --- |
| 200 | OK | Lire le corps |
| 201 | Créé | La ressource a été créée |
| 400 | Requête invalide | Corriger les paramètres |
| 401 / 403 | Non authentifié / interdit | Vérifier la clé d'API |
| 404 | Introuvable | Vérifier l'URL ou l'identifiant |
| 429 | Trop de requêtes | Attendre, puis réessayer |
| 500 / 503 | Erreur du serveur | Réessayer plus tard |

## Le JSON

Le **JSON** est le format d'échange des API. Il correspond presque exactement aux dictionnaires et listes Python.

```python
import json

texte = '{"titre": "Fondation", "annee": 1951, "sujets": ["science-fiction", "empire"], "disponible": true}'
livre = json.loads(texte)             # texte JSON → objet Python
print(livre["sujets"][0], type(livre["disponible"]))
print(json.dumps(livre, ensure_ascii=False, indent=2))   # objet Python → texte JSON
```

## Faire une requête

Sur ton ordinateur, on utilise la bibliothèque `requests`. Ici, sans accès à Internet, on utilise `fakeapi` : une fausse API de livres qui s'utilise **exactement** de la même façon. Sa base est `https://api.biblio.test`.

```python
import fakeapi as requests        # sur ton ordinateur : import requests

BASE = "https://api.biblio.test"
r = requests.get(f"{BASE}/books/3")
print(r.status_code, r.ok)
livre = r.json()
print(livre["titre"], "-", livre["note"]["moyenne"], "/ 5")
```

```python
r = requests.get(f"{BASE}/books", params={"page": 1, "limit": 5})
donnees = r.json()
print(donnees.keys())
[l["titre"] for l in donnees["resultats"]]
```

## Gérer les erreurs

Une API peut répondre par une erreur sans que Python ne plante. Vérifie toujours le statut, ou appelle `raise_for_status()`, qui lève une exception en cas d'erreur.

```python
r = requests.get(f"{BASE}/books/999")
print(r.status_code, r.json())
try:
    r.raise_for_status()
except requests.HTTPError as err:
    print("Erreur attrapée :", err)
```

## L'authentification

La plupart des API exigent une **clé**, envoyée dans un en-tête. Ne l'écris jamais en dur dans ton code : lis-la depuis une variable d'environnement.

```python
print(requests.get(f"{BASE}/secure").status_code)
r = requests.get(f"{BASE}/secure", headers={"Authorization": "Bearer cle-demo"})
print(r.status_code, r.json())
```

```pycode
# Sur ton ordinateur
import os, requests
cle = os.environ["MA_CLE_API"]          # définie dans un fichier .env, jamais publié
r = requests.get("https://api.exemple.com/data", headers={"Authorization": f"Bearer {cle}"}, timeout=10)
```

> **À retenir** : statut d'abord, JSON ensuite. Mets toujours un `timeout` sur tes requêtes réelles, et ne publie jamais une clé d'API.
''',
"exercises": [
 {"id": "e-api-1-a", "title": "Extraire des champs imbriqués",
  "prompt": "Récupère le livre d'identifiant 6 et crée un dictionnaire `resume` avec les clés `titre`, `annee`, `note` (la **moyenne**, un nombre) et `premier_sujet`.",
  "starter": 'import fakeapi as requests\nBASE = "https://api.biblio.test"\n',
  "solution": 'import fakeapi as requests\nBASE = "https://api.biblio.test"\nlivre = requests.get(f"{BASE}/books/6").json()\nresume = {\n    "titre": livre["titre"],\n    "annee": livre["annee"],\n    "note": livre["note"]["moyenne"],\n    "premier_sujet": livre["sujets"][0],\n}\nresume\n',
  "hint": "livre[\"note\"] est lui-même un dictionnaire ; livre[\"sujets\"] est une liste.",
  "check": 'assert resume == {"titre": "La Horde du Contrevent", "annee": 2004, "note": 4.6, "premier_sujet": "fantasy"}, f"resume vaut {resume}."\n'},
 {"id": "e-api-1-b", "title": "Une fonction robuste",
  "prompt": "Écris `titre_du_livre(livre_id)` qui renvoie le titre du livre, ou `None` si l'API répond autre chose que 200 (par exemple 404).",
  "starter": 'import fakeapi as requests\nBASE = "https://api.biblio.test"\n\ndef titre_du_livre(livre_id):\n    pass\n',
  "solution": 'import fakeapi as requests\nBASE = "https://api.biblio.test"\n\ndef titre_du_livre(livre_id):\n    r = requests.get(f"{BASE}/books/{livre_id}")\n    if r.status_code != 200:\n        return None\n    return r.json()["titre"]\n\nprint(titre_du_livre(1), titre_du_livre(999))\n',
  "hint": "Teste r.status_code avant d'appeler r.json().",
  "check": 'assert titre_du_livre(1) == "Frankenstein", "titre_du_livre(1) devrait renvoyer Frankenstein."\nassert titre_du_livre(999) is None, "Pour un livre inexistant, la fonction doit renvoyer None."\nassert titre_du_livre("abc") is None, "Pour un identifiant invalide aussi."\n'},
 {"id": "e-api-1-c", "title": "Joindre deux ressources",
  "prompt": "Pour chaque livre de la première page (`limit=5`), récupère son auteur via `/authors/<auteur_id>` et construis la liste `lignes` de chaînes au format `Titre — Auteur (année)`, par exemple `Frankenstein — Mary Shelley (1818)`. N'appelle qu'**une seule fois** chaque auteur (utilise un dictionnaire comme cache).",
  "starter": 'import fakeapi as requests\nBASE = "https://api.biblio.test"\nrequests.reset()\n',
  "solution": 'import fakeapi as requests\nBASE = "https://api.biblio.test"\nrequests.reset()\n\nlivres = requests.get(f"{BASE}/books", params={"page": 1, "limit": 5}).json()["resultats"]\ncache = {}\nlignes = []\nfor l in livres:\n    aid = l["auteur_id"]\n    if aid not in cache:\n        cache[aid] = requests.get(f"{BASE}/authors/{aid}").json()\n    lignes.append(f"{l[\'titre\']} — {cache[aid][\'nom\']} ({l[\'annee\']})")\nlignes\n',
  "hint": "Avant d'appeler /authors/..., regarde si l'auteur est déjà dans ton dictionnaire cache.",
  "check": 'import fakeapi\nassert lignes[0] == "Frankenstein — Mary Shelley (1818)", f"Première ligne : {lignes[0]!r}."\nassert len(lignes) == 5, "Il faut une ligne par livre de la première page (5)."\nn_auteurs = sum(1 for a in fakeapi.appels if "/authors/" in a["url"])\nassert n_auteurs == 3, f"Tu as appelé /authors/ {n_auteurs} fois ; avec un cache, 3 appels suffisent (3 auteurs différents)."\n'},
]},
# ---------------------------------------------------------------- API 2
{"id": "l-api-2", "title": "Collecter des données : pagination, reprises, pipeline", "minutes": 80,
"body": r'''
Dans un vrai projet, on ne fait pas une requête mais des centaines : il faut parcourir des **pages**, survivre aux **erreurs temporaires** et ranger proprement le résultat. C'est l'objet des projets « Collecteur de données FinPulse » et « Créer un pipeline de données pour les livres ».

## La pagination

Une API renvoie rarement tout d'un coup. Elle découpe les résultats en pages et indique comment obtenir la suivante.

```python
import fakeapi as requests
BASE = "https://api.biblio.test"

tous = []
page = 1
while page is not None:
    r = requests.get(f"{BASE}/books", params={"page": page, "limit": 10})
    r.raise_for_status()
    donnees = r.json()
    tous.extend(donnees["resultats"])
    page = donnees["page_suivante"]          # None quand c'est fini
print(len(tous), "livres récupérés sur", donnees["total"])
```

Autres formes courantes : un `offset`, un `cursor` opaque, ou un lien `next` dans la réponse. Le principe est toujours une boucle `while`.

## Les reprises avec attente exponentielle

Les erreurs **429** (trop de requêtes) et **5xx** (serveur) sont souvent temporaires : on réessaie après une pause, en doublant la pause à chaque échec (*exponential backoff*). Les erreurs **4xx** autres que 429 ne servent à rien à réessayer : c'est ta requête qui est fausse.

```python
import time

def get_avec_reprises(url, essais=4, pause=0.01, **kwargs):
    for tentative in range(essais):
        r = requests.get(url, **kwargs)
        if r.status_code == 429 or r.status_code >= 500:
            attente = pause * 2 ** tentative
            print(f"  tentative {tentative + 1} : {r.status_code}, nouvel essai dans {attente:.2f} s")
            time.sleep(attente)
            continue
        return r
    raise RuntimeError(f"Échec après {essais} tentatives")

requests.reset()
print(get_avec_reprises(f"{BASE}/flaky").json())
```

Sur une vraie API, respecte l'en-tête `Retry-After` quand il est présent : il dit combien de secondes attendre.

## Du JSON au tableau

`pd.json_normalize` aplatit des JSON imbriqués en colonnes.

```python
import pandas as pd
df = pd.json_normalize(tous)
print(df.columns.tolist())
df[["titre", "annee", "note.moyenne", "note.votes"]].sort_values("note.moyenne", ascending=False).head()
```

> **À retenir** : un collecteur de données professionnel pagine, réessaie intelligemment, journalise ce qu'il fait et ne refait pas les appels inutiles (cache). Sur ton ordinateur, ajoute aussi un `timeout` et respecte les limites de l'API.
''',
"exercises": [
 {"id": "e-api-2-a", "title": "Une fonction de pagination",
  "prompt": "Écris `recuperer_tout(limit)` qui parcourt toutes les pages de `/books` avec ce `limit` et renvoie la liste de tous les livres. Teste avec `limit=4`.",
  "starter": 'import fakeapi as requests\nBASE = "https://api.biblio.test"\n\ndef recuperer_tout(limit):\n    pass\n',
  "solution": 'import fakeapi as requests\nBASE = "https://api.biblio.test"\n\ndef recuperer_tout(limit):\n    tous, page = [], 1\n    while page is not None:\n        donnees = requests.get(f"{BASE}/books", params={"page": page, "limit": limit}).json()\n        tous.extend(donnees["resultats"])\n        page = donnees["page_suivante"]\n    return tous\n\nprint(len(recuperer_tout(4)))\n',
  "hint": "Une boucle while page is not None, et page = donnees[\"page_suivante\"] à la fin de chaque tour.",
  "check": 'import fakeapi\nfakeapi.reset()\nres = recuperer_tout(4)\nassert len(res) == 23, f"Tu récupères {len(res)} livres, il y en a 23."\nassert len({l["id"] for l in res}) == 23, "Certains livres sont en double."\nn = sum(1 for a in fakeapi.appels if a["url"].endswith("/books"))\nassert n == 6, f"Avec limit=4, il faut exactement 6 appels ; tu en fais {n}."\n'},
 {"id": "e-api-2-b", "title": "Reprises intelligentes",
  "prompt": "Écris `get_avec_reprises(url, essais=5)` qui réessaie **uniquement** sur les statuts 429 et 5xx, et renvoie immédiatement la réponse dans tous les autres cas (y compris 404). Après `essais` échecs, lève une `RuntimeError`. Utilise des pauses minuscules (`time.sleep(0.001)`) pour l'exercice.",
  "starter": 'import time\nimport fakeapi as requests\nBASE = "https://api.biblio.test"\n\ndef get_avec_reprises(url, essais=5):\n    pass\n',
  "solution": 'import time\nimport fakeapi as requests\nBASE = "https://api.biblio.test"\n\ndef get_avec_reprises(url, essais=5):\n    for i in range(essais):\n        r = requests.get(url)\n        if r.status_code == 429 or r.status_code >= 500:\n            time.sleep(0.001 * 2 ** i)\n            continue\n        return r\n    raise RuntimeError("Trop d\'échecs")\n\nrequests.reset()\nprint(get_avec_reprises(f"{BASE}/flaky").json())\n',
  "hint": "Dans la boucle : si erreur temporaire → pause puis continue ; sinon → return r. Après la boucle → raise.",
  "check": 'import fakeapi\nfakeapi.reset()\nr = get_avec_reprises(f"{BASE}/flaky")\nassert r.status_code == 200 and r.json()["tentative"] == 3, "Sur /flaky, il faut 3 tentatives pour réussir."\nfakeapi.reset()\nr = get_avec_reprises(f"{BASE}/books/999")\nassert r.status_code == 404 and len(fakeapi.appels) == 1, "Une 404 ne doit pas être réessayée."\nfakeapi.reset()\ntry:\n    get_avec_reprises(f"{BASE}/flaky", essais=2)\n    assert False, "Avec 2 essais seulement sur /flaky, il faut lever une RuntimeError."\nexcept RuntimeError:\n    pass\n'},
 {"id": "e-api-2-c", "title": "Collecter, aplatir, analyser",
  "prompt": "Récupère tous les livres (toutes les pages), aplatis-les avec `pd.json_normalize` dans `df`, puis crée `top_auteurs` : la note moyenne (`note.moyenne`) par `auteur_id`, triée par ordre décroissant.",
  "starter": 'import pandas as pd\nimport fakeapi as requests\nBASE = "https://api.biblio.test"\n',
  "solution": 'import pandas as pd\nimport fakeapi as requests\nBASE = "https://api.biblio.test"\n\ntous, page = [], 1\nwhile page:\n    d = requests.get(f"{BASE}/books", params={"page": page, "limit": 20}).json()\n    tous += d["resultats"]\n    page = d["page_suivante"]\n\ndf = pd.json_normalize(tous)\ntop_auteurs = df.groupby("auteur_id")["note.moyenne"].mean().sort_values(ascending=False)\ntop_auteurs\n',
  "hint": "Combine la boucle de pagination, pd.json_normalize(tous), puis un groupby.",
  "check": 'assert len(df) == 23 and "note.moyenne" in df.columns, "df doit contenir les 23 livres aplatis (colonne note.moyenne)."\nassert int(top_auteurs.index[0]) == 5, f"L\'auteur le mieux noté devrait être l\'auteur 5 ; tu as {top_auteurs.index[0]}."\nassert list(top_auteurs.values) == sorted(top_auteurs.values, reverse=True), "Trie par note décroissante."\n'},
]},
# ---------------------------------------------------------------- SQL 1
{"id": "l-sql-1", "title": "SQL : interroger une base de données", "minutes": 75,
"body": r'''
**SQL** est le langage des bases de données relationnelles. Chez Jedha, il arrive au module Infrastructure de données (« Bases du SQL », projet Brewly). Bonne nouvelle : la base d'exemple de cette plateforme s'appelle aussi **Brewly**, une chaîne de cafés, et tu l'interroges avec du vrai SQL, exécuté par **SQLite** dans ton navigateur.

Elle contient quatre tables :

| Table | Colonnes |
| --- | --- |
| `clients` | id, prenom, ville, inscrit_le |
| `produits` | id, nom, categorie, prix |
| `commandes` | id, client_id, date, magasin |
| `lignes` | commande_id, produit_id, quantite |

```python
import pandas as pd
from brewly import connecter

con = connecter()

def sql(requete):
    """Exécute une requête SQL et renvoie un DataFrame."""
    return pd.read_sql_query(requete, con)

sql("SELECT * FROM produits")
```

## SELECT, WHERE, ORDER BY, LIMIT

L'ordre d'écriture est toujours le même : `SELECT` (quelles colonnes), `FROM` (quelle table), `WHERE` (quelles lignes), `ORDER BY` (dans quel ordre), `LIMIT` (combien).

```python
sql("""
SELECT nom, prix
FROM produits
WHERE categorie = 'café' AND prix > 3
ORDER BY prix DESC
""")
```

Quelques opérateurs utiles dans `WHERE` :

```python
sql("""
SELECT prenom, ville, inscrit_le
FROM clients
WHERE ville IN ('Lyon', 'Lille')
  AND prenom LIKE 'L%'            -- commence par L
  AND inscrit_le BETWEEN '2026-02-01' AND '2026-03-31'
ORDER BY inscrit_le
""")
```

## Calculer et renommer

```python
sql("""
SELECT nom,
       prix,
       ROUND(prix * 1.10, 2) AS prix_ttc,
       CASE WHEN prix >= 4 THEN 'premium' ELSE 'standard' END AS gamme
FROM produits
ORDER BY prix_ttc DESC
LIMIT 5
""")
```

`SELECT DISTINCT` supprime les doublons : `SELECT DISTINCT magasin FROM commandes`.

> **À retenir** : SQL décrit **ce que tu veux**, pas comment le calculer. Écris tes mots-clés en majuscules, une clause par ligne : tes requêtes resteront lisibles quand elles grandiront.
''',
"exercises": [
 {"id": "e-sql-1-a", "title": "Les thés abordables",
  "prompt": "Écris dans la variable `requete` une requête SQL qui renvoie le `nom` et le `prix` des produits de la catégorie `thé` coûtant moins de 4,30 €, du moins cher au plus cher. Le code fourni l'exécute dans `res`.",
  "starter": 'import pandas as pd\nfrom brewly import connecter\ncon = connecter()\n\nrequete = """\n\n"""\nres = pd.read_sql_query(requete, con)\nres\n',
  "solution": 'import pandas as pd\nfrom brewly import connecter\ncon = connecter()\n\nrequete = """\nSELECT nom, prix\nFROM produits\nWHERE categorie = \'thé\' AND prix < 4.3\nORDER BY prix\n"""\nres = pd.read_sql_query(requete, con)\nres\n',
  "hint": "WHERE categorie = 'thé' AND prix < 4.3, puis ORDER BY prix.",
  "check": 'assert list(res.columns) == ["nom", "prix"], f"Colonnes : {list(res.columns)}."\nassert list(res["nom"]) == ["Thé vert", "Chaï latte"], f"Résultat : {list(res[\'nom\'])}."\n'},
 {"id": "e-sql-1-b", "title": "Les premières commandes de Bastille",
  "prompt": "Écris `requete` : les 5 **premières** commandes (par date croissante) passées au magasin `Bastille`, avec les colonnes `id` et `date`. En cas d'égalité de date, trie par `id`.",
  "starter": 'import pandas as pd\nfrom brewly import connecter\ncon = connecter()\n\nrequete = """\n\n"""\nres = pd.read_sql_query(requete, con)\nres\n',
  "solution": 'import pandas as pd\nfrom brewly import connecter\ncon = connecter()\n\nrequete = """\nSELECT id, date\nFROM commandes\nWHERE magasin = \'Bastille\'\nORDER BY date, id\nLIMIT 5\n"""\nres = pd.read_sql_query(requete, con)\nres\n',
  "hint": "ORDER BY date, id puis LIMIT 5.",
  "check": 'ref = pd.read_sql_query("SELECT id, date FROM commandes WHERE magasin = \'Bastille\' ORDER BY date, id LIMIT 5", con)\nassert list(res.columns) == ["id", "date"], f"Colonnes : {list(res.columns)}."\nassert res.equals(ref), "Le résultat ne correspond pas : vérifie le filtre, le tri et la limite."\n'},
]},
# ---------------------------------------------------------------- SQL 2
{"id": "l-sql-2", "title": "SQL : agréger avec GROUP BY", "minutes": 60,
"body": r'''
`GROUP BY` est l'équivalent SQL du `groupby` de pandas : on découpe les lignes en groupes, on applique une fonction d'agrégation, on combine.

```viz groupby
```

```python
import pandas as pd
from brewly import connecter
con = connecter()
sql = lambda q: pd.read_sql_query(q, con)

sql("""
SELECT magasin,
       COUNT(*)            AS nb_commandes,
       MIN(date)           AS premiere,
       MAX(date)           AS derniere
FROM commandes
GROUP BY magasin
ORDER BY nb_commandes DESC
""")
```

Les fonctions d'agrégation : `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`. `COUNT(DISTINCT client_id)` compte les valeurs différentes.

## Filtrer après agrégation : HAVING

`WHERE` filtre les **lignes avant** le regroupement ; `HAVING` filtre les **groupes après**.

```python
sql("""
SELECT client_id, COUNT(*) AS nb
FROM commandes
WHERE date >= '2026-04-01'
GROUP BY client_id
HAVING COUNT(*) >= 4
ORDER BY nb DESC
""")
```

## Grouper par une expression

SQLite stocke ici les dates comme du texte `AAAA-MM-JJ` : `SUBSTR(date, 1, 7)` en extrait le mois. Dans PostgreSQL, tu utiliserais `DATE_TRUNC('month', date)`.

```python
sql("""
SELECT SUBSTR(date, 1, 7) AS mois, COUNT(*) AS commandes
FROM commandes
GROUP BY mois
ORDER BY mois
""")
```

> **À retenir** : l'ordre d'exécution logique est FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT. C'est pour cela qu'un alias défini dans SELECT n'est pas toujours utilisable dans WHERE.
''',
"exercises": [
 {"id": "e-sql-2-a", "title": "Les magasins par mois",
  "prompt": "Écris `requete` qui compte le nombre de commandes par `magasin` pour le mois de mars 2026 uniquement, dans une colonne `nb`, triée par `nb` décroissant puis par `magasin`.",
  "starter": 'import pandas as pd\nfrom brewly import connecter\ncon = connecter()\n\nrequete = """\n\n"""\nres = pd.read_sql_query(requete, con)\nres\n',
  "solution": 'import pandas as pd\nfrom brewly import connecter\ncon = connecter()\n\nrequete = """\nSELECT magasin, COUNT(*) AS nb\nFROM commandes\nWHERE date BETWEEN \'2026-03-01\' AND \'2026-03-31\'\nGROUP BY magasin\nORDER BY nb DESC, magasin\n"""\nres = pd.read_sql_query(requete, con)\nres\n',
  "hint": "Le filtre sur le mois va dans WHERE (avant le regroupement). Tu peux utiliser BETWEEN ou SUBSTR(date, 1, 7) = '2026-03'.",
  "check": 'ref = pd.read_sql_query("SELECT magasin, COUNT(*) AS nb FROM commandes WHERE SUBSTR(date,1,7) = \'2026-03\' GROUP BY magasin ORDER BY nb DESC, magasin", con)\nassert list(res.columns) == ["magasin", "nb"], f"Colonnes : {list(res.columns)}."\nassert res.equals(ref), "Le résultat ne correspond pas. Vérifie le filtre sur mars et le tri."\n'},
 {"id": "e-sql-2-b", "title": "Les clients fidèles",
  "prompt": "Écris `requete` qui renvoie les `client_id` ayant passé **au moins 13 commandes**, avec leur nombre de commandes dans `nb` et le nombre de magasins différents fréquentés dans `nb_magasins`, triés par `nb` décroissant puis par `client_id`.",
  "starter": 'import pandas as pd\nfrom brewly import connecter\ncon = connecter()\n\nrequete = """\n\n"""\nres = pd.read_sql_query(requete, con)\nres\n',
  "solution": 'import pandas as pd\nfrom brewly import connecter\ncon = connecter()\n\nrequete = """\nSELECT client_id, COUNT(*) AS nb, COUNT(DISTINCT magasin) AS nb_magasins\nFROM commandes\nGROUP BY client_id\nHAVING COUNT(*) >= 13\nORDER BY nb DESC, client_id\n"""\nres = pd.read_sql_query(requete, con)\nres\n',
  "hint": "Le seuil porte sur un agrégat : il va dans HAVING. COUNT(DISTINCT magasin) compte les magasins différents.",
  "check": 'ref = pd.read_sql_query("SELECT client_id, COUNT(*) AS nb, COUNT(DISTINCT magasin) AS nb_magasins FROM commandes GROUP BY client_id HAVING COUNT(*) >= 13 ORDER BY nb DESC, client_id", con)\nassert list(res.columns) == ["client_id", "nb", "nb_magasins"], f"Colonnes : {list(res.columns)}."\nassert len(ref) > 0 and res.equals(ref), "Le résultat ne correspond pas. Le seuil va dans HAVING, pas dans WHERE."\n'},
]},
# ---------------------------------------------------------------- SQL 3
{"id": "l-sql-3", "title": "SQL : jointures et sous-requêtes", "minutes": 80,
"body": r'''
Les données sont réparties dans plusieurs tables pour éviter les répétitions (on dit qu'elles sont **normalisées**). Une **jointure** les recolle grâce aux clés : `commandes.client_id` pointe vers `clients.id`.

```viz join
```

## INNER JOIN

Garde uniquement les lignes qui ont une correspondance des deux côtés.

```python
import pandas as pd
from brewly import connecter
con = connecter()
sql = lambda q: pd.read_sql_query(q, con)

sql("""
SELECT c.id, c.date, cl.prenom, cl.ville
FROM commandes AS c
INNER JOIN clients AS cl ON cl.id = c.client_id
ORDER BY c.id
LIMIT 5
""")
```

## Plusieurs jointures pour calculer un chiffre d'affaires

```python
sql("""
SELECT p.categorie,
       SUM(l.quantite)                     AS articles,
       ROUND(SUM(l.quantite * p.prix), 2)  AS chiffre_affaires
FROM lignes AS l
JOIN produits AS p ON p.id = l.produit_id
GROUP BY p.categorie
ORDER BY chiffre_affaires DESC
""")
```

## LEFT JOIN : garder ce qui n'a pas de correspondance

`LEFT JOIN` garde **toutes** les lignes de la table de gauche ; les colonnes de droite valent `NULL` quand il n'y a pas de correspondance. C'est la méthode pour trouver « ceux qui n'ont jamais… ».

```python
sql("""
SELECT cl.id, cl.prenom, COUNT(c.id) AS nb_commandes
FROM clients AS cl
LEFT JOIN commandes AS c ON c.client_id = cl.id
GROUP BY cl.id
HAVING nb_commandes = 0
""")
```

## Sous-requêtes et CTE

Une requête peut en utiliser une autre. La forme la plus lisible est la **CTE** (`WITH ... AS`), qui donne un nom à un résultat intermédiaire.

```python
sql("""
WITH panier AS (
    SELECT l.commande_id, SUM(l.quantite * p.prix) AS montant
    FROM lignes l JOIN produits p ON p.id = l.produit_id
    GROUP BY l.commande_id
)
SELECT c.magasin, ROUND(AVG(panier.montant), 2) AS panier_moyen
FROM panier JOIN commandes c ON c.id = panier.commande_id
GROUP BY c.magasin
ORDER BY panier_moyen DESC
""")
```

> **À retenir** : INNER JOIN pour l'intersection, LEFT JOIN pour tout garder à gauche. Dès qu'une requête dépasse 15 lignes, découpe-la en CTE.
''',
"exercises": [
 {"id": "e-sql-3-a", "title": "Chiffre d'affaires par ville",
  "prompt": "Écris `requete` : le chiffre d'affaires total (`ca`, arrondi à 2 décimales) par **ville des clients**, trié par `ca` décroissant. Il faut joindre les quatre tables.",
  "starter": 'import pandas as pd\nfrom brewly import connecter\ncon = connecter()\n\nrequete = """\n\n"""\nres = pd.read_sql_query(requete, con)\nres\n',
  "solution": 'import pandas as pd\nfrom brewly import connecter\ncon = connecter()\n\nrequete = """\nSELECT cl.ville, ROUND(SUM(l.quantite * p.prix), 2) AS ca\nFROM lignes l\nJOIN produits p ON p.id = l.produit_id\nJOIN commandes c ON c.id = l.commande_id\nJOIN clients cl ON cl.id = c.client_id\nGROUP BY cl.ville\nORDER BY ca DESC\n"""\nres = pd.read_sql_query(requete, con)\nres\n',
  "hint": "lignes → produits (pour le prix), lignes → commandes → clients (pour la ville).",
  "check": 'ref = pd.read_sql_query("SELECT cl.ville, ROUND(SUM(l.quantite*p.prix),2) AS ca FROM lignes l JOIN produits p ON p.id=l.produit_id JOIN commandes c ON c.id=l.commande_id JOIN clients cl ON cl.id=c.client_id GROUP BY cl.ville ORDER BY ca DESC", con)\nassert list(res.columns) == ["ville", "ca"], f"Colonnes : {list(res.columns)}."\nassert res.equals(ref), "Les montants ne correspondent pas. Vérifie tes jointures."\n'},
 {"id": "e-sql-3-b", "title": "Les clients jamais venus",
  "prompt": "Écris `requete` qui renvoie l'`id` et le `prenom` des clients qui n'ont **aucune** commande, triés par `id`. Utilise un `LEFT JOIN`.",
  "starter": 'import pandas as pd\nfrom brewly import connecter\ncon = connecter()\n\nrequete = """\n\n"""\nres = pd.read_sql_query(requete, con)\nres\n',
  "solution": 'import pandas as pd\nfrom brewly import connecter\ncon = connecter()\n\nrequete = """\nSELECT cl.id, cl.prenom\nFROM clients cl\nLEFT JOIN commandes c ON c.client_id = cl.id\nWHERE c.id IS NULL\nORDER BY cl.id\n"""\nres = pd.read_sql_query(requete, con)\nres\n',
  "hint": "Après un LEFT JOIN, les clients sans commande ont c.id IS NULL.",
  "check": 'assert list(res.columns) == ["id", "prenom"], f"Colonnes : {list(res.columns)}."\nassert list(res["id"]) == [56, 57, 58, 59, 60], f"ids obtenus : {list(res[\'id\'])}."\n'},
 {"id": "e-sql-3-c", "title": "Le produit star de chaque magasin",
  "prompt": "Écris `requete` (avec une CTE) qui renvoie, pour chaque `magasin`, le `produit` le plus vendu en quantité et cette quantité `qte`, trié par `magasin`. Indice : calcule d'abord les quantités par magasin et produit, puis garde la ligne dont la quantité est le maximum du magasin.",
  "starter": 'import pandas as pd\nfrom brewly import connecter\ncon = connecter()\n\nrequete = """\n\n"""\nres = pd.read_sql_query(requete, con)\nres\n',
  "solution": 'import pandas as pd\nfrom brewly import connecter\ncon = connecter()\n\nrequete = """\nWITH ventes AS (\n    SELECT c.magasin, p.nom AS produit, SUM(l.quantite) AS qte\n    FROM lignes l\n    JOIN commandes c ON c.id = l.commande_id\n    JOIN produits p ON p.id = l.produit_id\n    GROUP BY c.magasin, p.nom\n)\nSELECT v.magasin, v.produit, v.qte\nFROM ventes v\nWHERE v.qte = (SELECT MAX(qte) FROM ventes w WHERE w.magasin = v.magasin)\nORDER BY v.magasin\n"""\nres = pd.read_sql_query(requete, con)\nres\n',
  "hint": "WITH ventes AS (...) puis WHERE v.qte = (SELECT MAX(qte) FROM ventes w WHERE w.magasin = v.magasin). Les fonctions de fenêtre (RANK() OVER ...) marchent aussi.",
  "check": 'ref = pd.read_sql_query("""WITH v AS (SELECT c.magasin, p.nom AS produit, SUM(l.quantite) AS qte FROM lignes l JOIN commandes c ON c.id=l.commande_id JOIN produits p ON p.id=l.produit_id GROUP BY c.magasin, p.nom) SELECT magasin, produit, qte FROM v a WHERE qte = (SELECT MAX(qte) FROM v b WHERE b.magasin=a.magasin) ORDER BY magasin""", con)\nassert list(res.columns) == ["magasin", "produit", "qte"], f"Colonnes : {list(res.columns)}."\nassert res.sort_values(["magasin", "produit"]).reset_index(drop=True).equals(ref.sort_values(["magasin", "produit"]).reset_index(drop=True)), "Le résultat ne correspond pas."\n'},
]},
# ---------------------------------------------------------------- ETL
{"id": "l-etl", "title": "ETL : extraire, transformer, charger", "minutes": 60,
"body": r'''
Un **ETL** (*Extract, Transform, Load*) est le pipeline qui déplace des données d'une source vers un entrepôt : extraire (API, fichiers, base), transformer (nettoyer, typer, agréger), charger (dans une base ou un lac de données). Chez Jedha : « Processus ETL », puis « Pipeline ETL PeopleFirst », puis l'orchestration avec Airflow au module Ingénierie ML.

```viz etl
```

## Un pipeline découpé en fonctions

Chaque étape est une fonction testable séparément. C'est ce qui rend un pipeline maintenable, et c'est exactement ce que fera un orchestrateur comme Airflow : chaque fonction deviendra une tâche.

```python
import sqlite3
import pandas as pd
import fakeapi as requests

BASE = "https://api.biblio.test"

def extraire():
    tous, page = [], 1
    while page:
        d = requests.get(f"{BASE}/books", params={"page": page, "limit": 20}).json()
        tous += d["resultats"]
        page = d["page_suivante"]
    return tous

def transformer(brut):
    df = pd.json_normalize(brut)
    df = df.rename(columns={"note.moyenne": "note", "note.votes": "votes"})
    df["siecle"] = (df["annee"] // 100 + 1).astype(int)
    df["sujets"] = df["sujets"].apply(", ".join)            # une base SQL ne stocke pas de listes
    return df[["id", "titre", "auteur_id", "annee", "siecle", "note", "votes", "sujets", "disponible"]]

def charger(df, con):
    df.to_sql("livres", con, if_exists="replace", index=False)
    return len(df)

con = sqlite3.connect(":memory:")
n = charger(transformer(extraire()), con)
print(n, "livres chargés")
pd.read_sql_query("SELECT siecle, COUNT(*) AS n, ROUND(AVG(note), 2) AS note FROM livres GROUP BY siecle", con)
```

## Les bonnes pratiques

- **Idempotence** : relancer le pipeline donne le même résultat, sans doublons (`if_exists="replace"`, ou une clé unique et un *upsert*).
- **Validation** : vérifie le nombre de lignes, les colonnes et les valeurs manquantes avant de charger.
- **Journalisation** : note ce qui a été extrait, quand, combien de lignes.
- **ELT** : dans les entrepôts modernes (BigQuery, Snowflake), on charge souvent les données brutes d'abord, puis on transforme en SQL.

> **À retenir** : un bon pipeline est une suite de petites fonctions pures, testées, qu'on peut relancer sans risque.
''',
"exercises": [
 {"id": "e-etl-a", "title": "Une étape de validation",
  "prompt": "Écris `valider(df)` qui vérifie qu'un DataFrame de livres : contient les colonnes `id`, `titre` et `note` ; n'a aucun `id` en double ; a des notes entre 0 et 5. Elle lève une `ValueError` avec un message explicite si une règle est violée, et renvoie `df` sinon.",
  "starter": 'import pandas as pd\n\ndef valider(df):\n    pass\n',
  "solution": 'import pandas as pd\n\ndef valider(df):\n    manquantes = {"id", "titre", "note"} - set(df.columns)\n    if manquantes:\n        raise ValueError(f"Colonnes manquantes : {manquantes}")\n    if df["id"].duplicated().any():\n        raise ValueError("Des id sont en double")\n    if not df["note"].between(0, 5).all():\n        raise ValueError("Des notes sont hors de [0, 5]")\n    return df\n\nok = pd.DataFrame({"id": [1, 2], "titre": ["a", "b"], "note": [4.2, 3.0]})\nvalider(ok)\n',
  "hint": "Utilise une différence d'ensembles pour les colonnes, .duplicated().any() pour les doublons et .between(0, 5).all() pour les notes.",
  "check": 'import pandas as pd\nok = pd.DataFrame({"id": [1, 2], "titre": ["a", "b"], "note": [4.2, 3.0]})\nassert valider(ok) is ok, "valider doit renvoyer le DataFrame quand tout va bien."\nfor mauvais in [ok.drop(columns="note"), pd.DataFrame({"id": [1, 1], "titre": ["a", "b"], "note": [1, 2]}), pd.DataFrame({"id": [1, 2], "titre": ["a", "b"], "note": [4, 7]})]:\n    try:\n        valider(mauvais)\n        assert False, "valider devrait lever une ValueError pour un DataFrame invalide."\n    except ValueError:\n        pass\n'},
]},
# ---------------------------------------------------------------- Cloud
{"id": "l-cloud", "title": "Le cloud et AWS : les bases", "minutes": 60,
"body": r'''
Le module Infrastructure de données du FullStack se déroule sur **AWS** et prépare la certification **AWS Cloud Practitioner (CLF-C02)**, avec cinq examens blancs. Cette leçon te donne le vocabulaire pour arriver à l'aise. Fais les manipulations sur ton ordinateur.

## Pourquoi le cloud

Au lieu d'acheter des serveurs, on loue de la puissance de calcul et du stockage à la demande, facturés à l'usage. Trois modèles :
- **IaaS** (*Infrastructure as a Service*) : tu loues des machines virtuelles et tu gères tout le reste (EC2).
- **PaaS** (*Platform as a Service*) : tu déploies ton code, la plateforme gère les serveurs (Elastic Beanstalk, Heroku).
- **SaaS** (*Software as a Service*) : tu utilises un logiciel prêt à l'emploi (Gmail, Notion).

## Les services AWS à connaître pour la formation

| Service | Rôle | Analogie |
| --- | --- | --- |
| **S3** | Stockage d'objets (fichiers) dans des *buckets* | Un disque dur infini en ligne |
| **EC2** | Machines virtuelles | Un ordinateur loué à l'heure |
| **RDS** | Bases de données relationnelles gérées (PostgreSQL…) | Une base SQL sans administration |
| **IAM** | Utilisateurs, rôles et permissions | Le service des badges d'accès |
| **Lambda** | Fonctions exécutées à la demande, sans serveur | Un script qui se réveille sur un événement |
| **SageMaker** | Entraînement et déploiement de modèles de ML | Un atelier de ML géré |
| **Bedrock** | Accès à des modèles de langage via une API | Un catalogue de LLM |

## Les notions qui tombent à l'examen

- **Régions** (par exemple eu-west-3 = Paris) et **zones de disponibilité** (des centres de données isolés dans une région) : on répartit sur plusieurs zones pour résister à une panne.
- Le **modèle de responsabilité partagée** : AWS sécurise *le* cloud (matériel, réseau, bâtiments) ; toi, tu sécurises ce que tu mets *dans* le cloud (données, accès, configuration).
- Le **principe du moindre privilège** : chaque utilisateur ou programme reçoit uniquement les droits dont il a besoin.
- La **tarification** : à l'usage (*on-demand*), réservée (engagement de 1 ou 3 ans, moins cher), ou *spot* (capacité inutilisée, jusqu'à 90 % moins cher mais interruptible).

## Manipuler S3 avec boto3

`boto3` est le SDK Python d'AWS. Ce code se lance sur ton ordinateur, une fois tes identifiants configurés avec `aws configure`.

```pycode
import boto3

s3 = boto3.client("s3", region_name="eu-west-3")
s3.create_bucket(Bucket="mon-lac-de-donnees-2026",
                 CreateBucketConfiguration={"LocationConstraint": "eu-west-3"})
s3.upload_file("titanic.csv", "mon-lac-de-donnees-2026", "raw/titanic.csv")

for obj in s3.list_objects_v2(Bucket="mon-lac-de-donnees-2026", Prefix="raw/")["Contents"]:
    print(obj["Key"], obj["Size"])

s3.download_file("mon-lac-de-donnees-2026", "raw/titanic.csv", "copie.csv")
```

Un **lac de données** (*data lake*) range les fichiers par zones : `raw/` (brut), `clean/` (nettoyé), `curated/` (prêt à l'analyse).

> **À retenir** : active la facturation par alertes (AWS Budgets) dès la création du compte, n'utilise jamais le compte racine au quotidien, et active l'authentification à deux facteurs. Une clé AWS publiée sur GitHub est exploitée en quelques minutes.
''',
"tasks": [
  "Créer un compte AWS (offre gratuite) et activer l'authentification à deux facteurs sur le compte racine",
  "Créer une alerte de budget à 5 € dans AWS Budgets",
  "Créer un utilisateur IAM pour tes travaux, sans utiliser le compte racine",
  "Installer AWS CLI et lancer aws configure avec cet utilisateur",
  "Créer un bucket S3 et y envoyer titanic.csv avec boto3",
  "Faire le parcours gratuit « AWS Cloud Practitioner Essentials » sur AWS Skill Builder",
],
"exercises": []},
]

PROJECTS = [
{"id": "p-infra", "title": "Projet · Un mini-entrepôt de données Brewly", "minutes": 120,
"body": r'''
Objectif : construire, en Python et SQL, un petit **entrepôt de données analytique** à partir de la base transactionnelle Brewly, comme dans les projets « Base de données Brewly vers AWS RDS PostgreSQL » et « Pipeline ETL PeopleFirst ».

Tu vas créer une **table de faits** (une ligne par ligne de commande, avec le montant) et produire les indicateurs qu'un directeur commercial regarde chaque lundi.
''',
"exercises": [
 {"id": "e-pinfra-a", "title": "La table de faits",
  "prompt": "Avec une seule requête SQL, crée le DataFrame `faits` : une ligne par ligne de commande, avec les colonnes `commande_id`, `date`, `mois` (format `AAAA-MM`), `magasin`, `ville_client`, `produit`, `categorie`, `quantite` et `montant` (quantité × prix).",
  "starter": 'import pandas as pd\nfrom brewly import connecter\ncon = connecter()\n',
  "solution": 'import pandas as pd\nfrom brewly import connecter\ncon = connecter()\n\nfaits = pd.read_sql_query("""\nSELECT l.commande_id, c.date, SUBSTR(c.date, 1, 7) AS mois, c.magasin,\n       cl.ville AS ville_client, p.nom AS produit, p.categorie,\n       l.quantite, l.quantite * p.prix AS montant\nFROM lignes l\nJOIN commandes c ON c.id = l.commande_id\nJOIN clients cl ON cl.id = c.client_id\nJOIN produits p ON p.id = l.produit_id\n""", con)\nfaits.head()\n',
  "hint": "Quatre tables, trois JOIN. SUBSTR(c.date, 1, 7) pour le mois.",
  "check": 'n = pd.read_sql_query("SELECT COUNT(*) AS n FROM lignes", con)["n"][0]\nattendues = ["commande_id", "date", "mois", "magasin", "ville_client", "produit", "categorie", "quantite", "montant"]\nassert list(faits.columns) == attendues, f"Colonnes : {list(faits.columns)}."\nassert len(faits) == n, f"faits a {len(faits)} lignes, il en faut {n} (une par ligne de commande)."\nassert faits["mois"].str.match(r"^\\d{4}-\\d{2}$").all(), "mois doit être au format AAAA-MM."\n'},
 {"id": "e-pinfra-b", "title": "Le tableau de bord du lundi",
  "prompt": "À partir de `faits` (recrée-le), calcule avec pandas : `ca_mensuel` (Series du chiffre d'affaires par mois, arrondi à 2 décimales, triée par mois), `croissance` (variation en % de mars à avril, arrondie à 1 décimale) et `top_categorie` (la catégorie qui rapporte le plus).",
  "starter": 'import pandas as pd\nfrom brewly import connecter\ncon = connecter()\nfaits = pd.read_sql_query("""\nSELECT l.commande_id, c.date, SUBSTR(c.date, 1, 7) AS mois, c.magasin,\n       cl.ville AS ville_client, p.nom AS produit, p.categorie,\n       l.quantite, l.quantite * p.prix AS montant\nFROM lignes l\nJOIN commandes c ON c.id = l.commande_id\nJOIN clients cl ON cl.id = c.client_id\nJOIN produits p ON p.id = l.produit_id\n""", con)\n',
  "solution": 'import pandas as pd\nfrom brewly import connecter\ncon = connecter()\nfaits = pd.read_sql_query("""\nSELECT l.commande_id, c.date, SUBSTR(c.date, 1, 7) AS mois, c.magasin,\n       cl.ville AS ville_client, p.nom AS produit, p.categorie,\n       l.quantite, l.quantite * p.prix AS montant\nFROM lignes l\nJOIN commandes c ON c.id = l.commande_id\nJOIN clients cl ON cl.id = c.client_id\nJOIN produits p ON p.id = l.produit_id\n""", con)\n\nca_mensuel = faits.groupby("mois")["montant"].sum().round(2).sort_index()\ncroissance = round((ca_mensuel["2026-04"] / ca_mensuel["2026-03"] - 1) * 100, 1)\ntop_categorie = faits.groupby("categorie")["montant"].sum().idxmax()\nprint(ca_mensuel, croissance, top_categorie)\n',
  "hint": "groupby(\"mois\")[\"montant\"].sum(). La croissance vaut (avril / mars − 1) × 100.",
  "check": 'ref = faits.groupby("mois")["montant"].sum()\nassert list(ca_mensuel.index) == sorted(ref.index), "ca_mensuel doit être indexé par mois, dans l\'ordre."\nassert abs(ca_mensuel.sum() - ref.sum()) < 0.1, "Les montants mensuels ne correspondent pas."\nexp = round((ref["2026-04"] / ref["2026-03"] - 1) * 100, 1)\nassert abs(croissance - exp) < 0.11, f"croissance vaut {croissance}, j\'attendais {exp}."\nassert top_categorie == faits.groupby("categorie")["montant"].sum().idxmax(), f"top_categorie vaut {top_categorie!r}."\n'},
],
"tasks": [
  "Installer PostgreSQL en local (ou avec Docker) et y charger les tables Brewly avec pandas.to_sql",
  "Refaire les requêtes du projet dans PostgreSQL (remplace SUBSTR par TO_CHAR(date, 'YYYY-MM'))",
  "Bonus : créer une base RDS PostgreSQL sur l'offre gratuite AWS et y charger les données",
  "Publier le pipeline sur GitHub avec un README",
]},
]

QUIZZES = {
"quiz-infra": {"title": "Quiz · API, SQL et ETL", "questions": [
 {"q": "Une API répond 429. Que fais-tu ?", "options": ["Tu corriges l'URL", "Tu attends puis tu réessaies, idéalement avec une attente croissante", "Tu changes de clé d'API", "Tu abandonnes"], "answer": 1,
  "explain": "429 = trop de requêtes. On ralentit et on réessaie (backoff exponentiel, en respectant Retry-After)."},
 {"q": "Quelle méthode HTTP utilise-t-on pour lire une ressource ?", "options": ["POST", "GET", "PUT", "DELETE"], "answer": 1,
  "explain": "GET lit, POST crée ou envoie, PUT/PATCH modifie, DELETE supprime."},
 {"q": "Quelle différence entre WHERE et HAVING ?", "options": ["Aucune", "WHERE filtre les lignes avant le regroupement, HAVING filtre les groupes après", "HAVING est plus rapide", "WHERE ne marche qu'avec des nombres"], "answer": 1,
  "explain": "Un filtre sur un agrégat (COUNT, SUM…) doit aller dans HAVING."},
 {"q": "Pour trouver les clients qui n'ont jamais commandé, on utilise :", "options": ["INNER JOIN", "LEFT JOIN puis WHERE commande IS NULL", "GROUP BY seul", "ORDER BY"], "answer": 1,
  "explain": "LEFT JOIN garde tous les clients ; ceux sans correspondance ont des colonnes NULL côté commandes."},
 {"q": "Que signifie qu'un pipeline ETL est idempotent ?", "options": ["Il est très rapide", "Le relancer donne le même résultat, sans doublons", "Il ne fait qu'une étape", "Il fonctionne sans base de données"], "answer": 1,
  "explain": "Un pipeline idempotent peut être relancé sans risque après une panne : indispensable en production."},
 {"q": "Que fait pd.json_normalize ?", "options": ["Il valide un JSON", "Il aplatit des JSON imbriqués en colonnes", "Il compresse un fichier", "Il trie les clés"], "answer": 1,
  "explain": "Les champs imbriqués deviennent des colonnes comme note.moyenne."},
 {"q": "Où stocker une clé d'API dans un projet ?", "options": ["Dans le code", "Dans une variable d'environnement (fichier .env ignoré par Git)", "Dans le README", "Dans le nom du fichier"], "answer": 1,
  "explain": "Le code lit os.environ ; la clé n'est jamais publiée."},
 {"q": "Une CTE (WITH ... AS) sert à :", "options": ["Créer une table permanente", "Nommer un résultat intermédiaire pour rendre la requête lisible", "Supprimer des doublons", "Indexer une colonne"], "answer": 1,
  "explain": "Une CTE découpe une requête complexe en étapes nommées."},
]},
"quiz-clf": {"title": "Quiz · Préparation AWS Cloud Practitioner", "questions": [
 {"q": "Selon le modèle de responsabilité partagée, qui est responsable de la configuration des permissions IAM de ton compte ?", "options": ["AWS", "Toi, le client", "Les deux à parts égales", "Personne"], "answer": 1,
  "explain": "AWS sécurise le cloud lui-même ; le client sécurise ce qu'il y met, dont les accès et permissions."},
 {"q": "Quel service AWS stocke des fichiers sous forme d'objets dans des buckets ?", "options": ["EC2", "S3", "RDS", "Lambda"], "answer": 1,
  "explain": "S3 (Simple Storage Service) est le stockage d'objets d'AWS, base des lacs de données."},
 {"q": "Une zone de disponibilité, c'est :", "options": ["Un pays", "Un ou plusieurs centres de données isolés au sein d'une région", "Un compte AWS", "Une période de facturation"], "answer": 1,
  "explain": "Chaque région contient plusieurs zones de disponibilité ; répartir sur plusieurs zones assure la haute disponibilité."},
 {"q": "Quel mode de tarification EC2 est le moins cher mais peut être interrompu ?", "options": ["À la demande", "Instances réservées", "Instances spot", "Hôtes dédiés"], "answer": 2,
  "explain": "Les instances spot utilisent la capacité inutilisée, avec de fortes remises, mais AWS peut les reprendre."},
 {"q": "Le principe du moindre privilège signifie :", "options": ["Donner les droits administrateur à tous pour aller vite", "Accorder uniquement les permissions nécessaires", "Supprimer les utilisateurs inactifs", "Utiliser le compte racine"], "answer": 1,
  "explain": "Chaque identité reçoit seulement les droits dont elle a besoin, ce qui limite les dégâts en cas de compromission."},
 {"q": "Quel service exécute du code sans gérer de serveur, en réponse à des événements ?", "options": ["EC2", "Lambda", "S3", "CloudFront"], "answer": 1,
  "explain": "AWS Lambda est le service serverless : on paie à l'exécution."},
 {"q": "Quel service fournit une base PostgreSQL gérée ?", "options": ["DynamoDB", "RDS", "Redshift", "S3"], "answer": 1,
  "explain": "RDS gère des bases relationnelles (PostgreSQL, MySQL…). DynamoDB est NoSQL, Redshift un entrepôt analytique."},
 {"q": "Quel outil permet d'être alerté quand les dépenses dépassent un seuil ?", "options": ["AWS Budgets", "IAM", "CloudTrail", "Route 53"], "answer": 0,
  "explain": "AWS Budgets envoie des alertes selon des seuils de coût ou d'usage. À configurer dès le premier jour."},
 {"q": "Quel modèle de service correspond à louer des machines virtuelles que tu administres toi-même ?", "options": ["SaaS", "PaaS", "IaaS", "FaaS"], "answer": 2,
  "explain": "IaaS : tu gères le système, les logiciels et les données ; le fournisseur gère le matériel."},
 {"q": "Quel service enregistre les appels d'API faits sur ton compte, pour l'audit ?", "options": ["CloudTrail", "CloudWatch", "Config", "Inspector"], "answer": 0,
  "explain": "CloudTrail journalise qui a fait quoi et quand ; CloudWatch surveille les métriques et les journaux applicatifs."},
]},
}
