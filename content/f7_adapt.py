"""FullStack · Adaptation et évaluation (vague 5) : transfert, fine-tuning, LoRA et QLoRA, apprentissage par renforcement, RLHF et DPO."""

def E(id, title, prompt, starter, solution, check, hint):
    return {"id": id, "title": title, "prompt": prompt, "starter": starter, "solution": solution, "check": check, "hint": hint}

LESSONS = [
# ================================================================ Fine-tuning et LoRA
{"id": "l-ft", "title": "Transfert, fine-tuning, LoRA et QLoRA", "minutes": 110,
"body": r'''
Entraîner un LLM de zéro coûte des millions d'euros. Presque personne ne le fait. Le vrai métier, c'est d'**adapter** un modèle existant à un besoin précis : un ton, un format de sortie, un vocabulaire métier, une tâche de classification. Cette leçon couvre les techniques, de la plus simple à la plus économe.

## L'apprentissage par transfert

Un modèle pré-entraîné a déjà appris des représentations générales : la grammaire, les faits, la structure des images. On les **réutilise** :

- **Extraction de caractéristiques** : on gèle tout le modèle, on récupère ses embeddings, et on entraîne un petit classifieur dessus (une régression logistique suffit souvent).
- **Fine-tuning complet** : on continue l'entraînement de tous les poids sur ses données, avec un petit taux d'apprentissage (de l'ordre de 2e-5) pour ne pas effacer ce qui est acquis.
- **Fine-tuning partiel** : on gèle les premières couches (générales) et on entraîne les dernières (spécialisées).

## Avant de fine-tuner : la bonne question

| Besoin | Meilleure approche |
| --- | --- |
| Le modèle doit connaître **tes documents** | RAG, pas de fine-tuning : les connaissances changent, et on veut citer les sources |
| Le modèle doit suivre **un format ou un ton** précis | Prompt avec exemples d'abord ; fine-tuning si ça ne suffit pas ou coûte trop de tokens |
| Une tâche **étroite et répétée** à grande échelle | Fine-tuning d'un petit modèle : moins cher et plus rapide qu'un grand modèle avec un long prompt |
| Changer le **comportement** (refus, sécurité) | Alignement par préférences (leçon RLHF et DPO) |

## Le problème de la mémoire

Fine-tuner tous les poids avec l'optimiseur Adam demande, par paramètre : le poids, son gradient, et deux moyennes d'Adam. En 32 bits, cela fait environ **16 octets par paramètre**, sans compter les activations.

```python
for nom, n in [("Llama 3 8B", 8e9), ("Mistral 7B", 7.2e9), ("Llama 3 70B", 70e9)]:
    print(f"{nom:12s} : {n * 16 / 1e9:6.0f} Go pour un fine-tuning complet (une carte H100 a 80 Go)")
```

## LoRA : n'apprendre qu'une petite correction

L'idée de **LoRA** (*Low-Rank Adaptation*, Microsoft, 2021) : la modification utile d'une grande matrice W est « simple », c'est-à-dire de **petit rang**. On gèle W et on apprend deux matrices fines A et B :

```latex
W' = W + \frac{\alpha}{r}\, A B \qquad W : (d, k) \quad A : (d, r) \quad B : (r, k) \quad r \ll d
```

- A est initialisée au hasard et B à **zéro** : au départ, W' = W, le modèle n'est pas abîmé.
- Seuls A et B sont entraînés : r(d + k) paramètres au lieu de d × k.
- α / r règle l'intensité de la correction.
- Après l'entraînement, on peut **fusionner** AB dans W : aucun coût à l'inférence. Ou garder plusieurs adaptateurs et les échanger à chaud.

```viz lora
```

```pycode
from peft import LoraConfig, get_peft_model
config = LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj", "v_proj"], lora_dropout=0.05, task_type="CAUSAL_LM")
modele = get_peft_model(modele, config)
modele.print_trainable_parameters()   # avec Llama 3 8B : trainable params: 6,815,744 || all params: 8,037,076,992 || trainable%: 0.0848
```

## QLoRA : quantifier le modèle de base

**QLoRA** (2023) va plus loin : le modèle gelé est stocké sur **4 bits** par poids au lieu de 16, et seuls les adaptateurs LoRA restent en haute précision. On fine-tune ainsi un modèle de 7 à 8 milliards de paramètres sur un seul GPU grand public.

La **quantification** remplace des nombres à virgule par de petits entiers et un facteur d'échelle. La version la plus simple, *absmax* sur 8 bits :

```latex
s = \frac{\max |w|}{127} \qquad q = \mathrm{round}(w / s) \in [-127, 127] \qquad \hat w = q \cdot s
```

Le piège : une seule valeur aberrante gonfle l'échelle s, et tous les autres poids perdent en précision. D'où la quantification **par blocs** (une échelle tous les 64 poids) utilisée par QLoRA, et le format NF4, adapté à la distribution normale des poids.

```pycode
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
import torch
bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16)
modele = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.3", quantization_config=bnb, device_map="auto")
```

> **À retenir** : RAG pour les connaissances, fine-tuning pour le format et le comportement. Fine-tuning complet ≈ 16 octets par paramètre. LoRA : W gelée + (α / r) AB, B initialisée à zéro, fusion possible. QLoRA : base sur 4 bits + LoRA.
''',
"tasks": [
  "Ouvrir un notebook Colab avec un GPU T4 et installer transformers, peft, bitsandbytes et trl",
  "Fine-tuner un petit modèle (Qwen2.5-0.5B ou SmolLM) avec LoRA sur 1 000 exemples instruction → réponse en français",
  "Comparer les réponses avant et après sur 10 questions, et noter le temps et la mémoire utilisés",
  "Refaire l'entraînement en QLoRA 4 bits sur un modèle de 7B et comparer la mémoire",
],
"exercises": [
 E("e-ft-a", "Une couche LoRA",
   "Écris une classe `LoRALineaire(W, r=8, alpha=16, graine=0)`. Elle garde `W` (d, k) gelée, crée `A` (d, r) avec `np.random.default_rng(graine).normal(0, 0.01, (d, r))` et `B` (r, k) remplie de zéros. Méthodes : `forward(x)` = x @ W + (alpha / r) · x @ A @ B ; `n_entrainables()` = nombre de paramètres de A et B ; `fusionner()` renvoie la matrice W + (alpha / r) · A @ B.",
   r'''import numpy as np

class LoRALineaire:
    pass
''',
   r'''import numpy as np

class LoRALineaire:
    def __init__(self, W, r=8, alpha=16, graine=0):
        d, k = W.shape
        self.W, self.r, self.alpha = W, r, alpha
        self.A = np.random.default_rng(graine).normal(0, 0.01, (d, r))
        self.B = np.zeros((r, k))

    def forward(self, x):
        return x @ self.W + (self.alpha / self.r) * (x @ self.A @ self.B)

    def n_entrainables(self):
        return self.A.size + self.B.size

    def fusionner(self):
        return self.W + (self.alpha / self.r) * self.A @ self.B

W = np.random.default_rng(1).normal(size=(512, 512))
couche = LoRALineaire(W, r=8)
print(f"{couche.n_entrainables()} paramètres entraînables au lieu de {W.size} ({couche.n_entrainables() / W.size:.1%})")
''',
   r'''import numpy as np
rng = np.random.default_rng(0)
W = rng.normal(size=(64, 32)); x = rng.normal(size=(5, 64))
c = LoRALineaire(W, r=4, alpha=8)
assert c.A.shape == (64, 4) and c.B.shape == (4, 32), "A doit être (d, r) et B (r, k)."
assert np.allclose(c.B, 0), "B doit être initialisée à zéro."
assert np.allclose(c.forward(x), x @ W), "Au départ, la couche LoRA doit donner exactement x @ W."
assert c.n_entrainables() == 4 * (64 + 32), "n_entrainables = r × (d + k)."
c.B = rng.normal(size=(4, 32))
assert np.allclose(c.fusionner(), W + 2 * c.A @ c.B), "fusionner = W + (alpha / r) · A @ B."
assert np.allclose(c.forward(x), x @ c.fusionner()), "Après fusion, x @ W_fusionnée doit donner la même sortie que forward."
''',
   "Range W, A, B, r et alpha dans self. A.size + B.size compte les paramètres."),
 E("e-ft-b", "Quantifier sur 8 bits",
   "Écris `quantifier(w)` qui renvoie `(q, echelle)` avec echelle = max|w| / 127 et q = round(w / echelle) converti en `np.int8`, puis `dequantifier(q, echelle)`. Calcule ensuite `err_normale` et `err_aberrante`, l'erreur absolue moyenne après quantification puis déquantification des tableaux `w` et `w_aberrant` fournis.",
   r'''import numpy as np
w = np.random.default_rng(0).normal(0, 0.02, 4096)
w_aberrant = w.copy(); w_aberrant[100] = 1.5          # un seul poids aberrant

def quantifier(w):
    pass

def dequantifier(q, echelle):
    pass

err_normale = None
err_aberrante = None
''',
   r'''import numpy as np
w = np.random.default_rng(0).normal(0, 0.02, 4096)
w_aberrant = w.copy(); w_aberrant[100] = 1.5

def quantifier(w):
    echelle = np.abs(w).max() / 127
    return np.round(w / echelle).astype(np.int8), echelle

def dequantifier(q, echelle):
    return q.astype(float) * echelle

err_normale = np.abs(dequantifier(*quantifier(w)) - w).mean()
err_aberrante = np.abs(dequantifier(*quantifier(w_aberrant)) - w_aberrant).mean()
print(f"erreur moyenne : {err_normale:.2e} sans aberrant, {err_aberrante:.2e} avec un seul aberrant")
''',
   r'''import numpy as np
r = quantifier(w)
assert isinstance(r, tuple) and len(r) == 2, "quantifier doit renvoyer (q, echelle)."
q, s = r
assert q.dtype == np.int8, "q doit être de type np.int8."
assert abs(s - np.abs(w).max() / 127) < 1e-15, "echelle = max|w| / 127."
assert np.abs(q).max() == 127, "La plus grande valeur absolue doit être codée par 127."
assert np.abs(dequantifier(q, s) - w).max() <= s / 2 + 1e-12, "L'erreur de chaque poids ne doit pas dépasser la moitié de l'échelle."
assert err_normale is not None and abs(err_normale - np.abs(np.round(w / s) * s - w).mean()) < 1e-12, "err_normale est l'erreur absolue moyenne sur w."
assert err_aberrante > 10 * err_normale, "Avec un aberrant, l'échelle explose et l'erreur moyenne aussi : recalcule err_aberrante sur w_aberrant."
''',
   "np.round(w / echelle).astype(np.int8) ; pour déquantifier, q.astype(float) * echelle."),
 E("e-ft-c", "Estimer la mémoire nécessaire",
   "Écris `memoire_go(n_params, n_entrainables, octets_base)` : les paramètres gelés coûtent `octets_base` octets chacun ; chaque paramètre entraînable coûte 16 octets (poids, gradient et deux états d'Adam en 32 bits). Renvoie le total en Go (1 Go = 1e9 octets), sans compter les activations. Calcule ensuite, pour un modèle de 7e9 paramètres : `complet` (tout est entraînable), `lora` (4e7 paramètres entraînables, base en 16 bits, soit 2 octets) et `qlora` (même chose, base sur 4 bits, soit 0,5 octet).",
   r'''def memoire_go(n_params, n_entrainables, octets_base):
    pass

complet = None
lora = None
qlora = None
''',
   r'''def memoire_go(n_params, n_entrainables, octets_base):
    return ((n_params - n_entrainables) * octets_base + n_entrainables * 16) / 1e9

complet = memoire_go(7e9, 7e9, 2)
lora = memoire_go(7e9, 4e7, 2)
qlora = memoire_go(7e9, 4e7, 0.5)
print(f"complet : {complet:.0f} Go · LoRA : {lora:.1f} Go · QLoRA : {qlora:.1f} Go")
''',
   r'''assert memoire_go(1e9, 0, 2) == 2.0, "Un modèle de 1e9 paramètres entièrement gelé en 16 bits pèse 2 Go."
assert abs(complet - 112) < 1e-9, f"Fine-tuning complet de 7e9 paramètres : 7e9 × 16 octets = 112 Go ; tu as {complet}."
assert abs(lora - 14.56) < 1e-9, f"LoRA : (7e9 − 4e7) × 2 + 4e7 × 16 octets = 14,56 Go ; tu as {lora}."
assert abs(qlora - 4.12) < 1e-9, f"QLoRA : (7e9 − 4e7) × 0,5 + 4e7 × 16 octets = 4,12 Go ; tu as {qlora}."
''',
   "Les paramètres gelés sont n_params − n_entrainables."),
]},
# ================================================================ RL
{"id": "l-rl", "title": "L'apprentissage par renforcement appliqué", "minutes": 110,
"body": r'''
En apprentissage supervisé, on montre la bonne réponse. En **apprentissage par renforcement** (*reinforcement learning*, RL), personne ne la connaît : un **agent** agit dans un **environnement**, reçoit des **récompenses**, et doit découvrir seul la stratégie qui en rapporte le plus. C'est ainsi qu'AlphaGo a battu les meilleurs joueurs de go, et c'est la dernière étape de l'entraînement de ChatGPT, de Claude et des modèles de raisonnement.

## Le vocabulaire

À chaque instant t, l'agent observe un **état** sₜ, choisit une **action** aₜ selon sa **politique** π, reçoit une **récompense** rₜ et arrive dans l'état sₜ₊₁. Son but : maximiser le **rendement**, la somme des récompenses futures, actualisées par un facteur γ < 1 (une récompense lointaine vaut un peu moins qu'une immédiate) :

```latex
G_t = r_t + \gamma\, r_{t+1} + \gamma^2 r_{t+2} + \dots = r_t + \gamma\, G_{t+1}
```

## Explorer ou exploiter : le bandit manchot

Le problème le plus simple : plusieurs machines à sous, chacune avec une probabilité de gain inconnue. Jouer toujours celle qui a le mieux marché jusqu'ici (**exploiter**) risque de passer à côté d'une meilleure. En essayer d'autres (**explorer**) coûte des parties. La stratégie **ε-gloutonne** explore au hasard avec une probabilité ε, et exploite sinon. C'est exactement le dilemme d'un test A/B ou d'un système de recommandation.

```python
import numpy as np
rng = np.random.default_rng(0)
vraies = np.array([0.3, 0.5, 0.7])
for eps in [0.0, 0.1, 0.5]:
    Q, N, gains = np.zeros(3), np.zeros(3), 0
    for _ in range(2000):
        a = rng.integers(3) if rng.random() < eps else int(Q.argmax())
        r = float(rng.random() < vraies[a])
        N[a] += 1; Q[a] += (r - Q[a]) / N[a]; gains += r
    print(f"ε = {eps:.1f} : gains {gains:5.0f} / 2000, estimations {Q.round(2)}")
```

Sans exploration (ε = 0), l'agent peut rester bloqué sur une machine médiocre. Trop d'exploration gaspille des parties.

## Le Q-learning

Quand les actions changent l'état, il faut planifier. Le **Q-learning** apprend Q(s, a), la valeur d'une action dans un état, en corrigeant son estimation après chaque pas :

```latex
Q(s, a) \leftarrow Q(s, a) + \alpha \Big[\, r + \gamma \max_{a'} Q(s', a') - Q(s, a) \Big]
```

Le terme entre crochets est l'**erreur de différence temporelle** : l'écart entre ce qu'on espérait et ce qu'on observe maintenant (récompense immédiate + meilleure valeur estimée de la suite). La politique finale consiste à choisir, dans chaque état, l'action de plus grande valeur.

```viz qlearn
```

## Quand il y a trop d'états : les politiques neuronales

Aux échecs ou pour un LLM, impossible de tenir un tableau Q. On utilise un réseau de neurones. Deux grandes familles :

- **Méthodes de valeur** (DQN) : un réseau approxime Q(s, a). C'est ce qui a joué aux jeux Atari en 2015.
- **Méthodes de politique** (REINFORCE, PPO) : un réseau donne directement π(a | s), et on augmente la probabilité des actions qui ont mené à un bon rendement. Pour un LLM, l'état est le texte jusqu'ici, l'action est le token suivant, et la récompense arrive à la fin de la réponse. **PPO** est l'algorithme du RLHF de ChatGPT.

```pycode
import gymnasium as gym
env = gym.make("FrozenLake-v1", is_slippery=False)
etat, _ = env.reset(seed=0)
etat, recompense, termine, tronque, info = env.step(env.action_space.sample())
```

> **À retenir** : agent, état, action, récompense, politique. Rendement actualisé par γ. Exploration contre exploitation (ε-glouton). Q-learning : corriger Q(s, a) vers r + γ max Q(s', ·). Pour les LLM, la politique est le modèle lui-même.
''',
"tasks": [
  "Installer gymnasium et résoudre FrozenLake avec ton Q-learning en tableau",
  "Entraîner un agent PPO sur CartPole avec stable-baselines3 et regarder la courbe de récompense",
  "Lire le billet « Illustrating RLHF » sur le blog de Hugging Face",
],
"exercises": [
 E("e-rl-a", "Les rendements actualisés",
   "Écris `rendements(recompenses, gamma)` qui renvoie un tableau NumPy de même longueur que `recompenses`, où l'élément t vaut Gₜ = rₜ + γ · Gₜ₊₁ (et le dernier vaut la dernière récompense). Parcours la liste à l'envers.",
   r'''import numpy as np

def rendements(recompenses, gamma):
    pass
''',
   r'''import numpy as np

def rendements(recompenses, gamma):
    G = np.zeros(len(recompenses))
    suite = 0.0
    for t in reversed(range(len(recompenses))):
        suite = recompenses[t] + gamma * suite
        G[t] = suite
    return G

print(rendements([0, 0, 0, 1], 0.9))
''',
   r'''import numpy as np
r = rendements([0, 0, 0, 1], 0.9)
assert r is not None and np.allclose(r, [0.729, 0.81, 0.9, 1.0]), f"Pour [0, 0, 0, 1] et γ = 0.9, on attend [0.729, 0.81, 0.9, 1] ; tu as {r}."
rr = np.random.default_rng(0).normal(size=12)
attendu = [sum(rr[k] * 0.95 ** (k - t) for k in range(t, 12)) for t in range(12)]
assert np.allclose(rendements(rr, 0.95), attendu), "Gₜ = somme des rₖ × γ^(k − t) pour k ≥ t."
assert np.allclose(rendements([1, 1, 1], 0), [1, 1, 1]), "Avec γ = 0, le rendement est la récompense immédiate."
''',
   "Garde une variable suite = 0, et remonte de la fin : suite = r[t] + gamma * suite."),
 E("e-rl-b", "Le bandit ε-glouton",
   "Écris `epsilon_glouton(probas, n_tours, epsilon, graine=0)`. À chaque tour, avec probabilité `epsilon` choisis une machine au hasard, sinon celle dont l'estimation est la plus haute. La machine a rapporte 1 avec probabilité `probas[a]`, sinon 0. Mets à jour l'estimation par moyenne incrémentale Q[a] += (r − Q[a]) / N[a]. Utilise `rng = np.random.default_rng(graine)`. Renvoie `(Q, gains_total)`.",
   r'''import numpy as np

def epsilon_glouton(probas, n_tours, epsilon, graine=0):
    pass
''',
   r'''import numpy as np

def epsilon_glouton(probas, n_tours, epsilon, graine=0):
    rng = np.random.default_rng(graine)
    k = len(probas)
    Q, N, gains = np.zeros(k), np.zeros(k), 0.0
    for _ in range(n_tours):
        a = int(rng.integers(k)) if rng.random() < epsilon else int(Q.argmax())
        r = float(rng.random() < probas[a])
        N[a] += 1
        Q[a] += (r - Q[a]) / N[a]
        gains += r
    return Q, gains

Q, g = epsilon_glouton([0.2, 0.5, 0.75], 3000, 0.1)
print(Q.round(2), g)
''',
   r'''import numpy as np
r = epsilon_glouton([0.2, 0.5, 0.75], 3000, 0.1, graine=1)
assert isinstance(r, tuple) and len(r) == 2, "epsilon_glouton doit renvoyer (Q, gains_total)."
Q, g = r
assert len(Q) == 3 and abs(Q[2] - 0.75) < 0.05, f"L'estimation de la meilleure machine devrait être proche de 0.75 ; tu as {Q[2]:.3f}."
assert g > 0.65 * 3000, f"Avec ε = 0.1, on devrait gagner plus de 1 950 fois sur 3 000 ; tu as {g}."
_, g_hasard = epsilon_glouton([0.2, 0.5, 0.75], 3000, 1.0, graine=1)
assert g_hasard < g, "Explorer tout le temps (ε = 1) doit rapporter moins qu'ε = 0.1."
assert abs(g_hasard / 3000 - 0.483) < 0.04, "Avec ε = 1, chaque machine est choisie au hasard : gain moyen ≈ (0.2 + 0.5 + 0.75) / 3."
''',
   "rng.random() < epsilon décide d'explorer ; rng.integers(k) choisit une machine au hasard ; Q.argmax() exploite."),
 E("e-rl-c", "Le Q-learning sur un couloir",
   "L'environnement est un couloir de 6 cases (0 à 5). L'agent part de la case 0 ; l'action 0 va à gauche, l'action 1 à droite. La fonction `pas(s, a)` est fournie. Écris `q_learning(n_episodes=300, alpha=0.5, gamma=0.9, epsilon=0.2, graine=0)` qui renvoie la table Q (6, 2). Dans chaque épisode (au plus 100 pas), choisis l'action de façon ε-gloutonne (au hasard si les deux valeurs sont égales), applique `pas`, et mets à jour Q avec la cible r si l'épisode est terminé, r + γ max Q[s'] sinon.",
   r'''import numpy as np

def pas(s, a):
    s2 = max(0, min(5, s + (1 if a == 1 else -1)))
    r = 1.0 if s2 == 5 else -0.01
    return s2, r, s2 == 5

def q_learning(n_episodes=300, alpha=0.5, gamma=0.9, epsilon=0.2, graine=0):
    pass
''',
   r'''import numpy as np

def pas(s, a):
    s2 = max(0, min(5, s + (1 if a == 1 else -1)))
    r = 1.0 if s2 == 5 else -0.01
    return s2, r, s2 == 5

def q_learning(n_episodes=300, alpha=0.5, gamma=0.9, epsilon=0.2, graine=0):
    rng = np.random.default_rng(graine)
    Q = np.zeros((6, 2))
    for _ in range(n_episodes):
        s = 0
        for _ in range(100):
            if rng.random() < epsilon or Q[s, 0] == Q[s, 1]:
                a = int(rng.integers(2))
            else:
                a = int(Q[s].argmax())
            s2, r, fini = pas(s, a)
            cible = r if fini else r + gamma * Q[s2].max()
            Q[s, a] += alpha * (cible - Q[s, a])
            s = s2
            if fini:
                break
    return Q

Q = q_learning()
print(Q.round(3))
print("politique :", ["←→"[a] for a in Q[:5].argmax(axis=1)])
''',
   r'''import numpy as np
Q = q_learning()
assert Q is not None and np.shape(Q) == (6, 2), "q_learning doit renvoyer un tableau (6, 2)."
assert (Q[:5].argmax(axis=1) == 1).all(), f"Dans les cases 0 à 4, la meilleure action doit être « droite » (1) ; ta politique : {Q[:5].argmax(axis=1)}."
assert abs(Q[4, 1] - 1.0) < 0.02, f"Depuis la case 4, aller à droite termine avec r = 1 : Q[4, 1] doit valoir environ 1 ; tu as {Q[4, 1]:.3f}."
assert abs(Q[3, 1] - (-0.01 + 0.9 * 1.0)) < 0.05, f"Q[3, 1] doit valoir environ −0.01 + 0.9 × 1 = 0.89 ; tu as {Q[3, 1]:.3f}."
assert np.allclose(Q[5], 0), "La case 5 est terminale : on n'y met jamais Q à jour."
''',
   "Deux boucles : épisodes, puis pas. La cible vaut r si fini, sinon r + gamma * Q[s2].max()."),
]},
# ================================================================ RLHF et DPO
{"id": "l-dpo", "title": "RLHF et DPO : aligner un modèle", "minutes": 90,
"body": r'''
Un modèle pré-entraîné complète du texte : demande-lui une recette, il peut continuer avec trois autres questions de forum. Le transformer en assistant utile, honnête et prudent, c'est l'**alignement**. Cette étape a fait passer GPT-3 à ChatGPT.

## Les trois étapes classiques

1. **Pré-entraînement** : prédire le token suivant sur des milliers de milliards de tokens.
2. **Fine-tuning supervisé** (SFT) : quelques dizaines de milliers d'exemples instruction → bonne réponse, écrits ou validés par des humains. Le modèle apprend le format d'un assistant.
3. **Apprentissage par préférences** : on montre deux réponses à la même question, un humain choisit la meilleure. Juger est bien plus facile qu'écrire la réponse parfaite.

## Le modèle de récompense

Avec ces paires (réponse choisie, réponse rejetée), on entraîne un **modèle de récompense** r(x, y) qui donne une note à une réponse. Le modèle de **Bradley-Terry** relie les notes aux préférences :

```latex
P(y_c \succ y_r) = \sigma\big(r(x, y_c) - r(x, y_r)\big) \qquad L_{RM} = -\log \sigma\big(r(x, y_c) - r(x, y_r)\big)
```

Seul l'**écart** de notes compte : c'est le même modèle que le classement Elo des échecs.

```python
import numpy as np
sigma = lambda z: 1 / (1 + np.exp(-z))
for ecart in [0, 1, 2, 4]:
    print(f"écart de récompense {ecart} → probabilité de préférer la réponse A : {sigma(ecart):.2f}")
```

## RLHF avec PPO

Le LLM devient la **politique** d'un problème de RL : il génère une réponse, le modèle de récompense la note, et PPO pousse le LLM vers les réponses bien notées. Une **pénalité KL** l'empêche de trop s'éloigner du modèle SFT de référence. Sans elle, il trouve des failles du modèle de récompense (*reward hacking*) : réponses interminables, flatterie, formules creuses qui plaisent au juge.

```latex
\max_\pi\ \mathbb{E}\big[r(x, y)\big] - \beta\, \mathrm{KL}\big(\pi(\cdot \mid x)\ \Vert\ \pi_{\mathrm{ref}}(\cdot \mid x)\big)
```

C'est puissant mais lourd : quatre modèles en mémoire (politique, référence, récompense, critique) et un entraînement instable.

## DPO : se passer du RL

**DPO** (*Direct Preference Optimization*, Stanford, 2023) montre qu'on peut obtenir la même solution optimale avec une simple perte de classification sur les paires, sans modèle de récompense ni PPO. La récompense devient implicite : c'est l'écart de log-probabilité entre le modèle entraîné et la référence.

```latex
L_{DPO} = -\log \sigma\Big(\beta \big[(\log \pi(y_c) - \log \pi_{\mathrm{ref}}(y_c)) - (\log \pi(y_r) - \log \pi_{\mathrm{ref}}(y_r))\big]\Big)
```

On augmente la probabilité de la réponse choisie **par rapport à la référence**, et on baisse celle de la rejetée. β joue le rôle de la pénalité KL. La plupart des modèles ouverts (Zephyr, Llama 3, Mistral) utilisent DPO ou une variante.

```pycode
from trl import DPOTrainer, DPOConfig
# jeu de données : colonnes "prompt", "chosen", "rejected"
trainer = DPOTrainer(model=modele, ref_model=None, args=DPOConfig(beta=0.1, output_dir="dpo"), train_dataset=paires, processing_class=tok)
trainer.train()
```

## Et ensuite

- **RLAIF** et **IA constitutionnelle** (Anthropic) : les préférences sont produites par un modèle qui suit une liste de principes écrits, ce qui réduit le besoin d'annotateurs humains.
- **RL avec récompenses vérifiables** : pour les maths et le code, la récompense est simplement « la réponse est juste » ou « les tests passent ». C'est ainsi que sont entraînés les modèles de raisonnement (o1, DeepSeek-R1 avec l'algorithme GRPO).

> **À retenir** : SFT pour le format, préférences pour le comportement. Modèle de récompense de Bradley-Terry, puis PPO avec pénalité KL : c'est le RLHF. DPO obtient le même effet avec une perte directe sur les paires.
''',
"exercises": [
 E("e-dpo-a", "Le modèle de Bradley-Terry",
   "Écris `proba_preference(r_a, r_b)`, la probabilité σ(r_a − r_b) que A soit préférée à B, puis `perte_recompense(r_choisies, r_rejetees)`, la moyenne de −log σ(r_c − r_r) sur des tableaux. Pour la stabilité, utilise l'identité −log σ(z) = `np.logaddexp(0, -z)`.",
   r'''import numpy as np

def proba_preference(r_a, r_b):
    pass

def perte_recompense(r_choisies, r_rejetees):
    pass
''',
   r'''import numpy as np

def proba_preference(r_a, r_b):
    return 1 / (1 + np.exp(-(r_a - r_b)))

def perte_recompense(r_choisies, r_rejetees):
    return np.mean(np.logaddexp(0, -(np.asarray(r_choisies) - np.asarray(r_rejetees))))

print(proba_preference(2.0, 1.0), perte_recompense([2.0, 0.5], [1.0, 1.5]))
''',
   r'''import numpy as np
assert proba_preference(1.0, 1.0) is not None and abs(proba_preference(1.0, 1.0) - 0.5) < 1e-12, "Deux récompenses égales donnent une probabilité de 0.5."
assert abs(proba_preference(3.0, 1.0) - 1 / (1 + np.exp(-2))) < 1e-12, "P = σ(r_a − r_b)."
rc, rr = np.array([2.0, 0.5, -1.0]), np.array([1.0, 1.5, -3.0])
attendu = np.mean(-np.log(1 / (1 + np.exp(-(rc - rr)))))
assert abs(perte_recompense(rc, rr) - attendu) < 1e-9, f"Perte attendue {attendu:.5f}."
assert np.isfinite(perte_recompense(np.array([0.0]), np.array([1000.0]))), "Avec un très grand écart, utilise np.logaddexp pour rester fini."
''',
   "−log σ(z) = log(1 + e^(−z)) = np.logaddexp(0, -z)."),
 E("e-dpo-b", "La log-probabilité d'une réponse",
   "Écris `logprob_reponse(logits, ids)` : `logits` (n, vocab) sont les sorties du modèle aux n positions de la réponse, `ids` (n,) les tokens réellement présents. Renvoie la somme des log-probabilités de ces tokens, avec un log-softmax stable ligne par ligne.",
   r'''import numpy as np

def logprob_reponse(logits, ids):
    pass
''',
   r'''import numpy as np

def logprob_reponse(logits, ids):
    z = logits - logits.max(axis=1, keepdims=True)
    log_p = z - np.log(np.exp(z).sum(axis=1, keepdims=True))
    return float(log_p[np.arange(len(ids)), ids].sum())

logits = np.array([[2.0, 0.5, -1.0], [0.0, 3.0, 0.0]])
print(logprob_reponse(logits, np.array([0, 1])))
''',
   r'''import numpy as np
rng = np.random.default_rng(0)
L = rng.normal(size=(6, 10)); ids = rng.integers(0, 10, 6)
P = np.exp(L) / np.exp(L).sum(axis=1, keepdims=True)
attendu = np.log(P[np.arange(6), ids]).sum()
r = logprob_reponse(L, ids)
assert r is not None and abs(r - attendu) < 1e-9, f"Somme attendue {attendu:.5f}, obtenue {r}."
assert r < 0, "Une log-probabilité est négative."
assert np.isfinite(logprob_reponse(L * 1000, ids)), "Avec de grands logits, soustrais le maximum de chaque ligne."
''',
   "log-softmax = z − log(somme des exp(z)), avec z = logits − max ; puis log_p[np.arange(n), ids].sum()."),
 E("e-dpo-c", "La perte DPO",
   "Écris `perte_dpo(lp_c, lp_r, lp_ref_c, lp_ref_r, beta=0.1)` : chaque argument est un tableau de log-probabilités de réponses (choisies `c` et rejetées `r`, sous le modèle entraîné et sous la référence). Renvoie la moyenne de −log σ(β · [(lp_c − lp_ref_c) − (lp_r − lp_ref_r)]), calculée avec `np.logaddexp`.",
   r'''import numpy as np

def perte_dpo(lp_c, lp_r, lp_ref_c, lp_ref_r, beta=0.1):
    pass
''',
   r'''import numpy as np

def perte_dpo(lp_c, lp_r, lp_ref_c, lp_ref_r, beta=0.1):
    marge = beta * ((np.asarray(lp_c) - lp_ref_c) - (np.asarray(lp_r) - lp_ref_r))
    return float(np.mean(np.logaddexp(0, -marge)))

ref_c, ref_r = np.array([-12.0, -30.0]), np.array([-11.0, -28.0])
print("au départ (modèle = référence) :", perte_dpo(ref_c, ref_r, ref_c, ref_r))
print("après entraînement :", perte_dpo(ref_c + 5, ref_r - 5, ref_c, ref_r))
''',
   r'''import numpy as np
rng = np.random.default_rng(1)
c, r_, rc, rr = (rng.normal(-20, 5, 8) for _ in range(4))
m = 0.1 * ((c - rc) - (r_ - rr))
attendu = np.mean(-np.log(1 / (1 + np.exp(-m))))
res = perte_dpo(c, r_, rc, rr)
assert res is not None and abs(res - attendu) < 1e-9, f"Perte attendue {attendu:.5f}, obtenue {res}."
assert abs(perte_dpo(c, r_, c, r_) - np.log(2)) < 1e-12, "Quand le modèle est identique à la référence, la perte vaut log 2."
assert perte_dpo(rc + 3, rr - 3, rc, rr) < np.log(2), "Favoriser la réponse choisie par rapport à la référence doit faire baisser la perte."
m2 = 0.5 * ((c - rc) - (r_ - rr))
assert abs(perte_dpo(c, r_, rc, rr, beta=0.5) - np.mean(np.logaddexp(0, -m2))) < 1e-9, "beta doit multiplier la marge."
''',
   "La marge vaut beta × ((lp_c − lp_ref_c) − (lp_r − lp_ref_r)) ; la perte est np.logaddexp(0, -marge) en moyenne."),
]},
]

