import re

VOCALES = set("aeiouáéíóúü")
FIN_DE_ORACION = r"[.!?]+"

# Whisper escribe las vacilaciones alargadas de muchas formas: eeeh, aaah, ummm
VACILACIONES_ALARGADAS = (
    (r"\be{2,}h*\b|\beh+\b", "eh"),
    (r"\ba{2,}h*\b|\bah+\b", "ah"),
    (r"\bu+m+\b", "um"),
    (r"\be+m+\b", "em"),
    (r"\bm{2,}\b", "mm"),
)


# Conserva la puntuacion que indica inicio de frase o pausa, necesaria para las muletillas
def normalizar(texto):
    texto = texto.lower()
    for patron, reemplazo in VACILACIONES_ALARGADAS:
        texto = re.sub(patron, reemplazo, texto)
    texto = re.sub(r"[^\w\s¿?¡!.,;:\-]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def tokenizar(texto):
    return re.findall(r"\w+", texto.lower())


def oraciones(texto):
    return [oracion.strip() for oracion in re.split(FIN_DE_ORACION, texto) if oracion.strip()]


# Expresion que encuentra la frase completa, sin tomar pedazos de otras palabras
def patron_frase(frase):
    partes = [re.escape(parte) for parte in frase.split()]
    return re.compile(r"(?<!\w)" + r"\s+".join(partes) + r"(?!\w)")


# Las frases largas van primero, asi "no sé si" no se cuenta ademas como "no sé"
def contar_frases(frases, texto):
    ocupado = [False] * len(texto)
    conteo = {}
    for frase in sorted(frases, key=lambda frase: (-len(frase.split()), -len(frase))):
        for coincidencia in patron_frase(frase).finditer(texto):
            inicio, fin = coincidencia.span()
            if any(ocupado[inicio:fin]):
                continue
            ocupado[inicio:fin] = [True] * (fin - inicio)
            conteo[frase] = conteo.get(frase, 0) + 1
    return conteo


# Aproximacion por grupos vocalicos, suficiente para el indice de legibilidad
def contar_silabas(palabra):
    silabas = 0
    vocal_anterior = False
    for letra in palabra.lower():
        es_vocal = letra in VOCALES
        if es_vocal and not vocal_anterior:
            silabas += 1
        vocal_anterior = es_vocal
    return max(1, silabas)
