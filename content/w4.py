WEEK = {
"id": "s4", "num": 4,
"title": "Premiers modèles et IA générative",
"goal": "Entraîner et évaluer tes premiers modèles avec scikit-learn, comprendre le principe d'un système RAG, et arriver avec un projet visible sur GitHub.",
"hours": "8 à 10 h",
"lessons": [
# ---------------------------------------------------------------- 4.1
{"id": "l-4-1", "title": "Le vocabulaire du machine learning", "minutes": 50,
"body": r'''
Le **machine learning** consiste à faire apprendre à un programme une règle à partir d'exemples, au lieu de l'écrire à la main.

## Les grandes familles

- **Apprentissage supervisé** : on dispose d'exemples avec la bonne réponse (la **cible**, ou *target*, notée y).
  - **Régression** : la cible est un nombre (un prix, une masse, une durée).
  - **Classification** : la cible est une catégorie (spam / non spam, espèce, survie).
- **Apprentissage non supervisé** : pas de cible. On cherche une structure : des groupes (*clustering*), une réduction de dimensions.
- L'**IA générative** produit du contenu (texte, images, code). Les grands modèles de langage sont entraînés de façon auto-supervisée : prédire le mot suivant.

## Features et cible

Les **features** (caractéristiques, notées X) sont les colonnes qui servent à prédire. La **cible** y est la colonne à prédire.

```python
import pandas as pd
df = pd.read_csv("penguins.csv").dropna()
X = df[["bill_length_mm", "bill_depth_mm", "flipper_length_mm"]]   # matrice : majuscule
y = df["species"]                                                   # vecteur : minuscule
print(X.shape, y.shape)
```

## Séparer entraînement et test

```viz split
```

Un modèle doit être évalué sur des données qu'il **n'a jamais vues**, sinon on mesure sa mémoire et non sa capacité à généraliser.

```python
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)
print(len(X_train), "exemples d'entraînement,", len(X_test), "de test")
```

`random_state` rend le découpage reproductible. `stratify=y` garde les mêmes proportions de classes dans les deux parties.

## Sous-apprentissage et surapprentissage

```viz overfit
```

- **Sous-apprentissage** (*underfitting*) : le modèle est trop simple. Il se trompe autant à l'entraînement qu'au test.
- **Surapprentissage** (*overfitting*) : le modèle a appris par cœur les données d'entraînement, bruit compris. Excellent à l'entraînement, mauvais au test.
- Le bon modèle se situe entre les deux : c'est le **compromis biais-variance**.

## Toujours une baseline

Avant tout modèle, calcule le score d'une stratégie naïve : prédire la classe majoritaire, ou la moyenne. Un modèle qui ne fait pas mieux ne sert à rien.

```python
print(y_train.value_counts(normalize=True).round(3))
```

> **À retenir** : features X, cible y, séparation train/test, baseline. Ces quatre réflexes s'appliquent à tous les projets, y compris en deep learning.
''',
"exercises": [
 {"id": "e-4-1-a", "title": "Préparer X et y",
  "prompt": "Avec `tips.csv`, on veut prédire le pourboire. Crée `X` (colonnes `total_bill` et `size`) et `y` (colonne `tip`), puis sépare-les avec `train_test_split` (25 % de test, `random_state=0`) en `X_train, X_test, y_train, y_test`.",
  "starter": 'import pandas as pd\nfrom sklearn.model_selection import train_test_split\ntips = pd.read_csv("tips.csv")\n',
  "solution": 'import pandas as pd\nfrom sklearn.model_selection import train_test_split\ntips = pd.read_csv("tips.csv")\nX = tips[["total_bill", "size"]]\ny = tips["tip"]\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)\nprint(X_train.shape, X_test.shape)\n',
  "hint": "X avec des doubles crochets, y avec des simples. train_test_split(X, y, test_size=0.25, random_state=0).",
  "check": 'assert list(X.columns) == ["total_bill", "size"], f"Colonnes de X : {list(X.columns)}."\nassert X_train.shape == (183, 2) and X_test.shape == (61, 2), f"Formes : {X_train.shape} et {X_test.shape}, j\'attendais (183, 2) et (61, 2)."\nassert len(y_train) == 183, "y_train doit avoir 183 valeurs."\n'},
 {"id": "e-4-1-b", "title": "Le score à battre",
  "prompt": "Sur le Titanic, calcule `baseline` : l'exactitude (*accuracy*) obtenue en prédisant **toujours** la classe la plus fréquente de `survived`. Exprime-la entre 0 et 1.",
  "starter": 'import pandas as pd\nt = pd.read_csv("titanic.csv")\n',
  "solution": 'import pandas as pd\nt = pd.read_csv("titanic.csv")\nbaseline = t["survived"].value_counts(normalize=True).max()\nprint(f"Baseline : {baseline:.1%}")\n',
  "hint": "value_counts(normalize=True) donne les proportions ; la plus grande est l'exactitude de la stratégie « toujours la classe majoritaire ».",
  "check": 'assert abs(baseline - 0.6162) < 0.001, f"baseline vaut {baseline}, j\'attendais environ 0.616."\n'},
]},
# ---------------------------------------------------------------- 4.2
{"id": "l-4-2", "title": "Régression avec scikit-learn", "minutes": 70,
"body": r'''
**scikit-learn** propose des dizaines de modèles avec la même interface : on crée le modèle, on appelle `fit` sur les données d'entraînement, puis `predict`. Tu as codé cette interface toi-même en semaine 3.

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

df = pd.read_csv("penguins.csv").dropna()
X = df[["flipper_length_mm", "bill_length_mm", "bill_depth_mm"]]
y = df["body_mass_g"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

modele = LinearRegression()
modele.fit(X_train, y_train)
print("coefficients :", modele.coef_.round(2))
print("biais :", round(modele.intercept_, 1))
```

Chaque coefficient indique de combien de grammes la masse prédite augmente quand la variable augmente d'une unité, les autres restant fixes.

## Évaluer une régression

- **MAE** (erreur absolue moyenne) : l'erreur moyenne, dans l'unité de la cible. Facile à expliquer.
- **RMSE** (racine de l'erreur quadratique moyenne) : pénalise davantage les grosses erreurs.
- **R²** : la part de la variance expliquée par le modèle. 1 = parfait, 0 = pas mieux que prédire la moyenne.

```python
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

pred = modele.predict(X_test)
print(f"MAE  : {mean_absolute_error(y_test, pred):.0f} g")
print(f"RMSE : {np.sqrt(mean_squared_error(y_test, pred)):.0f} g")
print(f"R²   : {r2_score(y_test, pred):.3f}")
```

Compare toujours à la baseline :

```python
baseline = np.full(len(y_test), y_train.mean())
print(f"RMSE baseline : {np.sqrt(mean_squared_error(y_test, baseline)):.0f} g")
```

## Visualiser les erreurs

```python
import plotly.express as px
resultats = pd.DataFrame({"réel": y_test, "prédit": pred})
px.scatter(resultats, x="réel", y="prédit", title="Prédictions contre valeurs réelles (g)")
```

Plus les points sont proches de la diagonale, meilleur est le modèle.

> **À retenir** : on ne calcule les métriques que sur le jeu de **test**. Un score mesuré sur les données d'entraînement est toujours trop optimiste.
''',
"exercises": [
 {"id": "e-4-2-a", "title": "Prédire le pourboire",
  "prompt": "Entraîne une `LinearRegression` nommée `modele` qui prédit `tip` à partir de `total_bill` et `size` (split 25 %, `random_state=0`). Calcule `mae` sur le jeu de test et `mae_baseline`, la MAE obtenue en prédisant toujours la moyenne de `y_train`.",
  "starter": 'import numpy as np\nimport pandas as pd\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.linear_model import LinearRegression\nfrom sklearn.metrics import mean_absolute_error\n\ntips = pd.read_csv("tips.csv")\nX = tips[["total_bill", "size"]]\ny = tips["tip"]\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)\n',
  "solution": 'import numpy as np\nimport pandas as pd\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.linear_model import LinearRegression\nfrom sklearn.metrics import mean_absolute_error\n\ntips = pd.read_csv("tips.csv")\nX = tips[["total_bill", "size"]]\ny = tips["tip"]\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)\n\nmodele = LinearRegression().fit(X_train, y_train)\nmae = mean_absolute_error(y_test, modele.predict(X_test))\nmae_baseline = mean_absolute_error(y_test, np.full(len(y_test), y_train.mean()))\nprint(f"MAE modèle : {mae:.3f} $  |  MAE baseline : {mae_baseline:.3f} $")\n',
  "hint": "modele = LinearRegression().fit(X_train, y_train), puis mean_absolute_error(y_test, modele.predict(X_test)).",
  "check": 'from sklearn.linear_model import LinearRegression\nassert isinstance(modele, LinearRegression), "modele doit être une LinearRegression."\nassert hasattr(modele, "coef_"), "Le modèle n\'est pas entraîné : appelle fit."\nassert mae < mae_baseline, "Ton modèle devrait battre la baseline."\nassert abs(mae - 0.6889) < 0.01, f"mae vaut {mae:.4f}, j\'attendais environ 0.689."\n'},
]},
# ---------------------------------------------------------------- 4.3
{"id": "l-4-3", "title": "Classification et métriques", "minutes": 80,
"body": r'''
La **régression logistique** est le modèle de classification de base. Malgré son nom, elle classe : elle calcule une combinaison linéaire des features, puis la transforme en probabilité entre 0 et 1 grâce à la fonction **sigmoïde**.

```latex
P(y = 1 \mid x) = \sigma(w \cdot x + b) = \frac{1}{1 + e^{-(w \cdot x + b)}}
```

## Préparer les données

Les modèles ne comprennent que des nombres. Il faut **encoder** les catégories et **imputer** les valeurs manquantes.

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

t = pd.read_csv("titanic.csv")
t["femme"] = (t["sex"] == "female").astype(int)          # encodage binaire
t["age"] = t["age"].fillna(t["age"].median())
features = ["pclass", "femme", "age", "fare", "sibsp", "parch"]
X, y = t[features], t["survived"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

clf = LogisticRegression(max_iter=1000).fit(X_train, y_train)
pred = clf.predict(X_test)
proba = clf.predict_proba(X_test)[:, 1]       # probabilité de survie
print(pred[:5], proba[:5].round(2))
```

Pour une variable à plusieurs catégories (comme `embarked`), on utilise le **one-hot encoding** : `pd.get_dummies(t["embarked"])` crée une colonne 0/1 par catégorie.

## La matrice de confusion

```python
from sklearn.metrics import confusion_matrix
pd.DataFrame(confusion_matrix(y_test, pred),
             index=["réel : décédé", "réel : survivant"],
             columns=["prédit : décédé", "prédit : survivant"])
```

- **Vrais positifs (VP)** : survivants prédits survivants. **Faux positifs (FP)** : décédés prédits survivants.
- **Vrais négatifs (VN)** et **faux négatifs (FN)** : de même pour l'autre classe.

## Les métriques

```latex
\text{précision} = \frac{VP}{VP + FP} \qquad \text{rappel} = \frac{VP}{VP + FN} \qquad F_1 = 2 \cdot \frac{\text{précision} \cdot \text{rappel}}{\text{précision} + \text{rappel}}
```

- **Exactitude** (*accuracy*) : la part de bonnes réponses. Trompeuse si les classes sont déséquilibrées.
- **Précision** : parmi les prédits positifs, combien le sont vraiment ? Importante quand un faux positif coûte cher (un mail légitime classé spam).
- **Rappel** (*recall*) : parmi les vrais positifs, combien en a-t-on trouvé ? Important quand un faux négatif coûte cher (une fraude ou une maladie non détectée).

```python
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
print(f"exactitude {accuracy_score(y_test, pred):.3f}  précision {precision_score(y_test, pred):.3f}  "
      f"rappel {recall_score(y_test, pred):.3f}  F1 {f1_score(y_test, pred):.3f}")
```

> **À retenir** : choisis ta métrique en fonction du **coût des erreurs** dans le problème métier, et dis-le explicitement dans tes projets.
''',
"exercises": [
 {"id": "e-4-3-a", "title": "Ajouter le port d'embarquement",
  "prompt": "Améliore le modèle de la leçon : ajoute un encodage one-hot de `embarked` (après avoir remplacé les valeurs manquantes par `\"S\"`). Construis `X` avec les features de base plus ces colonnes, entraîne `clf` (même split que la leçon) et calcule `acc`, l'exactitude sur le test. Elle doit dépasser 0.78.",
  "starter": 'import pandas as pd\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.metrics import accuracy_score\n\nt = pd.read_csv("titanic.csv")\nt["femme"] = (t["sex"] == "female").astype(int)\nt["age"] = t["age"].fillna(t["age"].median())\nbase = ["pclass", "femme", "age", "fare", "sibsp", "parch"]\n',
  "solution": 'import pandas as pd\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.metrics import accuracy_score\n\nt = pd.read_csv("titanic.csv")\nt["femme"] = (t["sex"] == "female").astype(int)\nt["age"] = t["age"].fillna(t["age"].median())\nbase = ["pclass", "femme", "age", "fare", "sibsp", "parch"]\n\nports = pd.get_dummies(t["embarked"].fillna("S"), prefix="port", dtype=int)\nX = pd.concat([t[base], ports], axis=1)\ny = t["survived"]\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)\nclf = LogisticRegression(max_iter=1000).fit(X_train, y_train)\nacc = accuracy_score(y_test, clf.predict(X_test))\nprint(X.columns.tolist(), round(acc, 3))\n',
  "hint": "pd.get_dummies(t[\"embarked\"].fillna(\"S\"), prefix=\"port\", dtype=int), puis pd.concat([t[base], ports], axis=1).",
  "check": 'assert X.shape[1] == 9, f"X a {X.shape[1]} colonnes, j\'en attendais 9 (6 de base + 3 ports)."\nassert X.isna().sum().sum() == 0, "X contient encore des valeurs manquantes."\nassert acc > 0.78, f"acc vaut {acc:.3f}, vise plus de 0.78."\n'},
 {"id": "e-4-3-b", "title": "Précision et rappel à la main",
  "prompt": "À partir de la matrice de confusion ci-dessous (lignes = réel, colonnes = prédit, ordre [négatif, positif]), calcule `precision`, `rappel` et `f1` **sans scikit-learn**.",
  "starter": "import numpy as np\ncm = np.array([[95, 15],\n               [20, 49]])\n",
  "solution": "import numpy as np\ncm = np.array([[95, 15],\n               [20, 49]])\nvn, fp, fn, vp = cm.ravel()\nprecision = vp / (vp + fp)\nrappel = vp / (vp + fn)\nf1 = 2 * precision * rappel / (precision + rappel)\nprint(round(precision, 3), round(rappel, 3), round(f1, 3))\n",
  "hint": "cm.ravel() donne [VN, FP, FN, VP]. Applique ensuite les formules.",
  "check": 'assert abs(precision - 49 / 64) < 1e-9, f"precision vaut {precision}, j\'attendais 49/64 ≈ 0.766."\nassert abs(rappel - 49 / 69) < 1e-9, f"rappel vaut {rappel}, j\'attendais 49/69 ≈ 0.710."\nassert abs(f1 - 0.7368) < 1e-3, f"f1 vaut {f1}."\n'},
]},
# ---------------------------------------------------------------- 4.4
{"id": "l-4-4", "title": "Surapprentissage et validation croisée", "minutes": 60,
"body": r'''
Un **arbre de décision** pose une suite de questions (« sexe = femme ? », « classe ≤ 2 ? ») pour classer. Plus il est profond, plus il peut coller aux données d'entraînement, jusqu'à les apprendre par cœur.

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

t = pd.read_csv("titanic.csv")
t["femme"] = (t["sex"] == "female").astype(int)
t["age"] = t["age"].fillna(t["age"].median())
X = t[["pclass", "femme", "age", "fare", "sibsp", "parch"]]
y = t["survived"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

lignes = []
for profondeur in [1, 2, 3, 5, 8, 12, None]:
    arbre = DecisionTreeClassifier(max_depth=profondeur, random_state=0).fit(X_train, y_train)
    lignes.append({"profondeur": str(profondeur), "train": arbre.score(X_train, y_train),
                   "test": arbre.score(X_test, y_test)})
pd.DataFrame(lignes).round(3)
```

Sans limite de profondeur, l'arbre atteint presque 100 % sur l'entraînement mais pas sur le test : c'est le **surapprentissage**. L'écart entre les deux scores est le signal d'alarme.

## La validation croisée

Un seul découpage train/test dépend du hasard. La **validation croisée à k plis** (*k-fold*) découpe les données en k parts, entraîne k fois en gardant à chaque fois une part différente pour l'évaluation, puis fait la moyenne.

```python
from sklearn.model_selection import cross_val_score
scores = cross_val_score(DecisionTreeClassifier(max_depth=3, random_state=0), X, y, cv=5)
print(scores.round(3), "→ moyenne", scores.mean().round(3), "± écart-type", scores.std().round(3))
```

## Choisir un hyperparamètre

`max_depth` est un **hyperparamètre** : on le fixe avant l'entraînement, il n'est pas appris. On le choisit par validation croisée, **jamais** sur le jeu de test, qui doit rester intact jusqu'à l'évaluation finale.

> **À retenir** : le jeu de test est comme l'examen final. Si tu t'en sers pour régler ton modèle, ton score final n'est plus fiable.
''',
"exercises": [
 {"id": "e-4-4-a", "title": "Trouver la meilleure profondeur",
  "prompt": "Pour chaque `max_depth` de 1 à 10, calcule le score moyen en validation croisée (`cv=5`, `random_state=0` pour l'arbre) sur `X, y`. Stocke les résultats dans le dictionnaire `scores_cv` `{profondeur: score moyen}`, puis `meilleure_profondeur`.",
  "starter": 'import pandas as pd\nfrom sklearn.tree import DecisionTreeClassifier\nfrom sklearn.model_selection import cross_val_score\n\nt = pd.read_csv("titanic.csv")\nt["femme"] = (t["sex"] == "female").astype(int)\nt["age"] = t["age"].fillna(t["age"].median())\nX = t[["pclass", "femme", "age", "fare", "sibsp", "parch"]]\ny = t["survived"]\n',
  "solution": 'import pandas as pd\nfrom sklearn.tree import DecisionTreeClassifier\nfrom sklearn.model_selection import cross_val_score\n\nt = pd.read_csv("titanic.csv")\nt["femme"] = (t["sex"] == "female").astype(int)\nt["age"] = t["age"].fillna(t["age"].median())\nX = t[["pclass", "femme", "age", "fare", "sibsp", "parch"]]\ny = t["survived"]\n\nscores_cv = {}\nfor d in range(1, 11):\n    arbre = DecisionTreeClassifier(max_depth=d, random_state=0)\n    scores_cv[d] = cross_val_score(arbre, X, y, cv=5).mean()\nmeilleure_profondeur = max(scores_cv, key=scores_cv.get)\nprint({d: round(s, 3) for d, s in scores_cv.items()}, meilleure_profondeur)\n',
  "hint": "Une boucle for d in range(1, 11), puis max(scores_cv, key=scores_cv.get).",
  "check": 'from sklearn.tree import DecisionTreeClassifier\nfrom sklearn.model_selection import cross_val_score\nref = {d: cross_val_score(DecisionTreeClassifier(max_depth=d, random_state=0), X, y, cv=5).mean() for d in range(1, 11)}\nassert set(scores_cv) == set(range(1, 11)), "scores_cv doit avoir les clés 1 à 10."\nassert meilleure_profondeur == max(ref, key=ref.get), f"meilleure_profondeur vaut {meilleure_profondeur}, j\'attendais {max(ref, key=ref.get)}."\n'},
]},
# ---------------------------------------------------------------- 4.5
{"id": "l-4-5", "title": "Découvrir l'IA générative et le RAG", "minutes": 60,
"body": r'''
Une grande partie de la formation porte sur l'**IA générative** : Transformers, RAG, agents. Voici les notions de base pour ne pas être perdu.

## Ce qu'est un grand modèle de langage

Un **LLM** (*Large Language Model*) est un réseau de neurones de type **Transformer**, entraîné à prédire le **token** suivant d'un texte. Un token est un morceau de mot : en moyenne, environ 4 caractères en anglais.

- Le **prompt** est le texte d'entrée. Le **prompt système** fixe le rôle et les règles du modèle.
- La **fenêtre de contexte** est la quantité maximale de tokens que le modèle peut lire en une fois.
- La **température** règle la part de hasard : basse pour des réponses stables, plus haute pour de la créativité.
- Un modèle peut **halluciner** : produire une réponse fausse mais crédible.

## Appeler un modèle depuis Python

Les fournisseurs proposent une API et un SDK Python. Le principe est toujours le même : une clé d'API, un modèle, une liste de messages. Ce code est à exécuter sur ton ordinateur, avec ta propre clé dans un fichier `.env`.

```pycode
# pip install anthropic python-dotenv
import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()                                   # lit ANTHROPIC_API_KEY dans .env
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

reponse = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=300,
    system="Tu es un tuteur de data science. Réponds en trois phrases maximum.",
    messages=[{"role": "user", "content": "Explique le surapprentissage à un débutant."}],
)
print(reponse.content[0].text)
```

Les SDK d'OpenAI, de Mistral ou de Google fonctionnent sur le même modèle.

## Le RAG : donner des documents au modèle

Un LLM ne connaît pas tes documents internes, et ses connaissances s'arrêtent à une date. Le **RAG** (*Retrieval-Augmented Generation*) résout ce problème en trois étapes :

1. **Indexer** : découper les documents en morceaux (*chunks*) et transformer chacun en vecteur (**embedding**), stocké dans une **base vectorielle**.
2. **Retrouver** : transformer la question en vecteur et chercher les morceaux les plus proches, par **similarité cosinus** (semaine 3).
3. **Générer** : envoyer au LLM la question accompagnée des morceaux retrouvés, avec la consigne de répondre à partir d'eux.

```viz rag
```

Voici l'étape 2 avec un embedding très simplifié : un vecteur de comptage de mots. Les vrais embeddings capturent le **sens**, mais le principe de recherche est identique.

```python
import numpy as np

documents = [
    "La descente de gradient minimise la fonction de perte en suivant le gradient.",
    "pandas permet de charger un fichier CSV dans un DataFrame.",
    "Le surapprentissage arrive quand le modèle apprend le bruit des données d'entraînement.",
]
vocab = sorted({m.strip(".,").lower() for d in documents for m in d.split()})

def vectoriser(texte):
    mots = [m.strip(".,?").lower() for m in texte.split()]
    return np.array([mots.count(v) for v in vocab], dtype=float)

def cosinus(u, v):
    n = np.linalg.norm(u) * np.linalg.norm(v)
    return 0.0 if n == 0 else u @ v / n

question = "Comment charger un CSV avec pandas ?"
q = vectoriser(question)
scores = [cosinus(q, vectoriser(d)) for d in documents]
print([round(s, 2) for s in scores])
print("Document retrouvé :", documents[int(np.argmax(scores))])
```

> **À retenir** : un agent IA est un LLM qui peut appeler des **outils** (une recherche, une base de données, du code) et enchaîner plusieurs étapes. Tu en construiras pendant la formation.
''',
"exercises": [
 {"id": "e-4-5-a", "title": "Construire le prompt d'un RAG",
  "prompt": "Écris `construire_prompt(question, documents, k=2)` qui retrouve les `k` documents les plus similaires à la question (fonctions `vectoriser` et `cosinus` fournies), puis renvoie un texte qui contient : la ligne `Contexte :`, les documents retenus (un par ligne, **du plus au moins similaire**), puis la ligne `Question : ` suivie de la question.",
  "starter": 'import numpy as np\n\ndocuments = [\n    "Le RAG combine une recherche de documents et un modèle de langage.",\n    "Une base vectorielle stocke des embeddings pour la recherche par similarité.",\n    "Les crêpes se préparent avec de la farine, des œufs et du lait.",\n    "Un embedding est un vecteur qui représente le sens d\'un texte.",\n]\nvocab = sorted({m.strip(".,").lower() for d in documents for m in d.split()})\n\ndef vectoriser(texte):\n    mots = [m.strip(".,?").lower() for m in texte.split()]\n    return np.array([mots.count(v) for v in vocab], dtype=float)\n\ndef cosinus(u, v):\n    n = np.linalg.norm(u) * np.linalg.norm(v)\n    return 0.0 if n == 0 else u @ v / n\n\ndef construire_prompt(question, documents, k=2):\n    pass\n\nprint(construire_prompt("Qu\'est-ce qu\'un embedding dans une base vectorielle ?", documents))\n',
  "solution": 'import numpy as np\n\ndocuments = [\n    "Le RAG combine une recherche de documents et un modèle de langage.",\n    "Une base vectorielle stocke des embeddings pour la recherche par similarité.",\n    "Les crêpes se préparent avec de la farine, des œufs et du lait.",\n    "Un embedding est un vecteur qui représente le sens d\'un texte.",\n]\nvocab = sorted({m.strip(".,").lower() for d in documents for m in d.split()})\n\ndef vectoriser(texte):\n    mots = [m.strip(".,?").lower() for m in texte.split()]\n    return np.array([mots.count(v) for v in vocab], dtype=float)\n\ndef cosinus(u, v):\n    n = np.linalg.norm(u) * np.linalg.norm(v)\n    return 0.0 if n == 0 else u @ v / n\n\ndef construire_prompt(question, documents, k=2):\n    q = vectoriser(question)\n    tries = sorted(documents, key=lambda d: cosinus(q, vectoriser(d)), reverse=True)\n    contexte = "\\n".join(tries[:k])\n    return f"Contexte :\\n{contexte}\\nQuestion : {question}"\n\nprint(construire_prompt("Qu\'est-ce qu\'un embedding dans une base vectorielle ?", documents))\n',
  "hint": "sorted(documents, key=lambda d: cosinus(q, vectoriser(d)), reverse=True)[:k], puis assemble le texte avec \"\\n\".join(...).",
  "check": 'p = construire_prompt("Qu\'est-ce qu\'un embedding dans une base vectorielle ?", documents)\nassert isinstance(p, str), "construire_prompt doit renvoyer un texte (as-tu oublié return ?)."\nassert p.startswith("Contexte :"), "Le prompt doit commencer par « Contexte : »."\nassert "Question : Qu\'est-ce qu\'un embedding" in p, "Le prompt doit se terminer par « Question : » suivi de la question."\nassert "crêpes" not in p, "Le document sur les crêpes ne devrait pas être retenu."\nassert p.index("Une base vectorielle") < p.index("Un embedding est"), "Les documents doivent être classés du plus au moins similaire."\nassert "Le RAG combine" in construire_prompt("le RAG combine recherche et modèle", documents, k=1), "Avec k=1, seul le meilleur document doit apparaître."\n'},
]},
# ---------------------------------------------------------------- 4.6
{"id": "l-4-6", "title": "L'anglais technique", "minutes": 40,
"body": r'''
Chez Jedha, les cours se font en français, mais **les supports, exercices et projets sont en anglais**, comme toute la documentation technique. Voici le vocabulaire qui revient tout le temps.

| Anglais | Français | Exemple d'usage |
| --- | --- | --- |
| feature | variable explicative | « Drop the leaking feature. » |
| target / label | cible / étiquette | « The target is imbalanced. » |
| training set / test set | jeu d'entraînement / de test | « Split into training and test sets. » |
| fit / predict | entraîner / prédire | « Fit the model on the training data. » |
| overfitting | surapprentissage | « The tree is overfitting. » |
| loss function | fonction de perte | « The loss keeps decreasing. » |
| learning rate | taux d'apprentissage | « Lower the learning rate. » |
| hyperparameter tuning | réglage des hyperparamètres | « Tune max_depth with cross-validation. » |
| missing values | valeurs manquantes | « Impute missing values with the median. » |
| outlier | valeur aberrante | « Remove outliers before fitting. » |
| accuracy / precision / recall | exactitude / précision / rappel | « Recall matters more for fraud detection. » |
| deploy / deployment | déployer / mise en production | « Deploy the model as an API. » |
| pipeline | chaîne de traitement | « Build a preprocessing pipeline. » |
| embedding | plongement (vecteur sémantique) | « Store the embeddings in a vector database. » |
| fine-tuning | ajustement fin d'un modèle | « Fine-tune a small model on your data. » |

## Lire une documentation efficacement

1. Commence par l'exemple de code (« Examples » ou « Quickstart »), pas par le texte.
2. Repère dans la liste des paramètres ceux qui ont une valeur par défaut : ce sont ceux que tu peux ignorer au début.
3. Regarde la section « Returns » : elle dit ce que tu récupères.
4. Lis les messages d'erreur en entier : la dernière ligne contient presque toujours la cause.

Entraîne-toi chaque jour : une page de la documentation de pandas ou de scikit-learn, et une vidéo technique en anglais.

> **À retenir** : en entreprise comme en formation, on écrit le code, les noms de variables, les commits et les README en anglais. Prends l'habitude dès maintenant pour tes projets GitHub.
''',
"tasks": [
  "Lire en anglais la page « Getting started » de scikit-learn",
  "Lire en anglais la page « 10 minutes to pandas »",
  "Regarder une vidéo StatQuest en anglais, sans sous-titres français",
  "Rédiger en anglais le README de ton projet de la semaine 4",
],
"exercises": []},
],
"project": {
"id": "p-4", "title": "Projet final · Classifier les espèces de manchots",
"body": r'''
Ton premier projet de portfolio complet : à partir des mesures d'un manchot, prédire son espèce (Adelie, Chinstrap ou Gentoo). Tu mobilises toute la mise à niveau : nettoyage, exploration, modèle, évaluation, et présentation.

Une **pipeline** scikit-learn enchaîne les étapes de préparation et le modèle en un seul objet. Elle évite les erreurs, en particulier les fuites de données : la standardisation n'apprend que sur le jeu d'entraînement.

```pycode
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

modele = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
modele.fit(X_train, y_train)
```

Modèle de README pour GitHub (à rédiger en anglais) :

```markdown
# Penguin species classifier
## Problem       What we predict and why it matters
## Data          Palmer Penguins: 344 rows, 7 columns, cleaning choices
## Approach      Features, model, train/test split
## Results       Accuracy, confusion matrix, baseline comparison
## How to run    pip install -r requirements.txt, then open the notebook
```
''',
"exercises": [
 {"id": "e-p4-a", "title": "Préparer les données",
  "prompt": "Charge `penguins.csv`, supprime les lignes incomplètes, et crée `X` avec les 4 mesures numériques plus une colonne `male` (1 si `sex == \"MALE\"`, sinon 0), et `y` = `species`. Sépare en train/test (20 %, `random_state=42`, stratifié).",
  "starter": 'import pandas as pd\nfrom sklearn.model_selection import train_test_split\n',
  "solution": 'import pandas as pd\nfrom sklearn.model_selection import train_test_split\n\ndf = pd.read_csv("penguins.csv").dropna()\ndf["male"] = (df["sex"] == "MALE").astype(int)\nX = df[["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g", "male"]]\ny = df["species"]\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)\nprint(X_train.shape, X_test.shape)\nprint(y_train.value_counts(normalize=True).round(2))\n',
  "hint": "dropna(), puis (df[\"sex\"] == \"MALE\").astype(int). N'oublie pas stratify=y.",
  "check": 'assert X.shape == (333, 5), f"X a la forme {X.shape}, j\'attendais (333, 5)."\nassert "male" in X.columns and set(X["male"].unique()) == {0, 1}, "La colonne male doit contenir des 0 et des 1."\nassert len(X_test) == 67, f"X_test a {len(X_test)} lignes, j\'en attendais 67."\n'},
 {"id": "e-p4-b", "title": "Entraîner et évaluer",
  "prompt": "Crée `modele`, une pipeline `StandardScaler` + `LogisticRegression(max_iter=1000)`, entraîne-la, calcule `acc` sur le test et `cm`, la matrice de confusion. Vise une exactitude d'au moins 0.97.",
  "starter": 'import pandas as pd\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.pipeline import make_pipeline\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.metrics import accuracy_score, confusion_matrix\n\ndf = pd.read_csv("penguins.csv").dropna()\ndf["male"] = (df["sex"] == "MALE").astype(int)\nX = df[["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g", "male"]]\ny = df["species"]\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)\n',
  "solution": 'import pandas as pd\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.pipeline import make_pipeline\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.metrics import accuracy_score, confusion_matrix\n\ndf = pd.read_csv("penguins.csv").dropna()\ndf["male"] = (df["sex"] == "MALE").astype(int)\nX = df[["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g", "male"]]\ny = df["species"]\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)\n\nmodele = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))\nmodele.fit(X_train, y_train)\npred = modele.predict(X_test)\nacc = accuracy_score(y_test, pred)\ncm = confusion_matrix(y_test, pred)\nprint(f"Exactitude : {acc:.3f}")\npd.DataFrame(cm, index=modele.classes_, columns=modele.classes_)\n',
  "hint": "make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)) s'utilise comme un modèle : fit puis predict.",
  "check": 'import numpy as np\nassert hasattr(modele, "predict") and hasattr(modele, "steps"), "modele doit être une pipeline (make_pipeline)."\nassert acc >= 0.97, f"acc vaut {acc:.3f}, vise au moins 0.97."\nassert np.asarray(cm).shape == (3, 3), "cm doit être une matrice 3 × 3 (une ligne et une colonne par espèce)."\n'},
 {"id": "e-p4-c", "title": "Prédire un nouveau manchot",
  "prompt": "Utilise ta pipeline (recopie le code nécessaire) pour prédire l'espèce d'un manchot mâle avec un bec de 50 mm de long et 15 mm d'épaisseur, une nageoire de 220 mm et une masse de 5 500 g. Stocke le nom de l'espèce dans `espece` et la probabilité associée dans `confiance`.",
  "starter": 'import pandas as pd\nfrom sklearn.pipeline import make_pipeline\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.linear_model import LogisticRegression\n\ndf = pd.read_csv("penguins.csv").dropna()\ndf["male"] = (df["sex"] == "MALE").astype(int)\ncols = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g", "male"]\nmodele = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)).fit(df[cols], df["species"])\n\nnouveau = pd.DataFrame([{\n    # à compléter\n}])\n',
  "solution": 'import pandas as pd\nfrom sklearn.pipeline import make_pipeline\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.linear_model import LogisticRegression\n\ndf = pd.read_csv("penguins.csv").dropna()\ndf["male"] = (df["sex"] == "MALE").astype(int)\ncols = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g", "male"]\nmodele = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)).fit(df[cols], df["species"])\n\nnouveau = pd.DataFrame([{\n    "bill_length_mm": 50, "bill_depth_mm": 15, "flipper_length_mm": 220,\n    "body_mass_g": 5500, "male": 1,\n}])\nespece = modele.predict(nouveau)[0]\nconfiance = modele.predict_proba(nouveau).max()\nprint(f"{espece} ({confiance:.1%})")\n',
  "hint": "Le DataFrame doit avoir exactement les mêmes colonnes que X. predict(...)[0] donne l'espèce, predict_proba(...).max() la probabilité.",
  "check": 'assert espece == "Gentoo", f"espece vaut {espece!r}."\nassert 0.9 < confiance <= 1, f"confiance vaut {confiance}, elle devrait être une probabilité élevée."\n'},
],
"tasks": [
  "Refaire le projet dans un notebook sur ton ordinateur",
  "Ajouter un graphique exploratoire (nageoire contre bec, coloré par espèce)",
  "Comparer avec un arbre de décision et expliquer ton choix",
  "Écrire le README en anglais à partir du modèle ci-dessus",
  "Publier sur GitHub et épingler le dépôt sur ton profil",
]},
"quiz": [
 {"q": "Prédire le prix d'un appartement est un problème de :", "options": ["Classification", "Régression", "Clustering", "Génération"], "answer": 1,
  "explain": "La cible est un nombre continu : c'est une régression."},
 {"q": "Pourquoi sépare-t-on les données en jeux d'entraînement et de test ?", "options": ["Pour aller plus vite", "Pour évaluer le modèle sur des données qu'il n'a jamais vues", "Parce que scikit-learn l'impose", "Pour avoir moins de données"], "answer": 1,
  "explain": "Le jeu de test mesure la capacité à généraliser, pas la mémoire du modèle."},
 {"q": "Un modèle obtient 99 % sur l'entraînement et 70 % sur le test. C'est :", "options": ["Du sous-apprentissage", "Du surapprentissage", "Un modèle parfait", "Une fuite de données certaine"], "answer": 1,
  "explain": "Un grand écart entre entraînement et test signale que le modèle a appris par cœur."},
 {"q": "Pour détecter une maladie grave, quelle métrique faut-il surveiller en priorité ?", "options": ["La précision", "Le rappel", "Le R²", "La MAE"], "answer": 1,
  "explain": "Un faux négatif (malade non détecté) coûte très cher : on veut un rappel élevé."},
 {"q": "Sur quelles données règle-t-on un hyperparamètre comme max_depth ?", "options": ["Sur le jeu de test", "Par validation croisée sur le jeu d'entraînement", "Au hasard", "Sur les données de production"], "answer": 1,
  "explain": "Le jeu de test doit rester intact jusqu'à l'évaluation finale, sinon le score est biaisé."},
 {"q": "Que fait l'étape « retrieval » d'un système RAG ?", "options": ["Elle entraîne le LLM", "Elle retrouve les morceaux de documents les plus proches de la question", "Elle traduit la réponse", "Elle supprime les hallucinations à coup sûr"], "answer": 1,
  "explain": "On compare l'embedding de la question à ceux des documents, généralement par similarité cosinus."},
 {"q": "Qu'est-ce qu'un token pour un LLM ?", "options": ["Une clé d'API", "Un morceau de mot, l'unité de base du texte", "Un paramètre du modèle", "Une phrase complète"], "answer": 1,
  "explain": "Le texte est découpé en tokens ; la fenêtre de contexte et la facturation se comptent en tokens."},
 {"q": "À quoi sert une pipeline scikit-learn ?", "options": ["À visualiser les données", "À enchaîner préparation et modèle en un seul objet, sans fuite de données", "À télécharger des données", "À accélérer Python"], "answer": 1,
  "explain": "La pipeline applique les mêmes transformations à l'entraînement et à la prédiction, apprises uniquement sur le train."},
]}
