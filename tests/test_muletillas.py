from datos.lexico import CONECTORES_LOGICOS
from datos.muletillas import MULETILLAS_CONTEXTUALES
from nucleo.muletillas import CATEGORIA_DE_MULETILLA, analizar_muletillas, contar_muletillas
from nucleo.texto import normalizar


def contar(texto):
    return dict(contar_muletillas(normalizar(texto)))


def test_frase_larga_no_se_cuenta_tambien_como_corta():
    assert contar("O sea que no vino.") == {"o sea que": 1}


def test_palabra_comun_no_es_muletilla_dentro_de_la_frase():
    assert contar("La causa del problema es este equipo y la mano de obra.") == {}


def test_palabra_comun_es_muletilla_al_inicio_o_entre_comas():
    assert contar("Este, el equipo, bueno, ganó.") == {"este": 1, "bueno": 1}


def test_detecta_confirmaciones_con_signos():
    assert contar("Está claro, ¿no? Lo hacemos, ¿me entiendes?") == {"¿no?": 1, "¿me entiendes?": 1}


def test_vacilaciones_alargadas():
    assert contar("Eeeh, ummm, empecemos") == {"eh": 1, "um": 1}


def test_texto_limpio():
    resultado = analizar_muletillas(normalizar("El informe presenta los resultados del trimestre."), 7)
    assert resultado["total"] == 0
    assert resultado["impacto"] == "Sin muletillas detectadas"


def test_clasifica_por_frecuencia_y_categoria():
    texto = normalizar("eh " * 5 + "o sea, o sea, o sea, básicamente")
    resultado = analizar_muletillas(texto, 9)
    assert resultado["criticas"] == {"eh": 5}
    assert resultado["moderadas"] == {"o sea": 3}
    assert resultado["leves"] == {"básicamente": 1}
    assert resultado["por_categoria"]["Hesitaciones vocálicas"]["total"] == 5
    assert resultado["alta_densidad"]


def test_los_conectores_logicos_no_son_muletillas():
    assert not CONECTORES_LOGICOS & set(CATEGORIA_DE_MULETILLA)


def test_las_contextuales_existen_en_el_diccionario():
    assert MULETILLAS_CONTEXTUALES.issubset(CATEGORIA_DE_MULETILLA)
