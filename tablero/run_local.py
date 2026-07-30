#!/usr/bin/env python3
"""
Servidor LOCAL para la Consola de Soporte CMQ  (Flask).
- Expone tu conector de Jira (main.py) en http://localhost:8787 con CORS.
- Guarda tus ajustes de la Consola (reasignaciones + clientes) en 'kb_state.json'.

REQUISITO (una sola vez):   pip install flask

USO
  1) Poné este archivo junto a 'main.py' (tu conector renombrado).
  2) Pegá tu TOKEN NUEVO en CONFIG (abajo).
  3) En la terminal:   python run_local.py
  4) En la Consola -> Cargar Jira -> Conexión API, pegá:  http://localhost:8787
Dejá esta ventana abierta mientras usás la Consola. Ctrl+C para frenar.
"""
import os, sys, json, importlib.util

CONFIG = {
    "JIRA_BASE_URL":   "https://geotab-cesetti.atlassian.net",
    "JIRA_USER_EMAIL": "df@cesetti.com.ar",
    "JIRA_API_TOKEN":  "PEGA_TU_TOKEN_AQUI",
}

# Token real: se lee de 'token_local.json' (mismo directorio), un archivo que
# NUNCA se sube a git (ver .gitignore) — así este archivo (run_local.py) se
# puede compartir/subir a GitHub sin exponer el token. Si no existe, se usa
# el placeholder de CONFIG de arriba.
_SECRETS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "token_local.json")
if os.path.exists(_SECRETS_FILE):
    try:
        CONFIG.update(json.load(open(_SECRETS_FILE, encoding="utf-8")))
    except Exception as e:
        print("  Aviso: no pude leer token_local.json:", e)

for k, v in CONFIG.items():
    if not os.environ.get(k):
        os.environ[k] = v

PORT = 8787
HERE = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(HERE, "kb_state.json")

try:
    from flask import Flask, request, make_response
except ImportError:
    print("Falta Flask. Instalalo con:   pip install flask")
    sys.exit(1)

main_path = os.path.join(HERE, "main.py")
if not os.path.exists(main_path):
    print("No encuentro 'main.py' en esta carpeta.")
    sys.exit(1)
spec = importlib.util.spec_from_file_location("main", main_path)
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)

HANDLER = None
for name in ("gcloud_handler", "handler", "main", "app"):
    if hasattr(main, name) and callable(getattr(main, name)):
        HANDLER = getattr(main, name); HANDLER_NAME = name; break
if HANDLER is None:
    print("No encontre 'gcloud_handler' en main.py.")
    sys.exit(1)

server = Flask(__name__)

def add_cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp

# ---- Persistencia de ajustes de la Consola (reasignaciones + clientes) ----
@server.route("/kb/state", methods=["GET", "OPTIONS"])
def kb_state():
    if request.method == "OPTIONS":
        return add_cors(make_response("", 204))
    try:
        data = open(STATE_FILE, encoding="utf-8").read() if os.path.exists(STATE_FILE) else "{}"
    except Exception:
        data = "{}"
    r = make_response(data, 200)
    r.headers["Content-Type"] = "application/json; charset=utf-8"
    return add_cors(r)

@server.route("/kb/save", methods=["POST", "OPTIONS"])
def kb_save():
    if request.method == "OPTIONS":
        return add_cors(make_response("", 204))
    try:
        body = request.get_data(as_text=True) or "{}"
        json.loads(body)  # validar que sea JSON
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            f.write(body)
        print("  guardado kb_state.json")
        r = make_response('{"ok":true}', 200)
    except Exception as e:
        print("  ERROR guardando:", e)
        r = make_response(json.dumps({"ok": False, "error": str(e)}), 500)
    r.headers["Content-Type"] = "application/json; charset=utf-8"
    return add_cors(r)

# ---- Proxy al conector de Jira (todo lo demás) ----
@server.route("/", defaults={"path": ""}, methods=["GET", "OPTIONS"])
@server.route("/<path:path>", methods=["GET", "OPTIONS"])
def proxy(path):
    if request.method == "OPTIONS":
        return add_cors(make_response("", 204))
    print("  ->", request.args.get("query", "todos"), "|", request.args.get("proyecto", "ambos"))
    try:
        resp = make_response(HANDLER(request))
    except Exception as e:
        print("  ERROR:", e)
        resp = make_response(json.dumps({"error": str(e)}, ensure_ascii=False), 500)
        resp.headers["Content-Type"] = "application/json; charset=utf-8"
    return add_cors(resp)

if __name__ == "__main__":
    if "PEGA_TU_TOKEN" in os.environ.get("JIRA_API_TOKEN", ""):
        print("Falta el token: edita CONFIG con tu token NUEVO.\n")
    print("Escuchando en http://localhost:%d  (Ctrl+C para frenar)" % PORT)
    server.run(host="127.0.0.1", port=PORT, threaded=True)
