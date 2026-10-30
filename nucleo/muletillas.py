from collections import Counter
from functools import cache

from config import MULETILLA_FRECUENCIA_ALTA, MULETILLA_FRECUENCIA_MEDIA, UMBRAL_SIMILITUD_MULETILLAS
from datos.muletillas import CATEGORIAS_MULETILLAS, DESCRIPCION_CATEGORIAS, MULETILLAS_CONTEXTUALES
from nucleo.texto import patron_frase
from nucleo.vectorial import ModeloVectorial

PAUSA_ANTES = set(".!?¿¡,;:")
PAUSA_DESPUES = {",", ";", ":"}


# Algunas muletillas estan en dos categorias; cada una queda en la primera donde aparece
def _indexar_categorias():
    indice = {}
    for categoria, muletillas in CATEGORIAS_MULETILLAS.items():
        for muletilla in muletillas:
            indice.setdefault(muletilla, categoria)
    return indice


CATEGORIA_DE_MULETILLA = _indexar_categorias()


# Las mas largas primero, asi "o sea que" no se cuenta ademas como "o sea"
ORDEN_BUSQUEDA = sorted(CATEGORIA_DE_MULETILLA, key=lambda muletilla: (-len(muletilla.split()), -len(muletilla)))
PATRONES = {muletilla: patron_frase(muletilla) for muletilla in ORDEN_BUSQUEDA}


@cache
def modelo_categorias():
    return ModeloVectorial({
        categoria: " ".join(muletillas) for categoria, muletillas in CATEGORIAS_MULETILLAS.items()
    })


def _hay_pausa_alrededor(texto, inicio, fin):
    previo = texto[:inicio].rstrip()
    if not previo or previo[-1] in PAUSA_ANTES:
        return True
    return texto[fin:].lstrip()[:1] in PAUSA_DESPUES


def contar_muletillas(texto):
    ocupado = [False] * len(texto)
    conteo = Counter()
    for muletilla in ORDEN_BUSQUEDA:
        contextual = muletilla in MULETILLAS_CONTEXTUALES
        for coincidencia in PATRONES[muletilla].finditer(texto):
            inicio, fin = coincidencia.span()
            if any(ocupado[inicio:fin]):
                continue
            if contextual and not _hay_pausa_alrededor(texto, inicio, fin):
                continue
            ocupado[inicio:fin] = [True] * (fin - inicio)
            conteo[muletilla] += 1
    return conteo


def _ordenar(conteo):
    return dict(sorted(conteo.items(), key=lambda par: -par[1]))


def _agrupar_por_categoria(conteo):
    por_categoria = {}
    for muletilla, veces in conteo.most_common():
        categoria = CATEGORIA_DE_MULETILLA[muletilla]
        grupo = por_categoria.setdefault(categoria, {
            "items": {},
            "descripcion": DESCRIPCION_CATEGORIAS.get(categoria, ""),
            "total": 0,
        })
        grupo["items"][muletilla] = veces
        grupo["total"] += veces
    return por_categoria


def analizar_muletillas(texto_normalizado, total_palabras):
    conteo = contar_muletillas(texto_normalizado)
    total = sum(conteo.values())
    ratio = total / max(total_palabras, 1)

    patron_cercano, similitud = modelo_categorias().mas_cercano(texto_normalizado)
    alta_densidad = similitud > UMBRAL_SIMILITUD_MULETILLAS
    if alta_densidad:
        diagnostico = "Alta densidad de muletillas (vectores alineados)"
    else:
        diagnostico = "Discurso limpio (vectores casi ortogonales)"

    if total:
        impacto = f"1 muletilla cada {total_palabras / total:.1f} palabras"
    else:
        impacto = "Sin muletillas detectadas"

    return {
        "total": total,
        "ratio": round(ratio, 4),
        "porcentaje": round(ratio * 100, 2),
        "criticas": _ordenar({m: v for m, v in conteo.items() if v >= MULETILLA_FRECUENCIA_ALTA}),
        "moderadas": _ordenar({
            m: v for m, v in conteo.items() if MULETILLA_FRECUENCIA_MEDIA <= v < MULETILLA_FRECUENCIA_ALTA
        }),
        "leves": _ordenar({m: v for m, v in conteo.items() if v < MULETILLA_FRECUENCIA_MEDIA}),
        "por_categoria": _agrupar_por_categoria(conteo),
        "todas": dict(conteo.most_common()),
        "impacto": impacto,
        "similitud_maxima": round(similitud, 4),
        "patron_cercano": patron_cercano,
        "alta_densidad": alta_densidad,
        "diagnostico_vectorial": diagnostico,
    }
