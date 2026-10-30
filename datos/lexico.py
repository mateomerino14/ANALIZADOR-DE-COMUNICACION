STOPWORDS = {
    "a", "al", "ante", "aun", "aunque", "bajo", "bien", "cabe", "como", "con", "contra",
    "cuando", "cuyo", "de", "del", "desde", "donde", "durante", "el", "él", "ella",
    "ellas", "ellos", "en", "entre", "era", "es", "esa", "ese", "eso", "esta", "este",
    "esto", "fue", "ha", "han", "hacia", "hasta", "hay", "la", "las", "le", "les", "lo",
    "los", "mas", "más", "me", "mediante", "mi", "mis", "muy", "ni", "no", "nos", "o",
    "para", "pero", "por", "porque", "pues", "que", "quien", "se", "según", "ser", "si",
    "sin", "sino", "sobre", "son", "su", "sus", "también", "te", "tiene", "tras", "tu",
    "tus", "un", "una", "versus", "vía", "y", "ya",
}

CONECTORES_LOGICOS = {
    "sin embargo", "no obstante", "aunque", "a pesar de", "por lo tanto",
    "en consecuencia", "dado que", "puesto que", "debido a", "ya que",
    "con el fin de", "para que", "de modo que", "de manera que",
    "mientras que", "siempre que", "a menos que", "salvo que",
}

# Palabras que vuelven compuesta a una oracion
SUBORDINANTES = {"que", "aunque", "porque", "cuando", "si", "donde"}

PALABRAS_POSITIVAS = {
    "bien", "bueno", "buena", "excelente", "genial", "fantástico", "maravilloso",
    "positivo", "éxito", "logro", "avance", "mejora", "beneficio", "oportunidad",
    "solución", "efectivo", "eficiente", "claro", "seguro", "confianza",
    "alegre", "feliz", "satisfecho", "orgulloso", "motivado", "inspirado",
    "innovador", "creativo", "productivo", "valioso", "importante", "necesario",
    "útil", "correcto", "adecuado", "apropiado", "conveniente", "favorable",
}

PALABRAS_NEGATIVAS = {
    "mal", "malo", "mala", "terrible", "horrible", "pésimo", "negativo",
    "problema", "error", "fallo", "fracaso", "dificultad", "obstáculo",
    "preocupante", "grave", "crítico", "urgente", "difícil", "complicado",
    "imposible", "inútil", "incorrecto", "inadecuado", "inapropiado",
    "insuficiente", "deficiente", "escaso", "limitado", "incompleto",
    "confuso", "ambiguo", "vago", "impreciso", "incertidumbre", "riesgo",
}

EXPRESIONES_DUDA = {
    "quizás", "quizá", "tal vez", "acaso", "puede que", "puede ser",
    "no sé", "creo que", "me parece", "supongo", "imagino", "asumo",
    "probablemente", "posiblemente", "seguramente", "a lo mejor", "no estoy seguro",
    "no sé si", "podría ser", "parece que",
}

EXPRESIONES_ASERTIVAS = {
    "definitivamente", "sin duda", "claramente", "es evidente", "es obvio",
    "estoy convencido", "es necesario", "es fundamental", "es esencial",
    "hay que", "debemos", "es imprescindible", "sin lugar a dudas",
    "afirmo", "aseguro", "garantizo", "confirmo", "demuestro",
}
