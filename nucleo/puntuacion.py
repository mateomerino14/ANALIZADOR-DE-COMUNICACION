PESOS = {
    "fluidez": 0.30,
    "vocabulario": 0.20,
    "claridad": 0.20,
    "coherencia": 0.15,
    "asertividad": 0.15,
}

PENALIZACION_VELOCIDAD = {"normal": 0, "lento": 15, "rapido": 15, "muy_rapido": 25}
PENALIZACION_MAXIMA_MULETILLAS = 40
PUNTOS_ASERTIVIDAD = {"Alta": 90, "Media": 65, "Baja": 35}


def limitar(valor):
    return max(0, min(100, round(valor)))


def subpuntuaciones(resultados):
    muletillas = resultados["muletillas"]
    velocidad = resultados["estadisticas"]["velocidad"]
    claridad = resultados["claridad"]
    coherencia = resultados["coherencia"]

    penalizacion_muletillas = min(PENALIZACION_MAXIMA_MULETILLAS, muletillas["ratio"] * 300)
    penalizacion_velocidad = PENALIZACION_VELOCIDAD.get(velocidad, 0)

    puntos = {
        "fluidez": limitar(100 - penalizacion_muletillas - penalizacion_velocidad),
        "vocabulario": limitar(
            resultados["diversidad"]["ttr"] * 140 - resultados["repeticiones"]["indice_redundancia"] * 60
        ),
        "claridad": limitar(claridad["indice_legibilidad"] - claridad["dobles_negaciones"] * 10),
        "coherencia": limitar(coherencia["ratio_conectores"] * 20 + coherencia["solapamiento_temas"] * 60 + 20),
        "asertividad": PUNTOS_ASERTIVIDAD[resultados["asertividad"]["nivel_asertividad"]],
        "pausas": None,
    }

    pausas = resultados["pausas"]
    if pausas:
        puntos["pausas"] = limitar(100 - pausas["largas"] / max(pausas["total"], 1) * 60)
    return puntos


# Las pausas se muestran aparte, solo existen cuando el analisis viene de un audio
def puntuacion_global(puntos):
    return limitar(sum(puntos[clave] * peso for clave, peso in PESOS.items()))
