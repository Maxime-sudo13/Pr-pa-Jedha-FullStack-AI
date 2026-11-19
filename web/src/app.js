"use strict";
/* ================================================================ utilitaires */
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const h = (html) => { const t = document.createElement("template"); t.innerHTML = html.trim(); return t.content.firstElementChild; };
const today = () => { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`; };
const pct = (a, b) => b ? Math.round(100 * a / b) : 0;
const sleep = ms => new Promise(r => setTimeout(r, ms));

/* ================================================================ contenu */
let C = null;
const MOD = {};        // id module -> { module, track }
const HOME = {};       // id item/quiz -> id module de rattachement
const ORDER = [];      // parcours ordonné d'items et de quiz (sans doublons)
const ITEM = id => (C.items[id] || C.quizzes[id] || null);

function indexContent() {
  const seen = new Set();
  const push = (id, mid) => { if (!seen.has(id)) { seen.add(id); ORDER.push(id); HOME[id] = mid; } };
  for (const T of C.tracks) for (const M of T.modules) {
    MOD[M.id] = { M, T };
    for (const s of M.sections) for (const id of s.lecons) push(id, M.id);
    for (const id of M.projets) push(id, M.id);
    for (const id of M.quiz) push(id, M.id);
  }
}
function moduleItems(M) {
  const ids = [];
  for (const s of M.sections) for (const id of s.lecons) if (!ids.includes(id)) ids.push(id);
  for (const id of M.projets) if (!ids.includes(id)) ids.push(id);
  for (const id of M.quiz) if (!ids.includes(id)) ids.push(id);
  return ids;
}

/* ================================================================ progression */
const LS_KEY = "mise-a-niveau-ia:v1";
const LS_CODE = "mise-a-niveau-ia:code:v1";
const blank = () => ({ v: 1, done: {}, ex: {}, tasks: {}, quiz: {}, days: [], start: null, track: "essentials", week: null });
let S = blank();
let CODE = {};
const store = { ref: null, codeRef: null, mode: "local", timer: null, codeTimer: null, writing: false, again: false, codeWriting: false, codeAgain: false };

function loadLocal() {
  try { const s = JSON.parse(localStorage.getItem(LS_KEY) || "null"); if (s && s.v === 1) S = Object.assign(blank(), s); } catch (e) {}
  try { CODE = JSON.parse(localStorage.getItem(LS_CODE) || "{}") || {}; } catch (e) {}
}
function merge(a, b) {
  const m = blank();
  for (const k of ["done", "ex", "tasks"]) m[k] = Object.assign({}, a[k], b[k]);
  for (const k of new Set([...Object.keys(a.quiz || {}), ...Object.keys(b.quiz || {})])) m.quiz[k] = Math.max(a.quiz?.[k] ?? 0, b.quiz?.[k] ?? 0);
  m.days = [...new Set([...(a.days || []), ...(b.days || [])])].sort();
  m.start = b.start || a.start || null;
  m.track = b.track || a.track || "essentials";
  m.week = b.week ?? a.week ?? null;
  return m;
}
function touchDay() { const d = today(); if (!S.days.includes(d)) S.days.push(d); }
function save() {
  touchDay();
  try { localStorage.setItem(LS_KEY, JSON.stringify(S)); } catch (e) {}
  updateGlobal();
  if (store.ref) { clearTimeout(store.timer); store.timer = setTimeout(pushRemote, 1200); }
}
async function pushRemote() {
  if (!store.ref) return;
  if (store.writing) { store.again = true; return; }
  store.writing = true;
  try { await store.ref.set(JSON.parse(JSON.stringify(S))); setSync("compte"); }
  catch (e) { if (e && ["invalid_argument", "revoked", "not_granted"].includes(e.code)) { store.ref = null; store.codeRef = null; setSync("local"); } }
  store.writing = false;
  if (store.again) { store.again = false; pushRemote(); }
}
function saveCode(id, code) {
  CODE[id] = code;
  try { localStorage.setItem(LS_CODE, JSON.stringify(CODE)); } catch (e) {}
  if (store.codeRef) { clearTimeout(store.codeTimer); store.codeTimer = setTimeout(pushCode, 2500); }
}
async function pushCode() {
  if (!store.codeRef) return;
  if (store.codeWriting) { store.codeAgain = true; return; }
  store.codeWriting = true;
  try { await store.codeRef.set(JSON.parse(JSON.stringify({ code: CODE }))); } catch (e) {}
  store.codeWriting = false;
  if (store.codeAgain) { store.codeAgain = false; pushCode(); }
}
function setSync(mode) {
  store.mode = mode;
  const el = $("#sync");
  if (el) el.textContent = mode === "compte" ? "Ta progression et ton code sont enregistrés sur ton compte : tu les retrouves sur tous tes appareils." : "Ta progression est enregistrée dans ce navigateur.";
}
async function connectStore() {
  if (!window.claude || typeof window.claude.use !== "function") return;
  try {
    const [db, user] = await Promise.all([window.claude.use("db"), window.claude.use("user")]);
    if (!db || !user) return;
    const uid = await user.id();
    if (!uid) return;
    const ref = db.doc(`data/users/${uid}/progress`);
    const codeRef = db.doc(`data/users/${uid}/code`);
    const res = await Promise.race([Promise.all([ref.get(), codeRef.get()]), sleep(10000).then(() => "timeout")]);
    if (res === "timeout") return;
    const [snap, csnap] = res;
    store.ref = ref; store.codeRef = codeRef;
    if (snap.exists) S = merge(S, snap.data() || {});
    if (csnap.exists) CODE = Object.assign({}, CODE, (csnap.data() || {}).code || {});
    try { localStorage.setItem(LS_KEY, JSON.stringify(S)); localStorage.setItem(LS_CODE, JSON.stringify(CODE)); } catch (e) {}
    setSync("compte");
    if (!snap.exists && (Object.keys(S.done).length || Object.keys(S.ex).length)) pushRemote();
    if (!csnap.exists && Object.keys(CODE).length) pushCode();
    const a = document.activeElement;
    if (!(a && (a.tagName === "TEXTAREA" || a.tagName === "INPUT"))) render(); else updateGlobal();
  } catch (e) { /* on reste en local */ }
}

/* ================================================================ calculs */
const passMark = q => Math.ceil(0.75 * q.questions.length);
function quizPassed(id) { const q = C.quizzes[id]; return q && (S.quiz[id] ?? 0) >= passMark(q); }
function unitsOf(id) {
  const it = ITEM(id); if (!it) return [0, 0];
  if (it.kind === "quiz") return [2, quizPassed(id) ? 2 : 0];
  const ex = it.exercises || [];
  return [1 + ex.length, (S.done[id] ? 1 : 0) + ex.filter(e => S.ex[e.id]).length];
}
function statsOf(ids) { let t = 0, d = 0; for (const id of ids) { const [a, b] = unitsOf(id); t += a; d += b; } return { total: t, done: d, p: pct(d, t) }; }
function moduleStats(M) { return statsOf(moduleItems(M)); }
function coverage(M) { const n = M.sections.length; const c = M.sections.filter(s => s.lecons.length).length; return { n, c, p: pct(c, n) }; }
function trackStats(T) { const ids = new Set(); for (const M of T.modules) for (const id of moduleItems(M)) ids.add(id); return statsOf([...ids]); }
function globalStats() { return statsOf(ORDER).p; }
function itemState(id) {
  const it = ITEM(id); if (!it) return "";
  if (it.kind === "quiz") { const s = S.quiz[id]; return quizPassed(id) ? "done" : s ? "half" : ""; }
  if (S.done[id]) return "done";
  return (it.exercises || []).some(e => S.ex[e.id]) ? "half" : "";
}
function nextItem() { return ORDER.find(id => itemState(id) !== "done") || null; }
function streak() {
  const set = new Set(S.days); let n = 0; const d = new Date();
  if (!set.has(today())) d.setDate(d.getDate() - 1);
  for (;;) { const k = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`; if (!set.has(k)) break; n++; d.setDate(d.getDate() - 1); }
  return n;
}
function weekIds(w) { const ids = []; for (const mid of w.modules) for (const id of moduleItems(MOD[mid].M)) if (!ids.includes(id)) ids.push(id); return ids; }
function currentWeek() {
  if (S.week) return S.week;
  for (const w of C.plan) { const s = statsOf(weekIds(w)); if (s.total && s.p < 100) return w.semaine; }
  return C.plan[C.plan.length - 1].semaine;
}
function updateGlobal() {
  if (!C) return;
  const g = globalStats();
  $("#gmeter").style.width = g + "%";
  $("#gpct").textContent = g + " %";
}
function maybeAutoDone(it) {
  if (!it.exercises || !it.exercises.length) return;
  if (it.exercises.every(e => S.ex[e.id]) && !S.done[it.id]) { S.done[it.id] = true; save(); const b = $(".done-btn"); if (b) setDoneBtn(b, it); }
}

