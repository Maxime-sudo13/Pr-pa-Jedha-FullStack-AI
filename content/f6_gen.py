"""FullStack · Architectures de modèles génératifs (vague 5) : attention, Transformer, tokenisation, Hugging Face, CLIP, diffusion."""

def E(id, title, prompt, starter, solution, check, hint):
    return {"id": id, "title": title, "prompt": prompt, "starter": starter, "solution": solution, "check": check, "hint": hint}

ATTN = r'''import numpy as np

def softmax(x, axis=-1):
    x = x - x.max(axis=axis, keepdims=True)
    e = np.exp(x)
    return e / e.sum(axis=axis, keepdims=True)

def attention(Q, K, V, masque=None):
    S = Q @ K.T / np.sqrt(K.shape[-1])
    if masque is not None:
        S = np.where(masque, S, -1e9)
    P = softmax(S)
    return P @ V, P
'''

LESSONS = [
# ================================================================ Attention
{"id": "l-attn", "title": "L'attention, pas à pas", "minutes": 100,
"body": r'''
En 2017, l'article *Attention Is All You Need* (Google) remplace les réseaux récurrents par un mécanisme unique : l'**attention**. Tous les grands modèles actuels (GPT, Claude, Llama, Gemini) en descendent. Si tu comprends cette leçon, tu comprends le cœur d'un LLM.

## Le problème à résoudre

Dans « Le chat dort sur le tapis car **il** est fatigué », pour comprendre « il », il faut regarder « chat », six mots plus tôt. Un réseau récurrent lit les mots un par un et doit garder cette information en mémoire tout du long : il oublie, et il ne se parallélise pas. L'attention permet à chaque mot de **regarder directement tous les autres** et de décider lesquels comptent.

## Un dictionnaire « doux »

Un dictionnaire Python associe une clé exacte à une valeur. L'attention fait la même chose en version floue : une **requête** (*query*) est comparée à toutes les **clés** (*keys*). Plus une clé ressemble à la requête, plus sa **valeur** (*value*) pèse dans le résultat.

```python
import numpy as np
cles = np.array([[1.0, 0.0], [0.0, 1.0], [0.7, 0.7]])
valeurs = np.array([10.0, 20.0, 30.0])
requete = np.array([0.9, 0.1])

scores = cles @ requete                         # ressemblance : produit scalaire
poids = np.exp(scores) / np.exp(scores).sum()   # softmax : des poids qui somment à 1
print("scores", scores.round(2), "→ poids", poids.round(2))
print("résultat :", (poids * valeurs).sum().round(2), "(un mélange des valeurs)")
```

## La formule

Pour toute une séquence d'un coup, on empile les requêtes, les clés et les valeurs dans des matrices Q, K et V :

```latex
\mathrm{Attention}(Q, K, V) = \mathrm{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right) V
```

- QKᵀ contient tous les scores requête × clé : une matrice (n, n) pour n tokens.
- Le softmax, ligne par ligne, transforme chaque ligne en poids qui somment à 1.
- Multiplier par V mélange les valeurs selon ces poids.

```viz attention
```

## Pourquoi diviser par √d_k

Le produit scalaire de deux vecteurs aléatoires grandit avec leur dimension. Des scores trop grands saturent le softmax : un seul poids vaut presque 1, les autres presque 0, et les gradients disparaissent. Diviser par √d_k ramène l'écart-type autour de 1.

```python
rng = np.random.default_rng(0)
for d in [4, 64, 512]:
    q, k = rng.normal(size=(2000, d)), rng.normal(size=(2000, d))
    s = (q * k).sum(axis=1)
    print(f"d = {d:3d} : écart-type de q·k = {s.std():5.1f}   après division par √d : {(s / np.sqrt(d)).std():.2f}")
```

## L'auto-attention

Dans l'**auto-attention** (*self-attention*), Q, K et V viennent tous de la même séquence X, par trois projections apprises :

```latex
Q = XW_Q \qquad K = XW_K \qquad V = XW_V
```

Chaque token produit ainsi trois vecteurs : ce qu'il cherche (Q), ce qu'il offre comme étiquette (K), et l'information qu'il transmet (V). Les matrices W sont les poids appris pendant l'entraînement.

```python
rng = np.random.default_rng(1)
n, d_model, d_k = 4, 8, 4
X = rng.normal(size=(n, d_model))              # 4 tokens, chacun un vecteur de 8 nombres
Wq, Wk, Wv = (rng.normal(size=(d_model, d_k)) for _ in range(3))
Q, K, V = X @ Wq, X @ Wk, X @ Wv
S = Q @ K.T / np.sqrt(d_k)
A = np.exp(S - S.max(axis=1, keepdims=True))
A /= A.sum(axis=1, keepdims=True)
print("poids d'attention (une ligne par token) :")
print(A.round(2))
(A @ V).shape
```

## Le masque causal

Un modèle qui **génère** du texte prédit le token suivant. Pendant l'entraînement, il ne doit donc pas voir les tokens futurs. On met leurs scores à −∞ avant le softmax : leur poids devient exactement 0. La matrice des positions autorisées est triangulaire inférieure.

```python
masque = np.tril(np.ones((n, n), dtype=bool))
print(masque.astype(int))
S_m = np.where(masque, S, -np.inf)
A = np.exp(S_m - S_m.max(axis=1, keepdims=True))
A /= A.sum(axis=1, keepdims=True)
A.round(2)
```

Le premier token ne voit que lui-même, le dernier voit tout le monde. C'est ce masque qui distingue un modèle de type GPT d'un modèle de type BERT, qui voit toute la phrase.

## L'attention croisée

Dans un traducteur, les requêtes viennent de la phrase en cours de génération, et les clés et valeurs de la phrase source : c'est l'**attention croisée** (*cross-attention*). Le même mécanisme sert à conditionner une image sur un texte dans Stable Diffusion.

## Le coût

La matrice des scores fait n × n : doubler la longueur du contexte quadruple le calcul et la mémoire de l'attention. C'est la raison des limites de fenêtre de contexte, et des optimisations comme **FlashAttention**, qui calcule le même résultat sans jamais stocker la matrice entière.

> **À retenir** : chaque token compare sa requête aux clés de tous les autres (QKᵀ), divise par √d_k, applique un softmax, et mélange les valeurs. Le masque causal interdit de regarder le futur. Coût : quadratique en la longueur.
''',
"exercises": [
 E("e-attn-a", "Un softmax qui ne déborde pas",
   "Écris `softmax(x, axis=-1)` qui applique le softmax le long de l'axe donné, pour un tableau de n'importe quelle dimension. Soustrais le maximum le long de cet axe pour éviter les débordements.",
   r'''import numpy as np

def softmax(x, axis=-1):
    pass
''',
   r'''import numpy as np

def softmax(x, axis=-1):
    x = x - x.max(axis=axis, keepdims=True)
    e = np.exp(x)
    return e / e.sum(axis=axis, keepdims=True)

print(softmax(np.array([1.0, 2.0, 3.0])))
print(softmax(np.array([[1000.0, 1001.0], [0.0, 0.0]])))
''',
   r'''import numpy as np
x = np.array([[1.0, 2.0, 3.0], [0.0, 0.0, 0.0]])
attendu = np.exp(x) / np.exp(x).sum(axis=-1, keepdims=True)
assert softmax(x) is not None and np.allclose(softmax(x), attendu), "Le softmax par défaut doit s'appliquer sur le dernier axe."
assert np.allclose(softmax(x, axis=0).sum(axis=0), 1), "Avec axis=0, chaque colonne doit sommer à 1."
assert np.isfinite(softmax(np.array([1000.0, 1001.0]))).all(), "Avec de grandes valeurs, soustrais le maximum avant np.exp."
t = np.random.default_rng(0).normal(size=(2, 3, 4))
assert np.allclose(softmax(t).sum(axis=-1), 1), "Le softmax doit fonctionner sur un tableau en 3 dimensions (keepdims=True)."
''',
   "x.max(axis=axis, keepdims=True) garde la dimension pour que la soustraction se diffuse correctement."),
 E("e-attn-b", "L'attention par produit scalaire",
   "Écris `attention(Q, K, V, masque=None)` qui renvoie le tuple `(sortie, poids)`. `poids` = softmax(QKᵀ / √d_k) ligne par ligne ; `sortie` = poids @ V. Si `masque` (tableau booléen, True = autorisé) est fourni, remplace les scores interdits par −1e9 avant le softmax. Le `softmax` est fourni.",
   r'''import numpy as np

def softmax(x, axis=-1):
    x = x - x.max(axis=axis, keepdims=True)
    e = np.exp(x)
    return e / e.sum(axis=axis, keepdims=True)

def attention(Q, K, V, masque=None):
    pass
''',
   ATTN + r'''
rng = np.random.default_rng(0)
Q, K, V = rng.normal(size=(3, 4)), rng.normal(size=(5, 4)), rng.normal(size=(5, 2))
sortie, poids = attention(Q, K, V)
print(poids.round(2), sortie.shape)
''',
   r'''import numpy as np
rng = np.random.default_rng(3)
Q, K, V = rng.normal(size=(5, 4)), rng.normal(size=(6, 4)), rng.normal(size=(6, 3))
res = attention(Q, K, V)
assert isinstance(res, tuple) and len(res) == 2, "attention doit renvoyer le tuple (sortie, poids)."
sortie, poids = res
assert poids.shape == (5, 6) and sortie.shape == (5, 3), f"Formes attendues : poids (5, 6) et sortie (5, 3) ; tu as {poids.shape} et {sortie.shape}."
S = Q @ K.T / np.sqrt(4)
P = np.exp(S) / np.exp(S).sum(axis=1, keepdims=True)
assert np.allclose(poids, P), "Les poids ne correspondent pas : as-tu bien divisé par √d_k (d_k = K.shape[-1]) ?"
assert np.allclose(sortie, P @ V), "La sortie doit valoir poids @ V."
m = np.tril(np.ones((5, 6), dtype=bool))
s2, p2 = attention(Q, K, V, m)
assert np.allclose(p2[~m], 0, atol=1e-8), "Les positions interdites par le masque doivent avoir un poids nul."
assert np.allclose(p2.sum(axis=1), 1), "Même masqués, les poids de chaque ligne doivent sommer à 1."
''',
   "S = Q @ K.T / np.sqrt(K.shape[-1]) ; np.where(masque, S, -1e9) ; puis softmax et P @ V."),
 E("e-attn-c", "L'auto-attention causale",
   "Écris `masque_causal(n)`, la matrice booléenne (n, n) qui autorise chaque position à voir les précédentes et elle-même, puis `auto_attention_causale(X, Wq, Wk, Wv)` qui calcule Q, K, V à partir de X et renvoie seulement la **sortie** de l'attention masquée. La fonction `attention` est fournie.",
   ATTN + r'''
def masque_causal(n):
    pass

def auto_attention_causale(X, Wq, Wk, Wv):
    pass
''',
   ATTN + r'''
def masque_causal(n):
    return np.tril(np.ones((n, n), dtype=bool))

def auto_attention_causale(X, Wq, Wk, Wv):
    Q, K, V = X @ Wq, X @ Wk, X @ Wv
    return attention(Q, K, V, masque_causal(len(X)))[0]

rng = np.random.default_rng(0)
X = rng.normal(size=(4, 6))
Wq, Wk, Wv = (rng.normal(size=(6, 3)) for _ in range(3))
print(masque_causal(4).astype(int))
print(auto_attention_causale(X, Wq, Wk, Wv).round(2))
''',
   r'''import numpy as np
m = masque_causal(4)
assert m is not None and m.dtype == bool and m.shape == (4, 4), "masque_causal doit renvoyer un tableau booléen (n, n)."
assert (m == np.tril(np.ones((4, 4), dtype=bool))).all(), "Chaque ligne i doit autoriser les colonnes 0 à i (np.tril)."
rng = np.random.default_rng(7)
X = rng.normal(size=(5, 6)); Wq, Wk, Wv = (rng.normal(size=(6, 3)) for _ in range(3))
Y = auto_attention_causale(X, Wq, Wk, Wv)
assert Y.shape == (5, 3), f"La sortie doit avoir la forme (5, 3) ; elle a {Y.shape}."
assert np.allclose(Y[0], (X @ Wv)[0]), "Le premier token ne voit que lui-même : sa sortie doit être sa propre valeur V[0]."
X2 = X.copy(); X2[4] += 10
assert np.allclose(auto_attention_causale(X2, Wq, Wk, Wv)[:4], Y[:4]), "Modifier le dernier token ne doit pas changer les sorties précédentes : le futur est masqué."
''',
   "Q, K, V = X @ Wq, X @ Wk, X @ Wv ; attention(...) renvoie (sortie, poids) : garde [0]."),
]},
# ================================================================ Transformer
{"id": "l-transfo", "title": "Le Transformer, bloc par bloc", "minutes": 130,
"body": r'''
L'attention seule ne suffit pas. Le **Transformer** l'entoure de quelques briques simples, empilées des dizaines de fois. Voici l'architecture d'un modèle de type GPT, de l'entrée à la sortie :

1. Les tokens deviennent des vecteurs (**embeddings**), auxquels on ajoute la **position**.
2. On empile N **blocs**, chacun fait d'une attention multi-têtes et d'un petit réseau dense, avec des **connexions résiduelles** et une **normalisation**.
3. Une dernière projection donne un score (*logit*) par mot du vocabulaire ; un softmax en fait des probabilités pour le token suivant.

## L'attention multi-têtes

Une seule attention capture un seul type de relation. On en fait donc plusieurs en parallèle, les **têtes** (*heads*) : on découpe la dimension d_model en h morceaux de taille d_k = d_model / h. Une tête peut suivre la grammaire, une autre les références (« il » → « chat »), une autre le token précédent. Les sorties sont recollées puis projetées par une matrice W_O.

```viz heads
```

```python
import numpy as np
rng = np.random.default_rng(0)
n, d, h = 5, 12, 3
dk = d // h
X = rng.normal(size=(n, d))
Wq, Wk, Wv, Wo = (rng.normal(size=(d, d)) / np.sqrt(d) for _ in range(4))

def separer(M):                                   # (n, d) → (h, n, dk)
    return M.reshape(n, h, dk).transpose(1, 0, 2)

Q, K, V = separer(X @ Wq), separer(X @ Wk), separer(X @ Wv)
S = Q @ K.transpose(0, 2, 1) / np.sqrt(dk)        # (h, n, n) : une matrice d'attention par tête
A = np.exp(S - S.max(-1, keepdims=True)); A /= A.sum(-1, keepdims=True)
Z = (A @ V).transpose(1, 0, 2).reshape(n, d)      # on recolle les têtes
print("attention :", A.shape, "→ sortie :", (Z @ Wo).shape)
```

## La position

L'attention ne voit pas l'ordre : mélanger les tokens mélange les sorties de la même façon. Il faut donc **injecter la position**. L'article original ajoute à chaque embedding un vecteur de sinus et de cosinus de fréquences différentes :

```latex
PE_{(pos,\,2i)} = \sin\!\left(\frac{pos}{10000^{2i/d}}\right) \qquad PE_{(pos,\,2i+1)} = \cos\!\left(\frac{pos}{10000^{2i/d}}\right)
```

```python
import matplotlib.pyplot as plt
pos = np.arange(60)[:, None]
i = np.arange(0, 64, 2)[None, :]
angle = pos / 10000 ** (i / 64)
PE = np.zeros((60, 64)); PE[:, 0::2] = np.sin(angle); PE[:, 1::2] = np.cos(angle)
plt.figure(figsize=(8, 3))
plt.imshow(PE.T, aspect="auto", cmap="RdBu")
plt.xlabel("position"); plt.ylabel("dimension"); plt.title("Encodage positionnel sinusoïdal")
plt.colorbar(); plt.show()
```

Chaque position reçoit une « empreinte » unique : les premières dimensions oscillent vite, les dernières lentement. GPT-2 apprend plutôt ses vecteurs de position ; les modèles récents (Llama, Mistral) utilisent **RoPE**, qui fait tourner Q et K d'un angle proportionnel à la position.

## Résiduel, normalisation et réseau dense

Dans chaque bloc :

```latex
x \leftarrow x + \mathrm{Attention}(\mathrm{LN}(x)) \qquad x \leftarrow x + \mathrm{FFN}(\mathrm{LN}(x))
```

- La **connexion résiduelle** (*x +*) laisse passer l'information et le gradient intacts : c'est ce qui permet d'empiler 100 couches.
- La **normalisation de couche** (*LayerNorm*) recentre chaque vecteur (moyenne 0, écart-type 1), puis applique un gain et un décalage appris.
- Le **FFN** est un petit MLP appliqué à chaque token séparément : d → 4d → d, avec une activation GELU. Il contient les deux tiers des paramètres : on pense que c'est là que le modèle stocke ses connaissances.

## Trois familles

| Famille | Attention | Exemples | Usage |
| --- | --- | --- | --- |
| **Encodeur seul** | Voit toute la phrase | BERT, RoBERTa | Classification, extraction, embeddings |
| **Décodeur seul** | Causale | GPT, Llama, Mistral, Claude | Génération de texte, chat, code |
| **Encodeur-décodeur** | Les deux, plus l'attention croisée | T5, BART, Whisper | Traduction, résumé, transcription |

## Combien de paramètres

Par bloc : 4d² pour l'attention (W_Q, W_K, W_V, W_O) et 8d² pour le FFN (d × 4d deux fois). Soit environ **12 d² par couche**, plus les embeddings.

```python
for nom, d, L in [("GPT-2 small", 768, 12), ("GPT-2 XL", 1600, 48), ("GPT-3", 12288, 96)]:
    print(f"{nom:12s} d = {d:5d}, {L:2d} couches → environ {12 * L * d * d / 1e9:6.2f} milliards de paramètres dans les blocs")
```

## Générer du texte

Un modèle décodeur génère **un token à la fois** : il prédit une distribution, on tire un token, on l'ajoute à l'entrée, on recommence. Plusieurs stratégies de tirage :

- **Glouton** (*greedy*) : toujours le plus probable. Déterministe, mais répétitif.
- **Température** : divise les logits par T avant le softmax (vu en Essentials).
- **Top-k** : ne garde que les k tokens les plus probables.
- **Top-p** (*nucleus*) : garde le plus petit ensemble de tokens dont la probabilité cumulée atteint p. Il s'adapte : peu de candidats quand le modèle est sûr, beaucoup quand il hésite.

```viz topp
```

## Le cache KV

À chaque nouveau token, recalculer l'attention de toute la séquence serait du gaspillage : les clés et valeurs des tokens précédents ne changent pas (le masque causal les protège du futur). On les garde en mémoire, c'est le **cache KV**. Le nouveau token calcule seulement sa requête, sa clé et sa valeur. Ce cache explique pourquoi les longues conversations consomment autant de mémoire GPU.

> **À retenir** : embeddings + position → N × [attention multi-têtes + FFN, avec résiduel et LayerNorm] → logits. Encodeur pour comprendre, décodeur pour générer. Environ 12 d² paramètres par couche. Génération token par token, accélérée par le cache KV.
''',
"exercises": [
 E("e-tr-a", "Compter les paramètres d'un GPT",
   "Écris `n_parametres(vocab, d, n_couches, n_ctx)` qui compte exactement les paramètres d'un GPT-2 : embeddings de tokens (vocab × d) et de positions (n_ctx × d) ; par couche, deux LayerNorm (gain et biais : 2d chacune), l'attention (W_QKV : d × 3d + biais 3d ; W_O : d × d + biais d) et le FFN (d × 4d + biais 4d ; 4d × d + biais d) ; une LayerNorm finale (2d). La projection de sortie partage les poids des embeddings de tokens : ne la compte pas.",
   r'''def n_parametres(vocab, d, n_couches, n_ctx):
    pass

print(n_parametres(50257, 768, 12, 1024))
''',
   r'''def n_parametres(vocab, d, n_couches, n_ctx):
    embeddings = vocab * d + n_ctx * d
    ln = 2 * d
    attention = d * 3 * d + 3 * d + d * d + d
    ffn = d * 4 * d + 4 * d + 4 * d * d + d
    par_couche = 2 * ln + attention + ffn
    return embeddings + n_couches * par_couche + ln

print(f"GPT-2 small : {n_parametres(50257, 768, 12, 1024):,}".replace(",", " "))
''',
   r'''assert n_parametres(50257, 768, 12, 1024) == 124439808, f"Pour GPT-2 small, on attend 124 439 808 paramètres ; tu en comptes {n_parametres(50257, 768, 12, 1024)}."
assert n_parametres(50257, 1024, 24, 1024) == 354823168, "Pour GPT-2 medium, on attend 354 823 168 paramètres."
assert n_parametres(10, 4, 0, 3) == 10 * 4 + 3 * 4 + 8, "Sans couche, il reste les embeddings et la LayerNorm finale."
''',
   "Par couche : 2 × 2d (LayerNorm) + 4d² + 4d (attention) + 8d² + 5d (FFN)."),
 E("e-tr-b", "La normalisation de couche",
   "Écris `layer_norm(x, gamma, beta, eps=1e-5)` qui normalise chaque vecteur le long du **dernier axe** : (x − moyenne) / √(variance + eps), puis multiplie par `gamma` et ajoute `beta`.",
   r'''import numpy as np

def layer_norm(x, gamma, beta, eps=1e-5):
    pass
''',
   r'''import numpy as np

def layer_norm(x, gamma, beta, eps=1e-5):
    m = x.mean(axis=-1, keepdims=True)
    v = x.var(axis=-1, keepdims=True)
    return gamma * (x - m) / np.sqrt(v + eps) + beta

x = np.array([[1.0, 2.0, 3.0, 4.0], [10.0, 0.0, 10.0, 0.0]])
print(layer_norm(x, np.ones(4), np.zeros(4)).round(3))
''',
   r'''import numpy as np
rng = np.random.default_rng(0)
x = rng.normal(5, 3, size=(6, 8))
y = layer_norm(x, np.ones(8), np.zeros(8))
assert y is not None and y.shape == (6, 8), "layer_norm doit renvoyer un tableau de même forme que x."
assert np.allclose(y.mean(axis=-1), 0, atol=1e-6) and np.allclose(y.std(axis=-1), 1, atol=1e-3), "Chaque ligne doit avoir une moyenne 0 et un écart-type 1 : normalise sur le dernier axe."
g, b = rng.normal(size=8), rng.normal(size=8)
attendu = g * (x - x.mean(-1, keepdims=True)) / np.sqrt(x.var(-1, keepdims=True) + 1e-5) + b
assert np.allclose(layer_norm(x, g, b), attendu), "Applique gamma (multiplication) puis beta (addition) après la normalisation."
''',
   "x.mean(axis=-1, keepdims=True) et x.var(axis=-1, keepdims=True)."),
 E("e-tr-c", "L'attention multi-têtes",
   "Écris `multi_tetes(X, Wq, Wk, Wv, Wo, h)` : X est (n, d), les quatre matrices (d, d). Découpe Q, K, V en h têtes de taille d // h, applique l'attention (sans masque) dans chaque tête, recolle les têtes dans l'ordre, puis multiplie par Wo. Le `softmax` est fourni.",
   r'''import numpy as np

def softmax(x, axis=-1):
    x = x - x.max(axis=axis, keepdims=True)
    e = np.exp(x)
    return e / e.sum(axis=axis, keepdims=True)

def multi_tetes(X, Wq, Wk, Wv, Wo, h):
    pass
''',
   r'''import numpy as np

def softmax(x, axis=-1):
    x = x - x.max(axis=axis, keepdims=True)
    e = np.exp(x)
    return e / e.sum(axis=axis, keepdims=True)

def multi_tetes(X, Wq, Wk, Wv, Wo, h):
    n, d = X.shape
    dk = d // h
    sep = lambda M: M.reshape(n, h, dk).transpose(1, 0, 2)
    Q, K, V = sep(X @ Wq), sep(X @ Wk), sep(X @ Wv)
    A = softmax(Q @ K.transpose(0, 2, 1) / np.sqrt(dk))
    Z = (A @ V).transpose(1, 0, 2).reshape(n, d)
    return Z @ Wo

rng = np.random.default_rng(0)
X = rng.normal(size=(4, 8))
Wq, Wk, Wv, Wo = (rng.normal(size=(8, 8)) for _ in range(4))
print(multi_tetes(X, Wq, Wk, Wv, Wo, 2).shape)
''',
   r'''import numpy as np
rng = np.random.default_rng(11)
n, d, h = 5, 12, 3
X = rng.normal(size=(n, d)); Wq, Wk, Wv, Wo = (rng.normal(size=(d, d)) / 3 for _ in range(4))
Y = multi_tetes(X, Wq, Wk, Wv, Wo, h)
assert Y is not None and Y.shape == (n, d), f"La sortie doit avoir la forme ({n}, {d})."
dk = d // h; morceaux = []
for t in range(h):
    sl = slice(t * dk, (t + 1) * dk)
    Q, K, V = (X @ Wq)[:, sl], (X @ Wk)[:, sl], (X @ Wv)[:, sl]
    S = Q @ K.T / np.sqrt(dk); P = np.exp(S - S.max(1, keepdims=True)); P /= P.sum(1, keepdims=True)
    morceaux.append(P @ V)
attendu = np.concatenate(morceaux, axis=1) @ Wo
assert np.allclose(Y, attendu), "Le résultat ne correspond pas : chaque tête prend une tranche consécutive de d_k colonnes, et on divise par √d_k (pas √d)."
assert not np.allclose(multi_tetes(X, Wq, Wk, Wv, Wo, 1), Y), "Le nombre de têtes doit changer le résultat."
''',
   "reshape(n, h, dk).transpose(1, 0, 2) donne (h, n, dk) ; pour recoller : transpose(1, 0, 2).reshape(n, d)."),
 E("e-tr-d", "L'échantillonnage top-p",
   "Écris `top_p(probas, p)` : garde le plus petit ensemble de tokens, pris du plus probable au moins probable, dont la probabilité cumulée atteint au moins `p`. Mets les autres à 0 et renormalise pour que la somme vaille 1. Le résultat reste dans l'ordre d'origine du vocabulaire.",
   r'''import numpy as np

def top_p(probas, p):
    pass
''',
   r'''import numpy as np

def top_p(probas, p):
    ordre = np.argsort(probas)[::-1]
    cumul = np.cumsum(probas[ordre])
    n_gardes = int(np.searchsorted(cumul, p)) + 1
    garde = np.zeros_like(probas)
    garde[ordre[:n_gardes]] = probas[ordre[:n_gardes]]
    return garde / garde.sum()

print(top_p(np.array([0.1, 0.5, 0.05, 0.2, 0.15]), 0.8))
''',
   r'''import numpy as np
pr = np.array([0.1, 0.5, 0.05, 0.2, 0.15])
r = top_p(pr, 0.8)
assert r is not None and r.shape == pr.shape, "top_p doit renvoyer un tableau de même taille, dans l'ordre d'origine."
assert np.allclose(r, np.array([0, 0.5, 0, 0.2, 0.15]) / 0.85), "Avec p = 0.8 : on garde 0.5, 0.2 et 0.15 (cumul 0.85), puis on renormalise."
assert np.allclose(top_p(pr, 0.4), [0, 1, 0, 0, 0]), "Si le token le plus probable atteint p à lui seul, il est le seul gardé."
assert np.allclose(top_p(pr, 1.0).sum(), 1) and (top_p(pr, 1.0) > 0).all(), "Avec p = 1, tous les tokens sont gardés."
''',
   "np.argsort(probas)[::-1] trie du plus probable au moins probable ; np.cumsum donne le cumul."),
]},
# ================================================================ Tokenisation
{"id": "l-tok", "title": "Tokenisation : du texte aux identifiants", "minutes": 80,
"body": r'''
Un modèle ne lit pas des lettres : il lit des **identifiants entiers**, un par token. La tokenisation décide de ce découpage, et ce choix a des conséquences très concrètes : coût, langues mal servies, erreurs d'arithmétique. En Essentials, tu as vu une étape de BPE. Ici, on construit la chaîne complète.

## Trois niveaux de découpage

```python
texte = "Les apprenants apprennent à apprendre."
print("caractères :", len(list(texte)), "tokens")
print("mots       :", texte.split())
print("sous-mots  :", ["Les", " appren", "ants", " appren", "nent", " à", " appren", "dre", "."])
```

- **Caractères** : vocabulaire minuscule, mais des séquences très longues, et chaque caractère porte peu de sens.
- **Mots** : séquences courtes, mais un vocabulaire énorme, et tout mot inconnu devient `[UNK]`.
- **Sous-mots** : le compromis utilisé partout. Les mots fréquents restent entiers, les rares se décomposent en morceaux connus.

## La chaîne d'un tokeniseur

1. **Normalisation** : Unicode (NFC), parfois minuscules ou suppression des accents.
2. **Pré-découpage** : par espaces et ponctuation. GPT garde l'espace collé au mot suivant (« Ġappren »).
3. **Modèle** : BPE (GPT, Llama), WordPiece (BERT, avec des « ##suffixes ») ou Unigram (T5, via SentencePiece).
4. **Post-traitement** : ajout des **tokens spéciaux** : `[CLS]` et `[SEP]` pour BERT, `<|begin_of_text|>` pour Llama, les balises de rôle d'un modèle de chat.

## Le BPE au niveau des octets

GPT-2 et ses successeurs appliquent le BPE sur les **octets** UTF-8 plutôt que sur les caractères. Les 256 octets de base suffisent à tout écrire : plus jamais de token inconnu, même pour un emoji ou du chinois.

```python
for s in ["a", "é", "€", "猫"]:
    print(repr(s), "→", list(s.encode("utf-8")))
```

## Ce que la tokenisation explique

```python
mot = "anticonstitutionnellement"
fusions_apprises = ["anti", "constitution", "nelle", "ment"]
print(f"{mot} : {len(mot)} caractères, mais seulement {len(fusions_apprises)} sous-mots si le tokeniseur connaît ces morceaux")
```

- **Les langues** : un tokeniseur entraîné surtout sur de l'anglais découpe le français plus finement. Même texte, plus de tokens, donc plus cher et plus lent.
- **Les nombres** : « 12345 » peut devenir « 123 » + « 45 ». Le modèle ne voit pas les chiffres alignés, d'où des erreurs de calcul. Llama 3 découpe les nombres en groupes de trois chiffres maximum pour limiter le problème.
- **L'orthographe** : compter les « r » de « strawberry » est difficile quand le mot est un seul token.

## Préparer un lot

Les séquences d'un lot (*batch*) n'ont pas la même longueur. On les **complète** (*padding*) avec un identifiant spécial jusqu'à la même longueur, et on fournit un **masque d'attention** : 1 pour un vrai token, 0 pour du remplissage, pour que le modèle l'ignore. Au-delà de la longueur maximale du modèle, on **tronque**.

```pycode
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained("camembert-base")
lot = tok(["Bonjour !", "Le chat dort sur le tapis."], padding=True, truncation=True, max_length=16, return_tensors="pt")
print(lot["input_ids"])        # identifiants, complétés avec le token de padding
print(lot["attention_mask"])   # 1 = vrai token, 0 = remplissage
print(tok.convert_ids_to_tokens(lot["input_ids"][1]))
```

> **À retenir** : texte → normalisation → pré-découpage → sous-mots (BPE, WordPiece, Unigram) → tokens spéciaux → identifiants. Le padding et le masque d'attention permettent de traiter des lots. La tokenisation explique les coûts par langue et les faiblesses en calcul.
''',
"exercises": [
 E("e-tok-a", "Entraîner un BPE",
   "Écris `entrainer_bpe(corpus, n_fusions)`. `corpus` est un dictionnaire {mot: fréquence}. Chaque mot commence découpé en caractères. À chaque étape, compte les paires de symboles voisins (pondérées par la fréquence du mot), fusionne la plus fréquente partout, et note-la. En cas d'égalité, garde la paire rencontrée en premier (c'est ce que fait `Counter.most_common(1)`). Renvoie la liste des fusions, sous forme de tuples comme `('e', 's')`.",
   r'''from collections import Counter

def entrainer_bpe(corpus, n_fusions):
    pass

corpus = {"low": 5, "lower": 2, "newest": 6, "widest": 3}
''',
   r'''from collections import Counter

def entrainer_bpe(corpus, n_fusions):
    mots = {tuple(m): f for m, f in corpus.items()}
    fusions = []
    for _ in range(n_fusions):
        paires = Counter()
        for symboles, f in mots.items():
            for a, b in zip(symboles, symboles[1:]):
                paires[(a, b)] += f
        if not paires:
            break
        (a, b), _ = paires.most_common(1)[0]
        fusions.append((a, b))
        nouveaux = {}
        for symboles, f in mots.items():
            res, i = [], 0
            while i < len(symboles):
                if i < len(symboles) - 1 and symboles[i] == a and symboles[i + 1] == b:
                    res.append(a + b); i += 2
                else:
                    res.append(symboles[i]); i += 1
            nouveaux[tuple(res)] = f
        mots = nouveaux
    return fusions

corpus = {"low": 5, "lower": 2, "newest": 6, "widest": 3}
print(entrainer_bpe(corpus, 6))
''',
   r'''from collections import Counter
def _ref(corpus, n):
    mots = {tuple(m): f for m, f in corpus.items()}; out = []
    for _ in range(n):
        c = Counter()
        for s, f in mots.items():
            for p in zip(s, s[1:]): c[p] += f
        if not c: break
        (a, b), _ = c.most_common(1)[0]; out.append((a, b)); nm = {}
        for s, f in mots.items():
            r, i = [], 0
            while i < len(s):
                if i < len(s) - 1 and s[i] == a and s[i + 1] == b: r.append(a + b); i += 2
                else: r.append(s[i]); i += 1
            nm[tuple(r)] = f
        mots = nm
    return out
c1 = {"low": 5, "lower": 2, "newest": 6, "widest": 3}
r = entrainer_bpe(c1, 6)
assert isinstance(r, list) and len(r) == 6, "entrainer_bpe doit renvoyer une liste de n_fusions tuples."
assert r[:2] == [("e", "s"), ("es", "t")], f"Les deux premières fusions attendues sont ('e', 's') puis ('es', 't') ; tu obtiens {r[:2]}. Pense à pondérer par la fréquence."
assert r == _ref(c1, 6), f"Fusions attendues : {_ref(c1, 6)} ; tu obtiens {r}."
c2 = {"banane": 3, "ananas": 2, "bandana": 1}
assert entrainer_bpe(c2, 5) == _ref(c2, 5), "Sur un autre corpus, les fusions ne correspondent pas : après une fusion, applique-la à tous les mots."
assert len(entrainer_bpe({"ab": 1}, 5)) == 1, "Quand il n'y a plus de paire, arrête-toi."
''',
   "Représente chaque mot comme un tuple de symboles. Après avoir choisi (a, b), reconstruis chaque tuple en remplaçant les paires voisines a, b par a + b."),
 E("e-tok-b", "Tokeniser un nouveau mot",
   "Écris `tokeniser(mot, fusions)` qui découpe un mot en caractères puis applique les fusions **dans l'ordre où elles ont été apprises**, chacune partout dans le mot. Renvoie la liste des tokens.",
   r'''def tokeniser(mot, fusions):
    pass

fusions = [("e", "s"), ("es", "t"), ("l", "o"), ("lo", "w"), ("n", "e"), ("ne", "w")]
''',
   r'''def tokeniser(mot, fusions):
    symboles = list(mot)
    for a, b in fusions:
        res, i = [], 0
        while i < len(symboles):
            if i < len(symboles) - 1 and symboles[i] == a and symboles[i + 1] == b:
                res.append(a + b); i += 2
            else:
                res.append(symboles[i]); i += 1
        symboles = res
    return symboles

fusions = [("e", "s"), ("es", "t"), ("l", "o"), ("lo", "w"), ("n", "e"), ("ne", "w")]
for m in ["lowest", "newer", "slow", "zest"]:
    print(m, "→", tokeniser(m, fusions))
''',
   r'''f = [("e", "s"), ("es", "t"), ("l", "o"), ("lo", "w"), ("n", "e"), ("ne", "w")]
assert tokeniser("lowest", f) == ["low", "est"], f"'lowest' doit donner ['low', 'est'] ; tu obtiens {tokeniser('lowest', f)}."
assert tokeniser("newer", f) == ["new", "e", "r"], "'newer' doit donner ['new', 'e', 'r']."
assert tokeniser("xyz", f) == ["x", "y", "z"], "Sans fusion applicable, on garde les caractères."
assert tokeniser("aaa", [("a", "a")]) == ["aa", "a"], "Une fusion se fait de gauche à droite, sans chevauchement."
''',
   "Même boucle de remplacement que dans l'entraînement, appliquée fusion après fusion."),
 E("e-tok-c", "Compléter et masquer un lot",
   "Écris `preparer_lot(sequences, pad_id=0, max_len=None)` : `sequences` est une liste de listes d'identifiants. Tronque chaque séquence à `max_len` si elle est donnée, complète à droite avec `pad_id` jusqu'à la longueur de la plus longue, et renvoie `(ids, masque)`, deux tableaux NumPy d'entiers (n, L). Le masque vaut 1 pour un vrai token et 0 pour le remplissage.",
   r'''import numpy as np

def preparer_lot(sequences, pad_id=0, max_len=None):
    pass
''',
   r'''import numpy as np

def preparer_lot(sequences, pad_id=0, max_len=None):
    if max_len is not None:
        sequences = [s[:max_len] for s in sequences]
    L = max(len(s) for s in sequences)
    ids = np.full((len(sequences), L), pad_id, dtype=int)
    masque = np.zeros((len(sequences), L), dtype=int)
    for i, s in enumerate(sequences):
        ids[i, :len(s)] = s
        masque[i, :len(s)] = 1
    return ids, masque

ids, masque = preparer_lot([[5, 8, 2], [7], [3, 3, 3, 3, 3]], max_len=4)
print(ids); print(masque)
''',
   r'''import numpy as np
r = preparer_lot([[5, 8, 2], [7], [9, 4]])
assert isinstance(r, tuple) and len(r) == 2, "preparer_lot doit renvoyer le tuple (ids, masque)."
ids, m = r
assert (ids == np.array([[5, 8, 2], [7, 0, 0], [9, 4, 0]])).all(), f"ids attendus : [[5, 8, 2], [7, 0, 0], [9, 4, 0]] ; tu as {ids.tolist()}."
assert (m == np.array([[1, 1, 1], [1, 0, 0], [1, 1, 0]])).all(), "Le masque vaut 1 pour un vrai token, 0 pour le remplissage."
ids2, m2 = preparer_lot([[1, 2, 3, 4, 5], [6]], pad_id=-1, max_len=3)
assert ids2.shape == (2, 3) and (ids2[1] == [6, -1, -1]).all(), "Respecte pad_id et tronque à max_len."
assert (m2[0] == 1).all(), "Une séquence tronquée n'a pas de remplissage."
''',
   "np.full((n, L), pad_id) crée le tableau rempli ; puis copie chaque séquence dans sa ligne."),
]},
# ================================================================ Hugging Face
{"id": "l-hf", "title": "Transformers appliqués avec Hugging Face", "minutes": 90,
"body": r'''
**Hugging Face** est le GitHub des modèles : plus d'un million de modèles, de jeux de données et de démos. Sa bibliothèque `transformers` charge n'importe lequel en trois lignes. Elle a besoin de PyTorch, donc tout ce qui suit se fait **sur ton ordinateur** ou dans Google Colab. Les exercices de la page reproduisent en NumPy ce que la bibliothèque fait pour toi.

## Le plus court chemin : pipeline

```pycode
from transformers import pipeline

sentiment = pipeline("text-classification", model="cmarkea/distilcamembert-base-sentiment")
print(sentiment("Cette formation est vraiment exigeante, mais passionnante."))

resume = pipeline("summarization", model="facebook/bart-large-cnn")
zero_shot = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
print(zero_shot("Mon colis n'est jamais arrivé", candidate_labels=["livraison", "facturation", "compte"]))
```

## Ce que fait le pipeline

```pycode
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

nom = "cmarkea/distilcamembert-base-sentiment"
tok = AutoTokenizer.from_pretrained(nom)
modele = AutoModelForSequenceClassification.from_pretrained(nom)

entree = tok(["Super cours !", "Je n'ai rien compris."], padding=True, return_tensors="pt")
with torch.no_grad():
    logits = modele(**entree).logits          # (2, nombre de classes)
probas = logits.softmax(dim=-1)
print([modele.config.id2label[i] for i in probas.argmax(dim=-1).tolist()])
```

Trois étapes : le tokeniseur fabrique `input_ids` et `attention_mask`, le modèle renvoie des **logits**, et un softmax les transforme en probabilités. `config.id2label` traduit les indices en noms de classes.

## Des embeddings de phrases

Un encodeur renvoie un vecteur **par token**. Pour un vecteur **par phrase** (recherche sémantique, RAG), on fait la moyenne des vecteurs des vrais tokens, en ignorant le padding grâce au masque : c'est le *mean pooling*. La bibliothèque `sentence-transformers` le fait pour toi.

```pycode
from sentence_transformers import SentenceTransformer
m = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
emb = m.encode(["Comment réinitialiser mon mot de passe ?", "J'ai oublié mon mot de passe", "Quel temps fait-il ?"])
print(emb.shape)   # (3, 384)
```

## Affiner un modèle

```pycode
from datasets import load_dataset
from transformers import Trainer, TrainingArguments

ds = load_dataset("allocine")                    # critiques de films en français
ds = ds.map(lambda b: tok(b["review"], truncation=True, max_length=256), batched=True)
args = TrainingArguments("sortie", per_device_train_batch_size=16, num_train_epochs=1, learning_rate=2e-5, eval_strategy="epoch")
Trainer(model=modele, args=args, train_dataset=ds["train"].shuffle(seed=0).select(range(5000)),
        eval_dataset=ds["validation"].select(range(1000)), tokenizer=tok).train()
```

## Choisir un modèle sur le Hub

- Lis la **fiche du modèle** (*model card*) : données d'entraînement, langues, limites, résultats.
- Vérifie la **licence** : Apache 2.0 et MIT permettent un usage commercial ; certaines licences l'interdisent ou le limitent.
- Regarde la **taille** : un modèle de 100 millions de paramètres tourne sur un CPU, un de 7 milliards demande un GPU ou de la quantification.
- Pour le français : CamemBERT, FlauBERT, et les modèles multilingues (mDeBERTa, XLM-R, E5).

> **À retenir** : `pipeline` pour essayer, `AutoTokenizer` + `AutoModel...` pour contrôler, `Trainer` pour affiner. Logits → softmax → id2label. Mean pooling avec le masque pour un embedding de phrase.
''',
"tasks": [
  "Installer transformers, datasets et sentence-transformers dans un environnement virtuel (ou ouvrir Google Colab)",
  "Faire tourner trois pipelines : sentiment, résumé et classification zero-shot, sur des textes en français",
  "Calculer les embeddings de 20 questions de support avec sentence-transformers et trouver les plus proches d'une nouvelle question",
  "Affiner DistilCamemBERT sur 5 000 critiques AlloCiné avec Trainer et noter l'exactitude obtenue",
],
"exercises": [
 E("e-hf-a", "Le mean pooling",
   "Écris `mean_pooling(etats, masque)` : `etats` a la forme (lot, longueur, d) et `masque` (lot, longueur) vaut 1 pour un vrai token et 0 pour le remplissage. Renvoie, pour chaque phrase, la moyenne des vecteurs de ses vrais tokens seulement : un tableau (lot, d).",
   r'''import numpy as np

def mean_pooling(etats, masque):
    pass
''',
   r'''import numpy as np

def mean_pooling(etats, masque):
    m = masque[:, :, None].astype(float)
    return (etats * m).sum(axis=1) / np.clip(m.sum(axis=1), 1e-9, None)

etats = np.arange(24, dtype=float).reshape(2, 4, 3)
masque = np.array([[1, 1, 0, 0], [1, 1, 1, 1]])
print(mean_pooling(etats, masque))
''',
   r'''import numpy as np
rng = np.random.default_rng(0)
etats = rng.normal(size=(3, 5, 4))
masque = np.array([[1, 1, 1, 0, 0], [1, 1, 1, 1, 1], [1, 0, 0, 0, 0]])
r = mean_pooling(etats, masque)
assert r is not None and r.shape == (3, 4), "La sortie doit avoir la forme (lot, d)."
assert np.allclose(r[0], etats[0, :3].mean(axis=0)), "La première phrase a 3 vrais tokens : moyenne des 3 premiers vecteurs seulement."
assert np.allclose(r[2], etats[2, 0]), "Une phrase d'un seul token a pour embedding ce token."
assert np.allclose(r[1], etats[1].mean(axis=0)), "Sans padding, c'est la moyenne simple."
''',
   "masque[:, :, None] ajoute un axe pour multiplier les états ; divise par le nombre de vrais tokens, masque.sum(axis=1)."),
 E("e-hf-b", "Des logits aux étiquettes",
   "Écris `predire(logits, id2label)` : `logits` est (n, k), `id2label` un dictionnaire {indice: nom}. Renvoie une liste de n dictionnaires `{\"label\": nom, \"score\": probabilité}`, la probabilité venant d'un softmax et arrondie à 4 décimales, comme le fait un pipeline.",
   r'''import numpy as np

def predire(logits, id2label):
    pass

id2label = {0: "négatif", 1: "neutre", 2: "positif"}
''',
   r'''import numpy as np

def predire(logits, id2label):
    z = logits - logits.max(axis=1, keepdims=True)
    p = np.exp(z) / np.exp(z).sum(axis=1, keepdims=True)
    return [{"label": id2label[int(i)], "score": round(float(p[r, i]), 4)} for r, i in enumerate(p.argmax(axis=1))]

id2label = {0: "négatif", 1: "neutre", 2: "positif"}
print(predire(np.array([[2.0, 0.1, -1.0], [-1.0, 0.0, 3.0]]), id2label))
''',
   r'''import numpy as np
id2 = {0: "négatif", 1: "neutre", 2: "positif"}
L = np.array([[2.0, 0.1, -1.0], [-1.0, 0.0, 3.0], [0.0, 0.0, 0.0]])
r = predire(L, id2)
assert isinstance(r, list) and len(r) == 3, "predire doit renvoyer une liste avec un dictionnaire par ligne."
assert [d["label"] for d in r] == ["négatif", "positif", "négatif"], f"Étiquettes attendues : négatif, positif, négatif (en cas d'égalité, argmax prend la première) ; tu as {[d['label'] for d in r]}."
p = np.exp(L[1]) / np.exp(L[1]).sum()
assert abs(r[1]["score"] - round(p[2], 4)) < 1e-9, "Le score est la probabilité softmax de la classe prédite, arrondie à 4 décimales."
assert isinstance(r[0]["score"], float), "Convertis le score en float Python."
''',
   "Softmax ligne par ligne, argmax(axis=1), puis id2label[int(i)]."),
]},
# ================================================================ CLIP
{"id": "l-clip", "title": "CLIP et l'apprentissage contrastif", "minutes": 90,
"body": r'''
**CLIP** (OpenAI, 2021) relie les images et le texte. Il a appris sur 400 millions de paires (image, légende) trouvées sur le web, sans aucune étiquette faite à la main. Résultat : un espace où une photo de chat et la phrase « une photo de chat » ont des vecteurs proches. On le retrouve partout : recherche d'images par texte, filtrage de contenu, et comme encodeur de texte de Stable Diffusion.

## Deux encodeurs, un espace commun

- Un **encodeur d'image** (un Vision Transformer ou un ResNet) transforme chaque image en vecteur.
- Un **encodeur de texte** (un Transformer) transforme chaque légende en vecteur de même dimension.
- On normalise les deux pour que leur produit scalaire soit une **similarité cosinus**.

## L'apprentissage contrastif

On prend un lot de N paires. On calcule les N × N similarités entre toutes les images et toutes les légendes. Sur la diagonale, les **bonnes paires** ; partout ailleurs, des paires qui ne vont pas ensemble. L'objectif : rendre la diagonale grande et le reste petit.

```viz clip
```

Concrètement, chaque ligne de la matrice est un problème de classification à N classes (« quelle légende va avec cette image ? »), et chaque colonne aussi (« quelle image va avec cette légende ? »). La perte est la moyenne des deux entropies croisées. C'est la perte **InfoNCE** :

```latex
L = \frac{1}{2}\Big[\mathrm{CE}\big(S/\tau,\ \mathrm{diag}\big) + \mathrm{CE}\big(S^\top/\tau,\ \mathrm{diag}\big)\Big] \qquad S_{ij} = \frac{\langle v_i, t_j \rangle}{\lVert v_i\rVert \lVert t_j\rVert}
```

La **température** τ (environ 0,07, apprise) étire les écarts de similarité pour que le softmax tranche.

```python
import numpy as np
rng = np.random.default_rng(0)
concepts = rng.normal(size=(4, 16))                       # 4 « idées » : chat, voiture, plage, pizza
images = concepts + 0.4 * rng.normal(size=(4, 16))         # ce que voit l'encodeur d'image
textes = concepts + 0.4 * rng.normal(size=(4, 16))         # ce que voit l'encodeur de texte
norme = lambda M: M / np.linalg.norm(M, axis=1, keepdims=True)
S = norme(images) @ norme(textes).T
print("similarités (ligne = image, colonne = légende) :")
print(S.round(2))
print("légende choisie pour chaque image :", S.argmax(axis=1))
```

## La classification zero-shot

CLIP sait classer des images dans des catégories qu'il n'a jamais vues comme telles. On écrit une phrase par classe, par exemple « une photo de {classe} », on encode ces phrases, et chaque image reçoit la classe dont la phrase est la plus proche. Aucun entraînement supplémentaire. Soigner ces phrases (*prompt engineering* pour la vision) fait gagner plusieurs points d'exactitude.

```pycode
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

modele = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
proc = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
classes = ["chat", "chien", "voiture", "pizza"]
entree = proc(text=[f"une photo de {c}" for c in classes], images=Image.open("photo.jpg"), return_tensors="pt", padding=True)
with torch.no_grad():
    probas = modele(**entree).logits_per_image.softmax(dim=-1)
print(dict(zip(classes, probas[0].round(decimals=3).tolist())))
```

## Les limites

CLIP compte mal (« trois chats »), confond les relations spatiales (« un chat sur un chien »), et hérite des biais des légendes du web. Les modèles plus récents (SigLIP, et les LLM multimodaux comme Claude ou GPT-4o) partent de la même idée d'un espace partagé.

> **À retenir** : deux encodeurs, un espace commun, une matrice de similarités N × N, et une perte qui pousse la diagonale. Zero-shot = comparer une image à des phrases « une photo de {classe} ».
''',
"exercises": [
 E("e-clip-a", "La matrice de similarités",
   "Écris `similarites(images, textes)` : chaque argument est (n, d) ou (m, d). Normalise chaque ligne à une norme de 1, puis renvoie la matrice (n, m) des similarités cosinus.",
   r'''import numpy as np

def similarites(images, textes):
    pass
''',
   r'''import numpy as np

def similarites(images, textes):
    I = images / np.linalg.norm(images, axis=1, keepdims=True)
    T = textes / np.linalg.norm(textes, axis=1, keepdims=True)
    return I @ T.T

print(similarites(np.array([[1.0, 0.0], [1.0, 1.0]]), np.array([[2.0, 0.0], [0.0, 3.0], [-1.0, -1.0]])).round(3))
''',
   r'''import numpy as np
rng = np.random.default_rng(2)
A, B = rng.normal(size=(4, 6)), rng.normal(size=(3, 6))
S = similarites(A, B)
assert S is not None and S.shape == (4, 3), "La matrice doit avoir la forme (n, m)."
attendu = np.array([[a @ b / np.linalg.norm(a) / np.linalg.norm(b) for b in B] for a in A])
assert np.allclose(S, attendu), "Ce ne sont pas des similarités cosinus : normalise chaque ligne avant le produit."
assert np.allclose(similarites(A, 5 * A).diagonal(), 1), "Un vecteur et le même vecteur multiplié par 5 ont une similarité de 1."
''',
   "np.linalg.norm(M, axis=1, keepdims=True) donne la norme de chaque ligne."),
 E("e-clip-b", "La perte contrastive de CLIP",
   "Écris `perte_clip(images, textes, temperature=0.07)` : calcule les similarités cosinus S (la fonction `similarites` est fournie), divise par la température, puis renvoie la moyenne de deux entropies croisées où la bonne réponse de la ligne i est la colonne i : une sur les lignes de S, une sur les lignes de Sᵀ.",
   r'''import numpy as np

def similarites(images, textes):
    I = images / np.linalg.norm(images, axis=1, keepdims=True)
    T = textes / np.linalg.norm(textes, axis=1, keepdims=True)
    return I @ T.T

def perte_clip(images, textes, temperature=0.07):
    pass
''',
   r'''import numpy as np

def similarites(images, textes):
    I = images / np.linalg.norm(images, axis=1, keepdims=True)
    T = textes / np.linalg.norm(textes, axis=1, keepdims=True)
    return I @ T.T

def entropie_diag(Z):
    Z = Z - Z.max(axis=1, keepdims=True)
    log_p = Z - np.log(np.exp(Z).sum(axis=1, keepdims=True))
    return -np.mean(np.diag(log_p))

def perte_clip(images, textes, temperature=0.07):
    Z = similarites(images, textes) / temperature
    return (entropie_diag(Z) + entropie_diag(Z.T)) / 2

rng = np.random.default_rng(0)
c = rng.normal(size=(8, 16))
print("paires alignées :", round(perte_clip(c + 0.1 * rng.normal(size=c.shape), c), 3))
print("paires mélangées :", round(perte_clip(rng.normal(size=c.shape), c), 3))
''',
   r'''import numpy as np
rng = np.random.default_rng(5)
I, T = rng.normal(size=(6, 8)), rng.normal(size=(6, 8))
def _ce(Z):
    P = np.exp(Z) / np.exp(Z).sum(axis=1, keepdims=True)
    return -np.mean(np.log(np.diag(P)))
S = similarites(I, T) / 0.07
attendu = (_ce(S) + _ce(S.T)) / 2
r = perte_clip(I, T)
assert r is not None and abs(r - attendu) < 1e-6, f"Perte attendue {attendu:.5f}, obtenue {r}. Vérifie la division par la température et la moyenne des deux sens."
S2 = similarites(I, T) / 0.5
assert abs(perte_clip(I, T, 0.5) - (_ce(S2) + _ce(S2.T)) / 2) < 1e-6, "La température doit être un paramètre."
assert perte_clip(T, T) < perte_clip(I, T), "Des paires parfaitement alignées doivent donner une perte plus faible."
assert np.isfinite(perte_clip(T, T, 0.001)), "Avec une température minuscule, stabilise le softmax (soustrais le maximum)."
''',
   "Écris une fonction pour l'entropie croisée « diagonale » : log-softmax par ligne, puis moyenne de −diag. Applique-la à Z et à Z.T."),
 E("e-clip-c", "Classer sans entraînement",
   "Écris `zero_shot(images, textes_classes, classes)` : `images` (n, d) sont des embeddings d'images, `textes_classes` (k, d) les embeddings des phrases « une photo de {classe} », `classes` la liste des k noms. Renvoie la liste des n noms de classe prédits (la phrase la plus similaire, en cosinus). La fonction `similarites` est fournie.",
   r'''import numpy as np

def similarites(images, textes):
    I = images / np.linalg.norm(images, axis=1, keepdims=True)
    T = textes / np.linalg.norm(textes, axis=1, keepdims=True)
    return I @ T.T

def zero_shot(images, textes_classes, classes):
    pass
''',
   r'''import numpy as np

def similarites(images, textes):
    I = images / np.linalg.norm(images, axis=1, keepdims=True)
    T = textes / np.linalg.norm(textes, axis=1, keepdims=True)
    return I @ T.T

def zero_shot(images, textes_classes, classes):
    return [classes[i] for i in similarites(images, textes_classes).argmax(axis=1)]

rng = np.random.default_rng(1)
t = rng.normal(size=(3, 8))
print(zero_shot(t[[2, 0, 1]] + 0.2 * rng.normal(size=(3, 8)), t, ["chat", "chien", "voiture"]))
''',
   r'''import numpy as np
rng = np.random.default_rng(9)
T = rng.normal(size=(4, 10)); noms = ["chat", "chien", "voiture", "pizza"]
idx = [3, 1, 1, 0, 2]
I = T[idx] * rng.uniform(0.5, 3, size=(5, 1)) + 0.2 * rng.normal(size=(5, 10))
r = zero_shot(I, T, noms)
assert r == [noms[i] for i in idx], f"Prédictions attendues {[noms[i] for i in idx]} ; tu as {r}."
''',
   "similarites(images, textes_classes).argmax(axis=1) donne l'indice de la classe pour chaque image."),
]},
# ================================================================ Diffusion
{"id": "l-diff", "title": "La diffusion : générer en débruitant", "minutes": 110,
"body": r'''
Stable Diffusion, Midjourney, DALL·E 3 et les générateurs de vidéo reposent sur une idée étonnamment simple : **apprendre à enlever du bruit**. Si un réseau sait retirer un peu de bruit d'une image bruitée, alors en partant d'un bruit pur et en répétant l'opération des centaines de fois, il fabrique une image.

## Le processus vers l'avant : détruire

On ajoute progressivement du bruit gaussien en T étapes (typiquement T = 1000). Un **programme de bruit** fixe la quantité βₜ ajoutée à chaque étape. Grâce aux propriétés des gaussiennes, on peut sauter directement à n'importe quelle étape t :

```latex
x_t = \sqrt{\bar\alpha_t}\, x_0 + \sqrt{1 - \bar\alpha_t}\; \varepsilon \qquad \varepsilon \sim \mathcal{N}(0, I) \qquad \alpha_t = 1 - \beta_t \qquad \bar\alpha_t = \prod_{s \le t} \alpha_s
```

Quand t est petit, ᾱₜ ≈ 1 : presque l'image d'origine. Quand t est grand, ᾱₜ ≈ 0 : du bruit pur.

```viz diffusion
```

## L'entraînement : prédire le bruit

On prend une image x₀, un instant t au hasard et un bruit ε. On fabrique xₜ avec la formule ci-dessus, et le réseau ε_θ(xₜ, t) doit **retrouver ε**. La perte est une simple erreur quadratique :

```latex
L = \mathbb{E}_{x_0,\, t,\, \varepsilon} \big\lVert \varepsilon - \varepsilon_\theta(x_t, t) \big\rVert^2
```

Le réseau est un **U-Net** (des convolutions qui réduisent puis agrandissent l'image) ou, dans les modèles récents, un **Transformer** sur des morceaux d'image (DiT, utilisé par Stable Diffusion 3 et Sora).

## Le processus inverse : créer

On part de x_T ~ 𝒩(0, I) et on remonte le temps. À chaque étape (algorithme DDPM) :

```latex
x_{t-1} = \frac{1}{\sqrt{\alpha_t}}\left(x_t - \frac{\beta_t}{\sqrt{1 - \bar\alpha_t}}\, \varepsilon_\theta(x_t, t)\right) + \sqrt{\beta_t}\, z \qquad z \sim \mathcal{N}(0, I)
```

On enlève le bruit prédit, puis on rajoute un peu de bruit frais (sauf à la dernière étape) pour garder de la diversité.

## Le voir en 2D

Ici, les « images » sont des points d'une spirale. Pour un jeu de données fini, le meilleur débruiteur possible se calcule exactement : il fait une moyenne pondérée des points d'origine compatibles avec le point bruité. On s'en sert à la place d'un réseau entraîné.

```python
import numpy as np
import matplotlib.pyplot as plt
rng = np.random.default_rng(0)
a = rng.uniform(0.5, 3.5 * np.pi, 300)
data = np.c_[a * np.cos(a), a * np.sin(a)] / 6                 # 300 points sur une spirale

T = 100
betas = np.linspace(1e-3, 0.1, T)
alphas = 1 - betas
abar = np.cumprod(alphas)

def eps_optimal(xt, t):
    """Le meilleur prédicteur de bruit possible pour ce jeu de données."""
    d2 = ((xt[:, None, :] - np.sqrt(abar[t]) * data[None]) ** 2).sum(-1)
    w = np.exp(-(d2 - d2.min(1, keepdims=True)) / (2 * (1 - abar[t])))
    x0 = (w / w.sum(1, keepdims=True)) @ data
    return (xt - np.sqrt(abar[t]) * x0) / np.sqrt(1 - abar[t])

x = rng.normal(size=(400, 2))                                   # on part du bruit pur
etapes = {}
for t in reversed(range(T)):
    eps = eps_optimal(x, t)
    x = (x - betas[t] / np.sqrt(1 - abar[t]) * eps) / np.sqrt(alphas[t])
    if t > 0:
        x += np.sqrt(betas[t]) * rng.normal(size=x.shape)
    if t in (99, 60, 30, 0):
        etapes[t] = x.copy()

fig, ax = plt.subplots(1, 4, figsize=(12, 3))
for k, (t, pts) in enumerate(etapes.items()):
    ax[k].scatter(*data.T, s=3, c="lightgray"); ax[k].scatter(*pts.T, s=4)
    ax[k].set_title(f"t = {t}"); ax[k].set_xlim(-2.2, 2.2); ax[k].set_ylim(-2.2, 2.2); ax[k].set_xticks([]); ax[k].set_yticks([])
plt.tight_layout(); plt.show()
```

Un vrai modèle n'a pas le jeu de données en mémoire : il **généralise** à partir de ce qu'il a vu, ce qui lui permet de produire des images nouvelles.

## Stable Diffusion : trois idées de plus

1. **Diffusion latente** : débruiter une image 1024 × 1024 pixel par pixel coûte trop cher. Un autoencodeur (VAE) compresse l'image en un petit tableau, environ 48 fois plus petit, et la diffusion travaille là.
2. **Conditionnement par le texte** : le prompt passe dans l'encodeur de texte de CLIP, et le U-Net le lit par **attention croisée**.
3. **Guidage sans classifieur** (*classifier-free guidance*) : on prédit le bruit avec et sans le prompt, et on exagère la différence. Le poids w (souvent 5 à 8) règle la fidélité au prompt au détriment de la diversité.

```latex
\hat\varepsilon = \varepsilon_\theta(x_t, \varnothing) + w\,\big(\varepsilon_\theta(x_t, \text{prompt}) - \varepsilon_\theta(x_t, \varnothing)\big)
```

```pycode
from diffusers import StableDiffusionPipeline
import torch
pipe = StableDiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-2-1-base", torch_dtype=torch.float16).to("cuda")
image = pipe("un chat astronaute, aquarelle", num_inference_steps=30, guidance_scale=7.5).images[0]
image.save("chat.png")
```

> **À retenir** : vers l'avant, on bruite avec une formule fermée ; le réseau apprend à prédire le bruit ; vers l'arrière, on part du bruit et on débruite pas à pas. Stable Diffusion = diffusion dans un espace latent + texte via CLIP et attention croisée + guidage.
''',
"exercises": [
 E("e-diff-a", "Le programme de bruit",
   "Écris `programme_bruit(T, beta_min=1e-4, beta_max=0.02)` qui renvoie le tuple `(betas, alphas, alpha_barre)` : les T valeurs βₜ régulièrement espacées de `beta_min` à `beta_max`, αₜ = 1 − βₜ, et ᾱₜ, le produit cumulé des αₜ.",
   r'''import numpy as np

def programme_bruit(T, beta_min=1e-4, beta_max=0.02):
    pass
''',
   r'''import numpy as np

def programme_bruit(T, beta_min=1e-4, beta_max=0.02):
    betas = np.linspace(beta_min, beta_max, T)
    alphas = 1 - betas
    return betas, alphas, np.cumprod(alphas)

b, a, ab = programme_bruit(1000)
print(f"ᾱ au début : {ab[0]:.4f} · au milieu : {ab[499]:.4f} · à la fin : {ab[-1]:.6f}")
''',
   r'''import numpy as np
r = programme_bruit(1000)
assert isinstance(r, tuple) and len(r) == 3, "programme_bruit doit renvoyer (betas, alphas, alpha_barre)."
b, a, ab = r
assert len(b) == 1000 and abs(b[0] - 1e-4) < 1e-12 and abs(b[-1] - 0.02) < 1e-12, "Les betas vont de beta_min à beta_max, inclus (np.linspace)."
assert np.allclose(a, 1 - b), "alphas = 1 - betas."
assert np.allclose(ab, np.cumprod(1 - b)), "alpha_barre est le produit cumulé des alphas (np.cumprod)."
assert ab[-1] < 1e-4, "À la fin du programme, il ne reste presque plus de signal."
''',
   "np.linspace pour les betas, np.cumprod pour le produit cumulé."),
 E("e-diff-b", "Bruiter en une étape",
   "Écris `bruiter(x0, t, alpha_barre, eps)` qui renvoie xₜ = √ᾱₜ · x0 + √(1 − ᾱₜ) · eps. Puis calcule `snr`, la liste des rapports signal sur bruit ᾱₜ / (1 − ᾱₜ) aux instants 0, 250, 500 et 999 du programme fourni.",
   r'''import numpy as np
betas = np.linspace(1e-4, 0.02, 1000)
alpha_barre = np.cumprod(1 - betas)

def bruiter(x0, t, alpha_barre, eps):
    pass

snr = None
''',
   r'''import numpy as np
betas = np.linspace(1e-4, 0.02, 1000)
alpha_barre = np.cumprod(1 - betas)

def bruiter(x0, t, alpha_barre, eps):
    return np.sqrt(alpha_barre[t]) * x0 + np.sqrt(1 - alpha_barre[t]) * eps

snr = [alpha_barre[t] / (1 - alpha_barre[t]) for t in (0, 250, 500, 999)]
print([f"{s:.3g}" for s in snr])
''',
   r'''import numpy as np
rng = np.random.default_rng(0)
x0, eps = rng.normal(size=(4, 3)), rng.normal(size=(4, 3))
r = bruiter(x0, 300, alpha_barre, eps)
assert r is not None and np.allclose(r, np.sqrt(alpha_barre[300]) * x0 + np.sqrt(1 - alpha_barre[300]) * eps), "xₜ = √ᾱₜ · x0 + √(1 − ᾱₜ) · eps."
assert np.allclose(bruiter(x0, 0, alpha_barre, eps), x0, atol=0.05), "À t = 0, l'image est presque intacte."
attendu = [alpha_barre[t] / (1 - alpha_barre[t]) for t in (0, 250, 500, 999)]
assert snr is not None and np.allclose(snr, attendu), "snr = ᾱₜ / (1 − ᾱₜ) pour t = 0, 250, 500, 999."
assert snr[0] > snr[1] > snr[2] > snr[3], "Le rapport signal sur bruit doit décroître avec t."
''',
   "alpha_barre[t] est un nombre : il se multiplie directement avec le tableau x0."),
 E("e-diff-c", "Une étape de débruitage",
   "Écris `etape_inverse(xt, t, eps_pred, betas, alpha_barre, z)` qui applique une étape DDPM : moyenne = (xt − βₜ / √(1 − ᾱₜ) · eps_pred) / √αₜ, puis ajoute √βₜ · z, **sauf si t = 0**.",
   r'''import numpy as np
betas = np.linspace(1e-4, 0.02, 1000)
alpha_barre = np.cumprod(1 - betas)

def etape_inverse(xt, t, eps_pred, betas, alpha_barre, z):
    pass
''',
   r'''import numpy as np
betas = np.linspace(1e-4, 0.02, 1000)
alpha_barre = np.cumprod(1 - betas)

def etape_inverse(xt, t, eps_pred, betas, alpha_barre, z):
    alpha = 1 - betas[t]
    moyenne = (xt - betas[t] / np.sqrt(1 - alpha_barre[t]) * eps_pred) / np.sqrt(alpha)
    return moyenne if t == 0 else moyenne + np.sqrt(betas[t]) * z

rng = np.random.default_rng(0)
x = rng.normal(size=3)
print(etape_inverse(x, 500, rng.normal(size=3), betas, alpha_barre, rng.normal(size=3)))
''',
   r'''import numpy as np
rng = np.random.default_rng(4)
xt, e, z = rng.normal(size=(3, 5))
t = 400
m = (xt - betas[t] / np.sqrt(1 - alpha_barre[t]) * e) / np.sqrt(1 - betas[t])
r = etape_inverse(xt, t, e, betas, alpha_barre, z)
assert r is not None and np.allclose(r, m + np.sqrt(betas[t]) * z), "Vérifie la moyenne et l'ajout de √βₜ · z."
m0 = (xt - betas[0] / np.sqrt(1 - alpha_barre[0]) * e) / np.sqrt(1 - betas[0])
assert np.allclose(etape_inverse(xt, 0, e, betas, alpha_barre, z), m0), "À t = 0, on n'ajoute pas de bruit."
''',
   "αₜ = 1 − betas[t] ; la moyenne ne dépend pas de z."),
 E("e-diff-d", "Le guidage sans classifieur",
   "Écris `guidage(eps_cond, eps_sans, w)` qui renvoie eps_sans + w · (eps_cond − eps_sans). Puis vérifie par le calcul : avec w = 1, on retrouve `eps_cond` ; avec w = 0, `eps_sans`. Mets dans `w_typique` la valeur de guidage par défaut de Stable Diffusion citée dans la leçon.",
   r'''import numpy as np

def guidage(eps_cond, eps_sans, w):
    pass

w_typique = None
''',
   r'''import numpy as np

def guidage(eps_cond, eps_sans, w):
    return eps_sans + w * (eps_cond - eps_sans)

w_typique = 7.5
a, b = np.array([1.0, 2.0]), np.array([0.0, 1.0])
print(guidage(a, b, 1), guidage(a, b, 0), guidage(a, b, w_typique))
''',
   r'''import numpy as np
a, b = np.array([1.0, -2.0, 0.5]), np.array([0.2, 0.1, 0.0])
assert guidage(a, b, 1) is not None and np.allclose(guidage(a, b, 1), a), "Avec w = 1, on retrouve la prédiction conditionnée."
assert np.allclose(guidage(a, b, 0), b), "Avec w = 0, on retrouve la prédiction sans prompt."
assert np.allclose(guidage(a, b, 3), b + 3 * (a - b)), "eps_sans + w · (eps_cond − eps_sans)."
assert w_typique == 7.5, "La leçon cite guidance_scale=7.5 dans l'exemple diffusers."
''',
   "Une seule ligne de calcul ; w_typique se trouve dans l'exemple de code diffusers."),
]},
]

