/*
 * Conector Jira para la Consola de Soporte CMQ — versión Cloudflare Worker.
 * Port 1:1 de tablero/main.py (Python) a JavaScript, para que el token de Jira
 * viva en un secreto de Cloudflare (nunca en el navegador, nunca en git) y
 * cualquiera con el link público de la Consola pueda traer datos de Jira sin
 * instalar nada local.
 *
 * CONTRATO DE DATOS: igual que main.py — no cambiar los nombres de campos de
 * "registros" ni de "sla" sin actualizar ticketTimes() en el HTML también.
 *
 * Variables de entorno (Cloudflare secrets, ver wrangler.toml / wrangler secret put):
 *   JIRA_BASE_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN
 */

const PROJECTS = { CMQ: "SG", CERVEPAR: "CERVEPAR" };

function authHeader(email, token) {
  // btoa no soporta UTF-8 directo; email/token de Jira son ASCII así que alcanza,
  // pero se usa un encoder seguro por las dudas.
  const bytes = new TextEncoder().encode(`${email}:${token}`);
  let bin = "";
  bytes.forEach((b) => (bin += String.fromCharCode(b)));
  return "Basic " + btoa(bin);
}

async function jget(base, auth, path, params) {
  const url = new URL(base + path);
  if (params) Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), 40000);
  try {
    const res = await fetch(url.toString(), {
      headers: { Authorization: auth, Accept: "application/json" },
      signal: ctrl.signal,
    });
    if (!res.ok) {
      const err = new Error(`HTTP ${res.status} ${res.statusText}`);
      err.httpStatus = res.status;
      err.detail = (await res.text().catch(() => "")).slice(0, 400);
      throw err;
    }
    return await res.json();
  } finally {
    clearTimeout(t);
  }
}

async function jpost(base, auth, path, body, retries = 2) {
  let lastErr;
  for (let attempt = 0; attempt <= retries; attempt++) {
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), 40000);
    try {
      const res = await fetch(base + path, {
        method: "POST",
        headers: { Authorization: auth, Accept: "application/json", "Content-Type": "application/json" },
        body: JSON.stringify(body),
        signal: ctrl.signal,
      });
      clearTimeout(t);
      if (!res.ok) {
        // Error real de Jira (400/401/etc.) — no tiene sentido reintentar.
        const err = new Error(`HTTP ${res.status} ${res.statusText}`);
        err.httpStatus = res.status;
        err.detail = (await res.text().catch(() => "")).slice(0, 400);
        throw err;
      }
      return await res.json();
    } catch (e) {
      clearTimeout(t);
      if (e.httpStatus) throw e; // error real de Jira, no reintentar
      lastErr = e;
      if (attempt < retries) await new Promise((r) => setTimeout(r, 1500 * (attempt + 1)));
    }
  }
  throw lastErr;
}

let _fieldsCache = null; // best-effort entre invocaciones "warm" del mismo Worker
async function detectFields(base, auth) {
  if (_fieldsCache) return _fieldsCache;
  let reqtype = null;
  const slas = {};
  try {
    const fields = await jget(base, auth, "/rest/api/3/field");
    for (const f of fields) {
      const name = (f.name || "").toLowerCase();
      const schema = f.schema || {};
      const custom = (schema.custom || "").toLowerCase();
      if (
        ["request type", "customer request type", "tipo de solicitud", "tipo de petición", "tipo de peticion", "tipo de pedido"].includes(name)
      ) {
        reqtype = f.id;
      }
      if (custom.includes("sla") || schema.type === "sla") slas[f.id] = f.name;
    }
  } catch (e) {
    // seguir sin Request Type / SLA si falla la detección
  }
  _fieldsCache = { reqtype, slas };
  return _fieldsCache;
}

function jqlFor(query, projKey) {
  const proj = projKey ? `project = ${projKey}` : "project in (SG, CERVEPAR)";
  const q = (query || "todos").toLowerCase();
  const m = {
    abiertos: `${proj} AND statusCategory != Done ORDER BY created DESC`,
    en_progreso: `${proj} AND statusCategory = "In Progress" ORDER BY created DESC`,
    resueltos_hoy: `${proj} AND resolved >= startOfDay() ORDER BY resolved DESC`,
    resueltos_semana: `${proj} AND resolved >= -7d ORDER BY resolved DESC`,
    resueltos_mes: `${proj} AND resolved >= -30d ORDER BY resolved DESC`,
    creados_hoy: `${proj} AND created >= startOfDay() ORDER BY created DESC`,
    creados_semana: `${proj} AND created >= -7d ORDER BY created DESC`,
    sin_asignar: `${proj} AND assignee is EMPTY AND statusCategory != Done ORDER BY created DESC`,
    alta_prioridad: `${proj} AND priority in (High, Highest) AND statusCategory != Done ORDER BY created DESC`,
  };
  return m[q] || `${proj} ORDER BY created DESC`;
}

