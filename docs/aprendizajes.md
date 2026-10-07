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

## Fase 2 — Memoria persistente con PostgreSQL

**Credenciales fuera del código (`.env`):** nunca se escriben usuario/contraseña directo en el `.py` — viven en un archivo `.env` que se agrega a `.gitignore`, para que nunca se suba a GitHub. `python-dotenv` (`load_dotenv()`) lee ese archivo y lo convierte en variables de entorno del sistema; `os.getenv("NOMBRE")` las recupera desde Python.

**Cursor:** la conexión (`psycopg2.connect(...)`) es el canal abierto hacia Postgres; el cursor (`conexion.cursor()`) es quien manda las consultas y trae resultados dentro de ese canal. Todo `INSERT`/`SELECT` pasa por `cursor.execute(...)`.

**Placeholders (`%s`) en vez de armar el SQL con texto:** los valores nunca se concatenan directo al string SQL — se pasan aparte, como una tupla, y `%s` marca dónde van. Evita SQL injection (que alguien meta código SQL malicioso disfrazado de un dato normal).

**`commit()`:** Postgres no guarda los cambios de un `INSERT`/`UPDATE`/`DELETE` automáticamente — hay que confirmarlos con `conexion.commit()`. Sin eso, el cambio se pierde al cerrar la conexión. No hace falta en un `SELECT`, porque no modifica nada.

**`SERIAL`:** tipo de columna que Postgres autoincrementa solo en cada fila nueva — nunca se manda ese valor desde Python.

**`DEFAULT NOW()`:** le dice a Postgres que rellene la columna con la fecha/hora actual si no se le manda un valor, sin tener que calcularla desde Python.

**`CHECK` para restringir valores:** `CHECK (columna IN ('a', 'b'))` rechaza cualquier fila que intente guardar un valor fuera de esa lista — forma simple de validar datos a nivel de base de datos, sin necesitar un tipo `ENUM` aparte.

**`VARCHAR(n)` vs `TEXT`:** `VARCHAR(n)` para texto corto y predecible (roles, categorías — un conjunto cerrado de palabras cortas). `TEXT` para texto libre de longitud desconocida (el contenido de un mensaje de conversación).

**`fetchall()`:** `cursor.execute("SELECT...")` solo ejecuta la consulta — no devuelve nada por sí sola. `cursor.fetchall()` es quien trae las filas encontradas, como una lista de tuplas.

**Desempacar tuplas en un `for`:** `for rol, contenido in lista_de_tuplas:` reparte automáticamente cada tupla de 2 valores en dos variables separadas, sin tener que indexar manualmente (`tupla[0]`, `tupla[1]`).

**Separar el dato interno del dato que exige una librería externa:** la base de datos guarda `rol` en español (`'usuario'`/`'asistente'`), pero Ollama exige `'user'`/`'assistant'` en inglés. En vez de forzar el nombre de la librería dentro de la base de datos, se traduce con un diccionario (`mapa_roles[rol]`) justo antes de mandárselo a Ollama — así la base de datos no depende de los detalles internos de una librería específica.

## Flujo de trabajo con Git

**Orden recomendado:**
1. Al empezar a trabajar: `git status` (ver que no haya cambios sueltos) → `git pull` (traer lo nuevo).
2. Antes de un commit: `git status` de nuevo, para revisar qué se va a subir.
3. Antes de un `push`: otro `git pull` si pasó tiempo, para evitar conflictos.

**Merge commit:** aparece automáticamente cuando Git une dos historias distintas (por ejemplo, un cambio hecho en GitHub y otro hecho en local). No es un error, es la forma en que Git resuelve que ambos lados tengan commits nuevos.

**Commits atómicos:** un commit por cambio con sentido propio, con un mensaje que describa qué se corrigió o agregó. Facilita revisar el historial después, sobre todo en un repo público.

**Conventional Commits:** prefijo en el mensaje (`feat:`, `fix:`, `refactor:`, `docs:` y `chore:`) que indica el tipo de cambio de un vistazo, en minúscula por convención.

**GitHub Flow (el que usa este proyecto):** `main` siempre queda desplegable. Cada cambio va en una rama corta por tarea puntual (no por fase ni por funcionalidad completa), nombrada `tipo/nombre-corto` (ej. `feature/modo-estudio`, `fix/personalidad-zoltrak`). Al terminar, se abre un Pull Request a `main`, se revisa (Copilot code review cuando aplica), y se mergea con **squash** (condensa todos los commits de la rama en uno solo, para un historial de `main` limpio). La rama se borra después de mergeada — el historial completo (commits, diff, PR) queda disponible para siempre en los Pull Requests cerrados de GitHub, aunque la rama ya no exista.

**Git Flow (no se usa en este proyecto):** convención más formal de ramas (`main`, `develop`, `feature/*`, `release/*`, `hotfix/*`) y etiquetas de versión (`v1.0.0`, etc.), pensada para proyectos con varios colaboradores o releases formales que sí necesitan separar "lo estable" de "lo que viene". Vale la pena conocerlo porque es lo que se usa en equipos de trabajo reales y en otros proyectos (ej. el de la U con GitFlow).