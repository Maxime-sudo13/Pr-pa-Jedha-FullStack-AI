"""Essentials : IA générative, agents, évaluation, automatisation et RAG."""

def E(id, title, prompt, starter, solution, check, hint):
    return {"id": id, "title": title, "prompt": prompt, "starter": starter, "solution": solution, "check": check, "hint": hint}

LESSONS = [
# ================================================================ LLM 1
{"id": "l-gen-1", "title": "Le paysage de l'IA et des LLM", "minutes": 90,
"body": r'''
L'**IA générative** est le dernier étage d'un empilement de notions qu'on confond souvent :

- **Intelligence artificielle** : tout programme qui accomplit une tâche qu'on croyait réservée aux humains.
- **Machine learning** : l'IA qui *apprend* une règle à partir d'exemples au lieu qu'on l'écrive.
- **Deep learning** : le machine learning avec des réseaux de neurones à plusieurs couches.
- **IA générative** : des modèles de deep learning qui *produisent* du contenu (texte, image, son, code).

Un **LLM** (*Large Language Model*) est un modèle génératif de texte : un réseau de neurones de type Transformer, avec des milliards de paramètres, entraîné sur une énorme quantité de texte.

## Comment un LLM écrit : un token à la fois

Un LLM ne « pense » pas une phrase entière. À chaque étape, il calcule une **probabilité pour chaque token possible** (un morceau de mot), en choisit un, l'ajoute au texte, et recommence. On dit qu'il est **autorégressif**.

```viz nexttoken
```

Le modèle produit des **scores bruts** (les *logits*), transformés en probabilités par la fonction **softmax**. La **température** T contrôle à quel point la distribution est piquée :

```latex
p_i = \frac{e^{z_i / T}}{\sum_j e^{z_j / T}}
```

T proche de 0 : le modèle prend presque toujours le token le plus probable (réponses stables). T élevée : il ose des tokens moins probables (plus de variété, plus d'erreurs).

```python
import numpy as np

logits = np.array([4.0, 3.2, 2.1, 0.5])       # scores pour : "Paris", "Lyon", "Marseille", "Tokyo"
for T in [0.2, 1.0, 2.0]:
    p = np.exp(logits / T) / np.exp(logits / T).sum()
    print(f"T = {T}:", p.round(3))
```

## Comment on fabrique un assistant

1. **Pré-entraînement** : le modèle apprend à prédire le token suivant sur des milliers de milliards de tokens. Il acquiert la langue et des connaissances, mais il ne sait pas encore « répondre ».
2. **Ajustement par instructions** (*instruction tuning*) : on l'entraîne sur des exemples de questions et de bonnes réponses.
3. **Alignement par préférences** (RLHF, DPO) : des humains, ou d'autres modèles, comparent des réponses ; le modèle apprend à préférer les meilleures. Tu verras RLHF et DPO dans le module Adaptation et évaluation du FullStack.

## Le paysage des modèles

- **Modèles propriétaires**, accessibles par API : la famille Claude d'Anthropic, GPT d'OpenAI, Gemini de Google.
- **Modèles à poids ouverts**, téléchargeables et exécutables chez soi : Llama de Meta, Mistral, Qwen, Gemma… On les trouve sur Hugging Face.
- Les modèles récents sont **multimodaux** : ils lisent des images, parfois du son et de la vidéo.

Le choix dépend de la qualité requise, du coût, de la latence, de la confidentialité des données et des contraintes de déploiement.

## Ton premier appel à un LLM

Sur cette plateforme, le module `llm` appelle un vrai modèle (Claude) depuis Python. `await` attend la réponse, comme dans Jupyter. Si aucun modèle n'est disponible sur ton appareil, une réponse simulée s'affiche.

```python
import llm
print("LLM disponible :", llm.disponible())
reponse = await llm.complete("En deux phrases, explique à un débutant ce qu'est un token.")
print(reponse)
```

> **À retenir** : un LLM prédit le token suivant à partir de probabilités. Il n'a pas accès à une base de faits : il peut produire une réponse fausse mais très bien formulée (une *hallucination*). Tout le travail d'ingénierie consiste à l'encadrer.
''',
"exercises": [
 E("e-gen-1-a", "Softmax avec température",
   "Écris `softmax(logits, temperature=1.0)` qui renvoie un tableau NumPy de probabilités (positives, de somme 1). Pour la stabilité numérique, soustrais le maximum des logits avant l'exponentielle.",
   "import numpy as np\n\ndef softmax(logits, temperature=1.0):\n    pass\n",
   "import numpy as np\n\ndef softmax(logits, temperature=1.0):\n    z = np.asarray(logits, dtype=float) / temperature\n    z = z - z.max()\n    e = np.exp(z)\n    return e / e.sum()\n\nprint(softmax([2.0, 1.0, 0.1]).round(3))\nprint(softmax([2.0, 1.0, 0.1], temperature=0.1).round(3))\n",
   r'''import numpy as np
p = softmax([2.0, 1.0, 0.1])
assert isinstance(p, np.ndarray), "softmax doit renvoyer un tableau NumPy."
assert np.isclose(p.sum(), 1) and (p > 0).all(), "Les probabilités doivent être positives et de somme 1."
assert np.allclose(p, [0.659, 0.242, 0.099], atol=1e-3), f"softmax([2, 1, 0.1]) vaut {p.round(3)}."
assert softmax([2.0, 1.0, 0.1], temperature=0.1)[0] > 0.99, "Avec une température de 0.1, le premier token doit dépasser 99 %."
assert np.isfinite(softmax([1000.0, 999.0])).all(), "Avec des logits très grands, pense à soustraire le maximum."
''',
   "Divise par la température, soustrais z.max(), applique np.exp, puis divise par la somme."),
 E("e-gen-1-b", "Un mini-modèle de langue",
   "`modele` associe à chaque mot les probabilités du mot suivant. Écris `generer(modele, debut, n)` qui part du mot `debut` et ajoute à chaque étape le mot suivant **le plus probable** (décodage glouton), `n` fois, ou s'arrête si le mot n'a pas de suite. Renvoie la phrase (mots séparés par des espaces).",
   'modele = {\n    "le": {"chat": 0.5, "chien": 0.3, "modèle": 0.2},\n    "chat": {"dort": 0.6, "mange": 0.4},\n    "dort": {"sur": 0.7, "bien": 0.3},\n    "sur": {"le": 1.0},\n    "chien": {"court": 1.0},\n}\n\ndef generer(modele, debut, n):\n    pass\n',
   'modele = {\n    "le": {"chat": 0.5, "chien": 0.3, "modèle": 0.2},\n    "chat": {"dort": 0.6, "mange": 0.4},\n    "dort": {"sur": 0.7, "bien": 0.3},\n    "sur": {"le": 1.0},\n    "chien": {"court": 1.0},\n}\n\ndef generer(modele, debut, n):\n    mots = [debut]\n    for _ in range(n):\n        suites = modele.get(mots[-1])\n        if not suites:\n            break\n        mots.append(max(suites, key=suites.get))\n    return " ".join(mots)\n\nprint(generer(modele, "le", 6))\n',
   r'''assert generer(modele, "le", 6) == "le chat dort sur le chat dort", f"generer(modele, 'le', 6) renvoie {generer(modele, 'le', 6)!r}."
assert generer(modele, "chien", 5) == "chien court", "Après « court », il n'y a plus de suite : il faut s'arrêter."
assert generer(modele, "le", 0) == "le", "Avec n = 0, on renvoie seulement le mot de départ."
''',
   "Garde une liste de mots. À chaque tour : max(suites, key=suites.get) donne le mot le plus probable."),
 E("e-gen-1-c", "Échantillonner avec top-k",
   "Le décodage glouton tourne en boucle (« le chat dort sur le chat… »). Écris `echantillonner(probas, k, rng)` qui garde les `k` tokens les plus probables (un dictionnaire token → probabilité), **renormalise** leurs probabilités pour que leur somme fasse 1, puis tire un token au hasard avec `rng.choice`.",
   "import numpy as np\n\ndef echantillonner(probas, k, rng):\n    pass\n\nrng = np.random.default_rng(0)\n",
   "import numpy as np\n\ndef echantillonner(probas, k, rng):\n    top = sorted(probas, key=probas.get, reverse=True)[:k]\n    p = np.array([probas[t] for t in top])\n    p = p / p.sum()\n    return str(rng.choice(top, p=p))\n\nrng = np.random.default_rng(0)\nprint([echantillonner({\"a\": 0.5, \"b\": 0.3, \"c\": 0.2}, 2, rng) for _ in range(10)])\n",
   r'''import numpy as np
from collections import Counter
rng = np.random.default_rng(1)
tirages = Counter(echantillonner({"a": 0.5, "b": 0.3, "c": 0.15, "d": 0.05}, 2, rng) for _ in range(4000))
assert set(tirages) <= {"a", "b"}, f"Avec k = 2, seuls a et b peuvent sortir ; tu obtiens {set(tirages)}."
assert abs(tirages["a"] / 4000 - 0.625) < 0.03, f"Après renormalisation, a devrait sortir environ 62,5 % du temps ; tu obtiens {tirages['a'] / 40:.1f} %."
assert echantillonner({"x": 0.9, "y": 0.1}, 1, rng) == "x", "Avec k = 1, c'est le décodage glouton."
''',
   "Trie les tokens par probabilité décroissante, garde les k premiers, divise leurs probabilités par leur somme, puis rng.choice(top, p=p)."),
]},
# ================================================================ LLM 2 : prompts
{"id": "l-gen-2", "title": "Le prompt comme interface", "minutes": 90,
"body": r'''
Avec un LLM, le **prompt** est l'interface de programmation. Un bon prompt ressemble au brief qu'on donnerait à un collègue brillant qui ne connaît rien au contexte.

## L'anatomie d'un bon prompt

1. **Le rôle et le contexte** : qui est le modèle, pour qui il travaille, pourquoi.
2. **La tâche**, formulée de façon précise et vérifiable.
3. **Les contraintes** : longueur, ton, ce qu'il ne faut pas faire.
4. **Le format de sortie** : liste, tableau, JSON avec des clés précises.
5. **Des exemples** (*few-shot*) quand le format ou le style est subtil.
6. **Les données**, clairement délimitées (balises `<texte>…</texte>`, triples guillemets).

Compare un prompt vague et un prompt précis :

```python
import llm

vague = "Résume cet avis client : Livraison en 5 jours au lieu de 2, colis abîmé, mais le service client a remboursé les frais de port en une heure."
precis = """Tu analyses des avis clients pour une boutique en ligne.
Lis l'avis entre les balises <avis>.
Réponds uniquement avec un objet JSON contenant :
- "sentiment" : "positif", "negatif" ou "mitige"
- "problemes" : une liste de problèmes courts (3 mots maximum chacun)
- "resume" : une phrase de 15 mots maximum

<avis>Livraison en 5 jours au lieu de 2, colis abîmé, mais le service client a remboursé les frais de port en une heure.</avis>"""

print(await llm.complete(vague))
print("-" * 40)
print(await llm.complete(precis))
```

## Les techniques qui marchent

- **Few-shot** : montrer deux ou trois exemples d'entrée et de sortie attendue. Très efficace pour imposer un format ou un style.
- **Laisser réfléchir** : demander au modèle de raisonner étape par étape avant de conclure améliore les tâches de logique et de calcul. On peut lui demander de mettre son raisonnement entre balises, puis ne garder que la conclusion.
- **Sortie structurée** : demander du JSON, puis **valider** le résultat en Python. Les API récentes proposent aussi des modes de sortie structurée, qui garantissent un JSON valide.
- **Découper** : plusieurs prompts simples enchaînés valent mieux qu'un prompt géant (*prompt chaining*, leçon sur les workflows).

## Toujours valider la sortie

Un LLM peut répondre avec du texte autour du JSON, entourer le JSON de balises de code, oublier une clé. Ton code doit s'en protéger.

```python
import json, re

def extraire_json(texte):
    bloc = re.search(r"\{.*\}", texte, re.S)          # du premier { au dernier }
    if not bloc:
        raise ValueError("Aucun JSON dans la réponse")
    return json.loads(bloc.group(0))

fence = "`" * 3                                     # trois accents graves, comme dans une vraie réponse
reponse = f'Voici le résultat :\n{fence}json\n{{"sentiment": "mitige", "problemes": ["retard", "colis abîmé"]}}\n{fence}'
extraire_json(reponse)
```

## L'injection de prompt

Si ton prompt contient un texte écrit par un utilisateur, ce texte peut contenir des instructions (« ignore les consignes précédentes et… »). Délimite clairement les données, rappelle au modèle de les traiter comme des données, et ne donne jamais à un LLM plus de droits que nécessaire. Le module LLMOps du Lead y consacre un chapitre entier (garde-fous).

> **À retenir** : sois précis, structure, donne des exemples, impose un format, et valide toujours la sortie avant de t'en servir.
''',
"exercises": [
 E("e-gen-2-a", "Un template de prompt few-shot",
   "Écris `construire_prompt(texte, exemples)` qui renvoie un prompt de classification de tickets de support. Le prompt doit contenir, dans cet ordre : la consigne exacte `Classe le ticket dans une catégorie : facturation, technique ou compte. Réponds par un seul mot.` ; puis chaque exemple sous la forme `Ticket : ...` suivi à la ligne de `Catégorie : ...` ; puis `Ticket : <texte>` et une dernière ligne `Catégorie :`.",
   'exemples = [("Ma carte a été débitée deux fois", "facturation"), ("L\'appli plante au démarrage", "technique")]\n\ndef construire_prompt(texte, exemples):\n    pass\n\nprint(construire_prompt("Je n\'arrive plus à me connecter", exemples))\n',
   'exemples = [("Ma carte a été débitée deux fois", "facturation"), ("L\'appli plante au démarrage", "technique")]\n\ndef construire_prompt(texte, exemples):\n    lignes = ["Classe le ticket dans une catégorie : facturation, technique ou compte. Réponds par un seul mot.", ""]\n    for t, c in exemples:\n        lignes += [f"Ticket : {t}", f"Catégorie : {c}", ""]\n    lignes += [f"Ticket : {texte}", "Catégorie :"]\n    return "\\n".join(lignes)\n\nprint(construire_prompt("Je n\'arrive plus à me connecter", exemples))\n',
   r'''p = construire_prompt("Je n'arrive plus à me connecter", exemples)
assert isinstance(p, str), "construire_prompt doit renvoyer un texte."
assert p.startswith("Classe le ticket dans une catégorie : facturation, technique ou compte."), "Le prompt doit commencer par la consigne exacte."
assert "Ticket : Ma carte a été débitée deux fois\nCatégorie : facturation" in p, "Chaque exemple doit être « Ticket : ... » puis, à la ligne, « Catégorie : ... »."
assert p.rstrip().endswith("Ticket : Je n'arrive plus à me connecter\nCatégorie :"), "Le prompt doit finir par le ticket à classer puis « Catégorie : »."
assert p.index("débitée") < p.index("plante") < p.index("connecter"), "Les exemples viennent avant le ticket à classer, dans l'ordre."
''',
   "Construis une liste de lignes, puis \"\\n\".join(lignes). Termine par \"Catégorie :\" pour que le modèle complète."),
 E("e-gen-2-b", "Valider une sortie structurée",
   "Écris `analyser(reponse)` qui extrait le JSON d'une réponse de LLM et vérifie qu'il contient `sentiment` (une valeur parmi `positif`, `negatif`, `mitige`) et `problemes` (une liste). Elle renvoie le dictionnaire, ou lève une `ValueError` avec un message clair dans tous les autres cas (pas de JSON, JSON invalide, clé manquante, valeur interdite).",
   "import json, re\n\ndef analyser(reponse):\n    pass\n",
   'import json, re\n\ndef analyser(reponse):\n    bloc = re.search(r"\\{.*\\}", reponse, re.S)\n    if not bloc:\n        raise ValueError("Aucun JSON trouvé")\n    try:\n        d = json.loads(bloc.group(0))\n    except json.JSONDecodeError as e:\n        raise ValueError(f"JSON invalide : {e}")\n    if d.get("sentiment") not in {"positif", "negatif", "mitige"}:\n        raise ValueError("sentiment manquant ou invalide")\n    if not isinstance(d.get("problemes"), list):\n        raise ValueError("problemes doit être une liste")\n    return d\n\nanalyser(\'Résultat : {"sentiment": "mitige", "problemes": ["retard"]}\')\n',
   r'''ok = analyser('Voici :\n```json\n{"sentiment": "negatif", "problemes": ["retard", "casse"]}\n```')
assert ok == {"sentiment": "negatif", "problemes": ["retard", "casse"]}, f"analyser renvoie {ok}."
for mauvais in ["Pas de JSON ici", '{"sentiment": "negatif", "problemes": ["x"', '{"problemes": []}', '{"sentiment": "joyeux", "problemes": []}', '{"sentiment": "positif", "problemes": "aucun"}']:
    try:
        analyser(mauvais)
        assert False, f"analyser({mauvais!r}) aurait dû lever une ValueError."
    except ValueError:
        pass
''',
   "re.search(r\"\\{.*\\}\", texte, re.S) trouve le JSON. Attrape json.JSONDecodeError pour la relancer en ValueError."),
]},
# ================================================================ LLM 3 : tokens
{"id": "l-gen-3", "title": "Tokens, fenêtre de contexte et coûts", "minutes": 70,
"body": r'''
Les LLM ne lisent pas des lettres ni des mots, mais des **tokens** : des morceaux de mots issus d'un découpage appris. C'est l'unité de tout : la **fenêtre de contexte**, la **facturation**, la **vitesse**.

## Comment on découpe : le BPE

L'algorithme le plus courant est le **BPE** (*Byte Pair Encoding*). On part des caractères, puis on fusionne, encore et encore, la paire de symboles voisins la plus fréquente dans le corpus. Les mots fréquents deviennent un seul token, les mots rares restent découpés.

```viz bpe
```

```python
from collections import Counter

corpus = ["l o w", "l o w e r", "n e w e s t", "w i d e s t"]
paires = Counter()
for mot in corpus:
    symboles = mot.split()
    for a, b in zip(symboles, symboles[1:]):
        paires[(a, b)] += 1
paires.most_common(3)
```

Ordres de grandeur utiles : en anglais, un token fait environ 4 caractères, soit trois quarts de mot. Le français, moins représenté dans les données d'entraînement, demande un peu plus de tokens pour le même texte. Le code et les langues rares en demandent encore plus.

## La fenêtre de contexte

C'est le nombre maximal de tokens que le modèle peut traiter **en une fois** : le prompt système, l'historique de la conversation, les documents ajoutés **et** la réponse. Les modèles récents acceptent de 100 000 à plus d'un million de tokens, mais :

- plus de contexte = plus cher et plus lent ;
- les modèles exploitent moins bien l'information noyée au milieu d'un très long contexte ;
- dans une conversation longue, il faut **résumer** ou **tronquer** l'historique.

## Les coûts

Les API facturent au **million de tokens**, avec des prix différents en entrée et en sortie (la sortie coûte en général plusieurs fois plus cher). Un calcul rapide évite les mauvaises surprises :

```python
def cout(tokens_entree, tokens_sortie, prix_entree_mtok, prix_sortie_mtok):
    return tokens_entree / 1e6 * prix_entree_mtok + tokens_sortie / 1e6 * prix_sortie_mtok

# 10 000 requêtes par jour, 2 000 tokens en entrée, 300 en sortie, avec des prix fictifs de 3 € et 15 € par million
par_jour = 10_000 * cout(2_000, 300, 3, 15)
print(f"{par_jour:.0f} € par jour, soit environ {par_jour * 30:.0f} € par mois")
```

## Les paramètres d'échantillonnage

- **Température** : la variété des réponses (leçon précédente). Basse pour l'extraction de données et le code, plus haute pour la création.
- **Top-p** (*nucleus sampling*) : on ne garde que les tokens les plus probables dont les probabilités cumulées atteignent p.
- **max_tokens** : la longueur maximale de la réponse. La génération s'arrête net quand elle est atteinte.

> **À retenir** : raisonne toujours en tokens. Estime le coût et la taille du contexte **avant** de construire, et mesure-les ensuite.
''',
"exercises": [
 E("e-gen-3-a", "Une étape de BPE",
   "Écris `fusion_bpe(corpus)` : elle trouve la paire de symboles voisins la plus fréquente dans le corpus (une liste de mots, symboles séparés par des espaces), puis renvoie un **nouveau corpus** où cette paire est fusionnée partout en un seul symbole. En cas d'égalité, prends la paire qui apparaît la première dans `Counter.most_common`.",
   'from collections import Counter\n\ncorpus = ["l o w", "l o w e r", "n e w e s t", "w i d e s t"]\n\ndef fusion_bpe(corpus):\n    pass\n',
   'from collections import Counter\n\ncorpus = ["l o w", "l o w e r", "n e w e s t", "w i d e s t"]\n\ndef fusion_bpe(corpus):\n    paires = Counter()\n    for mot in corpus:\n        s = mot.split()\n        paires.update(zip(s, s[1:]))\n    (a, b), _ = paires.most_common(1)[0]\n    nouveau = []\n    for mot in corpus:\n        s, sortie, i = mot.split(), [], 0\n        while i < len(s):\n            if i + 1 < len(s) and s[i] == a and s[i + 1] == b:\n                sortie.append(a + b)\n                i += 2\n            else:\n                sortie.append(s[i])\n                i += 1\n        nouveau.append(" ".join(sortie))\n    return nouveau\n\nc = corpus\nfor _ in range(3):\n    c = fusion_bpe(c)\n    print(c)\n',
   r'''c1 = fusion_bpe(["l o w", "l o w e r", "n e w e s t", "w i d e s t"])
assert c1 == ["lo w", "lo w e r", "n e w e s t", "w i d e s t"], f"Après une fusion : {c1}. La paire la plus fréquente (et la première à égalité) est ('l', 'o')."
c3 = fusion_bpe(fusion_bpe(c1))
assert c3 == ["low", "low e r", "n e w es t", "w i d es t"], f"Après trois fusions : {c3}."
''',
   "Counter.update(zip(s, s[1:])) compte les paires d'un mot. Puis reconstruis chaque mot en fusionnant la paire choisie."),
 E("e-gen-3-b", "Tenir dans le budget de contexte",
   "Écris `tronquer(messages, budget)` : `messages` est une liste de dictionnaires `{\"role\", \"content\"}` dont le premier est le message système. Garde **toujours** le message système, puis le plus grand nombre de messages **les plus récents** possible, sans que le total de tokens dépasse `budget`. Compte les tokens avec la fonction `tokens(texte)` fournie. L'ordre chronologique doit être conservé.",
   'def tokens(texte):\n    return len(texte) // 4 + 1          # estimation grossière : 4 caractères par token\n\ndef tronquer(messages, budget):\n    pass\n',
   'def tokens(texte):\n    return len(texte) // 4 + 1\n\ndef tronquer(messages, budget):\n    systeme, reste = messages[0], messages[1:]\n    total = tokens(systeme["content"])\n    gardes = []\n    for m in reversed(reste):\n        t = tokens(m["content"])\n        if total + t > budget:\n            break\n        gardes.append(m)\n        total += t\n    return [systeme] + gardes[::-1]\n',
   r'''conv = [{"role": "system", "content": "s" * 40}] + [{"role": "user" if i % 2 == 0 else "assistant", "content": f"message {i} " + "x" * 30} for i in range(10)]
r = tronquer(conv, 60)
assert r[0] is conv[0], "Le message système doit toujours être gardé, en premier."
assert sum(tokens(m["content"]) for m in r) <= 60, "Le total dépasse le budget."
assert [m["content"][:10] for m in r[1:]] == ["message 6 ", "message 7 ", "message 8 ", "message 9 "], f"Il faut garder les messages les plus récents dans l'ordre ; tu gardes {[m['content'][:10] for m in r[1:]]}."
assert len(tronquer(conv, 1000)) == 11, "Si tout tient dans le budget, il faut tout garder."
''',
   "Parcours les messages du plus récent au plus ancien (reversed), ajoute tant que le budget le permet, puis remets-les dans l'ordre avec [::-1]."),
]},
# ================================================================ Agents 1
{"id": "l-agent-1", "title": "Ce qu'est vraiment un agent", "minutes": 90,
"body": r'''
Un **agent** est un LLM qui **décide lui-même** des étapes à suivre, en appelant des **outils**, dans une **boucle**, jusqu'à atteindre son objectif. C'est l'idée la plus importante de l'IA appliquée actuelle, et un fil rouge de l'Essentials comme du FullStack (LangGraph, MCP).

```viz agent
```

## Les outils

Un **outil** est une fonction de ton code que le modèle peut demander d'appeler. On le décrit au modèle avec un nom, une description et un **schéma JSON** des paramètres :

```json
{
  "name": "meteo",
  "description": "Donne la météo actuelle d'une ville. À utiliser dès qu'on parle du temps qu'il fait.",
  "input_schema": {
    "type": "object",
    "properties": {"ville": {"type": "string", "description": "Nom de la ville, par exemple Lyon"}},
    "required": ["ville"]
  }
}
```

Le modèle n'exécute rien lui-même : il **répond** « appelle `meteo` avec `{"ville": "Lyon"}` ». C'est **ton code** qui exécute la fonction, puis renvoie le résultat au modèle, qui continue.

## La boucle d'un agent

1. On envoie au modèle l'objectif, l'historique et la liste des outils.
2. Le modèle répond soit par un **appel d'outil**, soit par une **réponse finale**.
3. Si c'est un appel d'outil, on l'exécute et on ajoute le résultat (l'**observation**) à l'historique. Retour à l'étape 1.
4. On s'arrête sur la réponse finale, ou après un **nombre maximal d'étapes** pour éviter les boucles infinies.

```python
import json

def calculatrice(expression):
    autorises = set("0123456789+-*/(). ")
    if not set(expression) <= autorises:
        return "Erreur : expression refusée"
    return str(eval(expression))

OUTILS = {"calculatrice": calculatrice}

def modele_simule(historique):
    """Un faux LLM qui sait utiliser la calculatrice, pour comprendre la boucle."""
    dernier = historique[-1]
    if dernier["role"] == "user":
        return {"type": "outil", "nom": "calculatrice", "args": {"expression": "450 / 12"}}
    return {"type": "final", "texte": f"Cela fait {dernier['content']} heures par semaine."}

historique = [{"role": "user", "content": "450 heures en 12 semaines, ça fait combien par semaine ?"}]
for etape in range(5):
    action = modele_simule(historique)
    print(f"Étape {etape + 1} :", action)
    if action["type"] == "final":
        break
    resultat = OUTILS[action["nom"]](**action["args"])
    historique.append({"role": "outil", "content": resultat})
```

## Avec un vrai LLM

On peut faire la même chose avec un vrai modèle, en lui demandant de répondre en JSON. Les API proposent un mécanisme natif d'appel d'outils (*tool use* ou *function calling*), plus fiable : c'est lui que tu utiliseras en formation.

```python
import llm, json, re

consigne = """Tu es un agent. Outils disponibles :
- calculatrice(expression) : calcule une expression arithmétique.
Réponds UNIQUEMENT en JSON, soit {"type": "outil", "nom": "calculatrice", "args": {"expression": "..."}},
soit {"type": "final", "texte": "..."} quand tu as la réponse."""

historique = [{"role": "user", "content": "Une formation de 450 heures sur 60 jours ouvrés : combien d'heures par jour ?"}]
for etape in range(4):
    texte = await llm.chat(historique, system=consigne)
    print(f"Étape {etape + 1} :", texte)
    try:
        action = json.loads(re.search(r"\{.*\}", texte, re.S).group(0))
    except Exception:
        print("Réponse non exploitable, on s'arrête.")
        break
    if action.get("type") != "outil":
        break
    observation = calculatrice(action["args"]["expression"])
    historique += [{"role": "assistant", "content": texte}, {"role": "user", "content": f"Résultat de l'outil : {observation}"}]
```

## Agent ou workflow ?

Un **workflow** enchaîne des étapes **fixées à l'avance** par le développeur ; un **agent** choisit ses étapes. Les agents sont plus flexibles mais plus chers, plus lents et plus difficiles à fiabiliser. Règle d'or : commence par la solution la plus simple qui marche, et n'ajoute de l'autonomie que si elle apporte un vrai gain.

> **À retenir** : agent = LLM + outils + boucle + condition d'arrêt. Valide les arguments des outils, limite le nombre d'étapes, et demande une confirmation humaine avant toute action irréversible.
''',
"exercises": [
 E("e-agent-1-a", "Exécuter un appel d'outil sans planter",
   "Écris `executer(appel, outils)` : `appel` est un dictionnaire `{\"nom\": ..., \"args\": {...}}` et `outils` un dictionnaire nom → fonction. Elle renvoie `{\"ok\": True, \"resultat\": ...}` si tout va bien, et `{\"ok\": False, \"erreur\": \"...\"}` si l'outil est inconnu ou si la fonction lève une exception (arguments manquants, erreur interne). Un agent ne doit jamais planter : l'erreur est renvoyée au modèle, qui peut se corriger.",
   'def meteo(ville):\n    donnees = {"Paris": "12 °C, nuageux", "Lyon": "15 °C, soleil"}\n    if ville not in donnees:\n        raise KeyError(f"Ville inconnue : {ville}")\n    return donnees[ville]\n\nOUTILS = {"meteo": meteo}\n\ndef executer(appel, outils):\n    pass\n',
   'def meteo(ville):\n    donnees = {"Paris": "12 °C, nuageux", "Lyon": "15 °C, soleil"}\n    if ville not in donnees:\n        raise KeyError(f"Ville inconnue : {ville}")\n    return donnees[ville]\n\nOUTILS = {"meteo": meteo}\n\ndef executer(appel, outils):\n    nom = appel.get("nom")\n    if nom not in outils:\n        return {"ok": False, "erreur": f"Outil inconnu : {nom}"}\n    try:\n        return {"ok": True, "resultat": outils[nom](**appel.get("args", {}))}\n    except Exception as e:\n        return {"ok": False, "erreur": f"{type(e).__name__} : {e}"}\n\nprint(executer({"nom": "meteo", "args": {"ville": "Lyon"}}, OUTILS))\nprint(executer({"nom": "meteo", "args": {"ville": "Brest"}}, OUTILS))\n',
   r'''assert executer({"nom": "meteo", "args": {"ville": "Lyon"}}, OUTILS) == {"ok": True, "resultat": "15 °C, soleil"}, "L'appel valide doit renvoyer ok et le résultat."
for appel in [{"nom": "bourse", "args": {}}, {"nom": "meteo", "args": {"ville": "Brest"}}, {"nom": "meteo", "args": {}}, {"nom": "meteo", "args": {"pays": "France"}}]:
    r = executer(appel, OUTILS)
    assert isinstance(r, dict) and r.get("ok") is False and r.get("erreur"), f"Pour {appel}, il faut renvoyer ok False et un message d'erreur ; tu renvoies {r}."
''',
   "Teste d'abord si le nom existe dans outils, puis entoure l'appel outils[nom](**args) d'un try / except Exception."),
 E("e-agent-1-b", "Ta propre boucle d'agent",
   "Écris `agent(question, modele, outils, max_etapes=5)`. L'historique commence par `{\"role\": \"user\", \"content\": question}`. À chaque étape : `action = modele(historique)` ; si `action[\"type\"] == \"final\"`, renvoie `action[\"texte\"]` ; sinon exécute l'outil (avec ta fonction `executer`, recopiée) et ajoute `{\"role\": \"outil\", \"content\": str(résultat_de_executer)}` à l'historique. Si `max_etapes` est atteint, renvoie exactement `Abandon : trop d'étapes`.",
   'def executer(appel, outils):\n    pass   # recopie ta fonction de l\'exercice précédent\n\ndef agent(question, modele, outils, max_etapes=5):\n    pass\n\n# Un faux modèle pour tester : il demande la météo de deux villes puis compare\ndef modele_test(historique):\n    n_obs = sum(1 for m in historique if m["role"] == "outil")\n    if n_obs == 0:\n        return {"type": "outil", "nom": "meteo", "args": {"ville": "Paris"}}\n    if n_obs == 1:\n        return {"type": "outil", "nom": "meteo", "args": {"ville": "Lyon"}}\n    return {"type": "final", "texte": "Il fait plus chaud à Lyon."}\n\nOUTILS = {"meteo": lambda ville: {"Paris": 12, "Lyon": 15}[ville]}\n',
   'def executer(appel, outils):\n    nom = appel.get("nom")\n    if nom not in outils:\n        return {"ok": False, "erreur": f"Outil inconnu : {nom}"}\n    try:\n        return {"ok": True, "resultat": outils[nom](**appel.get("args", {}))}\n    except Exception as e:\n        return {"ok": False, "erreur": f"{type(e).__name__} : {e}"}\n\ndef agent(question, modele, outils, max_etapes=5):\n    historique = [{"role": "user", "content": question}]\n    for _ in range(max_etapes):\n        action = modele(historique)\n        if action["type"] == "final":\n            return action["texte"]\n        historique.append({"role": "outil", "content": str(executer(action, outils))})\n    return "Abandon : trop d\'étapes"\n\ndef modele_test(historique):\n    n_obs = sum(1 for m in historique if m["role"] == "outil")\n    if n_obs == 0:\n        return {"type": "outil", "nom": "meteo", "args": {"ville": "Paris"}}\n    if n_obs == 1:\n        return {"type": "outil", "nom": "meteo", "args": {"ville": "Lyon"}}\n    return {"type": "final", "texte": "Il fait plus chaud à Lyon."}\n\nOUTILS = {"meteo": lambda ville: {"Paris": 12, "Lyon": 15}[ville]}\nprint(agent("Où fait-il le plus chaud ?", modele_test, OUTILS))\n',
   r'''vus = []
def espion(h):
    vus.append([dict(m) for m in h])
    return modele_test(h)
assert agent("Où fait-il le plus chaud ?", espion, OUTILS) == "Il fait plus chaud à Lyon.", "L'agent doit renvoyer le texte final du modèle."
assert vus[0] == [{"role": "user", "content": "Où fait-il le plus chaud ?"}], "L'historique doit commencer par la question de l'utilisateur."
assert len(vus[-1]) == 3 and "15" in vus[-1][2]["content"], "Les observations des outils doivent être ajoutées à l'historique."
boucle = lambda h: {"type": "outil", "nom": "meteo", "args": {"ville": "Paris"}}
assert agent("?", boucle, OUTILS, max_etapes=3) == "Abandon : trop d'étapes", "Un modèle qui boucle doit être arrêté après max_etapes."
casse = lambda h: {"type": "final", "texte": h[-1]["content"]} if len(h) > 1 else {"type": "outil", "nom": "inconnu", "args": {}}
assert "Outil inconnu" in agent("?", casse, OUTILS), "Une erreur d'outil doit être renvoyée au modèle dans l'historique, pas faire planter l'agent."
''',
   "Une boucle for sur range(max_etapes). Le return dans la boucle gère la réponse finale ; le return après la boucle gère l'abandon."),
]},
# ================================================================ Agents 2 : workflows
{"id": "l-agent-2", "title": "Modèles de conception : outils et workflows", "minutes": 70,
"body": r'''
La plupart des systèmes d'IA en production ne sont pas des agents totalement autonomes, mais des **workflows** : des compositions simples et prévisibles d'appels à un LLM. Voici les cinq motifs à connaître, du plus simple au plus autonome.

| Motif | Principe | Exemple |
| --- | --- | --- |
| **Enchaînement** (*prompt chaining*) | La sortie d'un appel devient l'entrée du suivant, avec des contrôles entre les étapes | Rédiger un plan, le valider, puis rédiger l'article |
| **Routage** (*routing*) | Un premier appel classe la demande, puis on l'envoie au traitement spécialisé | Un ticket de facturation part vers un prompt et des outils différents d'un ticket technique |
| **Parallélisation** | Plusieurs appels indépendants en même temps, puis agrégation | Analyser 50 avis en parallèle ; ou voter entre 3 réponses |
| **Orchestrateur et exécutants** | Un LLM découpe la tâche et délègue les sous-tâches | Modifier plusieurs fichiers d'un projet de code |
| **Évaluateur et optimiseur** | Un appel produit, un autre critique, on boucle jusqu'à ce que ce soit bon | Traduire, relire, corriger |

## Le routage, en code

Le routeur peut être un LLM, un petit modèle de classification, ou même des règles simples : le motif est le même.

```python
def router(message):
    m = message.lower()
    if any(mot in m for mot in ["facture", "paiement", "remboursement", "débité"]):
        return "facturation"
    if any(mot in m for mot in ["bug", "plante", "erreur", "lent"]):
        return "technique"
    return "general"

TRAITEMENTS = {
    "facturation": lambda m: "→ prompt facturation + outil : historique des paiements",
    "technique": lambda m: "→ prompt technique + outil : journal d'erreurs",
    "general": lambda m: "→ prompt généraliste",
}
for msg in ["J'ai été débité deux fois", "L'appli plante au démarrage", "Vous ouvrez le dimanche ?"]:
    route = router(msg)
    print(f"{msg!r:35} {route:12} {TRAITEMENTS[route](msg)}")
```

## L'enchaînement avec un contrôle, avec un vrai LLM

```python
import llm

idee = "une application qui aide les étudiants à réviser avec des quiz générés par IA"
accroche = await llm.complete(f"Écris une accroche marketing de 12 mots maximum pour : {idee}. Réponds par l'accroche seule.")
print("Accroche :", accroche)
if len(accroche.split()) > 15:                      # contrôle entre deux étapes
    accroche = await llm.complete(f"Raccourcis à 12 mots maximum : {accroche}")
traduction = await llm.complete(f"Traduis en anglais, réponds par la traduction seule : {accroche}")
print("Traduction :", traduction)
```

> **À retenir** : choisis le motif le plus simple qui résout ton problème. Un workflow est plus facile à tester, à surveiller et à expliquer qu'un agent. L'autonomie se justifie quand on ne peut pas prévoir les étapes à l'avance.
''',
"exercises": [
 E("e-agent-2-a", "Évaluateur et optimiseur",
   "Écris `ameliorer(tache, generer, evaluer, seuil=8, max_tours=4)`. Au premier tour, `brouillon = generer(tache, None)` ; à chaque tour, `note, critique = evaluer(brouillon)` ; si `note >= seuil`, renvoie `(brouillon, note, tour)` où `tour` est le numéro du tour (1 pour le premier) ; sinon `brouillon = generer(tache, critique)` et on recommence. Après `max_tours` tours sans atteindre le seuil, renvoie le **meilleur** brouillon vu, avec sa note et `max_tours`.",
   'def ameliorer(tache, generer, evaluer, seuil=8, max_tours=4):\n    pass\n\n# Des faux modèles pour tester\ndef generer_test(tache, critique):\n    return tache if critique is None else tache + " !"\n\ndef evaluer_test(texte):\n    note = 5 + texte.count("!")\n    return note, "Plus d\'enthousiasme."\n',
   'def ameliorer(tache, generer, evaluer, seuil=8, max_tours=4):\n    brouillon = generer(tache, None)\n    meilleur = None\n    for tour in range(1, max_tours + 1):\n        note, critique = evaluer(brouillon)\n        if meilleur is None or note > meilleur[1]:\n            meilleur = (brouillon, note)\n        if note >= seuil:\n            return brouillon, note, tour\n        brouillon = generer(tache, critique)\n    return meilleur[0], meilleur[1], max_tours\n\ndef generer_test(tache, critique):\n    return tache if critique is None else tache + " !"\n\ndef evaluer_test(texte):\n    note = 5 + texte.count("!")\n    return note, "Plus d\'enthousiasme."\n\nprint(ameliorer("Bonjour", generer_test, evaluer_test))\n',
   r'''assert ameliorer("Bonjour", generer_test, evaluer_test, seuil=6) == ("Bonjour !", 6, 2), f"Avec seuil=6 : {ameliorer('Bonjour', generer_test, evaluer_test, seuil=6)}, j'attendais ('Bonjour !', 6, 2)."
g = lambda t, c: t + "!" if c else t
assert ameliorer("x", g, lambda s: (5 + s.count("!"), "+"), seuil=20, max_tours=3) == ("x!", 6, 3), "Sans atteindre le seuil, il faut renvoyer le meilleur brouillon, sa note et max_tours."
n = []
ameliorer("a", lambda t, c: n.append(1) or t, lambda s: (9, ""), seuil=8)
assert len(n) == 1, "Si le premier brouillon suffit, on ne doit pas régénérer."
''',
   "Garde en mémoire le meilleur (brouillon, note). Une boucle for tour in range(1, max_tours + 1)."),
]},
# ================================================================ Évaluation
{"id": "l-eval-1", "title": "Évaluer un système d'IA", "minutes": 90,
"body": r'''
« Ça a l'air de marcher » n'est pas une évaluation. Un système d'IA se mesure, comme n'importe quel logiciel se teste. C'est aussi ce qui distingue un profil junior d'un profil solide en entretien : savoir **prouver** qu'un système marche, et savoir quand il ne marche pas.

## Le jeu d'évaluation

Tout commence par un **jeu d'évaluation** (*golden set*) : des dizaines à des centaines d'entrées représentatives, avec la sortie attendue ou des critères de réussite. Il doit contenir des cas faciles, des cas limites, et des cas pièges.

## Trois familles de méthodes

1. **Vérifications automatiques exactes** : la sortie est-elle un JSON valide ? la catégorie est-elle la bonne ? le chiffre est-il exact ? On calcule exactitude, précision, rappel.
2. **Métriques de similarité** avec une référence : recouvrement de mots (BLEU, ROUGE) ou similarité d'embeddings. Utile pour la traduction et le résumé, mais grossier.
3. **LLM juge** (*LLM-as-a-judge*) : un modèle note la réponse selon une **grille** précise. Rapide et souple, mais il faut vérifier que ses notes concordent avec celles d'humains sur un échantillon.

## L'exemple du triage médical

Un assistant classe des messages de patients en `urgent` ou `non urgent`. Une erreur n'a pas le même coût dans les deux sens : rater une urgence est grave. L'exactitude globale ne suffit pas, il faut regarder le **rappel** sur la classe `urgent`.

```python
import pandas as pd

jeu = pd.DataFrame({
    "message": ["Douleur thoracique depuis 1 h", "Renouvellement d'ordonnance", "Fièvre à 40 chez mon bébé de 2 mois",
                "Question sur ma facture", "Difficulté à respirer", "Rendez-vous de contrôle", "Mal de tête léger", "Saignement abondant"],
    "attendu": ["urgent", "non urgent", "urgent", "non urgent", "urgent", "non urgent", "non urgent", "urgent"],
})
jeu["predit"] = ["urgent", "non urgent", "non urgent", "non urgent", "urgent", "non urgent", "urgent", "urgent"]
exactitude = (jeu.attendu == jeu.predit).mean()
urgents = jeu[jeu.attendu == "urgent"]
rappel_urgent = (urgents.predit == "urgent").mean()
print(f"Exactitude : {exactitude:.0%}   Rappel sur les urgences : {rappel_urgent:.0%}")
jeu[jeu.attendu != jeu.predit]
```

75 % d'exactitude, mais une urgence pédiatrique ratée : ce système n'est pas déployable en l'état.

## Un LLM juge

```python
import llm

grille = """Tu évalues la réponse d'un assistant de support. Note de 1 à 5 :
5 = exacte, complète et concise ; 3 = partiellement utile ; 1 = fausse ou hors sujet.
Réponds sur la dernière ligne au format exact « Note : X/5 »."""
question = "Combien de temps les fichiers restent-ils dans la corbeille avec l'offre gratuite ?"
reponse = "Ils restent 30 jours, puis ils sont supprimés définitivement."
verdict = await llm.complete(f"{grille}\n\nQuestion : {question}\nRéponse évaluée : {reponse}")
print(verdict)
```

## Les bonnes pratiques

- **Automatise** : l'évaluation tourne à chaque changement de prompt ou de modèle, comme des tests de régression.
- **Répète** : un LLM n'est pas déterministe. Fais plusieurs passages et regarde la variance.
- **Lis les erreurs** une par une : c'est là que tu comprends ce qu'il faut corriger.
- **Mesure aussi** le coût, la latence et le taux de refus, pas seulement la qualité.

> **À retenir** : pas de déploiement sans jeu d'évaluation. Choisis la métrique selon le coût des erreurs, et vérifie ton LLM juge contre des notes humaines.
''',
"exercises": [
 E("e-eval-1-a", "Un banc d'évaluation",
   "Écris `evaluer(modele, jeu)` : `jeu` est une liste de couples `(entrée, attendu)` et `modele` une fonction. Elle renvoie un dictionnaire avec `exactitude` (proportion de bonnes réponses), `rappel_urgent` (proportion des cas attendus `urgent` prédits `urgent`) et `erreurs` (la liste des entrées mal classées, dans l'ordre).",
   'jeu = [("Douleur thoracique", "urgent"), ("Facture", "non urgent"), ("Bébé fièvre 40", "urgent"),\n       ("Ordonnance", "non urgent"), ("Saignement abondant", "urgent")]\n\ndef modele_test(texte):\n    return "urgent" if any(m in texte for m in ["Douleur", "Saignement"]) else "non urgent"\n\ndef evaluer(modele, jeu):\n    pass\n',
   'jeu = [("Douleur thoracique", "urgent"), ("Facture", "non urgent"), ("Bébé fièvre 40", "urgent"),\n       ("Ordonnance", "non urgent"), ("Saignement abondant", "urgent")]\n\ndef modele_test(texte):\n    return "urgent" if any(m in texte for m in ["Douleur", "Saignement"]) else "non urgent"\n\ndef evaluer(modele, jeu):\n    predits = [(x, y, modele(x)) for x, y in jeu]\n    urgents = [p for p in predits if p[1] == "urgent"]\n    return {\n        "exactitude": sum(y == p for _, y, p in predits) / len(jeu),\n        "rappel_urgent": sum(p == "urgent" for _, _, p in urgents) / len(urgents),\n        "erreurs": [x for x, y, p in predits if y != p],\n    }\n\nevaluer(modele_test, jeu)\n',
   r'''r = evaluer(modele_test, jeu)
assert abs(r["exactitude"] - 0.8) < 1e-9, f"exactitude vaut {r['exactitude']}, j'attendais 0.8."
assert abs(r["rappel_urgent"] - 2 / 3) < 1e-9, f"rappel_urgent vaut {r['rappel_urgent']}, j'attendais 2/3."
assert r["erreurs"] == ["Bébé fièvre 40"], f"erreurs vaut {r['erreurs']}."
''',
   "Calcule d'abord la liste des prédictions, puis filtre les cas attendus « urgent » pour le rappel."),
 E("e-eval-1-b", "Lire la note d'un LLM juge",
   "Écris `lire_note(verdict)` qui extrait la note d'une réponse de LLM juge contenant `Note : X/5` (X entier de 1 à 5, espaces optionnels, majuscule ou minuscule). S'il y a plusieurs notes, prends la **dernière**. Lève une `ValueError` si aucune note valide n'est trouvée.",
   "import re\n\ndef lire_note(verdict):\n    pass\n",
   'import re\n\ndef lire_note(verdict):\n    notes = re.findall(r"note\\s*:\\s*([1-5])\\s*/\\s*5", verdict, re.I)\n    if not notes:\n        raise ValueError("Aucune note trouvée")\n    return int(notes[-1])\n\nprint(lire_note("La réponse est exacte et concise.\\nNote : 5/5"))\n',
   r'''assert lire_note("Bonne réponse.\nNote : 4/5") == 4, "Cas simple : Note : 4/5."
assert lire_note("note:2 / 5") == 2, "Les espaces et la casse peuvent varier."
assert lire_note("Brouillon : Note : 3/5. Après relecture, Note : 5/5") == 5, "S'il y a plusieurs notes, prends la dernière."
for mauvais in ["Très bien !", "Note : 7/5", "Note : 4/10"]:
    try:
        lire_note(mauvais)
        assert False, f"lire_note({mauvais!r}) doit lever une ValueError."
    except ValueError:
        pass
''',
   "re.findall(r\"note\\s*:\\s*([1-5])\\s*/\\s*5\", texte, re.I) renvoie toutes les notes ; prends la dernière."),
]},
# ================================================================ n8n
{"id": "l-n8n", "title": "Automatiser avec n8n et l'IA", "minutes": 70,
"body": r'''
**n8n** est un outil d'automatisation visuel et open source : on relie des **nœuds** (*nodes*) dans un **workflow**, sans ou avec peu de code. L'Essentials y consacre une journée (pipeline de contenu, moteur de campagne GreenWatch, RAG dans n8n). C'est l'outil idéal pour prototyper en une heure un système qui combine des API, un LLM et des données.

## Les notions clés

- **Déclencheur** (*trigger*) : ce qui lance le workflow. Un horaire (Schedule), un webhook (une URL appelée par un autre service), un nouveau mail, un formulaire.
- **Nœuds** : chaque étape. HTTP Request, Google Sheets, Slack, IF, Merge, Code, et des nœuds IA (AI Agent, chat models, bases vectorielles).
- **Items** : les données circulent sous forme d'une **liste d'éléments**, chacun avec un champ `json`. Chaque nœud traite tous les items qu'il reçoit.
- **Expressions** : `{{ $json.titre }}` insère un champ de l'item courant dans un paramètre.
- **Identifiants** (*credentials*) : les clés d'API sont stockées à part, jamais en clair dans le workflow.

```viz n8n
```

## Le format des items

Un nœud **Code** de n8n reçoit et renvoie ce format. En Python, ça donne :

```python
items = [
    {"json": {"titre": "Lancement du produit", "vues": 1200, "langue": "fr"}},
    {"json": {"titre": "Product launch", "vues": 300, "langue": "en"}},
    {"json": {"titre": "Bilan trimestriel", "vues": 4500, "langue": "fr"}},
]
# Ce que ferait un nœud IF puis un nœud Set : garder le français, ajouter un champ
sortie = [{"json": {**it["json"], "populaire": it["json"]["vues"] > 1000}} for it in items if it["json"]["langue"] == "fr"]
sortie
```

## Installer n8n sur ton ordinateur

```bash
# Avec Node.js installé :
npx n8n
# ou avec Docker :
docker run -it --rm -p 5678:5678 -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n
```

Puis ouvre http://localhost:5678. Il existe aussi une version hébergée payante (n8n Cloud), avec un essai gratuit.

> **À retenir** : n8n pour prototyper vite et automatiser des processus métier ; Python quand il faut une logique complexe, des tests et du contrôle fin. Les deux se combinent : un nœud HTTP Request peut appeler ton API FastAPI.
''',
"tasks": [
  "Installer n8n en local (npx n8n ou Docker) et ouvrir http://localhost:5678",
  "Créer un workflow : déclencheur manuel → HTTP Request vers une API publique → nœud Code qui filtre les items",
  "Ajouter un nœud de modèle de langage (avec ta clé d'API) qui résume chaque item",
  "Envoyer le résultat dans un Google Sheet ou par e-mail",
  "Exporter le workflow en JSON et le publier sur GitHub",
],
"exercises": [
 E("e-n8n-a", "Un nœud Code en Python",
   "Écris `noeud_code(items)` qui imite un nœud Code de n8n : garde les items dont `statut` vaut `nouveau` et dont `montant` dépasse 100, et renvoie pour chacun un item `{\"json\": {\"client\": ..., \"montant_ttc\": ..., \"priorite\": ...}}` où `montant_ttc` vaut montant × 1,2 arrondi à 2 décimales, et `priorite` vaut `haute` au-delà de 1 000 € TTC, `normale` sinon.",
   'items = [\n    {"json": {"client": "Ada", "montant": 900, "statut": "nouveau"}},\n    {"json": {"client": "Linus", "montant": 80, "statut": "nouveau"}},\n    {"json": {"client": "Grace", "montant": 2500, "statut": "traité"}},\n    {"json": {"client": "Alan", "montant": 150, "statut": "nouveau"}},\n]\n\ndef noeud_code(items):\n    pass\n',
   'items = [\n    {"json": {"client": "Ada", "montant": 900, "statut": "nouveau"}},\n    {"json": {"client": "Linus", "montant": 80, "statut": "nouveau"}},\n    {"json": {"client": "Grace", "montant": 2500, "statut": "traité"}},\n    {"json": {"client": "Alan", "montant": 150, "statut": "nouveau"}},\n]\n\ndef noeud_code(items):\n    sortie = []\n    for it in items:\n        d = it["json"]\n        if d["statut"] == "nouveau" and d["montant"] > 100:\n            ttc = round(d["montant"] * 1.2, 2)\n            sortie.append({"json": {"client": d["client"], "montant_ttc": ttc, "priorite": "haute" if ttc > 1000 else "normale"}})\n    return sortie\n\nnoeud_code(items)\n',
   r'''assert noeud_code(items) == [{"json": {"client": "Ada", "montant_ttc": 1080.0, "priorite": "haute"}}, {"json": {"client": "Alan", "montant_ttc": 180.0, "priorite": "normale"}}], f"noeud_code renvoie {noeud_code(items)}."
''',
   "Parcours les items, lis it[\"json\"], filtre, puis construis un nouveau {\"json\": {...}} pour chaque item gardé."),
]},
# ================================================================ RAG
{"id": "l-rag-2", "title": "Un RAG de A à Z en Python", "minutes": 100,
"body": r'''
Tu as vu le principe du RAG : retrouver les bons morceaux de documents, puis demander au LLM de répondre **à partir d'eux**. On le construit maintenant de bout en bout, sur la base de connaissances du support de **CloudSync**, comme dans le projet « Créez le CloudSync RAG » de l'Essentials.

```python
from cloudsync import DOCS, QUESTIONS_TEST
print(len(DOCS), "documents. Exemple :")
print(DOCS[0]["titre"], "→", DOCS[0]["texte"][:120], "…")
```

## 1. Découper (chunking)

Les documents sont découpés en **morceaux** (*chunks*) assez petits pour être précis, assez grands pour garder le sens. Un **chevauchement** entre morceaux évite de couper une information en deux.

```viz chunk
```

## 2. Vectoriser

Chaque morceau devient un vecteur. En production, on utilise un **modèle d'embeddings** qui capture le sens (deux phrases synonymes ont des vecteurs proches). Ici, on utilise **TF-IDF**, une méthode classique fondée sur les mots, disponible dans scikit-learn : le principe de la recherche est exactement le même.

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

textes = [d["titre"] + ". " + d["texte"] for d in DOCS]
vectoriseur = TfidfVectorizer()
matrice = vectoriseur.fit_transform(textes)        # une ligne par document
print(matrice.shape, "→ documents × mots du vocabulaire")
```

## 3. Retrouver

```python
def rechercher(question, k=2):
    q = vectoriseur.transform([question])
    scores = cosine_similarity(q, matrice)[0]
    meilleurs = scores.argsort()[::-1][:k]
    return [(DOCS[i]["id"], round(float(scores[i]), 3)) for i in meilleurs]

rechercher("Combien de temps restent les fichiers supprimés ?")
```

## 4. Générer, avec les sources

Le prompt contient les morceaux retrouvés, numérotés, et une consigne stricte : répondre uniquement à partir d'eux, citer les sources, et dire « je ne sais pas » sinon.

```python
import llm

async def repondre(question, k=2):            # async : la fonction attend le LLM
    ids = [i for i, _ in rechercher(question, k)]
    contexte = "\n".join(f"[{i}] {next(d['texte'] for d in DOCS if d['id'] == i)}" for i in ids)
    prompt = f"""Tu es l'assistant du support CloudSync. Réponds en français, en 2 phrases maximum,
uniquement à partir des documents ci-dessous, et cite la source entre crochets.
Si la réponse n'y est pas, réponds : « Je ne sais pas, je transmets ta question à un conseiller. »

Documents :
{contexte}

Question : {question}"""
    return await llm.complete(prompt), ids

texte, sources = await repondre("Puis-je protéger un lien de partage par un mot de passe avec l'offre gratuite ?")
print(texte, "\nSources :", sources)
```

## 5. Évaluer la recherche

Si la recherche rate le bon document, le LLM ne peut pas bien répondre. On mesure donc d'abord le **rappel@k** : la proportion de questions pour lesquelles un document pertinent figure parmi les k premiers résultats.

```python
for k in [1, 2, 3]:
    trouves = sum(any(i in q["pertinents"] for i, _ in rechercher(q["question"], k)) for q in QUESTIONS_TEST)
    print(f"rappel@{k} = {trouves}/{len(QUESTIONS_TEST)}")
```

> **À retenir** : un RAG, c'est découper, vectoriser, retrouver, générer avec les sources, et évaluer chaque étape séparément. La qualité de la recherche limite la qualité de la réponse.
''',
"exercises": [
 E("e-rag-2-a", "Découper avec chevauchement",
   "Écris `decouper(texte, taille, chevauchement)` qui découpe le texte en morceaux de `taille` **mots**, chaque morceau commençant `taille - chevauchement` mots après le précédent. Le dernier morceau peut être plus court ; ne crée pas de morceau qui ne contiendrait que des mots déjà vus. Lève une `ValueError` si `chevauchement >= taille`.",
   "def decouper(texte, taille, chevauchement):\n    pass\n\nprint(decouper(\"un deux trois quatre cinq six sept\", 3, 1))\n",
   'def decouper(texte, taille, chevauchement):\n    if chevauchement >= taille:\n        raise ValueError("Le chevauchement doit être plus petit que la taille")\n    mots = texte.split()\n    pas = taille - chevauchement\n    morceaux = []\n    for debut in range(0, len(mots), pas):\n        morceaux.append(" ".join(mots[debut:debut + taille]))\n        if debut + taille >= len(mots):\n            break\n    return morceaux\n\nprint(decouper("un deux trois quatre cinq six sept", 3, 1))\n',
   r'''assert decouper("un deux trois quatre cinq six sept", 3, 1) == ["un deux trois", "trois quatre cinq", "cinq six sept"], f"Résultat : {decouper('un deux trois quatre cinq six sept', 3, 1)}."
assert decouper("a b c d e f g h", 4, 2) == ["a b c d", "c d e f", "e f g h"], f"Pour 8 mots, taille 4 et chevauchement 2 : {decouper('a b c d e f g h', 4, 2)}."
assert decouper("a b c d e", 3, 0) == ["a b c", "d e"], "Sans chevauchement, le dernier morceau peut être plus court."
try:
    decouper("a b", 2, 2)
    assert False, "Un chevauchement >= taille doit lever une ValueError."
except ValueError:
    pass
''',
   "Le pas vaut taille - chevauchement. Arrête-toi dès qu'un morceau atteint la fin du texte."),
 E("e-rag-2-b", "Un moteur de recherche réutilisable",
   "Écris une classe `Recherche` avec `fit(docs)` (une liste de dictionnaires avec `id`, `titre`, `texte` ; elle vectorise `titre + \". \" + texte` avec `TfidfVectorizer` et renvoie `self`) et `chercher(question, k=2)` qui renvoie la liste des `id` des k documents les plus similaires, du plus au moins similaire.",
   "from sklearn.feature_extraction.text import TfidfVectorizer\nfrom sklearn.metrics.pairwise import cosine_similarity\nfrom cloudsync import DOCS\n\nclass Recherche:\n    pass\n",
   'from sklearn.feature_extraction.text import TfidfVectorizer\nfrom sklearn.metrics.pairwise import cosine_similarity\nfrom cloudsync import DOCS\n\nclass Recherche:\n    def fit(self, docs):\n        self.docs = docs\n        self.vect = TfidfVectorizer()\n        self.matrice = self.vect.fit_transform([d["titre"] + ". " + d["texte"] for d in docs])\n        return self\n\n    def chercher(self, question, k=2):\n        scores = cosine_similarity(self.vect.transform([question]), self.matrice)[0]\n        return [self.docs[i]["id"] for i in scores.argsort()[::-1][:k]]\n\nr = Recherche().fit(DOCS)\nr.chercher("Comment récupérer un fichier supprimé ?")\n',
   r'''r = Recherche()
assert r.fit(DOCS) is r, "fit doit renvoyer self."
assert r.chercher("Comment récupérer un fichier supprimé dans la corbeille ?", 1) == ["corbeille"], f"Résultat : {r.chercher('Comment récupérer un fichier supprimé dans la corbeille ?', 1)}."
res = r.chercher("prix de l'offre Pro par mois", 3)
assert len(res) == 3 and res[0] == "tarifs", f"Pour une question de prix, le premier résultat doit être tarifs ; tu obtiens {res}."
''',
   "Inspire-toi de la leçon : fit_transform dans fit, transform puis cosine_similarity dans chercher, argsort()[::-1][:k]."),
 E("e-rag-2-c", "Mesurer le rappel@k",
   "Écris `rappel_at_k(recherche, questions, k)` qui renvoie la proportion de questions (dictionnaires avec `question` et `pertinents`) pour lesquelles **au moins un** document pertinent figure dans les k premiers résultats de `recherche(question, k)`. Puis calcule `r1` et `r3` pour la fonction de recherche fournie.",
   "from sklearn.feature_extraction.text import TfidfVectorizer\nfrom sklearn.metrics.pairwise import cosine_similarity\nfrom cloudsync import DOCS, QUESTIONS_TEST\n\nvect = TfidfVectorizer()\nmat = vect.fit_transform([d[\"titre\"] + \". \" + d[\"texte\"] for d in DOCS])\n\ndef recherche(question, k):\n    s = cosine_similarity(vect.transform([question]), mat)[0]\n    return [DOCS[i][\"id\"] for i in s.argsort()[::-1][:k]]\n\ndef rappel_at_k(recherche, questions, k):\n    pass\n",
   "from sklearn.feature_extraction.text import TfidfVectorizer\nfrom sklearn.metrics.pairwise import cosine_similarity\nfrom cloudsync import DOCS, QUESTIONS_TEST\n\nvect = TfidfVectorizer()\nmat = vect.fit_transform([d[\"titre\"] + \". \" + d[\"texte\"] for d in DOCS])\n\ndef recherche(question, k):\n    s = cosine_similarity(vect.transform([question]), mat)[0]\n    return [DOCS[i][\"id\"] for i in s.argsort()[::-1][:k]]\n\ndef rappel_at_k(recherche, questions, k):\n    trouves = sum(any(p in recherche(q[\"question\"], k) for p in q[\"pertinents\"]) for q in questions)\n    return trouves / len(questions)\n\nr1 = rappel_at_k(recherche, QUESTIONS_TEST, 1)\nr3 = rappel_at_k(recherche, QUESTIONS_TEST, 3)\nprint(r1, r3)\n",
   r'''fake = lambda q, k: ["a", "b", "c"][:k]
qs = [{"question": "x", "pertinents": ["b"]}, {"question": "y", "pertinents": ["z"]}]
assert rappel_at_k(fake, qs, 1) == 0 and rappel_at_k(fake, qs, 2) == 0.5, "Teste ta fonction sur un cas simple : avec k=2, une question sur deux est trouvée."
assert 0 < r1 <= r3 <= 1, f"r1 = {r1}, r3 = {r3} : le rappel ne peut qu'augmenter avec k."
assert r3 == rappel_at_k(recherche, QUESTIONS_TEST, 3), "r3 doit être calculé avec ta fonction et k = 3."
''',
   "any(p in resultats for p in q[\"pertinents\"]) vaut True si au moins un document pertinent est retrouvé."),
]},
]

