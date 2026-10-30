import shutil
import subprocess

import numpy as np

from config import FRECUENCIA_MUESTREO


class AudioNoCompatible(RuntimeError):
    pass


# Devuelve el audio mono a 16 kHz, que es lo que esperan Whisper y el analisis de tono
def cargar_audio(ruta):
    try:
        return _cargar_con_soundfile(ruta)
    except Exception:
        return _cargar_con_ffmpeg(ruta)


def duracion_segundos(audio):
    return len(audio) / FRECUENCIA_MUESTREO


def _cargar_con_soundfile(ruta):
    import soundfile

    audio, frecuencia = soundfile.read(ruta, dtype="float32", always_2d=True)
    audio = audio.mean(axis=1)
    if frecuencia != FRECUENCIA_MUESTREO:
        import librosa

        audio = librosa.resample(audio, orig_sr=frecuencia, target_sr=FRECUENCIA_MUESTREO)
    return audio.astype(np.float32)


# Formatos como .m4a no los lee soundfile y necesitan ffmpeg instalado en el sistema
def _cargar_con_ffmpeg(ruta):
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise AudioNoCompatible(
            f"No se pudo leer '{ruta}'. Para este formato instala ffmpeg o convierte el archivo a WAV."
        )

    comando = [
        ffmpeg, "-nostdin", "-i", str(ruta),
        "-f", "f32le", "-ac", "1", "-ar", str(FRECUENCIA_MUESTREO), "-",
    ]
    proceso = subprocess.run(comando, capture_output=True)
    if proceso.returncode != 0:
        raise AudioNoCompatible(f"ffmpeg no pudo leer el archivo: {proceso.stderr.decode(errors='ignore')[-300:]}")
    return np.frombuffer(proceso.stdout, dtype=np.float32).copy()
