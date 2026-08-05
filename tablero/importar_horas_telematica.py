#!/usr/bin/env python3
"""Normaliza un Excel (.xlsx) de un sistema externo al JSON que espera la Consola
de Telemática (Configuración → Conexión de datos → "Importar horas (.xlsx)").

Corre en tu PC, no en la nube ni en el conector de Jira: lee el .xlsx, valida
fila por fila, y escribe un .json con el mismo shape que ya usa la app
internamente para cada tarea de Telemática:

    {"cliente": "...", "tipo": "...", "fecha": "AAAA-MM-DD", "horas": 2.5,
     "estado": "Pendiente", "responsable": "...", "detalle": "..."}

Uso:
    python importar_horas_telematica.py entrada.xlsx
    python importar_horas_telematica.py entrada.xlsx -o salida.json --hoja "Horas"
    python importar_horas_telematica.py entrada.xlsx --mapeo mapeo.json
    python importar_horas_telematica.py entrada.xlsx --clientes clientes.txt

El mapeo de columnas (qué columna del Excel externo llena cada campo de
Telemática) tiene valores por defecto en español pero es 100% configurable:
pasá --mapeo con un JSON como este para adaptarlo a otro sistema sin tocar
el script:

    {"cliente": "Cuenta", "tipo": "Categoría de trabajo", "fecha": "Día",
     "horas": "Tiempo (hs)", "estado": "Estado ticket", "responsable": "Técnico",
     "detalle": "Observaciones"}

Los nombres de columna se buscan sin importar mayúsculas/tildes/espacios extra.

Validación:
  - cliente, tipo, fecha y horas son obligatorios por fila -> si falta alguno,
    o la fecha/horas no se pueden interpretar, la fila se RECHAZA (queda en el
    reporte, no en el .json de salida).
  - estado: si falta o no es "Pendiente"/"En curso"/"Resuelto", queda como
    "Pendiente" (con aviso).
  - cliente conocido: si pasás --clientes (un nombre de cliente por línea, o
    un .json con un array de nombres), un cliente que no está en esa lista
    NO rechaza la fila -- queda como advertencia. Rechazar de plano perdería
    filas reales por un cliente mal tipeado o todavía no cargado en la
    Consola; el uploader de la app ya tiene su propia vista previa antes de
    confirmar la carga, que es el mejor lugar para pescar ese error a ojo.

Requiere openpyxl (pip install openpyxl) -- es una dependencia de ESTE script,
no de la Consola (que sigue sin build step ni dependencias de servidor para
esto: ver PRODUCT.md).
"""
import argparse
import datetime
import json
import re
import sys
import unicodedata
from pathlib import Path

try:
    import openpyxl
except ImportError:
    print("Falta openpyxl. Instalalo con:  pip install openpyxl", file=sys.stderr)
    sys.exit(1)

# La consola de Windows suele quedar en un codepage que no es UTF-8 (cp1252/cp850): sin esto,
# los acentos del reporte (tildes, "ñ") salen como basura aunque el .json se escriba bien.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8")
        except Exception:
            pass

CAMPOS_OBLIGATORIOS = ["cliente", "tipo", "fecha", "horas"]
CAMPOS_OPCIONALES = ["estado", "responsable", "detalle"]
ESTADOS_VALIDOS = {"Pendiente", "En curso", "Resuelto"}

MAPEO_DEFAULT = {
    "cliente": "Cliente",
    "tipo": "Tipo",
    "fecha": "Fecha",
    "horas": "Horas",
    "estado": "Estado",
    "responsable": "Responsable",
    "detalle": "Detalle",
}


def normalizar_header(s):
    s = str(s or "").strip().lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s)


def cargar_mapeo(path):
    if not path:
        return dict(MAPEO_DEFAULT)
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    mapeo = dict(MAPEO_DEFAULT)
    mapeo.update(data)
    return mapeo


def cargar_clientes_conocidos(path):
    if not path:
        return None
    p = Path(path)
    if p.suffix.lower() == ".json":
        data = json.loads(p.read_text(encoding="utf-8"))
        return {str(c).strip() for c in data}
    return {l.strip() for l in p.read_text(encoding="utf-8").splitlines() if l.strip()}


def resolver_columnas(headers, mapeo):
    """Empareja cada campo de Telemática con el índice de su columna en el Excel
    (comparación case/tilde-insensitive). Devuelve (indices, faltantes_obligatorios)."""
    norm_headers = {normalizar_header(h): i for i, h in enumerate(headers)}
    indices = {}
    faltantes = []
    for campo, header_esperado in mapeo.items():
        idx = norm_headers.get(normalizar_header(header_esperado))
        if idx is None:
            if campo in CAMPOS_OBLIGATORIOS:
                faltantes.append((campo, header_esperado))
            continue
        indices[campo] = idx
    return indices, faltantes


