from nucleo.almacen import guardar_reporte
from nucleo.analizador import analizar
from nucleo.audio import cargar_audio, duracion_segundos
from nucleo.reporte import generar_reporte
from nucleo.tono import analizar_tono

SESION_AUDIO = "Análisis de audio"
SESION_TEXTO = "Análisis de texto"


def _sin_aviso(_mensaje):
    pass


# aviso recibe mensajes de progreso para mostrarlos en la interfaz
def analizar_audio(ruta, transcriptor, aviso=_sin_aviso):
    aviso("Leyendo el audio...")
    audio = cargar_audio(ruta)
    aviso("Cargando el modelo de transcripción...")
    transcriptor.cargar_modelo()
    aviso("Transcribiendo...")
    transcripcion = transcriptor.transcribir(audio)
    aviso("Analizando el discurso y la voz...")
    analisis = analizar(transcripcion["texto"], duracion_segundos(audio), transcripcion["segmentos"])
    reporte = generar_reporte(analisis, analizar_tono(audio), SESION_AUDIO)
    guardar_reporte(reporte)
    return reporte


def analizar_texto(texto):
    reporte = generar_reporte(analizar(texto), sesion=SESION_TEXTO)
    guardar_reporte(reporte)
    return reporte