/* ================================================================ Python (Pyodide) */
const PYODIDE_URL = "https://cdn.jsdelivr.net/pyodide/v0.28.3/full/";
let pyReady = null, py = null, pyRun = null;
function loadScript(src) {
  return new Promise((res, rej) => { const s = document.createElement("script"); s.src = src; s.onload = res; s.onerror = () => rej(new Error("Impossible de charger " + src)); document.head.appendChild(s); });
}
function ensurePython(onStatus) {
  if (pyReady) return pyReady;
  pyReady = (async () => {
    onStatus && onStatus("Chargement de Python dans ton navigateur (une seule fois, environ 10 Mo)…");
    await loadScript(PYODIDE_URL + "pyodide.js");
    py = await loadPyodide({ indexURL: PYODIDE_URL });
    for (const [name, src] of Object.entries(C.labs)) py.FS.writeFile(name, src);
    py.FS.writeFile("runner.py", C.runner);
    py.runPython("import sys\nsys.path.insert(0, '.')\nimport pxshim, runner\nasync def _run(code, key, check, fresh):\n    return await runner.run_async(code, key, check if check else None, bool(fresh))");
    pyRun = py.globals.get("_run");
    onStatus && onStatus("Chargement des jeux de données…");
    for (const f of ["penguins.csv", "titanic.csv", "tips.csv"]) py.FS.writeFile(f, await (await fetch("data/" + f)).text());
    return py;
  })();
  pyReady.catch(() => { pyReady = null; });
  return pyReady;
}
async function runPython(code, key, check, fresh, onStatus) {
  await ensurePython(onStatus);
  const all = code + "\n" + (check || "");
  const LOCAL = /^\s*(?:import|from)\s+(plotly|fakeapi|brewly|llm|cloudsync|immo|paiements|minifast|pxshim)\b.*$/gm;
  const scan = all.replace(LOCAL, "");
  let needs = "";
  if (/\bbrewly\b/.test(all)) needs += "import sqlite3\n";
  if (/\b(immo|paiements)\b/.test(all)) needs += "import numpy\nimport pandas\n";
  try { onStatus && onStatus("Chargement des bibliothèques nécessaires…"); await py.loadPackagesFromImports(needs + scan); } catch (e) {}
  if (needs) { try { await py.loadPackage("sqlite3"); } catch (e) {} }
  onStatus && onStatus("Exécution…");
  await sleep(30);
  return JSON.parse(await pyRun(code, key, check || "", !!fresh));
}

/* ================================================================ graphiques Plotly */
let plotlyReady = null;
function ensurePlotly() {
  if (!plotlyReady) { plotlyReady = loadScript("https://cdn.plot.ly/plotly-2.35.2.min.js"); plotlyReady.catch(() => { plotlyReady = null; }); }
  return plotlyReady;
}
function cssVar(n) { return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); }
async function drawFig(el, json) {
  await ensurePlotly();
  const fig = JSON.parse(json);
  const ink = cssVar("--ink"), line = cssVar("--line"), muted = cssVar("--muted");
  const lay = Object.assign({
    paper_bgcolor: "rgba(0,0,0,0)", plot_bgcolor: "rgba(0,0,0,0)",
    font: { family: "IBM Plex Sans, sans-serif", color: ink, size: 12 },
    margin: { l: 56, r: 16, t: fig.layout.title ? 48 : 16, b: 48 },
    colorway: [cssVar("--accent"), "#e0a100", cssVar("--ok"), "#c2410c", "#8b5cf6", "#0e8a9a"], legend: {},
  }, fig.layout);
  for (const ax of ["xaxis", "yaxis"]) lay[ax] = Object.assign({ gridcolor: line, zerolinecolor: line, linecolor: line, tickfont: { color: muted } }, fig.layout[ax] || {});
  if (lay.title) lay.title = Object.assign({ x: 0.02, font: { family: "Bricolage Grotesque, sans-serif", size: 16 } }, lay.title);
  window.Plotly.newPlot(el, fig.data, lay, { responsive: true, displayModeBar: false });
}

/* ================================================================ éditeur */
function highlight(code, lang = "python") {
  if (window.hljs && hljs.getLanguage(lang)) { try { return hljs.highlight(code, { language: lang, ignoreIllegals: true }).value; } catch (e) {} }
  return esc(code);
}
function makeEditor(code, onChange, onRun) {
  const wrap = h(`<div class="ed"><pre aria-hidden="true"><code></code></pre><textarea spellcheck="false" autocapitalize="off" autocomplete="off" autocorrect="off" aria-label="Éditeur de code Python"></textarea></div>`);
  const ta = $("textarea", wrap), pre = $("pre", wrap), co = $("code", wrap);
  let escaped = false;
  const sync = () => { co.innerHTML = highlight(ta.value) + "\n"; pre.scrollLeft = ta.scrollLeft; };
  ta.value = code; sync();
  ta.addEventListener("input", () => { sync(); onChange && onChange(ta.value); });
  ta.addEventListener("scroll", () => { pre.scrollLeft = ta.scrollLeft; });
  ta.addEventListener("keydown", e => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); onRun && onRun(); return; }
    if (e.key === "Escape") { escaped = true; return; }
    if (e.key === "Tab" && !escaped && !e.shiftKey) { e.preventDefault(); insert("    "); return; }
    if (e.key === "Tab") { escaped = false; return; }
    if (e.key === "Enter" && !e.shiftKey && !e.altKey) {
      const s = ta.selectionStart, before = ta.value.slice(0, s);
      const cur = before.slice(before.lastIndexOf("\n") + 1);
      let ind = (cur.match(/^\s*/) || [""])[0];
      if (/:\s*$/.test(cur)) ind += "    ";
      e.preventDefault(); insert("\n" + ind);
    }
  });
  function insert(txt) { ta.setRangeText(txt, ta.selectionStart, ta.selectionEnd, "end"); ta.dispatchEvent(new Event("input")); }
  return { el: wrap, get: () => ta.value, set: v => { ta.value = v; sync(); onChange && onChange(v); } };
}

