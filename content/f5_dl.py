"""FullStack · Fondation pour l'apprentissage profond (vague 4) : neurones, perceptron, rétropropagation, PyTorch, convolutions, embeddings."""

def E(id, title, prompt, starter, solution, check, hint):
    return {"id": id, "title": title, "prompt": prompt, "starter": starter, "solution": solution, "check": check, "hint": hint}

XOR = "import numpy as np\nX = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)\ny = np.array([[0], [1], [1], [0]], dtype=float)\n"

LESSONS = [
# ================================================================ Intro DL
{"id": "l-dl-intro", "title": "Le neurone, les couches et les fonctions d'activation", "minutes": 80,
"body": r'''
Un réseau de neurones est une fonction construite en empilant des opérations très simples. Comprendre ces briques, c'est pouvoir lire n'importe quelle architecture, du perceptron au Transformer.

## Un neurone

Un neurone artificiel fait trois choses : il multiplie chaque entrée par un **poids**, additionne le tout avec un **biais**, puis applique une **fonction d'activation** non linéaire.

```latex
a = f\Big(\sum_j w_j x_j + b\Big) = f(w \cdot x + b)
```

```viz neuron
```

## Pourquoi une activation non linéaire

Sans activation, empiler des couches ne sert à rien : une suite de transformations linéaires reste une transformation linéaire. L'activation permet au réseau d'apprendre des frontières courbes.

| Activation | Formule | Usage |
| --- | --- | --- |
| **ReLU** | max(0, z) | Couches cachées : simple, rapide, le choix par défaut |
| **Sigmoïde** | 1 / (1 + e⁻ᶻ) | Sortie d'une classification binaire (une probabilité) |
| **Tanh** | (eᶻ − e⁻ᶻ) / (eᶻ + e⁻ᶻ) | Couches cachées, sortie centrée entre −1 et 1 |
| **Softmax** | eᶻⁱ / Σ eᶻʲ | Sortie d'une classification à plusieurs classes |

```python
import numpy as np
z = np.linspace(-4, 4, 9)
print("z      ", z)
print("ReLU   ", np.maximum(0, z))
print("sigmoïde", (1 / (1 + np.exp(-z))).round(3))
print("tanh   ", np.tanh(z).round(3))
```

## Une couche, puis un réseau

Une **couche dense** applique plusieurs neurones aux mêmes entrées : c'est un produit matriciel. Pour un lot (*batch*) de n exemples à d variables, avec une couche de k neurones :

```latex
H = f(XW + b) \qquad X : (n, d) \quad W : (d, k) \quad b : (k,) \quad H : (n, k)
```

```python
rng = np.random.default_rng(0)
X = rng.normal(size=(5, 3))                 # 5 exemples, 3 variables
W1, b1 = rng.normal(size=(3, 4)), np.zeros(4)
W2, b2 = rng.normal(size=(4, 1)), np.zeros(1)
H = np.maximum(0, X @ W1 + b1)              # couche cachée : 4 neurones, ReLU
sortie = 1 / (1 + np.exp(-(H @ W2 + b2)))   # couche de sortie : une probabilité
print(H.shape, sortie.shape)
sortie.ravel().round(3)
```

Ce calcul de l'entrée vers la sortie s'appelle la **propagation avant** (*forward pass*).

## La fonction de coût

Pour apprendre, il faut mesurer l'erreur. En classification, on utilise l'**entropie croisée** (*cross-entropy*) : elle punit fortement une prédiction confiante et fausse.

```latex
L = -\frac{1}{n} \sum_i \big[ y_i \log p_i + (1 - y_i) \log(1 - p_i) \big]
```

```python
y = np.array([1, 0, 1])
for p in [np.array([0.9, 0.1, 0.8]), np.array([0.6, 0.4, 0.5]), np.array([0.1, 0.9, 0.2])]:
    L = -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))
    print(p, "→ perte", round(L, 3))
```

> **À retenir** : neurone = produit scalaire + biais + activation. Couche = produit matriciel. Réseau = couches empilées. Apprendre = ajuster les poids pour réduire la fonction de coût, par descente de gradient.
''',
"exercises": [
 E("e-dl-intro-a", "Les activations et leurs dérivées",
   "Écris `sigmoide(z)`, `relu(z)` et leurs dérivées `d_sigmoide(z)` et `d_relu(z)` pour des tableaux NumPy. Rappel : σ'(z) = σ(z)(1 − σ(z)) ; la dérivée de ReLU vaut 1 si z > 0, 0 sinon.",
   "import numpy as np\n\ndef sigmoide(z):\n    pass\n\ndef d_sigmoide(z):\n    pass\n\ndef relu(z):\n    pass\n\ndef d_relu(z):\n    pass\n",
   "import numpy as np\n\ndef sigmoide(z):\n    return 1 / (1 + np.exp(-z))\n\ndef d_sigmoide(z):\n    s = sigmoide(z)\n    return s * (1 - s)\n\ndef relu(z):\n    return np.maximum(0, z)\n\ndef d_relu(z):\n    return (z > 0).astype(float)\n\nz = np.array([-2.0, 0.0, 3.0])\nprint(sigmoide(z), d_sigmoide(z), relu(z), d_relu(z))\n",
   r'''import numpy as np
z = np.array([-2.0, -0.5, 0.0, 0.7, 3.0])
assert np.allclose(sigmoide(z), 1 / (1 + np.exp(-z))), "sigmoide est fausse."
assert np.allclose(relu(z), [0, 0, 0, 0.7, 3]), "relu est fausse."
h = 1e-6
assert np.allclose(d_sigmoide(z), (sigmoide(z + h) - sigmoide(z - h)) / (2 * h), atol=1e-6), "d_sigmoide ne correspond pas à la dérivée numérique."
assert np.allclose(d_relu(z), [0, 0, 0, 1, 1]), "d_relu doit valoir 1 si z > 0 et 0 sinon."
''',
   "np.maximum(0, z) pour ReLU ; (z > 0).astype(float) pour sa dérivée."),
 E("e-dl-intro-b", "Une propagation avant",
   "Écris `forward(X, W1, b1, W2, b2)` qui calcule un réseau à une couche cachée **tanh** et une sortie **softmax**, et renvoie les probabilités (n, k). Pour la stabilité, soustrais le maximum de chaque ligne avant l'exponentielle.",
   "import numpy as np\n\ndef forward(X, W1, b1, W2, b2):\n    pass\n\nrng = np.random.default_rng(1)\nX = rng.normal(size=(6, 4))\nW1, b1 = rng.normal(size=(4, 5)), np.zeros(5)\nW2, b2 = rng.normal(size=(5, 3)), np.zeros(3)\n",
   "import numpy as np\n\ndef forward(X, W1, b1, W2, b2):\n    H = np.tanh(X @ W1 + b1)\n    Z = H @ W2 + b2\n    Z = Z - Z.max(axis=1, keepdims=True)\n    E = np.exp(Z)\n    return E / E.sum(axis=1, keepdims=True)\n\nrng = np.random.default_rng(1)\nX = rng.normal(size=(6, 4))\nW1, b1 = rng.normal(size=(4, 5)), np.zeros(5)\nW2, b2 = rng.normal(size=(5, 3)), np.zeros(3)\nP = forward(X, W1, b1, W2, b2)\nprint(P.round(3), P.sum(axis=1))\n",
   r'''import numpy as np
P = forward(X, W1, b1, W2, b2)
assert P.shape == (6, 3), f"La sortie doit avoir la forme (6, 3) ; elle a {P.shape}."
assert np.allclose(P.sum(axis=1), 1), "Chaque ligne doit sommer à 1 (softmax par ligne : axis=1, keepdims=True)."
Z = np.tanh(X @ W1 + b1) @ W2 + b2
assert np.allclose(P, np.exp(Z) / np.exp(Z).sum(axis=1, keepdims=True)), "Les probabilités ne correspondent pas : tanh en couche cachée, softmax en sortie."
assert np.isfinite(forward(X * 1000, W1, b1, W2 * 1000, b2)).all(), "Avec de très grandes valeurs, pense à soustraire le maximum de chaque ligne."
''',
   "H = np.tanh(X @ W1 + b1) ; Z = H @ W2 + b2 ; softmax ligne par ligne avec axis=1, keepdims=True."),
 E("e-dl-intro-c", "L'entropie croisée multiclasse",
   "Écris `entropie_croisee(P, y)` : `P` contient les probabilités prédites (n, k) et `y` les indices des vraies classes (n,). Elle renvoie la moyenne de −log(probabilité de la vraie classe). Pour éviter log(0), limite les probabilités à [1e-12, 1] avec `np.clip`.",
   "import numpy as np\n\ndef entropie_croisee(P, y):\n    pass\n",
   "import numpy as np\n\ndef entropie_croisee(P, y):\n    p_vraie = np.clip(P[np.arange(len(y)), y], 1e-12, 1)\n    return -np.log(p_vraie).mean()\n\nP = np.array([[0.7, 0.2, 0.1], [0.1, 0.8, 0.1]])\nprint(entropie_croisee(P, np.array([0, 1])))\n",
   r'''import numpy as np
P = np.array([[0.7, 0.2, 0.1], [0.1, 0.8, 0.1], [0.3, 0.3, 0.4]])
y = np.array([0, 1, 2])
assert abs(entropie_croisee(P, y) - np.mean(-np.log([0.7, 0.8, 0.4]))) < 1e-9, f"entropie_croisee renvoie {entropie_croisee(P, y)}."
assert np.isfinite(entropie_croisee(np.array([[1.0, 0.0]]), np.array([1]))), "Une probabilité nulle ne doit pas donner l'infini : utilise np.clip."
''',
   "P[np.arange(len(y)), y] sélectionne, pour chaque ligne, la probabilité de la vraie classe."),
]},
# ================================================================ Perceptron
{"id": "l-dl-perceptron", "title": "Le perceptron, et sa limite", "minutes": 70,
"body": r'''
Le **perceptron** (Rosenblatt, 1958) est l'ancêtre de tous les réseaux de neurones : un seul neurone, avec une activation en marche d'escalier, qui sépare deux classes par une droite (un hyperplan en dimension plus grande).

```latex
\hat{y} = \begin{cases} 1 & \text{si } w \cdot x + b > 0 \\ 0 & \text{sinon} \end{cases}
```

## La règle d'apprentissage

On parcourt les exemples ; à chaque erreur, on déplace la droite vers le bon côté :

```latex
w \leftarrow w + \eta\,(y - \hat{y})\,x \qquad b \leftarrow b + \eta\,(y - \hat{y})
```

```python
import numpy as np

def entrainer_perceptron(X, y, epoques=20, eta=1.0):
    w, b = np.zeros(X.shape[1]), 0.0
    for _ in range(epoques):
        erreurs = 0
        for xi, yi in zip(X, y):
            pred = 1 if xi @ w + b > 0 else 0
            w += eta * (yi - pred) * xi
            b += eta * (yi - pred)
            erreurs += int(pred != yi)
        if erreurs == 0:
            break
    return w, b

X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
for nom, y in [("ET", [0, 0, 0, 1]), ("OU", [0, 1, 1, 1]), ("OU exclusif", [0, 1, 1, 0])]:
    w, b = entrainer_perceptron(X, np.array(y))
    pred = [(1 if x @ w + b > 0 else 0) for x in X]
    print(f"{nom:12} attendu {y}  prédit {pred}  {'✓' if pred == y else '✗'}")
```

## La limite : le OU exclusif

Le perceptron apprend ET et OU, mais pas le **OU exclusif** (XOR) : aucune droite ne sépare (0,1) et (1,0) de (0,0) et (1,1). Ce résultat, démontré par Minsky et Papert en 1969, a longtemps freiné la recherche.

```viz xor
```

La solution : **ajouter une couche cachée**. Le réseau transforme d'abord l'espace, dans lequel les classes deviennent séparables par une droite. C'est le **perceptron multicouche** (MLP), entraîné par **rétropropagation** : la leçon suivante.

> **À retenir** : un seul neurone = une frontière linéaire. Les couches cachées permettent d'apprendre des frontières non linéaires : c'est toute la puissance du deep learning.
''',
"exercises": [
 E("e-dl-perc-a", "Une classe Perceptron réutilisable",
   "Écris une classe `Perceptron(eta=1.0, epoques=20)` avec `fit(X, y)` (règle d'apprentissage de la leçon, arrêt quand une époque se passe sans erreur, renvoie `self`, stocke `w_` et `b_` et le nombre d'erreurs de chaque époque dans `erreurs_`) et `predict(X)` qui renvoie un tableau de 0 et de 1.",
   "import numpy as np\n\nclass Perceptron:\n    pass\n",
   "import numpy as np\n\nclass Perceptron:\n    def __init__(self, eta=1.0, epoques=20):\n        self.eta, self.epoques = eta, epoques\n\n    def fit(self, X, y):\n        self.w_, self.b_ = np.zeros(X.shape[1]), 0.0\n        self.erreurs_ = []\n        for _ in range(self.epoques):\n            n = 0\n            for xi, yi in zip(X, y):\n                pred = 1 if xi @ self.w_ + self.b_ > 0 else 0\n                self.w_ += self.eta * (yi - pred) * xi\n                self.b_ += self.eta * (yi - pred)\n                n += int(pred != yi)\n            self.erreurs_.append(n)\n            if n == 0:\n                break\n        return self\n\n    def predict(self, X):\n        return (X @ self.w_ + self.b_ > 0).astype(int)\n\nX = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)\nm = Perceptron().fit(X, np.array([0, 0, 0, 1]))\nprint(m.predict(X), m.erreurs_)\n",
   r'''import numpy as np
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
m = Perceptron()
assert m.fit(X, np.array([0, 1, 1, 1])) is m, "fit doit renvoyer self."
assert list(m.predict(X)) == [0, 1, 1, 1], "Le perceptron doit apprendre le OU."
assert m.erreurs_[-1] == 0 and len(m.erreurs_) < 20, "L'entraînement doit s'arrêter dès qu'une époque est sans erreur."
mx = Perceptron(epoques=30).fit(X, np.array([0, 1, 1, 0]))
assert len(mx.erreurs_) == 30 and min(mx.erreurs_) > 0, "Sur le OU exclusif, il reste toujours des erreurs : chaque époque doit être comptée."
rng = np.random.default_rng(0); A = rng.normal(size=(100, 2)); ya = (A[:, 0] + 2 * A[:, 1] > 0.3).astype(int)
assert (Perceptron(epoques=100).fit(A, ya).predict(A) == ya).mean() == 1, "Sur des données linéairement séparables, le perceptron doit tout classer correctement."
''',
   "Reprends la fonction de la leçon dans fit, avec self.w_ et self.b_. predict se fait sans boucle : (X @ w + b > 0).astype(int)."),
]},
# ================================================================ MLP et rétropropagation
{"id": "l-dl-backprop", "title": "Réseau multicouche et rétropropagation", "minutes": 110,
"body": r'''
Entraîner un réseau, c'est faire une descente de gradient sur tous ses poids. Il faut donc la dérivée de la perte par rapport à chaque poids. La **rétropropagation** (*backpropagation*) calcule toutes ces dérivées efficacement, en appliquant la **règle de la chaîne** de la sortie vers l'entrée.

```viz mlp
```

## La règle de la chaîne, sur un neurone

Pour un neurone sigmoïde avec une perte d'entropie croisée, les dérivées se simplifient remarquablement :

```latex
z = w \cdot x + b,\quad p = \sigma(z),\quad L = -[y \log p + (1-y)\log(1-p)]
\qquad\Rightarrow\qquad
\frac{\partial L}{\partial z} = p - y,\quad \frac{\partial L}{\partial w} = (p - y)\,x
```

## Les quatre étapes d'une itération

1. **Propagation avant** : calculer la sortie en gardant les valeurs intermédiaires.
2. **Perte** : mesurer l'erreur.
3. **Rétropropagation** : calculer les gradients, couche par couche, de la fin vers le début.
4. **Mise à jour** : chaque poids recule d'un petit pas dans la direction de son gradient.

```python
import numpy as np

X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
y = np.array([[0], [1], [1], [0]], dtype=float)          # le OU exclusif
rng = np.random.default_rng(1)
W1, b1 = rng.normal(size=(2, 8)), np.zeros(8)
W2, b2 = rng.normal(size=(8, 1)), np.zeros(1)
sig = lambda z: 1 / (1 + np.exp(-z))

for epoque in range(3001):
    # 1. propagation avant
    H = np.tanh(X @ W1 + b1)
    P = sig(H @ W2 + b2)
    # 2. perte
    L = -np.mean(y * np.log(P) + (1 - y) * np.log(1 - P))
    # 3. rétropropagation
    dZ2 = (P - y) / len(X)               # dL/dz de la sortie
    dW2, db2 = H.T @ dZ2, dZ2.sum(axis=0)
    dH = dZ2 @ W2.T                      # on remonte dans la couche cachée
    dZ1 = dH * (1 - H ** 2)              # dérivée de tanh
    dW1, db1 = X.T @ dZ1, dZ1.sum(axis=0)
    # 4. mise à jour
    for param, grad in [(W1, dW1), (b1, db1), (W2, dW2), (b2, db2)]:
        param -= 0.5 * grad
    if epoque % 1000 == 0:
        print(f"époque {epoque:4}  perte {L:.4f}")
print("prédictions :", P.ravel().round(3))
```

La couche cachée a appris à transformer l'espace : le OU exclusif, impossible pour le perceptron, est résolu.

## Vérifier ses gradients

Un bug dans la rétropropagation ne fait pas planter le programme : le réseau apprend juste mal. On vérifie donc les gradients analytiques en les comparant à des **dérivées numériques** (différences finies), comme en semaine de maths.

```python
def perte(W1_):
    H = np.tanh(X @ W1_ + b1)
    P = sig(H @ W2 + b2)
    return -np.mean(y * np.log(P) + (1 - y) * np.log(1 - P))

h, i, j = 1e-6, 0, 3
W_plus, W_moins = W1.copy(), W1.copy()
W_plus[i, j] += h; W_moins[i, j] -= h
H = np.tanh(X @ W1 + b1); P = sig(H @ W2 + b2)
dZ1 = ((P - y) / len(X)) @ W2.T * (1 - H ** 2)
print("numérique :", (perte(W_plus) - perte(W_moins)) / (2 * h), " analytique :", (X.T @ dZ1)[i, j])
```

PyTorch fait tout ce calcul automatiquement (*autograd*) : c'est la leçon suivante. Mais l'avoir codé une fois toi-même, c'est ce qui te permettra de comprendre les problèmes de gradients qui disparaissent ou explosent.

> **À retenir** : la rétropropagation = la règle de la chaîne appliquée couche par couche, de la sortie vers l'entrée. Les formes des gradients sont toujours celles des paramètres : vérifie-les avec `.shape`.
''',
"exercises": [
 E("e-dl-bp-a", "Les gradients d'un neurone",
   "Pour un neurone sigmoïde avec perte d'entropie croisée moyenne, écris `gradients(X, y, w, b)` qui renvoie `(dw, db)` en utilisant la formule de la leçon : dL/dz = (p − y) / n.",
   "import numpy as np\n\ndef gradients(X, y, w, b):\n    pass\n\nrng = np.random.default_rng(0)\nX = rng.normal(size=(20, 3))\ny = (X[:, 0] > 0).astype(float)\nw, b = rng.normal(size=3), 0.1\n",
   "import numpy as np\n\ndef gradients(X, y, w, b):\n    p = 1 / (1 + np.exp(-(X @ w + b)))\n    dz = (p - y) / len(y)\n    return X.T @ dz, dz.sum()\n\nrng = np.random.default_rng(0)\nX = rng.normal(size=(20, 3))\ny = (X[:, 0] > 0).astype(float)\nw, b = rng.normal(size=3), 0.1\nprint(gradients(X, y, w, b))\n",
   r'''import numpy as np
def L(w_, b_):
    p = 1 / (1 + np.exp(-(X @ w_ + b_)))
    return -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))
dw, db = gradients(X, y, w, b)
h = 1e-6
num = np.array([(L(w + h * e, b) - L(w - h * e, b)) / (2 * h) for e in np.eye(3)])
assert np.shape(dw) == (3,), f"dw doit avoir la forme de w, (3,) ; il a {np.shape(dw)}."
assert np.allclose(dw, num, atol=1e-6), f"dw = {np.round(dw, 5)} ne correspond pas au gradient numérique {np.round(num, 5)}."
assert abs(db - (L(w, b + h) - L(w, b - h)) / (2 * h)) < 1e-6, "db ne correspond pas au gradient numérique."
''',
   "p = sigmoïde(X @ w + b) ; dz = (p − y) / n ; dw = X.T @ dz ; db = dz.sum()."),
 E("e-dl-bp-b", "Un MLP qui apprend le OU exclusif",
   "Écris `entrainer_xor(epoques=3000, eta=0.5, graine=1)` qui entraîne le réseau de la leçon (8 neurones cachés tanh, sortie sigmoïde) sur XOR et renvoie `(P, pertes)` : les prédictions finales (4, 1) et la liste des pertes à chaque époque.",
   XOR + "\ndef entrainer_xor(epoques=3000, eta=0.5, graine=1):\n    pass\n",
   XOR + "\ndef entrainer_xor(epoques=3000, eta=0.5, graine=1):\n    rng = np.random.default_rng(graine)\n    W1, b1 = rng.normal(size=(2, 8)), np.zeros(8)\n    W2, b2 = rng.normal(size=(8, 1)), np.zeros(1)\n    pertes = []\n    for _ in range(epoques):\n        H = np.tanh(X @ W1 + b1)\n        P = 1 / (1 + np.exp(-(H @ W2 + b2)))\n        pertes.append(-np.mean(y * np.log(P) + (1 - y) * np.log(1 - P)))\n        dZ2 = (P - y) / len(X)\n        dZ1 = dZ2 @ W2.T * (1 - H ** 2)\n        W2 -= eta * H.T @ dZ2; b2 -= eta * dZ2.sum(axis=0)\n        W1 -= eta * X.T @ dZ1; b1 -= eta * dZ1.sum(axis=0)\n    return P, pertes\n\nP, pertes = entrainer_xor()\nprint(P.ravel().round(3), round(pertes[-1], 4))\n",
   r'''import numpy as np
P, pertes = entrainer_xor()
assert np.shape(P) == (4, 1), f"P doit avoir la forme (4, 1) ; il a {np.shape(P)}."
assert ((np.asarray(P) > 0.5) == y).all(), f"Le réseau n'a pas appris le OU exclusif : {np.asarray(P).ravel().round(3)}."
assert len(pertes) == 3000 and pertes[-1] < 0.1 * pertes[0], "La perte doit être enregistrée à chaque époque et diminuer fortement."
''',
   "Copie la boucle de la leçon dans la fonction. Attention à l'ordre : calcule dZ1 avec W2 avant de mettre W2 à jour."),
]},
# ================================================================ PyTorch
{"id": "l-dl-torch", "title": "Lire et écrire du PyTorch", "minutes": 90,
"body": r'''
**PyTorch** est la bibliothèque de deep learning utilisée au FullStack. Elle fait trois choses que tu viens de faire à la main : calculer sur des **tenseurs** (des tableaux NumPy qui tournent aussi sur GPU), calculer les gradients automatiquement (**autograd**), et fournir des briques prêtes (couches, pertes, optimiseurs). PyTorch ne tourne pas dans le navigateur : les blocs ci-dessous sont à exécuter sur ton ordinateur ou dans Google Colab.

## Les tenseurs et l'autograd

```pycode
import torch

x = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
w = torch.randn(2, 1, requires_grad=True)    # PyTorch suivra les opérations sur w
perte = ((x @ w) ** 2).mean()
perte.backward()                             # rétropropagation automatique
print(w.grad)                                # dPerte/dw, de la forme de w
```

## La correspondance avec ce que tu sais faire

| Ce que tu as codé en NumPy | En PyTorch |
| --- | --- |
| `W, b` et `X @ W + b` | `nn.Linear(d, k)` |
| `np.tanh`, `np.maximum(0, z)` | `nn.Tanh()`, `nn.ReLU()` |
| Softmax + entropie croisée | `nn.CrossEntropyLoss()` (prend les scores bruts) |
| Gradients à la main | `perte.backward()` |
| `W -= eta * dW` | `optimizer.step()` (SGD, Adam…) |
| Boucle sur des lots | `DataLoader` |

## Une boucle d'entraînement complète

C'est **toujours** la même structure : tu la retrouveras dans tous les projets.

```pycode
import torch
from torch import nn
from torch.utils.data import TensorDataset, DataLoader

modele = nn.Sequential(
    nn.Linear(4, 16), nn.ReLU(),
    nn.Linear(16, 3),                 # 3 classes : scores bruts (logits)
)
perte_fn = nn.CrossEntropyLoss()
optimiseur = torch.optim.Adam(modele.parameters(), lr=1e-2)
loader = DataLoader(TensorDataset(X_train, y_train), batch_size=32, shuffle=True)

for epoque in range(50):
    modele.train()
    for xb, yb in loader:
        optimiseur.zero_grad()            # 1. remettre les gradients à zéro
        logits = modele(xb)               # 2. propagation avant
        perte = perte_fn(logits, yb)      # 3. perte
        perte.backward()                  # 4. rétropropagation
        optimiseur.step()                 # 5. mise à jour
    modele.eval()
    with torch.no_grad():                 # pas de gradients pendant l'évaluation
        acc = (modele(X_test).argmax(dim=1) == y_test).float().mean()
    print(epoque, round(perte.item(), 4), round(acc.item(), 3))
```

Les pièges classiques : oublier `zero_grad()` (les gradients s'additionnent d'un lot à l'autre), appliquer une softmax avant `CrossEntropyLoss` (elle l'applique déjà), oublier `model.eval()` et `torch.no_grad()` pendant l'évaluation.

## Écrire son propre module

```pycode
class MonReseau(nn.Module):
    def __init__(self, d, cache, k):
        super().__init__()
        self.couche1 = nn.Linear(d, cache)
        self.couche2 = nn.Linear(cache, k)

    def forward(self, x):
        return self.couche2(torch.relu(self.couche1(x)))
```

Tu reconnais la POO de la Fondation : héritage de `nn.Module`, `super().__init__()`, et une méthode `forward`.

## Les mêmes briques, en NumPy

Pour bien comprendre ce que fait `nn.Linear`, on l'écrit avec sa méthode `backward` : c'est l'exercice de cette leçon.

```python
import numpy as np

class Lineaire:
    """Comme nn.Linear : y = x W + b, avec la rétropropagation."""
    def __init__(self, d, k, graine=0):
        rng = np.random.default_rng(graine)
        self.W = rng.normal(0, np.sqrt(2 / d), size=(d, k))    # initialisation de He
        self.b = np.zeros(k)

    def forward(self, x):
        self.x = x                       # gardé pour la rétropropagation
        return x @ self.W + self.b

couche = Lineaire(4, 3)
print(couche.forward(np.ones((2, 4))).shape)
```

> **À retenir** : zero_grad, forward, perte, backward, step. Cinq lignes au cœur de tout entraînement PyTorch.
''',
"tasks": [
  "Installer PyTorch (pip install torch) ou ouvrir un notebook Google Colab",
  "Recopier la boucle d'entraînement et l'appliquer aux manchots (4 variables, 3 espèces)",
  "Comparer SGD et Adam : quelle courbe de perte descend le plus vite ?",
  "Lire le tutoriel officiel « Learn the Basics » de PyTorch, en anglais",
],
"exercises": [
 E("e-dl-torch-a", "Une couche linéaire avec rétropropagation",
   "Complète la classe `Lineaire` avec `backward(grad_sortie)` : elle reçoit dL/dy de forme (n, k), stocke `self.dW` (forme (d, k)) et `self.db` (forme (k,)), et renvoie dL/dx (forme (n, d)). Rappel : y = xW + b.",
   "import numpy as np\n\nclass Lineaire:\n    def __init__(self, d, k, graine=0):\n        rng = np.random.default_rng(graine)\n        self.W = rng.normal(0, np.sqrt(2 / d), size=(d, k))\n        self.b = np.zeros(k)\n\n    def forward(self, x):\n        self.x = x\n        return x @ self.W + self.b\n\n    def backward(self, grad_sortie):\n        pass\n",
   "import numpy as np\n\nclass Lineaire:\n    def __init__(self, d, k, graine=0):\n        rng = np.random.default_rng(graine)\n        self.W = rng.normal(0, np.sqrt(2 / d), size=(d, k))\n        self.b = np.zeros(k)\n\n    def forward(self, x):\n        self.x = x\n        return x @ self.W + self.b\n\n    def backward(self, grad_sortie):\n        self.dW = self.x.T @ grad_sortie\n        self.db = grad_sortie.sum(axis=0)\n        return grad_sortie @ self.W.T\n\nc = Lineaire(4, 3)\nc.forward(np.ones((2, 4)))\nprint(c.backward(np.ones((2, 3))).shape, c.dW.shape, c.db.shape)\n",
   r'''import numpy as np
rng = np.random.default_rng(3)
c = Lineaire(4, 3, graine=1)
x = rng.normal(size=(5, 4)); cible = rng.normal(size=(5, 3))
perte = lambda: 0.5 * ((c.forward(x) - cible) ** 2).sum()
yv = c.forward(x)
dx = c.backward(yv - cible)
assert dx.shape == (5, 4) and c.dW.shape == (4, 3) and c.db.shape == (3,), "Les formes doivent être dx (n, d), dW (d, k), db (k,)."
h = 1e-6; W0 = c.W.copy()
c.W = W0.copy(); c.W[2, 1] += h; lp = perte(); c.W = W0.copy(); c.W[2, 1] -= h; lm = perte(); c.W = W0
assert abs(c.dW[2, 1] - (lp - lm) / (2 * h)) < 1e-4, "dW ne correspond pas au gradient numérique : dW = x.T @ grad_sortie."
x2 = x.copy(); x2[1, 3] += h; lp = 0.5 * ((x2 @ c.W + c.b - cible) ** 2).sum(); x2[1, 3] -= 2 * h; lm = 0.5 * ((x2 @ c.W + c.b - cible) ** 2).sum()
assert abs(dx[1, 3] - (lp - lm) / (2 * h)) < 1e-4, "dx ne correspond pas : dx = grad_sortie @ W.T."
''',
   "dW = x.T @ grad_sortie ; db = somme sur l'axe 0 ; dx = grad_sortie @ W.T. Vérifie les formes."),
]},
# ================================================================ Convolutions
{"id": "l-dl-conv", "title": "Les convolutions et les CNN", "minutes": 100,
"body": r'''
Une image de 224 × 224 pixels en couleur contient 150 528 valeurs. Une couche dense qui relie chaque pixel à 1 000 neurones aurait 150 millions de poids, et ignorerait que deux pixels voisins sont liés. Les **réseaux convolutifs** (CNN) résolvent ce problème avec une idée simple : faire glisser un petit **filtre** sur toute l'image.

```viz conv
```

## L'opération de convolution

Un filtre (ou *noyau*, *kernel*) est une petite matrice, par exemple 3 × 3. On le place sur chaque zone de l'image, on multiplie terme à terme et on additionne : cela donne un pixel de la **carte de caractéristiques** (*feature map*).

```python
import numpy as np

def convolution(image, filtre):
    h, w = image.shape
    k = filtre.shape[0]
    sortie = np.zeros((h - k + 1, w - k + 1))
    for i in range(sortie.shape[0]):
        for j in range(sortie.shape[1]):
            sortie[i, j] = (image[i:i + k, j:j + k] * filtre).sum()
    return sortie

image = np.zeros((6, 6)); image[:, 3:] = 1          # moitié gauche noire, moitié droite blanche
bord_vertical = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
convolution(image, bord_vertical)
```

Le filtre réagit fort là où l'intensité change de gauche à droite : il **détecte les bords verticaux**. Dans un CNN, les filtres ne sont pas choisis à la main : ils sont **appris**. Les premières couches apprennent des bords et des textures, les suivantes des formes, puis des objets.

## Les réglages d'une convolution

- **Taille du filtre** : 3 × 3 le plus souvent.
- **Pas** (*stride*) : de combien on décale le filtre. Un pas de 2 divise la taille par deux.
- **Remplissage** (*padding*) : des zéros autour de l'image pour garder la même taille en sortie.
- **Nombre de filtres** : chaque filtre produit une carte ; 32 filtres donnent 32 canaux.

Taille de sortie, pour une entrée de taille n, un filtre k, un remplissage p et un pas s :

```latex
\text{sortie} = \left\lfloor \frac{n + 2p - k}{s} \right\rfloor + 1
```

## Le pooling

Le **max pooling** garde le maximum de chaque bloc (souvent 2 × 2) : il réduit la taille et rend le réseau tolérant aux petits décalages.

## L'architecture typique

```pycode
from torch import nn

cnn = nn.Sequential(
    nn.Conv2d(3, 32, kernel_size=3, padding=1), nn.ReLU(), nn.MaxPool2d(2),   # 224 → 112
    nn.Conv2d(32, 64, kernel_size=3, padding=1), nn.ReLU(), nn.MaxPool2d(2),  # 112 → 56
    nn.Flatten(),
    nn.Linear(64 * 56 * 56, 2),       # chat ou chien
)
```

En pratique, on part presque toujours d'un réseau **pré-entraîné** sur des millions d'images (ResNet, EfficientNet) et on n'entraîne que les dernières couches : c'est l'**apprentissage par transfert**, au programme du module Adaptation et évaluation.

> **À retenir** : une convolution = un petit filtre partagé qui glisse sur l'image. Peu de paramètres, et le réseau détecte un motif où qu'il se trouve.
''',
"exercises": [
 E("e-dl-conv-a", "Convolution avec un pas",
   "Écris `conv2d(image, filtre, pas=1)` : une convolution sans remplissage (*valid*), avec un pas réglable. La taille de sortie est ⌊(n − k) / pas⌋ + 1 dans chaque dimension.",
   "import numpy as np\n\ndef conv2d(image, filtre, pas=1):\n    pass\n",
   "import numpy as np\n\ndef conv2d(image, filtre, pas=1):\n    k = filtre.shape[0]\n    h = (image.shape[0] - k) // pas + 1\n    w = (image.shape[1] - k) // pas + 1\n    sortie = np.zeros((h, w))\n    for i in range(h):\n        for j in range(w):\n            zone = image[i * pas:i * pas + k, j * pas:j * pas + k]\n            sortie[i, j] = (zone * filtre).sum()\n    return sortie\n\nimg = np.arange(25, dtype=float).reshape(5, 5)\nprint(conv2d(img, np.ones((3, 3))), conv2d(img, np.ones((3, 3)), pas=2))\n",
   r'''import numpy as np
from scipy.signal import correlate2d
rng = np.random.default_rng(0)
img = rng.normal(size=(7, 9)); f = rng.normal(size=(3, 3))
assert np.allclose(conv2d(img, f), correlate2d(img, f, mode="valid")), "Avec un pas de 1, le résultat doit correspondre à une corrélation 2D « valid »."
s2 = conv2d(img, f, pas=2)
assert s2.shape == (3, 4), f"Avec un pas de 2 sur une image 7 × 9, la sortie doit être 3 × 4 ; elle est {s2.shape}."
assert np.allclose(s2, correlate2d(img, f, mode="valid")[::2, ::2]), "Les valeurs avec un pas de 2 sont fausses."
''',
   "La zone commence en (i × pas, j × pas). La taille de sortie se calcule avec // (division entière)."),
 E("e-dl-conv-b", "Max pooling",
   "Écris `max_pool(carte, taille=2)` qui découpe la carte en blocs `taille × taille` sans chevauchement et garde le maximum de chacun. Si la taille ne divise pas exactement la carte, ignore les lignes et colonnes en trop.",
   "import numpy as np\n\ndef max_pool(carte, taille=2):\n    pass\n",
   "import numpy as np\n\ndef max_pool(carte, taille=2):\n    h, w = carte.shape[0] // taille, carte.shape[1] // taille\n    c = carte[:h * taille, :w * taille]\n    return c.reshape(h, taille, w, taille).max(axis=(1, 3))\n\nprint(max_pool(np.arange(16).reshape(4, 4)))\n",
   r'''import numpy as np
assert np.array_equal(max_pool(np.arange(16).reshape(4, 4)), [[5, 7], [13, 15]]), f"Sur une carte 4 × 4, j'attends [[5, 7], [13, 15]] ; tu renvoies {max_pool(np.arange(16).reshape(4, 4))}."
m = max_pool(np.arange(35).reshape(5, 7))
assert m.shape == (2, 3) and m[1, 2] == 26, f"Sur une carte 5 × 7, la sortie doit être 2 × 3 (le reste est ignoré) ; tu as {m.shape}."
''',
   "Astuce NumPy : reshape(h, taille, w, taille) puis .max(axis=(1, 3)). Une double boucle marche aussi."),
]},
# ================================================================ Embeddings
{"id": "l-dl-embed", "title": "Les embeddings", "minutes": 90,
"body": r'''
Un réseau de neurones ne manipule que des nombres. Comment lui donner des mots, des produits ou des utilisateurs ? Avec des **embeddings** (plongements) : chaque élément est représenté par un **vecteur dense**, appris de façon à ce que des éléments semblables aient des vecteurs proches. C'est la brique de base des LLM, des moteurs de recherche sémantique et des systèmes de recommandation.

## One-hot contre embedding

Le **one-hot** représente chaque mot d'un vocabulaire de 50 000 mots par un vecteur de 50 000 zéros et un seul 1 : énorme, et tous les mots sont à la même distance les uns des autres. Un **embedding** le représente par un vecteur de quelques centaines de valeurs, et la géométrie a du sens.

En pratique, une couche d'embedding est simplement une **table** : une matrice (taille du vocabulaire × dimension) dont on lit la ligne correspondant au mot. Ses valeurs sont des poids appris comme les autres.

```python
import numpy as np
vocab = {"chat": 0, "chien": 1, "voiture": 2}
rng = np.random.default_rng(0)
table = rng.normal(size=(len(vocab), 4))          # nn.Embedding(3, 4) en PyTorch
table[vocab["chien"]]
```

## La géométrie du sens

Des embeddings entraînés sur beaucoup de texte (word2vec, GloVe, puis ceux des Transformers) capturent des relations : les directions de l'espace encodent des notions comme le genre, le temps ou le pays.

```viz embed
```

Voici des vecteurs simplifiés à 4 dimensions (royauté, masculin, humain, animal), pour comprendre le principe :

```python
mots = {
    "roi":   np.array([0.9, 0.8, 0.9, 0.0]),
    "reine": np.array([0.9, -0.8, 0.9, 0.0]),
    "homme": np.array([0.1, 0.8, 0.9, 0.0]),
    "femme": np.array([0.1, -0.8, 0.9, 0.0]),
    "chat":  np.array([0.0, 0.1, 0.1, 0.9]),
    "lion":  np.array([0.6, 0.3, 0.0, 0.9]),
}
cos = lambda a, b: a @ b / (np.linalg.norm(a) * np.linalg.norm(b))
cible = mots["roi"] - mots["homme"] + mots["femme"]
sorted(((round(cos(cible, v), 3), m) for m, v in mots.items()), reverse=True)[:3]
```

« roi − homme + femme ≈ reine » : la célèbre analogie de word2vec.

## Comment on les apprend

- **word2vec** : on entraîne un petit réseau à prédire un mot à partir de ses voisins ; les poids appris sont les embeddings.
- **Dans un modèle** : la table d'embeddings est la première couche, entraînée avec tout le reste pour la tâche visée.
- **Modèles d'embeddings dédiés** : on obtient directement un vecteur pour une phrase ou un document, via une API ou un modèle Hugging Face. C'est ce qu'utilise un RAG.

## Classer des textes avec des embeddings

La méthode la plus simple : faire la **moyenne** des vecteurs des mots d'un texte, puis donner ce vecteur à un classifieur.

```python
from sklearn.linear_model import LogisticRegression

vecteurs = {"super": [1, 0.2], "génial": [0.9, 0.1], "top": [0.8, 0.3], "nul": [-1, 0.1], "horrible": [-0.9, 0.2],
            "décevant": [-0.8, 0.0], "film": [0, 1], "acteurs": [0.05, 0.9]}
def vectoriser(texte):
    vs = [vecteurs[m] for m in texte.split() if m in vecteurs]
    return np.mean(vs, axis=0) if vs else np.zeros(2)

textes = ["film super", "acteurs génial", "film top", "film nul", "acteurs horrible", "film décevant"]
y = [1, 1, 1, 0, 0, 0]
clf = LogisticRegression().fit([vectoriser(t) for t in textes], y)
clf.predict([vectoriser("acteurs top"), vectoriser("film horrible")])
```

> **À retenir** : un embedding est un vecteur appris qui place les éléments semblables près les uns des autres. On les compare par similarité cosinus. C'est le pont entre le deep learning, la recherche sémantique et les LLM.
''',
"exercises": [
 E("e-dl-emb-a", "Les plus proches voisins",
   "Écris `voisins(mot, mots, k=2)` qui renvoie la liste des `k` mots les plus similaires à `mot` (similarité cosinus), **sans** le mot lui-même, du plus au moins similaire.",
   "import numpy as np\n\nmots = {\n    \"roi\": np.array([0.9, 0.8, 0.9, 0.0]), \"reine\": np.array([0.9, -0.8, 0.9, 0.0]),\n    \"homme\": np.array([0.1, 0.8, 0.9, 0.0]), \"femme\": np.array([0.1, -0.8, 0.9, 0.0]),\n    \"chat\": np.array([0.0, 0.1, 0.1, 0.9]), \"lion\": np.array([0.6, 0.3, 0.0, 0.9]),\n}\n\ndef voisins(mot, mots, k=2):\n    pass\n",
   "import numpy as np\n\nmots = {\n    \"roi\": np.array([0.9, 0.8, 0.9, 0.0]), \"reine\": np.array([0.9, -0.8, 0.9, 0.0]),\n    \"homme\": np.array([0.1, 0.8, 0.9, 0.0]), \"femme\": np.array([0.1, -0.8, 0.9, 0.0]),\n    \"chat\": np.array([0.0, 0.1, 0.1, 0.9]), \"lion\": np.array([0.6, 0.3, 0.0, 0.9]),\n}\n\ndef voisins(mot, mots, k=2):\n    v = mots[mot]\n    cos = lambda a, b: a @ b / (np.linalg.norm(a) * np.linalg.norm(b))\n    autres = [m for m in mots if m != mot]\n    return sorted(autres, key=lambda m: cos(v, mots[m]), reverse=True)[:k]\n\nprint(voisins(\"chat\", mots), voisins(\"roi\", mots, 3))\n",
   r'''assert voisins("chat", mots, 1) == ["lion"], f"Le voisin de chat devrait être lion ; tu renvoies {voisins('chat', mots, 1)}."
r = voisins("roi", mots, 3)
assert "roi" not in r and len(r) == 3, "Le mot lui-même ne doit pas faire partie de ses voisins."
assert r[0] == "homme", f"Le plus proche de roi devrait être homme ; tu renvoies {r}."
''',
   "Calcule la similarité cosinus avec chaque autre mot, trie par ordre décroissant, garde les k premiers."),
 E("e-dl-emb-b", "Résoudre une analogie",
   "Écris `analogie(a, b, c, mots)` qui résout « a est à b ce que c est à ? » : elle calcule `mots[b] - mots[a] + mots[c]` et renvoie le mot le plus similaire (cosinus), en **excluant** a, b et c. Par exemple `analogie(\"homme\", \"roi\", \"femme\", mots)` doit renvoyer `\"reine\"`.",
   "import numpy as np\n\nmots = {\n    \"roi\": np.array([0.9, 0.8, 0.9, 0.0]), \"reine\": np.array([0.9, -0.8, 0.9, 0.0]),\n    \"homme\": np.array([0.1, 0.8, 0.9, 0.0]), \"femme\": np.array([0.1, -0.8, 0.9, 0.0]),\n    \"prince\": np.array([0.7, 0.8, 0.9, 0.1]), \"princesse\": np.array([0.7, -0.8, 0.9, 0.1]),\n    \"chat\": np.array([0.0, 0.1, 0.1, 0.9]), \"lion\": np.array([0.6, 0.3, 0.0, 0.9]),\n}\n\ndef analogie(a, b, c, mots):\n    pass\n",
   "import numpy as np\n\nmots = {\n    \"roi\": np.array([0.9, 0.8, 0.9, 0.0]), \"reine\": np.array([0.9, -0.8, 0.9, 0.0]),\n    \"homme\": np.array([0.1, 0.8, 0.9, 0.0]), \"femme\": np.array([0.1, -0.8, 0.9, 0.0]),\n    \"prince\": np.array([0.7, 0.8, 0.9, 0.1]), \"princesse\": np.array([0.7, -0.8, 0.9, 0.1]),\n    \"chat\": np.array([0.0, 0.1, 0.1, 0.9]), \"lion\": np.array([0.6, 0.3, 0.0, 0.9]),\n}\n\ndef analogie(a, b, c, mots):\n    cible = mots[b] - mots[a] + mots[c]\n    cos = lambda u, v: u @ v / (np.linalg.norm(u) * np.linalg.norm(v))\n    candidats = [m for m in mots if m not in (a, b, c)]\n    return max(candidats, key=lambda m: cos(cible, mots[m]))\n\nprint(analogie(\"homme\", \"roi\", \"femme\", mots), analogie(\"roi\", \"prince\", \"reine\", mots))\n",
   r'''assert analogie("homme", "roi", "femme", mots) == "reine", f"homme → roi, femme → {analogie('homme', 'roi', 'femme', mots)} (attendu : reine)."
assert analogie("roi", "prince", "reine", mots) == "princesse", "roi → prince, reine → princesse."
assert analogie("femme", "reine", "homme", mots) == "roi", "Pense à exclure a, b et c des candidats."
''',
   "cible = mots[b] − mots[a] + mots[c], puis max(candidats, key=similarité avec cible)."),
]},
]

