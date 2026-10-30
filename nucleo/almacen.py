import json
from datetime import datetime

from config import CARPETA_REPORTES, FORMATO_ARCHIVO_REPORTE

ANCHO_TXT = 60
MAXIMO_MULETILLAS_TXT = 10


def _ruta_libre(carpeta, base):
    ruta = carpeta / f"{base}.json"
    copia = 2
    while ruta.exists():
        ruta = carpeta / f"{base}_{copia}.json"
        copia += 1
    return ruta


# El JSON alimenta el historial y el TXT queda para leerlo o imprimirlo
def guardar_reporte(reporte, carpeta=CARPETA_REPORTES):
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta_json = _ruta_libre(carpeta, f"reporte_{datetime.now().strftime(FORMATO_ARCHIVO_REPORTE)}")
    ruta_json.write_text(json.dumps(reporte, ensure_ascii=False, indent=2), encoding="utf-8")
    ruta_json.with_suffix(".txt").write_text(reporte_a_texto(reporte), encoding="utf-8")
    return ruta_json


# Los mas recientes primero; un archivo dañado se salta sin detener el historial
def listar_reportes(carpeta=CARPETA_REPORTES):
    if not carpeta.is_dir():
        return []
    reportes = []
    for ruta in sorted(carpeta.glob("reporte_*.json"), reverse=True):
        try:
            reportes.append(json.loads(ruta.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue
    return reportes


def reporte_a_texto(reporte):
    separador = "-" * ANCHO_TXT
    lineas = [
        "=" * ANCHO_TXT,
        "REPORTE EXPRESA - ANÁLISIS DE COMUNICACIÓN".center(ANCHO_TXT),
        "=" * ANCHO_TXT,
        "",
        f"Sesión     : {reporte['sesion']}",
        f"Fecha      : {reporte['fecha']}",
        f"Puntuación : {reporte['puntuacion']}/100 - {reporte['nivel']}",
        "",
        reporte["mensaje_general"],
        "",
        separador,
        "SUBPUNTUACIONES",
    ]
    for clave, valor in reporte["subpuntuaciones"].items():
        if valor is not None:
            lineas.append(f"  {clave.capitalize():<15}{valor}/100")

    lineas += ["", separador, "MULETILLAS DETECTADAS"]
    muletillas = list(reporte["muletillas"]["todas"].items())[:MAXIMO_MULETILLAS_TXT]
    if muletillas:
        lineas += [f"  '{muletilla}': {veces} {'vez' if veces == 1 else 'veces'}" for muletilla, veces in muletillas]
    else:
        lineas.append("  Ninguna")

    lineas += ["", separador, "RECOMENDACIONES"]
    for recomendacion in reporte["recomendaciones"]:
        lineas.append(f"  [{recomendacion['categoria']}] {recomendacion['texto']}")

    lineas += ["", separador, "EJERCICIOS SUGERIDOS"]
    for ejercicio in reporte["ejercicios"]:
        lineas += [
            "",
            f"  {ejercicio['nombre']} ({ejercicio['nivel']}, {ejercicio['duracion']})",
            f"  Objetivo: {ejercicio['objetivo']}",
            f"  {ejercicio['descripcion']}",
        ]
    return "\n".join(lineas) + "\n"
