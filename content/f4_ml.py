"""FullStack · Apprentissage automatique (vague 3) : prétraitement, régularisation, arbres, boosting, séries temporelles, K-means."""

def E(id, title, prompt, starter, solution, check, hint):
    return {"id": id, "title": title, "prompt": prompt, "starter": starter, "solution": solution, "check": check, "hint": hint}

IMMO_PRE = '''import pandas as pd
from immo import charger
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

df = charger()
df = df[df["prix"] / df["surface"] < 20000]          # retire les erreurs de saisie
X, y = df.drop(columns="prix"), df["prix"]
NUM = ["surface", "pieces", "etage", "ascenseur", "annee_construction", "distance_metro_m", "balcon"]
CAT = ["quartier", "dpe"]
pre = ColumnTransformer([
    ("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), NUM),
    ("cat", OneHotEncoder(handle_unknown="ignore"), CAT),
])
'''

LESSONS = [
# ================================================================ Prétraitement
{"id": "l-ml-pre", "title": "Prétraitement avancé : ColumnTransformer et pipelines", "minutes": 80,
"body": r'''
Dans un vrai jeu de données, les colonnes n'ont pas toutes besoin du même traitement : les nombres doivent être imputés et mis à l'échelle, les catégories encodées. Le **ColumnTransformer** de scikit-learn applique le bon traitement à chaque groupe de colonnes, et la **Pipeline** enchaîne ce prétraitement avec le modèle. C'est le cœur du chapitre « Prétraitement avec sklearn » du FullStack.

On travaille avec **Immo** : 800 ventes d'appartements, avec des valeurs manquantes et deux erreurs de saisie, comme dans la vraie vie.

```python
import pandas as pd
from immo import charger

df = charger()
print(df.shape)
print(df.isna().sum()[lambda s: s > 0])
df.head()
```

```python
df["prix_m2"] = df["prix"] / df["surface"]
df.sort_values("prix_m2", ascending=False).head(3)[["surface", "quartier", "prix", "prix_m2"]]
```

Deux appartements à plus de 50 000 € le m² : un zéro de trop dans le prix. On les retire avant toute modélisation.

## Les briques du prétraitement

| Transformateur | Rôle |
| --- | --- |
| `SimpleImputer(strategy="median")` | Remplace les valeurs manquantes |
| `StandardScaler()` | Centre et réduit (moyenne 0, écart-type 1) |
| `MinMaxScaler()` | Ramène entre 0 et 1 |
| `OneHotEncoder(handle_unknown="ignore")` | Une colonne 0/1 par catégorie |
| `OrdinalEncoder(categories=[...])` | Un entier par catégorie, dans un ordre choisi (utile pour le DPE, de A à G) |

## Assembler avec ColumnTransformer

```python
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

df = df[df["prix_m2"] < 20000].drop(columns="prix_m2")
X, y = df.drop(columns="prix"), df["prix"]
NUM = ["surface", "pieces", "etage", "ascenseur", "annee_construction", "distance_metro_m", "balcon"]
CAT = ["quartier", "dpe"]

pre = ColumnTransformer([
    ("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), NUM),
    ("cat", OneHotEncoder(handle_unknown="ignore"), CAT),
])
Xt = pre.fit_transform(X)
print(Xt.shape)
print(pre.get_feature_names_out()[:10])
```

## Pourquoi tout mettre dans une pipeline

Si tu calcules la médiane ou la moyenne de mise à l'échelle sur **toutes** les données avant de séparer entraînement et test, des informations du test fuient dans l'entraînement : c'est une **fuite de données**, et ton score est trop optimiste. Dans une pipeline, chaque transformateur apprend uniquement sur les données d'entraînement de chaque pli de validation croisée.

```python
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score

modele = make_pipeline(pre, LinearRegression())
scores = cross_val_score(modele, X, y, cv=5, scoring="neg_mean_absolute_error")
print(f"Erreur absolue moyenne : {-scores.mean():,.0f} €".replace(",", " "))
```

> **À retenir** : un modèle de production = une pipeline (prétraitement + modèle) qu'on entraîne, évalue et sauvegarde comme un seul objet. C'est elle que tu déploieras derrière une API au module Ingénierie ML.
''',
"exercises": [
 E("e-ml-pre-a", "Un DPE ordonné",
   "Le DPE va de A (meilleur) à G (pire) : c'est une catégorie **ordonnée**. Crée `pre_ord`, un `ColumnTransformer` qui applique le traitement numérique de la leçon aux colonnes `NUM`, un `OrdinalEncoder` avec l'ordre `A` à `G` à la colonne `dpe`, et un `OneHotEncoder(handle_unknown=\"ignore\")` à `quartier`. Puis crée `Xt = pre_ord.fit_transform(X)`.",
   IMMO_PRE + "from sklearn.preprocessing import OrdinalEncoder\n",
   IMMO_PRE + 'from sklearn.preprocessing import OrdinalEncoder\n\npre_ord = ColumnTransformer([\n    ("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), NUM),\n    ("dpe", OrdinalEncoder(categories=[list("ABCDEFG")]), ["dpe"]),\n    ("quartier", OneHotEncoder(handle_unknown="ignore"), ["quartier"]),\n])\nXt = pre_ord.fit_transform(X)\nprint(Xt.shape)\n',
   r'''import numpy as np
Xd = np.asarray(Xt.todense()) if hasattr(Xt, "todense") else np.asarray(Xt)
assert Xd.shape == (len(X), 13), f"Xt a la forme {Xd.shape} ; attendu {len(X)} lignes et 13 colonnes (7 numériques + 1 DPE + 5 quartiers)."
assert not np.isnan(Xd).any(), "Il reste des valeurs manquantes : impute les colonnes numériques."
col = list(pre_ord.get_feature_names_out()).index([n for n in pre_ord.get_feature_names_out() if n.endswith("dpe")][0])
assert set(np.unique(Xd[:, col])) <= set(range(7)) and Xd[X["dpe"].values == "G", col].max() == 6, "Le DPE doit être codé de 0 (A) à 6 (G)."
''',
   "OrdinalEncoder(categories=[list(\"ABCDEFG\")]) : notez la liste de listes, une par colonne encodée."),
 E("e-ml-pre-b", "Une pipeline sans fuite",
   "Crée `modele`, une pipeline qui enchaîne `pre` et une `LinearRegression`, puis calcule `mae_cv`, l'erreur absolue moyenne en validation croisée à 5 plis (un nombre positif, en euros).",
   IMMO_PRE + "from sklearn.linear_model import LinearRegression\nfrom sklearn.model_selection import cross_val_score\n",
   IMMO_PRE + 'from sklearn.linear_model import LinearRegression\nfrom sklearn.model_selection import cross_val_score\n\nmodele = make_pipeline(pre, LinearRegression())\nmae_cv = -cross_val_score(modele, X, y, cv=5, scoring="neg_mean_absolute_error").mean()\nprint(round(mae_cv))\n',
   r'''from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
assert isinstance(modele, Pipeline), "modele doit être une Pipeline (make_pipeline)."
ref = -cross_val_score(modele, X, y, cv=5, scoring="neg_mean_absolute_error").mean()
assert mae_cv > 0, "Le score neg_mean_absolute_error est négatif : prends son opposé."
assert abs(mae_cv - ref) < 1, f"mae_cv vaut {mae_cv:.0f}, j'attendais {ref:.0f}."
''',
   "cross_val_score(modele, X, y, cv=5, scoring=\"neg_mean_absolute_error\") renvoie des scores négatifs : prends -scores.mean()."),
]},
# ================================================================ Régularisation
{"id": "l-ml-reg", "title": "Régularisation : Ridge, Lasso et recherche par grille", "minutes": 90,
"body": r'''
Avec beaucoup de variables, une régression linéaire peut donner des coefficients énormes qui s'ajustent au bruit : c'est le **surapprentissage**. La **régularisation** ajoute à l'erreur une pénalité sur la taille des coefficients.

```latex
\text{Ridge (L2)} : \; \min_w \sum_i (y_i - \hat{y}_i)^2 + \alpha \sum_j w_j^2
\qquad
\text{Lasso (L1)} : \; \min_w \sum_i (y_i - \hat{y}_i)^2 + \alpha \sum_j |w_j|
```

- **Ridge** rétrécit tous les coefficients, sans les annuler.
- **Lasso** annule les coefficients des variables peu utiles : il fait de la **sélection de variables**.
- **α** (*alpha*) règle la force de la pénalité : 0 = régression classique, très grand = coefficients presque nuls.

```viz regpath
```

Les variables doivent être **à la même échelle** (StandardScaler) : sinon la pénalité frappe davantage les variables exprimées en petites unités.

```python
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import StandardScaler

rng = np.random.default_rng(0)
X = rng.normal(size=(60, 8))
y = 3 * X[:, 0] - 2 * X[:, 1] + 0.5 * X[:, 2] + rng.normal(0, 1, 60)    # seules 3 variables comptent
X = StandardScaler().fit_transform(X)
for m in [LinearRegression(), Ridge(alpha=10), Lasso(alpha=0.3)]:
    print(f"{type(m).__name__:16}", m.fit(X, y).coef_.round(2))
```

## Choisir α : la recherche par grille

α est un **hyperparamètre** : on le choisit par validation croisée. `GridSearchCV` essaie toutes les valeurs d'une grille et garde la meilleure. Dans une pipeline, on nomme le paramètre `etape__parametre`.

```python
from immo import charger
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import GridSearchCV
import pandas as pd

df = charger(); df = df[df.prix / df.surface < 20000]
X, y = df.drop(columns="prix"), df["prix"]
NUM = ["surface", "pieces", "etage", "ascenseur", "annee_construction", "distance_metro_m", "balcon"]
pre = ColumnTransformer([("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), NUM),
                         ("cat", OneHotEncoder(handle_unknown="ignore"), ["quartier", "dpe"])])
grille = GridSearchCV(make_pipeline(pre, Ridge()), {"ridge__alpha": [0.01, 0.1, 1, 10, 100, 1000]},
                      cv=5, scoring="neg_mean_absolute_error")
grille.fit(X, y)
print("Meilleur alpha :", grille.best_params_, " MAE :", round(-grille.best_score_))
pd.DataFrame(grille.cv_results_)[["param_ridge__alpha", "mean_test_score"]].assign(mae=lambda d: -d.mean_test_score.round(0))
```

Pour une grande grille, `RandomizedSearchCV` tire des combinaisons au hasard : beaucoup plus rapide, presque aussi bon.

> **À retenir** : mets à l'échelle, régularise, et choisis α par validation croisée. Lasso si tu soupçonnes que beaucoup de variables sont inutiles, Ridge sinon ; ElasticNet combine les deux.
''',
"exercises": [
 E("e-ml-reg-a", "Lasso trouve les bonnes variables",
   "Sur les données générées ci-dessous (10 variables, seules quelques-unes comptent), entraîne un `Lasso(alpha=0.2)` et crée `gardees`, la liste des **indices** des variables dont le coefficient n'est pas nul.",
   "import numpy as np\nfrom sklearn.linear_model import Lasso\n\nrng = np.random.default_rng(42)\nX = rng.normal(size=(200, 10))\ny = 4 * X[:, 0] + 2.5 * X[:, 3] - 3 * X[:, 7] + rng.normal(0, 1, 200)\n",
   "import numpy as np\nfrom sklearn.linear_model import Lasso\n\nrng = np.random.default_rng(42)\nX = rng.normal(size=(200, 10))\ny = 4 * X[:, 0] + 2.5 * X[:, 3] - 3 * X[:, 7] + rng.normal(0, 1, 200)\n\nlasso = Lasso(alpha=0.2).fit(X, y)\ngardees = [i for i, c in enumerate(lasso.coef_) if c != 0]\nprint(lasso.coef_.round(2), gardees)\n",
   r'''assert list(gardees) == [0, 3, 7], f"gardees vaut {list(gardees)} ; les variables utiles sont 0, 3 et 7."
''',
   "lasso.coef_ contient un coefficient par variable ; garde les indices i où coef_[i] != 0."),
 E("e-ml-reg-b", "Grid search sur une pipeline",
   "Avec la pipeline Ridge de la leçon, lance un `GridSearchCV` sur `ridge__alpha` parmi `[0.1, 1, 10, 100, 1000]`, `cv=5`, en minimisant l'erreur absolue moyenne. Crée `meilleur_alpha` et `mae_meilleur` (positive).",
   IMMO_PRE + "from sklearn.linear_model import Ridge\nfrom sklearn.model_selection import GridSearchCV\n",
   IMMO_PRE + 'from sklearn.linear_model import Ridge\nfrom sklearn.model_selection import GridSearchCV\n\ngrille = GridSearchCV(make_pipeline(pre, Ridge()), {"ridge__alpha": [0.1, 1, 10, 100, 1000]},\n                      cv=5, scoring="neg_mean_absolute_error").fit(X, y)\nmeilleur_alpha = grille.best_params_["ridge__alpha"]\nmae_meilleur = -grille.best_score_\nprint(meilleur_alpha, round(mae_meilleur))\n',
   r'''from sklearn.linear_model import Ridge
from sklearn.model_selection import GridSearchCV
ref = GridSearchCV(make_pipeline(pre, Ridge()), {"ridge__alpha": [0.1, 1, 10, 100, 1000]}, cv=5, scoring="neg_mean_absolute_error").fit(X, y)
assert meilleur_alpha == ref.best_params_["ridge__alpha"], f"meilleur_alpha vaut {meilleur_alpha}, j'attendais {ref.best_params_['ridge__alpha']}."
assert abs(mae_meilleur + ref.best_score_) < 1, f"mae_meilleur vaut {mae_meilleur:.0f} ; attendu {-ref.best_score_:.0f} (pense au signe)."
''',
   "Le nom du paramètre est ridge__alpha (nom de l'étape en minuscules, deux tirets bas). best_score_ est négatif."),
]},
# ================================================================ Arbres
{"id": "l-ml-tree", "title": "Arbres de décision et forêts aléatoires", "minutes": 90,
"body": r'''
Un **arbre de décision** découpe l'espace des données par une suite de questions simples (« surface ≤ 45 m² ? »). Chaque feuille prédit la classe majoritaire (classification) ou la moyenne (régression) des exemples qui y tombent.

```viz tree
```

## Comment l'arbre choisit une question

À chaque nœud, il essaie toutes les variables et tous les seuils, et garde la coupe qui rend les deux groupes les plus **purs**. Pour la classification, la mesure d'impureté la plus courante est l'**indice de Gini** :

```latex
G = 1 - \sum_k p_k^2
```

où p_k est la proportion de la classe k dans le nœud. G = 0 : nœud pur. Pour la régression, on minimise la variance (l'erreur quadratique).

```python
from sklearn.tree import DecisionTreeClassifier, export_text
import pandas as pd

p = pd.read_csv("penguins.csv").dropna()
X, y = p[["bill_length_mm", "flipper_length_mm"]], p["species"]
arbre = DecisionTreeClassifier(max_depth=2, random_state=0).fit(X, y)
print(export_text(arbre, feature_names=list(X.columns)))
```

Un arbre est **lisible**, ne demande ni mise à l'échelle ni encodage numérique compliqué, et capte les interactions. Mais seul, il **surapprend** dès qu'il est profond : il faut le limiter (`max_depth`, `min_samples_leaf`).

## La forêt aléatoire

Une **forêt aléatoire** entraîne des centaines d'arbres, chacun sur un **échantillon bootstrap** des données (tirage avec remise) et en ne considérant qu'un **sous-ensemble aléatoire de variables** à chaque coupe. Puis elle moyenne leurs prédictions (ou fait voter). Les erreurs des arbres se compensent : c'est le **bagging**. Résultat : beaucoup moins de surapprentissage, et un excellent modèle par défaut sur les données tabulaires.

```python
from immo import charger
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score

df = charger(); df = df[df.prix / df.surface < 20000]
X = pd.get_dummies(df.drop(columns="prix"), columns=["quartier", "dpe"]).fillna(-1)
y = df["prix"]
foret = RandomForestRegressor(n_estimators=100, min_samples_leaf=2, random_state=0, n_jobs=1)
print("MAE :", round(-cross_val_score(foret, X, y, cv=3, scoring="neg_mean_absolute_error").mean()))
foret.fit(X, y)
pd.Series(foret.feature_importances_, index=X.columns).sort_values(ascending=False).head(6).round(3)
```

Les **importances** indiquent quelles variables le modèle utilise le plus. Attention : elles favorisent les variables continues et ne disent rien du sens de l'effet. Pour expliquer un modèle, on utilisera plus tard l'importance par permutation ou les valeurs SHAP.

> **À retenir** : un arbre seul = lisible mais instable ; une forêt = robuste et performante sans réglage fin. Les arbres n'ont besoin ni de mise à l'échelle, ni de linéarité.
''',
"exercises": [
 E("e-ml-tree-a", "L'indice de Gini",
   "Écris `gini(etiquettes)` qui renvoie l'impureté de Gini d'une liste d'étiquettes (n'importe quelles valeurs). Une liste vide a une impureté de 0.",
   "from collections import Counter\n\ndef gini(etiquettes):\n    pass\n",
   "from collections import Counter\n\ndef gini(etiquettes):\n    n = len(etiquettes)\n    if n == 0:\n        return 0.0\n    return 1 - sum((c / n) ** 2 for c in Counter(etiquettes).values())\n\nprint(gini([\"a\", \"a\", \"b\", \"b\"]), gini([\"a\"] * 5))\n",
   r'''assert abs(gini(["a", "a", "b", "b"]) - 0.5) < 1e-9, "Deux classes à égalité : Gini = 0.5."
assert gini(["x"] * 7) == 0, "Un nœud pur a un Gini de 0."
assert abs(gini([1, 2, 3]) - 2 / 3) < 1e-9, "Trois classes équiprobables : Gini = 2/3."
assert gini([]) == 0, "Une liste vide doit renvoyer 0."
''',
   "Compte les classes avec Counter, puis 1 - somme des proportions au carré."),
 E("e-ml-tree-b", "Trouver la meilleure coupe",
   "Écris `meilleur_seuil(x, y)` qui essaie comme seuils toutes les valeurs **distinctes** de `x` (sauf la plus grande), coupe en `x <= seuil` et `x > seuil`, et renvoie le couple `(seuil, impurete)` qui minimise l'**impureté de Gini pondérée** : (n_gauche × G_gauche + n_droite × G_droite) / n. Réutilise ta fonction `gini`.",
   "from collections import Counter\n\ndef gini(etiquettes):\n    pass   # recopie ta fonction\n\ndef meilleur_seuil(x, y):\n    pass\n\nx = [1, 2, 3, 4, 5, 6]\ny = [\"a\", \"a\", \"a\", \"b\", \"b\", \"a\"]\n",
   "from collections import Counter\n\ndef gini(etiquettes):\n    n = len(etiquettes)\n    return 0.0 if n == 0 else 1 - sum((c / n) ** 2 for c in Counter(etiquettes).values())\n\ndef meilleur_seuil(x, y):\n    n, meilleur = len(x), None\n    for s in sorted(set(x))[:-1]:\n        g = [c for v, c in zip(x, y) if v <= s]\n        d = [c for v, c in zip(x, y) if v > s]\n        imp = (len(g) * gini(g) + len(d) * gini(d)) / n\n        if meilleur is None or imp < meilleur[1]:\n            meilleur = (s, imp)\n    return meilleur\n\nx = [1, 2, 3, 4, 5, 6]\ny = [\"a\", \"a\", \"a\", \"b\", \"b\", \"a\"]\nprint(meilleur_seuil(x, y))\n",
   r'''s, imp = meilleur_seuil([1, 2, 3, 4, 5, 6], ["a", "a", "a", "b", "b", "a"])
assert s == 3 and abs(imp - 2 / 9) < 1e-9, f"meilleur_seuil renvoie {(s, imp)} ; attendu (3, 2/9)."
s2, imp2 = meilleur_seuil([10, 1, 7, 3], [1, 0, 1, 0])
assert s2 == 3 and imp2 == 0, f"Avec des x non triés : {(s2, imp2)} ; attendu (3, 0.0)."
''',
   "Boucle sur sorted(set(x))[:-1]. Pour chaque seuil, construis les deux groupes d'étiquettes et calcule l'impureté pondérée."),
 E("e-ml-tree-c", "Ce qui fait le prix",
   "Entraîne une `RandomForestRegressor(n_estimators=100, random_state=0)` sur Immo (préparé comme dans la leçon avec `get_dummies` et `fillna(-1)`) et crée `importances`, une Series des importances indexée par le nom des variables, triée par ordre décroissant.",
   "import pandas as pd\nfrom immo import charger\nfrom sklearn.ensemble import RandomForestRegressor\n\ndf = charger(); df = df[df.prix / df.surface < 20000]\nX = pd.get_dummies(df.drop(columns=\"prix\"), columns=[\"quartier\", \"dpe\"]).fillna(-1)\ny = df[\"prix\"]\n",
   "import pandas as pd\nfrom immo import charger\nfrom sklearn.ensemble import RandomForestRegressor\n\ndf = charger(); df = df[df.prix / df.surface < 20000]\nX = pd.get_dummies(df.drop(columns=\"prix\"), columns=[\"quartier\", \"dpe\"]).fillna(-1)\ny = df[\"prix\"]\n\nforet = RandomForestRegressor(n_estimators=100, random_state=0).fit(X, y)\nimportances = pd.Series(foret.feature_importances_, index=X.columns).sort_values(ascending=False)\nimportances.head(8).round(3)\n",
   r'''import pandas as pd
assert isinstance(importances, pd.Series) and len(importances) == X.shape[1], "importances doit être une Series avec une valeur par colonne de X."
assert list(importances.values) == sorted(importances.values, reverse=True), "Trie par ordre décroissant."
assert importances.index[0] == "surface", f"La variable la plus importante devrait être surface ; tu as {importances.index[0]}."
assert abs(importances.sum() - 1) < 1e-6, "Les importances d'une forêt somment à 1 : as-tu bien utilisé feature_importances_ ?"
''',
   "pd.Series(foret.feature_importances_, index=X.columns).sort_values(ascending=False)"),
]},
# ================================================================ Boosting
{"id": "l-ml-boost", "title": "Boosting, XGBoost et méthodes d'ensemble", "minutes": 90,
"body": r'''
Le **boosting** construit lui aussi un ensemble d'arbres, mais **en séquence** : chaque nouvel arbre, petit, corrige les erreurs de tous les précédents. C'est la famille de modèles qui gagne la plupart des compétitions sur données tabulaires : XGBoost, LightGBM, CatBoost, et `HistGradientBoosting` dans scikit-learn.

```viz boost
```

## Le principe, en régression

1. On part d'une prédiction constante : la moyenne.
2. On calcule les **résidus** (valeur réelle − prédiction).
3. On entraîne un petit arbre à prédire ces résidus.
4. On ajoute ses prédictions, multipliées par un **taux d'apprentissage** η (par exemple 0,1).
5. On recommence des centaines de fois.

C'est une descente de gradient… dans l'espace des fonctions : chaque arbre est un pas dans la direction qui réduit l'erreur.

```python
import numpy as np
from sklearn.tree import DecisionTreeRegressor

rng = np.random.default_rng(1)
x = np.sort(rng.uniform(0, 6, 120)).reshape(-1, 1)
y = np.sin(x[:, 0]) * 3 + rng.normal(0, 0.4, 120)

pred = np.full(len(y), y.mean())
for etape in range(1, 101):
    arbre = DecisionTreeRegressor(max_depth=2).fit(x, y - pred)   # on apprend les résidus
    pred += 0.1 * arbre.predict(x)
    if etape in [1, 10, 50, 100]:
        print(f"après {etape:3} arbres : MSE = {((y - pred) ** 2).mean():.3f}")
```

## Bagging contre boosting

| | Forêt aléatoire (bagging) | Gradient boosting |
| --- | --- | --- |
| Arbres | Profonds, indépendants, en parallèle | Petits, en séquence |
| Réduit surtout | La variance | Le biais |
| Réglages | Peu sensibles | Taux d'apprentissage, nombre d'arbres, profondeur |
| Risque | Faible | Surapprentissage si trop d'arbres : on utilise l'arrêt anticipé |

## En pratique

```python
import pandas as pd
from immo import charger
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import cross_val_score

df = charger(); df = df[df.prix / df.surface < 20000]
X = df.drop(columns="prix").astype({"quartier": "category", "dpe": "category"})
y = df["prix"]
hgb = HistGradientBoostingRegressor(learning_rate=0.1, max_iter=300, categorical_features="from_dtype", random_state=0)
print("MAE :", round(-cross_val_score(hgb, X, y, cv=3, scoring="neg_mean_absolute_error").mean()))
```

`HistGradientBoosting` gère seul les valeurs manquantes et les catégories. Sur ton ordinateur, XGBoost s'utilise de la même façon :

```pycode
from xgboost import XGBRegressor      # pip install xgboost
modele = XGBRegressor(n_estimators=500, learning_rate=0.05, max_depth=4,
                      subsample=0.8, colsample_bytree=0.8, early_stopping_rounds=30)
modele.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
```

## Voter et empiler

- **Vote** (`VotingClassifier`, `VotingRegressor`) : on moyenne les prédictions de modèles différents.
- **Empilement** (*stacking*, `StackingRegressor`) : un modèle final apprend à combiner les prédictions des autres.

> **À retenir** : sur des données tabulaires, commence par une forêt aléatoire puis un gradient boosting. Règle le taux d'apprentissage et le nombre d'arbres ensemble, avec arrêt anticipé.
''',
"exercises": [
 E("e-ml-boost-a", "Ton propre gradient boosting",
   "Écris `boosting(x, y, n_arbres, eta, profondeur=1)` qui implémente l'algorithme de la leçon et renvoie le couple `(pred, mses)` : les prédictions finales sur `x` et la liste des MSE d'entraînement **après chaque arbre** (longueur `n_arbres`).",
   "import numpy as np\nfrom sklearn.tree import DecisionTreeRegressor\n\nrng = np.random.default_rng(3)\nx = np.sort(rng.uniform(0, 6, 150)).reshape(-1, 1)\ny = np.sin(x[:, 0]) * 3 + rng.normal(0, 0.4, 150)\n\ndef boosting(x, y, n_arbres, eta, profondeur=1):\n    pass\n",
   "import numpy as np\nfrom sklearn.tree import DecisionTreeRegressor\n\nrng = np.random.default_rng(3)\nx = np.sort(rng.uniform(0, 6, 150)).reshape(-1, 1)\ny = np.sin(x[:, 0]) * 3 + rng.normal(0, 0.4, 150)\n\ndef boosting(x, y, n_arbres, eta, profondeur=1):\n    pred = np.full(len(y), y.mean())\n    mses = []\n    for _ in range(n_arbres):\n        arbre = DecisionTreeRegressor(max_depth=profondeur).fit(x, y - pred)\n        pred = pred + eta * arbre.predict(x)\n        mses.append(((y - pred) ** 2).mean())\n    return pred, mses\n\npred, mses = boosting(x, y, 200, 0.1)\nprint(round(mses[0], 3), round(mses[-1], 3))\n",
   r'''import numpy as np
pred, mses = boosting(x, y, 200, 0.1)
assert len(mses) == 200 and pred.shape == y.shape, "boosting doit renvoyer les prédictions et une MSE par arbre."
assert all(b <= a + 1e-12 for a, b in zip(mses, mses[1:])), "La MSE d'entraînement ne doit jamais augmenter d'un arbre à l'autre."
assert mses[-1] < 0.25 * y.var(), f"MSE finale {mses[-1]:.3f} : trop élevée, le modèle n'apprend pas les résidus."
p1, m1 = boosting(x, y, 1, 1.0)
assert abs(m1[0] - ((y - p1) ** 2).mean()) < 1e-9, "Chaque MSE doit être calculée après l'ajout de l'arbre correspondant."
''',
   "pred commence à y.mean(). À chaque tour : un arbre sur (x, y - pred), puis pred += eta * arbre.predict(x)."),
 E("e-ml-boost-b", "Forêt contre boosting",
   "Compare en validation croisée à 3 plis l'erreur absolue moyenne d'une `RandomForestRegressor(n_estimators=100, random_state=0)` et d'un `HistGradientBoostingRegressor(random_state=0)` sur `X_num` (variables encodées, fournies). Range les deux MAE (positives) dans le dictionnaire `maes` avec les clés `\"foret\"` et `\"boosting\"`, puis crée `meilleur`, la clé du modèle à l'erreur la plus basse.",
   "import pandas as pd\nfrom immo import charger\nfrom sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor\nfrom sklearn.model_selection import cross_val_score\n\ndf = charger(); df = df[df.prix / df.surface < 20000]\nX_num = pd.get_dummies(df.drop(columns=\"prix\"), columns=[\"quartier\", \"dpe\"]).fillna(-1)\ny = df[\"prix\"]\n",
   "import pandas as pd\nfrom immo import charger\nfrom sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor\nfrom sklearn.model_selection import cross_val_score\n\ndf = charger(); df = df[df.prix / df.surface < 20000]\nX_num = pd.get_dummies(df.drop(columns=\"prix\"), columns=[\"quartier\", \"dpe\"]).fillna(-1)\ny = df[\"prix\"]\n\nmodeles = {\"foret\": RandomForestRegressor(n_estimators=100, random_state=0),\n           \"boosting\": HistGradientBoostingRegressor(random_state=0)}\nmaes = {nom: -cross_val_score(m, X_num, y, cv=3, scoring=\"neg_mean_absolute_error\").mean() for nom, m in modeles.items()}\nmeilleur = min(maes, key=maes.get)\nprint({k: round(v) for k, v in maes.items()}, meilleur)\n",
   r'''assert set(maes) == {"foret", "boosting"}, f"maes doit avoir les clés foret et boosting ; tu as {set(maes)}."
assert all(20000 < v < 60000 for v in maes.values()), f"Les MAE doivent être positives et de l'ordre de 30 000 € : {maes}."
assert meilleur == min(maes, key=maes.get) == "boosting", f"meilleur vaut {meilleur!r}."
''',
   "Un dictionnaire de modèles, puis une compréhension de dictionnaire avec cross_val_score. min(maes, key=maes.get) donne la meilleure clé."),
]},
# ================================================================ Séries temporelles
{"id": "l-ml-ts", "title": "Séries chronologiques et prévision", "minutes": 90,
"body": r'''
Une **série chronologique** est une suite de mesures dans le temps : ventes quotidiennes, trafic d'un site, consommation électrique. Elle a souvent une **tendance**, une ou plusieurs **saisonnalités** (hebdomadaire, annuelle) et du bruit. Sa particularité : l'ordre compte, et on ne doit jamais utiliser le futur pour prédire le passé.

On simule deux ans de locations quotidiennes de vélos :

```python
import numpy as np
import pandas as pd
import plotly.express as px

rng = np.random.default_rng(0)
jours = pd.date_range("2024-01-01", "2025-12-31", freq="D")
t = np.arange(len(jours))
semaine = np.where(jours.dayofweek >= 5, 1.35, 1.0)                     # plus de locations le week-end
annee = 1 + 0.45 * np.sin(2 * np.pi * (jours.dayofyear - 110) / 365)    # pic en été
velos = pd.Series((200 + 0.15 * t) * semaine * annee + rng.normal(0, 18, len(t)), index=jours, name="locations").round()
px.line(x=velos.index, y=velos.values, title="Locations quotidiennes de vélos", labels={"x": "date", "y": "locations"})
```

## Manipuler le temps avec pandas

```python
print(velos["2025-07"].head(3))                         # sélectionner un mois
mensuel = velos.resample("MS").sum()                    # agréger par mois
lisse = velos.rolling(28, center=True).mean()           # moyenne mobile sur 28 jours
retard = velos.shift(7)                                 # la valeur d'il y a 7 jours
pd.DataFrame({"locations": velos, "il_y_a_7_jours": retard}).dropna().head(3)
```

```viz ts
```

## Évaluer une prévision

On sépare **dans le temps** : on entraîne sur le passé, on teste sur la période qui suit. Jamais de mélange aléatoire.

Et on compare toujours à deux **baselines** :
- **naïve** : demain = aujourd'hui ;
- **saisonnière naïve** : demain = le même jour la semaine dernière.

```python
test = velos["2025-11-01":]
naif = velos.shift(1)[test.index]
saisonnier = velos.shift(7)[test.index]
mae = lambda p: (test - p).abs().mean()
print(f"MAE naïve : {mae(naif):.1f}   MAE saisonnière : {mae(saisonnier):.1f}")
```

## Un modèle avec des variables de retard

On transforme la série en tableau classique : chaque jour devient une ligne avec, comme variables, les valeurs passées (*lags*) et le calendrier. N'importe quel modèle de régression s'applique alors. Ici on prévoit **le lendemain** : on a donc le droit d'utiliser la valeur de la veille (`lag_1`) et celles des semaines précédentes, que le modèle moyenne pour lisser le bruit.

```python
from sklearn.linear_model import LinearRegression

d = pd.DataFrame({"y": velos})
for k in [1, 7, 14, 21, 28]:
    d[f"lag_{k}"] = d["y"].shift(k)
d = d.join(pd.get_dummies(d.index.dayofweek, prefix="jour").set_index(d.index).astype(int)).dropna()
train, test_d = d[:"2025-10-31"], d["2025-11-01":]
modele = LinearRegression().fit(train.drop(columns="y"), train["y"])
pred = modele.predict(test_d.drop(columns="y"))
print(f"MAE du modèle : {(test_d['y'] - pred).abs().mean():.1f}")
```

## Prophet

Le FullStack utilise **Prophet** (Meta), qui décompose automatiquement tendance, saisonnalités et jours fériés. Sur ton ordinateur :

```pycode
from prophet import Prophet          # pip install prophet
df_p = velos.reset_index().rename(columns={"index": "ds", "locations": "y"})
m = Prophet(weekly_seasonality=True, yearly_seasonality=True).fit(df_p[df_p.ds < "2025-11-01"])
futur = m.make_future_dataframe(periods=61)
prevision = m.predict(futur)          # colonnes yhat, yhat_lower, yhat_upper
m.plot_components(prevision)
```

> **À retenir** : sépare dans le temps, bats d'abord la baseline saisonnière, et transforme la série en tableau avec des retards pour utiliser n'importe quel modèle de ML.
''',
"exercises": [
 E("e-ml-ts-a", "Les deux baselines",
   "Sur la série `velos` (fournie), pour la période de test à partir du 1er novembre 2025, calcule `mae_naif` (prévision = valeur de la veille) et `mae_saisonnier` (prévision = valeur 7 jours avant).",
   "import numpy as np\nimport pandas as pd\nrng = np.random.default_rng(0)\njours = pd.date_range(\"2024-01-01\", \"2025-12-31\", freq=\"D\")\nt = np.arange(len(jours))\nvelos = pd.Series((200 + 0.15 * t) * np.where(jours.dayofweek >= 5, 1.35, 1.0)\n                  * (1 + 0.45 * np.sin(2 * np.pi * (jours.dayofyear - 110) / 365))\n                  + rng.normal(0, 18, len(t)), index=jours).round()\n",
   "import numpy as np\nimport pandas as pd\nrng = np.random.default_rng(0)\njours = pd.date_range(\"2024-01-01\", \"2025-12-31\", freq=\"D\")\nt = np.arange(len(jours))\nvelos = pd.Series((200 + 0.15 * t) * np.where(jours.dayofweek >= 5, 1.35, 1.0)\n                  * (1 + 0.45 * np.sin(2 * np.pi * (jours.dayofyear - 110) / 365))\n                  + rng.normal(0, 18, len(t)), index=jours).round()\n\ntest = velos[\"2025-11-01\":]\nmae_naif = (test - velos.shift(1)[test.index]).abs().mean()\nmae_saisonnier = (test - velos.shift(7)[test.index]).abs().mean()\nprint(round(mae_naif, 1), round(mae_saisonnier, 1))\n",
   r'''test = velos["2025-11-01":]
assert abs(mae_naif - (test - velos.shift(1)[test.index]).abs().mean()) < 1e-6, "mae_naif ne correspond pas : prévision = velos.shift(1)."
assert abs(mae_saisonnier - (test - velos.shift(7)[test.index]).abs().mean()) < 1e-6, "mae_saisonnier ne correspond pas : prévision = velos.shift(7)."
assert mae_saisonnier < mae_naif, "Avec une forte saisonnalité hebdomadaire, la baseline saisonnière doit être meilleure."
''',
   "velos.shift(1) décale la série d'un jour ; sélectionne ensuite les dates de test avec [test.index]."),
 E("e-ml-ts-b", "Battre la baseline",
   "Construis le tableau `d` avec la cible `y`, les retards `lag_1`, `lag_7`, `lag_14`, `lag_21`, `lag_28` et les indicatrices du jour de la semaine, comme dans la leçon. Entraîne une `LinearRegression` jusqu'au 31 octobre 2025 et calcule `mae_modele` sur la période à partir du 1er novembre. Elle doit être meilleure que la baseline saisonnière.",
   "import numpy as np\nimport pandas as pd\nfrom sklearn.linear_model import LinearRegression\nrng = np.random.default_rng(0)\njours = pd.date_range(\"2024-01-01\", \"2025-12-31\", freq=\"D\")\nt = np.arange(len(jours))\nvelos = pd.Series((200 + 0.15 * t) * np.where(jours.dayofweek >= 5, 1.35, 1.0)\n                  * (1 + 0.45 * np.sin(2 * np.pi * (jours.dayofyear - 110) / 365))\n                  + rng.normal(0, 18, len(t)), index=jours).round()\n",
   "import numpy as np\nimport pandas as pd\nfrom sklearn.linear_model import LinearRegression\nrng = np.random.default_rng(0)\njours = pd.date_range(\"2024-01-01\", \"2025-12-31\", freq=\"D\")\nt = np.arange(len(jours))\nvelos = pd.Series((200 + 0.15 * t) * np.where(jours.dayofweek >= 5, 1.35, 1.0)\n                  * (1 + 0.45 * np.sin(2 * np.pi * (jours.dayofyear - 110) / 365))\n                  + rng.normal(0, 18, len(t)), index=jours).round()\n\nd = pd.DataFrame({\"y\": velos})\nfor k in [1, 7, 14, 21, 28]:\n    d[f\"lag_{k}\"] = d[\"y\"].shift(k)\nd = d.join(pd.get_dummies(d.index.dayofweek, prefix=\"jour\").set_index(d.index).astype(int)).dropna()\ntrain, test = d[:\"2025-10-31\"], d[\"2025-11-01\":]\nmodele = LinearRegression().fit(train.drop(columns=\"y\"), train[\"y\"])\nmae_modele = (test[\"y\"] - modele.predict(test.drop(columns=\"y\"))).abs().mean()\nprint(round(mae_modele, 1))\n",
   r'''assert {"lag_1", "lag_7", "lag_14", "lag_21", "lag_28"} <= set(d.columns), "d doit contenir les colonnes lag_1, lag_7, lag_14, lag_21 et lag_28."
assert d.index.min() >= pd.Timestamp("2024-01-29"), "Supprime les lignes incomplètes (dropna) créées par les retards."
tst = velos["2025-11-01":]
saison = (tst - velos.shift(7)[tst.index]).abs().mean()
assert mae_modele < saison, f"mae_modele = {mae_modele:.1f} ne bat pas la baseline saisonnière ({saison:.1f})."
''',
   "Reprends le code de la leçon. La séparation se fait par dates : d[:\"2025-10-31\"] et d[\"2025-11-01\":]."),
]},
# ================================================================ K-means
{"id": "l-ml-kmeans", "title": "K-means et clustering", "minutes": 90,
"body": r'''
Le **clustering** regroupe des données **sans étiquettes** : segmentation de clients, regroupement de documents, compression d'images. **K-means** est l'algorithme le plus utilisé : il cherche k centres tels que chaque point soit proche du centre de son groupe.

```viz kmeans
```

## L'algorithme

1. Choisir k centres au départ (au hasard parmi les points, ou avec l'initialisation *k-means++*).
2. **Affecter** chaque point au centre le plus proche.
3. **Mettre à jour** chaque centre : la moyenne des points qui lui sont affectés.
4. Répéter 2 et 3 jusqu'à ce que plus rien ne bouge.

K-means minimise l'**inertie** : la somme des distances au carré entre chaque point et son centre.

```latex
\text{inertie} = \sum_i \lVert x_i - \mu_{c(i)} \rVert^2
```

```python
import numpy as np

rng = np.random.default_rng(2)
X = np.vstack([rng.normal(c, 0.6, size=(50, 2)) for c in [(0, 0), (4, 1), (2, 4)]])
centres = X[rng.choice(len(X), 3, replace=False)]
for etape in range(6):
    distances = ((X[:, None, :] - centres[None, :, :]) ** 2).sum(axis=2)   # (150, 3)
    labels = distances.argmin(axis=1)
    centres = np.array([X[labels == k].mean(axis=0) for k in range(3)])
    print(f"étape {etape}: inertie = {distances.min(axis=1).sum():.1f}")
```

## Avec scikit-learn, et comment choisir k

```python
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

p = pd.read_csv("penguins.csv").dropna()
Xp = StandardScaler().fit_transform(p[["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]])
for k in range(2, 7):
    km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(Xp)
    print(f"k = {k}  inertie = {km.inertia_:7.1f}  silhouette = {silhouette_score(Xp, km.labels_):.3f}")
```

- La **méthode du coude** : l'inertie baisse toujours quand k augmente ; on cherche le point où elle cesse de baisser fortement.
- Le **score de silhouette** (entre −1 et 1) mesure si chaque point est plus proche de son groupe que du groupe voisin. Plus il est haut, mieux c'est.

Les manchots ont 3 espèces : K-means les retrouve-t-il sans les connaître ?

```python
km = KMeans(n_clusters=3, n_init=10, random_state=0).fit(Xp)
pd.crosstab(km.labels_, p["species"])
```

## Les limites

- Il faut **mettre à l'échelle** : sinon la masse en grammes écrase la longueur du bec en millimètres.
- K-means suppose des groupes **ronds** et de taille comparable. Pour des formes allongées ou du bruit, on utilise DBSCAN ou un mélange de gaussiennes.
- Le résultat dépend de l'initialisation : `n_init=10` relance l'algorithme 10 fois et garde le meilleur.

> **À retenir** : mets à l'échelle, essaie plusieurs k, regarde le coude et la silhouette, puis **interprète** chaque groupe avec les moyennes de ses variables. Un clustering n'a de valeur que s'il est utile au métier.
''',
"exercises": [
 E("e-ml-km-a", "Affecter les points",
   "Écris `affecter(X, centres)` qui renvoie, pour chaque point de `X` (tableau (n, d)), l'indice du centre le plus proche parmi `centres` (tableau (k, d)), **sans boucle** Python, grâce au broadcasting.",
   "import numpy as np\n\ndef affecter(X, centres):\n    pass\n",
   "import numpy as np\n\ndef affecter(X, centres):\n    d = ((X[:, None, :] - centres[None, :, :]) ** 2).sum(axis=2)\n    return d.argmin(axis=1)\n\nX = np.array([[0, 0], [10, 10], [1, 0], [9, 11]])\nprint(affecter(X, np.array([[0, 0], [10, 10]])))\n",
   r'''import numpy as np
X = np.array([[0, 0], [10, 10], [1, 0], [9, 11], [6, 6]], dtype=float)
C = np.array([[0, 0], [10, 10]], dtype=float)
assert list(affecter(X, C)) == [0, 1, 0, 1, 1], f"affecter renvoie {list(affecter(X, C))}."
rng = np.random.default_rng(0); A = rng.normal(size=(200, 3)); B = rng.normal(size=(4, 3))
ref = np.array([np.argmin([((a - b) ** 2).sum() for b in B]) for a in A])
assert (affecter(A, B) == ref).all(), "Le résultat est faux en dimension 3 : vérifie les axes du broadcasting."
''',
   "X[:, None, :] - centres[None, :, :] a la forme (n, k, d). Somme sur l'axe 2, puis argmin sur l'axe 1."),
 E("e-ml-km-b", "K-means de zéro",
   "Écris `kmeans(X, k, n_iter=50, graine=0)` : initialise les centres avec `k` points tirés sans remise (`np.random.default_rng(graine).choice(len(X), k, replace=False)`), puis alterne affectation et mise à jour. Arrête-toi si les centres ne bougent plus. Renvoie `(labels, centres, inertie)`.",
   "import numpy as np\n\ndef affecter(X, centres):\n    pass   # recopie ta fonction\n\ndef kmeans(X, k, n_iter=50, graine=0):\n    pass\n",
   "import numpy as np\n\ndef affecter(X, centres):\n    return ((X[:, None, :] - centres[None, :, :]) ** 2).sum(axis=2).argmin(axis=1)\n\ndef kmeans(X, k, n_iter=50, graine=0):\n    rng = np.random.default_rng(graine)\n    centres = X[rng.choice(len(X), k, replace=False)].astype(float)\n    for _ in range(n_iter):\n        labels = affecter(X, centres)\n        nouveaux = np.array([X[labels == j].mean(axis=0) if (labels == j).any() else centres[j] for j in range(k)])\n        if np.allclose(nouveaux, centres):\n            break\n        centres = nouveaux\n    labels = affecter(X, centres)\n    inertie = ((X - centres[labels]) ** 2).sum()\n    return labels, centres, inertie\n\nrng = np.random.default_rng(2)\nX = np.vstack([rng.normal(c, 0.6, size=(50, 2)) for c in [(0, 0), (4, 1), (2, 4)]])\nlabels, centres, inertie = kmeans(X, 3)\nprint(centres.round(2), round(inertie, 1))\n",
   r'''import numpy as np
from sklearn.cluster import KMeans
rng = np.random.default_rng(2)
X = np.vstack([rng.normal(c, 0.6, size=(50, 2)) for c in [(0, 0), (4, 1), (2, 4)]])
labels, centres, inertie = kmeans(X, 3)
assert centres.shape == (3, 2) and len(labels) == 150, "kmeans doit renvoyer 150 labels et 3 centres en 2D."
for j in range(3):
    assert np.allclose(centres[j], X[labels == j].mean(axis=0)), "À la convergence, chaque centre est la moyenne de ses points."
assert abs(inertie - ((X - centres[labels]) ** 2).sum()) < 1e-6, "L'inertie doit être la somme des distances au carré à son centre."
best = KMeans(3, n_init=10, random_state=0).fit(X).inertia_
assert inertie < 1.2 * best, f"Inertie {inertie:.1f} bien supérieure à l'optimum ({best:.1f}) : l'algorithme ne converge pas."
''',
   "Boucle : affecter, calculer les nouveaux centres (moyenne par groupe), comparer avec np.allclose pour s'arrêter."),
 E("e-ml-km-c", "Segmenter les manchots",
   "Mets à l'échelle les 4 mesures des manchots, applique `KMeans(n_clusters=3, n_init=10, random_state=0)`, puis calcule `purete` : pour chaque groupe, le nombre de manchots de l'espèce majoritaire, additionné sur les 3 groupes et divisé par le nombre total de manchots.",
   "import pandas as pd\nfrom sklearn.cluster import KMeans\nfrom sklearn.preprocessing import StandardScaler\n\np = pd.read_csv(\"penguins.csv\").dropna()\ncols = [\"bill_length_mm\", \"bill_depth_mm\", \"flipper_length_mm\", \"body_mass_g\"]\n",
   "import pandas as pd\nfrom sklearn.cluster import KMeans\nfrom sklearn.preprocessing import StandardScaler\n\np = pd.read_csv(\"penguins.csv\").dropna()\ncols = [\"bill_length_mm\", \"bill_depth_mm\", \"flipper_length_mm\", \"body_mass_g\"]\n\nXp = StandardScaler().fit_transform(p[cols])\nkm = KMeans(n_clusters=3, n_init=10, random_state=0).fit(Xp)\ntableau = pd.crosstab(km.labels_, p[\"species\"])\npurete = tableau.max(axis=1).sum() / len(p)\nprint(tableau, round(purete, 3))\n",
   r'''import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
Xr = StandardScaler().fit_transform(p[cols])
ref = pd.crosstab(KMeans(n_clusters=3, n_init=10, random_state=0).fit(Xr).labels_, p["species"]).max(axis=1).sum() / len(p)
assert abs(purete - ref) < 1e-9, f"purete vaut {purete:.3f}, j'attendais {ref:.3f}. As-tu bien mis à l'échelle ?"
assert purete > 0.85, "Sans mise à l'échelle, la masse écrase les autres variables."
''',
   "pd.crosstab(labels, espèces) donne le tableau groupes × espèces ; .max(axis=1).sum() additionne les effectifs majoritaires."),
]},
]

