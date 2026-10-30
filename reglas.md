# Estándares de desarrollo

EXPRESA — convenciones de ramas, commits y codificación.

---

## ESTÁNDARES DE RAMAS

| Rama | Uso |
|---|---|
| `main` | Versión estable |
| `develop` | Integración de los cambios terminados |
| `feature/<tema>` | Nueva funcionalidad o reestructuración, en `snake_case` (ej. `feature/deteccion_muletillas`) |
| `fix/<tema>` | Corrección puntual sobre `develop` |
| `docs/<tema>` | Cambios solo de documentación |
| `chore/<tema>` | Configuración, dependencias o integración continua |

### Flujo

1. Cada cambio se desarrolla en su propia rama, creada desde `develop`.
2. Al terminarlo se abre un Pull Request hacia `develop`. Las pruebas de GitHub Actions deben pasar antes del merge.
3. Cuando `develop` reúne una versión completa, se abre un Pull Request de `develop` hacia `main`.

---

## ESTÁNDARES DE COMMITS

Se utiliza la convención Conventional Commits.

| Tipo | Uso |
|---|---|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de errores |
| `style` | Cambios visuales o de formato sin afectar la lógica |
| `refactor` | Reestructuración de código sin modificar el comportamiento |
| `docs` | Documentación |
| `test` | Creación o actualización de pruebas |
| `chore` | Configuración, dependencias y CI |

### Formato

```
<tipo>: <Descripción>
```

```
feat: Detecta muletillas por contexto al inicio de frase o entre comas
fix: Remuestrea el audio a 16 kHz antes de transcribirlo
test: Agrega pruebas del flujo de audio con un transcriptor falso
```

### Reglas

- Los mensajes comienzan con mayúscula después del prefijo.
- Describir la funcionalidad, no los archivos modificados.
- Un commit representa una única funcionalidad, corrección o mejora.
- Evitar mensajes genéricos: `cambios`, `correcciones`, `actualización`, `prueba`.

---

## ESTÁNDARES DE CODIFICACIÓN

### Idioma

- Variables, funciones, clases y módulos en español, sin tildes ni `ñ` en los nombres (`tamano`, `pestana`).
- Los textos visibles para el usuario van en español correcto, con tildes.

### Comentarios

- No se usan docstrings. Cuando una función necesita explicación lleva un comentario
  de una línea encima, que dice el porqué y no repite lo que el código ya dice.

```python
# Las frases largas van primero, asi "no sé si" no se cuenta ademas como "no sé"
def contar_frases(frases, texto):
```

- Eliminar código comentado e impresiones de depuración antes de hacer commit.

### Sintaxis

El formato se valida con ruff (`ruff check .`), configurado en `pyproject.toml`.

**No usar el operador ternario en la lógica de control**; se prefieren bloques
`if`/`else` explícitos. Se admite solo para valores simples de presentación.

```python
# Correcto
if similitud > UMBRAL_SIMILITUD_MULETILLAS:
    diagnostico = "Alta densidad de muletillas"
else:
    diagnostico = "Discurso limpio"
```

**Evitar valores mágicos**; los umbrales de análisis van en `config.py` y las
constantes propias de un módulo, en mayúsculas al inicio del archivo.

```python
PPM_LENTO = 100
PAUSA_LARGA_SEG = 2.0
```

**Rutas con `pathlib`**, relativas a la raíz del proyecto (`config.RAIZ`).

**Las dependencias pesadas** (Whisper, sounddevice, librosa) se importan dentro de
la función que las usa, para que el análisis de texto y las pruebas no las exijan.

### Organización

| Carpeta | Contenido |
|---|---|
| `nucleo/` | Lógica del análisis. No importa nada de `interfaz/` |
| `datos/` | Diccionarios y bancos de ejercicios, sin lógica |
| `interfaz/` | Ventanas y componentes de Tkinter |
| `tests/` | Pruebas de `nucleo/`, en `test_<modulo>.py` |

---

## PRUEBAS

- `pytest` debe pasar antes de cada Pull Request.
- Las pruebas no dependen de Whisper, del micrófono ni de internet: se usan audios
  sintéticos y un transcriptor falso.
- Cada error corregido lleva una prueba que lo reproduce.