async function search(base, auth, jql, fields, limit = 0) {
  const out = [];
  let token = null;
  while (true) {
    const body = { jql, fields, maxResults: 100, expand: "changelog" };
    if (token) body.nextPageToken = token;
    const data = await jpost(base, auth, "/rest/api/3/search/jql", body);
    out.push(...(data.issues || []));
    token = data.nextPageToken;
    if (!token || data.isLast || (limit && out.length >= limit)) break;
  }
  return out;
}

function adfText(node) {
  if (node == null) return "";
  if (typeof node === "string") return node;
  if (Array.isArray(node)) return node.map(adfText).join("");
  if (typeof node === "object") {
    let t = node.text || "";
    for (const c of node.content || []) t += adfText(c);
    if (node.type === "paragraph" || node.type === "heading") t += "\n";
    return t;
  }
  return "";
}

function parseSla(val) {
  if (!val || typeof val !== "object") return null;
  let cyc = val.ongoingCycle;
  let ongoing = true;
  if (!cyc) {
    const comp = val.completedCycles || [];
    cyc = comp.length ? comp[comp.length - 1] : null;
    ongoing = false;
  }
  if (!cyc) return null;
  return {
    elapsed_ms: (cyc.elapsedTime || {}).millis ?? null,
    goal_ms: (cyc.goalDuration || {}).millis ?? null,
    breached: !!cyc.breached,
    ongoing,
  };
}

function classifySla(name) {
  const n = (name || "").toLowerCase();
  if (n.includes("first response") || n.includes("primera respuesta") || n.includes("respuesta inicial")) return "first_response";
  if (n.includes("close after resolution") || n.includes("time to close")) return "close";
  if (n.includes("review")) return null;
  if (n.includes("resolution") || n.includes("resoluc")) return "resolution";
  if (n.includes("waiting for customer") || n.includes("waiting on customer") || (n.includes("espera") && n.includes("cliente")))
    return "waiting_customer";
  return null;
}

function isoTs(x) {
  if (!x) return null;
  // Jira devuelve "2026-07-30T10:00:00.000+0000" (sin ":" en el offset) o con "Z".
  const s = x.trim();
  const m = s.match(/^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?)(Z|[+-]\d{2}:?\d{2})?$/);
  if (!m) {
    const t = Date.parse(s);
    return isNaN(t) ? null : t / 1000;
  }
  let [, main, off] = m;
  if (!off || off === "Z") off = "+00:00";
  else if (!off.includes(":")) off = off.slice(0, 3) + ":" + off.slice(3);
  const t = Date.parse(main + off);
  return isNaN(t) ? null : t / 1000;
}

function isWaitingStatus(s) {
  s = (s || "").toLowerCase();
  return (
    s.includes("waiting for customer") ||
    s.includes("waiting on customer") ||
    (s.includes("espera") && s.includes("cliente")) ||
    (s.includes("esperando") && s.includes("cliente"))
  );
}

function waitingCustomerMs(issue) {
  const hist = ((issue.changelog || {}).histories) || [];
  const events = [];
  for (const h of hist) {
    const t = isoTs(h.created);
    for (const it of h.items || []) {
      if (it.field === "status") events.push([t, it.fromString, it.toString]);
    }
  }
  const evs = events.filter((e) => e[0] != null).sort((a, b) => a[0] - b[0]);
  let total = 0;
  let prevT = isoTs((issue.fields || {}).created);
  let cur = evs.length ? evs[0][1] : ((issue.fields || {}).status || {}).name;
  for (const [t, , to] of evs) {
    if (prevT != null && isWaitingStatus(cur)) total += Math.max(0, t - prevT);
    cur = to;
    prevT = t;
  }
  const now = Date.now() / 1000;
  if (prevT != null && isWaitingStatus(cur)) total += Math.max(0, now - prevT);
  return total > 0 ? Math.round(total * 1000) : null;
}