PROJECTS = [
{"id": "p-ml", "title": "Projet · Estimer le prix d'un appartement", "minutes": 180,
"body": r'''
L'équivalent du projet « Marché immobilier » du FullStack : construire, comparer et évaluer proprement des modèles de prix sur le jeu de données Immo, puis préparer le modèle pour la mise en production.

La démarche professionnelle, dans l'ordre :

1. Nettoyer et justifier chaque choix.
2. Fixer une **baseline**.
3. Comparer plusieurs modèles **en validation croisée**, sur le jeu d'entraînement seulement.
4. Évaluer **une seule fois** le modèle retenu sur le jeu de test.
5. Expliquer les erreurs et les limites.
''',
"exercises": [
 E("e-pml-a", "Nettoyer et séparer",
   "Charge Immo, retire les ventes dont le prix au m² dépasse 20 000 €, puis sépare en `X_train, X_test, y_train, y_test` (20 % de test, `random_state=42`), avec `y` = `prix` et `X` = toutes les autres colonnes.",
   "import pandas as pd\nfrom immo import charger\nfrom sklearn.model_selection import train_test_split\n",
   "import pandas as pd\nfrom immo import charger\nfrom sklearn.model_selection import train_test_split\n\ndf = charger()\ndf = df[df[\"prix\"] / df[\"surface\"] <= 20000]\nX, y = df.drop(columns=\"prix\"), df[\"prix\"]\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\nprint(X_train.shape, X_test.shape)\n",
   r'''assert len(X_train) + len(X_test) == 798, f"Il doit rester 798 ventes après nettoyage ; tu en as {len(X_train) + len(X_test)}."
assert "prix" not in X_train.columns, "La colonne prix ne doit pas être dans X."
assert len(X_test) == 160, f"X_test doit avoir 160 lignes ; il en a {len(X_test)}."
''',
   "df[df[\"prix\"] / df[\"surface\"] <= 20000], puis train_test_split(X, y, test_size=0.2, random_state=42)."),
 E("e-pml-b", "Comparer et choisir",
   "Sur `X_train`, compare en validation croisée (5 plis, erreur absolue moyenne) trois pipelines : `pre` + `Ridge(alpha=10)`, `pre` + `RandomForestRegressor(n_estimators=100, random_state=0)`, et `pre` + `HistGradientBoostingRegressor(random_state=0)`. Range les MAE positives dans `scores` (clés `\"ridge\"`, `\"foret\"`, `\"boosting\"`), ajoute la clé `\"baseline\"` (MAE obtenue en prédisant toujours la moyenne de `y_train`, calculée sur `y_train`), et crée `retenu`, la clé du meilleur modèle hors baseline.",
   "import pandas as pd\nfrom immo import charger\nfrom sklearn.model_selection import train_test_split, cross_val_score\nfrom sklearn.compose import ColumnTransformer\nfrom sklearn.pipeline import make_pipeline\nfrom sklearn.impute import SimpleImputer\nfrom sklearn.preprocessing import StandardScaler, OneHotEncoder\nfrom sklearn.linear_model import Ridge\nfrom sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor\n\ndf = charger(); df = df[df.prix / df.surface <= 20000]\nX, y = df.drop(columns=\"prix\"), df[\"prix\"]\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\nNUM = [\"surface\", \"pieces\", \"etage\", \"ascenseur\", \"annee_construction\", \"distance_metro_m\", \"balcon\"]\npre = ColumnTransformer([(\"num\", make_pipeline(SimpleImputer(strategy=\"median\"), StandardScaler()), NUM),\n                         (\"cat\", OneHotEncoder(handle_unknown=\"ignore\", sparse_output=False), [\"quartier\", \"dpe\"])])\n",
   "import pandas as pd\nfrom immo import charger\nfrom sklearn.model_selection import train_test_split, cross_val_score\nfrom sklearn.compose import ColumnTransformer\nfrom sklearn.pipeline import make_pipeline\nfrom sklearn.impute import SimpleImputer\nfrom sklearn.preprocessing import StandardScaler, OneHotEncoder\nfrom sklearn.linear_model import Ridge\nfrom sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor\n\ndf = charger(); df = df[df.prix / df.surface <= 20000]\nX, y = df.drop(columns=\"prix\"), df[\"prix\"]\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\nNUM = [\"surface\", \"pieces\", \"etage\", \"ascenseur\", \"annee_construction\", \"distance_metro_m\", \"balcon\"]\npre = ColumnTransformer([(\"num\", make_pipeline(SimpleImputer(strategy=\"median\"), StandardScaler()), NUM),\n                         (\"cat\", OneHotEncoder(handle_unknown=\"ignore\", sparse_output=False), [\"quartier\", \"dpe\"])])\n\nmodeles = {\"ridge\": Ridge(alpha=10), \"foret\": RandomForestRegressor(n_estimators=100, random_state=0),\n           \"boosting\": HistGradientBoostingRegressor(random_state=0)}\nscores = {nom: -cross_val_score(make_pipeline(pre, m), X_train, y_train, cv=5, scoring=\"neg_mean_absolute_error\").mean()\n          for nom, m in modeles.items()}\nscores[\"baseline\"] = (y_train - y_train.mean()).abs().mean()\nretenu = min((k for k in scores if k != \"baseline\"), key=scores.get)\nprint({k: round(v) for k, v in scores.items()}, retenu)\n",
   r'''assert set(scores) == {"ridge", "foret", "boosting", "baseline"}, f"Clés de scores : {set(scores)}."
assert abs(scores["baseline"] - (y_train - y_train.mean()).abs().mean()) < 1, "La baseline prédit toujours la moyenne de y_train."
assert all(scores[k] < scores["baseline"] / 2 for k in ["ridge", "foret", "boosting"]), "Les trois modèles doivent largement battre la baseline : vérifie le signe des scores."
assert retenu == min(["ridge", "foret", "boosting"], key=scores.get) == "boosting", f"retenu vaut {retenu!r}."
''',
   "Un dictionnaire de modèles, une compréhension avec make_pipeline(pre, m) et cross_val_score sur X_train seulement."),
 E("e-pml-c", "L'évaluation finale",
   "Entraîne la pipeline `pre` + `HistGradientBoostingRegressor(random_state=0)` sur tout `X_train`, puis calcule sur `X_test` : `mae_test` (erreur absolue moyenne en euros) et `erreur_mediane_pct` (la médiane de l'erreur absolue **en pourcentage du prix réel**).",
   "import numpy as np\nimport pandas as pd\nfrom immo import charger\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.compose import ColumnTransformer\nfrom sklearn.pipeline import make_pipeline\nfrom sklearn.impute import SimpleImputer\nfrom sklearn.preprocessing import StandardScaler, OneHotEncoder\nfrom sklearn.ensemble import HistGradientBoostingRegressor\n\ndf = charger(); df = df[df.prix / df.surface <= 20000]\nX, y = df.drop(columns=\"prix\"), df[\"prix\"]\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\nNUM = [\"surface\", \"pieces\", \"etage\", \"ascenseur\", \"annee_construction\", \"distance_metro_m\", \"balcon\"]\npre = ColumnTransformer([(\"num\", make_pipeline(SimpleImputer(strategy=\"median\"), StandardScaler()), NUM),\n                         (\"cat\", OneHotEncoder(handle_unknown=\"ignore\", sparse_output=False), [\"quartier\", \"dpe\"])])\n",
   "import numpy as np\nimport pandas as pd\nfrom immo import charger\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.compose import ColumnTransformer\nfrom sklearn.pipeline import make_pipeline\nfrom sklearn.impute import SimpleImputer\nfrom sklearn.preprocessing import StandardScaler, OneHotEncoder\nfrom sklearn.ensemble import HistGradientBoostingRegressor\n\ndf = charger(); df = df[df.prix / df.surface <= 20000]\nX, y = df.drop(columns=\"prix\"), df[\"prix\"]\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\nNUM = [\"surface\", \"pieces\", \"etage\", \"ascenseur\", \"annee_construction\", \"distance_metro_m\", \"balcon\"]\npre = ColumnTransformer([(\"num\", make_pipeline(SimpleImputer(strategy=\"median\"), StandardScaler()), NUM),\n                         (\"cat\", OneHotEncoder(handle_unknown=\"ignore\", sparse_output=False), [\"quartier\", \"dpe\"])])\n\nmodele = make_pipeline(pre, HistGradientBoostingRegressor(random_state=0)).fit(X_train, y_train)\npred = modele.predict(X_test)\nmae_test = np.abs(y_test - pred).mean()\nerreur_mediane_pct = (np.abs(y_test - pred) / y_test * 100).median()\nprint(f\"MAE : {mae_test:,.0f} €  ·  erreur médiane : {erreur_mediane_pct:.1f} %\")\n",
   r'''import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import HistGradientBoostingRegressor
ref = make_pipeline(pre, HistGradientBoostingRegressor(random_state=0)).fit(X_train, y_train).predict(X_test)
assert abs(mae_test - np.abs(y_test - ref).mean()) < 1, f"mae_test vaut {mae_test:.0f}, j'attendais {np.abs(y_test - ref).mean():.0f}."
assert abs(erreur_mediane_pct - (np.abs(y_test - ref) / y_test * 100).median()) < 0.01, "erreur_mediane_pct : médiane de |réel − prédit| / réel × 100."
assert erreur_mediane_pct < 12, "L'erreur médiane devrait être sous 12 %."
''',
   "Entraîne sur X_train, prédis sur X_test. L'erreur en pourcentage vaut |y_test − pred| / y_test × 100 ; prends .median()."),
],
"tasks": [
  "Refaire le projet dans un notebook, avec une analyse exploratoire illustrée",
  "Ajouter un GridSearchCV sur learning_rate et max_iter du boosting",
  "Analyser les 10 plus grosses erreurs : quel quartier, quelle surface ?",
  "Sauvegarder la pipeline avec joblib.dump(modele, \"modele.joblib\")",
  "Publier sur GitHub avec un README en anglais (résultats en haut, baseline comparée)",
]},
]

