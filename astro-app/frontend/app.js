const $ = (s, el = document) => el.querySelector(s);
const state = { token: localStorage.getItem("token"), mode: "register", me: null };

const PLANET_GLYPHS = { Sun: "☉", Moon: "☽", Mercury: "☿", Venus: "♀", Mars: "♂", Jupiter: "♃",
  Saturn: "♄", Uranus: "♅", Neptune: "♆", Pluto: "♇", "North Node": "☊" };
const SIGN_GLYPHS = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"].map(g => g + "\uFE0E");

async function api(path, opts = {}) {
  const res = await fetch(path, {
    ...opts,
    headers: { "Content-Type": "application/json",
               ...(state.token ? { Authorization: `Bearer ${state.token}` } : {}) },
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    let msg = data.detail;
    if (Array.isArray(msg)) msg = msg.map(d => d.msg.replace(/^Value error, /, "")).join(" ");
    const err = new Error(msg || "Something went wrong. Try again.");
    err.status = res.status;
    throw err;
  }
  return data;
}

function show(view) {
  $("#view-auth").hidden = view !== "auth";
  $("#view-app").hidden = view !== "app";
  $("#logout").hidden = view !== "app";
}

/* ---------- Auth ---------- */
function setMode(mode) {
  state.mode = mode;
  document.querySelectorAll(".tabs button").forEach(b => b.setAttribute("aria-selected", b.dataset.mode === mode));
  document.querySelectorAll("[data-only=register]").forEach(el => el.hidden = mode !== "register");
  $("#auth-form .primary").textContent = mode === "register" ? "Create account" : "Sign in";
}
document.querySelectorAll(".tabs button").forEach(b => b.onclick = () => setMode(b.dataset.mode));

$("#auth-form").onsubmit = async e => {
  e.preventDefault();
  const f = new FormData(e.target), err = $(".error", e.target);
  err.textContent = "";
  const body = { email: f.get("email"), password: f.get("password") };
  if (state.mode === "register") body.full_name = f.get("full_name");
  try {
    const { access_token } = await api(`/api/${state.mode}`, { method: "POST", body });
    state.token = access_token;
    localStorage.setItem("token", access_token);
    boot();
  } catch (x) { err.textContent = x.message; }
};

$("#logout").onclick = () => { localStorage.removeItem("token"); state.token = null; show("auth"); };

/* ---------- Chart wheel ---------- */
function wheelSVG(chart) {
  const size = 560, c = size / 2, rOuter = 270, rSign = 235, rInner = 200, rPlanet = 165;
  const asc = chart.angles ? chart.angles.Ascendant.longitude : 0;
  const pt = (lon, r) => {
    const t = (180 + (lon - asc)) * Math.PI / 180;
    return [c + r * Math.cos(t), c - r * Math.sin(t)];
  };
  let s = `<svg viewBox="0 0 ${size} ${size}" role="img" xmlns="http://www.w3.org/2000/svg">
    <circle cx="${c}" cy="${c}" r="${rOuter}" fill="none" stroke="var(--line)" stroke-width="1.5"/>
    <circle cx="${c}" cy="${c}" r="${rInner}" fill="none" stroke="var(--line)"/>
    <circle cx="${c}" cy="${c}" r="70" fill="none" stroke="var(--line)"/>`;
  for (let i = 0; i < 12; i++) {
    const [x1, y1] = pt(i * 30, rInner), [x2, y2] = pt(i * 30, rOuter), [gx, gy] = pt(i * 30 + 15, rSign);
    s += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="var(--line)"/>
          <text x="${gx}" y="${gy}" text-anchor="middle" dominant-baseline="central" class="glyph" font-size="22" fill="var(--muted)">${SIGN_GLYPHS[i]}</text>`;
  }
  if (chart.houses) chart.houses.forEach(h => {
    const [x1, y1] = pt(h.longitude, 70), [x2, y2] = pt(h.longitude, rInner);
    const strong = [1, 4, 7, 10].includes(h.house);
    s += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${strong ? "var(--ink)" : "var(--line)"}" stroke-width="${strong ? 1.6 : 1}"/>`;
  });
  // Aspect lines between planets
  const colors = { trine: "var(--brass)", sextile: "var(--brass)", square: "var(--rose)", opposition: "var(--rose)" };
  chart.aspects.filter(a => a.aspect !== "conjunction").forEach(a => {
    const [x1, y1] = pt(chart.planets[a.a].longitude, 70), [x2, y2] = pt(chart.planets[a.b].longitude, 70);
    s += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${colors[a.aspect]}" stroke-opacity=".55"/>`;
  });
  // Planets, nudged apart when crowded
  const placed = Object.entries(chart.planets).sort((a, b) => a[1].longitude - b[1].longitude);
  let last = -99;
  placed.forEach(([name, p], i) => {
    let lon = p.longitude;
    if (lon - last < 7) lon = last + 7;
    last = lon;
    const [x, y] = pt(lon, rPlanet - (i % 2) * 18), [tx, ty] = pt(p.longitude, rInner);
    const [dx, dy] = pt(p.longitude, rInner - 8);
    s += `<line x1="${tx}" y1="${ty}" x2="${dx}" y2="${dy}" stroke="var(--ink)"/>
          <text x="${x}" y="${y}" text-anchor="middle" dominant-baseline="central" class="glyph" font-size="21" fill="var(--ink)"><title>${name} ${p.formatted}</title>${PLANET_GLYPHS[name]}</text>`;
  });
  if (chart.angles) {
    const [ax, ay] = pt(asc, rOuter + 2);
    s += `<text x="${ax - 6}" y="${ay}" text-anchor="end" dominant-baseline="central" font-size="13" fill="var(--muted)">ASC</text>`;
  }
  return s + "</svg>";
}