PROJECTS = [
{"id": "p-ess", "title": "Projet Demo Day · Un assistant de support intelligent", "minutes": 180,
"body": r'''
Ton projet de fin d'Essentials : un **assistant de support** pour CloudSync, qui combine ce que tu as appris. Il **route** la demande, **retrouve** les bons documents, **répond** avec ses sources, et il est **évalué**.

Les exercices ci-dessous construisent la version testable, avec un faux modèle. Tu remplaceras ensuite le faux modèle par le vrai (`await llm.complete(...)`) dans une cellule de la leçon RAG, puis tu en feras une démo avec n8n ou une petite interface.

L'architecture :

```markdown
question ──► routeur ──┬─► « humain » (résiliation, réclamation) ─► message de transfert
                       └─► recherche top-k ─► prompt avec sources ─► LLM ─► réponse + sources
```
''',
"exercises": [
 E("e-pess-a", "Le pipeline de l'assistant",
   "Écris `assistant(question, recherche, modele)`. Si la question contient `résilier` ou `réclamation` (sans tenir compte de la casse), renvoie `{\"route\": \"humain\", \"reponse\": \"Je transmets ta demande à un conseiller.\", \"sources\": []}`. Sinon : récupère les 2 meilleurs `id` avec `recherche(question, 2)`, construis un prompt qui contient la question et le texte de ces documents (cherche-les dans `DOCS`), appelle `modele(prompt)` et renvoie `{\"route\": \"rag\", \"reponse\": ..., \"sources\": [les 2 id]}`.",
   "from sklearn.feature_extraction.text import TfidfVectorizer\nfrom sklearn.metrics.pairwise import cosine_similarity\nfrom cloudsync import DOCS\n\nvect = TfidfVectorizer()\nmat = vect.fit_transform([d[\"titre\"] + \". \" + d[\"texte\"] for d in DOCS])\n\ndef recherche(question, k):\n    s = cosine_similarity(vect.transform([question]), mat)[0]\n    return [DOCS[i][\"id\"] for i in s.argsort()[::-1][:k]]\n\ndef modele_test(prompt):\n    return \"Réponse fondée sur \" + str(prompt.count(\"[\")) + \" documents.\"\n\ndef assistant(question, recherche, modele):\n    pass\n",
   "from sklearn.feature_extraction.text import TfidfVectorizer\nfrom sklearn.metrics.pairwise import cosine_similarity\nfrom cloudsync import DOCS\n\nvect = TfidfVectorizer()\nmat = vect.fit_transform([d[\"titre\"] + \". \" + d[\"texte\"] for d in DOCS])\n\ndef recherche(question, k):\n    s = cosine_similarity(vect.transform([question]), mat)[0]\n    return [DOCS[i][\"id\"] for i in s.argsort()[::-1][:k]]\n\ndef modele_test(prompt):\n    return \"Réponse fondée sur \" + str(prompt.count(\"[\")) + \" documents.\"\n\ndef assistant(question, recherche, modele):\n    q = question.lower()\n    if \"résilier\" in q or \"réclamation\" in q:\n        return {\"route\": \"humain\", \"reponse\": \"Je transmets ta demande à un conseiller.\", \"sources\": []}\n    ids = recherche(question, 2)\n    textes = {d[\"id\"]: d[\"texte\"] for d in DOCS}\n    contexte = \"\\n\".join(f\"[{i}] {textes[i]}\" for i in ids)\n    prompt = f\"Réponds à partir des documents et cite tes sources.\\n\\n{contexte}\\n\\nQuestion : {question}\"\n    return {\"route\": \"rag\", \"reponse\": modele(prompt), \"sources\": ids}\n\nprint(assistant(\"Combien coûte l'offre Plus ?\", recherche, modele_test))\nprint(assistant(\"Je veux RÉSILIER\", recherche, modele_test))\n",
   r'''vus = []
espion = lambda p: vus.append(p) or "ok"
r = assistant("Combien coûte l'offre Pro par mois ?", recherche, espion)
assert r["route"] == "rag" and r["reponse"] == "ok", f"Pour une question de prix, route rag attendue ; tu renvoies {r}."
assert r["sources"] == recherche("Combien coûte l'offre Pro par mois ?", 2), "sources doit contenir les 2 id renvoyés par la recherche."
assert "Combien coûte l'offre Pro" in vus[0] and "11,99" in vus[0], "Le prompt doit contenir la question et le texte des documents retrouvés."
h = assistant("Je souhaite faire une RÉCLAMATION", recherche, espion)
assert h == {"route": "humain", "reponse": "Je transmets ta demande à un conseiller.", "sources": []}, f"Les réclamations vont à un humain ; tu renvoies {h}."
assert len(vus) == 1, "Quand la demande part vers un humain, le modèle ne doit pas être appelé."
''',
   "Commence par le test de routage (question.lower()). Pour le texte des documents, un dictionnaire id → texte est pratique."),
 E("e-pess-b", "Le tableau de bord d'évaluation",
   "En réutilisant ton `assistant` (recopie-le avec `recherche`), calcule sur `QUESTIONS_TEST` : `taux_sources`, la proportion de questions dont la réponse cite au moins un document pertinent (dans `sources`), et `taux_humain`, la proportion de questions envoyées à un humain.",
   "from sklearn.feature_extraction.text import TfidfVectorizer\nfrom sklearn.metrics.pairwise import cosine_similarity\nfrom cloudsync import DOCS, QUESTIONS_TEST\n\nvect = TfidfVectorizer()\nmat = vect.fit_transform([d[\"titre\"] + \". \" + d[\"texte\"] for d in DOCS])\n\ndef recherche(question, k):\n    s = cosine_similarity(vect.transform([question]), mat)[0]\n    return [DOCS[i][\"id\"] for i in s.argsort()[::-1][:k]]\n\nmodele_test = lambda prompt: \"ok\"\n\n# recopie ta fonction assistant ici\n",
   "from sklearn.feature_extraction.text import TfidfVectorizer\nfrom sklearn.metrics.pairwise import cosine_similarity\nfrom cloudsync import DOCS, QUESTIONS_TEST\n\nvect = TfidfVectorizer()\nmat = vect.fit_transform([d[\"titre\"] + \". \" + d[\"texte\"] for d in DOCS])\n\ndef recherche(question, k):\n    s = cosine_similarity(vect.transform([question]), mat)[0]\n    return [DOCS[i][\"id\"] for i in s.argsort()[::-1][:k]]\n\nmodele_test = lambda prompt: \"ok\"\n\ndef assistant(question, recherche, modele):\n    q = question.lower()\n    if \"résilier\" in q or \"réclamation\" in q:\n        return {\"route\": \"humain\", \"reponse\": \"Je transmets ta demande à un conseiller.\", \"sources\": []}\n    ids = recherche(question, 2)\n    textes = {d[\"id\"]: d[\"texte\"] for d in DOCS}\n    contexte = \"\\n\".join(f\"[{i}] {textes[i]}\" for i in ids)\n    return {\"route\": \"rag\", \"reponse\": modele(f\"{contexte}\\n\\nQuestion : {question}\"), \"sources\": ids}\n\nresultats = [(q, assistant(q[\"question\"], recherche, modele_test)) for q in QUESTIONS_TEST]\ntaux_sources = sum(any(p in r[\"sources\"] for p in q[\"pertinents\"]) for q, r in resultats) / len(resultats)\ntaux_humain = sum(r[\"route\"] == \"humain\" for _, r in resultats) / len(resultats)\nprint(taux_sources, taux_humain)\n",
   r'''res = [(q, assistant(q["question"], recherche, lambda p: "ok")) for q in QUESTIONS_TEST]
exp_s = sum(any(p in r["sources"] for p in q["pertinents"]) for q, r in res) / len(res)
exp_h = sum(r["route"] == "humain" for _, r in res) / len(res)
assert abs(taux_sources - exp_s) < 1e-9, f"taux_sources vaut {taux_sources}, j'attendais {exp_s}."
assert abs(taux_humain - exp_h) < 1e-9 and exp_h == 1 / 8, f"taux_humain vaut {taux_humain} ; une question sur 8 parle de résiliation."
''',
   "Construis la liste des (question, résultat), puis deux moyennes de booléens."),
],
"tasks": [
  "Remplacer le faux modèle par le vrai LLM dans une cellule de la leçon RAG et comparer les réponses",
  "Construire la même chaîne dans n8n (Webhook → Code → modèle de langage → réponse)",
  "Préparer 5 diapositives de démo avec Gamma : problème, architecture, démo, évaluation, limites",
  "Publier le code et une vidéo de démo de 2 minutes sur GitHub",
]},
]

