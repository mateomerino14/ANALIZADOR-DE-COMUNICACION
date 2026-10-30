import tkinter as tk
from dataclasses import dataclass

from config import MULETILLA_FRECUENCIA_ALTA, MULETILLA_FRECUENCIA_MEDIA
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
    TEXTO_ALERTA,
    TEXTO_SUAVE,
    color_por_valor,
    fuente,
)

MAXIMO_MULETILLAS = 8
MAXIMO_PAUSAS_LARGAS_BIEN = 2
MAXIMO_EJEMPLOS = 6
CARACTERES_CONTEXTO = 30
PUNTOS_VELOCIDAD = {"normal": 100, "lento": 55, "rapido": 55, "muy_rapido": 30}
COLOR_NIVEL = {"Alta": COLOR_EXCELENTE, "Media": COLOR_MEDIO, "Baja": COLOR_BAJO}
COLOR_TONO = {"Positivo": COLOR_EXCELENTE, "Neutro": COLOR_BUENO, "Negativo": COLOR_BAJO}
SEVERIDADES = (
    ("criticas", f"Críticas ({MULETILLA_FRECUENCIA_ALTA}+ veces)", COLOR_BAJO),
    ("moderadas", f"Moderadas ({MULETILLA_FRECUENCIA_MEDIA}+ veces)", COLOR_MEDIO),
    ("leves", "Leves", COLOR_BUENO),
)


@dataclass
class Disposicion:
    bg: str = SUPERFICIE
    ancho_texto: int = 600
    columnas_tarjetas: int = 4
    columnas_datos: int = 2


AMPLIA = Disposicion()
ANGOSTA = Disposicion(ancho_texto=420, columnas_tarjetas=2, columnas_datos=1)


