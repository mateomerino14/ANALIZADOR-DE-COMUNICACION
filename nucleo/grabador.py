import threading

import numpy as np

from config import AUDIO_GRABADO, CANALES, FRECUENCIA_MUESTREO, SEGUNDOS_PRUEBA_MICROFONO, TAMANO_BLOQUE

ESPERA_CIERRE_SEG = 2


class MicrofonoNoDisponible(RuntimeError):
    pass


# Graba en un hilo aparte para que la ventana siga respondiendo
class Grabador:
    def __init__(self):
        self.grabando = False
        self.bloques = []
        self.hilo = None
        self.duracion = 0.0

    def verificar_microfono(self):
        import sounddevice

        try:
            sounddevice.rec(int(SEGUNDOS_PRUEBA_MICROFONO * FRECUENCIA_MUESTREO),
                            samplerate=FRECUENCIA_MUESTREO, channels=CANALES, dtype="float32")
            sounddevice.wait()
        except Exception as error:
            raise MicrofonoNoDisponible(f"No se pudo acceder al micrófono: {error}") from error

    def iniciar(self):
        self.grabando = True
        self.bloques = []
        self.hilo = threading.Thread(target=self._grabar, daemon=True)
        self.hilo.start()

    def _grabar(self):
        import sounddevice

        with sounddevice.InputStream(samplerate=FRECUENCIA_MUESTREO, channels=CANALES,
                                     dtype="float32", blocksize=TAMANO_BLOQUE) as entrada:
            while self.grabando:
                bloque, _ = entrada.read(TAMANO_BLOQUE)
                self.bloques.append(bloque.copy())

    # Devuelve la ruta del WAV grabado, o None si no se capto audio
    def detener(self):
        import soundfile

        self.grabando = False
        if self.hilo:
            self.hilo.join(timeout=ESPERA_CIERRE_SEG)
        if not self.bloques:
            return None

        audio = np.concatenate(self.bloques, axis=0)
        self.duracion = len(audio) / FRECUENCIA_MUESTREO
        AUDIO_GRABADO.parent.mkdir(parents=True, exist_ok=True)
        soundfile.write(AUDIO_GRABADO, audio, FRECUENCIA_MUESTREO)
        return AUDIO_GRABADO
