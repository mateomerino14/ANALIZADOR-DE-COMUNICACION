HESITACIONES = {
    "eh", "ehh", "ehhh", "ehhhh",
    "ah", "ahh", "ahhh",
    "um", "umm", "ummm",
    "mm", "mmm", "mmmm",
    "hmm", "hmmm",
    "uh", "uhh",
    "er", "err",
    "am", "amm",
    "em", "emm", "emmm",
    "este",        # Muy común en México y Cono Sur
    "esto",
    "eeeh", "aaah", "uuuh",
    "nn", "nnn",
    "bue...", "ento...",
}

CONECTORES_VACIOS = {
    "o sea",
    "o sea que",
    "o sea como",
    "o sea pues",
    "o sea así",
    "es decir",
    "es decir que",
    "es que",
    "o sea es que",
    "quiero decir",
    "lo que quiero decir",
    "me refiero",
    "me refiero a que",
    "en otras palabras",
    "dicho de otra manera",
    "o sea de alguna manera",
}

INICIO_TURNO = {
    "bueno",
    "bueno pues",
    "bueno entonces",
    "pues",
    "pues bien",
    "pues mira",
    "pues nada",
    "pues sí",
    "pues no",
    "pues eso",
    "entonces",
    "entonces pues",
    "a ver",
    "veamos",
    "vamos a ver",
    "mira",
    "mire",
    "miren",
    "oye",
    "oiga",
    "escucha",
    "fíjate",
    "fíjese",
    "imagínate",
    "imagínese",
    "resulta que",
    "resulta ser que",
    "la verdad",
    "la verdad es que",
    "la verdad sea dicha",
    "sinceramente",
    "honestamente",
    "francamente",
    "en serio",
    "en serio te digo",
    "te juro",
    "te lo juro",
    "de verdad",
    "de verdad que",
}

CONFIRMACION = {
    "¿no?",
    "¿no es así?",
    "¿verdad?",
    "¿verdad que sí?",
    "¿cierto?",
    "¿entiendes?",
    "¿me entiendes?",
    "¿entendiste?",
    "¿sabes?",
    "¿sabes lo que te digo?",
    "¿cachai?",           # Chile
    "¿viste?",            # Argentina, Uruguay
    "¿me explico?",
    "¿se entiende?",
    "¿sí o no?",
    "¿ok?",
    "¿está bien?",
    "¿bien?",
    "¿sí?",
    "¿no sé?",
    "¿ves?",
    "¿comprendes?",
}

INTENSIFICADORES = {
    "básicamente",
    "literalmente",
    "obviamente",
    "claramente",
    "evidentemente",
    "efectivamente",
    "realmente",
    "en realidad",
    "totalmente",
    "absolutamente",
    "completamente",
    "perfectamente",
    "exactamente",
    "precisamente",
    "simplemente",
    "meramente",
    "puramente",
    "francamente",
    "definitivamente",
    "indudablemente",
    "innegablemente",
    "prácticamente",
    "virtualmente",
    "esencialmente",
    "fundamentalmente",
    "genuinamente",
    "increíblemente",
}

APROXIMADORES = {
    "como",
    "como que",
    "tipo",
    "tipo que",
    "más o menos",
    "o algo así",
    "o algo por el estilo",
    "o lo que sea",
    "o lo que fuere",
    "o cosas así",
    "y eso",
    "y tal",
    "y tal y cual",
    "y demás",
    "etcétera",
    "y todo eso",
    "y todo lo demás",
    "y cosas de esas",
    "por así decir",
    "por así decirlo",
    "de alguna manera",
    "de algún modo",
    "en cierto modo",
    "en cierta medida",
    "de alguna forma",
    "algo así como",
    "una especie de",
    "una suerte de",
    "digamos",
    "digamos que",
    "podríamos decir",
    "podría decirse",
    "no sé",
    "no sé cómo decirte",
    "no sé cómo explicarlo",
}

MARCADORES_REDUNDANTES = {
    "al final",
    "al final del día",
    "a fin de cuentas",
    "en definitiva",
    "en resumen",
    "en conclusión",
    "en suma",
    "en fin",
    "total",
    "total que",
    "en pocas palabras",
    "dicho esto",
    "dicho lo cual",
    "con todo",
    "con todo y eso",
    "de todas formas",
    "de todas maneras",
    "de todas fiestas",   # coloquial
    "de todos modos",
    "sea como sea",
    "como sea",
    "sea como fuere",
    "en todo caso",
    "en cualquier caso",
    "pase lo que pase",
    "por otro lado",
    "por otra parte",
    "por un lado",
    "por una parte",
    "de hecho",
    "de hecho que",
    "incluso",
    "incluso así",
    "así que",
    "así pues",
    "por consiguiente",
}

