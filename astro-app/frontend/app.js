const $ = (s, el = document) => el.querySelector(s);
const state = { token: localStorage.getItem("token"), mode: "register", me: null, chart: null,
  lang: localStorage.getItem("lang") || ((navigator.language || "").toLowerCase().startsWith("fa") ? "fa" : "en") };

/* ---------- Translations ---------- */
const T = {
  en: {
    brand: "Stellar Chart", signOut: "Sign out", switchTo: "فارسی",
    heroTitle: "The sky at the minute you were born, read for you every morning.",
    heroText: "Enter your birth date, time and place. We calculate your natal chart with the Swiss Ephemeris, then send a personal reading each day and answer your questions about it.",
    tabRegister: "Create account", tabLogin: "Sign in", fullName: "Full name", email: "Email", password: "Password",
    subTitle: "Start your subscription",
    subText: "Daily readings and questions need an active plan. Pay in USDT; your plan starts as soon as the payment confirms.",
    payBtn: "Pay with USDT",
    wheelEmpty: "Your chart wheel appears here once your birth details are saved.",
    birthTitle: "Birth details", birthDate: "Date of birth", birthTime: "Time of birth",
    birthTimeHint: "as on the birth certificate; leave empty if unknown", birthPlace: "Place of birth",
    placePh: "City, country", calcBtn: "Calculate my chart", calculating: "Calculating…",
    placementsTitle: "Placements", thBody: "Body", thPos: "Position", thHouse: "House",
    reportTitle: "Your chart report", reportLoading: "Writing your chart report…",
    todayTitle: "Today", todayLoading: "Loading today's reading…",
    askTitle: "Ask about your chart", askPh: "For example: What does my chart say about changing careers this year?",
    askBtn: "Ask", asking: "Reading your chart…",
    notifTitle: "Notifications", sendAt: "Send my reading at", localTime: "local time",
    emailMe: "Email me the daily reading", telegramConnected: "Telegram is connected.",
    telegramLink: "Connect Telegram", telegramAfter: " to get readings there.",
    deleteAcc: "Delete my account and data",
    deleteConfirm: "Delete your account, chart and reading history permanently?",
    disclaimer: "Astrology readings are for reflection and entertainment and are not professional advice.",
    sun: "Sun", moon: "Moon", rising: "Rising", retro: "retrograde", asc: "ASC",
    saved: (place, tz, sys) => `Saved: ${place} (${tz}). ${sys} houses.`,
    savedNoTime: (place, tz) => `Saved: ${place} (${tz}). Birth time unknown, so houses and rising sign are not shown.`,
    generic: "Something went wrong. Try again.",
  },
  fa: {
    brand: "استلار چارت", signOut: "خروج", switchTo: "English",
    heroTitle: "آسمانِ لحظهٔ تولد شما، هر صبح برای شما خوانده می‌شود.",
    heroText: "تاریخ، ساعت و محل تولدتان را وارد کنید. ما چارت تولد شما را با دقت نجومی (Swiss Ephemeris) محاسبه می‌کنیم، سپس هر روز پیامی شخصی برایتان می‌فرستیم و به پرسش‌هایتان دربارهٔ آن پاسخ می‌دهیم.",
    tabRegister: "ساخت حساب", tabLogin: "ورود", fullName: "نام و نام خانوادگی", email: "ایمیل", password: "رمز عبور",
    subTitle: "اشتراک خود را فعال کنید",
    subText: "پیام‌های روزانه و پرسش‌ها به اشتراک فعال نیاز دارند. با USDT پرداخت کنید؛ اشتراک شما به محض تأیید پرداخت فعال می‌شود.",
    payBtn: "پرداخت با USDT",
    wheelEmpty: "پس از ثبت اطلاعات تولد، چرخهٔ چارت شما اینجا نمایش داده می‌شود.",
    birthTitle: "اطلاعات تولد", birthDate: "تاریخ تولد (میلادی)", birthTime: "ساعت تولد",
    birthTimeHint: "مطابق شناسنامه یا گواهی تولد؛ اگر نمی‌دانید خالی بگذارید", birthPlace: "محل تولد",
    placePh: "شهر، کشور", calcBtn: "محاسبهٔ چارت من", calculating: "در حال محاسبه…",
    placementsTitle: "جایگاه سیارات", thBody: "سیاره", thPos: "موقعیت", thHouse: "خانه",
    reportTitle: "گزارش چارت شما", reportLoading: "در حال نوشتن گزارش چارت شما…",
    todayTitle: "امروز", todayLoading: "در حال بارگذاری پیام امروز…",
    askTitle: "دربارهٔ چارت خود بپرسید", askPh: "مثلاً: چارت من دربارهٔ تغییر شغل در امسال چه می‌گوید؟",
    askBtn: "بپرس", asking: "در حال بررسی چارت شما…",
    notifTitle: "اعلان‌ها", sendAt: "ارسال پیام روزانه در ساعت", localTime: "به وقت محلی",
    emailMe: "پیام روزانه را برایم ایمیل کن", telegramConnected: "تلگرام متصل است.",
    telegramLink: "اتصال به تلگرام", telegramAfter: " تا پیام‌ها را آنجا دریافت کنید.",
    deleteAcc: "حذف حساب و اطلاعات من",
    deleteConfirm: "حساب، چارت و تاریخچهٔ پیام‌های شما برای همیشه حذف شود؟",
    disclaimer: "خوانش‌های طالع‌بینی برای تأمل و سرگرمی هستند و جایگزین مشاورهٔ تخصصی نیستند.",
    sun: "خورشید", moon: "ماه", rising: "طالع", retro: "بازگشتی", asc: "طالع",
    saved: (place, tz, sys) => `ذخیره شد: ${place} (${tz}). سیستم خانه‌ها: ${sys}.`,
    savedNoTime: (place, tz) => `ذخیره شد: ${place} (${tz}). ساعت تولد نامشخص است، بنابراین خانه‌ها و طالع نمایش داده نمی‌شوند.`,
    generic: "مشکلی پیش آمد. دوباره تلاش کنید.",
  },
};
const t = k => T[state.lang][k] ?? T.en[k] ?? k;