def parsear_fecha(v):
    """Excel entrega datetime/date para celdas de fecha reales; si es texto,
    probamos los formatos más comunes de un export manual (dd/mm/aaaa, etc.)."""
    if v is None or v == "":
        return None
    if isinstance(v, datetime.datetime):
        return v.date().isoformat()
    if isinstance(v, datetime.date):
        return v.isoformat()
    s = str(v).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y"):
        try:
            return datetime.datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def parsear_horas(v):
    if v is None or v == "":
        return None
    if isinstance(v, (int, float)):
        return round(float(v), 2)
    s = str(v).strip().replace(",", ".")
    try:
        return round(float(s), 2)
    except ValueError:
        return None


def normalizar_estado(v):
    s = str(v or "").strip()
    for e in ESTADOS_VALIDOS:
        if s.lower() == e.lower():
            return e, None
    return "Pendiente", (f'estado "{s}" no reconocido, se usó "Pendiente"' if s else None)


def procesar(rows, indices, clientes_conocidos):
    salida = []
    rechazadas = []
    advertencias = []
    for n, row in enumerate(rows, start=2):  # fila 1 = encabezados
        def val(campo):
            idx = indices.get(campo)
            return row[idx] if idx is not None and idx < len(row) else None

        cliente = str(val("cliente") or "").strip()
        tipo = str(val("tipo") or "").strip()
        fecha = parsear_fecha(val("fecha"))
        horas = parsear_horas(val("horas"))
        responsable = str(val("responsable") or "").strip()
        detalle = str(val("detalle") or "").strip()

        motivos = []
        if not cliente:
            motivos.append("falta cliente")
        if not tipo:
            motivos.append("falta tipo")
        if val("fecha") not in (None, "") and fecha is None:
            motivos.append(f'fecha "{val("fecha")}" no se pudo interpretar')
        elif fecha is None:
            motivos.append("falta fecha")
        if val("horas") not in (None, "") and horas is None:
            motivos.append(f'horas "{val("horas")}" no es un número')
        elif horas is None:
            motivos.append("faltan horas")

        if motivos:
            rechazadas.append({"fila": n, "motivo": "; ".join(motivos)})
            continue

        estado, aviso_estado = normalizar_estado(val("estado"))
        if aviso_estado:
            advertencias.append(f"fila {n}: {aviso_estado}")
        if clientes_conocidos is not None and cliente not in clientes_conocidos:
            advertencias.append(f'fila {n}: cliente "{cliente}" no está en la lista conocida (revisar en la vista previa antes de confirmar)')

        salida.append({
            "cliente": cliente, "tipo": tipo, "fecha": fecha, "horas": horas,
            "estado": estado, "responsable": responsable, "detalle": detalle,
            "_origenFila": n,
        })
    return salida, rechazadas, advertencias


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada", help="Excel (.xlsx) del sistema externo")
    ap.add_argument("-o", "--salida", help="JSON de salida (default: mismo nombre que la entrada, .json)")
    ap.add_argument("--hoja", help="Nombre de la hoja a leer (default: la primera/activa)")
    ap.add_argument("--mapeo", help="JSON con el mapeo de columnas (ver --help)")
    ap.add_argument("--clientes", help="Lista de clientes conocidos (.txt, uno por línea, o .json con un array) para marcar advertencias, no obligatorio")
    args = ap.parse_args()

    entrada = Path(args.entrada)
    salida = Path(args.salida) if args.salida else entrada.with_suffix(".json")
    mapeo = cargar_mapeo(args.mapeo)
    clientes_conocidos = cargar_clientes_conocidos(args.clientes)

    wb = openpyxl.load_workbook(entrada, read_only=True, data_only=True)
    ws = wb[args.hoja] if args.hoja else wb.active
    filas = list(ws.iter_rows(values_only=True))
    if not filas:
        print("El archivo no tiene filas.", file=sys.stderr)
        sys.exit(1)
    headers, cuerpo = filas[0], filas[1:]

    indices, faltantes = resolver_columnas(headers, mapeo)
    if faltantes:
        print("No se encontraron estas columnas obligatorias en el Excel:", file=sys.stderr)
        for campo, header in faltantes:
            print(f'  - "{campo}" (se esperaba una columna llamada "{header}")', file=sys.stderr)
        print(f"Columnas encontradas en el archivo: {list(headers)}", file=sys.stderr)
        print("Usá --mapeo para indicar los nombres reales de las columnas.", file=sys.stderr)
        sys.exit(1)

    tareas, rechazadas, advertencias = procesar(cuerpo, indices, clientes_conocidos)

    salida.write_text(json.dumps(tareas, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"Leídas {len(cuerpo)} filas de datos.")
    print(f"Convertidas {len(tareas)} tareas válidas -> {salida}")
    if advertencias:
        print(f"\n{len(advertencias)} advertencia(s) (se incluyeron igual, revisar en la vista previa de la Consola):")
        for a in advertencias[:30]:
            print(f"  - {a}")
        if len(advertencias) > 30:
            print(f"  ... y {len(advertencias) - 30} más.")
    if rechazadas:
        print(f"\n{len(rechazadas)} fila(s) RECHAZADA(S) (no entraron al .json):")
        for r in rechazadas[:30]:
            print(f"  - fila {r['fila']}: {r['motivo']}")
        if len(rechazadas) > 30:
            print(f"  ... y {len(rechazadas) - 30} más.")


if __name__ == "__main__":
    main()
