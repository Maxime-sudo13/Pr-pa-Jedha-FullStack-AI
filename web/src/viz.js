/* ================================================================ visualisations interactives
   Chaque visualisation est une fonction (el) => void qui remplit un bloc .viz. */
const NS = "http://www.w3.org/2000/svg";
const reduceMotion = () => window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
function svgEl(tag, attrs = {}, text) { const e = document.createElementNS(NS, tag); for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v); if (text != null) e.textContent = text; return e; }
function vizShell(el, title, kind) {
  el.innerHTML = `<div class="viz-h"><b>${esc(title)}</b><span class="eyebrow">${esc(kind || "interactif")}</span></div><div class="viz-b"></div><div class="viz-c"></div><div class="viz-note"></div>`;
  return { body: $(".viz-b", el), ctrl: $(".viz-c", el), note: $(".viz-note", el) };
}
function rangeCtl(ctrl, id, lab, min, max, step, val, fmt = v => v) {
  const w = h(`<label for="${id}">${esc(lab)} <input type="range" id="${id}" min="${min}" max="${max}" step="${step}" value="${val}"><output>${fmt(+val)}</output></label>`);
  const inp = $("input", w), out = $("output", w);
  inp.addEventListener("input", () => { out.textContent = fmt(+inp.value); });
  ctrl.appendChild(w);
  return inp;
}
function btnCtl(ctrl, txt, cls = "btn small") { const b = h(`<button type="button" class="${cls}">${esc(txt)}</button>`); ctrl.appendChild(b); return b; }
let vizUid = 0;
const VIZ = {};
function mountViz(el, name) {
  const f = VIZ[name];
  if (!f) { el.remove(); return; }
  try { f(el); } catch (e) { el.innerHTML = `<div class="viz-note">Cette animation n'a pas pu s'afficher.</div>`; }
}

/* ---------- POO : une classe, des objets ---------- */
VIZ.oop = el => {
  const { body, ctrl, note } = vizShell(el, "Une classe, plusieurs objets", "POO");
  const presets = [["Stylo", 1.5, 10], ["Cahier", 3.2, 1], ["Sac", 40, 1], ["Clavier", 49.9, 2], ["Lampe", 24, 1]];
  let k = 0;
  body.innerHTML = `<div class="vgrid"><div><p class="vcap">La classe (le plan)</p><pre class="json">class Article:
    tva = 0.20

    def __init__(self, nom, prix_ht, quantite):
        self.nom = nom
        self.prix_ht = prix_ht
        self.quantite = quantite

    def total_ttc(self):
        return prix_ht × quantite × (1 + tva)</pre></div><div><p class="vcap">Les objets (les exemplaires)</p><div class="objs"></div></div></div>`;
  const objs = $(".objs", body);
  const add = () => {
    if (k >= presets.length) { objs.innerHTML = ""; k = 0; }
    const [n, p, q] = presets[k++];
    const v = n.toLowerCase();
    objs.appendChild(h(`<div class="objcard"><b>${v}</b> = Article("${n}", ${p}, ${q})<br>nom = "${n}"<br>prix_ht = ${p}<br>quantite = ${q}<br>total_ttc() → <b>${(p * q * 1.2).toFixed(2)}</b></div>`));
    note.innerHTML = `Chaque objet a <b>ses propres valeurs</b> d'attributs, mais tous partagent les mêmes méthodes et l'attribut de classe <code>tva</code>. ${k} objet${k > 1 ? "s" : ""} créé${k > 1 ? "s" : ""}.`;
  };
  btnCtl(ctrl, "Créer un objet", "btn small primary").addEventListener("click", add);
  add(); add();
};

/* ---------- HTTP : requête et réponse ---------- */
VIZ.http = el => {
  const { body, ctrl, note } = vizShell(el, "Le cycle requête → réponse", "HTTP");
  const REQ = [
    { m: "GET", p: "/books/3", s: 200, t: "OK", j: { id: 3, titre: "Fondation", annee: 1951, note: { moyenne: 4.4 } } },
    { m: "GET", p: "/books/999", s: 404, t: "Not Found", j: { erreur: "Livre 999 introuvable" } },
    { m: "GET", p: "/secure", s: 401, t: "Unauthorized", j: { erreur: "Clé d'API manquante ou invalide" } },
    { m: "GET", p: "/flaky", s: 503, t: "Service Unavailable", j: { erreur: "Service indisponible" } },
  ];
  body.innerHTML = `<svg viewBox="0 0 600 150" role="img" aria-label="Animation d'une requête HTTP entre un client et un serveur"></svg><pre class="json" style="margin-top:10px"></pre>`;
  const svg = $("svg", body), pre = $("pre", body);
  const box = (x, label, sub) => { const g = svgEl("g"); g.append(svgEl("rect", { x, y: 35, width: 130, height: 80, rx: 12, class: "vz-code vz-line", "stroke-width": 1.5 }), svgEl("text", { x: x + 65, y: 70, "text-anchor": "middle", class: "vz-tb" }, label), svgEl("text", { x: x + 65, y: 90, "text-anchor": "middle", class: "vz-tm" }, sub)); svg.append(g); };
  box(10, "Ton code", "requests.get(...)"); box(460, "Serveur", "api.biblio.test");
  svg.append(svgEl("line", { x1: 140, y1: 60, x2: 460, y2: 60, class: "vz-line", "stroke-width": 2, "stroke-dasharray": "4 4" }), svgEl("line", { x1: 140, y1: 95, x2: 460, y2: 95, class: "vz-line", "stroke-width": 2, "stroke-dasharray": "4 4" }));
  const pk = svgEl("g"); const pr = svgEl("rect", { x: -60, y: -13, width: 120, height: 26, rx: 13, class: "vz-accent" }); const pt = svgEl("text", { x: 0, y: 5, "text-anchor": "middle", class: "vz-tc", style: "fill:var(--surface);font-weight:600" }, "");
  pk.append(pr, pt); pk.setAttribute("opacity", 0); svg.append(pk);
  let anim = 0;
  const move = (x0, x1, y, ms) => new Promise(res => { const t0 = performance.now(); const my = ++anim; const step = t => { if (my !== anim) return res(); const u = Math.min(1, (t - t0) / ms); const e = u < .5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2; pk.setAttribute("transform", `translate(${x0 + (x1 - x0) * e},${y})`); u < 1 ? requestAnimationFrame(step) : res(); }; requestAnimationFrame(step); });
  async function send(r) {
    pre.textContent = "…";
    pk.setAttribute("opacity", 1); pr.setAttribute("class", "vz-accent"); pt.textContent = `${r.m} ${r.p}`;
    const fast = reduceMotion();
    await move(200, 400, 60, fast ? 1 : 900);
    pr.setAttribute("class", r.s < 300 ? "vz-ok" : "vz-err"); pt.textContent = `${r.s} ${r.t}`;
    await move(400, 200, 95, fast ? 1 : 900);
    pk.setAttribute("opacity", 0);
    pre.textContent = `HTTP ${r.s} ${r.t}\nContent-Type: application/json\n\n${JSON.stringify(r.j, null, 2)}`;
    note.innerHTML = r.s < 300 ? "<b>2xx</b> : succès, le corps contient les données demandées." : r.s === 404 ? "<b>404</b> : la ressource n'existe pas. Réessayer ne sert à rien : corrige l'identifiant." : r.s === 401 ? "<b>401</b> : il manque une clé d'API valide dans l'en-tête Authorization." : "<b>503</b> : erreur temporaire du serveur. On attend un peu, puis on réessaie (backoff exponentiel).";
  }
  REQ.forEach((r, i) => btnCtl(ctrl, `${r.m} ${r.p}`, i ? "btn small" : "btn small primary").addEventListener("click", () => send(r)));
  pre.textContent = "Choisis une requête ci-dessous.";
  note.innerHTML = "Une requête part avec une <b>méthode</b> et un <b>chemin</b>, la réponse revient avec un <b>code de statut</b> et un corps JSON.";
};

