WEEK = {
"id": "s2", "num": 2,
"title": "NumPy, pandas et visualisation",
"goal": "Explorer un vrai jeu de données de A à Z dans un notebook : charger, nettoyer, transformer, visualiser et conclure.",
"hours": "8 à 10 h",
"lessons": [
# ---------------------------------------------------------------- 2.1
{"id": "l-2-1", "title": "NumPy : calculer sur des tableaux", "minutes": 70,
"body": r'''
**NumPy** est la base de tout le calcul scientifique en Python : pandas, scikit-learn et PyTorch reposent dessus. Son objet central est le **tableau** (`ndarray`) : une grille de nombres du même type, sur laquelle les calculs sont très rapides.

```python
import numpy as np

a = np.array([3.0, 8.0, 1.0, 6.0])
print(a * 2)          # l'opération s'applique à chaque élément
print(a + 10)
print(a.mean(), a.std(), a.max())
```

Ce calcul **élément par élément** sans boucle s'appelle la **vectorisation**. C'est à la fois plus court et des dizaines de fois plus rapide qu'une boucle `for`.

## Forme et dimensions

```python
M = np.array([[1, 2, 3],
              [4, 5, 6]])
print(M.shape)        # (2, 3) : 2 lignes, 3 colonnes
print(M.ndim, M.dtype)
print(M[0, 2])        # ligne 0, colonne 2
print(M[:, 1])        # toute la colonne 1
print(M.sum(axis=0))  # somme de chaque colonne
print(M.sum(axis=1))  # somme de chaque ligne
```

`axis=0` agrège **le long des lignes** (un résultat par colonne), `axis=1` le long des colonnes (un résultat par ligne). En ML, une ligne est un exemple et une colonne une caractéristique.

## Créer des tableaux

```python
print(np.zeros(3), np.ones((2, 2)))
print(np.arange(0, 10, 2))          # comme range
print(np.linspace(0, 1, 5))         # 5 points régulièrement espacés
rng = np.random.default_rng(42)     # générateur aléatoire reproductible
print(rng.normal(0, 1, size=3))
```

## Les masques booléens

Une comparaison renvoie un tableau de `True`/`False`, qu'on peut utiliser pour **filtrer**. C'est exactement ce que tu feras avec pandas.

```python
notes = np.array([12, 7, 15, 9, 18])
masque = notes >= 10
print(masque)
print(notes[masque])              # les notes >= 10
print(notes[(notes > 8) & (notes < 16)])   # & = et, | = ou, avec des parenthèses
print(masque.mean())              # proportion de True
```

## Le broadcasting

NumPy sait combiner des tableaux de formes différentes en « étirant » le plus petit. Exemple : centrer chaque colonne d'une matrice en soustrayant sa moyenne.

```python
X = np.array([[1.0, 200.0],
              [3.0, 400.0],
              [5.0, 600.0]])
moyennes = X.mean(axis=0)     # forme (2,)
X_centre = X - moyennes       # (3, 2) - (2,) : la ligne est répétée
X_centre
```

> **À retenir** : pense « tableau entier » plutôt que « boucle ». Si tu écris une boucle `for` sur les éléments d'un tableau NumPy, il existe presque toujours une version vectorisée.
''',
"exercises": [
 {"id": "e-2-1-a", "title": "Normalisation min-max vectorisée",
  "prompt": "Sans boucle, crée `x_norm` : les valeurs de `x` ramenées entre 0 et 1 avec `(x - min) / (max - min)`.",
  "starter": "import numpy as np\nx = np.array([4.0, 10.0, 7.0, 1.0, 13.0])\n",
  "solution": "import numpy as np\nx = np.array([4.0, 10.0, 7.0, 1.0, 13.0])\nx_norm = (x - x.min()) / (x.max() - x.min())\nx_norm\n",
  "hint": "x.min() et x.max() renvoient des nombres ; l'opération s'applique ensuite à tout le tableau.",
  "check": 'import numpy as np\nassert isinstance(x_norm, np.ndarray), "x_norm doit être un tableau NumPy."\nassert np.allclose(x_norm, [0.25, 0.75, 0.5, 0.0, 1.0]), f"x_norm vaut {x_norm}."\n'},
 {"id": "e-2-1-b", "title": "Filtrer avec un masque",
  "prompt": "Le tableau `latences` contient des temps de réponse d'une API en millisecondes. Crée `lentes`, les latences strictement supérieures à 200, et `part_lentes`, leur proportion (entre 0 et 1).",
  "starter": "import numpy as np\nlatences = np.array([120, 340, 95, 210, 180, 600, 150, 205])\n",
  "solution": "import numpy as np\nlatences = np.array([120, 340, 95, 210, 180, 600, 150, 205])\nlentes = latences[latences > 200]\npart_lentes = (latences > 200).mean()\nprint(lentes, part_lentes)\n",
  "hint": "latences > 200 est un masque. La moyenne d'un masque donne la proportion de True.",
  "check": 'import numpy as np\nassert list(lentes) == [340, 210, 600, 205], f"lentes vaut {lentes}."\nassert abs(part_lentes - 0.5) < 1e-9, f"part_lentes vaut {part_lentes}."\n'},
 {"id": "e-2-1-c", "title": "Standardiser les colonnes",
  "prompt": "Standardise chaque **colonne** de `X` : soustrais sa moyenne et divise par son écart-type (`axis=0`). Stocke le résultat dans `X_std`. Chaque colonne de `X_std` doit avoir une moyenne de 0 et un écart-type de 1.",
  "starter": "import numpy as np\nX = np.array([[170, 65], [180, 80], [160, 55], [175, 72]], dtype=float)\n",
  "solution": "import numpy as np\nX = np.array([[170, 65], [180, 80], [160, 55], [175, 72]], dtype=float)\nX_std = (X - X.mean(axis=0)) / X.std(axis=0)\nprint(X_std.mean(axis=0).round(6), X_std.std(axis=0))\n",
  "hint": "X.mean(axis=0) et X.std(axis=0) donnent une valeur par colonne ; le broadcasting fait le reste.",
  "check": 'import numpy as np\nassert X_std.shape == (4, 2), f"X_std a la forme {X_std.shape}, j\'attendais (4, 2)."\nassert np.allclose(X_std.mean(axis=0), 0) and np.allclose(X_std.std(axis=0), 1), "Chaque colonne doit avoir une moyenne 0 et un écart-type 1 : as-tu bien utilisé axis=0 ?"\n'},
]},
# ---------------------------------------------------------------- 2.2
{"id": "l-2-2", "title": "pandas : charger et explorer", "minutes": 75,
"body": r'''
**pandas** manipule des tableaux de données avec des colonnes nommées : les **DataFrame**. Chaque colonne est une **Series**. C'est l'outil que tu utiliseras le plus pendant la formation.

```python
import pandas as pd

df = pd.read_csv("penguins.csv")
df.head()
```

## Les premiers réflexes sur un nouveau jeu de données

```python
print(df.shape)          # (lignes, colonnes)
print(df.columns.tolist())
df.info()                # types et valeurs non nulles par colonne
```

```python
df.describe()            # statistiques des colonnes numériques
```

```python
df["species"].value_counts()    # effectifs par catégorie
```

## Sélectionner des colonnes et des lignes

```python
df["body_mass_g"]                      # une colonne : une Series
df[["species", "body_mass_g"]]         # plusieurs colonnes : un DataFrame
```

`loc` sélectionne par **étiquettes** (noms de lignes et de colonnes), `iloc` par **positions** numériques.

```python
print(df.loc[0, "species"])            # ligne d'étiquette 0, colonne species
print(df.iloc[0, 0])                   # première ligne, première colonne
df.loc[:4, ["island", "sex"]]          # avec loc, la borne de fin est incluse
```

## Filtrer avec des conditions

Même principe que les masques NumPy. Les parenthèses sont obligatoires autour de chaque condition.

```python
lourds = df[df["body_mass_g"] > 5500]
print(len(lourds), "manchots de plus de 5,5 kg")
gentoo_femelles = df[(df["species"] == "Gentoo") & (df["sex"] == "FEMALE")]
gentoo_femelles.head(3)
```

```python
df[df["island"].isin(["Dream", "Biscoe"])].shape
```

## Trier

```python
df.sort_values("flipper_length_mm", ascending=False).head(3)
```

> **À retenir** : `df[...]` avec une **chaîne** sélectionne une colonne ; avec un **masque booléen**, il filtre des lignes. Pour combiner des conditions, utilise `&` et `|` (pas `and`/`or`), avec des parenthèses.
''',
"exercises": [
 {"id": "e-2-2-a", "title": "Premiers chiffres",
  "prompt": "Charge `penguins.csv` dans `df`. Crée `n_lignes` (nombre de lignes), `n_gentoo` (nombre de manchots de l'espèce Gentoo) et `ile_max` (le nom de l'île qui compte le plus de manchots).",
  "starter": "import pandas as pd\n",
  "solution": 'import pandas as pd\ndf = pd.read_csv("penguins.csv")\nn_lignes = len(df)\nn_gentoo = (df["species"] == "Gentoo").sum()\nile_max = df["island"].value_counts().idxmax()\nprint(n_lignes, n_gentoo, ile_max)\n',
  "hint": "len(df) ou df.shape[0]. value_counts() trie par effectif ; .idxmax() ou .index[0] donne la catégorie la plus fréquente.",
  "check": 'assert n_lignes == 344, f"n_lignes vaut {n_lignes}."\nassert n_gentoo == 124, f"n_gentoo vaut {n_gentoo}."\nassert ile_max == "Biscoe", f"ile_max vaut {ile_max!r}."\n'},
 {"id": "e-2-2-b", "title": "Filtre combiné",
  "prompt": "Crée `selection` : les manchots de l'île `Dream` dont le bec (`bill_length_mm`) mesure plus de 45 mm, avec seulement les colonnes `species`, `bill_length_mm` et `sex`, triés par longueur de bec décroissante.",
  "starter": 'import pandas as pd\ndf = pd.read_csv("penguins.csv")\n',
  "solution": 'import pandas as pd\ndf = pd.read_csv("penguins.csv")\nselection = (\n    df[(df["island"] == "Dream") & (df["bill_length_mm"] > 45)]\n    [["species", "bill_length_mm", "sex"]]\n    .sort_values("bill_length_mm", ascending=False)\n)\nselection.head()\n',
  "hint": "Filtre d'abord avec deux conditions et &, puis sélectionne les colonnes avec [[...]], puis sort_values(..., ascending=False).",
  "check": 'import pandas as pd\nref = pd.read_csv("penguins.csv")\nref = ref[(ref.island == "Dream") & (ref.bill_length_mm > 45)][["species", "bill_length_mm", "sex"]].sort_values("bill_length_mm", ascending=False)\nassert list(selection.columns) == ["species", "bill_length_mm", "sex"], f"Colonnes : {list(selection.columns)}."\nassert len(selection) == len(ref), f"selection a {len(selection)} lignes, j\'en attendais {len(ref)}."\nassert list(selection["bill_length_mm"]) == list(ref["bill_length_mm"]), "L\'ordre n\'est pas le bon : trie par bill_length_mm décroissant."\n'},
]},
# ---------------------------------------------------------------- 2.3
{"id": "l-2-3", "title": "Nettoyer les données", "minutes": 70,
"body": r'''
En pratique, le nettoyage prend une grande partie du temps d'un projet data. Un modèle entraîné sur des données sales donne des résultats faux, sans forcément lever d'erreur.

## Les valeurs manquantes

```python
import pandas as pd
df = pd.read_csv("penguins.csv")
df.isna().sum()          # nombre de valeurs manquantes par colonne
```

Trois stratégies, selon le contexte :

```python
sans_na = df.dropna()                                     # 1. supprimer les lignes incomplètes
print(len(df), "→", len(sans_na))

df_imp = df.copy()
mediane = df_imp["body_mass_g"].median()
df_imp["body_mass_g"] = df_imp["body_mass_g"].fillna(mediane)   # 2. imputer (médiane, moyenne...)

df_sub = df.dropna(subset=["sex"])                        # 3. supprimer seulement si une colonne précise manque
print(df_imp["body_mass_g"].isna().sum(), len(df_sub))
```

La **médiane** est souvent préférée à la moyenne pour imputer, car elle est moins sensible aux valeurs extrêmes.

## Les doublons

```python
doublons = pd.concat([df.head(3), df.head(3)])
print(doublons.duplicated().sum())
doublons.drop_duplicates()
```

## Types, noms de colonnes et texte

```python
propre = df.rename(columns={"bill_length_mm": "bec_mm", "body_mass_g": "masse_g"})
propre["sex"] = propre["sex"].str.lower()            # méthodes texte avec .str
propre["species"] = propre["species"].astype("category")
propre.dtypes
```

## Les dates

```python
ventes = pd.DataFrame({"date": ["2026-01-05", "2026-02-17", "2026-02-28"], "montant": [120, 80, 200]})
ventes["date"] = pd.to_datetime(ventes["date"])
ventes["mois"] = ventes["date"].dt.month
ventes
```

> **À retenir** : ne modifie jamais tes données brutes. Travaille sur une copie (`df.copy()`) et note chaque choix de nettoyage : tu devras le justifier dans tes projets.
''',
"exercises": [
 {"id": "e-2-3-a", "title": "Nettoyer penguins",
  "prompt": "À partir de `df`, crée `propre` : supprime les lignes où `sex` manque, puis remplace les valeurs manquantes restantes de chaque colonne numérique par la **médiane** de cette colonne. Il ne doit plus rester aucune valeur manquante.",
  "starter": 'import pandas as pd\ndf = pd.read_csv("penguins.csv")\n',
  "solution": 'import pandas as pd\ndf = pd.read_csv("penguins.csv")\npropre = df.dropna(subset=["sex"]).copy()\nfor col in ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]:\n    propre[col] = propre[col].fillna(propre[col].median())\nprint(propre.isna().sum().sum(), len(propre))\n',
  "hint": "dropna(subset=[\"sex\"]), puis une boucle sur les colonnes numériques avec fillna(...median()).",
  "check": 'assert propre.isna().sum().sum() == 0, "Il reste des valeurs manquantes."\nassert len(propre) == 333, f"propre a {len(propre)} lignes, j\'en attendais 333 (on retire seulement les lignes sans sex)."\n'},
 {"id": "e-2-3-b", "title": "Uniformiser du texte",
  "prompt": "Les villes de `clients` ont été saisies n'importe comment. Crée la colonne `ville_propre` : sans espaces au début et à la fin, avec une majuscule en début de mot (`.str.strip()` puis `.str.title()`). Puis crée `n_villes`, le nombre de villes distinctes après nettoyage.",
  "starter": 'import pandas as pd\nclients = pd.DataFrame({"ville": ["paris", " Lyon", "PARIS ", "lyon", "Marseille", "marseille  "]})\n',
  "solution": 'import pandas as pd\nclients = pd.DataFrame({"ville": ["paris", " Lyon", "PARIS ", "lyon", "Marseille", "marseille  "]})\nclients["ville_propre"] = clients["ville"].str.strip().str.title()\nn_villes = clients["ville_propre"].nunique()\nprint(clients, n_villes)\n',
  "hint": "Enchaîne les méthodes : .str.strip().str.title(). nunique() compte les valeurs distinctes.",
  "check": 'assert list(clients["ville_propre"]) == ["Paris", "Lyon", "Paris", "Lyon", "Marseille", "Marseille"], f"ville_propre vaut {list(clients[\'ville_propre\'])}."\nassert n_villes == 3, f"n_villes vaut {n_villes}."\n'},
]},
# ---------------------------------------------------------------- 2.4
{"id": "l-2-4", "title": "Transformer : colonnes, groupby, pivot, merge", "minutes": 80,
"body": r'''
On utilise ici `tips.csv` : 244 additions d'un restaurant, avec le montant (`total_bill`), le pourboire (`tip`), le jour, le service (`Lunch`, `Dinner`), la taille de la table (`size`).

## Créer des colonnes

```python
import pandas as pd
tips = pd.read_csv("tips.csv")
tips["tip_pct"] = tips["tip"] / tips["total_bill"] * 100
tips["grande_table"] = tips["size"] >= 4
tips["service_fr"] = tips["time"].map({"Lunch": "Déjeuner", "Dinner": "Dîner"})
tips.head()
```

`pd.cut` découpe une variable numérique en tranches :

```python
tips["tranche"] = pd.cut(tips["total_bill"], bins=[0, 15, 30, 60], labels=["< 15 $", "15–30 $", "> 30 $"])
tips["tranche"].value_counts()
```

## groupby : agréger par groupe

C'est l'opération la plus utile de pandas : **découper** en groupes, **appliquer** un calcul, **combiner** les résultats.

```viz groupby
```

```python
tips.groupby("day")["tip_pct"].mean().round(1)
```

```python
tips.groupby(["day", "time"]).agg(
    nb=("tip", "size"),
    pourboire_moyen=("tip", "mean"),
    addition_max=("total_bill", "max"),
).round(2)
```

## pivot_table : un tableau croisé

```python
pd.pivot_table(tips, values="tip_pct", index="day", columns="smoker", aggfunc="mean").round(1)
```

## merge : joindre deux tables

Comme une jointure SQL : on associe les lignes de deux tables qui partagent une clé.

```python
jours = pd.DataFrame({"day": ["Thur", "Fri", "Sat", "Sun"],
                      "jour": ["Jeudi", "Vendredi", "Samedi", "Dimanche"],
                      "week_end": [False, False, True, True]})
fusion = tips.merge(jours, on="day", how="left")
fusion.groupby("week_end")["tip_pct"].mean().round(2)
```

`how="left"` garde toutes les lignes de la table de gauche ; `inner` ne garde que les correspondances ; `outer` garde tout.

> **À retenir** : `groupby` + `agg` répond à la plupart des questions métier du type « quel est le X moyen par Y ? ». Entraîne-toi à traduire une question en phrase pandas.
''',
"exercises": [
 {"id": "e-2-4-a", "title": "Pourboire moyen par jour",
  "prompt": "Ajoute à `tips` la colonne `tip_pct` (pourboire en % de l'addition). Crée la Series `par_jour` : le `tip_pct` moyen par jour (`day`), triée par ordre **décroissant**. Puis `meilleur_jour`, le jour au pourboire moyen le plus élevé.",
  "starter": 'import pandas as pd\ntips = pd.read_csv("tips.csv")\n',
  "solution": 'import pandas as pd\ntips = pd.read_csv("tips.csv")\ntips["tip_pct"] = tips["tip"] / tips["total_bill"] * 100\npar_jour = tips.groupby("day")["tip_pct"].mean().sort_values(ascending=False)\nmeilleur_jour = par_jour.index[0]\npar_jour\n',
  "hint": "groupby(\"day\")[\"tip_pct\"].mean() puis .sort_values(ascending=False). Le premier index est le meilleur jour.",
  "check": 'import pandas as pd\nassert "tip_pct" in tips.columns, "Il manque la colonne tip_pct."\nassert list(par_jour.index) == ["Fri", "Sun", "Thur", "Sat"], f"Ordre obtenu : {list(par_jour.index)}."\nassert meilleur_jour == "Fri", f"meilleur_jour vaut {meilleur_jour!r}."\nassert abs(par_jour["Fri"] - 16.99) < 0.01, f"Pour Fri, j\'attendais environ 16.99 %, tu as {par_jour[\'Fri\']:.2f}."\n'},
 {"id": "e-2-4-b", "title": "Tableau de synthèse",
  "prompt": "Crée `synthese` avec un `groupby` sur `time` et `agg` : une colonne `nb` (nombre d'additions), `addition_moy` (moyenne de `total_bill`) et `table_moy` (moyenne de `size`).",
  "starter": 'import pandas as pd\ntips = pd.read_csv("tips.csv")\n',
  "solution": 'import pandas as pd\ntips = pd.read_csv("tips.csv")\nsynthese = tips.groupby("time").agg(\n    nb=("total_bill", "size"),\n    addition_moy=("total_bill", "mean"),\n    table_moy=("size", "mean"),\n)\nsynthese.round(2)\n',
  "hint": "Syntaxe : .agg(nom_colonne=(\"colonne_source\", \"fonction\")).",
  "check": 'assert set(["nb", "addition_moy", "table_moy"]) <= set(synthese.columns), f"Colonnes : {list(synthese.columns)}."\nassert synthese.loc["Dinner", "nb"] == 176 and synthese.loc["Lunch", "nb"] == 68, "Les effectifs par service ne sont pas les bons."\nassert abs(synthese.loc["Dinner", "addition_moy"] - 20.797) < 0.01, "addition_moy pour Dinner devrait valoir environ 20.80."\n'},
 {"id": "e-2-4-c", "title": "Jointure",
  "prompt": "Joins `commandes` et `produits` sur `produit_id` pour obtenir `fusion`, puis calcule `ca_par_categorie` : la somme de `quantite * prix` par `categorie`.",
  "starter": 'import pandas as pd\ncommandes = pd.DataFrame({"produit_id": [1, 2, 1, 3, 2], "quantite": [2, 1, 5, 3, 2]})\nproduits = pd.DataFrame({"produit_id": [1, 2, 3], "categorie": ["livre", "cours", "livre"], "prix": [30, 200, 45]})\n',
  "solution": 'import pandas as pd\ncommandes = pd.DataFrame({"produit_id": [1, 2, 1, 3, 2], "quantite": [2, 1, 5, 3, 2]})\nproduits = pd.DataFrame({"produit_id": [1, 2, 3], "categorie": ["livre", "cours", "livre"], "prix": [30, 200, 45]})\nfusion = commandes.merge(produits, on="produit_id")\nfusion["ca"] = fusion["quantite"] * fusion["prix"]\nca_par_categorie = fusion.groupby("categorie")["ca"].sum()\nca_par_categorie\n',
  "hint": "commandes.merge(produits, on=\"produit_id\"), puis une colonne ca, puis groupby.",
  "check": 'assert len(fusion) == 5, f"fusion a {len(fusion)} lignes, j\'en attendais 5."\nassert dict(ca_par_categorie) == {"cours": 600, "livre": 345}, f"ca_par_categorie vaut {dict(ca_par_categorie)}."\n'},
]},
# ---------------------------------------------------------------- 2.5
{"id": "l-2-5", "title": "Visualiser avec Plotly Express", "minutes": 70,
"body": r'''
Chez Jedha, les graphiques se font avec **Plotly Express** : une ligne de code par graphique, et des graphiques interactifs (survol, zoom). Ici, tu disposes d'une **version simplifiée** qui accepte la même syntaxe pour `scatter`, `histogram`, `box`, `bar` et `line`. Sur ton ordinateur, le même code fonctionne avec la vraie bibliothèque.

## Choisir le bon graphique

- **Distribution** d'une variable numérique → `histogram` ou `box`.
- **Relation** entre deux variables numériques → `scatter`.
- **Comparaison** d'une valeur entre catégories → `bar`.
- **Évolution** dans le temps ou au fil des itérations → `line`.

## Histogramme

```python
import pandas as pd
import plotly.express as px

df = pd.read_csv("penguins.csv")
fig = px.histogram(df, x="body_mass_g", nbins=30, title="Distribution de la masse des manchots")
fig.show()
```

Ajoute `color=` pour séparer les groupes :

```python
px.histogram(df, x="flipper_length_mm", color="species", barmode="overlay",
             title="Longueur des nageoires par espèce")
```

## Nuage de points

```python
px.scatter(df, x="flipper_length_mm", y="body_mass_g", color="species",
           labels={"flipper_length_mm": "Nageoire (mm)", "body_mass_g": "Masse (g)"},
           title="Plus la nageoire est longue, plus le manchot est lourd")
```

## Boîte à moustaches

Elle montre la médiane, les quartiles et les valeurs extrêmes : idéale pour comparer des distributions.

```python
px.box(df, x="species", y="bill_depth_mm", title="Épaisseur du bec par espèce")
```

## Diagramme en barres

On agrège d'abord avec pandas, puis on trace.

```python
moy = df.groupby("species", as_index=False)["body_mass_g"].mean()
px.bar(moy, x="species", y="body_mass_g", title="Masse moyenne par espèce (g)")
```

> **À retenir** : un bon titre de graphique énonce la **conclusion** (« Les Gentoo sont les plus lourds »), pas seulement le contenu (« Masse par espèce »). Nomme toujours tes axes avec leurs unités.
''',
"exercises": [
 {"id": "e-2-5-a", "title": "Pourboire contre addition",
  "prompt": "Avec `tips.csv`, crée une figure `fig` : un nuage de points du pourboire (`tip`, en y) en fonction de l'addition (`total_bill`, en x), coloré par `time`, avec un titre. Affiche-la.",
  "starter": 'import pandas as pd\nimport plotly.express as px\ntips = pd.read_csv("tips.csv")\n',
  "solution": 'import pandas as pd\nimport plotly.express as px\ntips = pd.read_csv("tips.csv")\nfig = px.scatter(tips, x="total_bill", y="tip", color="time",\n                 title="Le pourboire augmente avec l\'addition")\nfig.show()\n',
  "hint": "px.scatter(tips, x=..., y=..., color=..., title=...)",
  "check": 'assert getattr(fig, "_is_px_fig", False) or hasattr(fig, "data"), "fig doit être une figure Plotly Express."\nassert fig.data[0]["type"] == "scatter", "Il faut un nuage de points (px.scatter)."\nassert len(fig.data) == 2, "Colore par time : il doit y avoir 2 groupes (Lunch et Dinner)."\nassert fig.layout.get("title"), "Ajoute un titre avec title=..."\n'},
 {"id": "e-2-5-b", "title": "Taux de survie par classe",
  "prompt": "Avec `titanic.csv`, calcule le taux de survie moyen par `pclass` dans un DataFrame `taux` (avec `as_index=False`), puis trace `fig`, un diagramme en barres de ce taux par classe.",
  "starter": 'import pandas as pd\nimport plotly.express as px\ntitanic = pd.read_csv("titanic.csv")\n',
  "solution": 'import pandas as pd\nimport plotly.express as px\ntitanic = pd.read_csv("titanic.csv")\ntaux = titanic.groupby("pclass", as_index=False)["survived"].mean()\nfig = px.bar(taux, x="pclass", y="survived", title="La 1re classe a le meilleur taux de survie",\n             labels={"pclass": "Classe", "survived": "Taux de survie"})\nfig.show()\n',
  "hint": "La moyenne d'une colonne 0/1 est un taux. Puis px.bar(taux, x=\"pclass\", y=\"survived\").",
  "check": 'assert len(taux) == 3, "taux doit avoir une ligne par classe."\nassert fig.data[0]["type"] == "bar", "Il faut un diagramme en barres (px.bar)."\nassert abs(max(fig.data[0]["y"]) - 0.6296) < 0.001, "Les hauteurs des barres ne correspondent pas aux taux de survie."\n'},
]},
# ---------------------------------------------------------------- 2.6
{"id": "l-2-6", "title": "Repérer anomalies et biais", "minutes": 50,
"body": r'''
Avant de modéliser, il faut se demander si les données sont **fiables** et **représentatives**. Un modèle reproduit fidèlement les défauts des données sur lesquelles il apprend.

## Les valeurs aberrantes (outliers)

La méthode de l'**écart interquartile** (IQR) est la plus courante : une valeur est suspecte si elle s'éloigne de plus de 1,5 IQR des quartiles.

```python
import pandas as pd
tips = pd.read_csv("tips.csv")
q1, q3 = tips["total_bill"].quantile([0.25, 0.75])
iqr = q3 - q1
bas, haut = q1 - 1.5 * iqr, q3 + 1.5 * iqr
aberrants = tips[(tips["total_bill"] < bas) | (tips["total_bill"] > haut)]
print(f"Bornes : [{bas:.2f} ; {haut:.2f}] → {len(aberrants)} valeurs suspectes")
```

Une valeur aberrante n'est pas forcément une erreur : une grosse addition est possible. On la vérifie, puis on décide de la garder, de la corriger ou de l'exclure, et on documente ce choix.

## Le z-score

Le z-score mesure à combien d'écarts-types une valeur se trouve de la moyenne. Au-delà de 3 en valeur absolue, elle est rare pour une distribution normale.

```python
z = (tips["tip"] - tips["tip"].mean()) / tips["tip"].std()
tips[z.abs() > 3][["total_bill", "tip"]]
```

## Le déséquilibre des classes

```python
titanic = pd.read_csv("titanic.csv")
titanic["survived"].value_counts(normalize=True).round(3)
```

Si 95 % des transactions sont légitimes, un modèle qui répond toujours « légitime » a 95 % d'exactitude, tout en étant inutile. Il faut le savoir **avant** d'évaluer un modèle (semaine 4).

## Les biais à garder en tête

- **Biais d'échantillonnage** : les données ne représentent pas la population visée (par exemple, un sondage fait uniquement en ligne).
- **Biais historique** : les données reflètent des décisions passées injustes, que le modèle va reproduire.
- **Fuite de données** : une colonne contient indirectement la réponse. Dans `titanic.csv`, la colonne `alive` est la même information que `survived` : l'utiliser pour prédire la survie serait tricher.
- **Corrélation n'est pas causalité** : deux variables peuvent évoluer ensemble à cause d'une troisième.

```python
pd.crosstab(titanic["survived"], titanic["alive"])
```

> **À retenir** : pour chaque jeu de données, pose-toi trois questions. Qui a collecté ces données, et comment ? Qui en est absent ? Quelle colonne ne sera pas disponible au moment de la prédiction ?
''',
"exercises": [
 {"id": "e-2-6-a", "title": "Une fonction de détection",
  "prompt": "Écris `outliers_iqr(serie)` qui renvoie un **masque booléen** (une Series de True/False) indiquant les valeurs hors de `[Q1 - 1.5 IQR ; Q3 + 1.5 IQR]`. Puis crée `n_outliers`, le nombre de valeurs aberrantes de `tips[\"tip\"]`.",
  "starter": 'import pandas as pd\ntips = pd.read_csv("tips.csv")\n\ndef outliers_iqr(serie):\n    pass\n',
  "solution": 'import pandas as pd\ntips = pd.read_csv("tips.csv")\n\ndef outliers_iqr(serie):\n    q1, q3 = serie.quantile([0.25, 0.75])\n    iqr = q3 - q1\n    return (serie < q1 - 1.5 * iqr) | (serie > q3 + 1.5 * iqr)\n\nn_outliers = outliers_iqr(tips["tip"]).sum()\nprint(n_outliers)\n',
  "hint": "Reprends le code de la leçon, mais renvoie le masque au lieu de filtrer.",
  "check": 'import pandas as pd\nm = outliers_iqr(tips["tip"])\nassert m is not None and m.dtype == bool, "outliers_iqr doit renvoyer une Series booléenne."\nassert n_outliers == 9, f"n_outliers vaut {n_outliers}, j\'attendais 9."\nassert outliers_iqr(pd.Series([1, 2, 3, 4, 100])).tolist() == [False, False, False, False, True], "Teste ta fonction sur [1, 2, 3, 4, 100] : seul 100 est aberrant."\n'},
 {"id": "e-2-6-b", "title": "Repérer la fuite de données",
  "prompt": "Parmi les colonnes de `titanic.csv`, une colonne textuelle répète exactement l'information de `survived`. Mets son nom dans la variable `colonne_fuite`, puis crée `features_ok` : la liste des colonnes **sans** `survived` et sans cette colonne.",
  "starter": 'import pandas as pd\ntitanic = pd.read_csv("titanic.csv")\nprint(titanic.columns.tolist())\n',
  "solution": 'import pandas as pd\ntitanic = pd.read_csv("titanic.csv")\ncolonne_fuite = "alive"\nfeatures_ok = [c for c in titanic.columns if c not in ["survived", colonne_fuite]]\nprint(features_ok)\n',
  "hint": "Regarde la colonne qui vaut yes/no. pd.crosstab permet de le confirmer.",
  "check": 'assert colonne_fuite == "alive", f"colonne_fuite vaut {colonne_fuite!r}."\nassert "survived" not in features_ok and "alive" not in features_ok, "features_ok ne doit contenir ni survived ni la colonne de fuite."\nassert len(features_ok) == 13, f"features_ok contient {len(features_ok)} colonnes, j\'en attendais 13."\n'},
]},
],
"project": {
"id": "p-2", "title": "Projet 2 · Analyse exploratoire du Titanic",
"body": r'''
Objectif : produire un notebook d'analyse complet, comme ceux que tu rendras chez Jedha. Pose des questions, réponds avec pandas et des graphiques, et conclus.

Les exercices ci-dessous te guident sur les étapes clés. Reproduis-les ensuite dans un notebook Jupyter sur ton ordinateur, en ajoutant entre chaque étape une cellule de texte qui explique ce que tu observes.
''',
"exercises": [
 {"id": "e-p2-a", "title": "Audit de qualité",
  "prompt": "Charge `titanic.csv` dans `df`. Crée `manquants` : le **pourcentage** de valeurs manquantes par colonne, trié par ordre décroissant, en ne gardant que les colonnes qui en ont.",
  "starter": "import pandas as pd\n",
  "solution": 'import pandas as pd\ndf = pd.read_csv("titanic.csv")\nmanquants = (df.isna().mean() * 100).sort_values(ascending=False)\nmanquants = manquants[manquants > 0].round(1)\nmanquants\n',
  "hint": "df.isna().mean() donne la proportion par colonne. Multiplie par 100, trie, puis filtre > 0.",
  "check": 'assert list(manquants.index[:2]) == ["deck", "age"], f"Les colonnes les plus incomplètes devraient être deck puis age, tu as {list(manquants.index[:2])}."\nassert abs(manquants.iloc[0] - 77.2) < 0.1, f"deck devrait avoir environ 77.2 % de valeurs manquantes."\nassert (manquants > 0).all(), "Ne garde que les colonnes qui ont des valeurs manquantes."\n'},
 {"id": "e-p2-b", "title": "Survie par sexe et par classe",
  "prompt": "Crée `tableau` : un `pivot_table` du taux de survie (`survived`) avec `sex` en lignes et `pclass` en colonnes.",
  "starter": 'import pandas as pd\ndf = pd.read_csv("titanic.csv")\n',
  "solution": 'import pandas as pd\ndf = pd.read_csv("titanic.csv")\ntableau = pd.pivot_table(df, values="survived", index="sex", columns="pclass", aggfunc="mean").round(3)\ntableau\n',
  "hint": "pd.pivot_table(df, values=..., index=..., columns=..., aggfunc=\"mean\")",
  "check": 'assert tableau.shape == (2, 3), f"tableau a la forme {tableau.shape}, j\'attendais (2, 3)."\nassert abs(tableau.loc["female", 1] - 0.968) < 0.001, "Le taux de survie des femmes de 1re classe devrait être d\'environ 0.968."\nassert abs(tableau.loc["male", 3] - 0.135) < 0.001, "Le taux de survie des hommes de 3e classe devrait être d\'environ 0.135."\n'},
 {"id": "e-p2-c", "title": "L'âge des survivants",
  "prompt": "Crée `fig`, un histogramme de `age` coloré par `alive`, avec `barmode=\"overlay\"` et un titre qui énonce ce que tu observes. Puis crée `taux_enfants`, le taux de survie des passagers de moins de 12 ans.",
  "starter": 'import pandas as pd\nimport plotly.express as px\ndf = pd.read_csv("titanic.csv")\n',
  "solution": 'import pandas as pd\nimport plotly.express as px\ndf = pd.read_csv("titanic.csv")\nfig = px.histogram(df, x="age", color="alive", barmode="overlay", nbins=40,\n                   title="Les enfants ont davantage survécu")\nfig.show()\ntaux_enfants = df[df["age"] < 12]["survived"].mean()\nprint(f"Taux de survie des moins de 12 ans : {taux_enfants:.1%}")\n',
  "hint": "px.histogram(df, x=\"age\", color=\"alive\", barmode=\"overlay\"). Puis filtre df[\"age\"] < 12.",
  "check": 'assert fig.data[0]["type"] == "histogram", "fig doit être un histogramme."\nassert len(fig.data) == 2, "Colore par alive : 2 groupes attendus."\nassert abs(taux_enfants - 0.5735) < 0.001, f"taux_enfants vaut {taux_enfants}, j\'attendais environ 0.574."\n'},
],
"tasks": [
  "Refaire l'analyse dans un notebook Jupyter sur ton ordinateur",
  "Poser 5 questions et y répondre, chacune avec un tableau ou un graphique",
  "Écrire une conclusion de 5 lignes maximum",
  "Publier le notebook et un README sur GitHub",
]},
"quiz": [
 {"q": "Que renvoie M.sum(axis=0) pour une matrice M de forme (3, 4) ?", "options": ["Un nombre", "Un tableau de 3 valeurs", "Un tableau de 4 valeurs", "Une matrice (3, 4)"], "answer": 2,
  "explain": "axis=0 agrège le long des lignes : on obtient une valeur par colonne, donc 4 valeurs."},
 {"q": "Comment filtrer les lignes où age > 30 ET sex == 'female' ?", "options": ["df[df.age > 30 and df.sex == 'female']", "df[(df.age > 30) & (df.sex == 'female')]", "df.filter(age > 30, sex='female')", "df[df.age > 30 & df.sex == 'female']"], "answer": 1,
  "explain": "Avec pandas, on combine les masques avec & et |, et chaque condition doit être entre parenthèses."},
 {"q": "Quelle différence entre loc et iloc ?", "options": ["Aucune", "loc utilise les étiquettes, iloc les positions", "iloc est plus rapide", "loc ne fonctionne que sur les colonnes"], "answer": 1,
  "explain": "loc sélectionne par noms d'index et de colonnes, iloc par positions entières (0, 1, 2...)."},
 {"q": "Pourquoi impute-t-on souvent avec la médiane plutôt qu'avec la moyenne ?", "options": ["Elle est plus rapide à calculer", "Elle est moins sensible aux valeurs extrêmes", "Elle est toujours un entier", "La moyenne n'existe pas pour pandas"], "answer": 1,
  "explain": "Quelques valeurs très grandes tirent la moyenne vers le haut, alors que la médiane reste stable."},
 {"q": "Quel graphique choisir pour voir la relation entre deux variables numériques ?", "options": ["Un histogramme", "Un diagramme en barres", "Un nuage de points", "Un camembert"], "answer": 2,
  "explain": "Le nuage de points (scatter) montre comment une variable évolue en fonction de l'autre."},
 {"q": "Que fait df.groupby('day')['tip'].mean() ?", "options": ["La moyenne globale des pourboires", "Le pourboire moyen pour chaque jour", "Le nombre de jours", "Trie le DataFrame par jour"], "answer": 1,
  "explain": "groupby découpe par jour, puis mean calcule la moyenne de tip dans chaque groupe."},
 {"q": "Un modèle de détection de fraude atteint 98 % d'exactitude alors que 98 % des transactions sont légitimes. Qu'en penses-tu ?", "options": ["Excellent modèle", "Il ne fait peut-être pas mieux que de toujours répondre « légitime »", "Il faut l'entraîner moins longtemps", "C'est impossible"], "answer": 1,
  "explain": "Avec des classes déséquilibrées, l'exactitude est trompeuse : il faut regarder la précision et le rappel (semaine 4)."},
 {"q": "Qu'est-ce qu'une fuite de données (data leakage) ?", "options": ["Un piratage de la base", "Une variable qui contient indirectement la réponse à prédire", "Une valeur manquante", "Un fichier CSV trop gros"], "answer": 1,
  "explain": "Une variable qui ne serait pas disponible au moment de la prédiction, ou qui encode la cible, donne des performances trompeuses."},
]}