/* ================================================================ sorties */
const ERR_FR = { NameError: "Nom inconnu", SyntaxError: "Erreur de syntaxe", IndentationError: "Erreur d'indentation", TypeError: "Erreur de type", KeyError: "Clé introuvable", IndexError: "Indice hors limites", ZeroDivisionError: "Division par zéro", AttributeError: "Attribut inconnu", ValueError: "Valeur invalide", ModuleNotFoundError: "Module introuvable", ImportError: "Import impossible", OperationalError: "Erreur SQL", DatabaseError: "Erreur SQL" };
function renderOutput(box, r) {
  box.innerHTML = "";
  if (r.stdout) box.appendChild(h(`<div class="out"><pre>${esc(r.stdout)}</pre></div>`));
  if (r.stderr && !r.error) box.appendChild(h(`<div class="out"><pre class="muted">${esc(r.stderr)}</pre></div>`));
  if (r.result) {
    const o = h(`<div class="out"></div>`);
    if (r.result.html) { o.appendChild(h(`<div class="res">${r.result.html}</div>`)); if (r.result.text) o.appendChild(h(`<div class="note">${esc(r.result.text)}</div>`)); }
    else o.appendChild(h(`<pre>${esc(r.result.text)}</pre>`));
    box.appendChild(o);
  }
  for (const f of r.figs || []) { const o = h(`<div class="out"><div class="plot"></div></div>`); box.appendChild(o); drawFig($(".plot", o), f).catch(() => { o.innerHTML = `<div class="loading">Le graphique n'a pas pu s'afficher (bibliothèque Plotly indisponible).</div>`; }); }
  for (const src of r.images || []) box.appendChild(h(`<div class="out"><img alt="Graphique matplotlib" src="${src}"></div>`));
  if (r.error) {
    const e = r.error;
    box.appendChild(h(`<div class="out err"><div class="head">${esc(ERR_FR[e.type] || e.type)}${e.line ? ` · ligne ${e.line}` : ""} — <span style="font-weight:400">${esc(e.type)}: ${esc(e.message)}</span></div>${e.source ? `<div class="src">${esc(e.source)}</div>` : ""}${e.hint ? `<div class="hint">${esc(e.hint)}</div>` : ""}</div>`));
  }
  if (!box.children.length && !r.check) box.appendChild(h(`<div class="out"><div class="note">Exécuté, sans rien à afficher.</div></div>`));
}
const loadErr = e => `<div class="out err"><div class="head">Python n'a pas pu se charger</div><div class="hint">Vérifie ta connexion internet puis réessaie. Détail : ${esc(e.message || e)}</div></div>`;

/* ================================================================ cellules */
let execCount = 0;
function makeLessonCell(code, nsKey) {
  const cell = h(`<div class="cell"><div class="gut">In [ ]:</div><div class="cellbox"></div><div class="output" aria-live="polite"></div></div>`);
  const box = $(".cellbox", cell), out = $(".output", cell), gut = $(".gut", cell);
  const ed = makeEditor(code, null, () => go());
  box.appendChild(ed.el);
  const bar = h(`<div class="cellbar"><button class="btn small run" type="button">▶ Exécuter</button><button class="btn small ghost" type="button" data-a="reset">Réinitialiser</button><button class="btn small ghost" type="button" data-a="copy">Copier</button><span class="grow"></span><span class="lang">python</span></div>`);
  box.appendChild(bar);
  const btn = $(".run", bar);
  async function go() {
    btn.disabled = true;
    out.innerHTML = `<div class="out"><div class="loading"><span class="spin"></span><span class="st">Exécution…</span></div></div>`;
    const st = $(".st", out);
    try {
      const r = await runPython(ed.get(), nsKey, null, false, m => { if (st) st.textContent = m; });
      execCount++; gut.textContent = `In [${execCount}]:`;
      renderOutput(out, r); save();
    } catch (e) { out.innerHTML = loadErr(e); }
    btn.disabled = false;
  }
  btn.addEventListener("click", go);
  $('[data-a="reset"]', bar).addEventListener("click", () => { ed.set(code); out.innerHTML = ""; });
  $('[data-a="copy"]', bar).addEventListener("click", ev => copyText(ed.get(), ev.currentTarget));
  return cell;
}
function makeStaticCell(code, lang) {
  const label = { pycode: "python · à exécuter sur ton ordinateur", bash: "terminal", markdown: "markdown", sql: "sql", yaml: "yaml", json: "json" }[lang] || lang;
  const hl = lang === "pycode" ? "python" : lang;
  const cell = h(`<div class="cell"><div class="gut">${lang === "bash" ? "$" : ""}</div><div class="cellbox static"><pre><code>${highlight(code, hl)}</code></pre><div class="cellbar"><button class="btn small ghost" type="button">Copier</button><span class="grow"></span><span class="lang">${esc(label)}</span></div></div></div>`);
  $("button", cell).addEventListener("click", ev => copyText(code, ev.currentTarget));
  return cell;
}
async function copyText(txt, btn) {
  try { await navigator.clipboard.writeText(txt); const o = btn.textContent; btn.textContent = "Copié"; setTimeout(() => btn.textContent = o, 1400); }
  catch (e) { btn.textContent = "Copie impossible"; }
}
function enhanceProse(root, nsKey) {
  for (const code of $$("pre > code", root)) {
    const lang = ((code.className || "").match(/language-(\w+)/) || [])[1] || "text";
    const src = code.textContent.replace(/\n$/, "");
    code.parentElement.replaceWith(lang === "python" ? makeLessonCell(src, nsKey) : makeStaticCell(src, lang));
  }
  for (const t of $$("table", root)) { if (!t.parentElement.classList.contains("table-wrap")) { const w = h(`<div class="table-wrap"></div>`); t.replaceWith(w); w.appendChild(t); } }
  for (const v of $$(".viz", root)) mountViz(v, v.dataset.viz);
}

/* ================================================================ exercices */
function makeExercise(ex, n, item) {
  const card = h(`<div class="card exo" id="${ex.id}">
    <div class="exo-h"><span class="num">Exercice ${n}</span><h3>${esc(ex.title)}</h3><span class="status">À faire</span></div>
    <div class="prompt">${ex.prompt}</div>
    <div class="cell"><div class="gut"></div><div class="cellbox"></div><div class="output" aria-live="polite"></div></div>
    <div class="more"></div></div>`);
  const status = $(".status", card);
  const setStatus = () => { const ok = !!S.ex[ex.id]; status.textContent = ok ? "Réussi" : "À faire"; status.classList.toggle("ok", ok); };
  setStatus();
  const box = $(".cellbox", card), out = $(".output", card), more = $(".more", card);
  const ed = makeEditor(CODE[ex.id] ?? ex.starter, v => saveCode(ex.id, v), () => go());
  box.appendChild(ed.el);
  const bar = h(`<div class="cellbar">
    <button class="btn small primary" type="button" data-a="check">▶ Vérifier</button>
    <button class="btn small ghost" type="button" data-a="hint">Indice</button>
    <button class="btn small ghost needs-sample" type="button" data-a="tutor">Demander au tuteur</button>
    <button class="btn small ghost" type="button" data-a="sol">Solution</button>
    <span class="grow"></span>
    <button class="btn small ghost" type="button" data-a="reset" title="Revenir au code de départ">Repartir de zéro</button></div>`);
  box.appendChild(bar);
  const checkBtn = $('[data-a="check"]', bar);
  let last = null, tries = 0;
  async function go() {
    checkBtn.disabled = true;
    out.innerHTML = `<div class="out"><div class="loading"><span class="spin"></span><span class="st">Exécution…</span></div></div>`;
    const st = $(".st", out);
    try {
      const code = ed.get(); saveCode(ex.id, code);
      const r = await runPython(code, ex.id, ex.check, true, m => { if (st) st.textContent = m; });
      last = { code, r }; tries++;
      renderOutput(out, r);
      const c = r.check || { ok: false, message: "Vérification impossible." };
      out.appendChild(h(`<div class="verdict ${c.ok ? "ok" : "no"}">${c.ok ? "✓ " : "✗ "}${esc(c.message)}</div>`));
      if (c.ok && !S.ex[ex.id]) { S.ex[ex.id] = true; save(); setStatus(); maybeAutoDone(item); } else save();
    } catch (e) { out.innerHTML = loadErr(e); }
    checkBtn.disabled = false;
  }
  checkBtn.addEventListener("click", go);
  $('[data-a="hint"]', bar).addEventListener("click", () => toggle("hint", () => `<div class="reveal"><b>Indice.</b> ${esc(ex.hint)}</div>`));
  $('[data-a="sol"]', bar).addEventListener("click", () => {
    if (!S.ex[ex.id] && tries < 2 && !more.querySelector(".confirm")) {
      more.innerHTML = `<div class="reveal confirm">Essaie encore au moins une fois avant de regarder : c'est en cherchant qu'on apprend. <button class="btn small" type="button">Afficher quand même</button></div>`;
      $("button", more).addEventListener("click", showSol); return;
    }
    showSol();
  });
  function showSol() {
    more.innerHTML = "";
    const r = h(`<div class="reveal"><b>Une solution possible</b><pre><code>${highlight(ex.solution)}</code></pre><button class="btn small" type="button">Copier dans l'éditeur</button></div>`);
    $("button", r).addEventListener("click", () => { ed.set(ex.solution); more.innerHTML = ""; });
    more.appendChild(r);
  }
  function toggle(kind, mk) { if (more.dataset.k === kind) { more.innerHTML = ""; more.dataset.k = ""; } else { more.innerHTML = mk(); more.dataset.k = kind; } }
  $('[data-a="reset"]', bar).addEventListener("click", () => { ed.set(ex.starter); out.innerHTML = ""; });
  $('[data-a="tutor"]', bar).addEventListener("click", () => exerciseTutor(ex, ed.get(), last, more));
  return card;
}

