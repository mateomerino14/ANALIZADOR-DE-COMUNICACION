from datos.ejercicios import BANCO_EJERCICIOS, RECOMENDACIONES_POR_PROBLEMA
from nucleo.analizador import analizar
from nucleo.reporte import generar_reporte, nivel_y_mensaje

MULETILLAS_VARIADAS = (
    "Bueno, eeeh, o sea que la verdad es que no sé, ¿no? Este, creo que el proyecto es importante "
    "porque, tipo, nos ayuda a mejorar. Sin embargo, hay que practicar mucho, ¿me entiendes? "
    "Básicamente es eso, y ya."
)


def categorias(reporte):
    return [recomendacion["categoria"] for recomendacion in reporte["recomendaciones"]]


def test_niveles():
    assert nivel_y_mensaje(90)[0] == "Excelente"
    assert nivel_y_mensaje(55)[0] == "Bueno"
    assert nivel_y_mensaje(0)[0] == "Requiere práctica"


def test_muchas_muletillas_distintas_generan_recomendacion():
    reporte = generar_reporte(analizar(MULETILLAS_VARIADAS))
    assert "Muletillas" in categorias(reporte)
    assert "General" not in categorias(reporte)


def test_habla_rapida_genera_recomendacion_de_velocidad():
    reporte = generar_reporte(analizar(MULETILLAS_VARIADAS, duracion_segundos=10))
    assert "Velocidad" in categorias(reporte)
    assert any(ejercicio["nombre"] == "Lectura Cronometrada" for ejercicio in reporte["ejercicios"])


def test_reporte_tiene_ejercicios_sin_repetir():
    reporte = generar_reporte(analizar(MULETILLAS_VARIADAS))
    nombres = [ejercicio["nombre"] for ejercicio in reporte["ejercicios"]]
    assert 1 <= len(nombres) <= 5
    assert len(nombres) == len(set(nombres))


def test_texto_del_reporte_es_el_original():
    reporte = generar_reporte(analizar(MULETILLAS_VARIADAS), sesion="Prueba")
    assert reporte["texto_analizado"] == MULETILLAS_VARIADAS
    assert reporte["sesion"] == "Prueba"
    assert reporte["tono"] == {"disponible": False}


def test_los_ejercicios_recomendados_existen():
    for claves in RECOMENDACIONES_POR_PROBLEMA.values():
        assert set(claves) <= set(BANCO_EJERCICIOS)
