# Aprendizajes — Zoltrak

Notas de estudio sobre los conceptos de programación practicados en cada fase. No es documentación del proyecto en sí (eso está en `Zoltrak proyecto.md`), es un resumen de los porqués técnicos.

## Fase 1 — Conversación con Ollama

**Rol `system` en el historial:** el primer mensaje de `historial` define personalidad y restricciones, y se manda en cada llamada junto con el resto de la conversación. El modelo no "recuerda" nada por sí solo entre llamadas; toda la memoria de sesión existe porque se reenvía la lista completa cada vez.

**Por qué se acumula en una lista y no se manda solo el último mensaje:** sin el historial completo, el modelo no tendría contexto de lo que se habló antes en esa sesión.

## Fase 1.5 — Acciones sobre el sistema

**`os.startfile()`:** en Windows, abre lo que el sistema asocie a esa ruta o URL, así que sirve igual para `.lnk`, carpetas y direcciones web, sin lógica distinta para cada caso.

**Rutas con `r"..."` (raw strings):** en Python, `\` dentro de un string normal se interpreta como inicio de un carácter especial (`\n`, `\t`). Las rutas de Windows usan `\` como separador, así que sin el prefijo `r`, una ruta como `C:\nueva` se rompe. `r"..."` le dice a Python que tome el texto literal, sin interpretar el `\`.

**`try/except` alrededor de acciones externas:** cualquier interacción con el sistema operativo o una red puede fallar por razones fuera de tu control (archivo movido, Ollama apagado). Encerrar esa llamada en `try/except` evita que un error externo tumbe todo el programa, y te permite decidir qué hacer cuando pasa.

**`continue` dentro de un `while True`:** corta la iteración actual y salta directo a la siguiente vuelta del bucle, sin ejecutar el código que queda debajo. Se usa cuando ya se resolvió lo que había que hacer en ese turno (una acción, un error manejado) y no tiene sentido seguir con el resto del cuerpo del bucle.

**`break` vs `continue`:** `break` sale del bucle por completo. `continue` solo salta a la siguiente vuelta. Confundirlos es un error común: usar `break` donde se necesita `continue` saca al usuario del programa quiere o no.

**Tres diccionarios separados y unidos con `.update()`:** separar `apps`, `paginas_web` y `carpetas` mantiene el código legible para quien lo lee (agrupación por tipo). `diccionario_a.update(diccionario_b)` mete las claves de `diccionario_b` dentro de `diccionario_a`, sin borrar lo que ya tenía. Se usa para tener una sola estructura (`todo`) donde buscar, sin sacrificar la organización de las tres originales.

**`for...else`:** el bloque `else` de un `for` se ejecuta solo si el bucle termina sin haber hecho `break`. Es la forma limpia de decir "recorrí toda la lista y no encontré nada", sin necesitar una variable bandera aparte.

**`.lower()` y `.strip()`:** `.lower()` normaliza mayúsculas/minúsculas para comparar texto sin que "Chao" y "chao" se traten distinto. `.strip()` quita espacios sobrantes al inicio y final, para que " chao " también sea reconocido.

**Fuzzy matching (`rapidfuzz`):** compara qué tan parecidas son dos cadenas de texto y devuelve un puntaje (0 a 100). Sirve para tolerar errores de tecleo, pero solo tiene sentido comparando palabras sueltas contra palabras sueltas (como nombres de apps); comparar una palabra contra una frase larga casi nunca da un puntaje alto, aunque el texto tenga sentido para una persona.

## Flujo de trabajo con Git

**Orden recomendado:**
1. Al empezar a trabajar: `git status` (ver que no haya cambios sueltos) → `git pull` (traer lo nuevo).
2. Antes de un commit: `git status` de nuevo, para revisar qué se va a subir.
3. Antes de un `push`: otro `git pull` si pasó tiempo, para evitar conflictos.

**Merge commit:** aparece automáticamente cuando Git une dos historias distintas (por ejemplo, un cambio hecho en GitHub y otro hecho en local). No es un error, es la forma en que Git resuelve que ambos lados tengan commits nuevos.

**Commits atómicos:** un commit por cambio con sentido propio, con un mensaje que describa qué se corrigió o agregó. Facilita revisar el historial después, sobre todo en un repo público.

**Git Flow (no se usa en este proyecto):** es una convención más formal de ramas (`main`, `develop`, `feature/*`, `release/*`, `hotfix/*`) y etiquetas de versión (`v1.0.0`, etc.), pensada para proyectos con varios colaboradores o releases formales. En Zoltrak se trabaja directo sobre `main`, sin ramas, porque el proyecto es pequeño y de una sola persona, y no lo justifica. Vale la pena conocerlo porque es lo que se usa en equipos de trabajo reales.