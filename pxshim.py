"""Version simplifiée de plotly.express pour le navigateur.
Même syntaxe que la vraie bibliothèque pour scatter, line, bar, histogram et box."""
import sys, types, json, math

_FIGS = []


def _clean(v):
    try:
        import numpy as np
        if isinstance(v, np.generic):
            v = v.item()
    except ImportError:
        pass
    if isinstance(v, float) and math.isnan(v):
        return None
    if hasattr(v, "isoformat"):
        return v.isoformat()
    return v


def _tolist(v):
    if v is None:
        return None
    if hasattr(v, "tolist"):
        v = v.tolist()
    return [_clean(x) for x in list(v)]


def _col(df, c):
    if c is None:
        return None
    if isinstance(c, str):
        if df is None:
            raise ValueError(f"Tu passes le nom de colonne '{c}' sans data_frame.")
        if c not in df.columns:
            raise ValueError(f"La colonne '{c}' n'existe pas. Colonnes disponibles : {list(df.columns)}")
        return _tolist(df[c])
    return _tolist(c)


def _label(name, labels, default=None, key=None):
    labels = labels or {}
    if isinstance(name, str):
        return labels.get(name, name)
    if key and key in labels:
        return labels[key]
    return default


class Figure:
    _is_px_fig = True

    def __init__(self, data, layout):
        self.data = data
        self.layout = layout

    def update_layout(self, **kw):
        for k, v in kw.items():
            if k == "title" and isinstance(v, str):
                v = {"text": v}
            if k.startswith("xaxis_") or k.startswith("yaxis_"):
                ax, prop = k.split("_", 1)
                self.layout.setdefault(ax, {})
                if prop == "title" and isinstance(v, str):
                    v = {"text": v}
                self.layout[ax][prop] = v
            else:
                self.layout[k] = v
        return self

    def update_traces(self, **kw):
        for t in self.data:
            t.update(kw)
        return self

    def show(self):
        _FIGS.append(self)

    def to_dict(self):
        return {"data": self.data, "layout": self.layout}

    def to_json(self):
        return json.dumps(self.to_dict(), default=_clean)

    def __repr__(self):
        kinds = ", ".join(sorted({t.get("type", "?") for t in self.data}))
        return f"<Figure plotly.express : {len(self.data)} trace(s) de type {kinds}>"


def _groups(df, color, n):
    if color is None:
        return [(None, list(range(n)))]
    vals = _col(df, color)
    order, idx = [], {}
    for i, v in enumerate(vals):
        if v not in idx:
            idx[v] = []
            order.append(v)
        idx[v].append(i)
    return [(v, idx[v]) for v in order]


def _pick(lst, ids):
    return None if lst is None else [lst[i] for i in ids]


def _layout(title, x, y, labels, color, ydefault=None, xdefault=None):
    lay = {"xaxis": {"title": {"text": _label(x, labels, xdefault, "x") or ""}},
           "yaxis": {"title": {"text": _label(y, labels, ydefault, "y") or ""}}}
    if title:
        lay["title"] = {"text": title}
    if color is not None and isinstance(color, str):
        lay["legend"] = {"title": {"text": _label(color, labels, None, "color")}}
    return lay


def _make(kind, data_frame, x, y, color, title, labels, extra=None, ydefault=None, xdefault=None):
    xs, ys = _col(data_frame, x), _col(data_frame, y)
    n = len(xs) if xs is not None else len(ys or [])
    traces = []
    for val, ids in _groups(data_frame, color, n):
        t = {"type": kind}
        if xs is not None:
            t["x"] = _pick(xs, ids)
        if ys is not None:
            t["y"] = _pick(ys, ids)
        if val is not None:
            t["name"] = str(val)
        t.update(extra or {})
        traces.append(t)
    return Figure(traces, _layout(title, x, y, labels, color, ydefault, xdefault))


def scatter(data_frame=None, x=None, y=None, color=None, title=None, labels=None, opacity=None, **kw):
    extra = {"mode": "markers"}
    if opacity is not None:
        extra["opacity"] = opacity
    return _make("scatter", data_frame, x, y, color, title, labels, extra)


def line(data_frame=None, x=None, y=None, color=None, title=None, labels=None, markers=False, **kw):
    if x is None and y is not None:
        ys = _col(data_frame, y)
        x = list(range(len(ys)))
        fig = _make("scatter", data_frame, x, y, color, title, labels,
                    {"mode": "lines+markers" if markers else "lines"}, xdefault="index")
        return fig
    return _make("scatter", data_frame, x, y, color, title, labels,
                 {"mode": "lines+markers" if markers else "lines"})


def bar(data_frame=None, x=None, y=None, color=None, title=None, labels=None, barmode="relative", **kw):
    fig = _make("bar", data_frame, x, y, color, title, labels)
    fig.layout["barmode"] = barmode
    return fig


def histogram(data_frame=None, x=None, y=None, color=None, nbins=None, title=None, labels=None,
              barmode="relative", **kw):
    extra = {}
    if nbins:
        extra["nbinsx"] = nbins
    fig = _make("histogram", data_frame, x, y, color, title, labels, extra, ydefault="count")
    fig.layout["barmode"] = "overlay" if barmode == "overlay" else barmode
    if barmode == "overlay":
        fig.update_traces(opacity=0.6)
    return fig


def box(data_frame=None, x=None, y=None, color=None, title=None, labels=None, **kw):
    return _make("box", data_frame, x, y, color, title, labels)


def _install():
    px = types.ModuleType("plotly.express")
    for name in ["scatter", "line", "bar", "histogram", "box", "Figure", "_FIGS"]:
        setattr(px, name, globals()[name])
    plotly = types.ModuleType("plotly")
    plotly.express = px
    plotly.__path__ = []
    sys.modules["plotly"] = plotly
    sys.modules["plotly.express"] = px
    return px


_install()
