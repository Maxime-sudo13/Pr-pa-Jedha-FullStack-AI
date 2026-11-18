"""Moteur d'exécution des cellules (Pyodide dans le navigateur, CPython pour les tests)."""
import sys, io, ast, json, traceback, base64, os

os.environ.setdefault("MPLBACKEND", "AGG")

_NAMESPACES = {}
FILENAME = "<cellule>"


def _fresh():
    return {"__name__": "__main__"}


def reset(key):
    _NAMESPACES[key] = _fresh()


HINTS = {
    "NameError": "Ce nom n'existe pas encore. Vérifie l'orthographe (Python distingue majuscules et minuscules) ou exécute d'abord la cellule qui le crée.",
    "SyntaxError": "Python n'arrive pas à lire cette ligne : regarde les parenthèses, guillemets, deux-points (:) et virgules.",
    "IndentationError": "Problème d'indentation : un bloc après « : » doit être décalé de 4 espaces, et les lignes d'un même bloc doivent être alignées.",
    "TypeError": "Tu combines des types incompatibles (par exemple un texte et un nombre) ou tu appelles une fonction avec de mauvais arguments.",
    "KeyError": "Cette clé (ou colonne) n'existe pas. Affiche les clés disponibles avec .keys() ou df.columns.",
    "IndexError": "Cet indice dépasse la taille de la liste. Rappel : le premier élément est à l'indice 0, le dernier à len(liste) - 1.",
    "ZeroDivisionError": "Division par zéro. Vérifie que ton dénominateur ne peut pas valoir 0.",
    "AttributeError": "Cet objet n'a pas cet attribut ou cette méthode. Vérifie son type avec type(...) et l'orthographe.",
    "ValueError": "La valeur n'a pas le bon format (par exemple float('abc')) ou les dimensions ne correspondent pas.",
    "ModuleNotFoundError": "Ce module n'est pas disponible ici. Dans le navigateur, tu as numpy, pandas, scikit-learn, matplotlib et plotly.express (version simplifiée).",
    "ImportError": "Import impossible : vérifie le nom du module et de ce que tu importes.",
    "OperationalError": "Erreur dans ta requête SQL : vérifie les noms de tables et de colonnes, les virgules, et les guillemets simples autour du texte.",
    "DatabaseError": "Erreur dans ta requête SQL : vérifie les noms de tables et de colonnes, les virgules, et les guillemets simples autour du texte.",
    "HTTPError": "L'API a répondu par une erreur : regarde le code de statut et le message renvoyé.",
    "RuntimeError": "Une erreur a été levée volontairement par le code : lis son message.",
    "NotImplementedError": "Cette méthode n'est pas encore implémentée : c'est à toi de l'écrire.",
}


def _error_info(e, code):
    etype = type(e).__name__
    line = None
    if isinstance(e, SyntaxError) and e.filename == FILENAME:
        line = e.lineno
    else:
        for fr in traceback.extract_tb(e.__traceback__):
            if fr.filename == FILENAME:
                line = fr.lineno
    msg = str(e)
    if isinstance(e, SyntaxError):
        msg = e.msg
    src = None
    if line:
        lines = code.split("\n")
        if 0 < line <= len(lines):
            src = lines[line - 1]
    return {"type": etype, "message": msg, "line": line, "source": src,
            "hint": HINTS.get(etype, "")}


def _display(value, figs):
    if value is None:
        return None
    if getattr(value, "_is_px_fig", False):
        figs.append(value.to_json())
        return None
    try:
        import pandas as pd
        if isinstance(value, pd.DataFrame):
            return {"html": value.to_html(max_rows=15, max_cols=12, border=0, classes="df"),
                    "text": f"{value.shape[0]} lignes × {value.shape[1]} colonnes"}
        if isinstance(value, pd.Series):
            return {"html": value.to_frame().to_html(max_rows=20, border=0, classes="df"),
                    "text": f"Series · {len(value)} valeurs · dtype {value.dtype}"}
    except ImportError:
        pass
    text = repr(value)
    if len(text) > 6000:
        text = text[:6000] + "\n… (affichage tronqué)"
    return {"text": text}


def _mpl_figures():
    out = []
    if "matplotlib.pyplot" not in sys.modules:
        return out
    plt = sys.modules["matplotlib.pyplot"]
    for num in plt.get_fignums():
        fig = plt.figure(num)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=110, bbox_inches="tight")
        out.append("data:image/png;base64," + base64.b64encode(buf.getvalue()).decode())
    plt.close("all")
    return out


def run(code, key, check=None, fresh=False):
    """Version synchrone (tests en CPython)."""
    import asyncio
    return asyncio.run(run_async(code, key, check, fresh))


async def _exec(source, filename, ns, mode="exec"):
    flags = ast.PyCF_ALLOW_TOP_LEVEL_AWAIT
    co = compile(source, filename, mode, flags=flags)
    res = eval(co, ns)
    if hasattr(res, "__await__"):
        res = await res
    return res


async def run_async(code, key, check=None, fresh=False):
    """Exécute `code` dans l'espace de noms `key` (accepte `await` au premier niveau). Renvoie un JSON."""
    if fresh or key not in _NAMESPACES:
        _NAMESPACES[key] = _fresh()
    ns = _NAMESPACES[key]
    px = sys.modules.get("plotly.express")
    figs = []
    if px is not None:
        px._FIGS.clear()
    out, err = io.StringIO(), io.StringIO()
    old = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = out, err
    res = {"stdout": "", "stderr": "", "error": None, "result": None,
           "figs": [], "images": [], "check": None}
    try:
        tree = ast.parse(code, FILENAME)
        last = None
        if tree.body and isinstance(tree.body[-1], ast.Expr):
            last = ast.Expression(tree.body.pop().value)
        await _exec(tree, FILENAME, ns)
        if last is not None:
            value = await _exec(last, FILENAME, ns, "eval")
            res["result"] = _display(value, figs)
    except BaseException as e:  # noqa
        if isinstance(e, KeyboardInterrupt):
            raise
        res["error"] = _error_info(e, code)
    finally:
        sys.stdout, sys.stderr = old
    res["stdout"] = out.getvalue()[-20000:]
    res["stderr"] = err.getvalue()[-5000:]
    if px is not None:
        figs = [f.to_json() for f in px._FIGS] + figs
        px._FIGS.clear()
    res["figs"] = figs
    try:
        res["images"] = _mpl_figures()
    except Exception:
        res["images"] = []
    if check is not None:
        if res["error"]:
            res["check"] = {"ok": False, "message": "Ton code s'arrête sur une erreur : corrige-la d'abord."}
        else:
            ns["_out"] = res["stdout"]
            try:
                await _exec(check, "<verification>", ns)
                res["check"] = {"ok": True, "message": "Bravo, tout est correct."}
            except AssertionError as e:
                res["check"] = {"ok": False, "message": str(e) or "Le résultat n'est pas encore celui attendu."}
            except NameError as e:
                name = str(e).split("'")[1] if "'" in str(e) else str(e)
                res["check"] = {"ok": False, "message": f"Je ne trouve pas « {name} » : as-tu bien créé cette variable ou cette fonction, avec ce nom exact ?"}
            except Exception as e:
                res["check"] = {"ok": False, "message": f"La vérification a échoué ({type(e).__name__} : {e}). Relis la consigne."}
    return json.dumps(res, default=str)