function toRegistro(issue, F) {
  const f = issue.fields || {};
  let tipo = "";
  const rt = F.reqtype ? f[F.reqtype] : null;
  if (rt && typeof rt === "object") {
    tipo = ((rt.requestType || {}).name) || rt.name || rt.value || "";
    tipo = tipo.trim();
  }
  const sla = { first_response: null, resolution: null, waiting_customer: null, all: [] };
  for (const [fid, fname] of Object.entries(F.slas || {})) {
    const p = parseSla(f[fid]);
    if (!p) continue;
    sla.all.push({ ...p, name: fname });
    const cat = classifySla(fname);
    if (cat && !sla[cat]) sla[cat] = p;
  }
  if (!sla.waiting_customer) {
    const wc = waitingCustomerMs(issue);
    if (wc != null) sla.waiting_customer = { elapsed_ms: wc, goal_ms: null, breached: false, ongoing: false, computed: true };
  }
  const coms = [];
  for (const c of ((f.comment || {}).comments) || []) {
    coms.push({
      autor: (c.author || {}).displayName || "",
      fecha: c.created || "",
      texto: adfText(c.body).trim().slice(0, 600),
    });
  }
  return {
    key: issue.key,
    resumen: f.summary || "",
    tipo,
    estado: (f.status || {}).name || "",
    prioridad: (f.priority || {}).name || "",
    asignado_a: (f.assignee || {}).displayName || "Sin asignar",
    informador: (f.reporter || {}).displayName || (f.reporter || {}).emailAddress || "",
    fecha_creacion: f.created || "",
    fecha_resolucion: f.resolutiondate || "",
    fecha_actualizacion: f.updated || "",
    descripcion: adfText(f.description).trim().slice(0, 600),
    comentarios: coms,
    sla,
  };
}

async function build(env, query, projName, debug, maxResults) {
  const base = (env.JIRA_BASE_URL || "").replace(/\/$/, "");
  const email = env.JIRA_USER_EMAIL || "";
  const token = env.JIRA_API_TOKEN || "";
  if (!base || !email || !token) return { error: "Faltan variables JIRA_BASE_URL / JIRA_USER_EMAIL / JIRA_API_TOKEN" };
  const auth = authHeader(email, token);
  const F = await detectFields(base, auth);
  if (debug === "fields") return { reqtype_field: F.reqtype, sla_fields: F.slas };
  const pn = String(projName || "").toLowerCase();
  const pk = ["", "ambos", "todos"].includes(pn) ? "" : PROJECTS[String(projName).toUpperCase()] || String(projName).toUpperCase();
  const fields = ["summary", "status", "priority", "assignee", "reporter", "created", "resolutiondate", "updated", "issuetype", "description", "comment"];
  if (F.reqtype) fields.push(F.reqtype);
  fields.push(...Object.keys(F.slas || {}));
  const jql = jqlFor(query, pk);
  const issues = await search(base, auth, jql, fields, maxResults);
  const regs = issues.map((i) => toRegistro(i, F));
  const by = {};
  for (const r of regs) {
    const k = r.tipo || "—";
    by[k] = (by[k] || 0) + 1;
  }
  return {
    consulta: query,
    proyecto: projName || "ambos",
    jql,
    metricas: { total_tickets: regs.length, por_tipo: by },
    registros: regs,
  };
}

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };
}

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: corsHeaders() });
    const url = new URL(request.url);
    const query = url.searchParams.get("query") || "todos";
    const proyecto = url.searchParams.get("proyecto") || "";
    const debug = url.searchParams.get("debug") || "";
    const maxResults = parseInt(url.searchParams.get("max_results") || "0", 10) || 0;
    try {
      const payload = await build(env, query, proyecto, debug, maxResults);
      return new Response(JSON.stringify(payload), {
        status: 200,
        headers: { "Content-Type": "application/json; charset=utf-8", ...corsHeaders() },
      });
    } catch (e) {
      const body = { error: e.httpStatus ? `HTTP ${e.httpStatus} ${e.message}` : String(e.message || e), detail: e.detail || "" };
      return new Response(JSON.stringify(body), {
        status: 500,
        headers: { "Content-Type": "application/json; charset=utf-8", ...corsHeaders() },
      });
    }
  },
};