function renderChart({ birth, chart }) {
  $("#wheel").innerHTML = wheelSVG(chart);
  const sm = chart.summary;
  $("#big-three").innerHTML = `<span>Sun</span><b>${sm.sun}</b><span>Moon</span><b>${sm.moon}</b>` +
    (sm.rising ? `<span>Rising</span><b>${sm.rising}</b>` : "");
  const rows = Object.entries(chart.planets).map(([n, p]) =>
    `<tr><td><span class="glyph">${PLANET_GLYPHS[n]}</span>${n}</td><td>${p.formatted}${p.retrograde ? " (retrograde)" : ""}</td><td>${p.house ?? "—"}</td></tr>`);
  if (chart.angles) Object.entries(chart.angles).forEach(([n, a]) => rows.push(`<tr><td>${n}</td><td>${a.formatted}</td><td>—</td></tr>`));
  $("#placements tbody").innerHTML = rows.join("");
  $("#placements").hidden = false;
  const f = $("#birth-form");
  f.birth_date.value = birth.date; f.birth_time.value = birth.time || ""; f.birth_place.value = birth.place.split(",")[0];
  $("#birth-saved").textContent = `Saved: ${birth.place} (${birth.timezone}). ` +
    (chart.time_known ? `${chart.house_system} houses.` : "Birth time unknown, so houses and rising sign are not shown.");
}

$("#birth-form").onsubmit = async e => {
  e.preventDefault();
  const f = e.target, err = $(".error", f), btn = $(".primary", f);
  err.textContent = ""; btn.disabled = true; btn.textContent = "Calculating…";
  try {
    renderChart(await api("/api/chart", { method: "POST", body: {
      birth_date: f.birth_date.value, birth_time: f.birth_time.value || null, birth_place: f.birth_place.value } }));
    state.me.has_chart = true;
    loadSubscriberContent();
  } catch (x) { err.textContent = x.message; }
  btn.disabled = false; btn.textContent = "Calculate my chart";
};

/* ---------- Subscription ---------- */
$("#subscribe").onclick = async e => {
  e.target.disabled = true;
  try { location.href = (await api("/api/payments/subscribe", { method: "POST" })).invoice_url; }
  catch (x) { alert(x.message); e.target.disabled = false; }
};

/* ---------- Readings & questions ---------- */
const esc = t => t.replace(/[&<>]/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[ch]));
const paras = t => esc(t).split(/\n{2,}/).map(p => `<p>${p}</p>`).join("");

async function loadSubscriberContent() {
  const ok = state.me.is_active_subscriber && state.me.has_chart;
  $("#today-panel").hidden = $("#ask-panel").hidden = !ok;
  if (!ok) return;
  api("/api/today").then(r => $("#today").innerHTML = paras(r.content))
    .catch(x => $("#today").innerHTML = `<p class="error">${esc(x.message)}</p>`);
  const msgs = await api("/api/messages");
  $("#history").innerHTML = msgs.filter(m => m.kind === "question").map(m =>
    `<li><p class="q">${esc(m.question)}</p><div class="a">${esc(m.content)}</div></li>`).join("");
}

$("#ask-form").onsubmit = async e => {
  e.preventDefault();
  const f = e.target, err = $(".error", f), btn = $(".primary", f);
  err.textContent = ""; btn.disabled = true; btn.textContent = "Reading your chart…";
  try {
    const m = await api("/api/ask", { method: "POST", body: { question: f.question.value } });
    $("#history").insertAdjacentHTML("afterbegin",
      `<li><p class="q">${esc(m.question)}</p><div class="a">${esc(m.content)}</div></li>`);
    f.reset();
  } catch (x) { err.textContent = x.message; }
  btn.disabled = false; btn.textContent = "Ask";
};

/* ---------- Settings ---------- */
function renderSettings(me) {
  const sel = $("#settings select");
  sel.innerHTML = Array.from({ length: 24 }, (_, h) => `<option value="${h}">${String(h).padStart(2, "0")}:00</option>`).join("");
  sel.value = me.notify_hour;
  $("#settings [name=notify_email]").checked = me.notify_email;
  $("#telegram").innerHTML = me.telegram_connected ? "Telegram is connected."
    : me.telegram_link ? `<a href="${me.telegram_link}" target="_blank" rel="noopener">Connect Telegram</a> to get readings there.` : "";
}
$("#settings select").onchange = e => api("/api/me", { method: "PATCH", body: { notify_hour: +e.target.value } });
$("#settings [name=notify_email]").onchange = e => api("/api/me", { method: "PATCH", body: { notify_email: e.target.checked } });
$("#delete-account").onclick = async () => {
  if (!confirm("Delete your account, chart and reading history permanently?")) return;
  await api("/api/me", { method: "DELETE" });
  $("#logout").click();
};

/* ---------- Boot ---------- */
async function boot() {
  if (!state.token) { setMode("register"); return show("auth"); }
  try { state.me = await api("/api/me"); }
  catch { localStorage.removeItem("token"); state.token = null; return show("auth"); }
  show("app");
  $("#subscription").hidden = state.me.is_active_subscriber;
  renderSettings(state.me);
  if (state.me.has_chart) renderChart(await api("/api/chart"));
  loadSubscriberContent();
}
boot();