QUIZZES = {
"quiz-adapt": {"title": "Quiz · Fine-tuning, RL et alignement", "questions": [
 {"q": "Une entreprise veut que son assistant réponde à partir de sa documentation, qui change chaque semaine. Que choisir ?", "options": ["Un fine-tuning complet chaque semaine", "Un RAG", "LoRA", "DPO"], "answer": 1,
  "explain": "Des connaissances qui changent et qu'on veut citer : RAG. Le fine-tuning sert plutôt au format et au comportement."},
 {"q": "Pourquoi initialise-t-on la matrice B de LoRA à zéro ?", "options": ["Pour économiser de la mémoire", "Pour que le modèle adapté soit identique au modèle d'origine au départ", "Pour accélérer l'inférence", "Pour quantifier le modèle"], "answer": 1,
  "explain": "AB = 0 au départ : W' = W, on ne dégrade pas le modèle avant d'avoir appris quoi que ce soit."},
 {"q": "Combien de paramètres entraînables ajoute LoRA de rang 8 sur une matrice 4096 × 4096 ?", "options": ["16 777 216", "65 536", "32 768", "8"], "answer": 1,
  "explain": "r (d + k) = 8 × (4096 + 4096) = 65 536, soit 0,4 % de la matrice."},
 {"q": "Qu'apporte QLoRA par rapport à LoRA ?", "options": ["Un meilleur modèle de récompense", "Le modèle de base gelé est stocké sur 4 bits, ce qui divise sa mémoire par 4", "Il supprime le besoin de données", "Il remplace PPO"], "answer": 1,
  "explain": "Les adaptateurs restent en haute précision ; seul le modèle gelé est quantifié."},
 {"q": "Dans le dilemme exploration / exploitation, que se passe-t-il avec ε = 0 ?", "options": ["L'agent explore tout le temps", "L'agent peut rester bloqué sur une action médiocre qu'il croit la meilleure", "L'agent ne reçoit plus de récompense", "Rien de particulier"], "answer": 1,
  "explain": "Sans exploration, une mauvaise première estimation n'est jamais corrigée."},
 {"q": "Dans le Q-learning, vers quelle cible corrige-t-on Q(s, a) ?", "options": ["La récompense moyenne de l'épisode", "r + γ × la meilleure valeur estimée de l'état suivant", "Toujours 1", "La valeur de l'état précédent"], "answer": 1,
  "explain": "C'est l'erreur de différence temporelle : r + γ max Q(s', ·) − Q(s, a)."},
 {"q": "À quoi sert la pénalité KL dans le RLHF ?", "options": ["À accélérer l'entraînement", "À empêcher le modèle de trop s'éloigner de la référence et d'exploiter les failles du modèle de récompense", "À compter les tokens", "À quantifier le modèle"], "answer": 1,
  "explain": "Sans elle, le modèle trouve des réponses que le juge note bien mais qui ne sont pas réellement meilleures (reward hacking)."},
 {"q": "Quel est l'avantage principal de DPO sur PPO ?", "options": ["Il n'a pas besoin de paires de préférences", "Il se passe du modèle de récompense et de la boucle de RL : une simple perte sur les paires", "Il entraîne le modèle de zéro", "Il fonctionne sans GPU"], "answer": 1,
  "explain": "DPO optimise directement les préférences, plus simple et plus stable que PPO."},
]},
}