/* ================================================================ tuteur (Claude) */
const caps = { sample: null, tts: null };
function mdLite(s) {
  const parts = String(s).split(/```(?:\w+)?\n?([\s\S]*?)```/g);
  let html = "";
  parts.forEach((p, i) => {
    if (i % 2 === 1) { html += `<pre><code>${esc(p.replace(/\n$/, ""))}</code></pre>`; return; }
    for (const b of p.split(/\n{2,}/).map(b => b.trim()).filter(Boolean)) {
      const t = esc(b).replace(/`([^`]+)`/g, "<code>$1</code>").replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>");
      if (/^(- |\* |\d+\. )/m.test(b)) {
        const items = t.split(/\n/).map(l => `<li>${l.replace(/^(- |\* |\d+\. )/, "")}</li>`).join("");
        html += /^\d+\. /.test(b) ? `<ol>${items}</ol>` : `<ul>${items}</ul>`;
      } else html += `<p>${t.replace(/\n/g, "<br>")}</p>`;
    }
  });
  return html;
}
const TUTOR_ROLE = "Tu es le tuteur d'une plateforme de préparation pour un adulte francophone en reconversion, inscrit aux formations FullStack AI puis Lead AI de Jedha. Il vise un très haut niveau. Tu le tutoies, tu es chaleureux, exigeant, précis et bref. Tu réponds en français.";
async function askClaude(input, target) {
  if (!caps.sample) return;
  target.innerHTML = `<div class="loading"><span class="spin"></span>Le tuteur réfléchit…</div>`;
  try {
    const r = await caps.sample(input, { cache: false, onText: ({ text }) => { target.innerHTML = mdLite(text); } });
    target.innerHTML = mdLite(r.text);
    return r.text;
  } catch (e) {
    if (e && e.code === "not_granted") { document.body.classList.remove("has-sample"); target.innerHTML = "<p>Le tuteur n'est pas disponible ici.</p>"; }
    else if (e && e.code === "rate_limited") target.innerHTML = "<p>Le tuteur reçoit trop de questions en ce moment. Réessaie dans une minute.</p>";
    else target.innerHTML = "<p>Le tuteur n'a pas pu répondre. Réessaie dans un instant.</p>";
    if (e && e.text) target.innerHTML = mdLite(e.text);
  }
}
function exerciseTutor(ex, code, last, more) {
  more.dataset.k = "tutor";
  more.innerHTML = `<div class="reveal"><b>Le tuteur</b><div class="msg ai help"></div></div>`;
  const tmp = document.createElement("div"); tmp.innerHTML = ex.prompt;
  let res = "Le code n'a pas encore été exécuté.";
  if (last && last.code === code) {
    const r = last.r;
    res = [r.stdout && `Sortie :\n${r.stdout.slice(0, 1500)}`, r.error && `Erreur : ${r.error.type}: ${r.error.message} (ligne ${r.error.line})`, r.check && `Vérification : ${r.check.message}`].filter(Boolean).join("\n") || "Exécuté sans sortie.";
  }
  askClaude(`${TUTOR_ROLE}

L'apprenant bloque sur cet exercice.
Titre : ${ex.title}
Consigne : ${tmp.textContent}

Son code actuel :
\`\`\`python
${code}
\`\`\`

Résultat de sa dernière exécution :
${res}

Pour référence (NE LA DONNE PAS) : solution attendue :
\`\`\`python
${ex.solution}
\`\`\`

Aide-le à trouver lui-même. Dis ce qui ne va pas dans SON code (ou ce qu'il reste à faire), explique la notion en jeu, et donne un indice concret pour l'étape suivante. Ne donne pas la solution complète ; un extrait d'une ou deux lignes au maximum. 120 mots maximum.`, $(".help", more));
}
function lessonTutor(it) {
  const box = h(`<section class="card tutor" aria-label="Tuteur">
    <h3>Une question sur cette leçon ?</h3>
    <p class="muted" style="margin:0;font-size:14px">Le tuteur connaît le contenu de la leçon. Demande-lui une autre explication, un exemple, une question d'entretien ou un exercice plus difficile.</p>
    <div class="thread"></div>
    <form class="ask"><label class="sr" for="ask-${it.id}">Ta question</label><textarea id="ask-${it.id}" rows="2" placeholder="Par exemple : donne-moi un exercice plus difficile sur ce sujet"></textarea><button class="btn primary" type="submit">Demander</button></form>
  </section>`);
  const thread = $(".thread", box), ta = $("textarea", box);
  const msgs = [];
  const ctx = `${TUTOR_ROLE}\n\nVoici la leçon que l'apprenant étudie, « ${it.title} » :\n\n${(it.text || "").slice(0, 7000)}\n\nRéponds à ses questions en t'appuyant sur cette leçon. 150 mots maximum, avec un court exemple de code si c'est utile.`;
  $("form", box).addEventListener("submit", async e => {
    e.preventDefault();
    const q = ta.value.trim(); if (!q) return;
    ta.value = "";
    thread.appendChild(h(`<div class="msg me">${esc(q)}</div>`));
    const a = h(`<div class="msg ai"></div>`); thread.appendChild(a);
    msgs.push({ role: "user", content: msgs.length ? q : `${ctx}\n\nQuestion : ${q}` });
    const txt = await askClaude(msgs.slice(), a);
    if (txt) msgs.push({ role: "assistant", content: txt }); else msgs.pop();
    save();
  });
  ta.addEventListener("keydown", e => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) { e.preventDefault(); $("form", box).requestSubmit(); } });
  return box;
}

/* ================================================================ lecture audio
   Lit la leçon paragraphe par paragraphe, avec un bouton ▶ sur chaque bloc et une barre de lecture.
   Moteur : la voix de Claude (capacité tts) quand elle est offerte, sinon la synthèse vocale du navigateur. */
const RATES = [0.8, 1, 1.25, 1.5];
const Reader = { segs: [], i: -1, state: "idle", tok: 0, bar: null, refused: false, follow: true,
  rate: (() => { try { return +localStorage.getItem("prepa-ai:rate") || 1; } catch (e) { return 1; } })() };
const canSpeak = () => !Reader.refused && (!!caps.tts || "speechSynthesis" in window);

function sayText(el) {
  let t = (el.innerText || el.textContent || "").replace(/^▶\s*/, "");
  t = t.replace(/→/g, ", ").replace(/≈/g, " environ ").replace(/×/g, " fois ").replace(/≤/g, " inférieur ou égal à ").replace(/≥/g, " supérieur ou égal à ")
       .replace(/[•·]/g, ", ").replace(/\s*\n+\s*/g, ". ").replace(/\s{2,}/g, " ").replace(/\.\s*\./g, ".").trim();
  return t.length > 1900 ? t.slice(0, t.lastIndexOf(" ", 1900)) + "…" : t;
}
function collectSegments(root) {
  const segs = [];
  const add = el => { if (sayText(el).length > 1) segs.push(el); };
  for (const el of $(".prose", root).children) {
    if (/^(P|H2|H3|H4)$/.test(el.tagName)) add(el);
    else if (el.tagName === "UL" || el.tagName === "OL") [...el.children].forEach(add);
    else if (el.tagName === "BLOCKQUOTE" || el.classList.contains("callout")) add(el);
    else if (el.classList.contains("table-wrap")) $$("tr", el).forEach(add);
  }
  for (const el of $$(".tasks-zone .section-t, .tasks-zone li, .ex-zone .exo", root)) {
    if (el.classList.contains("exo")) { const p = $(".prompt", el); if (p) { p.dataset.say = `${$(".num", el).textContent}. ${$("h3", el).textContent}. `; segs.push(p); } }
    else add(el);
  }
  return segs;
}
function segText(el) { return (el.dataset.say || "") + sayText(el); }

