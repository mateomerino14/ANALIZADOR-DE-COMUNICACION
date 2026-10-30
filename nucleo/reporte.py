from datetime import datetime

from config import DENSIDAD_MULETILLAS_ALTA, DIVERSIDAD_MEDIA, FORMATO_FECHA_REPORTE
from datos.ejercicios import BANCO_EJERCICIOS, RECOMENDACIONES_POR_PROBLEMA

MAXIMO_EJERCICIOS = 5
TTR_VOCABULARIO_LIMITADO = 0.35
TTR_VOCABULARIO_MEJORABLE = 0.5
TTR_EJERCICIOS_MEDIO = 0.55
COHERENCIA_BAJA = 50
LEGIBILIDAD_BAJA = 40
EJERCICIO_PERMANENTE = "grabacion_semanal"

NIVELES = (
    (85, "Excelente", "Comunicación excelente. Tus habilidades están muy bien desarrolladas."),
    (70, "Muy bueno", "Muy buen desempeño. Tienes bases sólidas con pequeños aspectos a pulir."),
    (55, "Bueno", "Buen comienzo. Con práctica constante alcanzarás un nivel excelente."),
    (40, "En desarrollo", "Hay aspectos importantes por mejorar. La práctica diaria hará la diferencia."),
    (0, "Requiere práctica",
     "Con práctica constante y los ejercicios correctos, tu comunicación mejorará significativamente."),
)

SIN_TONO = {"disponible": False}


def nivel_y_mensaje(puntuacion):
    for minimo, nivel, mensaje in NIVELES:
        if puntuacion >= minimo:
            return nivel, mensaje
    return NIVELES[-1][1], NIVELES[-1][2]


def generar_reporte(analisis, tono=None, sesion="Análisis"):
    tono = tono or SIN_TONO
    nivel, mensaje = nivel_y_mensaje(analisis["puntuacion"])
    return {
        "sesion": sesion,
        "fecha": datetime.now().strftime(FORMATO_FECHA_REPORTE),
        "puntuacion": analisis["puntuacion"],
        "nivel": nivel,
        "mensaje_general": mensaje,
        "texto_analizado": analisis["texto_original"],
        **{clave: valor for clave, valor in analisis.items() if clave not in ("texto_original", "puntuacion")},
        "tono": tono,
        "recomendaciones": recomendaciones(analisis, tono),
        "ejercicios": ejercicios(analisis, tono),
    }


def _recomendacion(prioridad, categoria, texto):
    return {"prioridad": prioridad, "categoria": categoria, "texto": texto}


def _citar(palabras):
    return ", ".join(f"'{palabra}'" for palabra in palabras)


def _densidad_alta(muletillas):
    return not muletillas["criticas"] and muletillas["porcentaje"] >= DENSIDAD_MULETILLAS_ALTA


def _expresividad_baja(tono):
    return tono.get("disponible") and tono["expresividad"]["clave"] == "baja"