const NAMES_FA = {
  Sun: "خورشید", Moon: "ماه", Mercury: "عطارد", Venus: "زهره", Mars: "مریخ", Jupiter: "مشتری", Saturn: "زحل",
  Uranus: "اورانوس", Neptune: "نپتون", Pluto: "پلوتو", "North Node": "گره شمالی",
  Ascendant: "طالع", Midheaven: "میانه‌آسمان",
  Aries: "حمل", Taurus: "ثور", Gemini: "جوزا", Cancer: "سرطان", Leo: "اسد", Virgo: "سنبله", Libra: "میزان",
  Scorpio: "عقرب", Sagittarius: "قوس", Capricorn: "جدی", Aquarius: "دلو", Pisces: "حوت",
  Placidus: "پلاسیدوس", "Whole Sign": "برج کامل",
};
const nm = s => state.lang === "fa" ? (NAMES_FA[s] || s) : s;
const num = v => state.lang === "fa" ? String(v).replace(/\d/g, d => "۰۱۲۳۴۵۶۷۸۹"[d]) : String(v);

// Server messages shown in Persian when the Persian interface is active
const ERR_FA = {
  "Email or password is incorrect.": "ایمیل یا رمز عبور اشتباه است.",
  "An account with this email already exists. Sign in instead.": "حسابی با این ایمیل وجود دارد. لطفاً وارد شوید.",
  "Sign in to continue.": "برای ادامه وارد شوید.",
  "Your session expired. Sign in again.": "نشست شما منقضی شده است. دوباره وارد شوید.",
  "An active subscription is required.": "برای این بخش به اشتراک فعال نیاز است.",
  "Payments are not configured yet.": "پرداخت هنوز راه‌اندازی نشده است.",
  "Could not create the payment. Try again in a minute.": "ایجاد پرداخت ممکن نشد. یک دقیقه دیگر دوباره تلاش کنید.",
  "Add your birth details first.": "ابتدا اطلاعات تولد خود را وارد کنید.",
  "Birth time must look like 14:30.": "ساعت تولد باید به شکل ۱۴:۳۰ باشد.",
  "Your full chart report is included with a subscription.": "گزارش کامل چارت با اشتراک در دسترس است.",
};
function translateError(msg) {
  if (state.lang !== "fa" || !msg) return msg;
  if (ERR_FA[msg]) return ERR_FA[msg];
  let m;
  if ((m = msg.match(/^Could not find '(.+?)'/))) return `محل «${m[1]}» پیدا نشد. نام استان یا کشور را هم اضافه کنید.`;
  if (/^You've used your/.test(msg)) return "سهمیهٔ پرسش‌های امروز شما تمام شده است. فردا دوباره می‌توانید بپرسید.";
  if (/at least 8 characters/.test(msg)) return "رمز عبور باید حداقل ۸ کاراکتر باشد.";
  if (/valid email/.test(msg)) return "ایمیل معتبر نیست.";
  return msg;
}

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
    const err = new Error(translateError(msg) || t("generic"));
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

/* ---------- Language ---------- */
function applyLang() {
  const fa = state.lang === "fa";
  document.documentElement.lang = state.lang;
  document.documentElement.dir = fa ? "rtl" : "ltr";
  document.title = t("brand");
  document.querySelectorAll("[data-i18n]").forEach(el => el.textContent = t(el.dataset.i18n));
  document.querySelectorAll("[data-i18n-ph]").forEach(el => el.placeholder = t(el.dataset.i18nPh));
  $("#lang").textContent = t("switchTo");
  $("#lang").lang = fa ? "en" : "fa";
  setMode(state.mode);
  if (state.me) renderSettings(state.me);
  if (state.chart) { renderChart(state.chart); loadReport(); }
}
$("#lang").onclick = () => {
  state.lang = state.lang === "fa" ? "en" : "fa";
  localStorage.setItem("lang", state.lang);
  applyLang();
};

/* ---------- Auth ---------- */
function setMode(mode) {
  state.mode = mode;
  document.querySelectorAll(".tabs button").forEach(b => b.setAttribute("aria-selected", b.dataset.mode === mode));
  document.querySelectorAll("[data-only=register]").forEach(el => el.hidden = mode !== "register");
  $("#auth-form .primary").textContent = mode === "register" ? t("tabRegister") : t("tabLogin");
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

$("#logout").onclick = () => {
  localStorage.removeItem("token"); state.token = null; state.me = null; state.chart = null; show("auth");
};

/* ---------- Chart wheel ---------- */
function wheelSVG(chart) {
  const size = 560, c = size / 2, rOuter = 270, rSign = 235, rInner = 200, rPlanet = 165;
  const asc = chart.angles ? chart.angles.Ascendant.longitude : 0;
  const pt = (lon, r) => {
    const a = (180 + (lon - asc)) * Math.PI / 180;
    return [c + r * Math.cos(a), c - r * Math.sin(a)];
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
  const colors = { trine: "var(--brass)", sextile: "var(--brass)", square: "var(--rose)", opposition: "var(--rose)" };
  chart.aspects.filter(a => a.aspect !== "conjunction").forEach(a => {
    const [x1, y1] = pt(chart.planets[a.a].longitude, 70), [x2, y2] = pt(chart.planets[a.b].longitude, 70);
    s += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${colors[a.aspect]}" stroke-opacity=".55"/>`;
  });
  const placed = Object.entries(chart.planets).sort((a, b) => a[1].longitude - b[1].longitude);
  let last = -99;
  placed.forEach(([name, p], i) => {
    let lon = p.longitude;
    if (lon - last < 7) lon = last + 7;
    last = lon;
    const [x, y] = pt(lon, rPlanet - (i % 2) * 18), [tx, ty] = pt(p.longitude, rInner);
    const [dx, dy] = pt(p.longitude, rInner - 8);
    s += `<line x1="${tx}" y1="${ty}" x2="${dx}" y2="${dy}" stroke="var(--ink)"/>
          <text x="${x}" y="${y}" text-anchor="middle" dominant-baseline="central" class="glyph" font-size="21" fill="var(--ink)"><title>${nm(name)} ${fmtPos(p)}</title>${PLANET_GLYPHS[name]}</text>`;
  });
  if (chart.angles) {
    const [ax, ay] = pt(asc, rOuter + 2);
    s += `<text x="${ax - 6}" y="${ay}" text-anchor="end" dominant-baseline="central" font-size="13" fill="var(--muted)" font-family="var(--body)">${t("asc")}</text>`;
  }
  return s + "</svg>";
}

// "4°17' Taurus" in English, "۴°۱۷′ ثور" in Persian
function fmtPos(p) {
  let d = Math.floor(p.degree), m = Math.round((p.degree - d) * 60);
  if (m === 60) { d += 1; m = 0; }
  if (d >= 30) { d = 29; m = 59; }
  return `${num(d)}°${num(String(m).padStart(2, "0"))}′ ${nm(p.sign)}`;
}

function renderChart(data) {
  state.chart = data;
  const { birth, chart } = data;
  $("#wheel").innerHTML = wheelSVG(chart);
  const sm = chart.summary;
  $("#big-three").innerHTML = `<span>${t("sun")}</span><b>${nm(sm.sun)}</b><span>${t("moon")}</span><b>${nm(sm.moon)}</b>` +
    (sm.rising ? `<span>${t("rising")}</span><b>${nm(sm.rising)}</b>` : "");
  const rows = Object.entries(chart.planets).map(([n, p]) =>
    `<tr><td><span class="glyph">${PLANET_GLYPHS[n]}</span>${nm(n)}</td><td>${fmtPos(p)}${p.retrograde ? ` (${t("retro")})` : ""}</td><td>${p.house ? num(p.house) : "—"}</td></tr>`);
  if (chart.angles) Object.entries(chart.angles).forEach(([n, a]) =>
    rows.push(`<tr><td>${nm(n)}</td><td>${fmtPos(a)}</td><td>—</td></tr>`));
  $("#placements tbody").innerHTML = rows.join("");
  $("#placements").hidden = false;
  const f = $("#birth-form");
  f.birth_date.value = birth.date; f.birth_time.value = birth.time || ""; f.birth_place.value = birth.place.split(",")[0];
  $("#birth-saved").textContent = chart.time_known
    ? T[state.lang].saved(birth.place, birth.timezone, nm(chart.house_system))
    : T[state.lang].savedNoTime(birth.place, birth.timezone);
}

$("#birth-form").onsubmit = async e => {
  e.preventDefault();
  const f = e.target, err = $(".error", f), btn = $(".primary", f);
  err.textContent = ""; btn.disabled = true; btn.textContent = t("calculating");
  try {
    renderChart(await api("/api/chart", { method: "POST", body: {
      birth_date: f.birth_date.value, birth_time: f.birth_time.value || null, birth_place: f.birth_place.value } }));
    state.me.has_chart = true;
    loadReport();
    loadSubscriberContent();
  } catch (x) { err.textContent = x.message; }
  btn.disabled = false; btn.textContent = t("calcBtn");
};

/* ---------- Subscription ---------- */
$("#subscribe").onclick = async e => {
  e.target.disabled = true;
  try { location.href = (await api("/api/payments/subscribe", { method: "POST" })).invoice_url; }
  catch (x) { alert(x.message); e.target.disabled = false; }
};

/* ---------- Report, readings & questions ---------- */
const esc = s => s.replace(/[&<>]/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[ch]));
const paras = s => esc(s).split(/\n{2,}/).map(p => `<p>${p}</p>`).join("");
const reportHTML = s => esc(s).replace(/\*\*/g, "").split("\n").map(l => l.trim()).reduce((out, line) => {
  if (line.startsWith("## ")) out.push({ h: line.slice(3) });
  else if (!line) out.push({ p: "" });
  else if (out.length && out[out.length - 1].p !== undefined) out[out.length - 1].p += (out[out.length - 1].p ? " " : "") + line;
  else out.push({ p: line });
  return out;
}, []).map(b => b.h !== undefined ? `<h3>${b.h}</h3>` : b.p ? `<p>${b.p}</p>` : "").join("");

let reportRequest = 0;
async function loadReport() {
  const id = ++reportRequest;
  $("#report-panel").hidden = false;
  $("#report").innerHTML = `<p class="hint">${t("reportLoading")}</p>`;
  try {
    const r = await api(`/api/chart/report?lang=${state.lang}`);
    if (id === reportRequest) $("#report").innerHTML = reportHTML(r.content);
  } catch (x) {
    if (id !== reportRequest) return;
    $("#report").innerHTML = x.status === 402 ? `<p>${esc(x.message)}</p>` : `<p class="error">${esc(x.message)}</p>`;
  }
}

async function loadSubscriberContent() {
  const ok = state.me.is_active_subscriber && state.me.has_chart;
  $("#today-panel").hidden = $("#ask-panel").hidden = !ok;
  if (!ok) return;
  $("#today").innerHTML = `<p class="hint">${t("todayLoading")}</p>`;
  api("/api/today").then(r => $("#today").innerHTML = paras(r.content))
    .catch(x => $("#today").innerHTML = `<p class="error">${esc(x.message)}</p>`);
  const msgs = await api("/api/messages");
  $("#history").innerHTML = msgs.filter(m => m.kind === "question").map(m =>
    `<li><p class="q">${esc(m.question)}</p><div class="a">${esc(m.content)}</div></li>`).join("");
}

$("#ask-form").onsubmit = async e => {
  e.preventDefault();
  const f = e.target, err = $(".error", f), btn = $(".primary", f);
  err.textContent = ""; btn.disabled = true; btn.textContent = t("asking");
  try {
    const m = await api("/api/ask", { method: "POST", body: { question: f.question.value } });
    $("#history").insertAdjacentHTML("afterbegin",
      `<li><p class="q">${esc(m.question)}</p><div class="a">${esc(m.content)}</div></li>`);
    f.reset();
  } catch (x) { err.textContent = x.message; }
  btn.disabled = false; btn.textContent = t("askBtn");
};

/* ---------- Settings ---------- */
function renderSettings(me) {
  const sel = $("#settings select");
  sel.innerHTML = Array.from({ length: 24 }, (_, h) => `<option value="${h}">${num(String(h).padStart(2, "0"))}:${num("00")}</option>`).join("");
  sel.value = me.notify_hour;
  $("#settings [name=notify_email]").checked = me.notify_email;
  $("#telegram").innerHTML = me.telegram_connected ? esc(t("telegramConnected"))
    : me.telegram_link ? `<a href="${me.telegram_link}" target="_blank" rel="noopener">${t("telegramLink")}</a>${t("telegramAfter")}` : "";
}
$("#settings select").onchange = e => api("/api/me", { method: "PATCH", body: { notify_hour: +e.target.value } });
$("#settings [name=notify_email]").onchange = e => api("/api/me", { method: "PATCH", body: { notify_email: e.target.checked } });
$("#delete-account").onclick = async () => {
  if (!confirm(t("deleteConfirm"))) return;
  await api("/api/me", { method: "DELETE" });
  $("#logout").click();
};

/* ---------- Boot ---------- */
async function boot() {
  applyLang();
  if (!state.token) { setMode("register"); return show("auth"); }
  try { state.me = await api("/api/me"); }
  catch { localStorage.removeItem("token"); state.token = null; return show("auth"); }
  show("app");
  $("#subscription").hidden = state.me.is_active_subscriber;
  renderSettings(state.me);
  if (state.me.has_chart) { renderChart(await api("/api/chart")); loadReport(); }
  loadSubscriberContent();
}
boot();
