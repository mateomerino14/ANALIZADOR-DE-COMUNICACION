import re
from collections import Counter

from config import (
    DIVERSIDAD_ALTA,
    DIVERSIDAD_MEDIA,
    PAUSA_LARGA_SEG,
    PAUSA_MINIMA_SEG,
    PPM_LENTO,
    PPM_NORMAL,
    PPM_RAPIDO,
    VENTANA_MATTR,
    VENTANA_REPETICION,
)
from datos.lexico import (
    CONECTORES_LOGICOS,
    EXPRESIONES_ASERTIVAS,
    EXPRESIONES_DUDA,
    PALABRAS_NEGATIVAS,
    PALABRAS_POSITIVAS,
    STOPWORDS,
    SUBORDINANTES,
)
from nucleo.muletillas import analizar_muletillas
from nucleo.puntuacion import puntuacion_global, subpuntuaciones
from nucleo.texto import contar_frases, contar_silabas, normalizar, oraciones, tokenizar

MINIMO_PALABRAS = 3
LARGO_PALABRA_CONTENIDO = 4
LARGO_PALABRA_LARGA = 11
CARACTERES_CONTEXTO_PAUSA = 40
MAXIMO_REPETICIONES_CERCANAS = 10
MAXIMO_PAUSAS_DETALLE = 8
MAXIMO_EJEMPLOS = 5


class TextoInsuficiente(ValueError):
    pass


def analizar(texto, duracion_segundos=None, segmentos=None):
    texto_normalizado = normalizar(texto or "")
    palabras = tokenizar(texto_normalizado)
    if len(palabras) < MINIMO_PALABRAS:
        raise TextoInsuficiente(f"Se necesitan al menos {MINIMO_PALABRAS} palabras para el análisis.")

    resultados = {
        "texto_original": texto,
        "estadisticas": analizar_velocidad(palabras, duracion_segundos),
        "muletillas": analizar_muletillas(texto_normalizado, len(palabras)),
        "repeticiones": analizar_repeticiones(palabras),
        "diversidad": analizar_diversidad(palabras),
        "pausas": analizar_pausas(segmentos or []),
        "claridad": analizar_claridad(texto_normalizado, palabras),
        "coherencia": analizar_coherencia(texto_normalizado, palabras),
        "sentimiento": analizar_sentimiento(palabras),
        "asertividad": analizar_asertividad(texto_normalizado, palabras),
        "complejidad": analizar_complejidad(texto_normalizado, palabras),
    }
    resultados["subpuntuaciones"] = subpuntuaciones(resultados)
    resultados["puntuacion"] = puntuacion_global(resultados["subpuntuaciones"])
    return resultados


def clasificar_velocidad(ppm):
    if ppm < PPM_LENTO:
        return "lento", "Lento"
    if ppm <= PPM_NORMAL:
        return "normal", "Normal"
    if ppm <= PPM_RAPIDO:
        return "rapido", "Rápido"
    return "muy_rapido", "Muy rápido"


# En un texto escrito no hay duracion real, por eso la velocidad queda sin medir
def analizar_velocidad(palabras, duracion_segundos):
    estadisticas = {
        "total_palabras": len(palabras),
        "rango_ideal": f"{PPM_LENTO}-{PPM_NORMAL} ppm",
        "velocidad": None,
        "categoria_velocidad": "No aplica",
    }
    if not duracion_segundos:
        return estadisticas

    ppm = len(palabras) / (duracion_segundos / 60)
    clave, etiqueta = clasificar_velocidad(ppm)
    estadisticas.update({
        "duracion_seg": round(duracion_segundos, 1),
        "palabras_por_min": round(ppm, 1),
        "velocidad": clave,
        "categoria_velocidad": etiqueta,
    })
    return estadisticas


def es_palabra_contenido(palabra):
    return palabra not in STOPWORDS and len(palabra) >= LARGO_PALABRA_CONTENIDO


def analizar_repeticiones(palabras):
    contenido = [palabra for palabra in palabras if es_palabra_contenido(palabra)]
    conteo = Counter(contenido)
    umbral = max(3, len(contenido) * 0.05)
    en_exceso = {palabra: veces for palabra, veces in conteo.items() if veces >= umbral}

    cercanas = []
    for posicion, palabra in enumerate(palabras):
        if not es_palabra_contenido(palabra):
            continue
        siguientes = palabras[posicion + 1:posicion + VENTANA_REPETICION + 1]
        if palabra in siguientes:
            cercanas.append({
                "palabra": palabra,
                "posicion": posicion,
                "distancia_palabras": siguientes.index(palabra) + 1,
            })

    repetidas = sum(veces - 1 for veces in en_exceso.values())
    return {
        "en_exceso": en_exceso,
        "cercanas": cercanas[:MAXIMO_REPETICIONES_CERCANAS],
        "indice_redundancia": round(repetidas / max(len(contenido), 1), 3),
        "total_contenido": len(contenido),
    }


