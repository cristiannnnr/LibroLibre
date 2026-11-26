from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class Usuario:
    id: int
    nombre: str
    email: str
    telefono: str
    activo: bool = True
    categoria: str = "regular"


@dataclass
class Libro:
    id: int
    titulo: str
    autor: str
    isbn: str
    tipo: str = "normal"
    disponible: bool = True


@dataclass
class Prestamo:
    id: int
    usuario_id: int
    libro_id: int
    fecha_prestamo: date
    fecha_devolucion_esperada: date
    estado: str = "activo"
    tipo_libro: str = "normal"
    fecha_devolucion_real: Optional[date] = None
