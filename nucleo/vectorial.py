import math

import numpy as np

from nucleo.texto import tokenizar


def construir_vocabulario(corpus):
    terminos = sorted({token for documento in corpus for token in tokenizar(documento)})
    return {termino: indice for indice, termino in enumerate(terminos)}


def frecuencia_terminos(texto, vocabulario):
    vector = np.zeros(len(vocabulario))
    tokens = tokenizar(texto)
    if not tokens:
        return vector
    for token in tokens:
        if token in vocabulario:
            vector[vocabulario[token]] += 1
    return vector / len(tokens)


# IDF suavizado: nunca es negativo aunque el termino aparezca en todos los documentos
def calcular_idf(corpus, vocabulario):
    documentos = len(corpus)
    apariciones = np.zeros(len(vocabulario))
    for documento in corpus:
        for token in set(tokenizar(documento)):
            apariciones[vocabulario[token]] += 1
    return np.array([math.log((1 + documentos) / (1 + df)) + 1 for df in apariciones])


def vectorizar(texto, vocabulario, idf):
    return frecuencia_terminos(texto, vocabulario) * idf


def similitud_coseno(vector_a, vector_b):
    norma = np.linalg.norm(vector_a) * np.linalg.norm(vector_b)
    if norma == 0:
        return 0.0
    return float(np.dot(vector_a, vector_b) / norma)


class ModeloVectorial:
    def __init__(self, documentos):
        self.nombres = list(documentos)
        corpus = list(documentos.values())
        self.vocabulario = construir_vocabulario(corpus)
        self.idf = calcular_idf(corpus, self.vocabulario)
        self.matriz = [vectorizar(documento, self.vocabulario, self.idf) for documento in corpus]

    # Devuelve el documento mas parecido al texto y su similitud
    def mas_cercano(self, texto):
        vector = vectorizar(texto, self.vocabulario, self.idf)
        similitudes = [similitud_coseno(vector, fila) for fila in self.matriz]
        indice = int(np.argmax(similitudes))
        return self.nombres[indice], similitudes[indice]