# TTR promediado en ventanas moviles, no se castiga a los textos largos
def calcular_mattr(palabras, ventana=VENTANA_MATTR):
    if len(palabras) < ventana:
        return len(set(palabras)) / max(len(palabras), 1)
    ventanas = len(palabras) - ventana + 1
    return sum(len(set(palabras[i:i + ventana])) / ventana for i in range(ventanas)) / ventanas


def analizar_diversidad(palabras):
    contenido = [palabra for palabra in palabras if palabra not in STOPWORDS]
    if not contenido:
        return {"ttr": 0, "mattr": 0, "nivel": "Sin datos", "total": 0, "unicos": 0}

    conteo = Counter(contenido)
    ttr = len(conteo) / len(contenido)
    hapax = sum(1 for veces in conteo.values() if veces == 1)

    if ttr >= DIVERSIDAD_ALTA:
        nivel = "Alta"
    elif ttr >= DIVERSIDAD_MEDIA:
        nivel = "Media"
    else:
        nivel = "Baja"

    return {
        "ttr": round(ttr, 3),
        "mattr": round(calcular_mattr(contenido), 3),
        "ratio_hapax": round(hapax / len(contenido), 3),
        "nivel": nivel,
        "total": len(contenido),
        "unicos": len(conteo),
        "palabras_clave": [palabra for palabra, veces in conteo.most_common(8) if veces >= 2],
    }


# Necesita las marcas de tiempo de Whisper, en texto escrito no hay pausas
def analizar_pausas(segmentos):
    if len(segmentos) < 2:
        return {}

    pausas = []
    for anterior, actual in zip(segmentos, segmentos[1:], strict=False):
        silencio = actual["inicio"] - anterior["fin"]
        if silencio >= PAUSA_MINIMA_SEG:
            pausas.append({
                "duracion": round(silencio, 2),
                "larga": silencio >= PAUSA_LARGA_SEG,
                "contexto": actual["texto"][:CARACTERES_CONTEXTO_PAUSA],
            })

    largas = sum(1 for pausa in pausas if pausa["larga"])
    if largas == 0:
        evaluacion = "Pausas bien distribuidas"
    elif largas <= 2:
        evaluacion = "Algunas pausas largas, pueden ser estratégicas"
    else:
        evaluacion = "Muchas pausas largas, conviene trabajar la fluidez"

    return {
        "total": len(pausas),
        "largas": largas,
        "normales": len(pausas) - largas,
        "promedio": round(sum(p["duracion"] for p in pausas) / max(len(pausas), 1), 2),
        "detalle": pausas[:MAXIMO_PAUSAS_DETALLE],
        "evaluacion": evaluacion,
    }


def nivel_oraciones(palabras_por_oracion):
    if palabras_por_oracion <= 12:
        return "Muy concisas"
    if palabras_por_oracion <= 18:
        return "Concisas"
    if palabras_por_oracion <= 25:
        return "Moderadas"
    return "Largas"


def nivel_legibilidad(indice):
    if indice >= 75:
        return "Muy fácil de entender"
    if indice >= 60:
        return "Fácil"
    if indice >= 45:
        return "Moderado"
    if indice >= 30:
        return "Difícil"
    return "Muy difícil"


# Indice de Fernandez Huerta, la adaptacion de Flesch al español
def indice_fernandez_huerta(silabas_por_palabra, palabras_por_oracion):
    indice = 206.84 - 60 * silabas_por_palabra - 1.02 * palabras_por_oracion
    return max(0.0, min(100.0, indice))


def analizar_claridad(texto, palabras):
    lista_oraciones = oraciones(texto)
    palabras_por_oracion = len(palabras) / max(len(lista_oraciones), 1)
    silabas_por_palabra = sum(contar_silabas(palabra) for palabra in palabras) / len(palabras)
    indice = indice_fernandez_huerta(silabas_por_palabra, palabras_por_oracion)

    return {
        "long_prom_palabras": round(sum(len(p) for p in palabras) / len(palabras), 1),
        "palabras_por_oracion": round(palabras_por_oracion, 1),
        "nivel_oraciones": nivel_oraciones(palabras_por_oracion),
        "total_oraciones": len(lista_oraciones),
        "silabas_prom_palabra": round(silabas_por_palabra, 2),
        "indice_legibilidad": round(indice, 1),
        "nivel_legibilidad": nivel_legibilidad(indice),
        "dobles_negaciones": len(re.findall(r"\bno\b[^.!?]{1,30}\bno\b", texto)),
    }


