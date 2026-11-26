import datetime
from flask import Flask, request, jsonify
from librolibre.reportes import obtener_morosos, validar_usuario, calcular_multa

app = Flask(__name__)

# Datos de ejemplo en memoria (simula la BD de LibroLibre)
USUARIOS = [
    {"id": 1, "nombre": "Ana García",    "email": "ana@example.com",    "activo": True},
    {"id": 2, "nombre": "Luis Pérez",    "email": "luis@example.com",   "activo": True},
    {"id": 3, "nombre": "María Torres",  "email": "maria@example.com",  "activo": True},
    {"id": 4, "nombre": "Carlos Ruiz",   "email": "carlos@example.com", "activo": False},
    {"id": 5, "nombre": "Sandra Mora",   "email": "sandra@example.com", "activo": True},
]

PRESTAMOS = [
    {"id": 1, "usuario_id": 1, "libro_id": 101, "tipo_libro": "normal",
     "fecha_devolucion_esperada": "2026-10-01", "estado": "activo"},
    {"id": 2, "usuario_id": 2, "libro_id": 102, "tipo_libro": "referencia",
     "fecha_devolucion_esperada": "2026-09-15", "estado": "activo"},
    {"id": 3, "usuario_id": 3, "libro_id": 103, "tipo_libro": "raro",
     "fecha_devolucion_esperada": "2026-08-20", "estado": "activo"},
    {"id": 4, "usuario_id": 4, "libro_id": 104, "tipo_libro": "normal",
     "fecha_devolucion_esperada": "2026-10-10", "estado": "activo"},
    {"id": 5, "usuario_id": 5, "libro_id": 105, "tipo_libro": "normal",
     "fecha_devolucion_esperada": "2026-11-01", "estado": "activo"},
    {"id": 6, "usuario_id": 1, "libro_id": 106, "tipo_libro": "normal",
     "fecha_devolucion_esperada": "2026-11-20", "estado": "devuelto"},
]


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "version": "1.0.0"}), 200


@app.route("/api/reportes/morosos", methods=["GET"])
def reporte_morosos():
    tipo = request.args.get("tipo", "completo")
    ordenar = request.args.get("ordenar_por", "nombre")
    incluir_inactivos = request.args.get("incluir_inactivos", "false").lower() == "true"
    fecha_corte = datetime.date.today()

    resultado = obtener_morosos(
        usuarios=USUARIOS,
        prestamos=PRESTAMOS,
        fecha_limite=fecha_corte,
        tipo_reporte=tipo,
        incluir_inactivos=incluir_inactivos,
        ordenar_por=ordenar,
    )
    return jsonify(resultado), 200


@app.route("/api/usuarios/validar", methods=["POST"])
def validar():
    datos = request.get_json(silent=True)
    if datos is None:
        return jsonify({"error": "Body JSON requerido"}), 400
    valido, motivo = validar_usuario(datos)
    return jsonify({"valido": valido, "motivo": motivo}), 200


@app.route("/api/multa", methods=["GET"])
def multa():
    try:
        dias = int(request.args.get("dias", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "El parámetro 'dias' debe ser un número entero"}), 400
    tipo = request.args.get("tipo_libro", "normal")
    monto = calcular_multa(dias, tipo)
    return jsonify({"dias_mora": dias, "tipo_libro": tipo, "multa_pesos": monto}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