QUIZZES = {
"quiz-ml2": {"title": "Quiz · Machine learning avancé", "questions": [
 {"q": "Pourquoi mettre le prétraitement dans une pipeline avant la validation croisée ?", "options": ["Pour aller plus vite", "Pour que l'imputation et la mise à l'échelle n'apprennent que sur les données d'entraînement de chaque pli", "Parce que sklearn l'impose", "Pour réduire le nombre de colonnes"], "answer": 1,
  "explain": "Sinon, des statistiques du jeu de validation fuient dans l'entraînement et le score est trop optimiste."},
 {"q": "Quelle différence principale entre Ridge et Lasso ?", "options": ["Ridge est pour la classification", "Lasso peut annuler des coefficients, Ridge les rétrécit seulement", "Lasso n'a pas d'hyperparamètre", "Aucune"], "answer": 1,
  "explain": "La pénalité L1 du Lasso produit des coefficients exactement nuls : il sélectionne des variables."},
 {"q": "Que se passe-t-il si alpha est très grand dans une régression Ridge ?", "options": ["Le modèle surapprend", "Les coefficients tendent vers zéro et le modèle sous-apprend", "Rien", "Le modèle devient non linéaire"], "answer": 1,
  "explain": "La pénalité domine : le modèle devient presque constant."},
 {"q": "Comment une forêt aléatoire réduit-elle le surapprentissage d'un arbre ?", "options": ["En élaguant chaque arbre", "En moyennant de nombreux arbres entraînés sur des échantillons et des variables tirés au hasard", "En utilisant un seul arbre très profond", "En mettant les données à l'échelle"], "answer": 1,
  "explain": "C'est le bagging : les erreurs d'arbres différents se compensent, ce qui réduit la variance."},
 {"q": "Dans le gradient boosting, sur quoi chaque nouvel arbre est-il entraîné ?", "options": ["Sur les données d'origine", "Sur les résidus (erreurs) des arbres précédents", "Sur un échantillon aléatoire de colonnes seulement", "Sur le jeu de test"], "answer": 1,
  "explain": "Chaque arbre corrige ce que l'ensemble précédent n'a pas encore appris."},
 {"q": "Comment séparer entraînement et test pour une série chronologique ?", "options": ["Au hasard, avec train_test_split", "Dans le temps : le passé pour entraîner, la période suivante pour tester", "En prenant un jour sur deux", "Ce n'est pas nécessaire"], "answer": 1,
  "explain": "Mélanger au hasard laisserait le modèle voir le futur : l'évaluation serait faussée."},
 {"q": "Quelle baseline utiliser pour des ventes quotidiennes avec un fort effet week-end ?", "options": ["La moyenne globale", "La saisonnière naïve : même jour la semaine précédente", "Zéro", "Le maximum historique"], "answer": 1,
  "explain": "Elle capture la saisonnalité hebdomadaire : un modèle doit faire mieux pour être utile."},
 {"q": "Pourquoi mettre les variables à l'échelle avant K-means ?", "options": ["Pour accélérer le calcul", "Parce que K-means repose sur des distances : une variable en grandes unités dominerait les autres", "Ce n'est pas nécessaire", "Pour avoir des clusters de même taille"], "answer": 1,
  "explain": "Sans mise à l'échelle, des grammes écrasent des millimètres dans le calcul des distances."},
]},
}