/* ---------- groupby : découper, appliquer, combiner ---------- */
VIZ.groupby = el => {
  const { body, ctrl, note } = vizShell(el, "Découper → appliquer → combiner", "GROUP BY");
  const rows = [["Bastille", 12], ["Part-Dieu", 8], ["Bastille", 5], ["Chartrons", 9], ["Part-Dieu", 14], ["Bastille", 7], ["Chartrons", 3], ["Part-Dieu", 6]];
  const groups = [...new Set(rows.map(r => r[0]))];
  const AGG = { sum: ["SUM", a => a.reduce((x, y) => x + y, 0)], mean: ["AVG", a => +(a.reduce((x, y) => x + y, 0) / a.length).toFixed(2)], count: ["COUNT", a => a.length], max: ["MAX", a => Math.max(...a)] };
  let agg = "sum", step = 0;
  const draw = () => {
    const [fname, f] = AGG[agg];
    const table = (rs, colored) => `<table class="vtab"><tr><th>magasin</th><th>montant</th></tr>${rs.map(r => `<tr class="${colored ? "" : ""}"><td class="${colored ? "gcolor-" + groups.indexOf(r[0]) : ""}">${r[0]}</td><td class="${colored ? "gcolor-" + groups.indexOf(r[0]) : ""}">${r[1]}</td></tr>`).join("")}</table>`;
    let left = `<p class="vcap">Données</p>${table(rows, step >= 1)}`, right = "";
    if (step >= 1) right = `<p class="vcap">1 · Découper en groupes</p>${groups.map(g => `<div style="margin-bottom:8px">${table(rows.filter(r => r[0] === g), true)}${step >= 2 ? `<div class="vz-tc" style="font:600 12px var(--mono);padding:4px 8px">${fname}(montant) = ${f(rows.filter(r => r[0] === g).map(r => r[1]))}</div>` : ""}</div>`).join("")}`;
    if (step >= 3) left = `<p class="vcap">3 · Combiner</p><table class="vtab"><tr><th>magasin</th><th>${fname.toLowerCase()}_montant</th></tr>${groups.map(g => `<tr><td class="gcolor-${groups.indexOf(g)}">${g}</td><td class="gcolor-${groups.indexOf(g)}">${f(rows.filter(r => r[0] === g).map(r => r[1]))}</td></tr>`).join("")}</table><p class="vcap" style="margin-top:14px">Données</p>${table(rows, true)}`;
    body.innerHTML = `<div class="vgrid"><div>${left}</div><div>${right || '<p class="vcap">Clique sur « Étape suivante »</p>'}</div></div>`;
    note.innerHTML = [`En pandas : <code>df.groupby("magasin")["montant"].${agg === "count" ? "count" : agg}()</code>. En SQL : <code>SELECT magasin, ${fname}(montant) FROM t GROUP BY magasin</code>.`,
      "<b>Découper</b> : chaque ligne rejoint le groupe de son magasin.", `<b>Appliquer</b> : la fonction ${fname} est calculée dans chaque groupe, séparément.`, "<b>Combiner</b> : une ligne par groupe dans le résultat."][step];
  };
  btnCtl(ctrl, "Étape suivante", "btn small primary").addEventListener("click", () => { step = (step + 1) % 4; draw(); });
  const sel = h(`<label for="gb-agg-${++vizUid}">Fonction <select id="gb-agg-${vizUid}" class="btn small"><option value="sum">somme</option><option value="mean">moyenne</option><option value="count">comptage</option><option value="max">maximum</option></select></label>`);
  ctrl.appendChild(sel);
  $("select", sel).addEventListener("change", e => { agg = e.target.value; draw(); });
  draw();
};

/* ---------- jointures SQL ---------- */
VIZ.join = el => {
  const { body, ctrl, note } = vizShell(el, "INNER JOIN contre LEFT JOIN", "SQL");
  const clients = [[1, "Léa"], [2, "Hugo"], [3, "Inès"], [4, "Adam"]];
  const cmds = [[101, 1, "Bastille"], [102, 3, "Bouffay"], [103, 1, "Chartrons"], [104, 3, "Bastille"], [105, 2, "Part-Dieu"]];
  let mode = "INNER";
  const draw = () => {
    const res = [];
    for (const [id, p] of clients) {
      const m = cmds.filter(c => c[1] === id);
      if (m.length) m.forEach(c => res.push([id, p, c[0], c[2]]));
      else if (mode === "LEFT") res.push([id, p, null, null]);
    }
    const venn = `<svg viewBox="0 0 200 110" style="max-width:220px"><circle cx="80" cy="55" r="44" class="${mode === "LEFT" ? "vz-accent" : "vz-code"}" fill-opacity="${mode === "LEFT" ? .35 : 1}" stroke="var(--line)"/><circle cx="125" cy="55" r="44" class="vz-code" fill-opacity=".6" stroke="var(--line)"/><path d="M102.5 17 A44 44 0 0 1 102.5 93 A44 44 0 0 1 102.5 17" class="vz-accent" fill-opacity=".7"/><text x="62" y="58" class="vz-tm" text-anchor="middle">clients</text><text x="146" y="58" class="vz-tm" text-anchor="middle">commandes</text></svg>`;
    body.innerHTML = `<div class="vgrid"><div><p class="vcap">clients</p><table class="vtab"><tr><th>id</th><th>prenom</th></tr>${clients.map(([i, p]) => `<tr class="${cmds.some(c => c[1] === i) ? "" : (mode === "INNER" ? "dim" : "hl")}"><td>${i}</td><td>${p}</td></tr>`).join("")}</table><p class="vcap" style="margin-top:12px">commandes</p><table class="vtab"><tr><th>id</th><th>client_id</th><th>magasin</th></tr>${cmds.map(c => `<tr><td>${c[0]}</td><td>${c[1]}</td><td>${c[2]}</td></tr>`).join("")}</table></div>
      <div>${venn}<p class="vcap">Résultat · ${res.length} lignes</p><table class="vtab"><tr><th>id</th><th>prenom</th><th>cmd</th><th>magasin</th></tr>${res.map(r => `<tr class="${r[2] === null ? "hl" : ""}">${r.map(v => v === null ? `<td class="null">NULL</td>` : `<td>${v}</td>`).join("")}</tr>`).join("")}</table></div></div>`;
    note.innerHTML = mode === "INNER" ? "<b>INNER JOIN</b> ne garde que les lignes qui ont une correspondance des deux côtés : Adam, qui n'a jamais commandé, disparaît." : "<b>LEFT JOIN</b> garde tous les clients. Adam apparaît avec des <b>NULL</b> : c'est ainsi qu'on trouve « ceux qui n'ont jamais commandé » (<code>WHERE c.id IS NULL</code>).";
    $$("button", ctrl).forEach(b => b.classList.toggle("primary", b.textContent.startsWith(mode)));
  };
  ["INNER JOIN", "LEFT JOIN"].forEach(t => btnCtl(ctrl, t).addEventListener("click", () => { mode = t.split(" ")[0]; draw(); }));
  draw();
};

/* ---------- ETL ---------- */
VIZ.etl = el => {
  const { body, ctrl, note } = vizShell(el, "Un pipeline ETL", "données");
  const st = [["Extract", "API /books", "23 livres JSON"], ["Transform", "pandas", "aplatir, renommer, typer"], ["Load", "SQLite / RDS", "table livres"]];
  body.innerHTML = `<svg viewBox="0 0 600 140" role="img" aria-label="Pipeline extraire, transformer, charger"></svg>`;
  const svg = $("svg", body);
  st.forEach(([t, s, d], i) => { const x = 20 + i * 200; svg.append(svgEl("rect", { x, y: 30, width: 160, height: 80, rx: 12, class: "vz-code vz-line", "stroke-width": 1.5, id: `etl${i}-${vizUid}` }), svgEl("text", { x: x + 80, y: 60, "text-anchor": "middle", class: "vz-tb" }, t), svgEl("text", { x: x + 80, y: 78, "text-anchor": "middle", class: "vz-tm" }, s), svgEl("text", { x: x + 80, y: 96, "text-anchor": "middle", class: "vz-tm" }, d)); if (i < 2) svg.append(svgEl("path", { d: `M${x + 165} 70 L${x + 195} 70`, class: "vz-smuted", "stroke-width": 2, "marker-end": "" }), svgEl("text", { x: x + 180, y: 64, "text-anchor": "middle", class: "vz-tm" }, "→")); });
  const dots = [];
  for (let i = 0; i < 12; i++) { const c = svgEl("circle", { r: 4, cx: 20, cy: 70, class: "vz-accent", opacity: 0 }); svg.append(c); dots.push(c); }
  const id = vizUid++;
  btnCtl(ctrl, "Lancer le pipeline", "btn small primary").addEventListener("click", () => {
    const t0 = performance.now();
    const run = t => {
      const el2 = (t - t0) / 1000;
      dots.forEach((d, i) => { const u = Math.max(0, Math.min(1, (el2 - i * 0.15) / 2.2)); d.setAttribute("opacity", u > 0 && u < 1 ? 1 : 0); d.setAttribute("cx", 100 + u * 400); d.setAttribute("cy", 70 + Math.sin(u * 12 + i) * 18 * (1 - u)); d.setAttribute("class", u > .5 ? "vz-ok" : "vz-accent"); });
      const stage = Math.min(2, Math.floor(el2 / 1.1));
      note.innerHTML = ["<b>Extraire</b> : on pagine l'API et on récupère le JSON brut.", "<b>Transformer</b> : on aplatit, on renomme les colonnes, on valide les types et les valeurs.", "<b>Charger</b> : on écrit la table dans la base, en remplaçant l'ancienne version (idempotence)."][stage];
      if (el2 < 4.2 && !reduceMotion()) requestAnimationFrame(run); else { dots.forEach(d => d.setAttribute("opacity", 0)); note.innerHTML = "Terminé : <b>23 lignes</b> chargées. Relancer le pipeline donne le même résultat, sans doublons."; }
    };
    requestAnimationFrame(run);
  });
  note.innerHTML = "Chaque étape est une fonction. Un orchestrateur comme <b>Airflow</b> en fera des tâches planifiées et surveillées.";
};