function markSegment(i) {
  $$(".reading").forEach(e => e.classList.remove("reading"));
  const el = Reader.segs[i]; if (!el) return;
  el.classList.add("reading");
  if (Reader.follow) el.scrollIntoView({ behavior: reduceMotion() ? "auto" : "smooth", block: "center" });
  updateBar();
}
function updateBar() {
  const b = Reader.bar; if (!b) return;
  const n = Reader.segs.length, i = Math.max(0, Reader.i);
  $(".rd-play", b).innerHTML = Reader.state === "playing" ? "❚❚" : "▶";
  $(".rd-play", b).setAttribute("aria-label", Reader.state === "playing" ? "Pause" : "Lecture");
  $(".rd-pos", b).textContent = Reader.state === "done" ? "Fin de la leçon" : `Paragraphe ${i + 1} / ${n}`;
  $(".rd-rate", b).textContent = String(Reader.rate).replace(".", ",") + "×";
  $(".rd-fill", b).style.width = `${n ? ((Reader.state === "done" ? n : i) / n) * 100 : 0}%`;
}
function showBar() {
  if (Reader.bar) return;
  const b = h(`<div class="reader" role="region" aria-label="Lecture audio">
    <div class="rd-track"><i class="rd-fill"></i></div>
    <div class="rd-in">
      <button type="button" class="rd-btn rd-prev" aria-label="Paragraphe précédent">⏮</button>
      <button type="button" class="rd-btn rd-play big" aria-label="Pause">❚❚</button>
      <button type="button" class="rd-btn rd-next" aria-label="Paragraphe suivant">⏭</button>
      <span class="rd-pos tab"></span>
      <button type="button" class="rd-btn rd-rate" aria-label="Vitesse de lecture"></button>
      <button type="button" class="rd-btn rd-close" aria-label="Arrêter la lecture">✕</button>
    </div></div>`);
  $(".rd-prev", b).addEventListener("click", () => readFrom(Math.max(0, Reader.i - 1)));
  $(".rd-next", b).addEventListener("click", () => { if (Reader.i < Reader.segs.length - 1) readFrom(Reader.i + 1); });
  $(".rd-play", b).addEventListener("click", togglePause);
  $(".rd-rate", b).addEventListener("click", () => {
    Reader.rate = RATES[(RATES.indexOf(Reader.rate) + 1) % RATES.length] || 1;
    try { localStorage.setItem("prepa-ai:rate", Reader.rate); } catch (e) {}
    if (caps.tts && Reader.engine === "claude") { try { caps.tts.setRate?.(Reader.rate); } catch (e) {} }
    else if (Reader.state === "playing") readFrom(Reader.i);
    updateBar();
  });
  $(".rd-close", b).addEventListener("click", stopReading);
  document.body.appendChild(b); document.body.classList.add("reading-on");
  Reader.bar = b;
}
function stopReading() {
  Reader.tok++;
  if (Reader.engine === "claude" && caps.tts) caps.tts.stop().catch(() => {});
  if ("speechSynthesis" in window) speechSynthesis.cancel();
  Reader.state = "idle"; Reader.i = -1;
  $$(".reading").forEach(e => e.classList.remove("reading"));
  if (Reader.bar) { Reader.bar.remove(); Reader.bar = null; }
  document.body.classList.remove("reading-on");
  $$(".listen-btn").forEach(b => b.textContent = "🎧 Écouter la leçon");
}
function togglePause() {
  if (Reader.state === "playing") {
    Reader.state = "paused";
    if (Reader.engine === "claude") caps.tts.pause().catch(() => {});
    else { Reader.tok++; speechSynthesis.cancel(); }
  } else if (Reader.state === "paused") {
    if (Reader.engine === "claude") { Reader.state = "playing"; caps.tts.resume().catch(() => {}); }
    else readFrom(Reader.i);
  } else readFrom(Reader.state === "done" ? 0 : Math.max(0, Reader.i));
  updateBar();
}
function finishReading() { Reader.state = "done"; $$(".reading").forEach(e => e.classList.remove("reading")); updateBar(); }

/* --- moteur 1 : la voix de Claude, toute la suite de la leçon en une lecture --- */
function readWithClaude(i, tok) {
  Reader.engine = "claude";
  const lines = Reader.segs.slice(i, i + 100).map((el, k) => ({ text: segText(el), id: "s" + (i + k), language: "fr" }));
  caps.tts.speak(lines, { rate: Reader.rate, language: "fr" }).then(() => {
    if (tok !== Reader.tok) return;
    if (i + 100 < Reader.segs.length) readFrom(i + 100); else finishReading();
  }).catch(e => {
    if (tok !== Reader.tok) return;
    if (e && (e.code === "not_granted" || e.code === "unavailable")) { Reader.refused = true; document.body.classList.remove("can-listen"); stopReading(); return; }
    if (e && e.code === "stopped" && e.reason === "viewer_stopped") { stopReading(); return; }
    if (e && e.code === "stopped") return;
    Reader.state = "paused"; updateBar();
  });
}
/* --- moteur 2 : la synthèse vocale du navigateur, phrase par phrase --- */
let frVoice = null;
function pickVoice() {
  if (!("speechSynthesis" in window)) return null;
  const v = speechSynthesis.getVoices().filter(v => /^fr(-|_|$)/i.test(v.lang));
  const score = x => (/fr[-_]FR/i.test(x.lang) ? 4 : 0) + (/premium|enhanced|natural|neural|google|amélie|amelie|thomas|audrey|denise|henri|marie/i.test(x.name) ? 3 : 0) + (x.localService ? 1 : 0);
  frVoice = v.sort((a, b) => score(b) - score(a))[0] || null;
  return frVoice;
}
if ("speechSynthesis" in window) { pickVoice(); speechSynthesis.addEventListener?.("voiceschanged", pickVoice); }
function chunks(text) {
  const out = []; let cur = "";
  for (const s of text.match(/[^.!?;:]+[.!?;:]*\s*/g) || [text]) {
    if ((cur + s).length > 220 && cur) { out.push(cur); cur = s; } else cur += s;
  }
  if (cur.trim()) out.push(cur);
  return out;
}
function readWithBrowser(i, tok) {
  Reader.engine = "browser";
  speechSynthesis.cancel();
  const parts = chunks(segText(Reader.segs[i]));
  let k = 0;
  const next = () => {
    if (tok !== Reader.tok) return;
    if (k >= parts.length) { if (i + 1 < Reader.segs.length) readFrom(i + 1, true); else finishReading(); return; }
    const u = new SpeechSynthesisUtterance(parts[k++]);
    u.lang = frVoice ? frVoice.lang : "fr-FR"; if (frVoice) u.voice = frVoice;
    u.rate = Reader.rate;
    u.onend = next;
    u.onerror = e => { if (tok === Reader.tok && e.error !== "interrupted" && e.error !== "canceled") next(); };
    speechSynthesis.speak(u);
  };
  next();
}
function readFrom(i, auto) {
  if (!canSpeak() || !Reader.segs[i]) return;
  const tok = ++Reader.tok;
  Reader.i = i; Reader.state = "playing";
  showBar(); markSegment(i);
  $$(".listen-btn").forEach(b => b.textContent = "■ Arrêter la lecture");
  if (caps.tts && !Reader.refused) {
    if (auto && Reader.engine === "claude") return;
    readWithClaude(i, tok);
  } else readWithBrowser(i, tok);
}
if (!window.__readerHooks) {
  window.__readerHooks = true;
  window.addEventListener("hashchange", stopReading);
  document.addEventListener("visibilitychange", () => { if (document.hidden && Reader.engine === "browser" && Reader.state === "playing") togglePause(); });
  let wheelT = 0;
  window.addEventListener("wheel", () => { Reader.follow = false; clearTimeout(wheelT); wheelT = setTimeout(() => Reader.follow = true, 6000); }, { passive: true });
  window.addEventListener("touchmove", () => { Reader.follow = false; clearTimeout(wheelT); wheelT = setTimeout(() => Reader.follow = true, 6000); }, { passive: true });
}

