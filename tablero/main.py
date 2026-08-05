#!/usr/bin/env python3
"""
Conector Jira para la Consola de Soporte CMQ — con Request Type + SLA.
Sin dependencias externas (solo librería estándar). Compatible con run_local.py
(usa gcloud_handler(request)) y con Google Cloud Functions.

Trae, por ticket:
  - Request Type real (tipo de desagío), no "[System] Service request"
  - SLA de JSM: tiempo de 1ª respuesta, resolución y espera del cliente
  - estado, prioridad, asignado, informador, fechas, descripción y comentarios

Variables de entorno (las setea run_local.py):
  JIRA_BASE_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN

Proyectos: CMQ -> clave 'SG',  CERVEPAR -> clave 'CERVEPAR'.

Para diagnosticar los campos detectados, abrí en el navegador:
  http://localhost:8787/?debug=fields

=== CONTRATO DE DATOS (para no romper el HTML al tocar esto) ===
Cada registro devuelto en "registros" trae, además de los campos planos
(key, resumen, tipo, estado, prioridad, asignado_a, informador, fecha_creacion,
fecha_resolucion, fecha_actualizacion, descripcion, comentarios):

  "sla": {
    "first_response":   {elapsed_ms, goal_ms, breached, ongoing} | None,
    "resolution":        {elapsed_ms, goal_ms, breached, ongoing} | None,
    "waiting_customer":  {elapsed_ms, goal_ms, breached, ongoing, computed?} | None,
    "all": [ {..., "name": "<nombre real del campo SLA en Jira>"}, ... ]
  }

El HTML (Consola_Soporte_CMQ.html, función ticketTimes()) lee EXACTAMENTE estas
claves en inglés (first_response / resolution / waiting_customer / elapsed_ms /
goal_ms / breached / ongoing). Si se cambian acá, hay que actualizar ticketTimes()
en el HTML en el mismo commit — si no, los tiempos vuelven a mostrar "—" para todo.

=== IMPORTANTE — ESTE ARCHIVO YA SE REVIRTIÓ SOLO UNA VEZ (2026-07-29) ===
Si estás por pegar una copia nueva de "jira_connector_sla.py" encima de este
archivo: esa versión de origen NO tiene los 6 fixes de abajo, confirmados en
vivo contra este Jira. Sin ellos la Consola vuelve a romper (400/500, conteos
truncados, Matriz N1 sin plantillas). Si vas a reemplazar este archivo, primero
re-aplicá (o pedí que se re-apliquen) estos 6 puntos:
  1. search(): limit=0 por defecto (no 2000) — si no, vuelve a truncar la base.
  2. build()/fields: incluir "updated" — si no, se pierde fecha_actualizacion.
  3. search(): "expand": "changelog" (STRING) — con ["changelog"] (array) Jira
     devuelve 400 Bad Request en /rest/api/3/search/jql (confirmado en vivo).
  4. to_registro(): tipo.strip() — algunos Request Type traen un \t al final
     (ej. "Reportes\t") y sin esto no matchean la Matriz N1.
  5. _args()/build(): soportar ?max_results= en la URL.
  6. _post(): reintentos (2) ante timeout/error de red — "todos" hace ~35-40
     llamadas seguidas a Jira; sin reintento, una sola falla transitoria tira
     HTTP 500 para toda la consulta (pasó en vivo el 2026-07-29).
"""
import os, json, base64, datetime, time, urllib.request, urllib.parse, urllib.error

BASE  = (os.environ.get("JIRA_BASE_URL", "") or "").rstrip("/")
EMAIL = os.environ.get("JIRA_USER_EMAIL", "")
TOKEN = os.environ.get("JIRA_API_TOKEN", "")
PROJECTS = {"CMQ": "SG", "CERVEPAR": "CERVEPAR"}   # nombre visible -> clave Jira


def _auth():
    return "Basic " + base64.b64encode(f"{EMAIL}:{TOKEN}".encode()).decode()

