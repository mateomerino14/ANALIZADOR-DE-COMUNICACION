# EXPRESA — Analizador de comunicación

[![CI](https://github.com/mateomerino14/ANALIZADOR-DE-COMUNICACION/actions/workflows/ci.yml/badge.svg)](https://github.com/mateomerino14/ANALIZADOR-DE-COMUNICACION/actions/workflows/ci.yml)

Aplicación de escritorio que transcribe la voz con Whisper y analiza la forma de
hablar: detecta muletillas, mide la velocidad, las pausas, el vocabulario, la
claridad y el tono de voz, y genera un reporte con recomendaciones y ejercicios
para mejorar.

Proyecto semestral de Inteligencia Artificial (procesamiento de lenguaje natural).

## Equipo

Desarrollado en grupo por:

- Mateo Alejandro Merino Vidal
- Anahí Sanabria
- Leonel Zeballos Aldunate
- Ignacio Jaldin

El repositorio original del equipo es [AnahiSU/IA-pln](https://github.com/AnahiSU/IA-pln).
Este repositorio es la versión que reestructuré después de la entrega: corregí
errores del análisis, separé la lógica de la interfaz, agregué pruebas automáticas
y dejé el código con los estándares de [`reglas.md`](reglas.md).
El detalle está en [Cambios respecto a la entrega](#cambios-respecto-a-la-entrega).

## Qué analiza

| Aspecto | Cómo se mide |
|---|---|
| Muletillas | Diccionario de más de 300 expresiones en 10 categorías, con detección por contexto y similitud TF-IDF |
| Velocidad | Palabras por minuto frente al rango ideal (100–160 ppm). Solo en audio |
| Pausas | Silencios entre los segmentos que devuelve Whisper. Solo en audio |
| Vocabulario | TTR, MATTR y palabras repetidas cerca unas de otras |
| Claridad | Índice de legibilidad de Fernández Huerta y largo de las oraciones |
| Coherencia | Conectores lógicos y continuidad temática entre las dos mitades del discurso |
| Asertividad | Balance entre expresiones asertivas y de duda |
| Complejidad | Proporción de palabras largas y de oraciones compuestas |
| Tono emocional | Polaridad según palabras positivas y negativas |
| Tono de voz | Pitch, volumen, expresividad (centroide espectral) y ritmo, con librosa |

Fluidez, vocabulario, claridad, coherencia y asertividad dan una subpuntuación de 0 a 100,
y la puntuación global las pondera:
fluidez 30 %, vocabulario 20 %, claridad 20 %, coherencia 15 % y asertividad 15 %.
En audio se muestra además la subpuntuación de pausas, que no entra en la global
porque un texto escrito no la tiene.

### Detección de muletillas

1. El texto se normaliza: las vacilaciones alargadas (`eeeh`, `ummm`) se unifican
   y se conserva la puntuación que marca pausas.
2. Se buscan primero las expresiones más largas, así `o sea que` no se cuenta
   además como `o sea`.
3. Las palabras comunes como `este`, `bueno` o `tipo` solo cuentan como muletilla
   al inicio de una frase o entre comas: en *"este equipo ganó"* no lo son, en
   *"Este, el equipo ganó"* sí.
4. Cada categoría del diccionario se convierte en un documento y el discurso se
   compara con ellas por similitud coseno sobre vectores TF-IDF, lo que indica a
   qué tipo de muletilla se parece más.

## Estructura

```
ANALIZADOR-DE-COMUNICACION/
├── main.py                 Punto de entrada: interfaz o terminal
├── config.py               Umbrales, rutas y modelo de Whisper
├── nucleo/                 Lógica, sin dependencias de la interfaz
│   ├── audio.py            Lectura de audio a 16 kHz mono
│   ├── grabador.py         Grabación desde el micrófono
│   ├── transcriptor.py     Whisper: voz a texto
│   ├── texto.py            Normalización, tokens y búsqueda de frases
│   ├── muletillas.py       Detección y clasificación de muletillas
│   ├── vectorial.py        TF-IDF y similitud coseno
│   ├── analizador.py       Métricas del discurso
│   ├── puntuacion.py       Subpuntuaciones y puntuación global
│   ├── tono.py             Análisis acústico con librosa
│   ├── reporte.py          Recomendaciones y ejercicios
│   ├── almacen.py          Guardado del reporte en JSON y TXT
│   └── flujo.py            Une los pasos para audio y para texto
├── datos/
│   ├── muletillas.py       Más de 300 muletillas en 10 categorías
│   ├── lexico.py           Stopwords, conectores y palabras de duda, asertivas y de tono
│   └── ejercicios.py       Banco de ejercicios y cuándo recomendar cada uno
├── interfaz/               Tkinter
│   ├── app.py              Ventana principal y pestañas de audio y texto
│   ├── historial.py        Pestaña de reportes guardados
│   ├── vista_reporte.py    Reporte completo, compartido por ambas pestañas
│   ├── componentes.py      Medidor, barras, tarjetas y panel desplazable
│   └── tema.py             Colores y fuentes
├── tests/
├── reportes/               Reportes generados (no se suben)
├── temporal/               Última grabación del micrófono (no se sube)
└── reglas.md               Estándares de ramas, commits y código
```

## Instalación

Requiere Python 3.10 o superior.

```bash
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux / macOS
pip install -r requirements.txt
```

La primera transcripción descarga el modelo de Whisper (`base`, unos 140 MB).

Según el sistema hace falta además:

- **Linux:** `sudo apt install portaudio19-dev python3-tk`
- **macOS:** `brew install portaudio`
- **Archivos .m4a:** [ffmpeg](https://ffmpeg.org/download.html) en el PATH. Los
  `.wav`, `.mp3`, `.ogg` y `.flac` se leen sin ffmpeg.

## Ejecución

```bash
python main.py                          # interfaz gráfica
python main.py --texto "Bueno, eh..."   # analiza un texto en la terminal
python main.py --audio charla.mp3       # transcribe y analiza un audio en la terminal
```

El modelo se cambia con la variable `EXPRESA_MODELO` (`tiny`, `base`, `small`,
`medium`, `large`). Los más grandes transcriben mejor las muletillas pero tardan más:

```bash
EXPRESA_MODELO=small python main.py
```

Cada análisis queda en `reportes/` como JSON, que alimenta la pestaña de
historial, y como TXT con el mismo detalle que la pantalla, para leerlo o imprimirlo.

## Pruebas

```bash
pytest
ruff check .
```

Las pruebas no necesitan Whisper ni micrófono: el flujo de audio se prueba con
voz sintética y un transcriptor falso. GitHub Actions ejecuta el lint y las pruebas
en Python 3.10 y 3.12 en cada push y Pull Request.

## Cambios respecto a la entrega

**Errores corregidos**

- La grabación fallaba al guardar: se pedía el tamaño del archivo antes de escribirlo.
- Los audios que no estaban a 16 kHz se transcribían mal porque llegaban a Whisper
  sin remuestrear; ahora todo el audio se lleva a 16 kHz mono antes de usarlo.
- Las recomendaciones y ejercicios de velocidad nunca aparecían: se buscaba
  `"rapido"` en la etiqueta `"Rápido"`, que lleva tilde.
- Las expresiones de duda y asertividad de varias palabras (`creo que`, `sin duda`)
  se comparaban con palabras sueltas y nunca se detectaban.
- Las muletillas contenidas en otras se contaban dos veces (`o sea que` y `o sea`),
  y las que empiezan con signo (`¿no?`) no se detectaban.
- Palabras comunes como `causa`, `mano` o `listo` se marcaban como muletillas en
  cualquier posición.
- `por lo tanto` y `en consecuencia` sumaban como muletilla y a la vez como conector
  lógico que mejora la coherencia.
- El IDF podía dar valores negativos; ahora es suavizado.
- En el análisis de texto se inventaba una duración y la velocidad salía siempre
  "Normal"; ahora no se mide porque un texto escrito no tiene duración real.
- Un discurso con muchas muletillas distintas, ninguna repetida tres veces,
  recibía "Excelente comunicación"; ahora se recomienda según la densidad total.
- Si fallaba el análisis, la interfaz lanzaba otro error al intentar mostrarlo.
- Una confirmación como `¿no?` se contaba como doble negación.

**Estructura y calidad**

- Se quitó del repositorio el entorno virtual, cachés, audios y reportes de prueba.
- Se eliminó la descarga automática de ffmpeg desde internet durante la ejecución.
- Lógica separada de la interfaz en `nucleo/`, utilizable también desde la terminal.
- La vista del reporte se comparte entre la pestaña de análisis y el historial, y muestra
  todos los datos que se calculan: vocabulario, claridad, complejidad, coherencia,
  asertividad, tono emocional, acústica y el detalle de cada pausa. El TXT tiene el mismo detalle.
- Rutas con `pathlib` relativas al proyecto, sin depender de la carpeta desde donde
  se ejecuta.
- Valores mágicos movidos a constantes con nombre, sin código comentado ni impresiones
  de depuración.
- 50 pruebas con pytest, lint con ruff e integración continua en GitHub Actions.
