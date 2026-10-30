import numpy as np
import pytest

from config import FRECUENCIA_MUESTREO
from nucleo.audio import AudioNoCompatible, cargar_audio, duracion_segundos

soundfile = pytest.importorskip("soundfile")
pytest.importorskip("librosa")


def test_lleva_estereo_a_mono_y_16_khz(tmp_path):
    frecuencia_original = 44100
    tiempo = np.linspace(0, 1, frecuencia_original, endpoint=False)
    estereo = np.stack([np.sin(2 * np.pi * 220 * tiempo)] * 2, axis=1) * 0.5
    ruta = tmp_path / "estereo.wav"
    soundfile.write(ruta, estereo, frecuencia_original)

    audio = cargar_audio(ruta)
    assert audio.ndim == 1
    assert audio.dtype == np.float32
    assert duracion_segundos(audio) == pytest.approx(1.0, abs=0.01)
    assert len(audio) == pytest.approx(FRECUENCIA_MUESTREO, abs=5)


def test_archivo_ilegible_sin_ffmpeg(tmp_path, monkeypatch):
    monkeypatch.setattr("nucleo.audio.shutil.which", lambda _programa: None)
    ruta = tmp_path / "falso.m4a"
    ruta.write_bytes(b"no es audio")
    with pytest.raises(AudioNoCompatible, match="ffmpeg"):
        cargar_audio(ruta)