def _get(path, params=None):
    url = BASE + path + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url, headers={"Authorization": _auth(), "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode())

def _post(path, body, retries=2):
    """POST con reintentos ante fallas transitorias de red/timeout.

    "todos" pagina ~35-40 llamadas seguidas a Jira (con changelog, que pesa);
    sin reintento, un solo timeout de red tira abajo la consulta entera con
    HTTP 500 aunque las otras 39 páginas hayan andado bien.
    """
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode(),
        headers={"Authorization": _auth(), "Accept": "application/json", "Content-Type": "application/json"},
        method="POST")
    last_err = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError:
            raise  # error real de Jira (400/401/etc.) — no tiene sentido reintentar
        except Exception as e:
            last_err = e
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
    raise last_err


_FIELDS = None
def detect_fields():
    """Detecta el id del campo Request Type y los ids de los campos SLA (una vez)."""
    global _FIELDS
    if _FIELDS is not None:
        return _FIELDS
    reqtype = None
    slas = {}
    try:
        for f in _get("/rest/api/3/field"):
            name = (f.get("name") or "").lower()
            schema = f.get("schema") or {}
            custom = (schema.get("custom") or "").lower()
            if name in ("request type", "customer request type", "tipo de solicitud",
                        "tipo de petición", "tipo de peticion", "tipo de pedido"):
                reqtype = f["id"]
            if "sla" in custom or schema.get("type") == "sla":
                slas[f["id"]] = f.get("name")
    except Exception:
        pass
    _FIELDS = {"reqtype": reqtype, "slas": slas}
    return _FIELDS


def jql_for(query, proj_key):
    proj = f"project = {proj_key}" if proj_key else "project in (SG, CERVEPAR)"
    q = (query or "todos").lower()
    m = {
        "abiertos":        f'{proj} AND statusCategory != Done ORDER BY created DESC',
        "en_progreso":     f'{proj} AND statusCategory = "In Progress" ORDER BY created DESC',
        "resueltos_hoy":   f'{proj} AND resolved >= startOfDay() ORDER BY resolved DESC',
        "resueltos_semana":f'{proj} AND resolved >= -7d ORDER BY resolved DESC',
        "resueltos_mes":   f'{proj} AND resolved >= -30d ORDER BY resolved DESC',
        "creados_hoy":     f'{proj} AND created >= startOfDay() ORDER BY created DESC',
        "creados_semana":  f'{proj} AND created >= -7d ORDER BY created DESC',
        "sin_asignar":     f'{proj} AND assignee is EMPTY AND statusCategory != Done ORDER BY created DESC',
        "alta_prioridad":  f'{proj} AND priority in (High, Highest) AND statusCategory != Done ORDER BY created DESC',
    }
    return m.get(q, f"{proj} ORDER BY created DESC")


def search(jql, fields, limit=0):
    """Búsqueda paginada con el endpoint vigente /rest/api/3/search/jql.

    limit=0 (o None) trae TODOS los issues que matchean el JQL, paginando hasta
    que Jira indique isLast=True. Un límite fijo bajo (ej. 2000) trunca la base
    en proyectos con miles de tickets y los conteos dejan de coincidir con Jira
    (ya pasó antes con un tope de 200 — ver README, Registro de cambios v8).
    """
    out, token = [], None
    while True:
        # OJO: /rest/api/3/search/jql exige "expand" como string ("changelog"),
        # no como array (["changelog"]) — con array devuelve 400 Bad Request.
        body = {"jql": jql, "fields": fields, "maxResults": 100, "expand": "changelog"}
        if token:
            body["nextPageToken"] = token
        data = _post("/rest/api/3/search/jql", body)
        out += data.get("issues", [])
        token = data.get("nextPageToken")
        if not token or data.get("isLast") or (limit and len(out) >= limit):
            break
    return out


def adf_text(node):
    """Extrae texto plano de un cuerpo ADF (formato de Jira v3)."""
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return "".join(adf_text(c) for c in node)
    if isinstance(node, dict):
        t = node.get("text", "")
        for c in node.get("content", []) or []:
            t += adf_text(c)
        if node.get("type") in ("paragraph", "heading"):
            t += "\n"
        return t
    return ""


