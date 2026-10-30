import numpy as np

from config import FRECUENCIA_MUESTREO, PITCH_MAX_HZ, PITCH_MIN_HZ

PITCH_GRAVE_HZ = 130
PITCH_MEDIO_HZ = 200
ENERGIA_UNIFORME_DB = 5
ENERGIA_CONSISTENTE_DB = 12
EXPRESIVIDAD_BAJA_HZ = 500
EXPRESIVIDAD_MEDIA_HZ = 1200
RITMO_REGULAR_SEG = 0.1
RITMO_NATURAL_SEG = 0.25


# Recibe el audio ya cargado a 16 kHz; librosa se importa aqui para que el analisis de texto no la necesite
def analizar_tono(audio):
    try:
        import librosa
    except ImportError:
        return {"disponible": False, "mensaje": "librosa no está instalado"}

    frecuencia = FRECUENCIA_MUESTREO
    resultado = {
        "disponible": True,
        "pitch": _pitch(librosa, audio, frecuencia),
        "energia": _energia(librosa, audio),
        "expresividad": _expresividad(librosa, audio, frecuencia),
        "ritmo": _ritmo(librosa, audio, frecuencia),
    }
    resultado["perfil"] = perfil_vocal(resultado)
    return resultado


def _pitch(librosa, audio, frecuencia):
    f0, con_voz, _ = librosa.pyin(audio, fmin=PITCH_MIN_HZ, fmax=PITCH_MAX_HZ, sr=frecuencia)
    f0_con_voz = f0[con_voz & ~np.isnan(f0)]
    if len(f0_con_voz) == 0:
        return {"tipo": "Sin voz detectada"}

    promedio = float(np.mean(f0_con_voz))
    if promedio < PITCH_GRAVE_HZ:
        tipo = "Grave"
    elif promedio < PITCH_MEDIO_HZ:
        tipo = "Media"
    else:
        tipo = "Aguda"

    return {
        "promedio_hz": round(promedio, 1),
        "desviacion_hz": round(float(np.std(f0_con_voz)), 1),
        "tipo": tipo,
        "voz_activa_pct": round(len(f0_con_voz) / max(len(f0), 1) * 100, 1),
    }


def _energia(librosa, audio):
    rms_db = librosa.amplitude_to_db(librosa.feature.rms(y=audio)[0], ref=np.max)
    variacion = float(np.std(rms_db))
    if variacion < ENERGIA_UNIFORME_DB:
        clave, descripcion = "uniforme", "Muy uniforme"
    elif variacion < ENERGIA_CONSISTENTE_DB:
        clave, descripcion = "consistente", "Consistente"
    else:
        clave, descripcion = "variable", "Variable"
    return {
        "promedio_db": round(float(np.mean(rms_db)), 1),
        "variacion_db": round(variacion, 1),
        "clave": clave,
        "descripcion": descripcion,
    }


# La variacion del centroide espectral sirve como medida de que tan expresiva es la voz
def _expresividad(librosa, audio, frecuencia):
    variacion = float(np.std(librosa.feature.spectral_centroid(y=audio, sr=frecuencia)[0]))
    if variacion < EXPRESIVIDAD_BAJA_HZ:
        clave, nivel = "baja", "Baja (monótona)"
    elif variacion < EXPRESIVIDAD_MEDIA_HZ:
        clave, nivel = "media", "Media"
    else:
        clave, nivel = "alta", "Alta (muy expresiva)"
    return {"variacion": round(variacion, 1), "clave": clave, "nivel": nivel}


def _ritmo(librosa, audio, frecuencia):
    inicios = librosa.onset.onset_detect(y=audio, sr=frecuencia, units="time")
    if len(inicios) < 2:
        return {"clave": None, "tipo": "Audio muy corto"}

    intervalos = np.diff(inicios)
    variacion = float(np.std(intervalos))
    if variacion < RITMO_REGULAR_SEG:
        clave, tipo = "regular", "Muy regular"
    elif variacion < RITMO_NATURAL_SEG:
        clave, tipo = "natural", "Natural"
    else:
        clave, tipo = "irregular", "Irregular"
    return {
        "inicios": len(inicios),
        "intervalo_prom": round(float(np.mean(intervalos)), 3),
        "clave": clave,
        "tipo": tipo,
    }


def perfil_vocal(resultado):
    fortalezas = []
    mejoras = []

    expresividad = resultado["expresividad"]["clave"]
    if expresividad == "baja":
        mejoras.append("Trabajar la variación de tono para evitar la monotonía")
    else:
        fortalezas.append("Buena variación tonal")

    energia = resultado["energia"]["clave"]
    if energia == "consistente":
        fortalezas.append("Volumen uniforme y controlado")
    elif energia == "variable":
        mejoras.append("Mantener un volumen más constante")

    ritmo = resultado["ritmo"]["clave"]
    if ritmo == "natural":
        fortalezas.append("Ritmo natural y fluido")
    elif ritmo == "irregular":
        mejoras.append("Practicar la fluidez rítmica")

    return {"fortalezas": fortalezas, "mejoras": mejoras}
