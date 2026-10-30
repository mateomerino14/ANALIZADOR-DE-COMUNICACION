FONDO = "#faf9f6"
SUPERFICIE = "#ffffff"
PRIMARIO = "#a7c7e7"
PRIMARIO_OSCURO = "#4f7ba8"
SECUNDARIO = "#eef2f5"
SELECCION = "#dce8f3"
TEXTO = "#4a4a4a"
TEXTO_SUAVE = "#8a8a8a"
BORDE = "#e8e6e1"
GRABAR = "#ffb3ba"
GRABANDO = "#ff8a94"

COLOR_EXCELENTE = "#8fd9c4"
COLOR_BUENO = "#a7c7e7"
COLOR_MEDIO = "#f4d9a0"
COLOR_BAJO = "#ffb3ba"

COLOR_PRIORIDAD = {"alta": COLOR_BAJO, "media": COLOR_MEDIO, "info": COLOR_BUENO}

FUENTE = "Segoe UI"


def fuente(tamano, *estilos):
    return (FUENTE, tamano, *estilos)


def color_por_valor(valor):
    if valor >= 80:
        return COLOR_EXCELENTE
    if valor >= 60:
        return COLOR_BUENO
    if valor >= 40:
        return COLOR_MEDIO
    return COLOR_BAJO