def parse_sla(val):
    if not isinstance(val, dict):
        return None
    cyc = val.get("ongoingCycle")
    ongoing = True
    if not cyc:
        comp = val.get("completedCycles") or []
        cyc = comp[-1] if comp else None
        ongoing = False
    if not cyc:
        return None
    return {
        "elapsed_ms": (cyc.get("elapsedTime") or {}).get("millis"),
        "goal_ms":    (cyc.get("goalDuration") or {}).get("millis"),
        "breached":   bool(cyc.get("breached", False)),
        "ongoing":    ongoing,
    }


def classify_sla(name):
    n = (name or "").lower()
    if "first response" in n or "primera respuesta" in n or "respuesta inicial" in n:
        return "first_response"
    if "close after resolution" in n or "time to close" in n:
        return "close"          # NO es resolución
    if "review" in n:
        return None
    if "resolution" in n or "resoluc" in n:
        return "resolution"
    if "waiting for customer" in n or "waiting on customer" in n or ("espera" in n and "cliente" in n):
        return "waiting_customer"
    return None


def _iso_ts(x):
    if not x:
        return None
    x = x.strip()
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.datetime.strptime(x, fmt).timestamp()
        except Exception:
            pass
    try:
        return datetime.datetime.fromisoformat(x.replace("Z", "+00:00")).timestamp()
    except Exception:
        return None

def _is_waiting_status(s):
    s = (s or "").lower()
    return ("waiting for customer" in s) or ("waiting on customer" in s) or \
           ("espera" in s and "cliente" in s) or ("esperando" in s and "cliente" in s)

def waiting_customer_ms(issue):
    """Tiempo (wall-clock) que el ticket pasó en estado 'Waiting for customer', del historial."""
    ch = (issue.get("changelog") or {})
    hist = ch.get("histories") or []
    events = []
    for h in hist:
        t = _iso_ts(h.get("created"))
        for it in (h.get("items") or []):
            if it.get("field") == "status":
                events.append((t, it.get("fromString"), it.get("toString")))
    events = [e for e in events if e[0] is not None]
    events.sort(key=lambda e: e[0])
    total = 0.0
    prev_t = _iso_ts((issue.get("fields") or {}).get("created"))
    cur = events[0][1] if events else ((issue.get("fields") or {}).get("status") or {}).get("name")
    for (t, frm, to) in events:
        if prev_t is not None and _is_waiting_status(cur):
            total += max(0, t - prev_t)
        cur = to
        prev_t = t
    now = datetime.datetime.now(datetime.timezone.utc).timestamp()
    if prev_t is not None and _is_waiting_status(cur):
        total += max(0, now - prev_t)
    return int(total * 1000) if total > 0 else None


def to_registro(issue, F):
    f = issue.get("fields", {}) or {}
    # Request Type
    tipo = ""
    rt = f.get(F["reqtype"]) if F["reqtype"] else None
    if isinstance(rt, dict):
        tipo = (rt.get("requestType") or {}).get("name") or rt.get("name") or rt.get("value") or ""
        tipo = tipo.strip()  # Jira devuelve algunos Request Type con un tab al final
                              # (ej. "Reportes\t"); sin esto no matchean la Matriz N1.
    # SLA
    sla = {"first_response": None, "resolution": None, "waiting_customer": None, "all": []}
    for fid, fname in (F["slas"] or {}).items():
        p = parse_sla(f.get(fid))
        if not p:
            continue
        item = dict(p); item["name"] = fname
        sla["all"].append(item)
        cat = classify_sla(fname)
        if cat and not sla.get(cat):
            sla[cat] = p
    # Espera del cliente: no hay SLA en este Jira -> se calcula del tiempo en estado "Waiting for customer"
    if not sla["waiting_customer"]:
        wc = waiting_customer_ms(issue)
        if wc is not None:
            sla["waiting_customer"] = {"elapsed_ms": wc, "goal_ms": None, "breached": False,
                                       "ongoing": False, "computed": True}
    # comentarios
    coms = []
    for c in ((f.get("comment") or {}).get("comments") or []):
        coms.append({
            "autor": (c.get("author") or {}).get("displayName", ""),
            "fecha": c.get("created", ""),
            "texto": adf_text(c.get("body")).strip()[:600],
        })
    return {
        "key": issue.get("key"),
        "resumen": f.get("summary", ""),
        "tipo": tipo,
        "estado": (f.get("status") or {}).get("name", ""),
        "prioridad": (f.get("priority") or {}).get("name", ""),
        "asignado_a": (f.get("assignee") or {}).get("displayName", "") or "Sin asignar",
        "informador": (f.get("reporter") or {}).get("displayName", "") or (f.get("reporter") or {}).get("emailAddress", ""),
        "fecha_creacion": f.get("created", ""),
        "fecha_resolucion": f.get("resolutiondate", ""),
        "fecha_actualizacion": f.get("updated", ""),
        "descripcion": adf_text(f.get("description")).strip()[:600],
        "comentarios": coms,
        "sla": sla,
    }


