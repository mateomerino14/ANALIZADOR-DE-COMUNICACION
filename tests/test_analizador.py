import pytest

from nucleo.analizador import (
    TextoInsuficiente,
    analizar,
    analizar_pausas,
    analizar_velocidad,
    calcular_mattr,
    clasificar_velocidad,
    contar_dobles_negaciones,
    indice_fernandez_huerta,
)

DISCURSO = (
    "Bueno, eh, hoy quiero hablar del reciclaje. Sin embargo, creo que no sé si todos reciclan. "
    "Es necesario separar la basura porque ayuda al planeta. Por lo tanto, debemos empezar hoy."
)


def test_texto_muy_corto():
    with pytest.raises(TextoInsuficiente):
        analizar("hola")


def test_analisis_completo_de_texto():
    resultado = analizar(DISCURSO)
    assert resultado["estadisticas"]["velocidad"] is None
    assert resultado["muletillas"]["todas"] == {"bueno": 1, "eh": 1, "no sé": 1}
    assert resultado["coherencia"]["conectores_usados"] == {"sin embargo": 1, "por lo tanto": 1}
    assert resultado["asertividad"]["expresiones_duda"] == 2
    assert resultado["asertividad"]["expresiones_asertivas"] == 2
    assert resultado["pausas"] == {}
    assert resultado["subpuntuaciones"]["pausas"] is None
    assert 0 <= resultado["puntuacion"] <= 100


@pytest.mark.parametrize("ppm, clave", [(90, "lento"), (130, "normal"), (180, "rapido"), (250, "muy_rapido")])
def test_clasificar_velocidad(ppm, clave):
    assert clasificar_velocidad(ppm)[0] == clave


def test_velocidad_con_duracion():
    estadisticas = analizar_velocidad(["palabra"] * 300, 60)
    assert estadisticas["palabras_por_min"] == 300
    assert estadisticas["velocidad"] == "muy_rapido"


def test_texto_escrito_no_penaliza_la_velocidad():
    assert analizar(DISCURSO)["subpuntuaciones"]["fluidez"] == analizar(DISCURSO, 0)["subpuntuaciones"]["fluidez"]


def test_pausas_entre_segmentos():
    segmentos = [
        {"inicio": 0.0, "fin": 2.0, "texto": "Hola"},
        {"inicio": 2.6, "fin": 4.0, "texto": "a todos"},
        {"inicio": 7.0, "fin": 8.0, "texto": "empecemos"},
    ]
    pausas = analizar_pausas(segmentos)
    assert pausas["total"] == 2
    assert pausas["largas"] == 1
    assert pausas["promedio"] == 1.8


def test_mattr_ventana():
    assert calcular_mattr(["a", "b", "a", "b"], ventana=2) == 1.0
    assert calcular_mattr(["a", "a"], ventana=5) == 0.5


def test_indice_legibilidad_acotado():
    assert indice_fernandez_huerta(1, 1) == 100
    assert indice_fernandez_huerta(4, 60) == 0


def test_doble_negacion():
    assert contar_dobles_negaciones("no quiero que no vengas") == 1


def test_la_confirmacion_no_es_doble_negacion():
    assert contar_dobles_negaciones("no sé, ¿no? es raro") == 0