/* Ajoute les boutons ▶ à chaque bloc lisible, et renvoie le bouton « Écouter la leçon ». */
function setupReader(root) {
  Reader.segs = collectSegments(root);
  (Reader.unsub || []).forEach(f => { try { f(); } catch (e) {} });
  Reader.unsub = [];
  if (caps.tts) {
    Reader.unsub.push(caps.tts.onLine?.(({ id }) => { if (id && Reader.engine === "claude") { const n = +id.slice(1); if (Reader.segs[n]) { Reader.i = n; markSegment(n); } } }));
    Reader.unsub.push(caps.tts.onState?.(({ state, reason }) => {
      if (Reader.engine !== "claude") return;
      if (state === "paused") { Reader.state = "paused"; updateBar(); }
      else if (state === "speaking" && Reader.state === "paused") { Reader.state = "playing"; updateBar(); }
      else if (state === "idle" && (reason === "viewer_stopped" || reason === "hidden" || reason === "time_limit")) stopReading();
    }));
    Reader.unsub = Reader.unsub.filter(Boolean);
  }
  Reader.segs.forEach((el, i) => {
    const b = h(`<button type="button" class="say" aria-label="Écouter à partir d'ici" title="Écouter à partir d'ici">▶</button>`);
    b.addEventListener("click", e => { e.stopPropagation(); Reader.follow = true; readFrom(i); });
    const cible = el.tagName === "TR" ? el.cells[0] : el;
    el.classList.add("speakable");
    cible.insertBefore(b, cible.firstChild);
  });
  const btn = h(`<button class="btn small listen-btn needs-listen" type="button">🎧 Écouter la leçon</button>`);
  btn.addEventListener("click", () => { if (Reader.state === "idle") { Reader.follow = true; readFrom(0); } else stopReading(); });
  return btn;
}

/* ================================================================ vues */
const app = () => $("#app");
function setTop(back) {
  const b = $("#back");
  if (back) { b.hidden = false; b.href = back.href; $("span", b).textContent = back.label; $("#brand").hidden = true; }
  else { b.hidden = true; $("#brand").hidden = false; }
}
const dot = st => `<span class="dot ${st}" aria-hidden="true"></span>`;
function label(id) { const it = ITEM(id); return it ? it.title : id; }
function meta(id) {
  const it = ITEM(id); if (!it) return "";
  if (it.kind === "quiz") { const s = S.quiz[id]; return s != null ? `${s}/${it.questions.length}` : `${it.questions.length} questions`; }
  const n = (it.exercises || []).length;
  return n ? `${it.exercises.filter(e => S.ex[e.id]).length}/${n} exos` : `${it.minutes || 30} min`;
}
const kindLabel = id => { const it = ITEM(id); return it.kind === "quiz" ? "Quiz" : it.kind === "project" ? "Projet" : "Leçon"; };
const shortLabel = id => { const l = label(id); return l.length > 34 ? l.slice(0, 32) + "…" : l; };
const itemRow = id => `<li><a href="#${id}">${dot(itemState(id))}<span>${esc(label(id))}</span><span class="meta tab">${esc(meta(id))}</span></a></li>`;