def analizar_coherencia(texto, palabras):
    conectores = contar_frases(CONECTORES_LOGICOS, texto)
    total_conectores = sum(conectores.values())
    ratio_conectores = total_conectores / len(palabras) * 100

    if ratio_conectores >= 3:
        nivel = "Alta"
        detalle = "Discurso bien estructurado"
    elif ratio_conectores >= 1:
        nivel = "Media"
        detalle = "Estructura aceptable"
    else:
        nivel = "Baja"
        detalle = "Añadir conectores mejoraría la coherencia"

    # Si las dos mitades comparten vocabulario, el discurso no se fue por las ramas
    mitad = len(palabras) // 2
    primera = {palabra for palabra in palabras[:mitad] if palabra not in STOPWORDS}
    segunda = {palabra for palabra in palabras[mitad:] if palabra not in STOPWORDS}
    solapamiento = len(primera & segunda) / max(len(primera | segunda), 1)

    if solapamiento > 0.5:
        progresion = "Temáticamente consistente"
    elif solapamiento > 0.3:
        progresion = "Progresión temática moderada"
    else:
        progresion = "Temas dispersos, conviene revisar el hilo conductor"

    return {
        "conectores_usados": conectores,
        "total_conectores": total_conectores,
        "ratio_conectores": round(ratio_conectores, 2),
        "nivel_coherencia": nivel,
        "detalle_coherencia": detalle,
        "progresion_tematica": progresion,
        "solapamiento_temas": round(solapamiento, 3),
    }


def analizar_sentimiento(palabras):
    positivas = [palabra for palabra in palabras if palabra in PALABRAS_POSITIVAS]
    negativas = [palabra for palabra in palabras if palabra in PALABRAS_NEGATIVAS]
    polaridad = (len(positivas) - len(negativas)) / max(len(positivas) + len(negativas), 1)

    if polaridad > 0.3:
        tono = "Positivo"
    elif polaridad > -0.3:
        tono = "Neutro"
    else:
        tono = "Negativo"

    return {
        "tono_general": tono,
        "polaridad": round(polaridad, 3),
        "palabras_pos": len(positivas),
        "palabras_neg": len(negativas),
        "ratio_positivo": round(len(positivas) / len(palabras) * 100, 1),
        "ratio_negativo": round(len(negativas) / len(palabras) * 100, 1),
        "ejemplos_pos": sorted(set(positivas))[:MAXIMO_EJEMPLOS],
        "ejemplos_neg": sorted(set(negativas))[:MAXIMO_EJEMPLOS],
    }


def analizar_asertividad(texto, palabras):
    asertivas = contar_frases(EXPRESIONES_ASERTIVAS, texto)
    dudas = contar_frases(EXPRESIONES_DUDA, texto)
    total_asertivas = sum(asertivas.values())
    total_dudas = sum(dudas.values())
    ratio = (total_asertivas - total_dudas * 0.5) / len(palabras)

    if ratio > 0.05 and total_dudas <= 2:
        nivel = "Alta"
    elif ratio > 0 or total_dudas <= 4:
        nivel = "Media"
    else:
        nivel = "Baja"

    return {
        "nivel_asertividad": nivel,
        "expresiones_asertivas": total_asertivas,
        "expresiones_duda": total_dudas,
        "ratio_asertividad": round(ratio, 3),
        "ejemplos_asertivos": list(asertivas)[:MAXIMO_EJEMPLOS],
        "ejemplos_duda": list(dudas)[:MAXIMO_EJEMPLOS],
    }


def analizar_complejidad(texto, palabras):
    largas = [palabra for palabra in palabras if len(palabra) >= LARGO_PALABRA_LARGA]
    lista_oraciones = oraciones(texto)
    compuestas = sum(1 for oracion in lista_oraciones if SUBORDINANTES & set(tokenizar(oracion)))
    ratio_largas = len(largas) / len(palabras)
    ratio_compuestas = compuestas / max(len(lista_oraciones), 1)

    if ratio_largas > 0.15 and ratio_compuestas > 0.4:
        nivel = "Alto, vocabulario y estructura ricos"
    elif ratio_largas > 0.08 or ratio_compuestas > 0.25:
        nivel = "Medio"
    else:
        nivel = "Básico, lenguaje sencillo y directo"

    return {
        "nivel_complejidad": nivel,
        "palabras_largas_count": len(largas),
        "ratio_palabras_largas": round(ratio_largas * 100, 1),
        "oraciones_compuestas": compuestas,
        "ratio_compuestas": round(ratio_compuestas * 100, 1),
        "ejemplos_largas": sorted(set(largas))[:MAXIMO_EJEMPLOS],
    }

