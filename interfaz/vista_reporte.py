import tkinter as tk
from dataclasses import dataclass

from interfaz.componentes import (
    BarraProgreso,
    EncabezadoSeccion,
    Medidor,
    TarjetaMetrica,
    etiqueta_color,
    fila_resaltada,
    limpiar,
)
from interfaz.tema import (
    BORDE,
    COLOR_BAJO,
    COLOR_BUENO,
    COLOR_EXCELENTE,
    COLOR_MEDIO,
    COLOR_PRIORIDAD,
    PRIMARIO,
    PRIMARIO_OSCURO,
    SUPERFICIE,
    TEXTO,
    TEXTO_SUAVE,
    color_por_valor,
    fuente,
)

MAXIMO_MULETILLAS = 8
MAXIMO_PAUSAS_LARGAS_BIEN = 2
PUNTOS_VELOCIDAD = {"normal": 100, "lento": 55, "rapido": 55, "muy_rapido": 30}


@dataclass
class Disposicion:
    bg: str = SUPERFICIE
    ancho_texto: int = 600
    columnas_tarjetas: int = 4


AMPLIA = Disposicion()
ANGOSTA = Disposicion(ancho_texto=420, columnas_tarjetas=2)


# Dibuja el reporte completo; lo usan la pestaña de analisis y el historial
def mostrar_reporte(contenedor, reporte, disposicion=AMPLIA):
    limpiar(contenedor)
    secciones = (
        _encabezado, _metricas_clave, _subpuntuaciones, _muletillas, _tono_y_coherencia,
        _acustica, _pausas, _recomendaciones, _ejercicios,
    )
    for seccion in secciones:
        seccion(contenedor, reporte, disposicion)
    tk.Frame(contenedor, bg=disposicion.bg, height=20).pack()


def _seccion(contenedor, titulo, disposicion):
    bg = disposicion.bg
    EncabezadoSeccion(contenedor, titulo, bg=bg).pack(fill="x", pady=(16, 6))
    cuerpo = tk.Frame(contenedor, bg=bg)
    cuerpo.pack(fill="x", anchor="w")
    return cuerpo


def _parrafo(padre, texto, disposicion, tamano=9, *estilos, color=TEXTO):
    return tk.Label(padre, text=texto, font=fuente(tamano, *estilos), bg=disposicion.bg, fg=color,
                    wraplength=disposicion.ancho_texto, justify="left", anchor="w")


def _encabezado(contenedor, reporte, disposicion):
    bg = disposicion.bg
    bloque = tk.Frame(contenedor, bg=bg)
    bloque.pack(fill="x", pady=(6, 0))
    Medidor(bloque, reporte["puntuacion"], reporte["nivel"], bg=bg).pack(side="left", padx=(0, 24))

    info = tk.Frame(bloque, bg=bg)
    info.pack(side="left", fill="both", expand=True, anchor="n", pady=10)
    tk.Label(info, text=f"{reporte['sesion']}  ·  {reporte['fecha']}", font=fuente(9),
             bg=bg, fg=TEXTO_SUAVE).pack(anchor="w")
    _parrafo(info, reporte["mensaje_general"], disposicion, 11, "bold").pack(anchor="w", pady=(4, 0))
    _parrafo(info, "Texto analizado:", disposicion, 9, "bold", color=TEXTO_SUAVE).pack(anchor="w", pady=(12, 2))
    _parrafo(info, f"“{reporte['texto_analizado']}”", disposicion, 9, "italic").pack(anchor="w")