function viewHome() {
  setTop(null);
  const g = globalStats();
  const nx = nextItem();
  const allLessons = Object.values(C.items);
  const nLessons = allLessons.filter(i => S.done[i.id]).length;
  const nEx = allLessons.reduce((a, i) => a + i.exercises.filter(e => S.ex[e.id]).length, 0);
  const totEx = allLessons.reduce((a, i) => a + i.exercises.length, 0);
  const qs = Object.keys(C.quizzes); const nQuiz = qs.filter(quizPassed).length;
  let jtxt = "";
  if (S.start) {
    const d = Math.ceil((new Date(S.start + "T09:00:00") - new Date()) / 86400000);
    jtxt = d > 0 ? `<b class="tab">J-${d}</b> avant le premier jour` : d === 0 ? `<b>C'est aujourd'hui !</b>` : `<b>La formation a commencé</b>`;
  }
  const cw = currentWeek();
  const T = C.tracks.find(t => t.id === S.track) || C.tracks[0];
  const el = h(`<div>
    <section class="hero">
      <div>
        <div class="eyebrow">Essentials → FullStack → Lead<br>${C.plan.length} semaines de préparation</div>
        <h1>Arrive chez Jedha <span class="mark">avec une longueur d'avance</span>.</h1>
        <p class="lede">La plateforme suit les modules officiels de tes programmes. Chaque leçon s'exécute ici même, chaque exercice est corrigé automatiquement, et un tuteur IA t'accompagne.</p>
        <div class="jday"><label for="start">Début de la formation</label><input type="date" id="start" value="${S.start || ""}"> <span>${jtxt}</span></div>
      </div>
      <div class="card resume">
        <div><div class="eyebrow">Progression globale</div><div class="big tab">${g}<small> %</small></div></div>
        <div><div class="epochs" style="grid-template-columns:repeat(${C.tracks.length},1fr)">${C.tracks.map(t => `<div><i style="width:${trackStats(t).p}%"></i></div>`).join("")}</div>
        <div class="epochs-l" style="grid-template-columns:repeat(${C.tracks.length},1fr)">${C.tracks.map(t => `<span title="${esc(t.nom)}">${esc(t.nom.split(" ")[0])} ${trackStats(t).p} %</span>`).join("")}</div></div>
        ${nx ? `<a class="continue" href="#${nx}"><span class="eyebrow">${g === 0 ? "Commencer" : "Reprendre"} · ${esc(MOD[HOME[nx]].M.titre)}</span><b>${esc(label(nx))}</b><span class="muted" style="font-size:13px">${esc(kindLabel(nx))} · ${esc(meta(nx))} →</span></a>`
              : `<div class="continue"><b>Tu as tout terminé. Bravo !</b><span class="muted">Refais les quiz, peaufine tes projets, et prépare ton Demo Day.</span></div>`}
      </div>
    </section>
    <section class="stats">
      <div class="card stat"><b class="tab">${nLessons}/${allLessons.length}</b><span>leçons et projets terminés</span></div>
      <div class="card stat"><b class="tab">${nEx}/${totEx}</b><span>exercices réussis</span></div>
      <div class="card stat"><b class="tab">${nQuiz}/${qs.length}</b><span>quiz réussis (75 % ou plus)</span></div>
      <div class="card stat"><b class="tab">${S.days.length}</b><span>jours de pratique · série de ${streak()}</span></div>
    </section>
    <div class="section-h"><h2>Ton plan de ${C.plan.length} semaines</h2><p>20 h et plus par semaine : Essentials d'abord, puis le FullStack</p></div>
    <div class="plan" role="list" style="--n:${C.plan.length}">${C.plan.map(w => { const s = statsOf(weekIds(w)); return `<button class="wk ${w.semaine === cw ? "cur" : ""}" type="button" data-w="${w.semaine}" role="listitem"><span class="n">S${w.semaine}</span><span class="t">${esc(w.titre)}</span><div class="bar"><i style="width:${s.p}%"></i></div></button>`; }).join("")}</div>
    <div class="card wkdetail"></div>
    <div class="section-h"><h2>Les programmes</h2><p>Les modules officiels, et ce que la plateforme couvre déjà</p></div>
    <div class="tabs" role="tablist">${C.tracks.map(t => `<button role="tab" type="button" data-t="${t.id}" aria-selected="${t.id === T.id}">${esc(t.nom)}</button>`).join("")}</div>
    <p class="muted" style="margin:0 0 12px">${esc(T.intro)}</p>
    <section class="modules">${T.modules.map(moduleCard).join("")}</section>
    <section class="extras">
      <a class="card" href="#jour-j"><span class="eyebrow">Checklist</span><b>Prêt pour le jour J ?</b><span class="muted" style="font-size:14px">${C.jourj.filter((_, i) => S.tasks["jj-" + i]).length}/${C.jourj.length} points validés</span></a>
      <a class="card" href="#ressources"><span class="eyebrow">Pour aller plus loin</span><b>Ressources gratuites</b><span class="muted" style="font-size:14px">Cours, vidéos et documentations, module par module</span></a>
    </section>
    <p class="sync" id="sync"></p>
  </div>`);
  app().replaceChildren(el);
  setSync(store.mode);
  const showWeek = n => {
    const w = C.plan.find(x => x.semaine === n);
    const ids = weekIds(w);
    const s = statsOf(ids);
    $(".wkdetail", el).innerHTML = `<div class="eyebrow">Semaine ${w.semaine} · ${esc(w.heures)} · ${s.p} % fait</div><h3>${esc(w.titre)}</h3>
      <ul>${w.modules.map(mid => { const { M, T } = MOD[mid]; const cv = coverage(M); return `<li><a href="#m-${mid}">${esc(M.titre)}</a> <span class="muted" style="font-size:13px">· ${esc(T.nom)} · ${cv.p} % du module préparé ici</span></li>`; }).join("")}</ul>
      <div class="lesson-tools"><button class="btn small" type="button" data-cur="${n}">${S.week === n ? "✓ Ma semaine en cours" : "Définir comme ma semaine en cours"}</button></div>`;
    $$(".wk", el).forEach(b => b.classList.toggle("cur", +b.dataset.w === n));
    $("[data-cur]", el).addEventListener("click", () => { S.week = S.week === n ? null : n; save(); showWeek(n); });
  };
  showWeek(cw);
  $$(".wk", el).forEach(b => b.addEventListener("click", () => showWeek(+b.dataset.w)));
  $$(".tabs button", el).forEach(b => b.addEventListener("click", () => { S.track = b.dataset.t; save(); render(); }));
  $("#start", el).addEventListener("change", e => { S.start = e.target.value || null; save(); render(); });
}
function moduleCard(M, i) {
  const s = moduleStats(M), cv = coverage(M);
  return `<a class="card mod" href="#m-${M.id}">
    <span class="num"><span>${M.jours ? `${M.jours} jour${M.jours > 1 ? "s" : ""} chez Jedha` : "Avant la formation"}</span><span>S${M.semaine}</span></span>
    <b>${esc(M.titre)}</b><span class="obj">${esc(M.objectif)}</span>
    <div class="meters">
      <div class="row"><span>Préparé ici</span><span>${cv.c}/${cv.n} sections</span></div>
      <div class="bar cov"><i style="width:${cv.p}%"></i></div>
      <div class="row"><span>Ta progression</span><span>${s.total ? s.p + " %" : "—"}</span></div>
      <div class="bar"><i style="width:${s.p}%"></i></div>
    </div></a>`;
}
function viewModule(mid) {
  const { M, T } = MOD[mid];
  setTop({ href: "#accueil", label: "Accueil" });
  const s = moduleStats(M), cv = coverage(M);
  const el = h(`<div class="read">
    <div class="pagehead"><div class="crumbs"><a href="#accueil">Accueil</a><span>/</span><span>${esc(T.nom)}</span></div>
      <h1>${esc(M.titre)}</h1><p>${esc(M.objectif)}</p>
      <div class="lesson-tools"><span class="badge jedha">${M.jours ? `${M.jours} jour${M.jours > 1 ? "s" : ""} chez Jedha` : "Avant la formation"}</span><span class="badge">Semaine ${M.semaine} du plan</span><span class="badge ok">${cv.c}/${cv.n} sections préparées ici</span>${s.total ? `<span class="badge">${s.p} % fait</span>` : ""}</div>
    </div>
    <h2 class="section-t" style="margin-top:8px">Le programme, section par section</h2>
    <p class="muted" style="margin:0 0 6px">Chaque bloc correspond à une section du programme Jedha. En dessous, les leçons qui t'y préparent.</p>
    ${M.sections.map(sec => `<div class="card sec"><div class="sec-h"><b>${esc(sec.titre)}</b>${sec.lecons.length ? `<span class="badge ok">Préparé</span>` : `<span class="badge soon">Prochaine vague</span>`}${sec.local ? `<span class="badge local">Sur ton ordinateur</span>` : ""}</div>
      ${sec.lecons.length ? `<ul class="items">${sec.lecons.map(itemRow).join("")}</ul>` : `<p class="soon-txt">Cette section sera ajoutée dans une prochaine vague de contenu.${sec.local ? " Elle se pratiquera surtout sur ton ordinateur, avec des guides pas à pas." : ""}</p>`}</div>`).join("")}
    ${M.projets.length || M.quiz.length ? `<h2 class="section-t">Projets et quiz</h2><nav class="card list" style="padding:6px">${[...M.projets, ...M.quiz].map(id => `<a href="#${id}">${dot(itemState(id))}<span><span class="k">${kindLabel(id)}</span><br><b>${esc(label(id))}</b></span><span class="meta muted tab" style="font-size:13px">${esc(meta(id))}</span></a>`).join("")}</nav>` : ""}
  </div>`);
  app().replaceChildren(el);
}
function setDoneBtn(b, it) { const on = !!S.done[it.id]; b.classList.toggle("on", on); b.textContent = on ? "✓ Terminé" : "Marquer comme terminé"; }
function navLinks(id) {
  const pos = ORDER.indexOf(id), prev = ORDER[pos - 1], next = ORDER[pos + 1];
  return { prev, next };
}
function viewLesson(it) {
  const { M, T } = MOD[HOME[it.id]];
  setTop({ href: "#m-" + M.id, label: M.titre.length > 26 ? M.titre.slice(0, 24) + "…" : M.titre });
  const { prev, next } = navLinks(it.id);
  const el = h(`<article class="read">
    <div class="pagehead">
      <div class="crumbs"><a href="#accueil">Accueil</a><span>/</span><a href="#m-${M.id}">${esc(M.titre)}</a><span>/</span><span>${it.kind === "project" ? "Projet" : "Leçon"}</span></div>
      <h1>${esc(it.title)}</h1>
      <p class="tab">${it.minutes ? `${it.minutes} min` : ""}${it.exercises.length ? ` · ${it.exercises.length} exercice${it.exercises.length > 1 ? "s" : ""}` : ""}${it.tasks.length ? ` · ${it.tasks.length} action${it.tasks.length > 1 ? "s" : ""} sur ton ordinateur` : ""}</p>
      <div class="lesson-tools"></div>
    </div>
    <div class="prose">${it.body}</div>
    <div class="tasks-zone"></div><div class="ex-zone"></div><div class="tutor-zone"></div>
    <div class="foot">
      ${prev ? `<a class="btn ghost" href="#${prev}">← ${esc(shortLabel(prev))}</a>` : "<span></span>"}
      <button class="btn done-btn" type="button"></button>
      ${next ? `<a class="btn primary" href="#${next}">${esc(shortLabel(next))} →</a>` : "<span></span>"}
    </div></article>`);
  enhanceProse($(".prose", el), it.id);
  if (it.tasks.length) {
    const z = $(".tasks-zone", el);
    z.appendChild(h(`<h2 class="section-t">À faire sur ton ordinateur</h2>`));
    const ul = h(`<ul class="card tasks"></ul>`);
    it.tasks.forEach((t, i) => {
      const key = `${it.id}-t${i}`;
      const li = h(`<li><label><input type="checkbox" id="${key}" ${S.tasks[key] ? "checked" : ""}><span>${esc(t)}</span></label></li>`);
      $("input", li).addEventListener("change", e => { if (e.target.checked) S.tasks[key] = true; else delete S.tasks[key]; save(); });
      ul.appendChild(li);
    });
    z.appendChild(ul);
  }
  if (it.exercises.length) {
    const z = $(".ex-zone", el);
    z.appendChild(h(`<h2 class="section-t">Exercices</h2>`));
    z.appendChild(h(`<p class="muted" style="margin:0 0 6px">Écris ton code, puis clique sur Vérifier (ou Ctrl + Entrée). Ton code est sauvegardé automatiquement.</p>`));
    it.exercises.forEach((ex, i) => z.appendChild(makeExercise(ex, i + 1, it)));
  }
  $(".tutor-zone", el).appendChild(lessonTutor(it));
  $(".lesson-tools", el).appendChild(setupReader(el));
  const db = $(".done-btn", el);
  setDoneBtn(db, it);
  db.addEventListener("click", () => { if (S.done[it.id]) delete S.done[it.id]; else S.done[it.id] = true; save(); setDoneBtn(db, it); });
  app().replaceChildren(el);
  if (it.body.includes("language-python") || it.exercises.length) setTimeout(() => ensurePython().catch(() => {}), 600);
}
function viewQuiz(q) {
  const { M } = MOD[HOME[q.id]];
  setTop({ href: "#m-" + M.id, label: M.titre.length > 26 ? M.titre.slice(0, 24) + "…" : M.titre });
  const { next } = navLinks(q.id);
  const n = q.questions.length, need = passMark(q), best = S.quiz[q.id];
  const el = h(`<div class="read">
    <div class="pagehead"><div class="crumbs"><a href="#accueil">Accueil</a><span>/</span><a href="#m-${M.id}">${esc(M.titre)}</a><span>/</span><span>Quiz</span></div>
    <h1>${esc(q.title)}</h1><p>${n} questions. Il faut ${need} bonnes réponses pour le valider.${best != null ? ` Meilleur score : <b class="tab">${best}/${n}</b>.` : ""}</p></div>
    <form class="quiz">${q.questions.map((x, i) => `<fieldset class="card q" style="border:1px solid var(--line)"><legend class="sr">Question ${i + 1}</legend><h3>${i + 1}. ${esc(x.q)}</h3>${x.options.map((o, j) => `<label><input type="radio" name="q${i}" value="${j}"><span>${esc(o)}</span></label>`).join("")}<div class="exp" hidden></div></fieldset>`).join("")}
    <div class="score-zone"></div>
    <div class="foot"><button class="btn primary" type="submit">Valider mes réponses</button><button class="btn ghost" type="button" data-a="again" hidden>Recommencer</button>${next ? `<a class="btn" href="#${next}">${esc(shortLabel(next))} →</a>` : `<a class="btn" href="#jour-j">Checklist du jour J →</a>`}</div>
    </form></div>`);
  const form = $("form", el);
  form.addEventListener("submit", e => {
    e.preventDefault();
    let score = 0;
    q.questions.forEach((x, i) => {
      const fs = $$("fieldset", form)[i];
      const v = $(`input[name="q${i}"]:checked`, fs);
      const ans = v ? +v.value : -1;
      if (ans === x.answer) score++;
      $$("label", fs).forEach((lb, j) => { lb.classList.toggle("right", j === x.answer); lb.classList.toggle("wrong", j === ans && ans !== x.answer); });
      $$("input", fs).forEach(z => z.disabled = true);
      const exp = $(".exp", fs); exp.hidden = false; exp.textContent = (ans === x.answer ? "Bonne réponse. " : ans < 0 ? "Pas de réponse. " : "Raté. ") + x.explain;
    });
    S.quiz[q.id] = Math.max(S.quiz[q.id] ?? 0, score); save();
    $(".score-zone", form).replaceChildren(h(`<div class="card score"><b class="tab">${score}/${n}</b><span>${score >= need ? "Quiz validé. Bravo !" : `Relis les explications, puis retente ta chance : il faut ${need}/${n}.`}</span></div>`));
    $('[type="submit"]', form).hidden = true; $('[data-a="again"]', form).hidden = false;
    $(".score-zone", form).scrollIntoView({ behavior: "smooth", block: "center" });
  });
  $('[data-a="again"]', form).addEventListener("click", () => viewQuiz(q));
  app().replaceChildren(el);
}
function viewJourJ() {
  setTop({ href: "#accueil", label: "Accueil" });
  const el = h(`<div class="read"><div class="pagehead"><div class="eyebrow">Checklist</div><h1>Prêt pour le jour J ?</h1><p>Coche chaque point quand il est vrai. Objectif : tout cocher avant ton premier jour chez Jedha.</p></div><ul class="card tasks"></ul></div>`);
  const ul = $("ul", el);
  C.jourj.forEach((t, i) => {
    const key = "jj-" + i;
    const li = h(`<li><label><input type="checkbox" id="${key}" ${S.tasks[key] ? "checked" : ""}><span>${esc(t)}</span></label></li>`);
    $("input", li).addEventListener("change", e => { if (e.target.checked) S.tasks[key] = true; else delete S.tasks[key]; save(); });
    ul.appendChild(li);
  });
  app().replaceChildren(el);
}
function viewResources() {
  setTop({ href: "#accueil", label: "Accueil" });
  const el = h(`<div class="read"><div class="pagehead"><div class="eyebrow">Pour aller plus loin</div><h1>Ressources gratuites</h1><p>Pour approfondir une notion, ou la voir expliquée autrement.</p></div>
    <div class="table-wrap"><table><thead><tr><th>Ressource</th><th>Module</th><th>Langue</th><th>Pour quoi faire</th></tr></thead><tbody>
    ${C.resources.map(r => `<tr><td><a href="${esc(r.url)}" target="_blank" rel="noopener">${esc(r.name)}</a></td><td>${esc(r.module)}</td><td>${esc(r.lang)}</td><td>${esc(r.why)}</td></tr>`).join("")}
    </tbody></table></div>
    <p class="muted" style="font-size:14px">Le glossaire anglais-français se trouve dans la leçon <a href="#l-4-6">L'anglais technique</a>.</p></div>`);
  app().replaceChildren(el);
}

