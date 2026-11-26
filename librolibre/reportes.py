import datetime
from typing import List, Optional

DIAS_LIMITE_PRESTAMO = 15
TARIFA_DIARIA_NORMAL = 500
TARIFA_DIARIA_REFERENCIA = 1500
TARIFA_DIARIA_RARO = 3000


def obtener_morosos(usuarios: List[dict],
                    prestamos: List[dict],
                    fecha_limite: datetime.date,
                    tipo_reporte: str = "completo",
                    incluir_inactivos: bool = False,
                    ordenar_por: str = "nombre") -> List[dict]:
    # Valida parámetros y construye reporte de morosos
    # Retorna lista de usuarios con mora activa
    if usuarios is None or len(usuarios) == 0:
        return []

    if prestamos is None:
        prestamos = []

    if tipo_reporte not in ["completo", "resumido", "critico"]:
        tipo_reporte = "completo"

    if fecha_limite is None:
        fecha_limite = datetime.date.today()

    morosos = []
    indice_usuarios = {}
    for u in usuarios:
        indice_usuarios[u.get("id")] = u

    for prestamo in prestamos:
        usuario_id = prestamo.get("usuario_id")
        fecha_dev = prestamo.get("fecha_devolucion_esperada")
        estado = prestamo.get("estado", "activo")

        if estado == "devuelto":
            continue

        usuario = indice_usuarios.get(usuario_id)

        if usuario is None:
            continue

        if not incluir_inactivos and not usuario.get("activo", True):
            continue

        if isinstance(fecha_dev, str):
            try:
                fecha_dev = datetime.date.fromisoformat(fecha_dev)
            except ValueError:
                continue

        if not isinstance(fecha_dev, datetime.date):
            continue

        dias_mora = (fecha_limite - fecha_dev).days

        if dias_mora <= 0:
            continue

        tipo_libro = prestamo.get("tipo_libro", "normal")
        multa = calcular_multa(dias_mora, tipo_libro)

        if dias_mora <= 7:
            categoria = "leve"
        elif dias_mora <= 30:
            categoria = "moderada"
        else:
            categoria = "grave"

        registro = {
            "usuario_id": usuario_id,
            "nombre": usuario.get("nombre", ""),
            "email": usuario.get("email", ""),
            "dias_mora": dias_mora,
            "multa_pesos": multa,
            "categoria_mora": categoria,
            "libro_id": prestamo.get("libro_id"),
            "tipo_libro": tipo_libro,
        }

        if tipo_reporte == "resumido":
            registro = {
                "usuario_id": registro["usuario_id"],
                "nombre": registro["nombre"],
                "dias_mora": registro["dias_mora"],
                "multa_pesos": registro["multa_pesos"],
            }
        elif tipo_reporte == "critico" and categoria != "grave":
            continue

        morosos.append(registro)

    if ordenar_por == "nombre":
        morosos.sort(key=lambda x: x.get("nombre", "").lower())
    elif ordenar_por == "mora":
        morosos.sort(key=lambda x: x.get("dias_mora", 0), reverse=True)
    elif ordenar_por == "multa":
        morosos.sort(key=lambda x: x.get("multa_pesos", 0), reverse=True)

    total_mora = sum(r.get("multa_pesos", 0) for r in morosos)
    return {
        "morosos": morosos,
        "total_registros": len(morosos),
        "total_mora_pesos": total_mora,
        "tipo_reporte": tipo_reporte,
        "fecha_corte": str(fecha_limite),
    }


def validar_usuario(usuario: dict) -> tuple:
    # Valida que el diccionario de usuario tenga campos obligatorios
    # Retorna (True, "") si válido o (False, "motivo") si no
    errores = []

    if not usuario.get("nombre") or len(usuario["nombre"].strip()) < 2:
        errores.append("nombre inválido o demasiado corto")

    if not usuario.get("email") or "@" not in usuario["email"]:
        errores.append("email inválido")

    if not usuario.get("id") or not isinstance(usuario["id"], int):
        errores.append("id debe ser un entero positivo")

    if errores:
        return False, "; ".join(errores)

    return True, ""


def calcular_multa(dias_mora: int, tipo_libro: str = "normal") -> int:
    if dias_mora <= 0:
        return 0

    if tipo_libro == "referencia":
        tarifa = TARIFA_DIARIA_REFERENCIA
    elif tipo_libro == "raro":
        tarifa = TARIFA_DIARIA_RARO
    elif tipo_libro == "normal":
        tarifa = TARIFA_DIARIA_NORMAL
    else:
        tarifa = TARIFA_DIARIA_NORMAL

    multa_base = dias_mora * tarifa

    if dias_mora > 30:
        multa_base = int(multa_base * 1.5)
    elif dias_mora > 15:
        multa_base = int(multa_base * 1.2)

    if tipo_libro == "raro" and dias_mora > 7:
        multa_base = int(multa_base * 1.1)

    tope = 500_000
    if multa_base > tope:
        multa_base = tope

    return multa_base