def recomendaciones(analisis, tono):
    lista = []
    muletillas = analisis["muletillas"]
    velocidad = analisis["estadisticas"]["velocidad"]
    ttr = analisis["diversidad"]["ttr"]

    if muletillas["criticas"]:
        lista.append(_recomendacion(
            "alta", "Muletillas",
            f"Elimina el uso frecuente de {_citar(list(muletillas['criticas'])[:3])}. "
            "Son tus muletillas más repetidas: reemplázalas por una pausa en silencio.",
        ))
    if muletillas["moderadas"]:
        lista.append(_recomendacion(
            "media", "Muletillas",
            f"Reduce {_citar(list(muletillas['moderadas'])[:2])}. "
            "Cuando sientas que van a salir, detente un segundo antes de hablar.",
        ))
    if _densidad_alta(muletillas):
        lista.append(_recomendacion(
            "alta", "Muletillas",
            f"Las muletillas ocupan el {muletillas['porcentaje']:.0f}% de tu discurso "
            f"({muletillas['impacto']}). Aunque sean distintas, juntas restan claridad: "
            f"empieza por {_citar(list(muletillas['todas'])[:3])}.",
        ))

    if velocidad in ("rapido", "muy_rapido"):
        lista.append(_recomendacion(
            "alta", "Velocidad",
            "Hablas muy rápido. Practica leer en voz alta a un ritmo deliberado: "
            "las pausas no son debilidad, dan tiempo a que te entiendan.",
        ))
    elif velocidad == "lento":
        lista.append(_recomendacion(
            "media", "Velocidad",
            "Tu ritmo es lento. Un ritmo más dinámico mantiene la atención de la audiencia.",
        ))

    if ttr < TTR_VOCABULARIO_LIMITADO:
        lista.append(_recomendacion(
            "alta", "Vocabulario",
            "Vocabulario limitado. Lee textos variados y practica el ejercicio 'Una palabra nueva por día'.",
        ))
    elif ttr < TTR_VOCABULARIO_MEJORABLE:
        lista.append(_recomendacion(
            "media", "Vocabulario",
            "Puedes enriquecer tu vocabulario buscando sinónimos para tus palabras más repetidas.",
        ))

    if analisis["subpuntuaciones"]["coherencia"] < COHERENCIA_BAJA:
        lista.append(_recomendacion(
            "media", "Coherencia",
            "Tu discurso ganaría coherencia con conectores como 'sin embargo', "
            "'por lo tanto' o 'en consecuencia' para articular las ideas.",
        ))

    if analisis["asertividad"]["nivel_asertividad"] == "Baja":
        lista.append(_recomendacion(
            "media", "Asertividad",
            "Usas muchas expresiones de duda. En lugar de 'creo que podría ser', "
            "prueba con 'considero que' o 'es necesario'.",
        ))

    if analisis["claridad"]["indice_legibilidad"] < LEGIBILIDAD_BAJA:
        lista.append(_recomendacion(
            "media", "Claridad",
            "Tu lenguaje es complejo. Usa frases más cortas (máximo 15 palabras) y palabras más sencillas.",
        ))

    if _expresividad_baja(tono):
        lista.append(_recomendacion(
            "media", "Expresividad",
            "Voz monótona. Practica el 'Teatro emocional': lee textos exagerando las emociones "
            "para ampliar tu rango tonal.",
        ))

    if not lista:
        lista.append(_recomendacion(
            "info", "General",
            "Excelente comunicación en general. Sigue practicando para mantener este nivel.",
        ))
    return lista


def _problemas_detectados(analisis, tono):
    muletillas = analisis["muletillas"]
    velocidad = analisis["estadisticas"]["velocidad"]
    ttr = analisis["diversidad"]["ttr"]
    problemas = []

    if muletillas["criticas"]:
        problemas.append("muletillas_alta")
    elif muletillas["moderadas"] or _densidad_alta(muletillas):
        problemas.append("muletillas_media")

    if velocidad in ("rapido", "muy_rapido"):
        problemas.append("velocidad_alta")
    elif velocidad == "lento":
        problemas.append("velocidad_baja")

    if ttr < DIVERSIDAD_MEDIA:
        problemas.append("vocabulario_bajo")
    elif ttr < TTR_EJERCICIOS_MEDIO:
        problemas.append("vocabulario_medio")

    if _expresividad_baja(tono):
        problemas.append("expresividad_baja")
    if analisis["subpuntuaciones"]["coherencia"] < COHERENCIA_BAJA:
        problemas.append("fluidez_baja")
    if analisis["asertividad"]["nivel_asertividad"] == "Baja":
        problemas.append("claridad_baja")
    return problemas


def ejercicios(analisis, tono):
    claves = []
    for problema in _problemas_detectados(analisis, tono):
        claves.extend(RECOMENDACIONES_POR_PROBLEMA[problema])
    claves.append(EJERCICIO_PERMANENTE)

    unicas = list(dict.fromkeys(clave for clave in claves if clave in BANCO_EJERCICIOS))
    return [BANCO_EJERCICIOS[clave] for clave in unicas[:MAXIMO_EJERCICIOS]]