def build(query, proj_name, debug="", max_results=0):
    if not (BASE and EMAIL and TOKEN):
        return {"error": "Faltan variables JIRA_BASE_URL / JIRA_USER_EMAIL / JIRA_API_TOKEN"}
    F = detect_fields()
    if debug == "fields":
        return {"reqtype_field": F["reqtype"], "sla_fields": F["slas"]}
    pk = "" if str(proj_name or "").lower() in ("", "ambos", "todos") else PROJECTS.get(str(proj_name).upper(), "")
    fields = ["summary", "status", "priority", "assignee", "reporter", "created",
              "resolutiondate", "updated", "issuetype", "description", "comment"]
    if F["reqtype"]:
        fields.append(F["reqtype"])
    fields += list((F["slas"] or {}).keys())
    jql = jql_for(query, pk)
    issues = search(jql, fields, limit=max_results)
    regs = [to_registro(i, F) for i in issues]
    by = {}
    for r in regs:
        k = r["tipo"] or "—"
        by[k] = by.get(k, 0) + 1
    return {
        "consulta": query, "proyecto": proj_name or "ambos", "jql": jql,
        "metricas": {"total_tickets": len(regs), "por_tipo": by},
        "registros": regs,
    }


def _args(request):
    a = getattr(request, "args", None)
    g = (lambda k, d=None: a.get(k, d)) if a is not None else (lambda k, d=None: d)
    try:
        max_results = int(g("max_results", 0) or 0)
    except (TypeError, ValueError):
        max_results = 0
    return g("query", "todos"), g("proyecto", ""), g("debug", ""), max_results


def gcloud_handler(request):
    try:
        query, proj, debug, max_results = _args(request)
        payload = build(query, proj, debug, max_results)
        return (json.dumps(payload, ensure_ascii=False), 200, {"Content-Type": "application/json; charset=utf-8"})
    except urllib.error.HTTPError as e:
        try:
            detail = e.read().decode()[:400]
        except Exception:
            detail = ""
        return (json.dumps({"error": f"HTTP {e.code} {e.reason}", "detail": detail}, ensure_ascii=False),
                500, {"Content-Type": "application/json; charset=utf-8"})
    except Exception as e:
        return (json.dumps({"error": str(e)}, ensure_ascii=False),
                500, {"Content-Type": "application/json; charset=utf-8"})


# AWS Lambda / genérico
def lambda_handler(event, context=None):
    p = (event or {}).get("queryStringParameters") or {}
    try:
        max_results = int(p.get("max_results", 0) or 0)
    except (TypeError, ValueError):
        max_results = 0
    body = build(p.get("query", "todos"), p.get("proyecto", ""), p.get("debug", ""), max_results)
    return {"statusCode": 200, "headers": {"Content-Type": "application/json"},
            "body": json.dumps(body, ensure_ascii=False)}


if __name__ == "__main__":
    # prueba rápida por consola:  python main.py todos CMQ
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else "todos"
    pr = sys.argv[2] if len(sys.argv) > 2 else ""
    print(json.dumps(build(q, pr), ensure_ascii=False, indent=1)[:2000])
