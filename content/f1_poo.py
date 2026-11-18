LESSONS = [
# ---------------------------------------------------------------- POO 1
{"id": "l-oop-1", "title": "Programmation orientée objet", "minutes": 90,
"body": r'''
Chez Jedha, le module « Bonnes pratiques Python » consacre deux cours à la POO, et la leçon « Pourquoi la POO est importante pour l'IA » explique pourquoi : tous les outils que tu vas utiliser (scikit-learn, PyTorch, Hugging Face, LangChain) sont construits avec des classes. Savoir lire et écrire une classe propre, c'est savoir lire leur documentation et leur code source.

```viz oop
```

## Une classe, des objets

Une **classe** décrit un type d'objet : ses **attributs** (ses données) et ses **méthodes** (ce qu'il sait faire). Chaque **objet** créé à partir de la classe a ses propres valeurs.

```python
class Article:
    tva = 0.20                       # attribut de classe : partagé par tous les articles

    def __init__(self, nom, prix_ht, quantite=1):
        self.nom = nom               # attributs d'instance : propres à chaque objet
        self.prix_ht = prix_ht
        self.quantite = quantite

    def total_ttc(self):
        return round(self.prix_ht * self.quantite * (1 + self.tva), 2)

stylo = Article("Stylo", 1.5, 10)
cahier = Article("Cahier", 3.2)
print(stylo.total_ttc(), cahier.total_ttc())
print(isinstance(stylo, Article), type(cahier).__name__)
```

## Les méthodes spéciales (dunder)

Les méthodes entourées de doubles tirets bas, comme `__init__`, permettent à tes objets de se comporter comme des objets Python natifs : s'afficher, se comparer, avoir une longueur, s'additionner.

```python
class Panier:
    def __init__(self):
        self.articles = []

    def ajouter(self, article):
        self.articles.append(article)
        return self                          # permet d'enchaîner les appels

    def __len__(self):                       # len(panier)
        return sum(a.quantite for a in self.articles)

    def __repr__(self):                      # affichage dans la console
        return f"Panier({len(self.articles)} lignes, {len(self)} articles)"

    def __iter__(self):                      # for article in panier
        return iter(self.articles)

p = Panier().ajouter(stylo).ajouter(cahier)
print(len(p))
for a in p:
    print("-", a.nom)
p
```

C'est exactement ce qui se passe quand tu fais `len(df)` sur un DataFrame ou `for batch in dataloader` en PyTorch : ces classes définissent `__len__` et `__iter__`.

## Héritage

Une classe peut **hériter** d'une autre : elle récupère tout son comportement et peut en modifier une partie. `super()` appelle la version de la classe parente.

```python
class ArticleSolde(Article):
    def __init__(self, nom, prix_ht, quantite=1, remise=0.3):
        super().__init__(nom, prix_ht, quantite)
        self.remise = remise

    def total_ttc(self):                     # on redéfinit (override) la méthode
        return round(super().total_ttc() * (1 - self.remise), 2)

sac = ArticleSolde("Sac", 40, remise=0.25)
print(sac.total_ttc(), isinstance(sac, Article))
```

Le code qui manipule des `Article` fonctionne aussi avec des `ArticleSolde` sans rien changer : c'est le **polymorphisme**. scikit-learn en est l'exemple parfait : `fit` et `predict` existent sur tous les modèles, quelle que soit leur classe.

## Composition plutôt qu'héritage

L'héritage exprime « est un » (un `ArticleSolde` est un `Article`). La **composition** exprime « a un » : un `Panier` a des articles. En pratique, on compose bien plus souvent qu'on hérite. Une `Pipeline` scikit-learn, par exemple, *contient* des étapes.

> **À retenir** : une classe = des données + les fonctions qui les manipulent. Hérite pour spécialiser un comportement, compose pour assembler des briques.
''',
"exercises": [
 {"id": "e-oop-1-a", "title": "Un compte bancaire",
  "prompt": "Écris une classe `Compte` avec : `__init__(self, titulaire, solde=0)`, une méthode `deposer(montant)`, une méthode `retirer(montant)` qui lève une `ValueError` si le solde est insuffisant, et `__repr__` qui renvoie exactement `Compte(Sam, 120.0 €)` pour un compte de Sam avec 120 euros.",
  "starter": "class Compte:\n    pass\n",
  "solution": 'class Compte:\n    def __init__(self, titulaire, solde=0):\n        self.titulaire = titulaire\n        self.solde = float(solde)\n\n    def deposer(self, montant):\n        self.solde += montant\n\n    def retirer(self, montant):\n        if montant > self.solde:\n            raise ValueError("Solde insuffisant")\n        self.solde -= montant\n\n    def __repr__(self):\n        return f"Compte({self.titulaire}, {self.solde} €)"\n\nc = Compte("Sam", 100)\nc.deposer(20)\nc\n',
  "hint": "raise ValueError(\"...\") lève une erreur. Dans __repr__, utilise une f-string avec self.titulaire et self.solde.",
  "check": 'c = Compte("Sam", 100)\nc.deposer(20)\nassert repr(c) == "Compte(Sam, 120.0 €)", f"repr(c) vaut {repr(c)!r}."\ntry:\n    c.retirer(500)\n    assert False, "retirer(500) aurait dû lever une ValueError."\nexcept ValueError:\n    pass\nc.retirer(20)\nassert c.solde == 100, "Après retirer(20), le solde devrait être 100."\n'},
 {"id": "e-oop-1-b", "title": "Un dataset itérable",
  "prompt": "Écris une classe `MiniDataset` qui reçoit une liste `X` et une liste `y` de même longueur. `len(ds)` doit renvoyer le nombre d'exemples, `ds[i]` le tuple `(X[i], y[i])` (méthode `__getitem__`), et le constructeur doit lever une `ValueError` si les longueurs diffèrent. C'est exactement l'interface d'un `Dataset` PyTorch.",
  "starter": "class MiniDataset:\n    pass\n",
  "solution": 'class MiniDataset:\n    def __init__(self, X, y):\n        if len(X) != len(y):\n            raise ValueError("X et y doivent avoir la même longueur")\n        self.X, self.y = X, y\n\n    def __len__(self):\n        return len(self.X)\n\n    def __getitem__(self, i):\n        return self.X[i], self.y[i]\n\nds = MiniDataset([[1, 2], [3, 4], [5, 6]], [0, 1, 0])\nprint(len(ds), ds[1])\nfor x, cible in ds:\n    print(x, cible)\n',
  "hint": "Trois méthodes : __init__, __len__ et __getitem__(self, i). Avec __getitem__, la boucle for fonctionne aussi.",
  "check": 'ds = MiniDataset([[1, 2], [3, 4], [5, 6]], [0, 1, 0])\nassert len(ds) == 3, "len(ds) devrait valoir 3."\nassert ds[1] == ([3, 4], 1), f"ds[1] vaut {ds[1]!r}."\nassert [c for _, c in ds] == [0, 1, 0], "On doit pouvoir parcourir le dataset avec for."\ntry:\n    MiniDataset([1, 2], [1])\n    assert False, "Des longueurs différentes doivent lever une ValueError."\nexcept ValueError:\n    pass\n'},
 {"id": "e-oop-1-c", "title": "Polymorphisme : des formes",
  "prompt": "Crée une classe `Forme` avec une méthode `aire()` qui lève `NotImplementedError`, puis deux classes filles `Rectangle(largeur, hauteur)` et `Cercle(rayon)` qui la redéfinissent (utilise `math.pi`). Enfin, crée `aire_totale`, la somme des aires des formes de la liste `formes`.",
  "starter": "import math\n\n# tes classes ici\n\nformes = [Rectangle(2, 3), Cercle(1), Rectangle(1, 1)]\n",
  "solution": 'import math\n\nclass Forme:\n    def aire(self):\n        raise NotImplementedError\n\nclass Rectangle(Forme):\n    def __init__(self, largeur, hauteur):\n        self.largeur, self.hauteur = largeur, hauteur\n\n    def aire(self):\n        return self.largeur * self.hauteur\n\nclass Cercle(Forme):\n    def __init__(self, rayon):\n        self.rayon = rayon\n\n    def aire(self):\n        return math.pi * self.rayon ** 2\n\nformes = [Rectangle(2, 3), Cercle(1), Rectangle(1, 1)]\naire_totale = sum(f.aire() for f in formes)\nprint(round(aire_totale, 3))\n',
  "hint": "class Rectangle(Forme): ... La somme se fait sans tester le type de chaque forme : c'est le polymorphisme.",
  "check": 'import math\nassert issubclass(Rectangle, Forme) and issubclass(Cercle, Forme), "Rectangle et Cercle doivent hériter de Forme."\ntry:\n    Forme().aire()\n    assert False, "Forme().aire() doit lever NotImplementedError."\nexcept NotImplementedError:\n    pass\nassert abs(aire_totale - (7 + math.pi)) < 1e-9, f"aire_totale vaut {aire_totale}."\n'},
]},
# ---------------------------------------------------------------- POO 2
{"id": "l-oop-2", "title": "POO avancée : dataclasses, propriétés, classes abstraites", "minutes": 90,
"body": r'''
Ces outils rendent ton code plus court, plus sûr et plus lisible. Tu les retrouveras partout dans le code professionnel, notamment dans FastAPI et Pydantic, qui reposent sur les annotations de type.

## Les annotations de type

Elles indiquent le type attendu des paramètres et du retour. Python ne les vérifie pas à l'exécution, mais ton éditeur et les outils comme `mypy` s'en servent pour détecter les erreurs.

```python
def moyenne_ponderee(valeurs: list[float], poids: list[float]) -> float:
    return sum(v * p for v, p in zip(valeurs, poids)) / sum(poids)

moyenne_ponderee([12, 15, 9], [1, 2, 1])
```

## Les dataclasses

`@dataclass` écrit pour toi `__init__`, `__repr__` et `__eq__` à partir des attributs annotés.

```python
from dataclasses import dataclass, field

@dataclass
class Experience:
    nom: str
    taux_apprentissage: float = 0.01
    epoques: int = 10
    tags: list[str] = field(default_factory=list)   # jamais de liste mutable comme valeur par défaut directe

e1 = Experience("baseline")
e2 = Experience("rapide", taux_apprentissage=0.1, tags=["test"])
print(e1)
print(e1 == Experience("baseline"))
```

`@dataclass(frozen=True)` rend l'objet immuable : pratique pour une configuration qui ne doit pas changer.

## Les propriétés

Une **propriété** ressemble à un attribut mais exécute du code : pour calculer une valeur à la volée, ou pour **valider** une affectation.

```python
class Temperature:
    def __init__(self, celsius: float):
        self.celsius = celsius            # passe par le setter ci-dessous

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, valeur: float):
        if valeur < -273.15:
            raise ValueError("En dessous du zéro absolu !")
        self._celsius = valeur

    @property
    def fahrenheit(self) -> float:        # propriété calculée, en lecture seule
        return self._celsius * 9 / 5 + 32

t = Temperature(25)
print(t.fahrenheit)
try:
    t.celsius = -300
except ValueError as err:
    print("Refusé :", err)
```

## Méthodes de classe et méthodes statiques

```python
class Modele:
    def __init__(self, params: dict):
        self.params = params

    @classmethod
    def depuis_json(cls, texte: str) -> "Modele":     # constructeur alternatif
        import json
        return cls(json.loads(texte))

    @staticmethod
    def version() -> str:                             # n'utilise ni self ni cls
        return "1.0"

m = Modele.depuis_json('{"profondeur": 3}')
print(m.params, Modele.version())
```

`AutoModel.from_pretrained(...)` chez Hugging Face est une méthode de classe de ce type.

## Les classes abstraites

Une **classe abstraite** définit un contrat : toute classe fille doit implémenter certaines méthodes, sinon on ne peut pas l'instancier.

```python
from abc import ABC, abstractmethod

class Estimateur(ABC):
    @abstractmethod
    def fit(self, X, y): ...

    @abstractmethod
    def predict(self, X): ...

    def fit_predict(self, X, y):          # méthode concrète, partagée par toutes les filles
        return self.fit(X, y).predict(X)

class Constant(Estimateur):
    def fit(self, X, y):
        self.valeur_ = max(set(y), key=y.count)
        return self

    def predict(self, X):
        return [self.valeur_] * len(X)

print(Constant().fit_predict([[1], [2], [3]], ["a", "b", "a"]))
try:
    Estimateur()
except TypeError as err:
    print("Impossible :", err)
```

> **À retenir** : `@dataclass` pour les objets qui portent surtout des données, `@property` pour valider ou calculer, `ABC` pour imposer une interface commune à plusieurs implémentations.
''',
"exercises": [
 {"id": "e-oop-2-a", "title": "Une commande en dataclass",
  "prompt": "Crée deux dataclasses : `Ligne(produit: str, prix: float, quantite: int = 1)` avec une propriété `total` (prix × quantité), et `Commande(client: str, lignes: list[Ligne])` (liste vide par défaut, avec `field(default_factory=list)`) avec une propriété `montant` (somme des totaux, arrondie à 2 décimales).",
  "starter": "from dataclasses import dataclass, field\n",
  "solution": 'from dataclasses import dataclass, field\n\n@dataclass\nclass Ligne:\n    produit: str\n    prix: float\n    quantite: int = 1\n\n    @property\n    def total(self) -> float:\n        return self.prix * self.quantite\n\n@dataclass\nclass Commande:\n    client: str\n    lignes: list[Ligne] = field(default_factory=list)\n\n    @property\n    def montant(self) -> float:\n        return round(sum(l.total for l in self.lignes), 2)\n\nc = Commande("Sam", [Ligne("Clavier", 49.9), Ligne("Souris", 19.95, 2)])\nprint(c, c.montant)\n',
  "hint": "Une propriété dans une dataclass s'écrit comme dans une classe normale, avec @property.",
  "check": 'import dataclasses\nassert dataclasses.is_dataclass(Ligne) and dataclasses.is_dataclass(Commande), "Ligne et Commande doivent être des dataclasses."\nc = Commande("Sam", [Ligne("Clavier", 49.9), Ligne("Souris", 19.95, 2)])\nassert c.montant == 89.8, f"montant vaut {c.montant}, j\'attendais 89.8."\na, b = Commande("A"), Commande("B")\na.lignes.append(Ligne("x", 1))\nassert b.lignes == [], "Les commandes partagent la même liste : utilise field(default_factory=list)."\nassert Ligne("x", 2.0, 3) == Ligne("x", 2.0, 3), "Deux lignes identiques doivent être égales (c\'est le rôle de @dataclass)."\n'},
 {"id": "e-oop-2-b", "title": "Valider avec une propriété",
  "prompt": "Écris une classe `Probabilite` dont l'attribut `valeur` est une propriété : son setter lève une `ValueError` si la valeur n'est pas entre 0 et 1. Ajoute une propriété en lecture seule `cote` qui renvoie `valeur / (1 - valeur)`.",
  "starter": "class Probabilite:\n    def __init__(self, valeur):\n        self.valeur = valeur\n",
  "solution": 'class Probabilite:\n    def __init__(self, valeur):\n        self.valeur = valeur\n\n    @property\n    def valeur(self):\n        return self._valeur\n\n    @valeur.setter\n    def valeur(self, v):\n        if not 0 <= v <= 1:\n            raise ValueError("Une probabilité doit être entre 0 et 1")\n        self._valeur = v\n\n    @property\n    def cote(self):\n        return self._valeur / (1 - self._valeur)\n\nprint(Probabilite(0.75).cote)\n',
  "hint": "Stocke la vraie valeur dans self._valeur, et passe par @property / @valeur.setter.",
  "check": 'p = Probabilite(0.75)\nassert abs(p.cote - 3) < 1e-9, f"cote vaut {p.cote}, j\'attendais 3."\nfor mauvais in [1.5, -0.1]:\n    try:\n        Probabilite(mauvais)\n        assert False, f"Probabilite({mauvais}) devrait lever une ValueError."\n    except ValueError:\n        pass\ntry:\n    p.valeur = 2\n    assert False, "Modifier valeur avec 2 devrait aussi lever une ValueError."\nexcept ValueError:\n    pass\n'},
 {"id": "e-oop-2-c", "title": "Ton propre estimateur",
  "prompt": "En héritant de `Estimateur` (fourni), écris `PlusProcheMoyenne` : un classifieur qui, dans `fit(X, y)`, calcule le **centre** (moyenne coordonnée par coordonnée) de chaque classe et le stocke dans `self.centres_` (un dictionnaire classe → liste), puis qui, dans `predict(X)`, renvoie pour chaque point la classe du centre le plus proche (distance euclidienne).",
  "starter": 'from abc import ABC, abstractmethod\n\nclass Estimateur(ABC):\n    @abstractmethod\n    def fit(self, X, y): ...\n    @abstractmethod\n    def predict(self, X): ...\n\nclass PlusProcheMoyenne(Estimateur):\n    pass\n\nX = [[1, 1], [1, 2], [8, 8], [9, 8]]\ny = ["bas", "bas", "haut", "haut"]\n',
  "solution": 'from abc import ABC, abstractmethod\nimport math\n\nclass Estimateur(ABC):\n    @abstractmethod\n    def fit(self, X, y): ...\n    @abstractmethod\n    def predict(self, X): ...\n\nclass PlusProcheMoyenne(Estimateur):\n    def fit(self, X, y):\n        self.centres_ = {}\n        for classe in set(y):\n            points = [x for x, c in zip(X, y) if c == classe]\n            self.centres_[classe] = [sum(col) / len(points) for col in zip(*points)]\n        return self\n\n    def predict(self, X):\n        return [min(self.centres_, key=lambda c: math.dist(x, self.centres_[c])) for x in X]\n\nX = [[1, 1], [1, 2], [8, 8], [9, 8]]\ny = ["bas", "bas", "haut", "haut"]\nm = PlusProcheMoyenne().fit(X, y)\nprint(m.centres_, m.predict([[2, 2], [7, 9]]))\n',
  "hint": "zip(*points) regroupe les coordonnées par colonne. math.dist(a, b) calcule la distance euclidienne.",
  "check": 'X = [[1, 1], [1, 2], [8, 8], [9, 8]]\ny = ["bas", "bas", "haut", "haut"]\nm = PlusProcheMoyenne()\nassert m.fit(X, y) is m, "fit doit renvoyer self."\nassert m.centres_["bas"] == [1.0, 1.5] and m.centres_["haut"] == [8.5, 8.0], f"centres_ vaut {m.centres_}."\nassert m.predict([[2, 2], [7, 9], [0, 0]]) == ["bas", "haut", "bas"], f"predict renvoie {m.predict([[2, 2], [7, 9], [0, 0]])}."\n'},
]},
# ---------------------------------------------------------------- Markdown
{"id": "l-md", "title": "Markdown et README qui donnent envie", "minutes": 45,
"body": r'''
Le **Markdown** est le format de texte des README, des notebooks Jupyter, de la documentation et de… cette plateforme. Un recruteur passe en moyenne moins d'une minute sur un dépôt : le README est ta vitrine.

## La syntaxe essentielle

```markdown
# Titre de niveau 1
## Titre de niveau 2

Du texte en **gras**, en *italique*, et du `code` en ligne.

- une liste à puces
- un deuxième point

1. une liste numérotée
2. deuxième étape

[un lien](https://www.jedha.co)   ![une image](images/courbe.png)

| Modèle | Exactitude |
| --- | --- |
| Baseline | 0.62 |
| Régression logistique | 0.80 |
```

Pour du code sur plusieurs lignes, on l'entoure de trois accents graves suivis du nom du langage.

## La structure d'un bon README de projet

1. **Un titre et une phrase** qui disent ce que fait le projet et pour qui.
2. **Un visuel** : capture d'écran, graphique clé ou GIF de démo.
3. **Les résultats** en chiffres, comparés à une baseline.
4. **Comment le lancer** : installation et commande, copiables-collables.
5. **Les données** : source, taille, licence.
6. **La démarche** : les choix importants et leurs raisons.
7. **Les limites et les pistes d'amélioration** : c'est là que tu montres ta maturité.

> **À retenir** : écris tes README en anglais, au présent, et mets les résultats en haut. Un recruteur doit comprendre en 30 secondes ce que tu as fait et à quel point ça marche.
''',
"tasks": [
  "Ajouter un README complet à ton dépôt « mise-a-niveau-ia » en suivant les 7 points",
  "Créer ton README de profil GitHub (un dépôt qui porte ton nom d'utilisateur)",
  "Épingler tes 3 meilleurs dépôts sur ton profil",
],
"exercises": []},
]