def _metricas_clave(contenedor, reporte, disposicion):
    bg = disposicion.bg
    cuerpo = _seccion(contenedor, "Métricas clave", disposicion)
    estadisticas = reporte["estadisticas"]
    diversidad = reporte["diversidad"]
    muletillas = reporte["muletillas"]

    if estadisticas["velocidad"] is None:
        velocidad = ("—", "Solo se mide en audio", BORDE)
    else:
        velocidad = (
            f"{estadisticas['palabras_por_min']:.0f} ppm",
            f"{estadisticas['categoria_velocidad']} (ideal {estadisticas['rango_ideal']})",
            color_por_valor(PUNTOS_VELOCIDAD[estadisticas["velocidad"]]),
        )

    tarjetas = (
        ("Velocidad", *velocidad),
        ("Diversidad léxica", f"{diversidad['ttr']:.2f}", diversidad["nivel"],
         color_por_valor(diversidad["ttr"] * 100)),
        ("Claridad", reporte["claridad"]["nivel_legibilidad"], "Índice de legibilidad",
         color_por_valor(reporte["subpuntuaciones"]["claridad"])),
        ("Muletillas", str(muletillas["total"]), muletillas["impacto"],
         color_por_valor(100 - muletillas["porcentaje"] * 5)),
    )
    columnas = disposicion.columnas_tarjetas
    for indice, (titulo, valor, descripcion, color) in enumerate(tarjetas):
        TarjetaMetrica(cuerpo, titulo, valor, descripcion, color, bg=bg).grid(
            row=indice // columnas, column=indice % columnas, sticky="nsew", padx=(0, 10), pady=6)
    for columna in range(columnas):
        cuerpo.columnconfigure(columna, weight=1, uniform="tarjetas")


def _subpuntuaciones(contenedor, reporte, disposicion):
    bg = disposicion.bg
    cuerpo = _seccion(contenedor, "Subpuntuaciones", disposicion)
    for clave, valor in reporte["subpuntuaciones"].items():
        if valor is not None:
            BarraProgreso(cuerpo, clave.capitalize(), valor, bg=bg).pack(anchor="w", pady=3)


def _muletillas(contenedor, reporte, disposicion):
    bg = disposicion.bg
    muletillas = reporte["muletillas"]
    cuerpo = _seccion(contenedor, "Muletillas", disposicion)

    color_diagnostico = COLOR_EXCELENTE
    if muletillas["alta_densidad"]:
        color_diagnostico = COLOR_BAJO
    fila = tk.Frame(cuerpo, bg=bg)
    fila.pack(anchor="w", pady=(0, 4))
    etiqueta_color(fila, muletillas["diagnostico_vectorial"], color_diagnostico).pack(side="left")
    fila_resaltada(cuerpo, [
        ("Similitud coseno (TF-IDF): ", None),
        (f"{muletillas['similitud_maxima']:.3f}", PRIMARIO_OSCURO),
        ("   ·   Categoría más cercana: ", None),
        (muletillas["patron_cercano"], PRIMARIO_OSCURO),
    ], bg=bg).pack(anchor="w", pady=(0, 6))

    if not muletillas["por_categoria"]:
        _parrafo(cuerpo, "No se detectaron muletillas.", disposicion, color=TEXTO_SUAVE).pack(anchor="w")
        return

    for categoria, grupo in muletillas["por_categoria"].items():
        detalle = ", ".join(f"'{m}' ×{v}" for m, v in list(grupo["items"].items())[:MAXIMO_MULETILLAS])
        fila_resaltada(cuerpo, [(f"{categoria} ({grupo['total']}): ", PRIMARIO_OSCURO), (detalle, None)],
                       bg=bg).pack(anchor="w", pady=(4, 0))
        _parrafo(cuerpo, grupo["descripcion"], disposicion, 8, color=TEXTO_SUAVE).pack(anchor="w")


def _tono_y_coherencia(contenedor, reporte, disposicion):
    bg = disposicion.bg
    cuerpo = _seccion(contenedor, "Asertividad, tono y coherencia", disposicion)
    subpuntuaciones = reporte["subpuntuaciones"]
    coherencia = reporte["coherencia"]
    etiquetas = (
        (f"Asertividad: {reporte['asertividad']['nivel_asertividad']}",
         color_por_valor(subpuntuaciones["asertividad"])),
        (f"Tono: {reporte['sentimiento']['tono_general']}", COLOR_BUENO),
        (f"Coherencia: {coherencia['nivel_coherencia']}", color_por_valor(subpuntuaciones["coherencia"])),
    )
    fila = tk.Frame(cuerpo, bg=bg)
    fila.pack(anchor="w")
    for texto, color in etiquetas:
        etiqueta_color(fila, texto, color).pack(side="left", padx=(0, 6))
    _parrafo(cuerpo, f"{coherencia['detalle_coherencia']}. {coherencia['progresion_tematica']}.", disposicion,
             color=TEXTO_SUAVE).pack(anchor="w", pady=(6, 0))


def _acustica(contenedor, reporte, disposicion):
    bg = disposicion.bg
    tono = reporte["tono"]
    if not tono.get("disponible"):
        return
    cuerpo = _seccion(contenedor, "Acústica de la voz", disposicion)
    fila = tk.Frame(cuerpo, bg=bg)
    fila.pack(anchor="w")
    for texto, color in (
        (f"Voz: {tono['pitch']['tipo']}", COLOR_BUENO),
        (f"Expresividad: {tono['expresividad']['nivel']}", COLOR_MEDIO),
        (f"Volumen: {tono['energia']['descripcion']}", COLOR_BUENO),
        (f"Ritmo: {tono['ritmo']['tipo']}", COLOR_BUENO),
    ):
        etiqueta_color(fila, texto, color).pack(side="left", padx=(0, 6))
    for fortaleza in tono["perfil"]["fortalezas"]:
        _parrafo(cuerpo, f"+ {fortaleza}", disposicion).pack(anchor="w", pady=(4, 0))
    for mejora in tono["perfil"]["mejoras"]:
        _parrafo(cuerpo, f"– {mejora}", disposicion).pack(anchor="w", pady=(4, 0))


def _pausas(contenedor, reporte, disposicion):
    bg = disposicion.bg
    pausas = reporte["pausas"]
    if not pausas:
        return
    cuerpo = _seccion(contenedor, "Pausas y silencios", disposicion)
    color_largas = PRIMARIO_OSCURO
    if pausas["largas"] > MAXIMO_PAUSAS_LARGAS_BIEN:
        color_largas = COLOR_BAJO
    fila_resaltada(cuerpo, [
        ("Total: ", None), (str(pausas["total"]), PRIMARIO_OSCURO),
        ("   ·   Largas (más de 2 s): ", None), (str(pausas["largas"]), color_largas),
        ("   ·   Promedio: ", None), (f"{pausas['promedio']} s", PRIMARIO_OSCURO),
    ], bg=bg).pack(anchor="w")
    _parrafo(cuerpo, pausas["evaluacion"], disposicion, color=TEXTO_SUAVE).pack(anchor="w", pady=(4, 0))


def _recomendaciones(contenedor, reporte, disposicion):
    bg = disposicion.bg
    cuerpo = _seccion(contenedor, "Recomendaciones", disposicion)
    for recomendacion in reporte["recomendaciones"]:
        fila = tk.Frame(cuerpo, bg=bg)
        fila.pack(fill="x", anchor="w", pady=3)
        etiqueta_color(fila, recomendacion["categoria"], COLOR_PRIORIDAD[recomendacion["prioridad"]]).pack(
            side="left", anchor="n", padx=(0, 8))
        _parrafo(fila, recomendacion["texto"], disposicion).pack(side="left", fill="x", expand=True)


def _ejercicios(contenedor, reporte, disposicion):
    bg = disposicion.bg
    cuerpo = _seccion(contenedor, "Plan de ejercicios", disposicion)
    for numero, ejercicio in enumerate(reporte["ejercicios"], start=1):
        marco = tk.Frame(cuerpo, bg=BORDE)
        marco.pack(fill="x", anchor="w", pady=4)
        tarjeta = tk.Frame(marco, bg=bg)
        tarjeta.pack(fill="x", padx=1, pady=1)

        cabecera = tk.Frame(tarjeta, bg=bg)
        cabecera.pack(fill="x", padx=14, pady=(10, 0))
        tk.Label(cabecera, text=f"{numero}. {ejercicio['nombre']}", font=fuente(10, "bold"),
                 bg=bg, fg=TEXTO).pack(side="left")
        etiqueta_color(cabecera, ejercicio["nivel"], PRIMARIO).pack(side="left", padx=(8, 0))
        tk.Label(cabecera, text=ejercicio["duracion"], font=fuente(8), bg=bg, fg=TEXTO_SUAVE).pack(side="right")

        _parrafo(tarjeta, f"Objetivo: {ejercicio['objetivo']}", disposicion, 9, "italic", color=TEXTO_SUAVE).pack(
            anchor="w", padx=14, pady=(4, 0))
        _parrafo(tarjeta, ejercicio["descripcion"], disposicion).pack(anchor="w", padx=14, pady=(4, 10))
