WEEK = {
"id": "s3", "num": 3,
"title": "Les maths du machine learning",
"goal": "Comprendre l'intuition derrière les modèles et coder soi-même une régression linéaire par descente de gradient.",
"hours": "8 à 10 h",
"lessons": [
# ---------------------------------------------------------------- 3.1
{"id": "l-3-1", "title": "Statistiques descriptives", "minutes": 60,
"body": r'''
Les statistiques descriptives résument une variable en quelques nombres. Tu les utiliseras dans chaque analyse exploratoire, et elles servent à préparer les données d'un modèle (standardisation).

## Tendance centrale

- **Moyenne** : la somme divisée par le nombre de valeurs. Sensible aux valeurs extrêmes.
- **Médiane** : la valeur du milieu une fois les données triées. Robuste aux extrêmes.

```python
import numpy as np
salaires = np.array([2100, 2300, 2400, 2500, 2600, 15000])
print("moyenne :", salaires.mean())
print("médiane :", np.median(salaires))
```

Un seul salaire très élevé fait monter la moyenne bien au-dessus de ce que gagnent la plupart des gens. C'est pour cela qu'on publie souvent des salaires **médians**.

## Dispersion

La **variance** est la moyenne des carrés des écarts à la moyenne. L'**écart-type** est sa racine carrée, dans la même unité que les données.

```latex
\sigma^2 = \frac{1}{n} \sum_{i=1}^{n} (x_i - \bar{x})^2
```

```python
x = np.array([4.0, 8.0, 6.0, 2.0])
ecarts = x - x.mean()
variance = (ecarts ** 2).mean()
print(variance, np.var(x), np.sqrt(variance), np.std(x))
```

Attention : pandas calcule par défaut la variance **d'échantillon** (division par n − 1), NumPy la variance de population (division par n). L'écart est minime sur de grands jeux de données.

## Quantiles

Les **quartiles** coupent les données triées en quatre parts égales. Q1 = 25 %, Q2 = médiane, Q3 = 75 %.

```python
print(np.percentile(salaires, [25, 50, 75]))
```

## Corrélation

Le **coefficient de corrélation de Pearson** mesure la force d'une relation **linéaire** entre deux variables, de −1 (parfaitement opposées) à +1 (parfaitement liées). Proche de 0 : pas de relation linéaire.

```python
import pandas as pd
df = pd.read_csv("penguins.csv").dropna()
df[["bill_length_mm", "flipper_length_mm", "body_mass_g"]].corr().round(2)
```

> **À retenir** : une corrélation de 0,87 entre la nageoire et la masse dit que les deux augmentent ensemble. Elle ne dit pas que l'une cause l'autre.
''',
"exercises": [
 {"id": "e-3-1-a", "title": "Variance à la main",
  "prompt": "Sans utiliser `np.var` ni `np.std`, calcule `variance` et `ecart_type` (version population, division par n) du tableau `x`, à partir de la formule.",
  "starter": "import numpy as np\nx = np.array([12.0, 15.0, 9.0, 14.0, 10.0])\n",
  "solution": "import numpy as np\nx = np.array([12.0, 15.0, 9.0, 14.0, 10.0])\nmoyenne = x.sum() / len(x)\nvariance = ((x - moyenne) ** 2).sum() / len(x)\necart_type = variance ** 0.5\nprint(variance, ecart_type)\n",
  "hint": "Calcule la moyenne, les écarts au carré, leur moyenne, puis la racine carrée (** 0.5).",
  "check": 'import numpy as np\nassert abs(variance - 5.2) < 1e-9, f"variance vaut {variance}, j\'attendais 5.2."\nassert abs(ecart_type - np.sqrt(5.2)) < 1e-9, f"ecart_type vaut {ecart_type}."\n'},
 {"id": "e-3-1-b", "title": "Quelle variable est la plus liée à la masse ?",
  "prompt": "Dans `penguins.csv` (lignes incomplètes supprimées), calcule `correlations` : la corrélation de chaque colonne numérique avec `body_mass_g`, **sans** `body_mass_g` elle-même. Puis `meilleure`, le nom de la colonne la plus corrélée.",
  "starter": 'import pandas as pd\ndf = pd.read_csv("penguins.csv").dropna()\n',
  "solution": 'import pandas as pd\ndf = pd.read_csv("penguins.csv").dropna()\nnum = df[["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]]\ncorrelations = num.corr()["body_mass_g"].drop("body_mass_g")\nmeilleure = correlations.abs().idxmax()\nprint(correlations.round(3), meilleure)\n',
  "hint": "df[colonnes].corr()[\"body_mass_g\"] donne une Series ; .drop(...) retire une étiquette ; .idxmax() donne l'étiquette du maximum.",
  "check": 'assert "body_mass_g" not in correlations.index, "Retire body_mass_g de correlations."\nassert len(correlations) == 3, f"correlations doit contenir 3 valeurs, elle en a {len(correlations)}."\nassert meilleure == "flipper_length_mm", f"meilleure vaut {meilleure!r}."\n'},
]},
# ---------------------------------------------------------------- 3.2
{"id": "l-3-2", "title": "Probabilités et lois usuelles", "minutes": 70,
"body": r'''
Un modèle de classification ne dit pas « ce mail est un spam ». Il dit « ce mail a 93 % de probabilité d'être un spam ». Les probabilités sont le langage des modèles.

## Les bases

Une probabilité est un nombre entre 0 et 1. La **probabilité conditionnelle** P(A | B) se lit « probabilité de A sachant B » :

```latex
P(A \mid B) = \frac{P(A \cap B)}{P(B)}
```

```python
import pandas as pd
t = pd.read_csv("titanic.csv")
p_survie = t["survived"].mean()
p_survie_si_femme = t[t["sex"] == "female"]["survived"].mean()
print(f"P(survie) = {p_survie:.2f}   P(survie | femme) = {p_survie_si_femme:.2f}")
```

## Le théorème de Bayes

Il permet de « retourner » une probabilité conditionnelle :

```latex
P(A \mid B) = \frac{P(B \mid A)\, P(A)}{P(B)}
```

Exemple classique : une maladie touche 1 % de la population. Un test la détecte dans 99 % des cas, mais se trompe aussi chez 5 % des personnes saines. Si ton test est positif, quelle est la probabilité que tu sois malade ?

```python
p_malade = 0.01
p_pos_si_malade = 0.99
p_pos_si_sain = 0.05
p_pos = p_pos_si_malade * p_malade + p_pos_si_sain * (1 - p_malade)
p_malade_si_pos = p_pos_si_malade * p_malade / p_pos
print(f"{p_malade_si_pos:.1%}")
```

Seulement 17 % ! La maladie est si rare que la plupart des tests positifs sont des faux positifs. C'est la même logique que pour les classes déséquilibrées en ML.

## Simuler pour comprendre

Quand un calcul semble difficile, on peut **simuler**. La **loi des grands nombres** dit que la fréquence observée se rapproche de la probabilité quand on répète l'expérience.

```python
import numpy as np
rng = np.random.default_rng(0)
for n in [10, 100, 10_000]:
    lancers = rng.integers(0, 2, size=n)      # 0 = pile, 1 = face
    print(n, "lancers → fréquence de face :", lancers.mean())
```

## Deux lois à connaître

```viz normal
```

La **loi binomiale** compte les succès sur n essais indépendants de probabilité p. La **loi normale** (courbe en cloche) décrit beaucoup de mesures naturelles. Environ 68 % des valeurs sont à moins d'un écart-type de la moyenne, et 95 % à moins de deux.

```python
normale = rng.normal(loc=170, scale=10, size=100_000)   # tailles : moyenne 170, écart-type 10
print(np.mean(np.abs(normale - 170) < 10))               # environ 0.68
print(np.mean(np.abs(normale - 170) < 20))               # environ 0.95
binom = rng.binomial(n=10, p=0.3, size=100_000)
print(binom.mean())                                       # environ n × p = 3
```

> **À retenir** : la loi normale est partout en ML : initialisation des réseaux de neurones, hypothèses de la régression linéaire, standardisation des données.
''',
"exercises": [
 {"id": "e-3-2-a", "title": "Une fonction Bayes",
  "prompt": "Écris `bayes(prior, sensibilite, faux_positifs)` qui renvoie la probabilité d'être malade sachant un test positif. `prior` = P(malade), `sensibilite` = P(positif | malade), `faux_positifs` = P(positif | sain).",
  "starter": "def bayes(prior, sensibilite, faux_positifs):\n    pass\n\nprint(bayes(0.01, 0.99, 0.05))\n",
  "solution": "def bayes(prior, sensibilite, faux_positifs):\n    p_pos = sensibilite * prior + faux_positifs * (1 - prior)\n    return sensibilite * prior / p_pos\n\nprint(bayes(0.01, 0.99, 0.05))\n",
  "hint": "Calcule d'abord P(positif) en additionnant les deux façons d'être positif.",
  "check": 'assert abs(bayes(0.01, 0.99, 0.05) - 0.16667) < 1e-4, f"bayes(0.01, 0.99, 0.05) renvoie {bayes(0.01, 0.99, 0.05)}, j\'attendais environ 0.1667."\nassert abs(bayes(0.5, 0.9, 0.1) - 0.9) < 1e-9, "Avec prior=0.5, sensibilite=0.9, faux_positifs=0.1, j\'attends 0.9."\n'},
 {"id": "e-3-2-b", "title": "Simuler deux dés",
  "prompt": "Avec `rng`, simule 100 000 lancers de **deux** dés à six faces. Calcule `p_sept`, la fréquence à laquelle leur somme vaut 7. La valeur théorique est 1/6.",
  "starter": "import numpy as np\nrng = np.random.default_rng(1)\n",
  "solution": "import numpy as np\nrng = np.random.default_rng(1)\nde1 = rng.integers(1, 7, size=100_000)\nde2 = rng.integers(1, 7, size=100_000)\np_sept = np.mean(de1 + de2 == 7)\nprint(p_sept, 1 / 6)\n",
  "hint": "rng.integers(1, 7, size=n) tire des entiers de 1 à 6. Additionne les deux tableaux, compare à 7, prends la moyenne.",
  "check": 'assert abs(p_sept - 1 / 6) < 0.01, f"p_sept vaut {p_sept}, loin de 1/6 ≈ 0.1667. Vérifie les bornes de integers (la fin est exclue)."\n'},
]},
# ---------------------------------------------------------------- 3.3
{"id": "l-3-3", "title": "Vecteurs et matrices", "minutes": 70,
"body": r'''
En ML, tout est vecteur ou matrice. Un exemple (un manchot, un passager) est un **vecteur** de caractéristiques. Un jeu de données est une **matrice** X : une ligne par exemple, une colonne par caractéristique.

## Vecteurs

```python
import numpy as np
u = np.array([3.0, 4.0])
v = np.array([1.0, 2.0])
print(u + v, 2 * u)
print("norme de u :", np.linalg.norm(u))     # longueur : racine(3² + 4²) = 5
```

## Le produit scalaire

Le produit scalaire multiplie les composantes deux à deux puis les additionne. C'est l'opération la plus fréquente en ML : une prédiction linéaire est un produit scalaire entre les caractéristiques et les poids.

```latex
u \cdot v = \sum_i u_i v_i
```

```python
print(u @ v, np.dot(u, v), (u * v).sum())   # trois écritures équivalentes : 3×1 + 4×2 = 11
```

La **similarité cosinus** compare la direction de deux vecteurs, entre −1 et 1. C'est elle qui mesure la proximité entre deux textes transformés en vecteurs (embeddings) dans un système RAG.

```latex
\cos(u, v) = \frac{u \cdot v}{\lVert u \rVert \, \lVert v \rVert}
```

## Matrices et produit matriciel

Le produit `A @ B` est possible si le nombre de colonnes de A égale le nombre de lignes de B. Une matrice (n, k) multipliée par une (k, m) donne une (n, m).

```viz matmul
```

```python
X = np.array([[1.0, 2.0],
              [3.0, 4.0],
              [5.0, 6.0]])        # 3 exemples, 2 caractéristiques
w = np.array([0.5, -1.0])         # un poids par caractéristique
b = 2.0
predictions = X @ w + b           # (3, 2) @ (2,) → (3,)
print(predictions)
```

Une seule ligne calcule les prédictions des 3 exemples à la fois. C'est le cœur d'un modèle linéaire et d'une couche de réseau de neurones.

```python
print(X.T)                 # transposée : lignes et colonnes échangées
print(X.T @ X)             # (2, 3) @ (3, 2) → (2, 2)
print(np.eye(2))           # matrice identité
```

> **À retenir** : avant chaque produit matriciel, vérifie les formes avec `.shape`. La majorité des bugs en deep learning sont des erreurs de dimensions.
''',
"exercises": [
 {"id": "e-3-3-a", "title": "Prédire avec des poids",
  "prompt": "Un modèle prédit le prix d'un logement : `prix = 3000 × surface + 15000 × pieces + 20000`. Écris les poids dans un vecteur `w`, puis calcule en **une opération matricielle** le vecteur `prix` pour les logements de `X` (colonnes : surface, pièces).",
  "starter": "import numpy as np\nX = np.array([[30, 1], [55, 3], [80, 4]], dtype=float)\nb = 20000\n",
  "solution": "import numpy as np\nX = np.array([[30, 1], [55, 3], [80, 4]], dtype=float)\nb = 20000\nw = np.array([3000, 15000])\nprix = X @ w + b\nprint(prix)\n",
  "hint": "w doit avoir autant de valeurs que X a de colonnes. Puis X @ w + b.",
  "check": 'import numpy as np\nassert np.allclose(prix, [125000, 230000, 320000]), f"prix vaut {prix}."\n'},
 {"id": "e-3-3-b", "title": "Similarité cosinus",
  "prompt": "Écris `cosinus(u, v)` qui renvoie la similarité cosinus de deux vecteurs NumPy. Puis trouve `plus_proche` : le nom du document dont le vecteur est le plus similaire à `requete`.",
  "starter": 'import numpy as np\ndocs = {\n    "cours_python": np.array([0.9, 0.1, 0.0]),\n    "recette_crepes": np.array([0.0, 0.2, 0.9]),\n    "tuto_pandas": np.array([0.7, 0.6, 0.1]),\n}\nrequete = np.array([0.8, 0.5, 0.0])\n\ndef cosinus(u, v):\n    pass\n',
  "solution": 'import numpy as np\ndocs = {\n    "cours_python": np.array([0.9, 0.1, 0.0]),\n    "recette_crepes": np.array([0.0, 0.2, 0.9]),\n    "tuto_pandas": np.array([0.7, 0.6, 0.1]),\n}\nrequete = np.array([0.8, 0.5, 0.0])\n\ndef cosinus(u, v):\n    return u @ v / (np.linalg.norm(u) * np.linalg.norm(v))\n\nscores = {nom: cosinus(requete, vec) for nom, vec in docs.items()}\nplus_proche = max(scores, key=scores.get)\nprint(scores, plus_proche)\n',
  "hint": "u @ v divisé par le produit des normes. max(dico, key=dico.get) renvoie la clé de plus grande valeur.",
  "check": 'import numpy as np\nassert abs(cosinus(np.array([1.0, 0.0]), np.array([0.0, 1.0]))) < 1e-9, "Deux vecteurs perpendiculaires ont un cosinus de 0."\nassert abs(cosinus(np.array([2.0, 2.0]), np.array([1.0, 1.0])) - 1) < 1e-9, "Deux vecteurs de même direction ont un cosinus de 1."\nassert plus_proche == "tuto_pandas", f"plus_proche vaut {plus_proche!r}."\n'},
]},
# ---------------------------------------------------------------- 3.4
{"id": "l-3-4", "title": "Dérivées et gradient", "minutes": 60,
"body": r'''
Entraîner un modèle, c'est **minimiser une erreur**. Pour savoir dans quelle direction modifier les paramètres, on utilise la **dérivée**.

## La dérivée : une pente

La dérivée de f en x mesure la pente de la courbe en ce point : de combien f varie quand x augmente un tout petit peu.

```latex
f'(x) \approx \frac{f(x + h) - f(x)}{h} \quad \text{pour } h \text{ très petit}
```

- Si f'(x) > 0, la fonction monte : pour descendre, il faut diminuer x.
- Si f'(x) < 0, elle descend : il faut augmenter x.
- Si f'(x) = 0, on est sur un plat, souvent un minimum ou un maximum.

```python
def f(x):
    return (x - 3) ** 2

def derivee(f, x, h=1e-6):
    return (f(x + h) - f(x - h)) / (2 * h)

for x in [0, 2, 3, 5]:
    print(f"x = {x}  pente ≈ {derivee(f, x):.3f}")
```

La dérivée exacte de (x − 3)² est 2(x − 3) : elle vaut −6 en 0, 0 en 3, et 4 en 5. La pente nulle en x = 3 indique le minimum.

## Les règles à connaître

| Fonction | Dérivée |
| --- | --- |
| c (constante) | 0 |
| x^n | n·x^(n−1) |
| a·x + b | a |
| e^x | e^x |
| g(h(x)) | g'(h(x)) · h'(x) (règle de la chaîne) |

La **règle de la chaîne** est au cœur de la *rétropropagation* (backpropagation), l'algorithme qui entraîne les réseaux de neurones.

## Plusieurs variables : le gradient

Quand f dépend de plusieurs paramètres, on calcule une **dérivée partielle** pour chacun, en faisant comme si les autres étaient constants. Le vecteur de toutes les dérivées partielles est le **gradient**. Il pointe dans la direction où f augmente le plus vite.

```python
import numpy as np

def g(p):
    x, y = p
    return x ** 2 + 3 * y ** 2

def gradient(f, p, h=1e-6):
    grad = np.zeros_like(p)
    for i in range(len(p)):
        e = np.zeros_like(p)
        e[i] = h
        grad[i] = (f(p + e) - f(p - e)) / (2 * h)
    return grad

print(gradient(g, np.array([1.0, 2.0])))   # exact : [2x, 6y] = [2, 12]
```

> **À retenir** : pour minimiser une fonction, on avance dans la direction **opposée** au gradient. C'est toute l'idée de la descente de gradient, la leçon suivante.
''',
"exercises": [
 {"id": "e-3-4-a", "title": "Dérivée numérique",
  "prompt": "Écris `derivee(f, x, h=1e-5)` (différence centrée), puis calcule `pente`, la dérivée de `f(x) = x**3 - 2*x` en x = 2. La valeur exacte est 3·2² − 2 = 10.",
  "starter": "def f(x):\n    return x ** 3 - 2 * x\n\ndef derivee(f, x, h=1e-5):\n    pass\n",
  "solution": "def f(x):\n    return x ** 3 - 2 * x\n\ndef derivee(f, x, h=1e-5):\n    return (f(x + h) - f(x - h)) / (2 * h)\n\npente = derivee(f, 2)\nprint(pente)\n",
  "hint": "(f(x + h) - f(x - h)) / (2 * h)",
  "check": 'assert abs(pente - 10) < 1e-4, f"pente vaut {pente}, j\'attendais 10."\nassert abs(derivee(lambda x: x ** 2, 3) - 6) < 1e-4, "Ta fonction derivee doit marcher pour n\'importe quelle fonction : la dérivée de x² en 3 vaut 6."\n'},
 {"id": "e-3-4-b", "title": "Gradient exact",
  "prompt": "Pour `perte(a, b) = (a - 1)**2 + (b + 2)**2`, écris `grad_perte(a, b)` qui renvoie le tuple des deux dérivées partielles **exactes** (pas numériques).",
  "starter": "def grad_perte(a, b):\n    pass\n",
  "solution": "def grad_perte(a, b):\n    return 2 * (a - 1), 2 * (b + 2)\n\nprint(grad_perte(0, 0))\n",
  "hint": "La dérivée de (a - 1)² par rapport à a est 2(a - 1) ; b est traité comme une constante.",
  "check": 'r = grad_perte(0, 0)\nassert tuple(r) == (-2, 4), f"grad_perte(0, 0) renvoie {r}, j\'attendais (-2, 4)."\nassert tuple(grad_perte(1, -2)) == (0, 0), "Au minimum (1, -2), le gradient doit être nul."\n'},
]},
# ---------------------------------------------------------------- 3.5
{"id": "l-3-5", "title": "La descente de gradient", "minutes": 90,
"body": r'''
La **descente de gradient** est l'algorithme qui entraîne la quasi-totalité des modèles modernes, de la régression linéaire aux grands modèles de langage. Le principe tient en une ligne : on répète

```latex
\theta \leftarrow \theta - \eta \, \nabla L(\theta)
```

θ représente les paramètres, L la fonction de perte (l'erreur), ∇L son gradient, et η (eta) le **taux d'apprentissage** (*learning rate*) : la taille du pas.

```viz gradient
```

## En une dimension

```python
def L(x):
    return (x - 3) ** 2

def dL(x):
    return 2 * (x - 3)

x = 10.0
eta = 0.1
for etape in range(30):
    x = x - eta * dL(x)
print(round(x, 4))   # proche de 3, le minimum
```

## Le taux d'apprentissage

C'est l'hyperparamètre le plus important. Trop petit, l'apprentissage est très lent. Trop grand, on saute par-dessus le minimum et l'erreur explose.

```python
for eta in [0.01, 0.1, 0.9, 1.1]:
    x = 10.0
    for _ in range(30):
        x = x - eta * dL(x)
    print(f"eta = {eta:<5} → x = {x:.3f}")
```

## Une régression linéaire, à la main

On cherche la droite ŷ = w·x + b qui colle le mieux aux données. La perte est l'**erreur quadratique moyenne** (MSE) :

```latex
L(w, b) = \frac{1}{n} \sum_i (w x_i + b - y_i)^2
\qquad
\frac{\partial L}{\partial w} = \frac{2}{n} \sum_i (\hat{y}_i - y_i)\, x_i
\qquad
\frac{\partial L}{\partial b} = \frac{2}{n} \sum_i (\hat{y}_i - y_i)
```

```python
import numpy as np
import plotly.express as px

rng = np.random.default_rng(0)
x = rng.uniform(0, 10, 100)
y = 2.5 * x + 4 + rng.normal(0, 2, 100)     # vraie droite : w = 2.5, b = 4, plus du bruit

w, b, eta = 0.0, 0.0, 0.01
pertes = []
for epoque in range(500):
    y_pred = w * x + b
    erreur = y_pred - y
    pertes.append((erreur ** 2).mean())
    w -= eta * 2 * (erreur * x).mean()
    b -= eta * 2 * erreur.mean()

print(f"w = {w:.2f}, b = {b:.2f}, MSE finale = {pertes[-1]:.2f}")
px.line(y=pertes, title="La perte diminue à chaque époque",
        labels={"y": "MSE", "x": "époque"})
```

Le modèle retrouve presque la vraie droite (w ≈ 2,5, b ≈ 4) à partir des seules données. scikit-learn et PyTorch font exactement cela, en plus rapide et avec plus de paramètres.

> **À retenir** : une **époque** est un passage complet sur les données. Une courbe de perte qui descend puis se stabilise signifie que l'entraînement a convergé. Une courbe qui remonte signale un taux d'apprentissage trop grand.
''',
"exercises": [
 {"id": "e-3-5-a", "title": "Minimiser une parabole",
  "prompt": "Avec une descente de gradient (eta = 0.1, 100 étapes, départ x = 0), trouve le minimum de `L(x) = (x + 4)**2 + 1`. Stocke le résultat final dans `x_min`. Écris toi-même la dérivée `dL`.",
  "starter": "def L(x):\n    return (x + 4) ** 2 + 1\n\ndef dL(x):\n    pass\n\nx = 0.0\n",
  "solution": "def L(x):\n    return (x + 4) ** 2 + 1\n\ndef dL(x):\n    return 2 * (x + 4)\n\nx = 0.0\nfor _ in range(100):\n    x -= 0.1 * dL(x)\nx_min = x\nprint(x_min, L(x_min))\n",
  "hint": "La dérivée de (x + 4)² + 1 est 2(x + 4). Répète x -= 0.1 * dL(x).",
  "check": 'assert abs(x_min + 4) < 1e-3, f"x_min vaut {x_min}, le minimum est en -4."\nassert dL(-4) == 0, "dL(-4) devrait valoir 0."\n'},
 {"id": "e-3-5-b", "title": "Régression sur les manchots",
  "prompt": "Entraîne par descente de gradient une régression `masse ≈ w × nageoire + b` sur les manchots. Les données sont **standardisées** pour que la descente converge vite (`xs`, `ys`). Utilise eta = 0.1 et 200 époques, et remplis la liste `pertes` avec la MSE à chaque époque. Compare ton `w` à la pente de `np.polyfit`.",
  "starter": 'import numpy as np\nimport pandas as pd\ndf = pd.read_csv("penguins.csv").dropna()\nx = df["flipper_length_mm"].to_numpy()\ny = df["body_mass_g"].to_numpy()\nxs = (x - x.mean()) / x.std()\nys = (y - y.mean()) / y.std()\n\nw, b = 0.0, 0.0\npertes = []\n',
  "solution": 'import numpy as np\nimport pandas as pd\nimport plotly.express as px\ndf = pd.read_csv("penguins.csv").dropna()\nx = df["flipper_length_mm"].to_numpy()\ny = df["body_mass_g"].to_numpy()\nxs = (x - x.mean()) / x.std()\nys = (y - y.mean()) / y.std()\n\nw, b = 0.0, 0.0\npertes = []\nfor _ in range(200):\n    erreur = w * xs + b - ys\n    pertes.append((erreur ** 2).mean())\n    w -= 0.1 * 2 * (erreur * xs).mean()\n    b -= 0.1 * 2 * erreur.mean()\n\nprint("w =", round(w, 4), " polyfit :", round(np.polyfit(xs, ys, 1)[0], 4))\npx.line(y=pertes, title="Courbe de perte")\n',
  "hint": "Reprends la boucle de la leçon en remplaçant x et y par xs et ys, et eta par 0.1.",
  "check": 'import numpy as np\nassert len(pertes) == 200, f"pertes contient {len(pertes)} valeurs, j\'en attendais 200."\nassert pertes[-1] < pertes[0], "La perte doit diminuer."\nassert abs(w - np.polyfit(xs, ys, 1)[0]) < 1e-3, f"w vaut {w:.4f}, la pente optimale est {np.polyfit(xs, ys, 1)[0]:.4f}."\n'},
]},
],
"project": {
"id": "p-3", "title": "Projet 3 · Ta régression linéaire de A à Z",
"body": r'''
Objectif : écrire une **classe** de régression linéaire entraînée par descente de gradient, avec l'interface `fit` / `predict` de scikit-learn. Tu réutilises les classes (semaine 1), NumPy (semaine 2) et les maths de cette semaine.

Ta classe doit gérer **plusieurs** caractéristiques : X est une matrice (n, k), les poids `coef_` un vecteur de k valeurs, et le biais `intercept_` un nombre. Les gradients en version matricielle :

```latex
\hat{y} = X w + b \qquad
\nabla_w L = \frac{2}{n} X^\top (\hat{y} - y) \qquad
\frac{\partial L}{\partial b} = \frac{2}{n} \sum_i (\hat{y}_i - y_i)
```
''',
"exercises": [
 {"id": "e-p3-a", "title": "La classe RegressionGD",
  "prompt": "Complète `RegressionGD`. `fit(X, y)` initialise `coef_` à des zéros et `intercept_` à 0, puis fait `n_epoques` étapes de descente de gradient en remplissant `self.pertes_` (MSE à chaque époque) ; elle renvoie `self`. `predict(X)` renvoie `X @ coef_ + intercept_`.",
  "starter": "import numpy as np\n\nclass RegressionGD:\n    def __init__(self, eta=0.1, n_epoques=500):\n        self.eta = eta\n        self.n_epoques = n_epoques\n\n    def fit(self, X, y):\n        pass\n\n    def predict(self, X):\n        pass\n",
  "solution": "import numpy as np\n\nclass RegressionGD:\n    def __init__(self, eta=0.1, n_epoques=500):\n        self.eta = eta\n        self.n_epoques = n_epoques\n\n    def fit(self, X, y):\n        n, k = X.shape\n        self.coef_ = np.zeros(k)\n        self.intercept_ = 0.0\n        self.pertes_ = []\n        for _ in range(self.n_epoques):\n            erreur = X @ self.coef_ + self.intercept_ - y\n            self.pertes_.append((erreur ** 2).mean())\n            self.coef_ -= self.eta * 2 / n * (X.T @ erreur)\n            self.intercept_ -= self.eta * 2 * erreur.mean()\n        return self\n\n    def predict(self, X):\n        return X @ self.coef_ + self.intercept_\n\nrng = np.random.default_rng(0)\nX = rng.normal(size=(200, 3))\ny = X @ np.array([2.0, -1.0, 0.5]) + 3 + rng.normal(0, 0.1, 200)\nm = RegressionGD().fit(X, y)\nprint(m.coef_.round(2), round(m.intercept_, 2))\n",
  "hint": "n, k = X.shape. L'erreur est X @ coef_ + intercept_ - y ; le gradient des poids est 2 / n * X.T @ erreur.",
  "check": 'import numpy as np\nrng = np.random.default_rng(5)\nX_t = rng.normal(size=(300, 3))\ny_t = X_t @ np.array([1.5, -2.0, 0.7]) + 4 + rng.normal(0, 0.05, 300)\nm_t = RegressionGD(eta=0.1, n_epoques=500)\nassert m_t.fit(X_t, y_t) is m_t, "fit doit renvoyer self."\nassert np.allclose(m_t.coef_, [1.5, -2.0, 0.7], atol=0.05), f"coef_ vaut {m_t.coef_}, j\'attendais environ [1.5, -2.0, 0.7]."\nassert abs(m_t.intercept_ - 4) < 0.05, f"intercept_ vaut {m_t.intercept_}, j\'attendais environ 4."\nassert len(m_t.pertes_) == 500 and m_t.pertes_[-1] < m_t.pertes_[0], "pertes_ doit contenir une MSE par époque, en baisse."\nassert m_t.predict(X_t[:2]).shape == (2,), "predict doit renvoyer une prédiction par ligne."\n'},
 {"id": "e-p3-b", "title": "Appliquer aux manchots",
  "prompt": "Utilise ta classe (recopie-la au début) pour prédire `body_mass_g` à partir de `flipper_length_mm`, `bill_length_mm` et `bill_depth_mm`, standardisés. Calcule `rmse`, la racine de l'erreur quadratique moyenne **en grammes** sur toutes les données.",
  "starter": 'import numpy as np\nimport pandas as pd\n# recopie ta classe RegressionGD ici\n\ndf = pd.read_csv("penguins.csv").dropna()\ncols = ["flipper_length_mm", "bill_length_mm", "bill_depth_mm"]\nX = df[cols].to_numpy()\nX = (X - X.mean(axis=0)) / X.std(axis=0)\ny = df["body_mass_g"].to_numpy()\n',
  "solution": 'import numpy as np\nimport pandas as pd\n\nclass RegressionGD:\n    def __init__(self, eta=0.1, n_epoques=500):\n        self.eta = eta\n        self.n_epoques = n_epoques\n\n    def fit(self, X, y):\n        n, k = X.shape\n        self.coef_ = np.zeros(k)\n        self.intercept_ = 0.0\n        self.pertes_ = []\n        for _ in range(self.n_epoques):\n            erreur = X @ self.coef_ + self.intercept_ - y\n            self.pertes_.append((erreur ** 2).mean())\n            self.coef_ -= self.eta * 2 / n * (X.T @ erreur)\n            self.intercept_ -= self.eta * 2 * erreur.mean()\n        return self\n\n    def predict(self, X):\n        return X @ self.coef_ + self.intercept_\n\ndf = pd.read_csv("penguins.csv").dropna()\ncols = ["flipper_length_mm", "bill_length_mm", "bill_depth_mm"]\nX = df[cols].to_numpy()\nX = (X - X.mean(axis=0)) / X.std(axis=0)\ny = df["body_mass_g"].to_numpy()\n\nmodele = RegressionGD(eta=0.1, n_epoques=1000).fit(X, y)\nrmse = np.sqrt(((modele.predict(X) - y) ** 2).mean())\nprint(f"RMSE : {rmse:.0f} g")\n',
  "hint": "rmse = np.sqrt(((predictions - y) ** 2).mean()). Avec des données standardisées, eta = 0.1 et 1 000 époques suffisent.",
  "check": 'assert 380 < rmse < 400, f"rmse vaut {rmse:.1f} g ; avec ces 3 variables on obtient environ 390 g. Ton modèle a-t-il convergé ?"\n'},
],
"tasks": [
  "Copier ta classe dans un fichier regression_gd.py",
  "Tracer la courbe de perte dans un notebook",
  "Expliquer dans le README ce que représentent coef_ et intercept_",
  "Publier sur GitHub",
]},
"quiz": [
 {"q": "Un jeu de salaires contient quelques valeurs très élevées. Quel indicateur décrit le mieux le salaire « typique » ?", "options": ["La moyenne", "La médiane", "Le maximum", "La variance"], "answer": 1,
  "explain": "La médiane n'est pas tirée vers le haut par les valeurs extrêmes, contrairement à la moyenne."},
 {"q": "Une corrélation de −0,9 entre deux variables signifie :", "options": ["Aucune relation", "Une forte relation linéaire : quand l'une monte, l'autre baisse", "Une erreur de calcul", "Que l'une cause l'autre"], "answer": 1,
  "explain": "Le signe donne le sens de la relation, la valeur absolue sa force. Corrélation n'est pas causalité."},
 {"q": "Une maladie est très rare et ton test est positif. Pourquoi la probabilité d'être malade peut-elle rester faible ?", "options": ["Parce que le test est inutile", "Parce que les faux positifs, chez les très nombreux sains, dépassent les vrais positifs", "Parce que Bayes ne s'applique pas aux tests", "Ce n'est pas possible"], "answer": 1,
  "explain": "Quand la prévalence est faible, même un petit taux de faux positifs s'applique à une très grande population de personnes saines."},
 {"q": "Quelle forme a le résultat de A @ B si A est (100, 5) et B est (5, 3) ?", "options": ["(5, 5)", "(100, 3)", "(3, 100)", "Erreur"], "answer": 1,
  "explain": "(n, k) @ (k, m) donne (n, m) : ici (100, 3)."},
 {"q": "Que mesure la similarité cosinus ?", "options": ["La distance en kilomètres", "L'angle entre deux vecteurs, indépendamment de leur longueur", "La somme des composantes", "La variance"], "answer": 1,
  "explain": "Elle compare les directions. C'est la mesure standard de proximité entre embeddings dans un système RAG."},
 {"q": "En x = 2, la dérivée d'une fonction vaut +5. Pour la diminuer, il faut :", "options": ["Augmenter x", "Diminuer x", "Garder x", "Doubler x"], "answer": 1,
  "explain": "Une pente positive signifie que la fonction monte quand x augmente : on va dans le sens opposé."},
 {"q": "Pendant l'entraînement, la perte augmente à chaque époque jusqu'à devenir énorme. Cause la plus probable ?", "options": ["Taux d'apprentissage trop petit", "Taux d'apprentissage trop grand", "Trop de données", "Le modèle a convergé"], "answer": 1,
  "explain": "Un pas trop grand fait sauter par-dessus le minimum, de plus en plus loin : la perte diverge."},
 {"q": "Qu'est-ce qu'une époque ?", "options": ["Une mise à jour d'un seul paramètre", "Un passage complet sur les données d'entraînement", "Le temps d'entraînement en heures", "Un type de modèle"], "answer": 1,
  "explain": "Une époque = toutes les données vues une fois. On entraîne généralement sur plusieurs époques."},
]}
