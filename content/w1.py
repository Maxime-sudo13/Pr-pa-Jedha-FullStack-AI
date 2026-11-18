WEEK = {
"id": "s1", "num": 1,
"title": "Python et Git",
"goal": "Écrire seul un petit script Python propre, structuré en fonctions, et le publier sur GitHub.",
"hours": "8 à 10 h",
"lessons": [
# ---------------------------------------------------------------- 1.1
{"id": "l-1-1", "title": "Ton environnement de travail", "minutes": 40,
"body": r'''
Pendant la formation, tu coderas surtout dans **VS Code** et dans des **notebooks Jupyter**, et tu publieras ton travail sur **GitHub**. Installe tout dès maintenant pour ne pas perdre de temps le premier jour.

Sur cette plateforme, Python tourne directement dans ton navigateur : chaque bloc de code gris a un bouton **Exécuter**. Le résultat s'affiche juste en dessous, comme dans un notebook. Les blocs d'une même leçon partagent leurs variables : exécute-les dans l'ordre.

```python
print("Bonjour ! Python fonctionne.")
2 + 3
```

La dernière ligne d'un bloc est affichée automatiquement si c'est une valeur (ici `2 + 3`), exactement comme dans Jupyter. Pour afficher autre chose, utilise `print()`.

## Ce qu'il faut installer sur ton ordinateur

1. **Python 3.12 ou plus récent**, depuis python.org. Sous Windows, coche « Add Python to PATH » pendant l'installation.
2. **VS Code**, puis ses extensions *Python* et *Jupyter* (de Microsoft).
3. **Git**, depuis git-scm.com. Sur Mac, il est souvent déjà là : tape `git --version` dans le Terminal.
4. Un **compte GitHub** gratuit, avec une adresse e-mail que tu consultes.

Vérifie l'installation dans un terminal :

```bash
python --version      # ou python3 --version sur Mac/Linux
git --version
pip install jupyter pandas numpy scikit-learn plotly
```

> **À retenir** : un *notebook* (.ipynb) mélange du code, ses résultats et du texte. C'est l'outil de base pour explorer des données. Un *script* (.py) s'exécute d'un bloc, et c'est ce qu'on utilise pour du code réutilisable ou mis en production.
''',
"tasks": [
  "Installer Python 3.12+ et vérifier python --version",
  "Installer VS Code avec les extensions Python et Jupyter",
  "Installer Git et vérifier git --version",
  "Créer un compte GitHub",
  "Installer jupyter, pandas, numpy, scikit-learn et plotly avec pip",
  "Ouvrir un premier notebook dans VS Code et exécuter print('ok')",
],
"exercises": [
 {"id": "e-1-1-a", "title": "Premier programme",
  "prompt": "Affiche exactement la phrase `Je deviens AI Engineer` avec `print()`.",
  "starter": "# Écris ton code ici\n",
  "solution": 'print("Je deviens AI Engineer")\n',
  "hint": "print(\"...\") affiche le texte entre guillemets.",
  "check": 'assert "Je deviens AI Engineer" in _out, "Je ne vois pas la phrase exacte dans ce que tu affiches (attention aux majuscules)."\n'},
]},
# ---------------------------------------------------------------- 1.2
{"id": "l-1-2", "title": "Variables, types et opérations", "minutes": 60,
"body": r'''
Une **variable** est un nom qui pointe vers une valeur. On la crée avec `=`. Python devine le **type** tout seul.

```python
age = 29              # int : nombre entier
taille = 1.78         # float : nombre à virgule (avec un point !)
prenom = "Sam"        # str : texte, entre guillemets
admis = True          # bool : True ou False
type(taille)
```

## Les opérations sur les nombres

```python
print(7 + 2, 7 - 2, 7 * 2)
print(7 / 2)     # division classique : 3.5
print(7 // 2)    # division entière : 3
print(7 % 2)     # reste (modulo) : 1
print(2 ** 10)   # puissance : 1024
```

Le modulo `%` sert souvent à tester la parité : `n % 2 == 0` signifie « n est pair ».

## Le texte et les f-strings

Pour mélanger texte et valeurs, utilise une **f-string** : un `f` devant les guillemets, et les variables entre accolades.

```python
heures = 450
semaines = 12
print(f"{prenom} suivra {heures} heures en {semaines} semaines.")
print(f"Soit {heures / semaines:.1f} heures par semaine.")   # :.1f = 1 décimale
```

## Convertir un type en un autre

Ce que tu lis dans un fichier ou que tape un utilisateur arrive souvent sous forme de texte. Il faut le convertir.

```python
texte = "42"
nombre = int(texte)
print(nombre + 1)
print(float("3.14") * 2)
print(str(100) + " %")
```

> **À retenir** : `"42" + 1` provoque une `TypeError`, car on ne peut pas additionner un texte et un nombre. Convertis d'abord avec `int()` ou `float()`.
''',
"exercises": [
 {"id": "e-1-2-a", "title": "Prix TTC",
  "prompt": "Une formation coûte `prix_ht = 6250` euros hors taxes. Crée une variable `prix_ttc` qui contient le prix avec 20 % de TVA, puis affiche-la.",
  "starter": "prix_ht = 6250\n# prix_ttc = ...\n",
  "solution": "prix_ht = 6250\nprix_ttc = prix_ht * 1.2\nprint(prix_ttc)\n",
  "hint": "Ajouter 20 %, c'est multiplier par 1.2.",
  "check": 'assert abs(prix_ttc - 7500) < 1e-6, f"prix_ttc vaut {prix_ttc}, j\'attendais 7500."\n'},
 {"id": "e-1-2-b", "title": "Heures par jour",
  "prompt": "La formation dure `450` heures sur `60` jours ouvrés. Calcule `heures_par_jour`, puis crée une f-string `message` qui vaut exactement `7.5 heures par jour` (une décimale).",
  "starter": "heures = 450\njours = 60\n",
  "solution": 'heures = 450\njours = 60\nheures_par_jour = heures / jours\nmessage = f"{heures_par_jour:.1f} heures par jour"\nprint(message)\n',
  "hint": "Dans une f-string, {valeur:.1f} affiche une décimale.",
  "check": 'assert heures_par_jour == 7.5, "heures_par_jour devrait valoir 7.5."\nassert message == "7.5 heures par jour", f"message vaut {message!r}."\n'},
 {"id": "e-1-2-c", "title": "Pair ou impair",
  "prompt": "Crée une variable booléenne `est_pair` qui vaut `True` si `n` est pair, `False` sinon. Ton code doit marcher quelle que soit la valeur de `n`.",
  "starter": "n = 17\n# est_pair = ...\n",
  "solution": "n = 17\nest_pair = n % 2 == 0\n",
  "hint": "Utilise le modulo : n % 2 vaut 0 quand n est pair.",
  "check": 'assert isinstance(est_pair, bool), "est_pair doit être un booléen (True ou False)."\nassert est_pair == (n % 2 == 0), "est_pair ne correspond pas à la parité de n."\n'},
]},
# ---------------------------------------------------------------- 1.3
{"id": "l-1-3", "title": "Conditions et boucles", "minutes": 60,
"body": r'''
## Les conditions : if, elif, else

Le bloc sous une condition est **indenté** de 4 espaces. Les deux-points `:` sont obligatoires.

```python
note = 14
if note >= 16:
    mention = "Très bien"
elif note >= 12:
    mention = "Bien"
elif note >= 10:
    mention = "Passable"
else:
    mention = "Ajourné"
print(mention)
```

Les opérateurs de comparaison : `==` (égal), `!=` (différent), `<`, `<=`, `>`, `>=`. On combine avec `and`, `or`, `not`.

## La boucle for

`for` parcourt une séquence : une liste, un texte, ou une suite de nombres avec `range()`.

```python
for i in range(5):        # 0, 1, 2, 3, 4
    print("Itération", i)

total = 0
for x in [3, 8, 1, 6]:
    total = total + x     # ou : total += x
print("Total :", total)
```

`range(debut, fin, pas)` s'arrête **avant** `fin` : `range(2, 10, 3)` donne 2, 5, 8.

## La boucle while

`while` répète tant qu'une condition est vraie. Attention à faire évoluer la condition, sinon la boucle ne s'arrête jamais.

```python
capital = 1000
annees = 0
while capital < 2000:
    capital = capital * 1.07
    annees += 1
print(f"Le capital double en {annees} ans.")
```

`break` sort de la boucle immédiatement, `continue` passe directement au tour suivant.

> **À retenir** : en machine learning, l'entraînement d'un modèle est une boucle. On répète une étape de calcul des milliers de fois en améliorant le modèle à chaque tour. Tu le coderas toi-même en semaine 3.
''',
"exercises": [
 {"id": "e-1-3-a", "title": "Somme des pairs",
  "prompt": "Avec une boucle `for`, calcule dans `somme` la somme de tous les nombres **pairs** de 1 à 100 inclus.",
  "starter": "somme = 0\n# ta boucle ici\n",
  "solution": "somme = 0\nfor i in range(1, 101):\n    if i % 2 == 0:\n        somme += i\nprint(somme)\n",
  "hint": "range(1, 101) va de 1 à 100. Teste la parité avec i % 2 == 0.",
  "check": 'assert somme == 2550, f"somme vaut {somme}, j\'attendais 2550."\n'},
 {"id": "e-1-3-b", "title": "Catégoriser des scores",
  "prompt": "Pour chaque score de la liste, ajoute à la liste `categories` : `\"faible\"` si le score est inférieur à 0.5, `\"moyen\"` s'il est entre 0.5 inclus et 0.8 exclu, `\"fort\"` sinon.",
  "starter": "scores = [0.12, 0.55, 0.91, 0.79, 0.5, 0.8]\ncategories = []\n",
  "solution": 'scores = [0.12, 0.55, 0.91, 0.79, 0.5, 0.8]\ncategories = []\nfor s in scores:\n    if s < 0.5:\n        categories.append("faible")\n    elif s < 0.8:\n        categories.append("moyen")\n    else:\n        categories.append("fort")\nprint(categories)\n',
  "hint": "Utilise if / elif / else dans la boucle, et categories.append(...) pour ajouter.",
  "check": 'assert categories == ["faible", "moyen", "fort", "moyen", "moyen", "fort"], f"categories vaut {categories}. Vérifie les bornes : 0.5 est moyen, 0.8 est fort."\n'},
 {"id": "e-1-3-c", "title": "Combien d'époques ?",
  "prompt": "Un modèle commence avec une erreur `erreur = 10`. À chaque époque, l'erreur est multipliée par `0.8`. Avec une boucle `while`, compte dans `epoques` combien d'époques il faut pour que l'erreur passe **sous** 1.",
  "starter": "erreur = 10\nepoques = 0\n",
  "solution": "erreur = 10\nepoques = 0\nwhile erreur >= 1:\n    erreur *= 0.8\n    epoques += 1\nprint(epoques, erreur)\n",
  "hint": "while erreur >= 1: puis multiplie et incrémente le compteur.",
  "check": 'assert epoques == 11, f"epoques vaut {epoques}, j\'attendais 11."\n'},
]},
# ---------------------------------------------------------------- 1.4
{"id": "l-1-4", "title": "Listes, dictionnaires, tuples et sets", "minutes": 75,
"body": r'''
## Les listes

Une liste est une suite ordonnée et modifiable. Les indices commencent à **0**, et les indices négatifs partent de la fin.

```python
langages = ["Python", "SQL", "Bash", "R"]
print(langages[0], langages[-1])     # premier et dernier
print(langages[1:3])                 # tranche : indices 1 et 2
langages.append("Rust")              # ajouter à la fin
langages.remove("R")                 # retirer une valeur
print(len(langages), langages)
print(sorted([5, 2, 9, 1]))          # trier sans modifier l'original
```

## Les dictionnaires

Un dictionnaire associe des **clés** à des **valeurs**. C'est la structure idéale pour décrire un objet, ou pour compter.

```python
apprenant = {"prenom": "Sam", "semaine": 1, "langages": ["Python"]}
print(apprenant["prenom"])
apprenant["semaine"] = 2                    # modifier
apprenant["objectif"] = "AI Engineer"       # ajouter
print(apprenant.get("ville", "inconnue"))   # valeur par défaut si la clé manque
for cle, valeur in apprenant.items():
    print(cle, "→", valeur)
```

Compter des occurrences est un réflexe à avoir :

```python
mots = "le chat et le chien et le lapin".split()
compte = {}
for m in mots:
    compte[m] = compte.get(m, 0) + 1
compte
```

## Tuples et sets

Un **tuple** est une liste qu'on ne peut pas modifier : `point = (3, 4)`. On l'utilise pour des valeurs qui vont ensemble, comme la forme d'un tableau `(lignes, colonnes)`.

Un **set** est un ensemble sans doublons, très rapide pour tester l'appartenance.

```python
especes = {"Adelie", "Gentoo", "Adelie", "Chinstrap"}
print(especes)                 # les doublons disparaissent
print("Gentoo" in especes)
```

## Les compréhensions de listes

Une compréhension construit une liste en une ligne. Tu en verras partout dans le code data.

```python
nombres = [1, 2, 3, 4, 5, 6]
carres = [n ** 2 for n in nombres]
pairs = [n for n in nombres if n % 2 == 0]
print(carres, pairs)
```

> **À retenir** : la forme est `[expression for element in sequence if condition]`. La partie `if` est facultative. Il existe aussi la version dictionnaire : `{k: v for k, v in ...}`.
''',
"exercises": [
 {"id": "e-1-4-a", "title": "Compter les mots",
  "prompt": "Crée un dictionnaire `frequences` qui compte combien de fois chaque mot apparaît dans `phrase`. Les mots sont séparés par des espaces.",
  "starter": 'phrase = "data science data engineering ia data ia"\n',
  "solution": 'phrase = "data science data engineering ia data ia"\nfrequences = {}\nfor mot in phrase.split():\n    frequences[mot] = frequences.get(mot, 0) + 1\nprint(frequences)\n',
  "hint": "phrase.split() découpe en mots. Utilise frequences.get(mot, 0) + 1.",
  "check": 'assert frequences == {"data": 3, "science": 1, "engineering": 1, "ia": 2}, f"frequences vaut {frequences}."\n'},
 {"id": "e-1-4-b", "title": "Filtrer avec une compréhension",
  "prompt": "À partir de `temperatures`, crée **en une ligne** la liste `chaudes` des températures strictement supérieures à 25, converties en Fahrenheit (`f = c * 9 / 5 + 32`).",
  "starter": "temperatures = [18, 27, 31, 22, 26, 15]\n",
  "solution": "temperatures = [18, 27, 31, 22, 26, 15]\nchaudes = [c * 9 / 5 + 32 for c in temperatures if c > 25]\nprint(chaudes)\n",
  "hint": "[conversion for c in temperatures if condition]",
  "check": 'assert [round(x, 1) for x in chaudes] == [80.6, 87.8, 78.8], f"chaudes vaut {chaudes}."\n'},
 {"id": "e-1-4-c", "title": "Fusionner sans doublons",
  "prompt": "Crée `competences`, la liste **triée par ordre alphabétique** de toutes les compétences présentes dans `a` ou `b`, sans doublons.",
  "starter": 'a = ["python", "sql", "git"]\nb = ["git", "docker", "python", "mlflow"]\n',
  "solution": 'a = ["python", "sql", "git"]\nb = ["git", "docker", "python", "mlflow"]\ncompetences = sorted(set(a) | set(b))\nprint(competences)\n',
  "hint": "set(a) | set(b) fait l'union de deux ensembles, puis sorted(...) renvoie une liste triée.",
  "check": 'assert competences == ["docker", "git", "mlflow", "python", "sql"], f"competences vaut {competences}."\n'},
]},
# ---------------------------------------------------------------- 1.5
{"id": "l-1-5", "title": "Fonctions", "minutes": 60,
"body": r'''
Une **fonction** regroupe du code réutilisable. Elle reçoit des **paramètres** et **renvoie** un résultat avec `return`.

```python
def moyenne(valeurs):
    """Renvoie la moyenne d'une liste de nombres."""
    return sum(valeurs) / len(valeurs)

print(moyenne([12, 15, 9]))
```

La phrase entre triples guillemets est la **docstring** : elle documente la fonction. `help(moyenne)` l'affiche.

## Paramètres par défaut et arguments nommés

```python
def arrondir_pct(x, decimales=1):
    return f"{x * 100:.{decimales}f} %"

print(arrondir_pct(0.8734))
print(arrondir_pct(0.8734, decimales=3))
```

Tu retrouveras ce style partout dans scikit-learn : `train_test_split(X, y, test_size=0.2, random_state=42)`.

## return contre print

`print` affiche, mais la valeur est perdue. `return` renvoie la valeur pour qu'on puisse la réutiliser. Une fonction sans `return` renvoie `None`.

```python
def double_print(x):
    print(x * 2)

def double_return(x):
    return x * 2

a = double_print(5)
b = double_return(5)
print("a =", a, "| b =", b)
```

## Renvoyer plusieurs valeurs

```python
def min_max(valeurs):
    return min(valeurs), max(valeurs)   # renvoie un tuple

bas, haut = min_max([4, 9, 1, 7])
print(bas, haut)
```

## La portée des variables

Une variable créée **dans** une fonction n'existe que dans cette fonction. Passe ce dont la fonction a besoin en paramètre plutôt que d'utiliser des variables globales.

> **À retenir** : une bonne fonction fait une seule chose, porte un nom qui dit ce qu'elle fait (un verbe), et renvoie son résultat.
''',
"exercises": [
 {"id": "e-1-5-a", "title": "Écart à la moyenne",
  "prompt": "Écris une fonction `ecarts(valeurs)` qui renvoie la liste des écarts de chaque valeur à la moyenne. Par exemple `ecarts([1, 2, 3])` renvoie `[-1.0, 0.0, 1.0]`.",
  "starter": "def ecarts(valeurs):\n    # à compléter\n    pass\n\nprint(ecarts([1, 2, 3]))\n",
  "solution": "def ecarts(valeurs):\n    m = sum(valeurs) / len(valeurs)\n    return [v - m for v in valeurs]\n\nprint(ecarts([1, 2, 3]))\n",
  "hint": "Calcule d'abord la moyenne m, puis une compréhension [v - m for v in valeurs].",
  "check": 'assert ecarts([1, 2, 3]) == [-1.0, 0.0, 1.0], "ecarts([1, 2, 3]) devrait renvoyer [-1.0, 0.0, 1.0]."\nassert ecarts([10, 20]) == [-5.0, 5.0], "Teste avec [10, 20] : j\'attends [-5.0, 5.0]."\n'},
 {"id": "e-1-5-b", "title": "Résumé statistique",
  "prompt": "Écris `resume(valeurs)` qui renvoie un dictionnaire avec les clés `\"n\"`, `\"min\"`, `\"max\"` et `\"moyenne\"` (moyenne arrondie à 2 décimales avec `round`).",
  "starter": "def resume(valeurs):\n    pass\n\nprint(resume([3, 7, 8, 12]))\n",
  "solution": 'def resume(valeurs):\n    return {\n        "n": len(valeurs),\n        "min": min(valeurs),\n        "max": max(valeurs),\n        "moyenne": round(sum(valeurs) / len(valeurs), 2),\n    }\n\nprint(resume([3, 7, 8, 12]))\n',
  "hint": "len, min, max, sum existent déjà en Python. round(x, 2) arrondit.",
  "check": 'r = resume([3, 7, 8, 12])\nassert isinstance(r, dict), "resume doit renvoyer un dictionnaire (as-tu oublié return ?)."\nassert r == {"n": 4, "min": 3, "max": 12, "moyenne": 7.5}, f"resume([3, 7, 8, 12]) renvoie {r}."\nassert resume([1, 2, 2])["moyenne"] == 1.67, "La moyenne doit être arrondie à 2 décimales."\n'},
 {"id": "e-1-5-c", "title": "Normaliser avec un paramètre par défaut",
  "prompt": "Écris `normaliser(valeurs, bas=0, haut=1)` qui ramène les valeurs dans l'intervalle [bas, haut] (normalisation min-max). Formule : `bas + (v - min) / (max - min) * (haut - bas)`.",
  "starter": "def normaliser(valeurs, bas=0, haut=1):\n    pass\n",
  "solution": "def normaliser(valeurs, bas=0, haut=1):\n    mn, mx = min(valeurs), max(valeurs)\n    return [bas + (v - mn) / (mx - mn) * (haut - bas) for v in valeurs]\n\nprint(normaliser([10, 15, 20]))\nprint(normaliser([10, 15, 20], bas=-1, haut=1))\n",
  "hint": "Calcule min et max une seule fois avant la compréhension.",
  "check": 'assert normaliser([10, 15, 20]) == [0.0, 0.5, 1.0], f"normaliser([10, 15, 20]) renvoie {normaliser([10, 15, 20])}."\nassert normaliser([10, 15, 20], bas=-1, haut=1) == [-1.0, 0.0, 1.0], "Avec bas=-1 et haut=1, j\'attends [-1.0, 0.0, 1.0]."\n'},
]},
# ---------------------------------------------------------------- 1.6
{"id": "l-1-6", "title": "Fichiers, CSV, JSON et erreurs", "minutes": 70,
"body": r'''
Les données arrivent presque toujours dans des fichiers. Sur cette plateforme, trois fichiers CSV sont disponibles : `penguins.csv` (manchots de l'Antarctique), `titanic.csv` (passagers du Titanic) et `tips.csv` (pourboires dans un restaurant).

## Lire un fichier texte

Utilise toujours `with` : le fichier est fermé automatiquement, même en cas d'erreur.

```python
with open("penguins.csv") as f:
    lignes = f.readlines()
print(len(lignes), "lignes")
print(lignes[0])
print(lignes[1])
```

## Lire un CSV avec le module csv

`csv.DictReader` transforme chaque ligne en dictionnaire dont les clés sont les noms de colonnes. Toutes les valeurs sont du **texte**.

```python
import csv

with open("penguins.csv") as f:
    manchots = list(csv.DictReader(f))

print(manchots[0])
print(manchots[0]["body_mass_g"], type(manchots[0]["body_mass_g"]))
```

## Écrire et lire du JSON

Le JSON est le format des API web et des fichiers de configuration. Il ressemble aux dictionnaires Python.

```python
import json

config = {"modele": "regression", "epoques": 100, "taux": 0.01}
with open("config.json", "w") as f:
    json.dump(config, f, indent=2)

with open("config.json") as f:
    relu = json.load(f)
print(relu["epoques"])
```

## Gérer les erreurs avec try / except

Les vraies données sont sales : valeurs vides, texte au lieu de nombres. `try / except` permet de traiter le problème au lieu de tout arrêter.

```python
def en_nombre(texte):
    try:
        return float(texte)
    except ValueError:
        return None

print(en_nombre("3750"), en_nombre(""), en_nombre("NA"))
```

> **À retenir** : attrape une erreur **précise** (`ValueError`, `KeyError`...) plutôt qu'un `except:` nu, qui cacherait aussi tes vrais bugs.
''',
"exercises": [
 {"id": "e-1-6-a", "title": "Compter les espèces",
  "prompt": "Lis `penguins.csv` avec `csv.DictReader` et crée un dictionnaire `especes` qui compte le nombre de manchots par espèce (colonne `species`).",
  "starter": "import csv\n\n",
  "solution": 'import csv\n\nwith open("penguins.csv") as f:\n    lignes = list(csv.DictReader(f))\n\nespeces = {}\nfor l in lignes:\n    especes[l["species"]] = especes.get(l["species"], 0) + 1\nprint(especes)\n',
  "hint": "Reprends la méthode de comptage avec .get(cle, 0) + 1 de la leçon sur les dictionnaires.",
  "check": 'assert especes == {"Adelie": 152, "Chinstrap": 68, "Gentoo": 124}, f"especes vaut {especes}."\n'},
 {"id": "e-1-6-b", "title": "Masse moyenne en ignorant les vides",
  "prompt": "Calcule `masse_moyenne`, la masse moyenne (colonne `body_mass_g`) des manchots, en **ignorant** les valeurs vides. Utilise une fonction de conversion avec `try / except`.",
  "starter": "import csv\n\ndef en_nombre(texte):\n    pass\n",
  "solution": 'import csv\n\ndef en_nombre(texte):\n    try:\n        return float(texte)\n    except ValueError:\n        return None\n\nwith open("penguins.csv") as f:\n    lignes = list(csv.DictReader(f))\n\nmasses = [en_nombre(l["body_mass_g"]) for l in lignes]\nmasses = [m for m in masses if m is not None]\nmasse_moyenne = sum(masses) / len(masses)\nprint(round(masse_moyenne, 1))\n',
  "hint": "Convertis toutes les valeurs, garde celles qui ne sont pas None, puis fais sum / len.",
  "check": 'assert abs(masse_moyenne - 4201.754) < 0.01, f"masse_moyenne vaut {masse_moyenne}, j\'attendais environ 4201.75."\n'},
]},
# ---------------------------------------------------------------- 1.7
{"id": "l-1-7", "title": "Classes et objets", "minutes": 50,
"body": r'''
Tu n'écriras pas beaucoup de classes au début, mais tu en **utiliseras** tout le temps : un modèle scikit-learn, un DataFrame pandas, un tokenizer Hugging Face sont des objets. Comprendre les classes, c'est comprendre leur documentation.

Une **classe** est un plan de fabrication. Un **objet** est un exemplaire fabriqué à partir de ce plan. Il a des **attributs** (ses données) et des **méthodes** (ses fonctions).

```python
class Compteur:
    def __init__(self, nom):
        self.nom = nom          # attribut
        self.valeur = 0

    def incrementer(self, pas=1):   # méthode
        self.valeur += pas
        return self

c = Compteur("lecons")
c.incrementer()
c.incrementer(3)
print(c.nom, c.valeur)
```

`__init__` est appelé à la création de l'objet. `self` désigne l'objet lui-même : c'est toujours le premier paramètre d'une méthode.

## Le modèle fit / predict

Tous les modèles de scikit-learn suivent la même interface : `fit` apprend à partir des données, `predict` prédit. Voici un modèle minimal qui prédit toujours la moyenne. C'est ce qu'on appelle une **baseline**.

```python
class ModeleMoyenne:
    def fit(self, y):
        self.moyenne_ = sum(y) / len(y)    # le _ final : attribut appris
        return self

    def predict(self, n):
        return [self.moyenne_] * n

m = ModeleMoyenne().fit([3, 5, 10])
print(m.predict(2))
```

> **À retenir** : dans scikit-learn, les attributs appris pendant `fit` finissent par un tiret bas, comme `coef_` ou `intercept_`. Tu les reconnaîtras en semaine 4.
''',
"exercises": [
 {"id": "e-1-7-a", "title": "Un modèle médiane",
  "prompt": "Écris une classe `ModeleMediane` avec une méthode `fit(self, y)` qui stocke la médiane de `y` dans `self.mediane_` et renvoie `self`, et une méthode `predict(self, n)` qui renvoie une liste de `n` fois cette médiane. Médiane : trie les valeurs ; si leur nombre est impair, prends celle du milieu, sinon la moyenne des deux du milieu.",
  "starter": "class ModeleMediane:\n    def fit(self, y):\n        pass\n\n    def predict(self, n):\n        pass\n",
  "solution": "class ModeleMediane:\n    def fit(self, y):\n        s = sorted(y)\n        k = len(s) // 2\n        if len(s) % 2 == 1:\n            self.mediane_ = s[k]\n        else:\n            self.mediane_ = (s[k - 1] + s[k]) / 2\n        return self\n\n    def predict(self, n):\n        return [self.mediane_] * n\n\nprint(ModeleMediane().fit([5, 1, 9]).predict(3))\n",
  "hint": "len(s) // 2 donne l'indice du milieu. Pour une taille paire, moyenne de s[k-1] et s[k].",
  "check": 'm = ModeleMediane()\nassert m.fit([5, 1, 9]) is m, "fit doit renvoyer self."\nassert m.mediane_ == 5, f"Pour [5, 1, 9], mediane_ vaut {m.mediane_}, j\'attendais 5."\nassert m.predict(2) == [5, 5], "predict(2) doit renvoyer [5, 5]."\nassert ModeleMediane().fit([4, 1, 3, 10]).mediane_ == 3.5, "Pour [4, 1, 3, 10], la médiane est 3.5."\n'},
]},
# ---------------------------------------------------------------- 1.8
{"id": "l-1-8", "title": "Git et GitHub", "minutes": 60,
"body": r'''
**Git** enregistre l'historique de ton code : chaque *commit* est une photo de ton projet à un instant donné. **GitHub** héberge ces projets en ligne. C'est aussi ton **portfolio** : les recruteurs regarderont ton GitHub.

## Les notions à connaître

- **Dépôt (repository)** : un dossier suivi par Git.
- **Commit** : un enregistrement de modifications, avec un message qui explique ce qui a changé.
- **Branche** : une ligne de développement parallèle. `main` est la branche principale.
- **Remote** : la copie du dépôt sur GitHub, souvent appelée `origin`.

## Le cycle de base

```bash
git clone https://github.com/ton-pseudo/mon-projet.git   # copier un dépôt
cd mon-projet
# ... tu modifies des fichiers ...
git status                  # qu'est-ce qui a changé ?
git add analyse.py          # préparer ce fichier pour le commit
git commit -m "Ajoute le calcul des statistiques par espèce"
git push                    # envoyer sur GitHub
git pull                    # récupérer les changements distants
```

Pour démarrer un projet local : `git init`, puis crée un dépôt vide sur GitHub et relie-le avec `git remote add origin <url>` puis `git push -u origin main`.

## Les bonnes habitudes

- Des commits **petits et fréquents**, avec un message au présent qui dit ce que fait le commit.
- Un fichier **README.md** dans chaque projet : le problème traité, les données, comment lancer le code, les résultats.
- Un fichier **.gitignore** pour exclure ce qui ne doit pas être publié :

```bash
# .gitignore
.venv/
__pycache__/
.ipynb_checkpoints/
.env          # tes clés d'API : ne JAMAIS les publier
data/*.csv    # les gros fichiers de données
```

> **À retenir** : ne publie jamais une clé d'API ou un mot de passe sur GitHub, même dans un dépôt privé. Mets-les dans un fichier `.env` listé dans `.gitignore`.
''',
"tasks": [
  "Configurer Git : git config --global user.name et user.email",
  "Créer un dépôt « mise-a-niveau-ia » sur GitHub avec un README",
  "Le cloner sur ton ordinateur avec git clone",
  "Ajouter un fichier, faire un commit et un push",
  "Vérifier sur github.com que le fichier apparaît",
],
"exercises": []},
],
"project": {
"id": "p-1", "title": "Projet 1 · Statistiques du Titanic en Python pur",
"body": r'''
Objectif : écrire un script qui lit `titanic.csv` **sans pandas** et répond à trois questions. C'est l'occasion de mobiliser tout ce que tu as vu cette semaine : fichiers, boucles, dictionnaires et fonctions.

Colonnes utiles : `survived` (1 = survivant, 0 = non), `sex` (`male` ou `female`), `pclass` (classe 1, 2 ou 3), `age` (parfois vide).
''',
"exercises": [
 {"id": "e-p1-a", "title": "Taux de survie global",
  "prompt": "Charge le fichier dans une liste `passagers` (avec `csv.DictReader`), puis calcule `taux_global`, la proportion de survivants (un nombre entre 0 et 1).",
  "starter": "import csv\n\n",
  "solution": 'import csv\n\nwith open("titanic.csv") as f:\n    passagers = list(csv.DictReader(f))\n\nsurvivants = sum(int(p["survived"]) for p in passagers)\ntaux_global = survivants / len(passagers)\nprint(f"{len(passagers)} passagers, taux de survie : {taux_global:.1%}")\n',
  "hint": "int(p[\"survived\"]) vaut 0 ou 1 : leur somme donne le nombre de survivants.",
  "check": 'assert len(passagers) == 891, f"passagers contient {len(passagers)} lignes, j\'attendais 891."\nassert abs(taux_global - 0.3838) < 0.001, f"taux_global vaut {taux_global}, j\'attendais environ 0.384."\n'},
 {"id": "e-p1-b", "title": "Taux de survie par groupe",
  "prompt": "Écris une fonction `taux_par(passagers, colonne)` qui renvoie un dictionnaire `{valeur: taux de survie}` pour chaque valeur de la colonne. Teste-la avec `\"sex\"` puis `\"pclass\"`.",
  "starter": "import csv\n\nwith open(\"titanic.csv\") as f:\n    passagers = list(csv.DictReader(f))\n\ndef taux_par(passagers, colonne):\n    pass\n",
  "solution": 'import csv\n\nwith open("titanic.csv") as f:\n    passagers = list(csv.DictReader(f))\n\ndef taux_par(passagers, colonne):\n    total, survie = {}, {}\n    for p in passagers:\n        v = p[colonne]\n        total[v] = total.get(v, 0) + 1\n        survie[v] = survie.get(v, 0) + int(p["survived"])\n    return {v: survie[v] / total[v] for v in total}\n\nprint(taux_par(passagers, "sex"))\nprint(taux_par(passagers, "pclass"))\n',
  "hint": "Tiens deux dictionnaires : le nombre total par valeur et le nombre de survivants par valeur. Divise à la fin.",
  "check": 'r = taux_par(passagers, "sex")\nassert set(r) == {"male", "female"}, f"Clés obtenues : {set(r)}."\nassert abs(r["female"] - 0.742) < 0.001 and abs(r["male"] - 0.189) < 0.001, f"Taux par sexe : {r}."\nc = taux_par(passagers, "pclass")\nassert abs(c["1"] - 0.6296) < 0.001 and abs(c["3"] - 0.2424) < 0.001, f"Taux par classe : {c}."\n'},
 {"id": "e-p1-c", "title": "Âge moyen des survivants",
  "prompt": "Calcule `age_survivants` et `age_victimes`, l'âge moyen des survivants et des victimes, en ignorant les âges vides.",
  "starter": "import csv\n\nwith open(\"titanic.csv\") as f:\n    passagers = list(csv.DictReader(f))\n",
  "solution": 'import csv\n\nwith open("titanic.csv") as f:\n    passagers = list(csv.DictReader(f))\n\ndef age_moyen(groupe):\n    ages = [float(p["age"]) for p in groupe if p["age"] != ""]\n    return sum(ages) / len(ages)\n\nage_survivants = age_moyen([p for p in passagers if p["survived"] == "1"])\nage_victimes = age_moyen([p for p in passagers if p["survived"] == "0"])\nprint(round(age_survivants, 1), round(age_victimes, 1))\n',
  "hint": "Filtre d'abord les passagers par survie, puis ignore ceux dont p[\"age\"] vaut \"\".",
  "check": 'assert abs(age_survivants - 28.34) < 0.01, f"age_survivants vaut {age_survivants}."\nassert abs(age_victimes - 30.63) < 0.01, f"age_victimes vaut {age_victimes}."\n'},
],
"tasks": [
  "Copier ton code dans un fichier titanic_stats.py sur ton ordinateur",
  "Le lancer avec python titanic_stats.py",
  "Écrire un README qui présente les 3 résultats en une phrase chacun",
  "Publier le projet sur GitHub",
]},
"quiz": [
 {"q": "Que vaut 17 // 5 en Python ?", "options": ["3.4", "3", "2", "4"], "answer": 1,
  "explain": "// est la division entière : 17 = 5 × 3 + 2, donc 3. Le reste (2) s'obtient avec 17 % 5."},
 {"q": "Quel est le premier élément de la liste l = ['a', 'b', 'c'] ?", "options": ["l[1]", "l[0]", "l[-0]", "l.first()"], "answer": 1,
  "explain": "Les indices commencent à 0 en Python. l[-1] donne le dernier élément."},
 {"q": "Que renvoie une fonction qui n'a pas d'instruction return ?", "options": ["0", "Une erreur", "None", "La dernière valeur calculée"], "answer": 2,
  "explain": "Sans return, une fonction renvoie None. C'est une erreur fréquente : print affiche, mais ne renvoie rien."},
 {"q": "Quelle expression construit la liste des carrés des nombres pairs de nums ?", "options": ["[n**2 if n % 2 == 0 for n in nums]", "[n**2 for n in nums if n % 2 == 0]", "[for n in nums: n**2]", "{n**2 for n in nums}"], "answer": 1,
  "explain": "La forme est [expression for élément in séquence if condition]. La dernière option crée un set, pas une liste."},
 {"q": "Avec d = {'a': 1}, que renvoie d.get('b', 0) ?", "options": ["Une KeyError", "None", "0", "'b'"], "answer": 2,
  "explain": "get renvoie la valeur par défaut fournie quand la clé est absente, sans lever d'erreur, contrairement à d['b']."},
 {"q": "Quelle commande envoie tes commits locaux vers GitHub ?", "options": ["git commit", "git push", "git pull", "git add"], "answer": 1,
  "explain": "add prépare les fichiers, commit enregistre localement, push envoie vers le dépôt distant, pull récupère."},
 {"q": "Où doit-on stocker une clé d'API dans un projet ?", "options": ["Dans le README", "En dur dans le code", "Dans un fichier .env ignoré par Git", "Dans le nom du dépôt"], "answer": 2,
  "explain": "Les secrets vont dans un fichier .env listé dans .gitignore, pour ne jamais être publiés."},
 {"q": "Dans scikit-learn, que signale le tiret bas final de model.coef_ ?", "options": ["Un attribut privé", "Un attribut appris pendant fit", "Une méthode", "Une variable globale"], "answer": 1,
  "explain": "Par convention, les attributs appris lors de l'entraînement (fit) se terminent par un tiret bas."},
]}
