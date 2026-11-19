"""Un mini-framework qui imite FastAPI, pour s'entraîner dans le navigateur.

    from minifast import FastAPI, HTTPException, TestClient
    from pydantic import BaseModel

    app = FastAPI(title="Mon API")

    class Entree(BaseModel):
        surface: float

    @app.get("/sante")
    def sante():
        return {"statut": "ok"}

    @app.post("/predire")
    def predire(entree: Entree):
        return {"prix": entree.surface * 4000}

    client = TestClient(app)
    client.post("/predire", json={"surface": 50}).json()

Pour les bases (routes, paramètres de chemin et de requête, corps validé par
pydantic, HTTPException, codes de statut), la syntaxe est celle de FastAPI.
Sur ton ordinateur : pip install fastapi uvicorn, puis uvicorn main:app --reload.
"""
import inspect
import json as _json
import re
from urllib.parse import urlsplit, parse_qsl

__all__ = ["FastAPI", "HTTPException", "TestClient", "Response"]


class HTTPException(Exception):
    def __init__(self, status_code, detail=None):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class Response:
    def __init__(self, status_code, contenu):
        self.status_code = status_code
        self._contenu = contenu
        self.text = _json.dumps(contenu, ensure_ascii=False)

    def json(self):
        return _json.loads(self.text)

    def __repr__(self):
        return f"<Response [{self.status_code}]>"


def _est_modele(t):
    return inspect.isclass(t) and hasattr(t, "model_validate") and hasattr(t, "model_fields")


def _vers_json(v):
    if hasattr(v, "model_dump"):
        return v.model_dump()
    if isinstance(v, dict):
        return {k: _vers_json(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_vers_json(x) for x in v]
    if hasattr(v, "item") and callable(v.item):          # nombres NumPy
        return v.item()
    return v


def _convertir(valeur, annotation):
    base = annotation
    origine = getattr(annotation, "__args__", None)
    if origine and type(None) in origine:                # Optional[X] ou X | None
        base = next(a for a in origine if a is not type(None))
    if base in (int, float):
        return base(valeur)
    if base is bool:
        return str(valeur).lower() in ("1", "true", "oui", "yes")
    return valeur


class _Route:
    def __init__(self, methode, chemin, fonction, status_code):
        self.methode, self.chemin, self.fonction, self.status_code = methode, chemin, fonction, status_code
        self.noms = re.findall(r"{(\w+)}", chemin)
        self.regex = re.compile("^" + re.sub(r"{(\w+)}", r"(?P<\1>[^/]+)", chemin) + "$")
        self.signature = inspect.signature(fonction)


class FastAPI:
    def __init__(self, title="API", version="0.1.0", description=""):
        self.title, self.version, self.description = title, version, description
        self.routes = []

    def _ajouter(self, methode, chemin, status_code):
        def deco(f):
            self.routes.append(_Route(methode, chemin, f, status_code))
            return f
        return deco

    def get(self, chemin, status_code=200):
        return self._ajouter("GET", chemin, status_code)

    def post(self, chemin, status_code=200):
        return self._ajouter("POST", chemin, status_code)

    def put(self, chemin, status_code=200):
        return self._ajouter("PUT", chemin, status_code)

    def delete(self, chemin, status_code=200):
        return self._ajouter("DELETE", chemin, status_code)

    def openapi(self):
        """Une version simplifiée de la documentation générée automatiquement (/docs)."""
        chemins = {}
        for r in self.routes:
            params = []
            for nom, p in r.signature.parameters.items():
                if _est_modele(p.annotation):
                    params.append({"nom": nom, "dans": "body", "schema": p.annotation.model_json_schema()})
                else:
                    params.append({"nom": nom, "dans": "path" if nom in r.noms else "query",
                                   "type": getattr(p.annotation, "__name__", str(p.annotation)),
                                   "obligatoire": p.default is inspect.Parameter.empty})
            chemins.setdefault(r.chemin, {})[r.methode.lower()] = {"fonction": r.fonction.__name__, "parametres": params}
        return {"titre": self.title, "version": self.version, "chemins": chemins}

    def _traiter(self, methode, url, corps=None, params=None):
        morceaux = urlsplit(url)
        requete = dict(parse_qsl(morceaux.query))
        requete.update({k: str(v) for k, v in (params or {}).items()})
        trouvees = [(r, r.regex.match(morceaux.path)) for r in self.routes]
        trouvees = [(r, m) for r, m in trouvees if m]
        if not trouvees:
            return Response(404, {"detail": "Not Found"})
        route = next((r for r, m in trouvees if r.methode == methode), None)
        if route is None:
            return Response(405, {"detail": "Method Not Allowed"})
        m = route.regex.match(morceaux.path)
        args, erreurs = {}, []
        for nom, p in route.signature.parameters.items():
            try:
                if nom in route.noms:
                    args[nom] = _convertir(m.group(nom), p.annotation)
                elif _est_modele(p.annotation):
                    if corps is None:
                        erreurs.append({"loc": ["body"], "msg": "Field required", "type": "missing"})
                    else:
                        args[nom] = p.annotation.model_validate(corps)
                elif nom in requete:
                    args[nom] = _convertir(requete[nom], p.annotation)
                elif p.default is not inspect.Parameter.empty:
                    args[nom] = p.default
                else:
                    erreurs.append({"loc": ["query", nom], "msg": "Field required", "type": "missing"})
            except (ValueError, TypeError) as e:
                if hasattr(e, "errors"):
                    for err in e.errors():
                        erreurs.append({"loc": ["body", *err["loc"]], "msg": err["msg"], "type": err["type"]})
                else:
                    loc = "path" if nom in route.noms else "query"
                    erreurs.append({"loc": [loc, nom], "msg": "Input should be a valid " + getattr(p.annotation, "__name__", "value"), "type": "parsing"})
        if erreurs:
            return Response(422, {"detail": erreurs})
        try:
            res = route.fonction(**args)
            if inspect.iscoroutine(res):
                res = _executer(res)
        except HTTPException as e:
            return Response(e.status_code, {"detail": e.detail})
        return Response(route.status_code, _vers_json(res))


def _executer(coro):
    """Exécute une fonction async qui n'attend rien d'extérieur (pas de sleep réel)."""
    try:
        coro.send(None)
    except StopIteration as fin:
        return fin.value
    coro.close()
    raise RuntimeError("Cette route async attend une vraie opération : sur ton ordinateur, lance-la avec uvicorn.")


class TestClient:
    """Envoie des requêtes à l'application sans serveur, comme fastapi.testclient.TestClient."""

    def __init__(self, app):
        self.app = app

    def get(self, url, params=None):
        return self.app._traiter("GET", url, params=params)

    def delete(self, url, params=None):
        return self.app._traiter("DELETE", url, params=params)

    def post(self, url, json=None, params=None):
        return self.app._traiter("POST", url, corps=json, params=params)

    def put(self, url, json=None, params=None):
        return self.app._traiter("PUT", url, corps=json, params=params)
