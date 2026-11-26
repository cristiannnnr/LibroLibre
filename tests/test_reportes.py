import datetime
import pytest
from librolibre.reportes import obtener_morosos, validar_usuario, calcular_multa


USUARIOS_PRUEBA = [
    {"id": 1, "nombre": "Ana García",   "email": "ana@test.com",  "activo": True},
    {"id": 2, "nombre": "Luis Pérez",   "email": "luis@test.com", "activo": True},
    {"id": 3, "nombre": "Inactivo Uno", "email": "i@test.com",    "activo": False},
]

HOY = datetime.date.today()
HACE_10 = HOY - datetime.timedelta(days=10)
HACE_35 = HOY - datetime.timedelta(days=35)

PRESTAMOS_PRUEBA = [
    {"id": 1, "usuario_id": 1, "libro_id": 10, "tipo_libro": "normal",
     "fecha_devolucion_esperada": HACE_10.isoformat(), "estado": "activo"},
    {"id": 2, "usuario_id": 2, "libro_id": 20, "tipo_libro": "referencia",
     "fecha_devolucion_esperada": HACE_35.isoformat(), "estado": "activo"},
    {"id": 3, "usuario_id": 3, "libro_id": 30, "tipo_libro": "normal",
     "fecha_devolucion_esperada": HACE_10.isoformat(), "estado": "activo"},
]


class TestObtenerMorosos:
    def test_retorna_lista_vacia_sin_usuarios(self):
        resultado = obtener_morosos([], [], HOY)
        assert resultado == []

    def test_excluye_prestamos_devueltos(self):
        prestamo_devuelto = {**PRESTAMOS_PRUEBA[0], "estado": "devuelto"}
        res = obtener_morosos(USUARIOS_PRUEBA, [prestamo_devuelto], HOY)
        assert res["total_registros"] == 0

    def test_excluye_usuarios_inactivos_por_defecto(self):
        res = obtener_morosos(USUARIOS_PRUEBA, PRESTAMOS_PRUEBA, HOY)
        ids = [m["usuario_id"] for m in res["morosos"]]
        assert 3 not in ids

    def test_incluye_inactivos_cuando_se_pide(self):
        res = obtener_morosos(USUARIOS_PRUEBA, PRESTAMOS_PRUEBA, HOY,
                              incluir_inactivos=True)
        ids = [m["usuario_id"] for m in res["morosos"]]
        assert 3 in ids

    def test_tipo_reporte_critico_solo_mora_grave(self):
        res = obtener_morosos(USUARIOS_PRUEBA, PRESTAMOS_PRUEBA, HOY,
                              tipo_reporte="critico")
        for m in res["morosos"]:
            assert m["categoria_mora"] == "grave"


class TestValidarUsuario:
    def test_usuario_valido(self):
        ok, msg = validar_usuario({"id": 1, "nombre": "Juan", "email": "j@t.com"})
        assert ok is True
        assert msg == ""

    def test_email_invalido(self):
        ok, msg = validar_usuario({"id": 1, "nombre": "Juan", "email": "invalido"})
        assert ok is False
        assert "email" in msg

    def test_nombre_muy_corto(self):
        ok, msg = validar_usuario({"id": 1, "nombre": "A", "email": "a@b.com"})
        assert ok is False

    def test_id_no_entero(self):
        ok, msg = validar_usuario({"id": "abc", "nombre": "Juan", "email": "j@t.com"})
        assert ok is False


class TestCalcularMulta:
    def test_dias_cero_retorna_cero(self):
        assert calcular_multa(0) == 0

    def test_dias_negativos_retorna_cero(self):
        assert calcular_multa(-5) == 0

    def test_tarifa_normal(self):
        assert calcular_multa(5, "normal") == 5 * 500

    def test_tarifa_referencia_mayor_que_normal(self):
        assert calcular_multa(5, "referencia") > calcular_multa(5, "normal")

    def test_recargo_mora_larga(self):
        multa_corta = calcular_multa(10, "normal")
        multa_larga = calcular_multa(31, "normal")
        assert multa_larga > multa_corta

    def test_tope_maximo(self):
        assert calcular_multa(10000, "raro") == 500_000