# Dibuja el reporte completo; lo usan la pestaña de analisis y el historial
def mostrar_reporte(contenedor, reporte, disposicion=AMPLIA):
    limpiar(contenedor)
    secciones = (
        _encabezado, _metricas_clave, _subpuntuaciones, _muletillas, _vocabulario, _claridad,
        _complejidad, _coherencia, _asertividad_y_sentimiento, _acustica, _pausas,
        _recomendaciones, _ejercicios,
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


# Pares (dato, valor) en columnas; en el historial se apilan en una sola
def _tabla_datos(padre, pares, disposicion):
    bg = disposicion.bg
    tabla = tk.Frame(padre, bg=bg)
    tabla.pack(fill="x", anchor="w", pady=(2, 4))
    columnas = disposicion.columnas_datos
    for indice, (dato, valor) in enumerate(pares):
        fila, columna = divmod(indice, columnas)
        tk.Label(tabla, text=dato, font=fuente(9), bg=bg, fg=TEXTO_SUAVE, anchor="w").grid(
            row=fila, column=columna * 2, sticky="w", padx=(0, 8), pady=1)
        tk.Label(tabla, text=valor, font=fuente(9, "bold"), bg=bg, fg=TEXTO, anchor="w").grid(
            row=fila, column=columna * 2 + 1, sticky="w", padx=(0, 28), pady=1)


# Lista corta con titulo; no dibuja nada si no hay elementos
def _lista(padre, titulo, elementos, disposicion):
    if not elementos:
        return
    fila_resaltada(padre, [(f"{titulo}: ", PRIMARIO_OSCURO)], bg=disposicion.bg).pack(anchor="w", pady=(4, 0))
    _parrafo(padre, ", ".join(elementos[:MAXIMO_EJEMPLOS]), disposicion).pack(anchor="w")


def _etiquetas(padre, etiquetas, disposicion):
    fila = tk.Frame(padre, bg=disposicion.bg)
    fila.pack(anchor="w", pady=(0, 4))
    for texto, color in etiquetas:
        etiqueta_color(fila, texto, color).pack(side="left", padx=(0, 6))


def _porcentaje(valor):
    return f"{valor:.0f} %"


def _encabezado(contenedor, reporte, disposicion):
    bg = disposicion.bg
    bloque = tk.Frame(contenedor, bg=bg)
    bloque.pack(fill="x", pady=(6, 0))
    Medidor(bloque, reporte["puntuacion"], reporte["nivel"], bg=bg).pack(side="left", padx=(0, 24))

    estadisticas = reporte["estadisticas"]
    datos = f"{reporte['sesion']}  ·  {reporte['fecha']}  ·  {estadisticas['total_palabras']} palabras"
    if estadisticas["velocidad"] is not None:
        datos += f"  ·  {estadisticas['duracion_seg']} s"

    info = tk.Frame(bloque, bg=bg)
    info.pack(side="left", fill="both", expand=True, anchor="n", pady=10)
    _parrafo(info, datos, disposicion, color=TEXTO_SUAVE).pack(anchor="w")
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
    _etiquetas(cuerpo, [(muletillas["diagnostico_vectorial"], color_diagnostico)], disposicion)
    fila_resaltada(cuerpo, [
        ("Similitud coseno (TF-IDF): ", None),
        (f"{muletillas['similitud_maxima']:.3f}", PRIMARIO_OSCURO),
        ("   ·   Categoría más cercana: ", None),
        (muletillas["patron_cercano"], PRIMARIO_OSCURO),
    ], bg=bg).pack(anchor="w", pady=(0, 6))

    if not muletillas["por_categoria"]:
        _parrafo(cuerpo, "No se detectaron muletillas.", disposicion, color=TEXTO_SUAVE).pack(anchor="w")
        return

    _etiquetas(cuerpo, [
        (f"{titulo}: {len(muletillas[clave])}", color) for clave, titulo, color in SEVERIDADES
    ], disposicion)
    _tabla_datos(cuerpo, [
        ("Porcentaje del discurso", _porcentaje(muletillas["porcentaje"])),
        ("Frecuencia", muletillas["impacto"]),
    ], disposicion)

    for categoria, grupo in muletillas["por_categoria"].items():
        detalle = ", ".join(f"'{m}' ×{v}" for m, v in list(grupo["items"].items())[:MAXIMO_MULETILLAS])
        fila_resaltada(cuerpo, [(f"{categoria} ({grupo['total']}): ", PRIMARIO_OSCURO), (detalle, None)],
                       bg=bg).pack(anchor="w", pady=(4, 0))
        _parrafo(cuerpo, grupo["descripcion"], disposicion, 8, color=TEXTO_SUAVE).pack(anchor="w")


def _vocabulario(contenedor, reporte, disposicion):
    diversidad = reporte["diversidad"]
    repeticiones = reporte["repeticiones"]
    cuerpo = _seccion(contenedor, "Vocabulario y repeticiones", disposicion)
    if not diversidad["total"]:
        _parrafo(cuerpo, "No hay palabras de contenido para medir.", disposicion, color=TEXTO_SUAVE).pack(anchor="w")
        return

    _tabla_datos(cuerpo, [
        ("Palabras distintas", f"{diversidad['unicos']} de {diversidad['total']}"),
        ("Diversidad (TTR)", f"{diversidad['ttr']:.2f}"),
        ("Diversidad por ventanas (MATTR)", f"{diversidad['mattr']:.2f}"),
        ("Palabras usadas una sola vez", _porcentaje(diversidad["ratio_hapax"] * 100)),
        ("Palabras de contenido", str(repeticiones["total_contenido"])),
        ("Índice de redundancia", _porcentaje(repeticiones["indice_redundancia"] * 100)),
    ], disposicion)
    _lista(cuerpo, "Palabras clave", diversidad["palabras_clave"], disposicion)
    _lista(cuerpo, "Usadas en exceso",
           [f"'{palabra}' ×{veces}" for palabra, veces in repeticiones["en_exceso"].items()], disposicion)
    _lista(cuerpo, "Repetidas muy cerca",
           [f"'{r['palabra']}' a {r['distancia_palabras']} palabras" for r in repeticiones["cercanas"]],
           disposicion)


def _claridad(contenedor, reporte, disposicion):
    claridad = reporte["claridad"]
    cuerpo = _seccion(contenedor, "Claridad", disposicion)
    _etiquetas(cuerpo, [
        (f"Legibilidad: {claridad['nivel_legibilidad']}", color_por_valor(claridad["indice_legibilidad"])),
        (f"Oraciones: {claridad['nivel_oraciones']}", COLOR_BUENO),
    ], disposicion)
    _tabla_datos(cuerpo, [
        ("Índice Fernández Huerta", f"{claridad['indice_legibilidad']:.0f} / 100"),
        ("Oraciones", str(claridad["total_oraciones"])),
        ("Palabras por oración", f"{claridad['palabras_por_oracion']:.1f}"),
        ("Sílabas por palabra", f"{claridad['silabas_prom_palabra']:.2f}"),
        ("Letras por palabra", f"{claridad['long_prom_palabras']:.1f}"),
        ("Dobles negaciones", str(claridad["dobles_negaciones"])),
    ], disposicion)


def _complejidad(contenedor, reporte, disposicion):
    complejidad = reporte["complejidad"]
    cuerpo = _seccion(contenedor, "Complejidad del discurso", disposicion)
    _parrafo(cuerpo, complejidad["nivel_complejidad"], disposicion, 10, "bold").pack(anchor="w")
    _tabla_datos(cuerpo, [
        ("Palabras largas",
         f"{complejidad['palabras_largas_count']} ({_porcentaje(complejidad['ratio_palabras_largas'])})"),
        ("Oraciones compuestas",
         f"{complejidad['oraciones_compuestas']} ({_porcentaje(complejidad['ratio_compuestas'])})"),
    ], disposicion)
    _lista(cuerpo, "Palabras largas", complejidad["ejemplos_largas"], disposicion)


def _coherencia(contenedor, reporte, disposicion):
    coherencia = reporte["coherencia"]
    cuerpo = _seccion(contenedor, "Coherencia", disposicion)
    _etiquetas(cuerpo, [
        (f"Coherencia: {coherencia['nivel_coherencia']}", COLOR_NIVEL[coherencia["nivel_coherencia"]]),
    ], disposicion)
    _parrafo(cuerpo, f"{coherencia['detalle_coherencia']}. {coherencia['progresion_tematica']}.", disposicion,
             color=TEXTO_SUAVE).pack(anchor="w")
    _tabla_datos(cuerpo, [
        ("Conectores lógicos", str(coherencia["total_conectores"])),
        ("Conectores cada 100 palabras", f"{coherencia['ratio_conectores']:.1f}"),
        ("Vocabulario compartido entre mitades", _porcentaje(coherencia["solapamiento_temas"] * 100)),
    ], disposicion)
    _lista(cuerpo, "Conectores usados",
           [f"'{conector}' ×{veces}" for conector, veces in coherencia["conectores_usados"].items()], disposicion)


def _asertividad_y_sentimiento(contenedor, reporte, disposicion):
    asertividad = reporte["asertividad"]
    sentimiento = reporte["sentimiento"]
    cuerpo = _seccion(contenedor, "Asertividad y tono emocional", disposicion)
    _etiquetas(cuerpo, [
        (f"Asertividad: {asertividad['nivel_asertividad']}", COLOR_NIVEL[asertividad["nivel_asertividad"]]),
        (f"Tono: {sentimiento['tono_general']}", COLOR_TONO[sentimiento["tono_general"]]),
    ], disposicion)
    _tabla_datos(cuerpo, [
        ("Expresiones asertivas", str(asertividad["expresiones_asertivas"])),
        ("Expresiones de duda", str(asertividad["expresiones_duda"])),
        ("Palabras positivas", f"{sentimiento['palabras_pos']} ({_porcentaje(sentimiento['ratio_positivo'])})"),
        ("Palabras negativas", f"{sentimiento['palabras_neg']} ({_porcentaje(sentimiento['ratio_negativo'])})"),
        ("Polaridad (-1 a 1)", f"{sentimiento['polaridad']:+.2f}"),
        ("Balance asertivo", f"{asertividad['ratio_asertividad']:+.3f}"),
    ], disposicion)
    _lista(cuerpo, "Asertivas", [f"'{e}'" for e in asertividad["ejemplos_asertivos"]], disposicion)
    _lista(cuerpo, "De duda", [f"'{e}'" for e in asertividad["ejemplos_duda"]], disposicion)
    _lista(cuerpo, "Positivas", sentimiento["ejemplos_pos"], disposicion)
    _lista(cuerpo, "Negativas", sentimiento["ejemplos_neg"], disposicion)


def _datos_voz(tono):
    pares = []
    pitch = tono["pitch"]
    if "promedio_hz" in pitch:
        pares += [
            ("Tono promedio", f"{pitch['promedio_hz']:.0f} Hz (± {pitch['desviacion_hz']:.0f})"),
            ("Tiempo con voz", _porcentaje(pitch["voz_activa_pct"])),
        ]
    energia = tono["energia"]
    pares += [
        ("Volumen promedio", f"{energia['promedio_db']:.1f} dB"),
        ("Variación de volumen", f"{energia['variacion_db']:.1f} dB"),
        ("Variación espectral", f"{tono['expresividad']['variacion']:.0f} Hz"),
    ]
    ritmo = tono["ritmo"]
    if ritmo["clave"] is not None:
        pares.append(("Golpes de voz detectados", f"{ritmo['inicios']} (cada {ritmo['intervalo_prom']:.2f} s)"))
    return pares


def _acustica(contenedor, reporte, disposicion):
    tono = reporte["tono"]
    if not tono.get("disponible"):
        return
    cuerpo = _seccion(contenedor, "Acústica de la voz", disposicion)
    _etiquetas(cuerpo, [
        (f"Voz: {tono['pitch']['tipo']}", COLOR_BUENO),
        (f"Expresividad: {tono['expresividad']['nivel']}", COLOR_MEDIO),
        (f"Volumen: {tono['energia']['descripcion']}", COLOR_BUENO),
        (f"Ritmo: {tono['ritmo']['tipo']}", COLOR_BUENO),
    ], disposicion)
    _tabla_datos(cuerpo, _datos_voz(tono), disposicion)
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
        color_largas = TEXTO_ALERTA
    fila_resaltada(cuerpo, [
        ("Total: ", None), (str(pausas["total"]), PRIMARIO_OSCURO),
        ("   ·   Normales: ", None), (str(pausas["normales"]), PRIMARIO_OSCURO),
        ("   ·   Largas (más de 2 s): ", None), (str(pausas["largas"]), color_largas),
        ("   ·   Promedio: ", None), (f"{pausas['promedio']} s", PRIMARIO_OSCURO),
    ], bg=bg).pack(anchor="w")
    _parrafo(cuerpo, pausas["evaluacion"], disposicion, color=TEXTO_SUAVE).pack(anchor="w", pady=(4, 0))
    for pausa in pausas["detalle"]:
        color = PRIMARIO_OSCURO
        if pausa["larga"]:
            color = TEXTO_ALERTA
        fila_resaltada(cuerpo, [
            (f"{pausa['duracion']:.1f} s", color),
            (f"  antes de “{pausa['contexto'][:CARACTERES_CONTEXTO]}”", None),
        ], bg=bg).pack(anchor="w", pady=1)


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
