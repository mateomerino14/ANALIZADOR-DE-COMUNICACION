import numpy as np
import pytest

from config import FRECUENCIA_MUESTREO
from nucleo import flujo
from nucleo.almacen import reporte_a_texto

soundfile = pytest.importorskip("soundfile")
pytest.importorskip("librosa")

TRANSCRIPCION = "Bueno, eh, hoy les presento el proyecto. Este, creo que es importante, ¿no?"


# Reemplaza a Whisper para probar el flujo sin descargar el modelo
class TranscriptorFalso:
    def __init__(self):
        self.audio_recibido = None

    def cargar_modelo(self):
        pass

    def transcribir(self, audio):
        self.audio_recibido = audio
        return {
            "texto": TRANSCRIPCION,
            "segmentos": [
                {"inicio": 0.0, "fin": 2.0, "texto": "Bueno, eh, hoy les presento el proyecto."},
                {"inicio": 4.5, "fin": 6.0, "texto": "Este, creo que es importante, ¿no?"},
            ],
        }


def voz_sintetica(segundos):
    tiempo = np.linspace(0, segundos, int(FRECUENCIA_MUESTREO * segundos), endpoint=False)
    tono = 140 + 30 * np.sin(2 * np.pi * 0.5 * tiempo)
    envolvente = (np.sin(2 * np.pi * 2 * tiempo) > 0).astype(float)
    return 0.4 * envolvente * np.sin(2 * np.pi * np.cumsum(tono) / FRECUENCIA_MUESTREO)


def test_flujo_de_audio(tmp_path, monkeypatch):
    monkeypatch.setattr(flujo, "guardar_reporte", lambda reporte: None)
    ruta = tmp_path / "charla.wav"
    soundfile.write(ruta, voz_sintetica(6), FRECUENCIA_MUESTREO)
    transcriptor = TranscriptorFalso()
    avisos = []

    reporte = flujo.analizar_audio(ruta, transcriptor, aviso=avisos.append)

    assert len(transcriptor.audio_recibido) == FRECUENCIA_MUESTREO * 6
    assert reporte["estadisticas"]["duracion_seg"] == 6.0
    assert reporte["estadisticas"]["velocidad"] == "normal"
    assert reporte["pausas"]["largas"] == 1
    assert reporte["muletillas"]["total"] == 4
    assert reporte["tono"]["disponible"]
    assert reporte["tono"]["pitch"]["tipo"] == "Media"
    assert "VOZ Y PAUSAS" in reporte_a_texto(reporte)
    assert avisos


def test_flujo_de_texto(tmp_path, monkeypatch):
    guardados = []
    monkeypatch.setattr(flujo, "guardar_reporte", guardados.append)
    reporte = flujo.analizar_texto(TRANSCRIPCION)
    assert guardados == [reporte]
    assert reporte["tono"] == {"disponible": False}