MINIGPT = r'''import numpy as np

def softmax(x, axis=-1):
    x = x - x.max(axis=axis, keepdims=True)
    e = np.exp(x)
    return e / e.sum(axis=axis, keepdims=True)

def layer_norm(x, g, b, eps=1e-5):
    m = x.mean(axis=-1, keepdims=True)
    v = x.var(axis=-1, keepdims=True)
    return g * (x - m) / np.sqrt(v + eps) + b

def gelu(x):
    return 0.5 * x * (1 + np.tanh(np.sqrt(2 / np.pi) * (x + 0.044715 * x ** 3)))
'''

MINIGPT_CLASSE = r'''
class MiniGPT:
    def __init__(self, vocab, d=32, h=4, n_couches=2, n_ctx=64, graine=0):
        rng = np.random.default_rng(graine)
        N = lambda *forme: rng.normal(0, 0.3, forme)
        self.h, self.n_ctx = h, n_ctx
        self.wte, self.wpe = N(vocab, d), N(n_ctx, d)
        self.blocs = [dict(g1=np.ones(d), b1=np.zeros(d), Wqkv=N(d, 3 * d), Wo=N(d, d),
                           g2=np.ones(d), b2=np.zeros(d), W1=N(d, 4 * d), c1=np.zeros(4 * d),
                           W2=N(4 * d, d), c2=np.zeros(d)) for _ in range(n_couches)]
        self.gf, self.bf = np.ones(d), np.zeros(d)

    def _attention(self, x, B):
        n, d = x.shape
        h, dk = self.h, d // self.h
        q, k, v = np.split(x @ B["Wqkv"], 3, axis=-1)
        q, k, v = (m.reshape(n, h, dk).transpose(1, 0, 2) for m in (q, k, v))
        s = q @ k.transpose(0, 2, 1) / np.sqrt(dk)
        s = np.where(np.tril(np.ones((n, n), dtype=bool)), s, -1e9)
        z = (softmax(s) @ v).transpose(1, 0, 2).reshape(n, d)
        return z @ B["Wo"]

    def forward(self, ids):
        ids = np.asarray(ids)
        x = self.wte[ids] + self.wpe[np.arange(len(ids))]
        for B in self.blocs:
            x = x + self._attention(layer_norm(x, B["g1"], B["b1"]), B)
            x = x + gelu(layer_norm(x, B["g2"], B["b2"]) @ B["W1"] + B["c1"]) @ B["W2"] + B["c2"]
        return layer_norm(x, self.gf, self.bf) @ self.wte.T
'''

