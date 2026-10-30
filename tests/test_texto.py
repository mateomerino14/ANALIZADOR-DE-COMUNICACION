from nucleo.texto import contar_frases, contar_silabas, normalizar, oraciones, tokenizar


def test_normalizar_unifica_vacilaciones_alargadas():
    assert normalizar("Eeeeh, ummm, aaah y mmm") == "eh, um, ah y mm"


def test_normalizar_no_toca_la_conjuncion_e():
    assert normalizar("Padres e hijos") == "padres e hijos"


def test_normalizar_conserva_puntuacion_de_pausa():
    assert normalizar("Bueno… ¿no? «Claro»") == "bueno ¿no? claro"


def test_tokenizar_ignora_puntuacion():
    assert tokenizar("¿Qué tal?, bien.") == ["qué", "tal", "bien"]


def test_oraciones():
    assert oraciones("Hola. ¿Cómo estás? Bien!") == ["Hola", "¿Cómo estás", "Bien"]


def test_contar_frases_no_toma_pedazos_de_palabras():
    assert contar_frases({"este"}, "este es el oeste") == {"este": 1}
    assert contar_frases({"o sea"}, "o  sea, o sea") == {"o sea": 2}
    assert contar_frases({"¿no?"}, "es así, ¿no?") == {"¿no?": 1}


def test_contar_frases_omite_las_ausentes():
    assert contar_frases({"creo que", "tal vez"}, "creo que sí, creo que no") == {"creo que": 2}


def test_contar_silabas():
    assert contar_silabas("casa") == 2
    assert contar_silabas("murciélago") == 4
    assert contar_silabas("y") == 1


def test_contar_frases_no_cuenta_dos_veces_la_frase_contenida():
    assert contar_frases({"no sé", "no sé si"}, "no sé si ir, no sé") == {"no sé si": 1, "no sé": 1}
