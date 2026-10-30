import json
from datetime import datetime

from config import CARPETA_REPORTES, FORMATO_ARCHIVO_REPORTE

ANCHO_TXT = 60
ANCHO_DATO_TXT = 32
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


def _separador(titulo):
    return ["", "-" * ANCHO_TXT, titulo]


def _datos(pares):
    return [f"  {dato:<{ANCHO_DATO_TXT}}{valor}" for dato, valor in pares]


def _veces(veces):
    if veces == 1:
        return "1 vez"
    return f"{veces} veces"


def _cabecera(reporte):
    estadisticas = reporte["estadisticas"]
    lineas = [
        "=" * ANCHO_TXT,
        "REPORTE EXPRESA - ANÁLISIS DE COMUNICACIÓN".center(ANCHO_TXT),
        "=" * ANCHO_TXT,
        "",
        f"Sesión     : {reporte['sesion']}",
        f"Fecha      : {reporte['fecha']}",
        f"Palabras   : {estadisticas['total_palabras']}",
    ]
    if estadisticas["velocidad"] is not None:
        lineas += [
            f"Duración   : {estadisticas['duracion_seg']} s",
            f"Velocidad  : {estadisticas['palabras_por_min']} ppm - {estadisticas['categoria_velocidad']}",
        ]
    lineas += [
        f"Puntuación : {reporte['puntuacion']}/100 - {reporte['nivel']}",
        "",
        reporte["mensaje_general"],
    ]
    lineas += _separador("SUBPUNTUACIONES")
    for clave, valor in reporte["subpuntuaciones"].items():
        if valor is not None:
            lineas.append(f"  {clave.capitalize():<15}{valor}/100")
    return lineas


def _muletillas(reporte):
    muletillas = reporte["muletillas"]
    lineas = _separador("MULETILLAS DETECTADAS")
    if not muletillas["todas"]:
        return lineas + ["  Ninguna"]
    lineas += _datos([
        ("Total", f"{muletillas['total']} ({muletillas['porcentaje']}% del discurso)"),
        ("Frecuencia", muletillas["impacto"]),
        ("Categoría más cercana", f"{muletillas['patron_cercano']} (similitud {muletillas['similitud_maxima']})"),
    ])
    for muletilla, veces in list(muletillas["todas"].items())[:MAXIMO_MULETILLAS_TXT]:
        lineas.append(f"  '{muletilla}': {_veces(veces)}")
    return lineas


def _lenguaje(reporte):
    diversidad = reporte["diversidad"]
    repeticiones = reporte["repeticiones"]
    claridad = reporte["claridad"]
    complejidad = reporte["complejidad"]
    lineas = _separador("VOCABULARIO")
    lineas += _datos([
        ("Diversidad (TTR / MATTR)", f"{diversidad['ttr']} / {diversidad['mattr']} - {diversidad['nivel']}"),
        ("Palabras distintas", f"{diversidad['unicos']} de {diversidad['total']}"),
        ("Índice de redundancia", repeticiones["indice_redundancia"]),
        ("Usadas en exceso", ", ".join(repeticiones["en_exceso"]) or "Ninguna"),
    ])
    lineas += _separador("CLARIDAD Y COMPLEJIDAD")
    lineas += _datos([
        ("Legibilidad", f"{claridad['indice_legibilidad']} - {claridad['nivel_legibilidad']}"),
        ("Palabras por oración", f"{claridad['palabras_por_oracion']} - {claridad['nivel_oraciones']}"),
        ("Dobles negaciones", claridad["dobles_negaciones"]),
        ("Complejidad", complejidad["nivel_complejidad"]),
        ("Oraciones compuestas", f"{complejidad['ratio_compuestas']}%"),
    ])
    return lineas


def _actitud(reporte):
    coherencia = reporte["coherencia"]
    asertividad = reporte["asertividad"]
    sentimiento = reporte["sentimiento"]
    lineas = _separador("COHERENCIA, ASERTIVIDAD Y TONO")
    lineas += _datos([
        ("Coherencia", f"{coherencia['nivel_coherencia']} - {coherencia['detalle_coherencia']}"),
        ("Conectores usados", ", ".join(coherencia["conectores_usados"]) or "Ninguno"),
        ("Asertividad", asertividad["nivel_asertividad"]),
        ("Expresiones asertivas / duda",
         f"{asertividad['expresiones_asertivas']} / {asertividad['expresiones_duda']}"),
        ("Tono emocional", f"{sentimiento['tono_general']} (polaridad {sentimiento['polaridad']})"),
    ])
    return lineas


def _voz(reporte):
    tono = reporte["tono"]
    pausas = reporte["pausas"]
    if not tono.get("disponible"):
        return []
    lineas = _separador("VOZ Y PAUSAS")
    lineas += _datos([
        ("Tipo de voz", tono["pitch"]["tipo"]),
        ("Expresividad", tono["expresividad"]["nivel"]),
        ("Volumen", tono["energia"]["descripcion"]),
        ("Ritmo", tono["ritmo"]["tipo"]),
    ])
    if pausas:
        lineas += _datos([
            ("Pausas", f"{pausas['total']} ({pausas['largas']} largas, promedio {pausas['promedio']} s)"),
            ("Evaluación", pausas["evaluacion"]),
        ])
    return lineas


def _plan(reporte):
    lineas = _separador("RECOMENDACIONES")
    for recomendacion in reporte["recomendaciones"]:
        lineas.append(f"  [{recomendacion['categoria']}] {recomendacion['texto']}")

    lineas += _separador("EJERCICIOS SUGERIDOS")
    for ejercicio in reporte["ejercicios"]:
        lineas += [
            "",
            f"  {ejercicio['nombre']} ({ejercicio['nivel']}, {ejercicio['duracion']})",
            f"  Objetivo: {ejercicio['objetivo']}",
            f"  {ejercicio['descripcion']}",
        ]
    return lineas


def reporte_a_texto(reporte):
    secciones = (_cabecera, _muletillas, _lenguaje, _actitud, _voz, _plan)
    lineas = [linea for seccion in secciones for linea in seccion(reporte)]
    return "\n".join(lineas) + "\n"