PROJECTS = [
{"id": "p-gen", "title": "Projet · Ton mini-GPT, de l'embedding au cache KV", "minutes": 180,
"body": r'''
Tu vas assembler toutes les pièces du module dans un vrai modèle de type GPT, écrit en NumPy : embeddings de tokens et de positions, blocs Transformer avec attention multi-têtes causale, génération, puis le **cache KV** qu'utilisent tous les serveurs de LLM en production.

Le modèle n'est pas entraîné (les poids sont aléatoires) : il génère donc du charabia. Ce qui compte ici, c'est l'architecture et l'inférence. L'entraînement se fait ensuite en PyTorch, sur ton ordinateur, avec exactement la même architecture.

Les fonctions utilitaires `softmax`, `layer_norm` et `gelu` sont fournies dans chaque exercice.

## L'architecture à coder

```pycode
x = wte[ids] + wpe[positions]                  # (n, d)
pour chaque bloc :
    x = x + Attention_causale(LN1(x))          # multi-têtes, W_QKV : (d, 3d), W_O : (d, d)
    x = x + W2 · gelu(W1 · LN2(x) + c1) + c2   # FFN d → 4d → d
logits = LN_finale(x) @ wte.T                  # poids partagés avec l'embedding : (n, vocab)
```
''',
"exercises": [
 E("e-pgen-a", "La classe MiniGPT",
   "Écris une classe `MiniGPT(vocab, d=32, h=4, n_couches=2, n_ctx=64, graine=0)`. Le constructeur crée les poids avec `np.random.default_rng(graine).normal(0, 0.3, forme)` : `wte` (vocab, d), `wpe` (n_ctx, d), puis pour chaque couche un dictionnaire avec deux LayerNorm, `Wqkv` (d, 3d), `Wo` (d, d), `W1` (d, 4d), `W2` (4d, d) et leurs biais, et une LayerNorm finale. La méthode `forward(ids)` renvoie les logits (n, vocab) en suivant l'architecture du projet, avec un **masque causal** dans chaque tête.",
   MINIGPT + "\nclass MiniGPT:\n    pass\n",
   MINIGPT + MINIGPT_CLASSE + r'''
m = MiniGPT(vocab=20, d=16, h=4, n_couches=2, n_ctx=12)
logits = m.forward([1, 5, 3, 7])
print(logits.shape)
print("prochain token le plus probable :", logits[-1].argmax())
''',
   r'''import numpy as np
m = MiniGPT(vocab=20, d=16, h=4, n_couches=2, n_ctx=12)
L = m.forward([1, 5, 3, 7, 2])
assert L.shape == (5, 20), f"forward doit renvoyer (n, vocab) = (5, 20) ; tu as {L.shape}."
assert np.isfinite(L).all(), "Les logits doivent être finis."
assert np.allclose(m.forward([1, 5, 3, 7, 9])[:4], L[:4]), "Changer le dernier token ne doit pas modifier les logits des positions précédentes : vérifie le masque causal."
assert not np.allclose(m.forward([4, 5, 3, 7, 2])[-1], L[-1]), "La dernière position doit dépendre des tokens précédents : l'attention doit mélanger le contexte."
assert not np.allclose(m.forward([2, 2])[1], m.forward([2])[0]), "Le même token à deux positions différentes doit donner des logits différents : ajoute wpe."
m2 = MiniGPT(vocab=20, d=16, h=4, n_couches=0, n_ctx=12)
assert m2.forward([3]).shape == (1, 20), "Avec 0 couche, le modèle doit quand même fonctionner (embeddings, LayerNorm finale, projection)."
assert not np.allclose(MiniGPT(20, 16, 4, 2, 12, graine=1).forward([1, 2])[-1], m.forward([1, 2])[-1]), "La graine doit changer les poids."
''',
   "Écris une méthode _attention(x, B) : np.split(x @ B['Wqkv'], 3, axis=-1) donne q, k, v ; reshape(n, h, dk).transpose(1, 0, 2) pour les têtes. La projection de sortie réutilise wte.T."),
 E("e-pgen-b", "Générer, token par token",
   "Écris `generer(modele, ids, n_nouveaux, temperature=1.0, graine=0)` : à chaque étape, appelle `modele.forward` sur les `modele.n_ctx` derniers tokens au plus, prends les logits de la dernière position, et choisis le token suivant. Si `temperature == 0`, prends l'argmax ; sinon, tire selon softmax(logits / temperature) avec `np.random.default_rng(graine)` créé une seule fois. Renvoie la liste complète (contexte + nouveaux tokens). La classe `MiniGPT` est fournie.",
   MINIGPT + MINIGPT_CLASSE + r'''
def generer(modele, ids, n_nouveaux, temperature=1.0, graine=0):
    pass
''',
   MINIGPT + MINIGPT_CLASSE + r'''
def generer(modele, ids, n_nouveaux, temperature=1.0, graine=0):
    rng = np.random.default_rng(graine)
    ids = list(ids)
    for _ in range(n_nouveaux):
        logits = modele.forward(ids[-modele.n_ctx:])[-1]
        if temperature == 0:
            suivant = int(logits.argmax())
        else:
            suivant = int(rng.choice(len(logits), p=softmax(logits / temperature)))
        ids.append(suivant)
    return ids

alphabet = list("abcdefghijklmnopqrstuvwxyz ")
m = MiniGPT(vocab=len(alphabet), d=32, h=4, n_couches=2, n_ctx=16)
debut = [alphabet.index(c) for c in "bonjour"]
print("".join(alphabet[i] for i in generer(m, debut, 30, temperature=0.8)))
''',
   r'''import numpy as np
m = MiniGPT(vocab=15, d=16, h=2, n_couches=1, n_ctx=8)
r = generer(m, [1, 2, 3], 12, temperature=0)
assert isinstance(r, list) and len(r) == 15 and r[:3] == [1, 2, 3], "generer renvoie le contexte suivi des n_nouveaux tokens, dans une liste."
ref = [1, 2, 3]
for _ in range(12):
    ref.append(int(m.forward(ref[-8:])[-1].argmax()))
assert r == ref, "Avec temperature=0, chaque token est l'argmax des logits de la dernière position, calculés sur les n_ctx derniers tokens."
a, b = generer(m, [1], 20, 1.0, graine=3), generer(m, [1], 20, 1.0, graine=3)
assert a == b, "À graine égale, la génération doit être identique : crée le générateur une seule fois, avant la boucle."
assert all(0 <= t < 15 for t in a), "Les tokens générés doivent être des indices du vocabulaire."
assert len(set(generer(m, [1], 40, 5.0, graine=1))) > 3, "Avec une température élevée, la génération doit varier."
''',
   "rng.choice(len(logits), p=softmax(logits / temperature)) tire un indice selon les probabilités."),
 E("e-pgen-c", "Le cache KV",
   "Ajoute à une sous-classe `MiniGPTCache(MiniGPT)` une méthode `pas(id_token, cache)` qui traite **un seul** nouveau token. `cache` vaut `None` au départ, puis contient ce que tu veux (par exemple, pour chaque couche, les clés et valeurs déjà calculées). La méthode renvoie `(logits, cache)` où `logits` (vocab,) sont ceux du nouveau token. Les logits doivent être **identiques** à `forward(tous_les_ids)[-1]`, mais sans recalculer les tokens précédents.",
   MINIGPT + MINIGPT_CLASSE + r'''
class MiniGPTCache(MiniGPT):
    def pas(self, id_token, cache):
        pass
''',
   MINIGPT + MINIGPT_CLASSE + r'''
class MiniGPTCache(MiniGPT):
    def pas(self, id_token, cache):
        if cache is None:
            cache = {"n": 0, "kv": [None] * len(self.blocs)}
        pos = cache["n"]
        x = self.wte[id_token] + self.wpe[pos]                  # (d,)
        d = x.shape[0]; h, dk = self.h, d // self.h
        for i, B in enumerate(self.blocs):
            q, k, v = np.split(layer_norm(x, B["g1"], B["b1"]) @ B["Wqkv"], 3)
            q, k, v = (m.reshape(h, 1, dk) for m in (q, k, v))
            if cache["kv"][i] is not None:
                K0, V0 = cache["kv"][i]
                k, v = np.concatenate([K0, k], axis=1), np.concatenate([V0, v], axis=1)
            cache["kv"][i] = (k, v)
            z = softmax(q @ k.transpose(0, 2, 1) / np.sqrt(dk)) @ v   # (h, 1, dk) : le nouveau token voit tout le passé
            x = x + z.reshape(d) @ B["Wo"]
            x = x + gelu(layer_norm(x, B["g2"], B["b2"]) @ B["W1"] + B["c1"]) @ B["W2"] + B["c2"]
        cache["n"] = pos + 1
        return layer_norm(x, self.gf, self.bf) @ self.wte.T, cache

m = MiniGPTCache(vocab=20, d=16, h=4, n_couches=2, n_ctx=12)
ids, cache = [3, 1, 4, 1, 5], None
for t in ids:
    logits, cache = m.pas(t, cache)
print(np.allclose(logits, m.forward(ids)[-1]))
''',
   r'''import numpy as np
m = MiniGPTCache(vocab=20, d=16, h=4, n_couches=2, n_ctx=12)
ids, cache = [3, 1, 4, 1, 5, 9, 2], None
for i, t in enumerate(ids):
    r = m.pas(t, cache)
    assert isinstance(r, tuple) and len(r) == 2, "pas doit renvoyer le tuple (logits, cache)."
    logits, cache = r
    assert np.shape(logits) == (20,), f"Les logits d'un seul token ont la forme (vocab,) = (20,) ; tu as {np.shape(logits)}."
    assert np.allclose(logits, m.forward(ids[:i + 1])[-1], atol=1e-8), f"Au token {i}, les logits avec cache diffèrent de forward(ids[:{i + 1}])[-1]."
appels = []
m2 = MiniGPTCache(vocab=20, d=16, h=4, n_couches=2, n_ctx=12)
m2.forward = lambda *a: appels.append(1)
c = None
for t in [1, 2, 3]:
    _, c = m2.pas(t, c)
assert not appels, "pas ne doit pas appeler forward sur toute la séquence : c'est tout l'intérêt du cache."
''',
   "Dans pas, x est un seul vecteur (d,). Pour chaque couche, calcule q, k, v du nouveau token, concatène k et v à ceux du cache (axe des positions), et fais l'attention de q sur toutes les clés : pas besoin de masque, le passé est entièrement visible."),
],
"tasks": [
  "Suivre la vidéo « Let's build GPT » d'Andrej Karpathy et entraîner nanoGPT sur un corpus français (Molière, Hugo) avec PyTorch",
  "Réécrire ton MiniGPT en PyTorch (nn.Module) et vérifier qu'il donne les mêmes logits que ta version NumPy avec les mêmes poids",
  "Mesurer le temps de génération de 200 tokens avec et sans cache KV, et tracer le résultat",
  "Publier le projet sur GitHub avec un schéma de l'architecture dans le README",
]},
]

