"""Appeler un vrai LLM (Claude) depuis Python, directement dans la plateforme.

    import llm
    texte = await llm.complete("Explique le RAG en une phrase.")
    texte = await llm.chat([{"role": "user", "content": "Bonjour"}], system="Tu réponds en une phrase.")
    llm.disponible()   # True si un vrai modèle répond sur cet appareil

`await` s'utilise directement dans les cellules, comme dans un notebook Jupyter.
Hors de la plateforme (tests, ordinateur sans clé), un modèle simulé répond.
Sur ton ordinateur, tu utiliseras le SDK de ton fournisseur (anthropic, openai, mistralai…).
"""
try:
    import js  # disponible seulement dans le navigateur (Pyodide)
    from pyodide.ffi import to_js
    _NAVIGATEUR = True
except ImportError:
    _NAVIGATEUR = False

historique = []   # journal des appels : utile pour compter les appels et les tokens


def disponible():
    if not _NAVIGATEUR:
        return False
    try:
        return bool(js.plateformeLLMDispo())
    except Exception:
        return False


def _simule(messages):
    dernier = messages[-1]["content"]
    return f"[Réponse simulée : aucun LLM disponible ici] Tu as demandé : {dernier[:120]}"


async def chat(messages, system=None):
    """Envoie une conversation (liste de {"role": "user"|"assistant", "content": str}, terminée par "user")."""
    msgs = [{"role": m["role"], "content": str(m["content"])} for m in messages]
    if not msgs or msgs[-1]["role"] != "user":
        raise ValueError("La conversation doit se terminer par un message de rôle 'user'.")
    if system:
        msgs[0] = {"role": msgs[0]["role"], "content": f"{system}\n\n{msgs[0]['content']}"}
    if disponible():
        try:
            texte = str(await js.plateformeLLM(to_js(msgs, dict_converter=js.Object.fromEntries)))
        except Exception as e:
            raise RuntimeError(f"Le LLM n'a pas pu répondre : {e}")
    else:
        texte = _simule(msgs)
    historique.append({"messages": msgs, "reponse": texte})
    return texte


async def complete(prompt, system=None):
    """Envoie un seul message et renvoie la réponse texte."""
    return await chat([{"role": "user", "content": prompt}], system=system)
