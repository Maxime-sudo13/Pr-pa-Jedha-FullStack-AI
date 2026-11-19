"""Lead · Gouvernance des données, informatique pour l'IA, infrastructure et orchestration (vague 7)."""

def E(id, title, prompt, starter, solution, check, hint):
    return {"id": id, "title": title, "prompt": prompt, "starter": starter, "solution": solution, "check": check, "hint": hint}

CLIENTS = r'''import numpy as np
import pandas as pd

clients = pd.DataFrame({
    "id": [1, 2, 3, 4, 4, 6, 7, 8],
    "email": ["ana@mail.fr", "bob@mail", None, "dee@mail.fr", "dee@mail.fr", "eli@mail.fr", None, "gus@mail.fr"],
    "age": [34, 17, 52, 41, 41, 230, 29, np.nan],
    "pays": ["FR", "FR", "BE", "XX", "XX", "FR", "DE", "FR"],
})
'''

LESSONS = [
# ================================================================ Gouvernance
{"id": "l-gouv", "title": "Gouvernance et qualité des données", "minutes": 90,
"body": r'''
Un modèle n'est jamais meilleur que ses données. À l'échelle d'une entreprise, la question n'est plus « mon jeu de données est-il propre ? », mais « qui est responsable de quelles données, avec quelle qualité, qui y a accès, et qu'a-t-on le droit d'en faire ? ». C'est la **gouvernance des données**, et c'est le premier sujet d'un Lead AI.

## Les rôles

| Rôle | Responsabilité |
| --- | --- |
| **Propriétaire** (*data owner*) | Un responsable métier : il décide de l'usage et des accès |
| **Intendant** (*data steward*) | Il veille à la qualité, aux définitions, à la documentation |
| **Ingénieur de données** | Il construit et maintient les flux (ETL, entrepôt) |
| **DPO** | Le délégué à la protection des données : la conformité au RGPD |

## Les dimensions de la qualité

- **Complétude** : quelle part des valeurs est renseignée ?
- **Unicité** : y a-t-il des doublons ?
- **Validité** : les valeurs respectent-elles les règles (un âge entre 0 et 120, un code pays existant) ?
- **Cohérence** : la même information est-elle identique d'un système à l'autre ?
- **Fraîcheur** : les données sont-elles à jour ?

```python
import numpy as np
import pandas as pd
clients = pd.DataFrame({"id": [1, 2, 3, 3], "age": [34, 230, np.nan, np.nan], "pays": ["FR", "XX", "BE", "BE"]})
print("complétude :", clients.notna().mean().round(2).to_dict())
print("doublons   :", clients.duplicated().sum())
print("âges invalides :", (~clients["age"].dropna().between(0, 120)).sum())
```

## Les contrats de données

Un **contrat de données** est un accord écrit entre l'équipe qui produit une table et celles qui la consomment : colonnes, types, valeurs autorisées, fraîcheur, et qui prévenir en cas de changement. Il est vérifié automatiquement à chaque chargement, et un chargement non conforme est bloqué **avant** d'atteindre le modèle. Des outils comme **Great Expectations**, **Soda** ou **dbt tests** font ce travail.

## Les données personnelles

Le RGPD (leçon Réglementation) impose de savoir où sont les **données personnelles**, de limiter leur usage à une finalité, et de les protéger. En pratique :

- **Classer** chaque colonne : publique, interne, confidentielle, personnelle.
- **Minimiser** : ne collecter et ne garder que ce qui sert.
- **Pseudonymiser** ou **masquer** : remplacer un e-mail par un identifiant, retirer les numéros de téléphone des textes avant de les envoyer à un LLM.
- **Tracer les accès** : qui a lu quoi, et quand.

> **À retenir** : des rôles clairs (propriétaire, intendant), cinq dimensions de qualité mesurées automatiquement, des contrats entre producteurs et consommateurs, et un inventaire des données personnelles, masquées dès que possible.
''',
"exercises": [
 E("e-gv-a", "Un rapport de qualité",
   "Écris `rapport_qualite(df, regles)` : `regles` associe un nom de colonne à une fonction qui renvoie True si **une** valeur est valide. Renvoie un dictionnaire avec `completude` (dictionnaire colonne → part de valeurs non nulles, arrondie à 3 décimales), `doublons` (nombre de lignes entièrement dupliquées) et `invalides` (dictionnaire colonne → nombre de valeurs **non nulles** qui ne respectent pas la règle, pour les colonnes de `regles`).",
   CLIENTS + r'''
regles = {
    "age": lambda v: 0 <= v <= 120,
    "pays": lambda v: v in {"FR", "BE", "DE", "ES", "IT"},
    "email": lambda v: "@" in v and "." in v.split("@")[-1],
}

def rapport_qualite(df, regles):
    pass
''',
   CLIENTS + r'''
regles = {
    "age": lambda v: 0 <= v <= 120,
    "pays": lambda v: v in {"FR", "BE", "DE", "ES", "IT"},
    "email": lambda v: "@" in v and "." in v.split("@")[-1],
}

def rapport_qualite(df, regles):
    return {
        "completude": {c: round(float(df[c].notna().mean()), 3) for c in df.columns},
        "doublons": int(df.duplicated().sum()),
        "invalides": {c: int((~df[c].dropna().map(f).astype(bool)).sum()) for c, f in regles.items()},
    }

rapport_qualite(clients, regles)
''',
   r'''r = rapport_qualite(clients, regles)
assert isinstance(r, dict) and set(r) == {"completude", "doublons", "invalides"}, "Le rapport doit contenir completude, doublons et invalides."
assert r["completude"] == {"id": 1.0, "email": 0.75, "age": 0.875, "pays": 1.0}, f"Complétude attendue : id 1.0, email 0.75, age 0.875, pays 1.0 ; tu as {r['completude']}."
assert r["doublons"] == 1, "Il y a une ligne entièrement dupliquée (le client 4)."
assert r["invalides"] == {"age": 1, "pays": 2, "email": 1}, f"Invalides attendus : age 1 (230), pays 2 (XX deux fois), email 1 (bob@mail) ; tu as {r['invalides']}. Ne compte que les valeurs non nulles."
''',
   "df[c].notna().mean() pour la complétude ; df.duplicated().sum() pour les doublons ; df[c].dropna().map(regle) pour tester chaque valeur."),
 E("e-gv-b", "Masquer les données personnelles",
   "Écris `masquer(texte)` qui remplace : les adresses e-mail par `[EMAIL]` ; les numéros de téléphone français par `[TEL]` (10 chiffres commençant par 0, ou `+33` suivi de 9 chiffres, éventuellement séparés par des espaces, des points ou des tirets) ; les IBAN français par `[IBAN]` (`FR` suivi de 25 caractères alphanumériques, éventuellement par groupes séparés d'espaces). Utilise le module `re`.",
   r'''import re

def masquer(texte):
    pass
''',
   r'''import re

EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
IBAN = re.compile(r"\bFR\d{2}(?:\s?[0-9A-Z]{4}){5}\s?[0-9A-Z]{3}\b")
TEL = re.compile(r"(?:\+33[\s.-]?[1-9]|\b0[1-9])(?:[\s.-]?\d{2}){4}\b")

def masquer(texte):
    texte = EMAIL.sub("[EMAIL]", texte)
    texte = IBAN.sub("[IBAN]", texte)
    return TEL.sub("[TEL]", texte)

print(masquer("Contact : marie.durand@exemple.fr, 06 12 34 56 78, IBAN FR76 3000 6000 0112 3456 7890 189."))
''',
   r'''cas = {
    "Écris à jean.dupont+test@mail.example.com demain": "Écris à [EMAIL] demain",
    "Appelle le 06 12 34 56 78.": "Appelle le [TEL].",
    "ou le 01.23.45.67.89 ou le 0612345678": "ou le [TEL] ou le [TEL]",
    "Depuis l'étranger : +33 6 12 34 56 78": "Depuis l'étranger : [TEL]",
    "IBAN : FR76 3000 6000 0112 3456 7890 189": "IBAN : [IBAN]",
    "IBAN collé FR7630006000011234567890189 fin": "IBAN collé [IBAN] fin",
    "Commande 2024 de 3 articles, réf. 12345": "Commande 2024 de 3 articles, réf. 12345",
}
for entree, attendu in cas.items():
    obtenu = masquer(entree)
    assert obtenu == attendu, f"masquer({entree!r}) devrait donner {attendu!r} ; tu obtiens {obtenu!r}."
''',
   "Trois expressions régulières. Pour le téléphone : (?:\\+33[\\s.-]?[1-9]|\\b0[1-9]) suivi de 4 groupes (?:[\\s.-]?\\d{2}). Remplace l'IBAN avant le téléphone."),
 E("e-gv-c", "Vérifier un contrat de données",
   "Écris `verifier_contrat(df, contrat)` qui renvoie la liste des violations, dans l'ordre des colonnes du contrat, avec exactement ces messages : `\"<col> : colonne manquante\"` (et rien d'autre pour cette colonne) ; `\"<col> : <n> valeurs nulles\"` si `nullable` vaut False et qu'il y a des nulls ; `\"<col> : <n> valeurs hors de [<min>, <max>]\"` si `min`/`max` sont donnés (sur les valeurs non nulles) ; `\"<col> : <n> valeurs non autorisées\"` si `valeurs` est donné (sur les valeurs non nulles).",
   CLIENTS + r'''
contrat = {
    "id": {"nullable": False},
    "email": {"nullable": False},
    "age": {"nullable": True, "min": 18, "max": 120},
    "pays": {"nullable": False, "valeurs": ["FR", "BE", "DE"]},
    "date_inscription": {"nullable": False},
}

def verifier_contrat(df, contrat):
    pass
''',
   CLIENTS + r'''
contrat = {
    "id": {"nullable": False},
    "email": {"nullable": False},
    "age": {"nullable": True, "min": 18, "max": 120},
    "pays": {"nullable": False, "valeurs": ["FR", "BE", "DE"]},
    "date_inscription": {"nullable": False},
}

def verifier_contrat(df, contrat):
    erreurs = []
    for col, regle in contrat.items():
        if col not in df.columns:
            erreurs.append(f"{col} : colonne manquante")
            continue
        n_nuls = int(df[col].isna().sum())
        if not regle.get("nullable", True) and n_nuls:
            erreurs.append(f"{col} : {n_nuls} valeurs nulles")
        v = df[col].dropna()
        if "min" in regle or "max" in regle:
            lo, hi = regle.get("min", float("-inf")), regle.get("max", float("inf"))
            n = int((~v.between(lo, hi)).sum())
            if n:
                erreurs.append(f"{col} : {n} valeurs hors de [{regle.get('min')}, {regle.get('max')}]")
        if "valeurs" in regle:
            n = int((~v.isin(regle["valeurs"])).sum())
            if n:
                erreurs.append(f"{col} : {n} valeurs non autorisées")
    return erreurs

verifier_contrat(clients, contrat)
''',
   r'''r = verifier_contrat(clients, contrat)
attendu = ["email : 2 valeurs nulles", "age : 2 valeurs hors de [18, 120]", "pays : 2 valeurs non autorisées", "date_inscription : colonne manquante"]
assert r == attendu, f"Violations attendues :\n{attendu}\nTu obtiens :\n{r}"
assert verifier_contrat(clients, {"id": {"nullable": False}}) == [], "Un contrat respecté ne donne aucune violation."
''',
   "Pour chaque colonne : d'abord la présence (continue si absente), puis les nulls, puis min/max avec between, puis valeurs avec isin, toujours sur df[col].dropna()."),
]},
# ================================================================ Catalogue et lignage
{"id": "l-catalog", "title": "Catalogue de données et lignage", "minutes": 70,
"body": r'''
Dans une entreprise, il y a des milliers de tables. Un analyste cherche « le chiffre d'affaires par client » : laquelle utiliser ? Qui la maintient ? Est-elle à jour ? Contient-elle des données personnelles ? Le **catalogue de données** répond à ces questions, comme un moteur de recherche interne pour les données.

## Ce que contient un catalogue

- Les **métadonnées techniques** : schéma, types, volumétrie, date de mise à jour, collectées automatiquement depuis les bases, l'entrepôt et les outils (dbt, Airflow, Tableau).
- Les **métadonnées métier** : description, glossaire (« client actif = au moins un achat sur 12 mois »), propriétaire, tags (`PII`, `certifié`).
- Le **lignage** (*lineage*) : d'où vient chaque table et ce qui en dépend, jusqu'aux tableaux de bord et aux modèles.
- La **qualité** : les résultats des contrôles de la leçon précédente.

Les outils open source les plus utilisés sont **OpenMetadata** (celui du programme) et **DataHub** ; côté cloud, AWS Glue Data Catalog, Google Dataplex ou Microsoft Purview.

## Pourquoi le lignage est si utile

```pycode
crm.clients ──┐
              ├──▶ entrepot.clients_propres ──▶ marts.ventes_par_client ──▶ dashboard.ca_mensuel
erp.commandes ┘                                         └──────────────────▶ modele.churn
```

- **Analyse d'impact** : avant de renommer une colonne de `crm.clients`, on voit immédiatement qu'un tableau de bord et un modèle en dépendent.
- **Analyse de cause** : un tableau de bord affiche un chiffre faux ? On remonte le lignage jusqu'à la source fautive.
- **Conformité** : un client demande la suppression de ses données (droit à l'effacement) ; le lignage montre toutes les tables où elles ont été copiées.

> **À retenir** : un catalogue = métadonnées techniques + métier + lignage + qualité. Le lignage est un graphe orienté : on le parcourt vers l'aval pour l'impact, vers l'amont pour la cause.
''',
"tasks": [
  "Lancer OpenMetadata avec Docker (guide « Quickstart ») et y connecter une base PostgreSQL ou un fichier CSV",
  "Ajouter une description, un propriétaire et un tag PII à une table",
  "Observer le lignage généré automatiquement à partir d'un projet dbt ou d'un DAG Airflow",
],
"exercises": [
 E("e-cat-a", "Parcourir le lignage",
   "Le lignage est un dictionnaire : chaque actif pointe vers la liste des actifs construits à partir de lui. Écris `en_aval(lignage, actif)`, l'ensemble de tous les actifs qui dépendent de `actif`, directement ou indirectement, et `en_amont(lignage, actif)`, l'ensemble de toutes ses sources. Puis `impact(lignage, actif)` : la liste triée des actifs en aval dont le nom commence par `dashboard.` ou `modele.`.",
   r'''lignage = {
    "crm.clients": ["entrepot.clients_propres"],
    "erp.commandes": ["entrepot.commandes_propres"],
    "entrepot.clients_propres": ["marts.ventes_par_client", "marts.segments"],
    "entrepot.commandes_propres": ["marts.ventes_par_client"],
    "marts.ventes_par_client": ["dashboard.ca_mensuel", "modele.churn"],
    "marts.segments": ["dashboard.marketing"],
}

def en_aval(lignage, actif):
    pass

def en_amont(lignage, actif):
    pass

def impact(lignage, actif):
    pass
''',
   r'''lignage = {
    "crm.clients": ["entrepot.clients_propres"],
    "erp.commandes": ["entrepot.commandes_propres"],
    "entrepot.clients_propres": ["marts.ventes_par_client", "marts.segments"],
    "entrepot.commandes_propres": ["marts.ventes_par_client"],
    "marts.ventes_par_client": ["dashboard.ca_mensuel", "modele.churn"],
    "marts.segments": ["dashboard.marketing"],
}

def en_aval(lignage, actif):
    vus, a_voir = set(), list(lignage.get(actif, []))
    while a_voir:
        x = a_voir.pop()
        if x not in vus:
            vus.add(x)
            a_voir.extend(lignage.get(x, []))
    return vus

def en_amont(lignage, actif):
    inverse = {}
    for src, dsts in lignage.items():
        for d in dsts:
            inverse.setdefault(d, []).append(src)
    return en_aval(inverse, actif)

def impact(lignage, actif):
    return sorted(a for a in en_aval(lignage, actif) if a.startswith(("dashboard.", "modele.")))

print(impact(lignage, "crm.clients"))
print(sorted(en_amont(lignage, "modele.churn")))
''',
   r'''assert en_aval(lignage, "erp.commandes") == {"entrepot.commandes_propres", "marts.ventes_par_client", "dashboard.ca_mensuel", "modele.churn"}, "en_aval doit suivre le lignage jusqu'au bout."
assert en_aval(lignage, "dashboard.ca_mensuel") == set(), "Un tableau de bord n'a rien en aval."
assert en_amont(lignage, "modele.churn") == {"marts.ventes_par_client", "entrepot.clients_propres", "entrepot.commandes_propres", "crm.clients", "erp.commandes"}, "en_amont doit remonter toutes les sources : inverse d'abord le graphe."
assert impact(lignage, "crm.clients") == ["dashboard.ca_mensuel", "dashboard.marketing", "modele.churn"], "impact : les tableaux de bord et modèles en aval, triés."
cycle = {"a": ["b"], "b": ["a"]}
assert en_aval(cycle, "a") == {"a", "b"}, "Avec un cycle, le parcours doit s'arrêter : garde un ensemble des actifs déjà vus."
''',
   "Un parcours avec une pile et un ensemble « vus ». Pour remonter, construis le graphe inverse, puis réutilise en_aval."),
 E("e-cat-b", "Classer automatiquement les colonnes",
   "Écris `classer(df)` qui renvoie un dictionnaire colonne → `\"PII\"` ou `\"interne\"`. Une colonne est `PII` si son nom (en minuscules) contient l'un des mots de `MOTS_PII`, **ou** si plus de la moitié de ses valeurs non nulles (converties en texte) ressemblent à un e-mail (`EMAIL.fullmatch`) ou à un numéro de téléphone (`TEL.fullmatch`).",
   r'''import re
import pandas as pd

MOTS_PII = ["nom", "prenom", "email", "mail", "tel", "adresse", "naissance", "iban"]
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
TEL = re.compile(r"(?:\+33|0)[1-9](?:[\s.-]?\d{2}){4}")

df = pd.DataFrame({
    "client_id": [1, 2, 3],
    "nom_complet": ["Ana Ruiz", "Bob Lee", "Cléo Martin"],
    "contact": ["ana@mail.fr", "bob@mail.fr", None],
    "commentaire": ["rappeler", "06 12 34 56 78", "ok"],
    "montant": [12.5, 40.0, 7.2],
    "joignable": ["0612345678", "07 11 22 33 44", "+33 6 98 76 54 32"],
})

def classer(df):
    pass
''',
   r'''import re
import pandas as pd

MOTS_PII = ["nom", "prenom", "email", "mail", "tel", "adresse", "naissance", "iban"]
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
TEL = re.compile(r"(?:\+33|0)[1-9](?:[\s.-]?\d{2}){4}")

df = pd.DataFrame({
    "client_id": [1, 2, 3],
    "nom_complet": ["Ana Ruiz", "Bob Lee", "Cléo Martin"],
    "contact": ["ana@mail.fr", "bob@mail.fr", None],
    "commentaire": ["rappeler", "06 12 34 56 78", "ok"],
    "montant": [12.5, 40.0, 7.2],
    "joignable": ["0612345678", "07 11 22 33 44", "+33 6 98 76 54 32"],
})

def classer(df):
    res = {}
    for c in df.columns:
        par_nom = any(m in c.lower() for m in MOTS_PII)
        valeurs = df[c].dropna().astype(str)
        part = valeurs.map(lambda v: bool(EMAIL.fullmatch(v) or TEL.fullmatch(v))).mean() if len(valeurs) else 0
        res[c] = "PII" if par_nom or part > 0.5 else "interne"
    return res

classer(df)
''',
   r'''r = classer(df)
attendu = {"client_id": "interne", "nom_complet": "PII", "contact": "PII", "commentaire": "interne", "montant": "interne", "joignable": "PII"}
assert r == attendu, f"Classement attendu : {attendu} ; tu as {r}."
assert classer(pd.DataFrame({"Email_Pro": [None, None]})) == {"Email_Pro": "PII"}, "Le nom de colonne se compare en minuscules."
''',
   "Pour chaque colonne : any(m in c.lower() for m in MOTS_PII), puis la part des valeurs (dropna().astype(str)) qui passent EMAIL.fullmatch ou TEL.fullmatch."),
]},
# ================================================================ GPU
{"id": "l-gpu", "title": "GPU : architecture et optimisation", "minutes": 100,
"body": r'''
Le GPU est la ressource la plus chère d'un projet d'IA : une carte H100 coûte autour de 30 000 €, ou 2 à 4 € de l'heure dans le cloud. Un Lead AI doit savoir ce qui la limite, pour choisir le bon matériel et ne pas payer des GPU qui attendent.

## Pourquoi un GPU

Un processeur (CPU) a quelques dizaines de cœurs puissants. Un GPU en a des **milliers** de plus simples, plus des **Tensor Cores** spécialisés dans le produit matriciel en basse précision. Or un réseau de neurones, c'est presque uniquement des produits matriciels.

| Carte | Calcul bf16 (dense) | Mémoire | Bande passante |
| --- | --- | --- | --- |
| NVIDIA T4 (Colab gratuit) | 65 TFLOPS | 16 Go | 320 Go/s |
| NVIDIA A100 | 312 TFLOPS | 80 Go | 2 000 Go/s |
| NVIDIA H100 SXM | 989 TFLOPS | 80 Go | 3 350 Go/s |

## Calcul ou mémoire : le modèle du toit

Chaque opération lit des données en mémoire, puis calcule. Son **intensité arithmétique** est le nombre d'opérations faites par octet lu. Le **modèle du toit** (*roofline*) en déduit la performance atteignable :

```latex
\text{perf} = \min\big(\text{pic de calcul},\ \text{intensité} \times \text{bande passante}\big)
```

Sous un certain seuil d'intensité (environ 300 opérations par octet sur H100), on est **limité par la mémoire** : le GPU attend les données. Au-dessus, on est **limité par le calcul**.

```viz roofline
```

- Un grand produit matriciel (entraînement, préremplissage d'un LLM) a une forte intensité : il utilise vraiment le GPU.
- Un produit matrice × vecteur (décodage d'un LLM, un token à la fois) a une intensité proche de 1 : il est limité par la mémoire. C'est pourquoi on regroupe les requêtes (vague 6) et pourquoi la quantification accélère l'inférence : moins d'octets à lire.

## Les leviers d'optimisation

- **Précision mixte** (bf16 ou fp16) : 2 fois moins de mémoire, et les Tensor Cores. En PyTorch : `torch.autocast("cuda", dtype=torch.bfloat16)`.
- **Taille de lot** : la plus grande qui tient en mémoire, pour augmenter l'intensité.
- **Fusion d'opérations** : `torch.compile` regroupe plusieurs petites opérations pour éviter des allers-retours en mémoire ; FlashAttention fait de même pour l'attention.
- **Ne pas affamer le GPU** : un chargement de données trop lent (`DataLoader` avec `num_workers` et `pin_memory`) laisse le GPU à 30 % d'utilisation.
- **Mesurer** : `nvidia-smi` pour l'utilisation et la mémoire, le profileur PyTorch pour savoir où passe le temps.

## Estimer un entraînement

Entraîner un Transformer coûte environ **6 opérations par paramètre et par token** (2 pour la passe avant, 4 pour la rétropropagation). Le taux d'utilisation réel, la **MFU** (*model FLOPs utilization*), dépasse rarement 40 à 50 %.

```latex
\text{durée} \approx \frac{6\, N\, D}{n_{\text{GPU}} \times \text{pic} \times \text{MFU}}
```

> **À retenir** : le GPU est limité soit par le calcul, soit par la mémoire. Entraînement et préremplissage : calcul. Décodage : mémoire. Précision mixte, grands lots, fusion d'opérations et chargement de données efficace. Coût d'un entraînement ≈ 6 N D opérations.
''',
"tasks": [
  "Sur Google Colab avec un GPU T4, lancer nvidia-smi et repérer la mémoire et l'utilisation",
  "Mesurer le temps d'un produit de matrices 4096 × 4096 avec PyTorch en float32 puis en bfloat16 ou float16",
  "Entraîner le CNN de la vague 4 avec et sans torch.autocast, et comparer la durée d'une époque",
],
"exercises": [
 E("e-gpu-a", "Le modèle du toit",
   "Écris `intensite_matmul(m, n, k, octets=2)` : l'intensité arithmétique du produit d'une matrice (m, k) par une matrice (k, n), qui fait 2·m·n·k opérations et lit ou écrit (m·k + k·n + m·n) nombres de `octets` octets. Puis `regime(intensite, pic_tflops, bande_go_s)` qui renvoie `\"calcul\"` si l'intensité atteint le seuil pic / bande passante (attention aux unités : téra = 1e12, giga = 1e9), sinon `\"mémoire\"`. Enfin `perf_tflops(intensite, pic_tflops, bande_go_s)`, la performance atteignable en TFLOPS selon le modèle du toit.",
   r'''def intensite_matmul(m, n, k, octets=2):
    pass

def regime(intensite, pic_tflops, bande_go_s):
    pass

def perf_tflops(intensite, pic_tflops, bande_go_s):
    pass
''',
   r'''def intensite_matmul(m, n, k, octets=2):
    return 2 * m * n * k / (octets * (m * k + k * n + m * n))

def regime(intensite, pic_tflops, bande_go_s):
    seuil = pic_tflops * 1e12 / (bande_go_s * 1e9)
    return "calcul" if intensite >= seuil else "mémoire"

def perf_tflops(intensite, pic_tflops, bande_go_s):
    return min(pic_tflops, intensite * bande_go_s * 1e9 / 1e12)

H100 = (989, 3350)
for nom, (m, n, k) in {"entraînement (4096³)": (4096, 4096, 4096), "décodage (matrice × vecteur)": (4096, 1, 4096)}.items():
    I = intensite_matmul(m, n, k)
    print(f"{nom:30s} intensité {I:7.1f} → {regime(I, *H100):7s} · {perf_tflops(I, *H100):6.1f} TFLOPS")
''',
   r'''I = intensite_matmul(4096, 4096, 4096)
assert abs(I - 4096 / 3) < 1e-9, f"Pour 4096³ en 16 bits, l'intensité vaut 2·4096³ / (2·3·4096²) = 1365,3 ; tu as {I}."
assert abs(intensite_matmul(10, 1, 10, octets=4) - 200 / (4 * 120)) < 1e-12, "Vérifie la formule : 2mnk / (octets × (mk + kn + mn))."
assert regime(I, 989, 3350) == "calcul" and regime(intensite_matmul(4096, 1, 4096), 989, 3350) == "mémoire", "Le grand produit matriciel est limité par le calcul, le produit matrice × vecteur par la mémoire."
assert regime(989e12 / 3350e9, 989, 3350) == "calcul", "Au seuil exact, on considère qu'on atteint le calcul (>=)."
assert perf_tflops(I, 989, 3350) == 989, "Au-dessus du seuil, la performance plafonne au pic."
assert abs(perf_tflops(1.0, 989, 3350) - 3.35) < 1e-9, "Avec une intensité de 1, on atteint 1 × 3 350 Go/s = 3,35 TFLOPS."
''',
   "Le seuil vaut pic_tflops × 1e12 / (bande_go_s × 1e9) opérations par octet. perf = min(pic, intensité × bande) en convertissant la bande en TFLOPS."),
 E("e-gpu-b", "Combien de temps pour entraîner un LLM ?",
   "Écris `duree_jours(n_params, n_tokens, n_gpus, pic_tflops, mfu)` avec la règle des 6·N·D opérations. Puis calcule pour Llama 3 8B (8e9 paramètres, 15e12 tokens) sur 1 024 H100 (989 TFLOPS) à une MFU de 0,4 : `jours`, et `cout_euros`, le coût à 2,50 € par GPU et par heure.",
   r'''def duree_jours(n_params, n_tokens, n_gpus, pic_tflops, mfu):
    pass

jours = None
cout_euros = None
''',
   r'''def duree_jours(n_params, n_tokens, n_gpus, pic_tflops, mfu):
    operations = 6 * n_params * n_tokens
    secondes = operations / (n_gpus * pic_tflops * 1e12 * mfu)
    return secondes / 86400

jours = duree_jours(8e9, 15e12, 1024, 989, 0.4)
cout_euros = jours * 24 * 1024 * 2.5
print(f"{jours:.1f} jours, environ {cout_euros / 1e6:.2f} M€")
''',
   r'''attendu = 6 * 8e9 * 15e12 / (1024 * 989e12 * 0.4) / 86400
assert abs(duree_jours(8e9, 15e12, 1024, 989, 0.4) - attendu) < 1e-9, f"duree_jours doit valoir {attendu:.2f} jours pour Llama 3 8B."
assert abs(duree_jours(1e9, 1e9, 1, 1, 1) - 6e18 / 1e12 / 86400) < 1e-9, "6 × N × D opérations divisées par (GPUs × pic × 1e12 × MFU), puis par 86 400."
assert abs(jours - attendu) < 1e-9, "jours doit utiliser les valeurs de Llama 3 8B."
assert abs(cout_euros - attendu * 24 * 1024 * 2.5) < 1e-3, "cout_euros = jours × 24 h × 1 024 GPU × 2,50 €."
''',
   "6 * n_params * n_tokens opérations ; le débit effectif vaut n_gpus × pic_tflops × 1e12 × mfu opérations par seconde."),
]},
# ================================================================ Kubernetes et Helm
{"id": "l-k8s", "title": "Kubernetes et Helm", "minutes": 110,
"body": r'''
Docker fait tourner un conteneur sur une machine. En production, on veut des dizaines de conteneurs sur des dizaines de machines, qui redémarrent quand ils plantent, se multiplient quand la charge monte, et se mettent à jour sans coupure. C'est le rôle d'un **orchestrateur**, et **Kubernetes** (K8s) est le standard. Les services gérés s'appellent EKS (AWS), GKE (Google) et AKS (Azure).

## Les objets à connaître

| Objet | Rôle |
| --- | --- |
| **Pod** | Un ou plusieurs conteneurs lancés ensemble ; l'unité de base |
| **Deployment** | Maintient N copies identiques d'un pod et gère les mises à jour progressives |
| **Service** | Une adresse stable qui répartit le trafic entre les pods |
| **Ingress** | L'entrée HTTP depuis l'extérieur (domaine, HTTPS, chemins) |
| **ConfigMap** et **Secret** | La configuration et les secrets, injectés en variables d'environnement |
| **HorizontalPodAutoscaler** | Ajoute ou retire des pods selon la charge |
| **Job** et **CronJob** | Une tâche ponctuelle ou planifiée (un entraînement, un scoring de nuit) |

## Un Deployment pour l'API de fraude

```pycode
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fraude-api
spec:
  replicas: 3
  selector:
    matchLabels: {app: fraude-api}
  template:
    metadata:
      labels: {app: fraude-api}
    spec:
      containers:
        - name: fraude-api
          image: 123456789.dkr.ecr.eu-west-3.amazonaws.com/fraude-api:1.2.0
          ports: [{containerPort: 8000}]
          resources:
            requests: {cpu: "500m", memory: "512Mi"}      # ce qui est réservé
            limits:   {cpu: "1",    memory: "1Gi"}        # le maximum autorisé
          readinessProbe:                                  # prêt à recevoir du trafic ?
            httpGet: {path: /sante, port: 8000}
```

On applique ce fichier avec `kubectl apply -f deployment.yaml`. Kubernetes compare en permanence l'**état désiré** (3 copies) à l'**état réel**, et corrige l'écart. C'est le principe central : on décrit le résultat voulu, pas les étapes.

## La montée en charge automatique

```viz hpa
```

L'**HorizontalPodAutoscaler** calcule le nombre de pods nécessaire à partir d'une métrique (CPU, requêtes par seconde, longueur d'une file) :

```latex
\text{replicas} = \left\lceil \text{replicas actuels} \times \frac{\text{valeur mesurée}}{\text{valeur cible}} \right\rceil
```

borné par un minimum et un maximum, avec une tolérance de 10 % pour éviter les oscillations.

## Les GPU dans Kubernetes

Un pod demande un GPU avec `limits: {nvidia.com/gpu: 1}` ; le plugin NVIDIA place le pod sur un nœud qui en a un. Les GPU sont chers : on les met dans un groupe de nœuds séparé, qui monte à zéro quand rien ne tourne.

## Helm : des modèles de manifestes

Écrire des dizaines de fichiers YAML presque identiques (développement, recette, production) est fastidieux. **Helm** est le gestionnaire de paquets de Kubernetes : un **chart** contient des gabarits avec des trous, et un fichier `values.yaml` par environnement les remplit.

```pycode
# templates/deployment.yaml (extrait)
spec:
  replicas: {{ .Values.replicas }}
  containers:
    - image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"

helm install fraude ./chart -f values-prod.yaml
helm upgrade fraude ./chart --set image.tag=1.3.0     # mise à jour progressive
helm rollback fraude 1                                 # retour arrière
```

> **À retenir** : on décrit l'état désiré (Deployment, Service, Ingress), Kubernetes le maintient. Requests et limits pour les ressources, readinessProbe pour le trafic, HPA pour la charge. Helm pour réutiliser les manifestes d'un environnement à l'autre.
''',
"tasks": [
  "Installer kind ou minikube et créer un cluster local",
  "Déployer l'image de l'API de la vague 6 avec un Deployment et un Service, puis l'appeler avec kubectl port-forward",
  "Ajouter un HorizontalPodAutoscaler et générer de la charge pour voir les pods se multiplier",
  "Transformer les manifestes en chart Helm avec un values.yaml par environnement",
],
"exercises": [
 E("e-k8s-a", "Générer un Deployment",
   "Écris `manifeste(nom, image, replicas, cpu, memoire, gpu=0, port=8000)` qui renvoie le dictionnaire d'un Deployment : `apiVersion` `apps/v1`, `kind` `Deployment`, `metadata.name`, `spec.replicas`, `spec.selector.matchLabels` = `{\"app\": nom}`, et `spec.template` avec `metadata.labels` = `{\"app\": nom}` et `spec.containers`, une liste d'un conteneur : `name`, `image`, `ports` = `[{\"containerPort\": port}]`, `resources` avec `requests` et `limits` égaux à `{\"cpu\": cpu, \"memory\": memoire}` (plus `\"nvidia.com/gpu\": gpu` dans `limits` si gpu > 0), et `readinessProbe` = `{\"httpGet\": {\"path\": \"/sante\", \"port\": port}}`.",
   r'''def manifeste(nom, image, replicas, cpu, memoire, gpu=0, port=8000):
    pass
''',
   r'''def manifeste(nom, image, replicas, cpu, memoire, gpu=0, port=8000):
    limits = {"cpu": cpu, "memory": memoire}
    if gpu > 0:
        limits["nvidia.com/gpu"] = gpu
    return {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {"name": nom},
        "spec": {
            "replicas": replicas,
            "selector": {"matchLabels": {"app": nom}},
            "template": {
                "metadata": {"labels": {"app": nom}},
                "spec": {"containers": [{
                    "name": nom,
                    "image": image,
                    "ports": [{"containerPort": port}],
                    "resources": {"requests": {"cpu": cpu, "memory": memoire}, "limits": limits},
                    "readinessProbe": {"httpGet": {"path": "/sante", "port": port}},
                }]},
            },
        },
    }

import json
print(json.dumps(manifeste("fraude-api", "fraude-api:1.2.0", 3, "500m", "512Mi"), indent=2))
''',
   r'''m = manifeste("fraude-api", "reg/fraude-api:1.2.0", 3, "500m", "512Mi")
assert m["apiVersion"] == "apps/v1" and m["kind"] == "Deployment" and m["metadata"] == {"name": "fraude-api"}, "Vérifie apiVersion, kind et metadata.name."
assert m["spec"]["replicas"] == 3 and m["spec"]["selector"] == {"matchLabels": {"app": "fraude-api"}}, "spec.replicas et spec.selector.matchLabels."
t = m["spec"]["template"]
assert t["metadata"]["labels"] == {"app": "fraude-api"}, "Les labels du gabarit doivent correspondre au sélecteur, sinon le Deployment ne trouve pas ses pods."
c = t["spec"]["containers"]
assert isinstance(c, list) and len(c) == 1, "containers est une liste d'un conteneur."
c = c[0]
assert c["name"] == "fraude-api" and c["image"] == "reg/fraude-api:1.2.0" and c["ports"] == [{"containerPort": 8000}], "Vérifie name, image et ports."
assert c["resources"] == {"requests": {"cpu": "500m", "memory": "512Mi"}, "limits": {"cpu": "500m", "memory": "512Mi"}}, "requests et limits avec cpu et memory ; pas de GPU si gpu = 0."
assert c["readinessProbe"] == {"httpGet": {"path": "/sante", "port": 8000}}, "readinessProbe sur /sante."
g = manifeste("llm", "vllm:0.6", 1, "8", "64Gi", gpu=2, port=9000)["spec"]["template"]["spec"]["containers"][0]
assert g["resources"]["limits"]["nvidia.com/gpu"] == 2 and "nvidia.com/gpu" not in g["resources"]["requests"], "Avec gpu > 0, ajoute nvidia.com/gpu dans limits seulement."
assert g["ports"] == [{"containerPort": 9000}] and g["readinessProbe"]["httpGet"]["port"] == 9000, "Le port doit être utilisé partout."
''',
   "Construis le dictionnaire limits à part, ajoute la clé GPU si besoin, puis assemble la structure imbriquée en suivant l'exemple YAML de la leçon."),
 E("e-k8s-b", "L'autoscaler",
   "Écris `replicas_cibles(actuels, mesure, cible, min_r=1, max_r=10, tolerance=0.1)` : si le rapport mesure / cible est à moins de `tolerance` de 1 (inclus), garde `actuels` ; sinon, calcule ⌈actuels × mesure / cible⌉ (avec `math.ceil`). Dans tous les cas, borne le résultat entre `min_r` et `max_r`.",
   r'''import math

def replicas_cibles(actuels, mesure, cible, min_r=1, max_r=10, tolerance=0.1):
    pass
''',
   r'''import math

def replicas_cibles(actuels, mesure, cible, min_r=1, max_r=10, tolerance=0.1):
    rapport = mesure / cible
    voulu = actuels if abs(rapport - 1) <= tolerance else math.ceil(actuels * rapport)
    return max(min_r, min(max_r, voulu))

for cpu in [30, 55, 62, 90, 250]:
    print(f"CPU moyen {cpu} % (cible 60 %) avec 4 pods → {replicas_cibles(4, cpu, 60)} pods")
''',
   r'''assert replicas_cibles(4, 90, 60) == 6, "4 pods à 90 % pour une cible de 60 % : ⌈4 × 1,5⌉ = 6."
assert replicas_cibles(4, 62, 60) == 4, "62 / 60 est dans la tolérance de 10 % : on ne bouge pas."
assert replicas_cibles(4, 65, 60) == 4, "65 / 60 ≈ 1,08 : dans la tolérance, on ne bouge pas."
assert replicas_cibles(4, 70, 60) == 5, "70 / 60 ≈ 1,17 : hors tolérance, ⌈4 × 1,17⌉ = 5."
assert replicas_cibles(4, 30, 60) == 2, "À 30 % pour 60 %, on divise par deux : 2 pods."
assert replicas_cibles(4, 250, 60) == 10, "Le résultat est plafonné à max_r."
assert replicas_cibles(2, 5, 60, min_r=2) == 2, "Le résultat ne descend pas sous min_r."
assert replicas_cibles(3, 61, 60, tolerance=0) == 4, "Avec une tolérance nulle, ⌈3 × 61/60⌉ = 4."
''',
   "rapport = mesure / cible ; si abs(rapport − 1) <= tolerance on garde actuels ; puis max(min_r, min(max_r, …))."),
 E("e-k8s-c", "Un gabarit à la Helm",
   "Écris `rendre(gabarit, valeurs)` qui remplace chaque `{{ .Values.chemin.vers.cle }}` (espaces facultatifs autour) par la valeur correspondante dans le dictionnaire imbriqué `valeurs`, convertie en texte. Si une clé manque, lève une `KeyError` dont le message contient le chemin complet (par exemple `image.tag`). Utilise `re.sub` avec une fonction.",
   r'''import re

def rendre(gabarit, valeurs):
    pass

gabarit = """spec:
  replicas: {{ .Values.replicas }}
  containers:
    - image: "{{ .Values.image.repository }}:{{.Values.image.tag}}"
"""
valeurs = {"replicas": 3, "image": {"repository": "reg/fraude-api", "tag": "1.2.0"}}
''',
   r'''import re

def rendre(gabarit, valeurs):
    def remplacer(m):
        chemin = m.group(1)
        v = valeurs
        for cle in chemin.split("."):
            if not isinstance(v, dict) or cle not in v:
                raise KeyError(f"Valeur manquante : {chemin}")
            v = v[cle]
        return str(v)
    return re.sub(r"\{\{\s*\.Values\.([\w.]+)\s*\}\}", remplacer, gabarit)

gabarit = """spec:
  replicas: {{ .Values.replicas }}
  containers:
    - image: "{{ .Values.image.repository }}:{{.Values.image.tag}}"
"""
valeurs = {"replicas": 3, "image": {"repository": "reg/fraude-api", "tag": "1.2.0"}}
print(rendre(gabarit, valeurs))
''',
   r'''r = rendre(gabarit, valeurs)
assert r is not None and "replicas: 3" in r and '"reg/fraude-api:1.2.0"' in r and "{{" not in r, f"Toutes les valeurs doivent être remplacées ; tu obtiens :\n{r}"
assert rendre("a={{ .Values.x }} b={{.Values.x}}", {"x": True}) == "a=True b=True", "Les espaces autour sont facultatifs, et la valeur est convertie en texte."
try:
    rendre("{{ .Values.image.digest }}", valeurs); ok = False
except KeyError as e:
    ok = "image.digest" in str(e)
assert ok, "Une clé manquante doit lever une KeyError qui nomme le chemin complet."
assert rendre("rien à remplacer", {}) == "rien à remplacer", "Un texte sans gabarit reste inchangé."
''',
   "re.sub(r\"\\{\\{\\s*\\.Values\\.([\\w.]+)\\s*\\}\\}\", fonction, gabarit) : la fonction reçoit l'objet match et suit le chemin m.group(1).split(\".\")."),
]},
# ================================================================ Calcul distribué
{"id": "l-ray", "title": "Calcul distribué : Ray et deep learning distribué", "minutes": 100,
"body": r'''
Quand un calcul ne tient plus sur une machine (trop de données, trop d'hyperparamètres à essayer, un modèle trop gros pour un GPU), il faut le **distribuer**. Deux outils dominent : **Ray** pour distribuer du Python en général, et les techniques de **parallélisme** de PyTorch pour l'entraînement des gros modèles.

## Ray : du Python sur un cluster

Ray transforme une fonction en **tâche** distante et une classe en **acteur** (un processus qui garde un état), avec un seul décorateur. Le même code tourne sur un portable ou sur 100 machines.

```pycode
import ray
ray.init()                                    # local, ou ray.init(address="ray://cluster:10001")

@ray.remote
def scorer(lot):
    return modele.predict(lot)

futurs = [scorer.remote(lot) for lot in lots]  # lancés en parallèle, partout dans le cluster
resultats = ray.get(futurs)
```

Au-dessus, des bibliothèques prêtes à l'emploi : **Ray Tune** (recherche d'hyperparamètres distribuée), **Ray Train** (entraînement distribué), **Ray Data** (traitement de gros volumes), **Ray Serve** (servir des modèles). OpenAI et Uber l'utilisent à très grande échelle.

## Le parallélisme de données

La forme la plus courante pour entraîner : chaque GPU a une **copie complète** du modèle et traite une **part du lot**. Après la rétropropagation, les GPU font la **moyenne de leurs gradients** (une opération collective appelée *all-reduce*), et appliquent tous la même mise à jour. Mathématiquement, c'est exactement la même descente de gradient que sur un seul GPU avec le lot complet. En PyTorch : `DistributedDataParallel` (DDP), lancé avec `torchrun --nproc_per_node=8 train.py`.

## Quand le modèle ne tient plus sur un GPU

Rappel (vague 5) : entraîner avec Adam en précision mixte demande environ **16 octets par paramètre** : 2 pour les poids en 16 bits, 2 pour les gradients, 12 pour les états de l'optimiseur (copie des poids en 32 bits et deux moments). Un modèle de 7 milliards de paramètres demande donc 112 Go, plus qu'un H100.

**ZeRO** (DeepSpeed) et **FSDP** (PyTorch) découpent ces données entre les N GPU au lieu de les dupliquer :

| Étape | Ce qui est découpé | Mémoire par GPU |
| --- | --- | --- |
| Sans ZeRO | rien | 16 Ψ |
| ZeRO-1 | états de l'optimiseur | 4 Ψ + 12 Ψ / N |
| ZeRO-2 | + gradients | 2 Ψ + 14 Ψ / N |
| ZeRO-3 (FSDP) | + poids | 16 Ψ / N |

(Ψ = nombre de paramètres, en octets par paramètre.)

```viz zero
```

Pour les plus gros modèles, on combine avec le **parallélisme de tenseur** (chaque matrice est coupée entre GPU d'une même machine) et le **parallélisme de pipeline** (les couches sont réparties en étages). C'est ce qu'on appelle le parallélisme 3D.

> **À retenir** : Ray pour distribuer du Python (tâches, acteurs, Tune, Serve). Parallélisme de données = copies du modèle + moyenne des gradients, mathématiquement identique. ZeRO et FSDP découpent poids, gradients et états de l'optimiseur pour faire tenir les gros modèles.
''',
"tasks": [
  "Installer ray, lancer ray.init() et paralléliser un scoring du jeu Immo avec @ray.remote",
  "Faire une recherche d'hyperparamètres avec Ray Tune sur 4 cœurs et comparer la durée avec GridSearchCV",
  "Lire le tutoriel « Getting Started with Distributed Data Parallel » de PyTorch et lancer l'exemple avec torchrun sur CPU",
],
"exercises": [
 E("e-ray-a", "Le parallélisme de données, vérifié",
   "Pour une régression linéaire, le gradient de l'erreur quadratique moyenne vaut 2/n · Xᵀ(Xw − y) (fonction `gradient` fournie). Écris `gradient_parallele(X, y, w, k)` : découpe les données en `k` parts avec `np.array_split` (une par « GPU »), calcule le gradient de chaque part, puis combine-les en une **moyenne pondérée par la taille des parts** (l'all-reduce). Vérifie que le résultat est identique au gradient complet.",
   r'''import numpy as np

def gradient(X, y, w):
    return 2 / len(X) * X.T @ (X @ w - y)

rng = np.random.default_rng(0)
X = rng.normal(size=(1003, 5))
y = X @ np.array([1.0, -2.0, 0.5, 3.0, 0.0]) + rng.normal(0, 0.1, 1003)
w = np.zeros(5)

def gradient_parallele(X, y, w, k):
    pass
''',
   r'''import numpy as np

def gradient(X, y, w):
    return 2 / len(X) * X.T @ (X @ w - y)

rng = np.random.default_rng(0)
X = rng.normal(size=(1003, 5))
y = X @ np.array([1.0, -2.0, 0.5, 3.0, 0.0]) + rng.normal(0, 0.1, 1003)
w = np.zeros(5)

def gradient_parallele(X, y, w, k):
    parts = zip(np.array_split(X, k), np.array_split(y, k))
    grads, tailles = zip(*[(gradient(Xi, yi, w), len(Xi)) for Xi, yi in parts])
    return np.average(np.array(grads), axis=0, weights=tailles)

print(np.allclose(gradient_parallele(X, y, w, 8), gradient(X, y, w)))
for _ in range(200):
    w -= 0.05 * gradient_parallele(X, y, w, 8)
print(w.round(2))
''',
   r'''import numpy as np
for k in [1, 2, 7, 8]:
    g = gradient_parallele(X, y, w * 0 + 0.3, k)
    assert g is not None and np.allclose(g, gradient(X, y, w * 0 + 0.3)), f"Avec k = {k}, le gradient parallèle doit être identique au gradient complet. Pondère chaque part par sa taille (les parts n'ont pas toutes la même taille : 1003 n'est pas divisible par 7 ou 8)."
''',
   "np.array_split(X, k) et np.array_split(y, k) ; np.average(grads, axis=0, weights=tailles)."),
 E("e-ray-b", "La mémoire avec ZeRO",
   "Écris `memoire_zero_go(n_params, n_gpus, etape)` qui renvoie la mémoire par GPU en Go (1 Go = 1e9 octets) selon le tableau de la leçon, pour `etape` valant 0, 1, 2 ou 3. Puis calcule `gpus_min_70b`, le plus petit nombre de GPU de 80 Go qui permet d'entraîner un modèle de 70e9 paramètres avec ZeRO-3, sans compter les activations.",
   r'''def memoire_zero_go(n_params, n_gpus, etape):
    pass

gpus_min_70b = None
''',
   r'''def memoire_zero_go(n_params, n_gpus, etape):
    P, N = n_params, n_gpus
    octets = {0: 16 * P, 1: 4 * P + 12 * P / N, 2: 2 * P + 14 * P / N, 3: 16 * P / N}[etape]
    return octets / 1e9

gpus_min_70b = next(n for n in range(1, 1000) if memoire_zero_go(70e9, n, 3) <= 80)
for e in range(4):
    print(f"ZeRO-{e} : {memoire_zero_go(7e9, 8, e):6.1f} Go par GPU pour 7B sur 8 GPU")
print("70B avec ZeRO-3 : au moins", gpus_min_70b, "GPU de 80 Go")
''',
   r'''assert memoire_zero_go(7e9, 8, 0) == 112, "Sans ZeRO : 16 octets par paramètre, soit 112 Go pour 7B."
assert abs(memoire_zero_go(7e9, 8, 1) - (28 + 84 / 8)) < 1e-9, "ZeRO-1 : 4Ψ + 12Ψ / N."
assert abs(memoire_zero_go(7e9, 8, 2) - (14 + 98 / 8)) < 1e-9, "ZeRO-2 : 2Ψ + 14Ψ / N."
assert abs(memoire_zero_go(7e9, 8, 3) - 14) < 1e-9, "ZeRO-3 : 16Ψ / N, soit 14 Go pour 7B sur 8 GPU."
assert gpus_min_70b == 14, f"16 × 70e9 / N ≤ 80e9 donne N ≥ 14 ; tu as {gpus_min_70b}."
''',
   "Un dictionnaire des quatre formules, indexé par etape. Pour le minimum : essaie n = 1, 2, 3… jusqu'à tenir dans 80 Go."),
]},
# ================================================================ Terraform
{"id": "l-terraform", "title": "Infrastructure as Code : Terraform et réseau AWS", "minutes": 100,
"body": r'''
Créer des serveurs, des bases et des réseaux en cliquant dans la console AWS ne se rejoue pas, ne se relit pas en revue de code, et dérive avec le temps. L'**Infrastructure as Code** décrit l'infrastructure dans des fichiers texte, versionnés dans Git. **Terraform** (ou son fork open source **OpenTofu**) est l'outil le plus répandu, et fonctionne avec tous les clouds.

## Le cycle de Terraform

```pycode
# main.tf
provider "aws" { region = "eu-west-3" }

resource "aws_s3_bucket" "modeles" {
  bucket = "fraude-modeles-prod"
}

resource "aws_instance" "api" {
  ami           = "ami-0abcdef1234567890"
  instance_type = var.type_instance
  subnet_id     = aws_subnet.prive_a.id       # une référence : Terraform en déduit l'ordre de création
  tags          = { Name = "fraude-api" }
}

variable "type_instance" { default = "t3.small" }
output "ip_api" { value = aws_instance.api.private_ip }
```

1. `terraform init` : télécharge les fournisseurs (*providers*).
2. `terraform plan` : compare la configuration à l'**état** actuel et affiche ce qui va changer : `+` créer, `~` modifier sur place, `-` détruire, `-/+` détruire et recréer (quand un attribut ne peut pas changer sur place, comme l'image d'une instance).
3. `terraform apply` : applique le plan.

Comme Kubernetes, Terraform est **déclaratif** : on décrit le résultat voulu, l'outil calcule les étapes.

## L'état, et pourquoi il doit être distant

Terraform garde dans un fichier d'**état** (*state*) la correspondance entre la configuration et les ressources réelles. En équipe, ce fichier doit être **partagé et verrouillé** : stocké dans un bucket S3, avec un verrou (table DynamoDB, ou le verrou natif de S3) pour que deux personnes n'appliquent pas en même temps. Il contient des données sensibles : il ne va jamais dans Git.

## Le réseau AWS en un schéma

- Un **VPC** : ton réseau privé, avec une plage d'adresses (par exemple `10.0.0.0/16`, 65 536 adresses).
- Des **sous-réseaux** dans plusieurs zones de disponibilité : **publics** (avec une route vers une Internet Gateway) pour le load balancer, **privés** pour l'API, les bases et les GPU.
- Une **NAT Gateway** pour que les sous-réseaux privés sortent vers Internet (télécharger des paquets) sans être joignables de l'extérieur.
- Des **groupes de sécurité** (vague 6) sur chaque ressource.

La notation CIDR `10.0.1.0/24` signifie : les 24 premiers bits sont fixés, il reste 8 bits, soit 256 adresses.

## Les modules

Un **module** Terraform regroupe des ressources réutilisables (« un VPC standard », « une API sur ECS »), paramétrées par des variables. Le registre public en propose des milliers, dont le module VPC officiel d'AWS.

> **À retenir** : init, plan, apply. Le plan compare l'état à la configuration (+, ~, -, -/+). État distant et verrouillé, jamais dans Git. VPC, sous-réseaux publics et privés, NAT, groupes de sécurité.
''',
"tasks": [
  "Installer Terraform (ou OpenTofu) et créer un bucket S3 avec terraform apply, puis le détruire avec terraform destroy",
  "Configurer un état distant dans S3 avec verrouillage",
  "Créer un VPC avec deux sous-réseaux publics et deux privés grâce au module terraform-aws-modules/vpc",
],
"exercises": [
 E("e-tf-a", "Calculer un plan",
   "Écris `planifier(etat, config, immuables=(\"ami\", \"instance_type\"))` : `etat` et `config` associent un nom de ressource à un dictionnaire d'attributs. Renvoie la liste des actions, triée par nom : `(\"+\", nom)` pour une ressource à créer, `(\"-\", nom)` pour une ressource à détruire, et pour une ressource dont des attributs changent (ajoutés, retirés ou modifiés) : `(\"-/+\", nom, attributs)` si l'un d'eux est immuable, sinon `(\"~\", nom, attributs)`, où `attributs` est la liste triée des attributs qui changent. Une ressource identique n'apparaît pas.",
   r'''def planifier(etat, config, immuables=("ami", "instance_type")):
    pass

etat = {
    "aws_s3_bucket.modeles": {"bucket": "fraude-modeles"},
    "aws_instance.api": {"ami": "ami-1", "instance_type": "t3.small", "tags": {"Name": "api"}},
    "aws_instance.batch": {"ami": "ami-1", "instance_type": "t3.large"},
    "aws_security_group.api": {"ingress": [443]},
}
config = {
    "aws_s3_bucket.modeles": {"bucket": "fraude-modeles"},
    "aws_instance.api": {"ami": "ami-1", "instance_type": "t3.small", "tags": {"Name": "api", "equipe": "ml"}},
    "aws_instance.batch": {"ami": "ami-2", "instance_type": "t3.large"},
    "aws_db_instance.suivi": {"engine": "postgres"},
}
''',
   r'''def planifier(etat, config, immuables=("ami", "instance_type")):
    actions = []
    for nom in sorted(set(etat) | set(config)):
        if nom not in etat:
            actions.append(("+", nom))
        elif nom not in config:
            actions.append(("-", nom))
        else:
            a, b = etat[nom], config[nom]
            changes = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
            if changes:
                actions.append(("-/+" if any(k in immuables for k in changes) else "~", nom, changes))
    return actions

etat = {
    "aws_s3_bucket.modeles": {"bucket": "fraude-modeles"},
    "aws_instance.api": {"ami": "ami-1", "instance_type": "t3.small", "tags": {"Name": "api"}},
    "aws_instance.batch": {"ami": "ami-1", "instance_type": "t3.large"},
    "aws_security_group.api": {"ingress": [443]},
}
config = {
    "aws_s3_bucket.modeles": {"bucket": "fraude-modeles"},
    "aws_instance.api": {"ami": "ami-1", "instance_type": "t3.small", "tags": {"Name": "api", "equipe": "ml"}},
    "aws_instance.batch": {"ami": "ami-2", "instance_type": "t3.large"},
    "aws_db_instance.suivi": {"engine": "postgres"},
}
for action in planifier(etat, config):
    print(*action)
''',
   r'''r = planifier(etat, config)
attendu = [("+", "aws_db_instance.suivi"), ("~", "aws_instance.api", ["tags"]), ("-/+", "aws_instance.batch", ["ami"]), ("-", "aws_security_group.api")]
assert r == attendu, f"Plan attendu :\n{attendu}\nTu obtiens :\n{r}"
assert planifier(etat, etat) == [], "Sans changement, le plan est vide."
assert planifier({"x": {"a": 1}}, {"x": {"a": 1, "b": 2}}) == [("~", "x", ["b"])], "Un attribut ajouté compte comme un changement."
assert planifier({"x": {"a": 1}}, {"x": {"a": 2}}, immuables=("a",)) == [("-/+", "x", ["a"])], "Respecte le paramètre immuables."
''',
   "Parcours sorted(set(etat) | set(config)). Pour une ressource présente des deux côtés, compare a.get(k) et b.get(k) sur l'union des clés."),
 E("e-tf-b", "Découper un VPC",
   "Avec le module `ipaddress` de la bibliothèque standard, écris `decouper(cidr_vpc, nombre, prefixe)` qui renvoie les `nombre` premiers sous-réseaux de taille `/prefixe` du VPC, sous forme de chaînes ; `taille(cidr)`, le nombre d'adresses d'un bloc ; et `appartient(ip, cidr)`, True si l'adresse est dans le bloc.",
   r'''import ipaddress

def decouper(cidr_vpc, nombre, prefixe):
    pass

def taille(cidr):
    pass

def appartient(ip, cidr):
    pass
''',
   r'''import ipaddress
from itertools import islice

def decouper(cidr_vpc, nombre, prefixe):
    reseau = ipaddress.ip_network(cidr_vpc)
    return [str(s) for s in islice(reseau.subnets(new_prefix=prefixe), nombre)]

def taille(cidr):
    return ipaddress.ip_network(cidr).num_addresses

def appartient(ip, cidr):
    return ipaddress.ip_address(ip) in ipaddress.ip_network(cidr)

publics, prives = decouper("10.0.0.0/16", 2, 24), decouper("10.0.0.0/16", 4, 24)[2:]
print("publics :", publics, "· privés :", prives)
print(taille("10.0.0.0/16"), "adresses dans le VPC ;", taille("10.0.1.0/24"), "par sous-réseau")
''',
   r'''assert decouper("10.0.0.0/16", 3, 24) == ["10.0.0.0/24", "10.0.1.0/24", "10.0.2.0/24"], "Les trois premiers /24 de 10.0.0.0/16."
assert decouper("10.0.0.0/16", 2, 20) == ["10.0.0.0/20", "10.0.16.0/20"], "Avec un préfixe /20, les blocs font 4 096 adresses."
assert taille("10.0.0.0/16") == 65536 and taille("10.0.1.0/24") == 256, "Un /16 a 65 536 adresses, un /24 en a 256."
assert appartient("10.0.1.42", "10.0.1.0/24") and not appartient("10.0.2.1", "10.0.1.0/24"), "10.0.1.42 est dans 10.0.1.0/24, pas 10.0.2.1."
''',
   "ipaddress.ip_network(cidr).subnets(new_prefix=prefixe) génère les sous-réseaux ; prends-en les premiers ; num_addresses donne la taille."),
 E("e-tf-c", "L'ordre de création",
   "Terraform crée les ressources dans un ordre compatible avec leurs références. Écris `ordre_creation(dependances)` : `dependances` associe chaque ressource à la liste de celles qu'elle référence. Renvoie une liste où chaque ressource vient après ses dépendances ; parmi les ressources prêtes au même moment, prends l'ordre **alphabétique**. S'il y a un cycle, lève une `ValueError`.",
   r'''def ordre_creation(dependances):
    pass

dependances = {
    "aws_instance.api": ["aws_subnet.prive", "aws_security_group.api"],
    "aws_subnet.prive": ["aws_vpc.principal"],
    "aws_security_group.api": ["aws_vpc.principal"],
    "aws_vpc.principal": [],
    "aws_lb.public": ["aws_subnet.public", "aws_security_group.lb"],
    "aws_subnet.public": ["aws_vpc.principal"],
    "aws_security_group.lb": ["aws_vpc.principal"],
}
''',
   r'''def ordre_creation(dependances):
    noeuds = set(dependances) | {d for ds in dependances.values() for d in ds}
    restantes = {n: set(dependances.get(n, [])) for n in noeuds}
    ordre = []
    while restantes:
        pretes = sorted(n for n, ds in restantes.items() if not ds)
        if not pretes:
            raise ValueError("Cycle de dépendances : " + ", ".join(sorted(restantes)))
        n = pretes[0]
        ordre.append(n)
        del restantes[n]
        for ds in restantes.values():
            ds.discard(n)
    return ordre

dependances = {
    "aws_instance.api": ["aws_subnet.prive", "aws_security_group.api"],
    "aws_subnet.prive": ["aws_vpc.principal"],
    "aws_security_group.api": ["aws_vpc.principal"],
    "aws_vpc.principal": [],
    "aws_lb.public": ["aws_subnet.public", "aws_security_group.lb"],
    "aws_subnet.public": ["aws_vpc.principal"],
    "aws_security_group.lb": ["aws_vpc.principal"],
}
for i, r in enumerate(ordre_creation(dependances), 1):
    print(i, r)
''',
   r'''r = ordre_creation(dependances)
attendu = ["aws_vpc.principal", "aws_security_group.api", "aws_security_group.lb", "aws_subnet.prive", "aws_instance.api", "aws_subnet.public", "aws_lb.public"]
assert r == attendu, f"Ordre attendu (à chaque étape, la première ressource prête par ordre alphabétique) :\n{attendu}\nTu obtiens :\n{r}"
assert ordre_creation({"b": ["a"]}) == ["a", "b"], "Une ressource référencée mais non listée doit aussi apparaître."
try:
    ordre_creation({"a": ["b"], "b": ["a"]}); cycle = False
except ValueError:
    cycle = True
assert cycle, "Un cycle doit lever une ValueError."
''',
   "Algorithme de Kahn : garde pour chaque ressource l'ensemble de ses dépendances restantes. Tant qu'il en reste, prends la plus petite ressource (alphabétiquement) sans dépendance, ajoute-la, et retire-la des autres ensembles."),
]},
# ================================================================ Airflow
{"id": "l-airflow", "title": "Orchestration avec Airflow", "minutes": 90,
"body": r'''
Un pipeline ML réel enchaîne des étapes : extraire les transactions de la veille, contrôler leur qualité, recalculer les variables, réentraîner, évaluer, publier le modèle si c'est mieux. Chaque nuit, avec des reprises en cas d'échec et des alertes. C'est le travail d'un **orchestrateur**. **Apache Airflow** est le plus utilisé ; Dagster et Prefect sont des alternatives modernes. Tu as vu les bases dans la leçon ETL de la vague 1 ; ici, on passe au niveau production.

## Les notions clés

- **DAG** (*directed acyclic graph*) : le pipeline, un graphe de tâches sans cycle.
- **Tâche** : une étape, créée à partir d'un **opérateur** (Python, Bash, SQL, Kubernetes, Spark…).
- **Planification** : `schedule="@daily"`, ou une expression cron (`"0 2 * * *"` = tous les jours à 2 h).
- **Intervalle de données** : chaque exécution traite une période précise. L'exécution du 15 mars à 2 h traite les données du 14 mars, de 00:00 à 24:00.
- **Reprises** : `retries=3`, `retry_delay=timedelta(minutes=5)` pour les pannes passagères.
- **Rattrapage** (*backfill*, *catchup*) : rejouer automatiquement les périodes manquées.

```viz dagrun
```

```pycode
from datetime import datetime, timedelta
from airflow.decorators import dag, task

@dag(schedule="@daily", start_date=datetime(2026, 1, 1), catchup=False,
     default_args={"retries": 2, "retry_delay": timedelta(minutes=5)})
def fraude_quotidien():

    @task
    def extraire(data_interval_start=None, data_interval_end=None):
        return requete_sql(debut=data_interval_start, fin=data_interval_end)

    @task
    def controler(chemin):
        verifier_contrat(chemin)        # échoue si les données sont invalides : rien en aval ne tourne

    @task
    def entrainer(chemin): ...

    @task
    def publier_si_meilleur(run_id): ...

    donnees = extraire()
    controler(donnees) >> entrainer(donnees)

fraude_quotidien()
```

## Les règles d'or

- **Idempotence** : relancer une tâche pour la même période doit donner le même résultat, sans doublon (on écrase la partition du jour au lieu d'ajouter des lignes).
- **Des tâches atomiques** : une tâche fait une chose ; si elle échoue, on la relance seule.
- **Pas de gros calcul dans Airflow lui-même** : il orchestre. Le calcul part dans un conteneur, un job Kubernetes ou Spark.
- **Pas de données entre tâches**, seulement des références (un chemin S3, un identifiant de run MLflow).

> **À retenir** : DAG de tâches, planification par intervalles de données, reprises, rattrapage. Des tâches idempotentes et atomiques qui orchestrent le calcul sans le faire.
''',
"tasks": [
  "Lancer Airflow avec Docker Compose (guide officiel « Running Airflow in Docker »)",
  "Écrire un DAG quotidien qui extrait des données Immo, contrôle leur qualité et réentraîne un modèle",
  "Provoquer un échec, observer les reprises, puis relancer une période passée avec airflow dags backfill",
],
"exercises": [
 E("e-af-a", "Exécuter un DAG avec reprises",
   "Écris `executer(taches, dependances, retries=1)` : `taches` associe un nom à une fonction sans argument, `dependances` associe un nom à la liste des tâches dont il dépend. Exécute les tâches dans l'ordre (parmi les prêtes, ordre alphabétique). Une tâche qui lève une exception est relancée jusqu'à `retries` fois de plus ; si elle échoue encore, son statut est `\"failed\"`, et toutes les tâches qui en dépendent, directement ou non, prennent le statut `\"upstream_failed\"` sans être exécutées. Les autres prennent `\"success\"`. Renvoie le dictionnaire des statuts.",
   r'''def executer(taches, dependances, retries=1):
    pass
''',
   r'''def executer(taches, dependances, retries=1):
    statuts = {}
    while len(statuts) < len(taches):
        pretes = sorted(t for t in taches if t not in statuts and all(d in statuts for d in dependances.get(t, [])))
        t = pretes[0]
        if any(statuts[d] != "success" for d in dependances.get(t, [])):
            statuts[t] = "upstream_failed"
            continue
        for essai in range(retries + 1):
            try:
                taches[t]()
                statuts[t] = "success"
                break
            except Exception:
                statuts[t] = "failed"
    return statuts

appels = {"n": 0}
def instable():
    appels["n"] += 1
    if appels["n"] < 2:
        raise ConnectionError("base indisponible")

print(executer({"extraire": instable, "controler": lambda: None, "entrainer": lambda: None},
               {"controler": ["extraire"], "entrainer": ["controler"]}, retries=1))
''',
   r'''journal = []
def ok(nom):
    return lambda: journal.append(nom)
def ko():
    journal.append("ko"); raise RuntimeError("panne")
essais = {"n": 0}
def instable():
    essais["n"] += 1; journal.append("instable")
    if essais["n"] < 3: raise ConnectionError("réseau")
T = {"extraire": ok("extraire"), "controler": ko, "entrainer": ok("entrainer"), "rapport": ok("rapport"), "publier": ok("publier")}
D = {"controler": ["extraire"], "entrainer": ["controler"], "publier": ["entrainer"], "rapport": ["extraire"]}
r = executer(T, D, retries=2)
assert r == {"extraire": "success", "controler": "failed", "entrainer": "upstream_failed", "publier": "upstream_failed", "rapport": "success"}, f"Statuts inattendus : {r}"
assert journal.count("ko") == 3, f"Avec retries=2, une tâche en échec est tentée 3 fois ; elle l'a été {journal.count('ko')} fois."
assert "entrainer" not in journal and "publier" not in journal, "Les tâches en aval d'un échec ne doivent pas être exécutées."
assert journal.index("controler" if "controler" in journal else "ko") < journal.index("rapport"), "Parmi les tâches prêtes, l'ordre est alphabétique : controler avant rapport."
journal.clear()
assert executer({"a": instable, "b": ok("b")}, {"b": ["a"]}, retries=2) == {"a": "success", "b": "success"}, "Une tâche qui réussit à la 3e tentative est un succès."
''',
   "Boucle tant que toutes les tâches n'ont pas de statut. Une tâche est prête quand toutes ses dépendances ont un statut ; si l'une n'est pas success, elle devient upstream_failed sans être exécutée."),
 E("e-af-b", "Les intervalles de données",
   "Écris `intervalles(debut, maintenant, catchup=True)` pour un DAG quotidien : `debut` et `maintenant` sont des `datetime`. Chaque exécution couvre un jour complet `[J 00:00, J+1 00:00)`, et ne peut tourner qu'une fois l'intervalle **terminé**. Renvoie la liste des tuples `(debut_intervalle, fin_intervalle)` à exécuter, du plus ancien au plus récent, en commençant au jour de `debut` (à minuit). Avec `catchup=False`, renvoie seulement le dernier intervalle terminé (une liste d'un élément, ou vide).",
   r'''from datetime import datetime, timedelta

def intervalles(debut, maintenant, catchup=True):
    pass
''',
   r'''from datetime import datetime, timedelta

def intervalles(debut, maintenant, catchup=True):
    jour = datetime(debut.year, debut.month, debut.day)
    res = []
    while jour + timedelta(days=1) <= maintenant:
        res.append((jour, jour + timedelta(days=1)))
        jour += timedelta(days=1)
    return res if catchup else res[-1:]

for a, b in intervalles(datetime(2026, 3, 10), datetime(2026, 3, 13, 2, 0)):
    print(a.date(), "→", b.date())
''',
   r'''from datetime import datetime
r = intervalles(datetime(2026, 3, 10, 15, 30), datetime(2026, 3, 13, 2, 0))
assert r == [(datetime(2026, 3, 10), datetime(2026, 3, 11)), (datetime(2026, 3, 11), datetime(2026, 3, 12)), (datetime(2026, 3, 12), datetime(2026, 3, 13))], f"Trois intervalles terminés (10, 11 et 12 mars) ; tu as {r}."
assert intervalles(datetime(2026, 3, 10), datetime(2026, 3, 13, 2, 0), catchup=False) == [(datetime(2026, 3, 12), datetime(2026, 3, 13))], "Sans rattrapage, seul le dernier intervalle terminé est exécuté."
assert intervalles(datetime(2026, 3, 10), datetime(2026, 3, 10, 23, 59)) == [], "L'intervalle du jour n'est pas terminé : rien à exécuter."
assert intervalles(datetime(2026, 3, 10), datetime(2026, 3, 11)) == [(datetime(2026, 3, 10), datetime(2026, 3, 11))], "Un intervalle qui se termine exactement maintenant peut tourner."
''',
   "Pars de minuit le jour de debut ; ajoute des intervalles d'un jour tant que leur fin est <= maintenant. Pour catchup=False, res[-1:]."),
]},
]

