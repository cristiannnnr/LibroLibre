# Instrucciones de Ejecución — Taller 3

## 1. Instalar dependencias Python

```bash
pip install flask pytest pytest-cov
```

---

## 2. Ejecutar pruebas unitarias con cobertura (Actividad 3)

```bash
cd LibroLibre
python -m pytest tests/ -v --cov=librolibre --cov-report=term-missing
```

Resultado esperado: 15 tests pasando, ~83% cobertura en reportes.py

---

## 3. SonarQube — Análisis Interno (Actividades 1 y 2)

### Paso A: Levantar SonarQube con Docker
```bash
docker run -d --name sonarqube -p 9000:9000 sonarqube:community
```
Esperar ~1 minuto y abrir http://localhost:9000
Usuario: admin / Contraseña: admin (cambiarla al primer login)

### Paso B: Crear proyecto en la UI
1. New Project → Manual → Key: `librolibre`
2. Generar token y copiarlo

### Paso C: Reemplazar token en sonar-project.properties
```
sonar.token=TU_TOKEN_AQUI
```

### Paso D: Ejecutar análisis (requiere sonar-scanner instalado)
```bash
# Primero generar coverage.xml con pytest
python -m pytest tests/ --cov=librolibre --cov-report=xml

# Luego correr el scanner
sonar-scanner
```

Instalar sonar-scanner: https://docs.sonarqube.org/latest/analyzing-source-code/scanners/sonarscanner/

### Qué ver en SonarQube:
- **Issues > Complexity**: muestra CC por función → confirmar CC=15 en obtener_morosos
- **Measures > Documentation**: densidad de comentarios → confirmar ~7.6%
- **Measures > Coverage**: cobertura de líneas → ~83% en reportes.py

---

## 4. Levantar el servidor Flask (para JMeter)

```bash
cd LibroLibre
python app.py
```

El servidor queda en http://localhost:5000

Endpoints disponibles:
- GET  /health
- GET  /api/reportes/morosos?tipo=completo&ordenar_por=nombre
- POST /api/usuarios/validar  (body JSON)
- GET  /api/multa?dias=10&tipo_libro=normal

---

## 5. JMeter — Análisis Externo (Actividades 4 y 5)

### Paso A: Descargar JMeter
https://jmeter.apache.org/download_jmeter.cgi → Descomprimir

### Paso B: Abrir el plan de pruebas
```bash
# Windows
bin\jmeter.bat -t jmeter\librolibre_plan.jmx
```

O con la GUI: File → Open → seleccionar librolibre_plan.jmx

### Paso C: Ejecutar
- Botón verde ▶ (Run → Start)
- Ver resultados en "Ver Árbol de Resultados" y "Reporte de Estadísticas Agregadas"

### Qué registrar (Actividad 4):
Los 5 loops del Thread Group "Actividad 4" miden el tiempo de cada petición.
Anotar los 5 tiempos y calcular el promedio.
La aserción de 2000ms marcará FAIL si el servidor supera ese umbral.

### Qué registrar (Actividad 5):
El Thread Group "Actividad 5" envía datos basura.
Revisar en el árbol cuáles responden con error controlado (400) vs error no controlado (500).

---

## Resumen de resultados esperados del taller

| Métrica | Valor | Estándar | Veredicto |
|---|---|---|---|
| CC máxima (obtener_morosos) | 15 | ≤ 10 | FALLA |
| Densidad comentarios | 7.6% | 15–25% | FALLA |
| Cobertura de código | 83% | ≥ 70% | OK |
| Tiempo medio respuesta | 5.0 s | < 2 s | FALLA |
| Tasa de error | 6% | < 1% | FALLA |
| Disponibilidad | 91.67% | ≥ 99% | FALLA |
| MTTR | 20 min | < 5 min | FALLA |

**Conclusión: No apto para producción.**