QUIZZES = {
"quiz-gen": {"title": "Quiz · LLM, prompts et tokens", "questions": [
 {"q": "Comment un LLM génère-t-il du texte ?", "options": ["Il cherche la réponse dans une base de données", "Il prédit un token à la fois, à partir de probabilités", "Il recopie des phrases apprises par cœur", "Il génère toute la phrase d'un coup"], "answer": 1,
  "explain": "Un LLM est autorégressif : il calcule une distribution de probabilités sur le token suivant, en choisit un, et recommence."},
 {"q": "Que se passe-t-il quand on baisse la température vers 0 ?", "options": ["Les réponses deviennent plus créatives", "Le modèle choisit presque toujours le token le plus probable", "Le modèle répond plus vite", "Le contexte s'agrandit"], "answer": 1,
  "explain": "La distribution devient très piquée : la sortie est plus stable et plus déterministe."},
 {"q": "Qu'est-ce qu'une hallucination ?", "options": ["Un bug d'affichage", "Une réponse fausse mais formulée avec assurance", "Un refus de répondre", "Une réponse trop longue"], "answer": 1,
  "explain": "Le modèle produit un texte plausible sans vérifier les faits : il faut l'encadrer (RAG, vérifications, citations)."},
 {"q": "Que contient la fenêtre de contexte ?", "options": ["Seulement la question", "Le prompt système, l'historique, les documents ajoutés et la réponse", "Les poids du modèle", "Les données d'entraînement"], "answer": 1,
  "explain": "Tout ce que le modèle lit et écrit en une fois doit tenir dans la fenêtre de contexte, réponse comprise."},
 {"q": "Pourquoi utiliser des exemples (few-shot) dans un prompt ?", "options": ["Pour réduire le coût", "Pour montrer précisément le format ou le style attendu", "Pour entraîner le modèle", "C'est obligatoire"], "answer": 1,
  "explain": "Les exemples sont le moyen le plus fiable d'imposer un format ou un ton. Le modèle n'est pas réentraîné pour autant."},
 {"q": "Un LLM répond avec du texte autour du JSON demandé. Que fait ton code ?", "options": ["Il plante", "Il extrait et valide le JSON, et gère l'erreur proprement", "Il ignore la réponse", "Il redémarre le serveur"], "answer": 1,
  "explain": "On ne fait jamais confiance à la sortie brute : extraction, validation des clés et des valeurs, gestion d'erreur."},
 {"q": "Comment fonctionne le découpage BPE ?", "options": ["Il coupe les mots en syllabes", "Il fusionne itérativement les paires de symboles les plus fréquentes", "Il coupe tous les 4 caractères", "Il utilise un dictionnaire"], "answer": 1,
  "explain": "Les séquences fréquentes deviennent un seul token ; les mots rares restent découpés en morceaux."},
 {"q": "Une API facture 3 € par million de tokens en entrée. Combien coûtent 20 000 requêtes de 1 500 tokens en entrée ?", "options": ["9 €", "90 €", "0,9 €", "900 €"], "answer": 1,
  "explain": "20 000 × 1 500 = 30 millions de tokens, × 3 € par million = 90 €."},
]},
"quiz-agents": {"title": "Quiz · Agents, évaluation, n8n et RAG", "questions": [
 {"q": "Quelle est la différence entre un agent et un workflow ?", "options": ["Aucune", "Le workflow suit des étapes fixées par le développeur ; l'agent décide lui-même de ses étapes", "Un agent n'utilise pas de LLM", "Un workflow est toujours plus lent"], "answer": 1,
  "explain": "Le workflow est prévisible ; l'agent est flexible mais plus difficile à fiabiliser."},
 {"q": "Quand le modèle demande d'appeler un outil, qui exécute la fonction ?", "options": ["Le modèle lui-même", "Ton code, qui renvoie ensuite le résultat au modèle", "Le navigateur de l'utilisateur", "Personne"], "answer": 1,
  "explain": "Le modèle ne fait que demander l'appel ; ton application l'exécute, en validant les arguments."},
 {"q": "Pourquoi limiter le nombre d'étapes d'un agent ?", "options": ["Pour la lisibilité", "Pour éviter les boucles infinies et maîtriser le coût", "Parce que les API l'imposent", "Ce n'est pas utile"], "answer": 1,
  "explain": "Un agent peut tourner en rond : une limite garantit l'arrêt et borne le coût."},
 {"q": "Quel motif utiliser pour envoyer chaque ticket vers un traitement spécialisé ?", "options": ["La parallélisation", "Le routage", "L'évaluateur-optimiseur", "Le fine-tuning"], "answer": 1,
  "explain": "Le routage classe la demande puis l'oriente vers le prompt et les outils adaptés."},
 {"q": "Pour un assistant de triage médical, quelle métrique surveiller en priorité ?", "options": ["L'exactitude globale", "Le rappel sur la classe « urgent »", "La longueur des réponses", "Le nombre de tokens"], "answer": 1,
  "explain": "Rater une urgence coûte beaucoup plus cher qu'une fausse alerte : on veut un rappel élevé sur les urgences."},
 {"q": "Que faut-il vérifier avant de faire confiance à un LLM juge ?", "options": ["Sa vitesse", "Que ses notes concordent avec des notes humaines sur un échantillon", "Son prix", "Rien"], "answer": 1,
  "explain": "Un juge automatique peut être biaisé : on le calibre contre des évaluations humaines."},
 {"q": "Dans n8n, comment les données circulent-elles entre les nœuds ?", "options": ["En fichiers CSV", "Sous forme d'une liste d'items, chacun avec un champ json", "En SQL", "En variables globales"], "answer": 1,
  "explain": "Chaque nœud reçoit et renvoie une liste d'items {json: {...}}."},
 {"q": "Que mesure le rappel@k d'un système RAG ?", "options": ["La qualité du style", "La proportion de questions dont un document pertinent est dans les k premiers résultats", "Le nombre de documents indexés", "La vitesse de la recherche"], "answer": 1,
  "explain": "Si la recherche ne retrouve pas le bon document, le LLM ne peut pas bien répondre : on mesure cette étape à part."},
]},
}