QUIZZES = {
"quiz-lead-infra": {"title": "Quiz · Gouvernance et infrastructure", "questions": [
 {"q": "Qui décide de l'usage d'un jeu de données et des accès dans un modèle de gouvernance ?", "options": ["L'ingénieur de données", "Le propriétaire métier (data owner)", "Le data scientist", "Le fournisseur cloud"], "answer": 1,
  "explain": "Le propriétaire est un responsable métier ; l'intendant veille à la qualité au quotidien."},
 {"q": "À quoi sert le lignage dans un catalogue de données ?", "options": ["À chiffrer les données", "À savoir d'où vient chaque table et ce qui en dépend, pour l'impact et les causes d'erreur", "À accélérer les requêtes", "À compresser les tables"], "answer": 1,
  "explain": "On le parcourt vers l'aval pour l'impact d'un changement, vers l'amont pour trouver une source fautive."},
 {"q": "Le décodage d'un LLM, un token à la fois, est limité par…", "options": ["Le calcul", "La bande passante mémoire", "Le disque", "Le réseau"], "answer": 1,
  "explain": "Un produit matrice × vecteur a une intensité arithmétique proche de 1 : le GPU attend les données."},
 {"q": "Combien d'opérations faut-il, environ, pour entraîner un Transformer de N paramètres sur D tokens ?", "options": ["N × D", "2 N D", "6 N D", "N² D"], "answer": 2,
  "explain": "2 pour la passe avant et 4 pour la rétropropagation, par paramètre et par token."},
 {"q": "Dans Kubernetes, que fait un Deployment ?", "options": ["Il expose une adresse HTTP", "Il maintient N copies d'un pod et gère les mises à jour", "Il stocke des secrets", "Il planifie des tâches cron"], "answer": 1,
  "explain": "Le Service donne l'adresse, le Secret stocke les secrets, le CronJob planifie."},
 {"q": "Avec ZeRO-3 (ou FSDP), qu'est-ce qui est découpé entre les GPU ?", "options": ["Seulement les données", "Les états de l'optimiseur, les gradients et les poids", "Seulement les gradients", "Rien"], "answer": 1,
  "explain": "La mémoire par GPU devient 16Ψ / N."},
 {"q": "Que signifie « -/+ » dans un terraform plan ?", "options": ["Une ressource modifiée sur place", "Une ressource détruite puis recréée, car un attribut ne peut pas changer sur place", "Une erreur", "Une ressource ignorée"], "answer": 1,
  "explain": "Par exemple changer l'image (ami) d'une instance : prudence, la ressource est remplacée."},
 {"q": "Pourquoi une tâche Airflow doit-elle être idempotente ?", "options": ["Pour aller plus vite", "Pour qu'une relance sur la même période donne le même résultat, sans doublon", "Pour éviter Kubernetes", "C'est imposé par Python"], "answer": 1,
  "explain": "Reprises et rattrapages relancent les tâches : elles doivent pouvoir tourner plusieurs fois sans dégâts."},
]},
}