/* ---------- loi normale ---------- */
VIZ.normal = el => {
  const { body, ctrl, note } = vizShell(el, "La loi normale", "distribution");
  body.innerHTML = `<svg viewBox="0 0 600 240" role="img" aria-label="Courbe de la loi normale avec un histogramme d'échantillons"></svg>`;
  const svg = $("svg", body);
  const mu = rangeCtl(ctrl, `mu${++vizUid}`, "Moyenne μ", 140, 200, 1, 170);
  const sg = rangeCtl(ctrl, `sg${vizUid}`, "Écart-type σ", 3, 20, 1, 10);
  const drawBtn = btnCtl(ctrl, "Tirer 500 valeurs", "btn small primary");
  let sample = [];
  const X0 = 110, X1 = 230, W = 560, H = 190, L = 20, T = 20;
  const sx = x => L + (x - X0) / (X1 - X0) * W;
  const randn = () => { let u = 0, v = 0; while (!u) u = Math.random(); while (!v) v = Math.random(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };
  const draw = () => {
    const m = +mu.value, s = +sg.value;
    svg.innerHTML = "";
    const pdf = x => Math.exp(-((x - m) ** 2) / (2 * s * s)) / (s * Math.sqrt(2 * Math.PI));
    const ymax = pdf(m) * 1.15;
    const sy = y => T + H - y / ymax * H;
    svg.append(svgEl("line", { x1: L, x2: L + W, y1: T + H, y2: T + H, class: "vz-line" }));
    for (let x = 110; x <= 230; x += 20) svg.append(svgEl("text", { x: sx(x), y: T + H + 16, "text-anchor": "middle", class: "vz-tm" }, x));
    [[2, .18], [1, .3]].forEach(([k, op]) => { let d = `M${sx(m - k * s)} ${sy(0)}`; for (let x = m - k * s; x <= m + k * s; x += .5) d += ` L${sx(x)} ${sy(pdf(x))}`; d += ` L${sx(m + k * s)} ${sy(0)} Z`; svg.append(svgEl("path", { d, class: "vz-accent", "fill-opacity": op })); });
    if (sample.length) {
      const bw = 3, bins = {};
      sample.forEach(v => { const b = Math.floor(v / bw); bins[b] = (bins[b] || 0) + 1; });
      for (const [b, c] of Object.entries(bins)) { const x = +b * bw; if (x < X0 || x > X1) continue; const dens = c / sample.length / bw; svg.append(svgEl("rect", { x: sx(x), y: sy(dens), width: Math.max(1, sx(x + bw) - sx(x) - 1), height: sy(0) - sy(dens), class: "vz-mark", "fill-opacity": .75 })); }
    }
    let d = ""; for (let x = X0; x <= X1; x += .5) d += `${d ? "L" : "M"}${sx(x)} ${sy(pdf(x))} `;
    svg.append(svgEl("path", { d, fill: "none", class: "vz-sink", "stroke-width": 2.2 }));
    svg.append(svgEl("text", { x: sx(m), y: sy(pdf(m) * .45), "text-anchor": "middle", class: "vz-tb" }, "68 %"), svgEl("text", { x: sx(m + 1.5 * s), y: sy(pdf(m + 1.5 * s) * .3), "text-anchor": "middle", class: "vz-tm" }, "95 %"));
    const within = sample.length ? Math.round(100 * sample.filter(v => Math.abs(v - m) < s).length / sample.length) : null;
    note.innerHTML = `Zone foncée : μ ± σ = [${m - s} ; ${m + s}], environ <b>68 %</b> des valeurs. Zone claire : μ ± 2σ, environ <b>95 %</b>.` + (within != null ? ` Dans ton tirage : <b>${within} %</b> des valeurs sont à moins d'un écart-type.` : "");
  };
  mu.addEventListener("input", () => { sample = []; draw(); }); sg.addEventListener("input", () => { sample = []; draw(); });
  drawBtn.addEventListener("click", () => { const m = +mu.value, s = +sg.value; sample = Array.from({ length: 500 }, () => m + s * randn()); draw(); });
  draw();
};

/* ---------- produit matriciel ---------- */
VIZ.matmul = el => {
  const { body, ctrl, note } = vizShell(el, "Prédire avec X @ w + b", "algèbre linéaire");
  const X = [[1, 2], [3, 4], [5, 6]], w = [0.5, -1], b = 2;
  let r = 0, timer = null;
  const draw = () => {
    const y = X.map(row => row[0] * w[0] + row[1] * w[1] + b);
    body.innerHTML = `<div style="display:flex;gap:18px;align-items:center;flex-wrap:wrap;justify-content:center;font:14px var(--mono)">
      <div><p class="vcap">X (3 × 2)</p><table class="vtab">${X.map((row, i) => `<tr class="${i === r ? "hl" : ""}">${row.map(v => `<td>${v}</td>`).join("")}</tr>`).join("")}</table></div>
      <span>@</span>
      <div><p class="vcap">w (2,)</p><table class="vtab">${w.map(v => `<tr class="hl"><td>${v}</td></tr>`).join("")}</table></div>
      <span>+ ${b} =</span>
      <div><p class="vcap">ŷ (3,)</p><table class="vtab">${y.map((v, i) => `<tr class="${i === r ? "hl" : ""}"><td>${v}</td></tr>`).join("")}</table></div></div>`;
    note.innerHTML = `Ligne ${r + 1} : ${X[r][0]} × ${w[0]} + ${X[r][1]} × (${w[1]}) + ${b} = <b>${y[r]}</b>. Chaque prédiction est le <b>produit scalaire</b> d'une ligne de X avec w, plus le biais. Les trois sont calculées en une seule opération.`;
  };
  btnCtl(ctrl, "Ligne suivante", "btn small primary").addEventListener("click", () => { r = (r + 1) % 3; draw(); });
  btnCtl(ctrl, "Lecture automatique").addEventListener("click", e => { if (timer) { clearInterval(timer); timer = null; e.target.textContent = "Lecture automatique"; } else { timer = setInterval(() => { if (!el.isConnected) { clearInterval(timer); return; } r = (r + 1) % 3; draw(); }, 1600); e.target.textContent = "Pause"; } });
  draw();
};

/* ---------- descente de gradient ---------- */
VIZ.gradient = el => {
  const { body, ctrl, note } = vizShell(el, "La descente de gradient pas à pas", "optimisation");
  body.innerHTML = `<svg viewBox="0 0 600 272" role="img" aria-label="Descente de gradient sur une parabole"></svg>`;
  const svg = $("svg", body);
  const eta = rangeCtl(ctrl, `eta${++vizUid}`, "Taux η", 0.02, 1.1, 0.01, 0.1, v => v.toFixed(2));
  const x0 = rangeCtl(ctrl, `x0${vizUid}`, "Départ", -6, 12, 0.5, 10);
  const go = btnCtl(ctrl, "Lancer", "btn small primary");
  const f = x => (x - 3) ** 2, df = x => 2 * (x - 3);
  const L = 40, W = 520, T = 15, H = 210, XA = -7, XB = 13, YB = 110;
  const sx = x => L + (x - XA) / (XB - XA) * W, sy = y => T + H - Math.min(y, YB) / YB * H;
  let path = [], k = 0, timer = null;
  const base = () => {
    svg.innerHTML = "";
    svg.append(svgEl("line", { x1: L, x2: L + W, y1: T + H, y2: T + H, class: "vz-line" }));
    for (let x = -6; x <= 12; x += 3) svg.append(svgEl("text", { x: sx(x), y: T + H + 16, "text-anchor": "middle", class: "vz-tm" }, x));
    let d = ""; for (let x = XA; x <= XB; x += .1) d += `${d ? "L" : "M"}${sx(x)} ${sy(f(x))} `;
    svg.append(svgEl("path", { d, fill: "none", class: "vz-smuted", "stroke-width": 2 }));
    svg.append(svgEl("text", { x: sx(3), y: T + H + 34, "text-anchor": "middle", class: "vz-tm" }, "minimum : x = 3"));
  };
  const drawPath = () => {
    base();
    for (let i = 0; i <= k && i < path.length; i++) {
      const x = path[i];
      if (i > 0) { const p = path[i - 1]; svg.append(svgEl("line", { x1: sx(p), y1: sy(f(p)), x2: sx(x), y2: sy(f(x)), class: "vz-sacc", "stroke-width": 1.5, "stroke-opacity": .6 })); }
      svg.append(svgEl("circle", { cx: sx(Math.max(XA, Math.min(XB, x))), cy: sy(f(x)), r: i === k ? 7 : 4, class: i === k ? "vz-mark" : "vz-accent", stroke: "var(--ink)", "stroke-width": i === k ? 1.5 : 0 }));
    }
    const x = path[Math.min(k, path.length - 1)];
    const div = Math.abs(x) > 40;
    note.innerHTML = `Étape <b>${k}</b> · x = ${x.toFixed(3)} · perte = ${f(x).toFixed(3)} · pente = ${df(x).toFixed(2)}. ` + (div ? "<b>Divergence</b> : avec η > 1, chaque pas saute plus loin que le précédent." : +eta.value < .05 ? "Avec un η très petit, on avance très lentement." : +eta.value > .9 ? "η proche de 1 : on rebondit d'un côté à l'autre du minimum." : "La pente diminue près du minimum, donc les pas raccourcissent.");
  };
  const start = () => {
    clearInterval(timer);
    path = [+x0.value]; for (let i = 0; i < 30; i++) { const x = path[path.length - 1]; path.push(x - +eta.value * df(x)); }
    k = 0; drawPath();
    if (reduceMotion()) { k = path.length - 1; drawPath(); return; }
    timer = setInterval(() => { if (!el.isConnected || k >= path.length - 1) { clearInterval(timer); return; } k++; drawPath(); }, 280);
  };
  go.addEventListener("click", start);
  [eta, x0].forEach(i => i.addEventListener("change", start));
  path = [10]; base(); drawPath();
  note.innerHTML = "Règle de mise à jour : <b>x ← x − η × f'(x)</b>. Change le taux d'apprentissage η puis clique sur Lancer. Essaie 0,02, 0,5, 0,95 et 1,05.";
};

/* ---------- train / test split ---------- */
VIZ.split = el => {
  const { body, ctrl, note } = vizShell(el, "Séparer entraînement et test", "évaluation");
  body.innerHTML = `<svg viewBox="0 0 600 120" role="img" aria-label="Répartition des exemples entre entraînement et test"></svg>`;
  const svg = $("svg", body);
  const n = 40; let seed = 3;
  const cls = Array.from({ length: n }, (_, i) => i < 28 ? 0 : 1);       // 70 % / 30 %
  const ts = rangeCtl(ctrl, `ts${++vizUid}`, "test_size", 0.1, 0.5, 0.05, 0.2, v => v.toFixed(2));
  const strat = h(`<label><input type="checkbox" checked id="st${vizUid}"> stratify=y</label>`); ctrl.appendChild(strat);
  const shuf = btnCtl(ctrl, "Changer random_state");
  const rnd = () => { seed = (seed * 9301 + 49297) % 233280; return seed / 233280; };
  const draw = () => {
    const t = +ts.value, k = Math.round(n * t), st = $("input", strat).checked;
    let s0 = seed; const r = () => { s0 = (s0 * 9301 + 49297) % 233280; return s0 / 233280; };
    const idx = [...Array(n).keys()].sort(() => r() - .5);
    let test;
    if (st) { const k1 = Math.round(k * 12 / 40); test = new Set([...idx.filter(i => cls[i] === 1).slice(0, k1), ...idx.filter(i => cls[i] === 0).slice(0, k - k1)]); }
    else test = new Set(idx.slice(0, k));
    svg.innerHTML = "";
    for (let i = 0; i < n; i++) {
      const x = 20 + (i % 20) * 28, y = 22 + Math.floor(i / 20) * 34, te = test.has(i);
      const shape = cls[i] ? svgEl("rect", { x: x - 8, y: y - 8, width: 16, height: 16, rx: 3 }) : svgEl("circle", { cx: x, cy: y, r: 8 });
      shape.setAttribute("class", te ? "vz-mark" : "vz-accent"); shape.setAttribute("stroke", "var(--ink)"); shape.setAttribute("stroke-width", te ? 1.5 : 0);
      svg.append(shape);
    }
    svg.append(svgEl("text", { x: 20, y: 108, class: "vz-tm" }, "● classe 0   ■ classe 1   bleu = entraînement   jaune = test"));
    const t1 = [...test].filter(i => cls[i]).length;
    note.innerHTML = `<b>${n - k}</b> exemples d'entraînement, <b>${k}</b> de test. Classe 1 dans le test : <b>${k ? Math.round(100 * t1 / k) : 0} %</b> (30 % dans les données). ${st ? "Avec <code>stratify</code>, la proportion est respectée." : "Sans <code>stratify</code>, le hasard peut déséquilibrer le jeu de test : relance plusieurs fois."}`;
  };
  ts.addEventListener("input", draw); $("input", strat).addEventListener("change", draw); shuf.addEventListener("click", () => { rnd(); draw(); });
  draw();
};

/* ---------- sous- et sur-apprentissage ---------- */
VIZ.overfit = el => {
  const { body, ctrl, note } = vizShell(el, "Trop simple, juste bien, trop complexe", "biais-variance");
  body.innerHTML = `<div class="vgrid"><div><svg viewBox="0 0 300 220" class="fit" role="img" aria-label="Ajustement polynomial"></svg></div><div><svg viewBox="0 0 300 220" class="err" role="img" aria-label="Erreurs d'entraînement et de test selon le degré"></svg></div></div>`;
  const deg = rangeCtl(ctrl, `dg${++vizUid}`, "Complexité (degré)", 1, 12, 1, 3);
  let s = 7; const r = () => { s = (s * 16807) % 2147483647; return s / 2147483647; };
  const g = x => Math.sin(2.6 * x) + 0.3 * x;
  const mk = (n, off) => Array.from({ length: n }, (_, i) => { const x = -1 + 2 * (i + off) / n; return [x, g(x) + (r() - .5) * 0.7]; });
  const train = mk(14, 0.2), test = mk(14, 0.7);
  function fit(pts, d) {
    const m = d + 1, A = Array.from({ length: m }, () => Array(m + 1).fill(0));
    for (const [x, y] of pts) { const p = Array.from({ length: m }, (_, k) => x ** k); for (let i = 0; i < m; i++) { for (let j = 0; j < m; j++) A[i][j] += p[i] * p[j]; A[i][m] += p[i] * y; } }
    for (let i = 0; i < m; i++) A[i][i] += 1e-7;
    for (let i = 0; i < m; i++) { let piv = i; for (let k = i + 1; k < m; k++) if (Math.abs(A[k][i]) > Math.abs(A[piv][i])) piv = k; [A[i], A[piv]] = [A[piv], A[i]]; for (let k = 0; k < m; k++) if (k !== i) { const f = A[k][i] / A[i][i]; for (let j = i; j <= m; j++) A[k][j] -= f * A[i][j]; } }
    const c = A.map((row, i) => row[m] / row[i]);
    return x => c.reduce((a, ci, k) => a + ci * x ** k, 0);
  }
  const mse = (p, pts) => pts.reduce((a, [x, y]) => a + (p(x) - y) ** 2, 0) / pts.length;
  const curves = Array.from({ length: 12 }, (_, i) => { const p = fit(train, i + 1); return [mse(p, train), mse(p, test), p]; });
  const draw = () => {
    const d = +deg.value, [tr, te, p] = curves[d - 1];
    const sf = $("svg.fit", body); sf.innerHTML = "";
    const X = x => 20 + (x + 1) / 2 * 260, Y = y => 110 - y * 55;
    sf.append(svgEl("text", { x: 20, y: 14, class: "vz-tm" }, `degré ${d}`));
    let path = ""; for (let x = -1; x <= 1.0001; x += .01) { const y = Math.max(-1.9, Math.min(1.9, p(x))); path += `${path ? "L" : "M"}${X(x)} ${Y(y)} `; }
    sf.append(svgEl("path", { d: path, fill: "none", class: "vz-sacc", "stroke-width": 2.2 }));
    train.forEach(([x, y]) => sf.append(svgEl("circle", { cx: X(x), cy: Y(y), r: 4, class: "vz-accent" })));
    test.forEach(([x, y]) => sf.append(svgEl("rect", { x: X(x) - 4, y: Y(y) - 4, width: 8, height: 8, class: "vz-mark", stroke: "var(--ink)", "stroke-width": 1 })));
    sf.append(svgEl("text", { x: 20, y: 212, class: "vz-tm" }, "● entraînement   ■ test"));
    const se = $("svg.err", body); se.innerHTML = "";
    const ymax = .6, EX = i => 30 + (i - 1) / 11 * 250, EY = v => 190 - Math.min(v, ymax) / ymax * 170;
    se.append(svgEl("line", { x1: 30, x2: 280, y1: 190, y2: 190, class: "vz-line" }));
    [[0, "vz-sacc", "entraînement"], [1, "vz-serr", "test"]].forEach(([k, c, lab], j) => { let pth = ""; curves.forEach((cv, i) => { pth += `${pth ? "L" : "M"}${EX(i + 1)} ${EY(cv[k])} `; }); se.append(svgEl("path", { d: pth, fill: "none", class: c, "stroke-width": 2 }), svgEl("text", { x: 190, y: 20 + j * 16, style: `font:600 11px var(--mono);fill:var(--${k ? "err" : "accent"})` }, "── " + lab)); });
    se.append(svgEl("line", { x1: EX(d), x2: EX(d), y1: 10, y2: 190, class: "vz-smuted", "stroke-dasharray": "3 3" }));
    se.append(svgEl("text", { x: 30, y: 206, class: "vz-tm" }, "erreur (MSE) selon le degré, de 1 à 12"));
    note.innerHTML = `Erreur d'entraînement <b>${tr.toFixed(3)}</b>, erreur de test <b>${te.toFixed(3)}</b>. ` + (d <= 2 ? "Le modèle est <b>trop simple</b> : il se trompe partout (sous-apprentissage)." : d >= 8 ? "Le modèle colle aux points d'entraînement, bruit compris, et se trompe sur le test : <b>surapprentissage</b>." : "Bon compromis : l'erreur de test est proche de son minimum.");
  };
  deg.addEventListener("input", draw); draw();
};

/* ---------- RAG : recherche par similarité ---------- */
VIZ.rag = el => {
  const { body, ctrl, note } = vizShell(el, "Retrouver les bons documents", "RAG");
  const docs = [["Descente de gradient", [.9, .3]], ["Taux d'apprentissage", [.85, .45]], ["Rétropropagation", [.7, .55]], ["Charger un CSV", [-.6, .8]], ["groupby pandas", [-.75, .6]], ["Jointures SQL", [-.5, .9]], ["Clé d'API", [-.2, -.9]], ["Docker", [.1, -.95]], ["Surapprentissage", [.6, .75]]];
  const qs = [["Comment régler le learning rate ?", [.92, .38]], ["Fusionner deux tables ?", [-.55, .85]], ["Déployer mon modèle ?", [.05, -.98]]];
  let qi = 0;
  body.innerHTML = `<div class="vgrid"><div><svg viewBox="-1.2 -1.2 2.4 2.4" style="max-width:300px;margin:auto" role="img" aria-label="Espace des embeddings"></svg></div><div><p class="vcap">Prompt envoyé au LLM</p><pre class="json"></pre></div></div>`;
  const k = rangeCtl(ctrl, `k${++vizUid}`, "k documents", 1, 4, 1, 2);
  const sel = h(`<label for="q${vizUid}">Question <select id="q${vizUid}" class="btn small">${qs.map((q, i) => `<option value="${i}">${esc(q[0])}</option>`).join("")}</select></label>`); ctrl.appendChild(sel);
  const cos = (a, b) => (a[0] * b[0] + a[1] * b[1]) / (Math.hypot(...a) * Math.hypot(...b));
  const draw = () => {
    const [qt, qv] = qs[qi], K = +k.value;
    const ranked = docs.map(d => [d[0], d[1], cos(qv, d[1])]).sort((a, b) => b[2] - a[2]);
    const top = new Set(ranked.slice(0, K).map(d => d[0]));
    const svg = $("svg", body); svg.innerHTML = "";
    svg.append(svgEl("circle", { cx: 0, cy: 0, r: 1, fill: "none", class: "vz-line", "stroke-width": .01 }));
    ranked.forEach(([n, v]) => { if (top.has(n)) svg.append(svgEl("line", { x1: qv[0], y1: -qv[1], x2: v[0], y2: -v[1], class: "vz-sacc", "stroke-width": .015 })); });
    docs.forEach(([n, v]) => { svg.append(svgEl("circle", { cx: v[0], cy: -v[1], r: .05, class: top.has(n) ? "vz-accent" : "vz-muted" })); svg.append(svgEl("text", { x: v[0] + .07, y: -v[1] + .03, style: `font:${top.has(n) ? 600 : 400} .085px var(--body);fill:var(--${top.has(n) ? "ink" : "muted"})` }, n)); });
    svg.append(svgEl("rect", { x: qv[0] - .06, y: -qv[1] - .06, width: .12, height: .12, class: "vz-mark", stroke: "var(--ink)", "stroke-width": .015 }));
    $("pre", body).textContent = `Réponds uniquement à partir du contexte.\n\nContexte :\n${ranked.slice(0, K).map(d => `- [${d[0]}] (similarité ${d[2].toFixed(2)})`).join("\n")}\n\nQuestion : ${qt}`;
    note.innerHTML = "Chaque texte devient un <b>vecteur</b> (embedding). La question (carré jaune) est comparée à tous les documents par <b>similarité cosinus</b> ; les <b>k</b> plus proches sont ajoutés au prompt.";
  };
  k.addEventListener("input", draw); $("select", sel).addEventListener("change", e => { qi = +e.target.value; draw(); });
  draw();
};

/* ---------- token suivant et température ---------- */
VIZ.nexttoken = el => {
  const { body, ctrl, note } = vizShell(el, "Le token suivant", "LLM");
  const ctx = "La capitale de la France est";
  const cand = [["Paris", 6.0], ["une", 3.2], ["la", 2.6], ["Lyon", 1.6], ["située", 1.3], ["Marseille", 0.6], ["belle", 0.2]];
  const T = rangeCtl(ctrl, `t${++vizUid}`, "Température", 0.1, 2.5, 0.05, 1, v => v.toFixed(2));
  const tirer = btnCtl(ctrl, "Tirer un token", "btn small primary");
  let tires = [];
  const probs = () => { const t = +T.value, z = cand.map(c => c[1] / t), m = Math.max(...z), e = z.map(v => Math.exp(v - m)), s = e.reduce((a, b) => a + b, 0); return e.map(v => v / s); };
  const draw = () => {
    const p = probs();
    body.innerHTML = `<p style="font:15px var(--mono);margin:0 0 12px">${esc(ctx)} <span class="mark">▁▁▁</span></p>` +
      cand.map((c, i) => `<div style="display:grid;grid-template-columns:90px 1fr 56px;gap:8px;align-items:center;margin:4px 0;font:13px var(--mono)"><span>${c[0]}</span><div class="bar" style="height:14px"><i style="width:${(p[i] * 100).toFixed(1)}%;transition:width .2s"></i></div><span class="tab" style="text-align:right">${(p[i] * 100).toFixed(1)} %</span></div>`).join("") +
      (tires.length ? `<p class="vcap" style="margin-top:12px">Tirages</p><p style="font:13px var(--mono);margin:0">${tires.map(t => `<span class="badge${t === "Paris" ? "" : " jedha"}">${esc(t)}</span>`).join(" ")}</p>` : "");
    const t = +T.value;
    note.innerHTML = t < 0.4 ? "Température basse : « Paris » écrase tout, la réponse est quasi déterministe." : t > 1.6 ? "Température haute : la distribution s'aplatit, des tokens improbables apparaissent souvent." : "Température moyenne : le token le plus probable domine, mais d'autres sortent parfois.";
  };
  T.addEventListener("input", () => { tires = []; draw(); });
  tirer.addEventListener("click", () => { const p = probs(); let r = Math.random(), i = 0; while (i < p.length - 1 && r > p[i]) { r -= p[i]; i++; } tires.push(cand[i][0]); if (tires.length > 14) tires.shift(); draw(); });
  draw();
};

/* ---------- BPE ---------- */
VIZ.bpe = el => {
  const { body, ctrl, note } = vizShell(el, "Le découpage BPE, fusion par fusion", "tokens");
  const start = ["l o w", "l o w e r", "n e w e s t", "w i d e s t", "l o w e s t"];
  let corpus = start.slice(), merges = [];
  const step = () => {
    const c = new Map();
    corpus.forEach(m => { const s = m.split(" "); for (let i = 0; i < s.length - 1; i++) { const k = s[i] + " " + s[i + 1]; c.set(k, (c.get(k) || 0) + 1); } });
    if (!c.size) return false;
    let best = null; for (const [k, v] of c) if (!best || v > best[1]) best = [k, v];
    const [a, b] = best[0].split(" ");
    corpus = corpus.map(m => { const s = m.split(" "), o = []; for (let i = 0; i < s.length; i++) { if (i < s.length - 1 && s[i] === a && s[i + 1] === b) { o.push(a + b); i++; } else o.push(s[i]); } return o.join(" "); });
    merges.push(`${a} + ${b} → ${a + b} (${best[1]} fois)`);
    return true;
  };
  const draw = () => {
    body.innerHTML = `<div class="vgrid"><div><p class="vcap">Corpus découpé</p>${corpus.map(m => `<div style="margin:6px 0">${m.split(" ").map(t => `<span class="badge${t.length > 1 ? " jedha" : ""}" style="font-family:var(--mono);margin-right:3px">${esc(t)}</span>`).join("")}</div>`).join("")}</div>
      <div><p class="vcap">Fusions apprises</p><ol style="margin:0;padding-left:1.3em;font:13px var(--mono)">${merges.map(m => `<li>${esc(m)}</li>`).join("") || "<li class='muted'>aucune pour l'instant</li>"}</ol></div></div>`;
    const n = corpus.reduce((a, m) => a + m.split(" ").length, 0);
    note.innerHTML = `<b>${n} tokens</b> pour 5 mots. Chaque fusion crée un nouveau token à partir de la paire voisine la plus fréquente : les morceaux fréquents (« low », « est ») deviennent des tokens entiers.`;
  };
  btnCtl(ctrl, "Fusion suivante", "btn small primary").addEventListener("click", () => { step(); draw(); });
  btnCtl(ctrl, "Recommencer").addEventListener("click", () => { corpus = start.slice(); merges = []; draw(); });
  draw();
};

/* ---------- la boucle d'un agent ---------- */
VIZ.agent = el => {
  const { body, ctrl, note } = vizShell(el, "La boucle d'un agent", "agents");
  const steps = [
    ["user", "Utilisateur", "Quel temps fait-il à Lyon, et faut-il un parapluie demain ?"],
    ["llm", "LLM", "Je dois connaître la météo. → appel d'outil : meteo(ville=\"Lyon\")"],
    ["tool", "Outil · meteo", "{ \"aujourd_hui\": \"15 °C, soleil\", \"demain\": \"pluie 80 %\" }"],
    ["llm", "LLM", "J'ai l'information, pas besoin d'autre outil. → réponse finale"],
    ["final", "Réponse", "Il fait 15 °C et beau à Lyon. Demain, 80 % de risque de pluie : prends un parapluie."],
  ];
  const nodes = [["user", 70, "Utilisateur"], ["llm", 300, "LLM"], ["tool", 530, "Outils"]];
  let k = 0;
  const draw = () => {
    const cur = steps[k][0] === "final" ? "user" : steps[k][0];
    const svg = `<svg viewBox="0 0 600 130">${nodes.map(([id, x, lab]) => `<g><rect x="${x - 60}" y="20" width="120" height="50" rx="12" class="${cur === id ? "vz-accent" : "vz-code"}" stroke="var(--line)"/><text x="${x}" y="50" text-anchor="middle" class="vz-tb" style="${cur === id ? "fill:var(--surface)" : ""}">${lab}</text></g>`).join("")}
      <path d="M130 38 L240 38" class="vz-smuted" stroke-width="2"/><path d="M360 38 L470 38" class="vz-smuted" stroke-width="2"/>
      <path d="M470 55 L360 55" class="vz-smuted" stroke-width="2" stroke-dasharray="4 3"/><path d="M240 55 L130 55" class="vz-smuted" stroke-width="2" stroke-dasharray="4 3"/>
      <path d="M300 70 C 300 120, 360 120, 360 90 C 360 75, 330 72, 318 72" fill="none" class="vz-smuted" stroke-width="1.5"/>
      <text x="380" y="115" class="vz-tm">boucle jusqu'à la réponse finale</text></svg>`;
    body.innerHTML = svg + `<div style="margin-top:8px">${steps.slice(0, k + 1).map(([t, who, txt], i) => `<div class="msg ${t === "user" ? "me" : "ai"}" style="margin:6px 0;${i === k ? "outline:2px solid var(--accent)" : ""}"><b>${esc(who)}</b> · ${esc(txt)}</div>`).join("")}</div>`;
    note.innerHTML = ["L'utilisateur pose une question.", "Le LLM ne répond pas directement : il <b>demande</b> l'appel d'un outil.", "<b>Ton code</b> exécute l'outil et renvoie le résultat (l'observation) au LLM.", "Le LLM décide s'il lui faut une autre étape. Ici, non.", "Réponse finale. L'agent s'arrête aussi s'il atteint le nombre maximal d'étapes."][k];
  };
  btnCtl(ctrl, "Étape suivante", "btn small primary").addEventListener("click", () => { k = (k + 1) % steps.length; draw(); });
  draw();
};

/* ---------- n8n : des items qui traversent des nœuds ---------- */
VIZ.n8n = el => {
  const { body, ctrl, note } = vizShell(el, "Un workflow n8n", "automatisation");
  const items = [{ titre: "Lancement produit", vues: 1200, langue: "fr" }, { titre: "Product launch", vues: 300, langue: "en" }, { titre: "Bilan trimestriel", vues: 4500, langue: "fr" }];
  const stages = [
    ["Déclencheur", "Schedule · tous les lundis", items],
    ["HTTP Request", "GET /articles", items],
    ["IF", "{{ $json.langue }} = fr", items.filter(i => i.langue === "fr")],
    ["Modèle de langage", "Résume {{ $json.titre }}", items.filter(i => i.langue === "fr").map(i => ({ ...i, resume: "Résumé généré…" }))],
    ["Slack", "Envoie au canal #veille", items.filter(i => i.langue === "fr").map(i => ({ ...i, resume: "Résumé généré…" }))],
  ];
  let k = 0;
  const draw = () => {
    body.innerHTML = `<div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap">${stages.map((s, i) => `<div class="badge ${i === k ? "jedha" : ""}" style="padding:8px 10px;font-size:12px;${i === k ? "outline:2px solid var(--accent)" : ""}"><b>${esc(s[0])}</b></div>${i < stages.length - 1 ? "<span class='muted'>→</span>" : ""}`).join("")}</div>
      <p class="vcap" style="margin-top:12px">${esc(stages[k][0])} · ${esc(stages[k][1])} · ${stages[k][2].length} item(s) en sortie</p><pre class="json">${esc(JSON.stringify(stages[k][2].map(j => ({ json: j })), null, 1))}</pre>`;
    note.innerHTML = "Chaque nœud reçoit une <b>liste d'items</b> et en renvoie une autre. Les expressions <code>{{ $json.champ }}</code> lisent les champs de l'item courant.";
  };
  btnCtl(ctrl, "Nœud suivant", "btn small primary").addEventListener("click", () => { k = (k + 1) % stages.length; draw(); });
  draw();
};

/* ---------- découpage en morceaux ---------- */
VIZ.chunk = el => {
  const { body, ctrl, note } = vizShell(el, "Découper un document en morceaux", "RAG");
  const words = "Les fichiers supprimés restent dans la corbeille pendant 30 jours avec l'offre Gratuite et 180 jours avec l'offre Pro. Pour restaurer un fichier, ouvre la corbeille depuis le site web, sélectionne le fichier puis clique sur Restaurer.".split(" ");
  const size = rangeCtl(ctrl, `cs${++vizUid}`, "Taille (mots)", 4, 20, 1, 10);
  const ov = rangeCtl(ctrl, `co${vizUid}`, "Chevauchement", 0, 8, 1, 3);
  const cols = ["gcolor-0", "gcolor-1", "gcolor-2"];
  const draw = () => {
    let s = +size.value, o = Math.min(+ov.value, s - 1); const pas = s - o, chunks = [];
    for (let d = 0; d < words.length; d += pas) { chunks.push([d, Math.min(d + s, words.length)]); if (d + s >= words.length) break; }
    body.innerHTML = chunks.map(([a, b], i) => `<div style="margin:6px 0;font:13px/1.9 var(--body)"><span class="badge" style="margin-right:6px">#${i + 1}</span>${words.map((w, j) => j >= a && j < b ? `<span class="${cols[i % 3]}" style="padding:1px 2px;border-radius:3px">${esc(w)}</span>` : "").filter(Boolean).join(" ")}</div>`).join("");
    note.innerHTML = `<b>${chunks.length} morceaux</b>. Chaque morceau commence ${pas} mots après le précédent ; les ${o} derniers mots de l'un sont repris au début du suivant, pour ne pas couper une information en deux. Trop petit : on perd le contexte. Trop grand : la recherche devient imprécise.`;
  };
  size.addEventListener("input", draw); ov.addEventListener("input", draw); draw();
};

/* ---------- outils numériques partagés ---------- */
function mulberry(seed) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function gauss(r) { let u = 0, v = 0; while (!u) u = r(); while (!v) v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }
function solve(A, b) { const n = b.length, M = A.map((row, i) => [...row, b[i]]); for (let i = 0; i < n; i++) { let p = i; for (let k = i + 1; k < n; k++) if (Math.abs(M[k][i]) > Math.abs(M[p][i])) p = k; [M[i], M[p]] = [M[p], M[i]]; for (let k = 0; k < n; k++) if (k !== i) { const f = M[k][i] / M[i][i]; for (let j = i; j <= n; j++) M[k][j] -= f * M[i][j]; } } return M.map((r, i) => r[n] / r[i]); }

/* ---------- Ridge contre Lasso ---------- */
VIZ.regpath = el => {
  const { body, ctrl, note } = vizShell(el, "Ridge contre Lasso : l'effet de α", "régularisation");
  const r = mulberry(11), n = 80, p = 8, vrai = [3, -2, 1.2, 0, 0, 0, 0, 0];
  const X = Array.from({ length: n }, () => Array.from({ length: p }, () => gauss(r)));
  X.forEach(x => { x[3] = x[0] * 0.7 + gauss(r) * 0.5; });                 // une variable inutile mais corrélée
  const y = X.map(x => x.reduce((a, v, j) => a + v * vrai[j], 0) + gauss(r) * 1.2);
  const XtX = Array.from({ length: p }, (_, i) => Array.from({ length: p }, (_, j) => X.reduce((a, x) => a + x[i] * x[j], 0)));
  const Xty = Array.from({ length: p }, (_, i) => X.reduce((a, x, k) => a + x[i] * y[k], 0));
  const ridge = a => solve(XtX.map((row, i) => row.map((v, j) => v + (i === j ? a : 0))), Xty);
  const lasso = a => { const w = Array(p).fill(0); for (let it = 0; it < 200; it++) for (let j = 0; j < p; j++) { let rho = 0; for (let k = 0; k < n; k++) { let pred = 0; for (let m = 0; m < p; m++) if (m !== j) pred += X[k][m] * w[m]; rho += X[k][j] * (y[k] - pred); } const z = XtX[j][j], t = a * n / 10; w[j] = rho > t ? (rho - t) / z : rho < -t ? (rho + t) / z : 0; } return w; };
  let mode = "Ridge";
  const la = rangeCtl(ctrl, `ra${++vizUid}`, "log₁₀ α", -2, 3, 0.1, 0, v => `α = ${(10 ** v).toPrecision(2)}`);
  ["Ridge", "Lasso"].forEach(m => btnCtl(ctrl, m).addEventListener("click", () => { mode = m; draw(); }));
  const draw = () => {
    const a = 10 ** +la.value, w = mode === "Ridge" ? ridge(a) : lasso(a);
    const W = 560, H = 200, mid = 110, sc = 28;
    let svg = `<svg viewBox="0 0 600 256"><line x1="30" x2="590" y1="${mid}" y2="${mid}" class="vz-line"/>`;
    w.forEach((v, j) => { const x = 50 + j * 68, hgt = Math.max(-95, Math.min(95, v * sc)); svg += `<rect x="${x}" width="26" y="${hgt > 0 ? mid - hgt : mid}" height="${Math.abs(hgt) || 1}" class="${Math.abs(v) < 1e-6 ? "vz-muted" : "vz-accent"}" rx="3"/><rect x="${x + 28}" width="8" y="${vrai[j] > 0 ? mid - vrai[j] * sc : mid}" height="${Math.abs(vrai[j] * sc) || 1}" class="vz-mark"/><text x="${x + 16}" y="228" text-anchor="middle" class="vz-tm">x${j}</text><text x="${x + 13}" y="${hgt >= 0 ? mid - hgt - 6 : mid - hgt + 14}" text-anchor="middle" class="vz-tm">${v.toFixed(2)}</text>`; });
    body.innerHTML = svg + `<text x="40" y="252" class="vz-tm">barres bleues : coefficients estimés · jaunes : vrais coefficients</text></svg>`;
    $$("button", ctrl).forEach(b => b.classList.toggle("primary", b.textContent === mode));
    const zeros = w.filter(v => Math.abs(v) < 1e-6).length;
    note.innerHTML = mode === "Ridge" ? `Ridge rétrécit <b>tous</b> les coefficients à mesure que α grandit, sans jamais les annuler. Seules x0, x1 et x2 comptent vraiment.` : `Lasso met <b>${zeros}</b> coefficient${zeros > 1 ? "s" : ""} à zéro : il sélectionne les variables. Trop fort, il finit par annuler aussi les variables utiles.`;
  };
  la.addEventListener("input", draw); draw();
};

/* ---------- arbre de décision en 2D ---------- */
VIZ.tree = el => {
  const { body, ctrl, note } = vizShell(el, "Un arbre découpe l'espace", "arbres");
  const r = mulberry(5), pts = [];
  for (let i = 0; i < 160; i++) { const a = r() * Math.PI, c = i % 2; const x = c ? 1 - Math.cos(a) : Math.cos(a), y = c ? 0.5 - Math.sin(a) : Math.sin(a); pts.push([x + gauss(r) * 0.18, y + gauss(r) * 0.18, c]); }
  const gini = s => { if (!s.length) return 0; const p = s.filter(q => q[2]).length / s.length; return 1 - p * p - (1 - p) * (1 - p); };
  function build(s, d, box) {
    const maj = s.filter(q => q[2]).length * 2 >= s.length ? 1 : 0;
    if (d === 0 || gini(s) === 0 || s.length < 4) return { leaf: true, c: maj, box, n: s.length };
    let best = null;
    for (const f of [0, 1]) { const vals = [...new Set(s.map(q => q[f]))].sort((a, b) => a - b); for (let i = 0; i < vals.length - 1; i += 2) { const t = (vals[i] + vals[i + 1]) / 2, L = s.filter(q => q[f] <= t), R = s.filter(q => q[f] > t), g = (L.length * gini(L) + R.length * gini(R)) / s.length; if (!best || g < best.g) best = { f, t, g, L, R }; } }
    if (!best) return { leaf: true, c: maj, box, n: s.length };
    const bl = box.slice(), br = box.slice(); if (best.f === 0) { bl[2] = best.t; br[0] = best.t; } else { bl[3] = best.t; br[1] = best.t; }
    return { f: best.f, t: best.t, l: build(best.L, d - 1, bl), r: build(best.R, d - 1, br) };
  }
  const predict = (nd, q) => nd.leaf ? nd.c : predict(q[nd.f] <= nd.t ? nd.l : nd.r, q);
  const leaves = nd => nd.leaf ? [nd] : [...leaves(nd.l), ...leaves(nd.r)];
  const depth = rangeCtl(ctrl, `td${++vizUid}`, "Profondeur max", 1, 10, 1, 2);
  const draw = () => {
    const tree = build(pts, +depth.value, [-1.6, -1.1, 2.6, 1.6]);
    const X = x => 20 + (x + 1.6) / 4.2 * 560, Y = y => 240 - (y + 1.1) / 2.7 * 230;
    let svg = `<svg viewBox="0 0 600 250">`;
    leaves(tree).forEach(lf => { const [x0, y0, x1, y1] = lf.box; svg += `<rect x="${X(x0)}" y="${Y(y1)}" width="${X(x1) - X(x0)}" height="${Y(y0) - Y(y1)}" class="${lf.c ? "vz-mark" : "vz-accent"}" fill-opacity=".16" stroke="var(--line)"/>`; });
    pts.forEach(q => { svg += q[2] ? `<rect x="${X(q[0]) - 4}" y="${Y(q[1]) - 4}" width="8" height="8" class="vz-mark" stroke="var(--ink)" stroke-width=".8"/>` : `<circle cx="${X(q[0])}" cy="${Y(q[1])}" r="4" class="vz-accent"/>`; });
    body.innerHTML = svg + "</svg>";
    const acc = pts.filter(q => predict(tree, q) === q[2]).length / pts.length, nl = leaves(tree).length;
    note.innerHTML = `<b>${nl} feuilles</b> · exactitude sur ces points : <b>${(acc * 100).toFixed(0)}${" "}%</b>. ` + (+depth.value <= 2 ? "Peu profond : des frontières grossières, l'arbre sous-apprend." : +depth.value >= 7 ? "Très profond : l'arbre isole des points de bruit dans de minuscules rectangles. Il surapprend." : "Les coupes sont toujours parallèles aux axes : l'arbre approche la frontière courbe par des marches d'escalier.");
  };
  depth.addEventListener("input", draw); draw();
};

/* ---------- boosting pas à pas ---------- */
VIZ.boost = el => {
  const { body, ctrl, note } = vizShell(el, "Le boosting corrige ses erreurs", "boosting");
  const r = mulberry(3), N = 70, xs = Array.from({ length: N }, (_, i) => i / (N - 1) * 6).map(x => x + (r() - .5) * .05), ys = xs.map(x => Math.sin(x) * 3 + gauss(r) * 0.45);
  const mean = ys.reduce((a, b) => a + b, 0) / N;
  const stump = res => { let best = null; for (let i = 1; i < N; i++) { const t = (xs[i - 1] + xs[i]) / 2, L = res.slice(0, i), R = res.slice(i), ml = L.reduce((a, b) => a + b, 0) / L.length, mr = R.reduce((a, b) => a + b, 0) / R.length, e = L.reduce((a, v) => a + (v - ml) ** 2, 0) + R.reduce((a, v) => a + (v - mr) ** 2, 0); if (!best || e < best.e) best = { t, ml, mr, e }; } return x => x <= best.t ? best.ml : best.mr; };
  const it = rangeCtl(ctrl, `bi${++vizUid}`, "Nombre d'arbres", 0, 150, 1, 0);
  const eta = rangeCtl(ctrl, `be${vizUid}`, "Taux η", 0.05, 1, 0.05, 0.2, v => v.toFixed(2));
  let cache = {};
  const run = (m, e) => { const key = e; if (!cache[key]) { const preds = [ys.map(() => mean)]; let p = preds[0].slice(); for (let k = 0; k < 150; k++) { const h = stump(ys.map((v, i) => v - p[i])); p = p.map((v, i) => v + e * h(xs[i])); preds.push(p.slice()); } cache[key] = preds; } return cache[key][m]; };
  const draw = () => {
    const m = +it.value, e = +eta.value, p = run(m, e);
    const X = x => 20 + x / 6 * 560, Y = y => 120 - y * 30;
    let svg = `<svg viewBox="0 0 600 240"><line x1="20" x2="580" y1="120" y2="120" class="vz-line"/>`;
    xs.forEach((x, i) => { svg += `<line x1="${X(x)}" x2="${X(x)}" y1="${Y(ys[i])}" y2="${Y(p[i])}" class="vz-serr" stroke-opacity=".45"/><circle cx="${X(x)}" cy="${Y(ys[i])}" r="3.5" class="vz-accent"/>`; });
    svg += `<path d="${xs.map((x, i) => `${i ? "L" : "M"}${X(x)} ${Y(p[i])}`).join(" ")}" fill="none" class="vz-sink" stroke-width="2.2"/></svg>`;
    body.innerHTML = svg;
    const mse = ys.reduce((a, v, i) => a + (v - p[i]) ** 2, 0) / N;
    note.innerHTML = `Après <b>${m}</b> arbre${m > 1 ? "s" : ""} : MSE = <b>${mse.toFixed(3)}</b>. Les traits rouges sont les <b>résidus</b> : chaque nouvel arbre (une simple « marche ») apprend à les réduire. ` + (m === 0 ? "Au départ, on prédit la moyenne." : e > 0.6 ? "Avec un grand η, chaque arbre corrige brutalement : on risque de surapprendre." : "");
  };
  it.addEventListener("input", draw); eta.addEventListener("input", draw); draw();
};

/* ---------- séries temporelles ---------- */
VIZ.ts = el => {
  const { body, ctrl, note } = vizShell(el, "Tendance, saisonnalité et moyenne mobile", "séries temporelles");
  const r = mulberry(9), N = 365, ys = Array.from({ length: N }, (_, t) => { const d = new Date(2025, 0, 1 + t), we = d.getDay() === 0 || d.getDay() === 6; return (200 + 0.15 * t) * (we ? 1.35 : 1) * (1 + 0.45 * Math.sin(2 * Math.PI * (t - 110) / 365)) + gauss(r) * 18; });
  const win = rangeCtl(ctrl, `tw${++vizUid}`, "Fenêtre (jours)", 1, 60, 1, 7);
  const show = h(`<label><input type="checkbox" id="tf${vizUid}"> Prévision saisonnière naïve (30 derniers jours)</label>`); ctrl.appendChild(show);
  const draw = () => {
    const w = +win.value, lo = Math.min(...ys), hi = Math.max(...ys);
    const X = t => 20 + t / (N - 1) * 560, Y = v => 220 - (v - lo) / (hi - lo) * 200;
    const roll = ys.map((_, i) => { if (i < w - 1) return null; let s = 0; for (let k = i - w + 1; k <= i; k++) s += ys[k]; return s / w; });
    let svg = `<svg viewBox="0 0 600 240"><path d="${ys.map((v, i) => `${i ? "L" : "M"}${X(i)} ${Y(v)}`).join(" ")}" fill="none" class="vz-smuted" stroke-opacity=".45" stroke-width="1"/>`;
    svg += `<path d="${roll.map((v, i) => v == null ? "" : `${roll[i - 1] == null ? "M" : "L"}${X(i)} ${Y(v)}`).join(" ")}" fill="none" class="vz-sacc" stroke-width="2.4"/>`;
    let extra = "";
    if ($("input", show).checked) { const s = N - 30; svg += `<rect x="${X(s)}" y="10" width="${X(N - 1) - X(s)}" height="215" class="vz-mark" fill-opacity=".12"/><path d="${ys.slice(s).map((_, j) => `${j ? "L" : "M"}${X(s + j)} ${Y(ys[s + j - 7])}`).join(" ")}" fill="none" class="vz-serr" stroke-width="1.8" stroke-dasharray="4 3"/>`; const mae = ys.slice(s).reduce((a, v, j) => a + Math.abs(v - ys[s + j - 7]), 0) / 30; extra = ` Prévision saisonnière (pointillés rouges) : MAE = <b>${mae.toFixed(1)}</b>.`; }
    ["janv.", "avr.", "juil.", "oct."].forEach((m, i) => { svg += `<text x="${X(i * 91)}" y="238" class="vz-tm">${m}</text>`; });
    body.innerHTML = svg + "</svg>";
    note.innerHTML = (w === 1 ? "Fenêtre de 1 jour : la série brute, avec ses pics du week-end." : w === 7 ? "Fenêtre de <b>7 jours</b> : l'effet week-end disparaît exactement, il reste la tendance et la saison." : w > 30 ? "Fenêtre large : on ne voit plus que la tendance de fond et le cycle annuel." : `Moyenne mobile sur ${w} jours.`) + extra;
  };
  win.addEventListener("input", draw); $("input", show).addEventListener("change", draw); draw();
};

/* ---------- K-means pas à pas ---------- */
VIZ.kmeans = el => {
  const { body, ctrl, note } = vizShell(el, "K-means, étape par étape", "clustering");
  const r = mulberry(21);
  const pts = []; [[-1.2, -0.6], [1.3, -0.4], [0.1, 1.2]].forEach(([cx, cy]) => { for (let i = 0; i < 45; i++) pts.push([cx + gauss(r) * 0.45, cy + gauss(r) * 0.45]); });
  let K = 3, centres, labels, phase, iter;
  const init = () => { const rr = mulberry(Math.floor(Math.random() * 1e6)); centres = Array.from({ length: K }, () => pts[Math.floor(rr() * pts.length)].slice()); labels = pts.map(() => -1); phase = "affecter"; iter = 0; draw(); };
  const COLS = ["vz-accent", "vz-mark", "vz-ok", "vz-err", "vz-muted"];
  const inertie = () => labels[0] < 0 ? null : pts.reduce((a, p, i) => a + (p[0] - centres[labels[i]][0]) ** 2 + (p[1] - centres[labels[i]][1]) ** 2, 0);
  const step = () => {
    if (phase === "affecter") { labels = pts.map(p => { let b = 0, bd = Infinity; centres.forEach((c, j) => { const d = (p[0] - c[0]) ** 2 + (p[1] - c[1]) ** 2; if (d < bd) { bd = d; b = j; } }); return b; }); phase = "deplacer"; }
    else { centres = centres.map((c, j) => { const g = pts.filter((_, i) => labels[i] === j); return g.length ? [g.reduce((a, p) => a + p[0], 0) / g.length, g.reduce((a, p) => a + p[1], 0) / g.length] : c; }); phase = "affecter"; iter++; }
    draw();
  };
  const draw = () => {
    const X = x => 300 + x * 105, Y = y => 118 - y * 62;
    let svg = `<svg viewBox="0 0 600 250">`;
    pts.forEach((p, i) => { svg += `<circle cx="${X(p[0])}" cy="${Y(p[1])}" r="4" class="${labels[i] < 0 ? "vz-muted" : COLS[labels[i]]}" fill-opacity="${labels[i] < 0 ? .5 : .85}"/>`; });
    centres.forEach((c, j) => { svg += `<g transform="translate(${X(c[0])},${Y(c[1])})"><circle r="11" class="${COLS[j]}" stroke="var(--ink)" stroke-width="2.5"/><path d="M-5 0 H5 M0 -5 V5" class="vz-sink" stroke-width="2"/></g>`; });
    body.innerHTML = svg + "</svg>";
    const I = inertie();
    note.innerHTML = `Itération <b>${iter}</b>${I != null ? ` · inertie = <b>${I.toFixed(1)}</b>` : ""}. ` + (phase === "affecter" ? "Prochaine étape : <b>affecter</b> chaque point au centre le plus proche." : "Prochaine étape : <b>déplacer</b> chaque centre à la moyenne de ses points.") + " Relance avec un autre départ : le résultat peut changer, d'où <code>n_init=10</code>.";
    $$(".kbtn", ctrl).forEach(b => b.textContent = phase === "affecter" ? "Affecter les points" : "Déplacer les centres");
  };
  const b = btnCtl(ctrl, "Affecter les points", "btn small primary kbtn"); b.addEventListener("click", step);
  btnCtl(ctrl, "Nouveau départ").addEventListener("click", init);
  const ks = h(`<label for="kk${++vizUid}">k <select id="kk${vizUid}" class="btn small">${[2, 3, 4, 5].map(k => `<option ${k === 3 ? "selected" : ""}>${k}</option>`).join("")}</select></label>`); ctrl.appendChild(ks);
  $("select", ks).addEventListener("change", e => { K = +e.target.value; init(); });
  init();
};
