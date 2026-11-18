"""Une fausse API web, pour s'entraîner sans connexion dans le navigateur.

Elle imite la bibliothèque `requests` : `get(url, params=None, headers=None)` renvoie une réponse
avec `.status_code`, `.headers`, `.json()` et `.raise_for_status()`.

Points d'entrée disponibles (base https://api.biblio.test) :
- GET /books?page=N&limit=K         → liste paginée de livres
- GET /books/<id>                   → un livre (404 s'il n'existe pas)
- GET /authors/<id>                 → un auteur
- GET /flaky                        → échoue (503, puis 429) avant de répondre : pour tester les reprises
- GET /secure                       → exige l'en-tête Authorization: Bearer cle-demo
"""
import json as _json

BASE = "https://api.biblio.test"

AUTEURS = {
    1: {"id": 1, "nom": "Mary Shelley", "naissance": 1797, "pays": "Royaume-Uni"},
    2: {"id": 2, "nom": "Isaac Asimov", "naissance": 1920, "pays": "États-Unis"},
    3: {"id": 3, "nom": "Ursula K. Le Guin", "naissance": 1929, "pays": "États-Unis"},
    4: {"id": 4, "nom": "Alain Damasio", "naissance": 1969, "pays": "France"},
    5: {"id": 5, "nom": "Ted Chiang", "naissance": 1967, "pays": "États-Unis"},
}
_TITRES = [
    ("Frankenstein", 1, 1818, ["gothique", "science-fiction"], 4.1),
    ("Les Robots", 2, 1950, ["science-fiction", "robots"], 4.3),
    ("Fondation", 2, 1951, ["science-fiction", "empire"], 4.4),
    ("La Main gauche de la nuit", 3, 1969, ["science-fiction", "genre"], 4.2),
    ("Les Dépossédés", 3, 1974, ["science-fiction", "utopie"], 4.3),
    ("La Horde du Contrevent", 4, 2004, ["fantasy", "aventure"], 4.6),
    ("Les Furtifs", 4, 2019, ["science-fiction", "surveillance"], 3.9),
    ("La Zone du Dehors", 4, 1999, ["science-fiction", "politique"], 4.0),
    ("La Tour de Babylone", 5, 1990, ["nouvelle", "fantasy"], 4.2),
    ("L'Histoire de ta vie", 5, 1998, ["nouvelle", "langage"], 4.5),
    ("Expiration", 5, 2019, ["nouvelle", "science-fiction"], 4.4),
    ("Le Dernier Homme", 1, 1826, ["anticipation"], 3.6),
    ("Les Cavernes d'acier", 2, 1954, ["science-fiction", "policier"], 4.1),
    ("Terremer", 3, 1968, ["fantasy"], 4.3),
    ("Le Dit d'Aka", 3, 2000, ["science-fiction"], 3.8),
    ("Aucun souvenir assez solide", 4, 2012, ["nouvelle"], 3.7),
    ("Le Cycle de vie des objets logiciels", 5, 2010, ["novella", "IA"], 4.2),
    ("Moi, robot", 2, 1950, ["science-fiction", "robots"], 4.2),
    ("Le Monde de Rocannon", 3, 1966, ["science-fiction"], 3.7),
    ("Mathilda", 1, 1959, ["roman"], 3.5),
    ("Les Dieux eux-mêmes", 2, 1972, ["science-fiction"], 4.0),
    ("Le Nom du monde est forêt", 3, 1972, ["science-fiction", "écologie"], 4.0),
    ("Scarlett et Novak", 4, 2021, ["nouvelle", "IA"], 3.6),
]
LIVRES = {i: {"id": i, "titre": t, "auteur_id": a, "annee": y,
              "sujets": s, "note": {"moyenne": n, "votes": 50 + (i * 37) % 900},
              "disponible": i % 4 != 0}
          for i, (t, a, y, s, n) in enumerate(_TITRES, 1)}

_compteur_flaky = {"n": 0}
appels = []   # journal des appels, utile pour les vérifications


class Response:
    def __init__(self, status_code, data=None, headers=None, url=""):
        self.status_code = status_code
        self._data = data
        self.headers = headers or {"Content-Type": "application/json"}
        self.url = url
        self.text = _json.dumps(data, ensure_ascii=False) if data is not None else ""

    @property
    def ok(self):
        return 200 <= self.status_code < 400

    def json(self):
        if self._data is None:
            raise ValueError("La réponse ne contient pas de JSON.")
        return self._data

    def raise_for_status(self):
        if not self.ok:
            raise HTTPError(f"{self.status_code} Error for url: {self.url}", response=self)

    def __repr__(self):
        return f"<Response [{self.status_code}]>"


class HTTPError(Exception):
    def __init__(self, msg, response=None):
        super().__init__(msg)
        self.response = response


def reset():
    _compteur_flaky["n"] = 0
    appels.clear()


def get(url, params=None, headers=None, timeout=None):
    params = dict(params or {})
    headers = dict(headers or {})
    appels.append({"url": url, "params": params})
    if not url.startswith(BASE):
        return Response(404, {"erreur": "Domaine inconnu : utilise " + BASE}, url=url)
    chemin = url[len(BASE):].rstrip("/")
    parts = [p for p in chemin.split("/") if p]
    if parts == ["books"]:
        page = int(params.get("page", 1))
        limit = min(int(params.get("limit", 10)), 20)
        ids = sorted(LIVRES)
        total = len(ids)
        debut = (page - 1) * limit
        items = [LIVRES[i] for i in ids[debut:debut + limit]]
        suivante = page + 1 if debut + limit < total else None
        return Response(200, {"page": page, "limit": limit, "total": total,
                              "page_suivante": suivante, "resultats": items}, url=url)
    if len(parts) == 2 and parts[0] == "books":
        i = int(parts[1]) if parts[1].isdigit() else -1
        if i in LIVRES:
            return Response(200, LIVRES[i], url=url)
        return Response(404, {"erreur": f"Livre {parts[1]} introuvable"}, url=url)
    if len(parts) == 2 and parts[0] == "authors":
        i = int(parts[1]) if parts[1].isdigit() else -1
        if i in AUTEURS:
            return Response(200, AUTEURS[i], url=url)
        return Response(404, {"erreur": "Auteur introuvable"}, url=url)
    if parts == ["flaky"]:
        _compteur_flaky["n"] += 1
        n = _compteur_flaky["n"]
        if n == 1:
            return Response(503, {"erreur": "Service indisponible"}, url=url)
        if n == 2:
            return Response(429, {"erreur": "Trop de requêtes"}, headers={"Retry-After": "1"}, url=url)
        return Response(200, {"message": "Enfin !", "tentative": n}, url=url)
    if parts == ["secure"]:
        if headers.get("Authorization") == "Bearer cle-demo":
            return Response(200, {"secret": "42"}, url=url)
        return Response(401, {"erreur": "Clé d'API manquante ou invalide"}, url=url)
    return Response(404, {"erreur": f"Point d'entrée inconnu : {chemin}"}, url=url)
