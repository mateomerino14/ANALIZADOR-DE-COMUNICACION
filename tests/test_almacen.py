import json

from nucleo.almacen import guardar_reporte, listar_reportes, reporte_a_texto
from nucleo.analizador import analizar
from nucleo.reporte import generar_reporte

TEXTO = "Bueno, eh, presentamos el proyecto final de inteligencia artificial, ¿no?"


def test_guardar_y_listar(tmp_path):
    reporte = generar_reporte(analizar(TEXTO))
    ruta = guardar_reporte(reporte, tmp_path)
    assert ruta.with_suffix(".txt").exists()
    assert listar_reportes(tmp_path) == [json.loads(json.dumps(reporte))]


def test_dos_reportes_en_el_mismo_segundo_no_se_pisan(tmp_path):
    reporte = generar_reporte(analizar(TEXTO))
    primero = guardar_reporte(reporte, tmp_path)
    segundo = guardar_reporte(reporte, tmp_path)
    assert primero != segundo
    assert len(listar_reportes(tmp_path)) == 2


def test_listar_salta_archivos_danados(tmp_path):
    (tmp_path / "reporte_20260101_000000.json").write_text("{roto", encoding="utf-8")
    assert listar_reportes(tmp_path) == []


def test_listar_sin_carpeta(tmp_path):
    assert listar_reportes(tmp_path / "no_existe") == []


def test_reporte_en_texto():
    texto = reporte_a_texto(generar_reporte(analizar(TEXTO), sesion="Prueba"))
    assert "Sesión     : Prueba" in texto
    assert "'eh': 1 vez" in texto
    assert "RECOMENDACIONES" in texto


def test_reporte_en_texto_incluye_el_detalle_del_lenguaje():
    texto = reporte_a_texto(generar_reporte(analizar(TEXTO)))
    for seccion in ("VOCABULARIO", "CLARIDAD Y COMPLEJIDAD", "COHERENCIA, ASERTIVIDAD Y TONO"):
        assert seccion in texto
    assert "VOZ Y PAUSAS" not in texto