QUIZZES = {
"quiz-oop": {"title": "Quiz · Bonnes pratiques Python", "questions": [
 {"q": "Que fait le décorateur @dataclass ?", "options": ["Il rend la classe plus rapide", "Il génère __init__, __repr__ et __eq__ à partir des attributs annotés", "Il enregistre l'objet dans une base de données", "Il rend les attributs privés"], "answer": 1,
  "explain": "@dataclass écrit pour toi le code répétitif d'une classe qui porte des données."},
 {"q": "Pourquoi ne faut-il pas écrire tags: list = [] dans une dataclass ?", "options": ["C'est une erreur de syntaxe", "Tous les objets partageraient la même liste", "Les listes sont interdites", "Ça ralentit le code"], "answer": 1,
  "explain": "La valeur par défaut serait créée une seule fois et partagée. On utilise field(default_factory=list)."},
 {"q": "Quelle méthode permet d'utiliser len(obj) sur ton objet ?", "options": ["__size__", "__len__", "length()", "__count__"], "answer": 1,
  "explain": "len(obj) appelle obj.__len__(). C'est ce que font les Dataset PyTorch et les DataFrame."},
 {"q": "Que fait super().__init__(...) dans une classe fille ?", "options": ["Il crée une nouvelle classe", "Il appelle le constructeur de la classe parente", "Il supprime l'objet", "Il rend la méthode abstraite"], "answer": 1,
  "explain": "super() donne accès aux méthodes de la classe parente, ici pour réutiliser son initialisation."},
 {"q": "Une classe héritant d'ABC avec une méthode @abstractmethod non implémentée…", "options": ["s'instancie normalement", "ne peut pas être instanciée", "devient une dataclass", "lève une erreur à l'import"], "answer": 1,
  "explain": "Python refuse d'instancier une classe qui n'implémente pas toutes ses méthodes abstraites (TypeError)."},
 {"q": "AutoModel.from_pretrained(...) chez Hugging Face est un exemple de :", "options": ["Méthode statique", "Méthode de classe servant de constructeur alternatif", "Propriété", "Fonction lambda"], "answer": 1,
  "explain": "Une @classmethod reçoit la classe (cls) et renvoie une nouvelle instance, construite autrement qu'avec __init__."},
 {"q": "Quelle relation exprime la composition ?", "options": ["« est un »", "« a un »", "« hérite de »", "« remplace »"], "answer": 1,
  "explain": "Un Panier a des Articles, une Pipeline a des étapes : c'est de la composition."},
 {"q": "À quoi sert une @property avec un setter ?", "options": ["À rendre l'attribut global", "À exécuter du code (validation, calcul) lors de la lecture ou de l'affectation", "À accélérer l'accès", "À cacher la classe"], "answer": 1,
  "explain": "On garde la syntaxe d'un attribut (obj.valeur = 2) tout en validant la valeur."},
]},
}