/* ================================================================ routeur */
const route = () => (location.hash || "#accueil").slice(1) || "accueil";
function render() {
  if (!C) return;
  const id = route();
  updateGlobal();
  if (id.startsWith("m-") && MOD[id.slice(2)]) return viewModule(id.slice(2));
  if (C.quizzes[id] && HOME[id]) return viewQuiz(C.quizzes[id]);
  if (C.items[id] && HOME[id]) return viewLesson(C.items[id]);
  if (id === "jour-j") return viewJourJ();
  if (id === "ressources") return viewResources();
  return viewHome();
}
let lastRoute = null;
window.addEventListener("hashchange", () => { const r = route(); if (r !== lastRoute) { lastRoute = r; render(); window.scrollTo(0, 0); } });

/* ================================================================ démarrage */
(async function boot() {
  loadLocal();
  try { C = await (await fetch("content.json")).json(); }
  catch (e) { app().innerHTML = `<div class="boot">Le contenu n'a pas pu se charger. Recharge la page.</div>`; return; }
  indexContent();
  if ("speechSynthesis" in window) document.body.classList.add("can-listen");
  lastRoute = route();
  render();
  connectStore();
  if (window.claude && typeof window.claude.use === "function") {
    window.claude.use("sample").then(s => { if (s) { caps.sample = s; document.body.classList.add("has-sample"); } }).catch(() => {});
    window.plateformeLLMDispo = () => !!caps.sample;
    window.plateformeLLM = async msgs => {
      if (!caps.sample) throw new Error("Aucun LLM disponible sur cet appareil.");
      const arr = Array.from(msgs).map(m => ({ role: m.role, content: String(m.content) }));
      const r = await caps.sample(arr, { cache: false });
      return r.text;
    };
    window.claude.use("tts").then(t => { if (t) { caps.tts = t; document.body.classList.add("has-tts"); try { t.setRate?.(Reader.rate); } catch (e) {} if (C && C.items[route()]) render(); } }).catch(() => {});
  }
})();
