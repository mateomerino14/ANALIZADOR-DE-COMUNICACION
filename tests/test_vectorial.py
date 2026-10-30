import numpy as np

from nucleo.vectorial import ModeloVectorial, calcular_idf, construir_vocabulario, similitud_coseno


def test_idf_suavizado_nunca_es_negativo():
    corpus = ["eh um", "eh o sea", "eh tipo"]
    idf = calcular_idf(corpus, construir_vocabulario(corpus))
    assert (idf > 0).all()


def test_similitud_coseno():
    assert similitud_coseno(np.array([1.0, 0.0]), np.array([2.0, 0.0])) == 1.0
    assert similitud_coseno(np.array([1.0, 0.0]), np.array([0.0, 3.0])) == 0.0
    assert similitud_coseno(np.zeros(2), np.array([1.0, 1.0])) == 0.0


def test_modelo_encuentra_el_documento_mas_cercano():
    modelo = ModeloVectorial({"vacilaciones": "eh um ah", "confirmacion": "verdad cierto sabes"})
    nombre, similitud = modelo.mas_cercano("eh, eh, um, ¿verdad?")
    assert nombre == "vacilaciones"
    assert 0 < similitud <= 1