PROJECTS = [
{"id": "p-dl", "title": "Projet · Ton réseau de neurones from scratch", "minutes": 150,
"body": r'''
L'équivalent des projets « Créez une classe de perceptron réutilisable » et « Réseaux neuronaux avec PyTorch » : un réseau de neurones complet, écrit en NumPy, qui classe les espèces de manchots. Tu le réécriras ensuite en PyTorch sur ton ordinateur, et tu compareras.

Architecture : 4 variables standardisées → couche cachée de 16 neurones ReLU → 3 sorties softmax, perte d'entropie croisée, descente de gradient sur tout le jeu d'entraînement.

Les gradients, pour une sortie softmax avec entropie croisée et des étiquettes en one-hot Y :

```latex
dZ_2 = \frac{P - Y}{n} \qquad dW_2 = H^\top dZ_2 \qquad dH = dZ_2 W_2^\top \qquad dZ_1 = dH \odot \mathbb{1}[Z_1 > 0] \qquad dW_1 = X^\top dZ_1
```
''',
"exercises": [
 E("e-pdl-a", "La classe MLP",
   "Écris une classe `MLP(d, cache, k, eta=0.1, epoques=300, graine=0)`. Le constructeur initialise `W1` (d, cache), `W2` (cache, k) avec une loi normale de He (écart-type √(2 / entrées)) et des biais nuls. `fit(X, y)` (y : indices de classe) fait `epoques` itérations de descente de gradient en stockant la perte de chaque époque dans `self.pertes_`, et renvoie `self`. `predict_proba(X)` et `predict(X)` complètent l'interface.",
   "import numpy as np\n\nclass MLP:\n    pass\n",
   "import numpy as np\n\nclass MLP:\n    def __init__(self, d, cache, k, eta=0.1, epoques=300, graine=0):\n        rng = np.random.default_rng(graine)\n        self.W1 = rng.normal(0, np.sqrt(2 / d), (d, cache)); self.b1 = np.zeros(cache)\n        self.W2 = rng.normal(0, np.sqrt(2 / cache), (cache, k)); self.b2 = np.zeros(k)\n        self.k, self.eta, self.epoques = k, eta, epoques\n\n    def _forward(self, X):\n        Z1 = X @ self.W1 + self.b1\n        H = np.maximum(0, Z1)\n        Z2 = H @ self.W2 + self.b2\n        Z2 = Z2 - Z2.max(axis=1, keepdims=True)\n        P = np.exp(Z2) / np.exp(Z2).sum(axis=1, keepdims=True)\n        return Z1, H, P\n\n    def fit(self, X, y):\n        Y = np.eye(self.k)[y]\n        self.pertes_ = []\n        for _ in range(self.epoques):\n            Z1, H, P = self._forward(X)\n            self.pertes_.append(-np.log(np.clip(P[np.arange(len(y)), y], 1e-12, 1)).mean())\n            dZ2 = (P - Y) / len(X)\n            dZ1 = (dZ2 @ self.W2.T) * (Z1 > 0)\n            self.W2 -= self.eta * H.T @ dZ2; self.b2 -= self.eta * dZ2.sum(axis=0)\n            self.W1 -= self.eta * X.T @ dZ1; self.b1 -= self.eta * dZ1.sum(axis=0)\n        return self\n\n    def predict_proba(self, X):\n        return self._forward(X)[2]\n\n    def predict(self, X):\n        return self.predict_proba(X).argmax(axis=1)\n\nrng = np.random.default_rng(0)\nX = rng.normal(size=(150, 2)); y = (X[:, 0] * X[:, 1] > 0).astype(int)\nm = MLP(2, 16, 2, eta=0.5, epoques=500).fit(X, y)\nprint((m.predict(X) == y).mean(), round(m.pertes_[-1], 3))\n",
   r'''import numpy as np
m = MLP(4, 16, 3)
assert m.W1.shape == (4, 16) and m.W2.shape == (16, 3) and m.b1.shape == (16,), "Vérifie les formes des poids."
rng = np.random.default_rng(0)
X = rng.normal(size=(200, 2)); y = (X[:, 0] * X[:, 1] > 0).astype(int)
m2 = MLP(2, 16, 2, eta=0.5, epoques=600)
assert m2.fit(X, y) is m2, "fit doit renvoyer self."
assert len(m2.pertes_) == 600 and m2.pertes_[-1] < m2.pertes_[0] * 0.5, "La perte doit être enregistrée à chaque époque et diminuer."
P = m2.predict_proba(X)
assert P.shape == (200, 2) and np.allclose(P.sum(axis=1), 1), "predict_proba doit renvoyer des probabilités qui somment à 1."
assert (m2.predict(X) == y).mean() > 0.9, f"Sur ce problème non linéaire (XOR en 2D), l'exactitude devrait dépasser 90 % ; tu as {(m2.predict(X) == y).mean():.2f}."
''',
   "Sépare une méthode _forward qui renvoie Z1, H et P. Dans fit, convertis y en one-hot avec np.eye(k)[y]."),
 E("e-pdl-b", "Classer les manchots",
   "Utilise ta classe `MLP` (recopie-la) sur les manchots : standardise les 4 mesures **avec la moyenne et l'écart-type du jeu d'entraînement**, entraîne `MLP(4, 16, 3, eta=0.1, epoques=300)` sur l'entraînement et calcule `acc_test`, l'exactitude sur le test.",
   "import numpy as np\nimport pandas as pd\n\n# recopie ta classe MLP ici\n\np = pd.read_csv(\"penguins.csv\").dropna()\ncols = [\"bill_length_mm\", \"bill_depth_mm\", \"flipper_length_mm\", \"body_mass_g\"]\nclasses = sorted(p[\"species\"].unique())\nX = p[cols].to_numpy()\ny = p[\"species\"].map({c: i for i, c in enumerate(classes)}).to_numpy()\nidx = np.random.default_rng(42).permutation(len(X))\ntrain, test = idx[:266], idx[266:]\n",
   "import numpy as np\nimport pandas as pd\n\nclass MLP:\n    def __init__(self, d, cache, k, eta=0.1, epoques=300, graine=0):\n        rng = np.random.default_rng(graine)\n        self.W1 = rng.normal(0, np.sqrt(2 / d), (d, cache)); self.b1 = np.zeros(cache)\n        self.W2 = rng.normal(0, np.sqrt(2 / cache), (cache, k)); self.b2 = np.zeros(k)\n        self.k, self.eta, self.epoques = k, eta, epoques\n\n    def _forward(self, X):\n        Z1 = X @ self.W1 + self.b1\n        H = np.maximum(0, Z1)\n        Z2 = H @ self.W2 + self.b2\n        Z2 = Z2 - Z2.max(axis=1, keepdims=True)\n        P = np.exp(Z2) / np.exp(Z2).sum(axis=1, keepdims=True)\n        return Z1, H, P\n\n    def fit(self, X, y):\n        Y = np.eye(self.k)[y]\n        self.pertes_ = []\n        for _ in range(self.epoques):\n            Z1, H, P = self._forward(X)\n            self.pertes_.append(-np.log(np.clip(P[np.arange(len(y)), y], 1e-12, 1)).mean())\n            dZ2 = (P - Y) / len(X)\n            dZ1 = (dZ2 @ self.W2.T) * (Z1 > 0)\n            self.W2 -= self.eta * H.T @ dZ2; self.b2 -= self.eta * dZ2.sum(axis=0)\n            self.W1 -= self.eta * X.T @ dZ1; self.b1 -= self.eta * dZ1.sum(axis=0)\n        return self\n\n    def predict_proba(self, X):\n        return self._forward(X)[2]\n\n    def predict(self, X):\n        return self.predict_proba(X).argmax(axis=1)\n\np = pd.read_csv(\"penguins.csv\").dropna()\ncols = [\"bill_length_mm\", \"bill_depth_mm\", \"flipper_length_mm\", \"body_mass_g\"]\nclasses = sorted(p[\"species\"].unique())\nX = p[cols].to_numpy()\ny = p[\"species\"].map({c: i for i, c in enumerate(classes)}).to_numpy()\nidx = np.random.default_rng(42).permutation(len(X))\ntrain, test = idx[:266], idx[266:]\n\nmoy, ecart = X[train].mean(axis=0), X[train].std(axis=0)\nXs = (X - moy) / ecart\nmodele = MLP(4, 16, 3, eta=0.1, epoques=300).fit(Xs[train], y[train])\nacc_test = (modele.predict(Xs[test]) == y[test]).mean()\nprint(f\"Exactitude sur le test : {acc_test:.3f}\")\n",
   r'''assert acc_test >= 0.95, f"acc_test vaut {acc_test:.3f} ; avec des données standardisées, on dépasse 95 %."
assert 0 <= acc_test <= 1, "acc_test doit être une proportion entre 0 et 1."
''',
   "moy et ecart se calculent sur X[train] seulement (pas de fuite), puis on transforme tout X avec eux."),
],
"tasks": [
  "Réécrire le même réseau en PyTorch (nn.Sequential, CrossEntropyLoss, Adam) dans un notebook",
  "Tracer les courbes de perte NumPy et PyTorch sur le même graphique",
  "Entraîner un petit CNN sur MNIST ou chats contre chiens dans Google Colab avec un GPU",
  "Publier le tout sur GitHub avec un README qui explique la rétropropagation en 5 lignes",
]},
]