QUIZZES = {
"quiz-transfo": {"title": "Quiz · Transformers, CLIP et diffusion", "questions": [
 {"q": "Dans l'attention, que contient la matrice QKᵀ ?", "options": ["Les valeurs à mélanger", "Les scores de compatibilité entre chaque requête et chaque clé", "Les embeddings de position", "Les probabilités du token suivant"], "answer": 1,
  "explain": "QKᵀ donne un score par paire (requête, clé) ; le softmax en fait des poids qui mélangent V."},
 {"q": "Pourquoi divise-t-on les scores par √d_k ?", "options": ["Pour accélérer le calcul", "Pour éviter que des scores trop grands saturent le softmax", "Pour normaliser les valeurs V", "Pour masquer le futur"], "answer": 1,
  "explain": "La variance du produit scalaire croît avec d_k ; sans correction, le softmax devient presque un argmax et les gradients s'effondrent."},
 {"q": "À quoi sert le masque causal ?", "options": ["À ignorer le padding", "À empêcher un token de voir les tokens suivants", "À réduire le nombre de têtes", "À accélérer l'entraînement"], "answer": 1,
  "explain": "Un modèle génératif prédit le token suivant : il ne doit pas le voir pendant l'entraînement."},
 {"q": "Pourquoi faut-il un encodage de position ?", "options": ["L'attention ne tient pas compte de l'ordre des tokens", "Pour réduire la taille du vocabulaire", "Pour remplacer la LayerNorm", "Pour le cache KV"], "answer": 0,
  "explain": "Sans position, « le chien mord l'homme » et « l'homme mord le chien » auraient les mêmes représentations."},
 {"q": "Quel modèle choisir pour classer des tickets de support (pas de génération) ?", "options": ["Un décodeur seul comme GPT", "Un encodeur seul comme CamemBERT", "Un modèle de diffusion", "CLIP"], "answer": 1,
  "explain": "Un encodeur voit toute la phrase dans les deux sens : idéal pour classer ou extraire. Plus petit et moins cher qu'un LLM."},
 {"q": "Que garde en mémoire le cache KV ?", "options": ["Les logits des tokens précédents", "Les clés et valeurs déjà calculées des tokens précédents", "Les poids du modèle", "Les gradients"], "answer": 1,
  "explain": "Le passé ne change pas grâce au masque causal : inutile de recalculer ses clés et valeurs à chaque nouveau token."},
 {"q": "Dans la perte de CLIP, où sont les « bonnes réponses » de la matrice de similarités ?", "options": ["Sur la première ligne", "Sur la diagonale", "Partout", "Sur la dernière colonne"], "answer": 1,
  "explain": "L'image i va avec la légende i : la perte pousse la diagonale vers le haut et le reste vers le bas."},
 {"q": "Comment CLIP classe-t-il en zero-shot ?", "options": ["Il est réentraîné sur chaque classe", "Il compare l'image aux embeddings de phrases comme « une photo de {classe} »", "Il génère une légende puis la lit", "Il utilise un arbre de décision"], "answer": 1,
  "explain": "La classe prédite est celle dont la phrase est la plus proche de l'image dans l'espace commun."},
 {"q": "Que prédit le réseau d'un modèle de diffusion pendant l'entraînement ?", "options": ["L'image finale directement", "Le bruit ε ajouté à l'image", "La légende de l'image", "Le pas de temps t"], "answer": 1,
  "explain": "On bruite x₀ avec ε connu à un instant t, et le réseau doit retrouver ε : une simple erreur quadratique."},
 {"q": "Pourquoi Stable Diffusion travaille-t-il dans un espace latent ?", "options": ["Pour avoir de meilleures couleurs", "Parce que débruiter directement les pixels coûte beaucoup trop cher", "Pour se passer de texte", "Pour éviter le surapprentissage"], "answer": 1,
  "explain": "Un VAE compresse l'image en un petit tableau ; la diffusion y est des dizaines de fois moins coûteuse."},
]},
}