REGIONALISMOS = {
    # México
    "güey", "wey", "cuate", "órale", "ándale",
    "híjole", "chido", "chida", "neta", "nel",
    "simon", "simón", "chale", "ps", "ps sí",

    # Colombia
    "listo", "listo pues", "parcero", "venga",
    "venga pues", "¿si me entiende?", "¿cierto?",
    "¿no ve?", "marica", "gonorrea",

    # Argentina / Uruguay
    "boludo", "che", "dale", "bárbaro", "¿viste?",
    "¿ta?", "bue", "mirá vos", "¿entendés?",

    # Chile
    "po", "po sí", "¿cachai?", "weon", "puta",
    "ya po", "sí po", "no po",

    # Venezuela
    "chamo", "chama", "pana", "coño", "verga",
    "¿me entiendes?", "vale", "¿ok?",

    # Perú
    "causa", "pe", "pues pe", "oye pe",

    # España
    "tío", "tía", "joder", "ostia",
    "macho", "¿sabes?", "¿eh?",

    # General latinoamericano
    "mano", "mae",   # Costa Rica
    "oe", "huevón",  # varios países
}

CLICHES = {
    "al día de hoy",
    "a día de hoy",
    "en el día de hoy",
    "en estos momentos",
    "en este momento",
    "en el momento actual",
    "actualmente en el día de hoy",
    "hoy en día",
    "a estas alturas",
    "a estas alturas del partido",
    "en el ámbito de",
    "en el marco de",
    "en el contexto de",
    "a nivel de",
    "a nivel general",
    "desde el punto de vista",
    "desde mi punto de vista",
    "desde mi perspectiva",
    "en mi opinión personal",
    "personalmente creo",
    "yo pienso que",
    "yo creo que",
    "en lo personal",
    "para mí personalmente",
    "a grandes rasgos",
    "en líneas generales",
    "grosso modo",
    "mutatis mutandis",
    "sin más ni más",
    "sin más preámbulos",
    "dicho esto",
    "habiendo dicho esto",
    "con esto en mente",
    "teniendo en cuenta lo anterior",
    "como bien sabemos",
    "como todos sabemos",
    "como es bien sabido",
    "no hace falta decir",
    "huelga decir",
    "por supuesto",
    "como no",
    "lógicamente",
    "naturalmente",
}

REPETIDORES = {
    "y ya",
    "y nada",
    "y nada más",
    "y eso es todo",
    "y punto",
    "y listo",
    "y ya está",
    "y ya estuvo",   # México
    "y ya fue",
    "nada más que",
    "no más que",
    "o sea nada",
    "y demás cosas",
    "y así sucesivamente",
    "y así",
    "y así nos fue",
    "así que nada",
    "pues nada",
    "pues eso",
    "pues ya",
    "pues sí",
    "no, nada",
}


CATEGORIAS_MULETILLAS = {
    "Hesitaciones vocálicas": HESITACIONES,
    "Conectores vacíos": CONECTORES_VACIOS,
    "Marcadores de inicio": INICIO_TURNO,
    "Búsqueda de confirmación": CONFIRMACION,
    "Intensificadores vacíos": INTENSIFICADORES,
    "Aproximadores y vagueadores": APROXIMADORES,
    "Marcadores redundantes": MARCADORES_REDUNDANTES,
    "Regionalismos y coloquialismos": REGIONALISMOS,
    "Frases cliché": CLICHES,
    "Repetidores y continuadores": REPETIDORES,
}

# Palabras comunes que solo son muletilla al inicio de una frase o entre comas
MULETILLAS_CONTEXTUALES = {
    "bueno", "pues", "este", "esto", "como", "total", "mira",
    "entonces", "tipo", "listo", "vale", "dale", "venga", "causa", "mano", "pana",
    "incluso", "escucha", "che", "pe", "po", "mae", "macho", "realmente",
    "simplemente", "exactamente", "naturalmente", "en realidad", "de hecho",
}

DESCRIPCION_CATEGORIAS = {
    "Hesitaciones vocálicas":
        "Sonidos de relleno que emitimos mientras buscamos las palabras. "
        "Una pausa en silencio es más profesional que 'eh' o 'um'.",
    "Conectores vacíos":
        "'O sea' y 'es decir' deberían introducir una aclaración real. "
        "Si no aclaran nada, son muletillas.",
    "Marcadores de inicio":
        "Palabras como 'bueno' o 'pues' al inicio de cada frase "
        "generan una cadencia monótona y previsible.",
    "Búsqueda de confirmación":
        "Buscar constantemente validación ('¿no?', '¿verdad?') "
        "puede transmitir inseguridad al interlocutor.",
    "Intensificadores vacíos":
        "'Literalmente' y 'básicamente' han perdido su fuerza por uso excesivo. "
        "Usarlos menos los hace más efectivos.",
    "Aproximadores y vagueadores":
        "'Como', 'tipo' y 'más o menos' hacen el lenguaje impreciso. "
        "La precisión transmite autoridad y claridad.",
    "Marcadores redundantes":
        "Frases de cierre como 'al final del día' o 'en definitiva' "
        "pierden impacto si se repiten constantemente.",
    "Regionalismos y coloquialismos":
        "Válidos en contextos informales, pero pueden restar "
        "credibilidad en presentaciones formales.",
    "Frases cliché":
        "Expresiones tan usadas que ya no comunican nada nuevo. "
        "Busca formas más originales de expresar las mismas ideas.",
    "Repetidores y continuadores":
        "Frases de cierre vacías ('y ya', 'pues nada') que alargan "
        "el discurso sin agregar valor.",
}