QUIZZES = {
"quiz-dl": {"title": "Quiz · Fondations du deep learning", "questions": [
 {"q": "Pourquoi une fonction d'activation non linéaire est-elle indispensable ?", "options": ["Pour accélérer le calcul", "Sans elle, empiler des couches reste une transformation linéaire", "Pour normaliser les données", "Pour éviter le surapprentissage"], "answer": 1,
  "explain": "Une composition de fonctions linéaires est linéaire : les couches cachées ne servent à rien sans non-linéarité."},
 {"q": "Quelle activation utiliser en sortie d'une classification à 5 classes ?", "options": ["ReLU", "Sigmoïde", "Softmax", "Aucune"], "answer": 2,
  "explain": "Softmax transforme 5 scores en 5 probabilités qui somment à 1. En PyTorch, CrossEntropyLoss l'applique pour toi."},
 {"q": "Pourquoi le perceptron ne peut-il pas apprendre le OU exclusif ?", "options": ["Il n'a pas assez d'époques", "Aucune droite ne sépare les deux classes", "Le taux d'apprentissage est trop grand", "XOR n'a pas de solution"], "answer": 1,
  "explain": "Un seul neurone trace une frontière linéaire ; XOR demande une frontière non linéaire, donc une couche cachée."},
 {"q": "Que calcule la rétropropagation ?", "options": ["La sortie du réseau", "Le gradient de la perte par rapport à chaque poids, par la règle de la chaîne", "Les données d'entraînement", "Le meilleur taux d'apprentissage"], "answer": 1,
  "explain": "Elle propage les dérivées de la sortie vers l'entrée, couche par couche."},
 {"q": "Dans une boucle PyTorch, que se passe-t-il si on oublie optimizer.zero_grad() ?", "options": ["Rien", "Les gradients s'accumulent d'un lot à l'autre et l'entraînement devient faux", "Le modèle ne se charge pas", "Le GPU s'arrête"], "answer": 1,
  "explain": "PyTorch additionne les gradients à chaque backward() : il faut les remettre à zéro avant chaque lot."},
 {"q": "Quelle est la taille de sortie d'une convolution 3 × 3 sans remplissage, pas de 1, sur une image 32 × 32 ?", "options": ["32 × 32", "30 × 30", "29 × 29", "16 × 16"], "answer": 1,
  "explain": "(32 − 3) / 1 + 1 = 30."},
 {"q": "Quel est l'avantage principal d'une convolution sur une couche dense pour une image ?", "options": ["Elle est plus précise sur les nombres", "Le même petit filtre est partagé sur toute l'image : peu de paramètres, et un motif est détecté où qu'il soit", "Elle n'a pas besoin d'entraînement", "Elle fonctionne sans GPU"], "answer": 1,
  "explain": "Partage des poids et localité : c'est ce qui rend les CNN efficaces sur les images."},
 {"q": "Qu'est-ce qu'une couche d'embedding, concrètement ?", "options": ["Un encodage one-hot", "Une table de vecteurs appris, dont on lit la ligne correspondant à chaque élément", "Une couche de convolution", "Une fonction d'activation"], "answer": 1,
  "explain": "nn.Embedding est une matrice (vocabulaire × dimension) de poids appris comme les autres."},
]},
}
