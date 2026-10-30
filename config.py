import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent

CARPETA_REPORTES = RAIZ / "reportes"
CARPETA_TEMPORAL = RAIZ / "temporal"
AUDIO_GRABADO = CARPETA_TEMPORAL / "grabacion.wav"
FORMATO_ARCHIVO_REPORTE = "%Y%m%d_%H%M%S"
FORMATO_FECHA_REPORTE = "%Y-%m-%d %H:%M:%S"

EXTENSIONES_AUDIO = (".wav", ".mp3", ".m4a", ".ogg", ".flac")

# Whisper trabaja a 16 kHz mono, todo el audio se lleva a ese formato
FRECUENCIA_MUESTREO = 16000
CANALES = 1
TAMANO_BLOQUE = 1024
SEGUNDOS_PRUEBA_MICROFONO = 0.3

# Opciones: tiny, base, small, medium, large. Se cambia con la variable EXPRESA_MODELO
MODELO_WHISPER = os.environ.get("EXPRESA_MODELO", "base")
IDIOMA_WHISPER = "es"

PAUSA_MINIMA_SEG = 0.5
PAUSA_LARGA_SEG = 2.0

PPM_LENTO = 100
PPM_NORMAL = 160
PPM_RAPIDO = 200

MULETILLA_FRECUENCIA_ALTA = 5
MULETILLA_FRECUENCIA_MEDIA = 3
# Porcentaje del discurso a partir del cual las muletillas, aunque variadas, ya molestan
DENSIDAD_MULETILLAS_ALTA = 5
UMBRAL_SIMILITUD_MULETILLAS = 0.15

VENTANA_REPETICION = 10
VENTANA_MATTR = 50
DIVERSIDAD_ALTA = 0.6
DIVERSIDAD_MEDIA = 0.4

PITCH_MIN_HZ = 75
PITCH_MAX_HZ = 400
