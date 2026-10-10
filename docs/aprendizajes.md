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

## Fase 2.5 — Leer correo con la API de Gmail (en progreso)

Cubre la autenticación, la búsqueda, la lectura de cada correo, el manejo de errores y la conexión con `main.py`. Falta el resumen con Ollama, que va en su propia rama (`feature/resumen-correo`); cuando esté, se agrega aquí.

### Conceptos de API y autenticación

**API:** puerta que un servicio deja abierta para usarlo desde código. Con Ollama ya se hacía (mandar un mensaje, recibir una respuesta); con Gmail es igual, pero Google necesita asegurarse de que el usuario le dio permiso al programa para leer su correo. De ahí salen los tokens.

**Archivo `.json`:** archivo de texto con datos organizados como un diccionario de Python (`{"nombre": "Jose"}`). `credentials.json` y `token.json` no son código, son datos guardados en ese formato.

**OAuth (analogía del hotel):** el programa es un mensajero, el usuario es el huésped y Google es la recepción. El mensajero nunca recibe la contraseña; recepción le pregunta al huésped si autoriza un acceso limitado, y si dice que sí, le entrega una tarjeta de acceso. Esa tarjeta es el token.

**`credentials.json` vs `token.json`:**
- `credentials.json` (se descarga de Google Cloud Console) identifica a **la aplicación** (`zoltrak-desktop`). Se crea una vez y no cambia.
- `token.json` es el permiso que Google le da a **la persona**, tras aceptar en el navegador. Lo genera el propio programa la primera vez que se hace login; no se crea a mano ni se descarga.

**Access token vs refresh token:** el *access token* es la tarjeta que se usa en cada petición y dura cerca de una hora (para que, si alguien lo roba, le sirva poco). El *refresh token* sirve para pedir un access token nuevo sin molestar al usuario. En modo Testing, Google invalida el refresh token a los 7 días y hay que hacer login de nuevo.

**Scope (alcance) `gmail.readonly`:** declara qué puede hacer el programa. Con solo lectura, Zoltrak no puede marcar correos como leídos, enviar ni borrar. Un correo "no leído" sigue así hasta que el usuario lo abre en Gmail. Si el permiso no se marca en la pantalla de Google, el token se crea sin él y las peticiones fallan después.

**Qué hace cada librería:**
- `google-auth-oauthlib`: el login con navegador (`InstalledAppFlow`).
- `google-auth`: representa las credenciales y sabe renovarlas (`Credentials`, `Request`).
- `google-api-python-client`: con credenciales válidas, construye el objeto con el que se le piden cosas a Gmail (`build`).

**Los tres casos del token, y por qué son un solo camino de código:** el token puede (1) existir y ser válido, (2) existir pero haber caducado, con refresh token, o (3) no existir o tener el refresh token muerto. Los casos "no existe" y "refresh token muerto" terminan en lo mismo: el login completo con navegador. El programa revisa de lo más barato a lo más molesto: cargar el archivo, ver si es válido, renovar en silencio, y solo si nada funcionó, login completo. El login es el último recurso, no el primer caso a revisar.

**Dos órdenes distintos:** el orden en que se *construye* (primero el login completo, porque genera `token.json` y permite probar lo demás) no es el orden en que el programa *revisa* al ejecutarse.

**Guardar el token solo cuando cambió algo:** `token.json` se reescribe después de una renovación o de un login nuevo. Si las credenciales ya eran válidas, no hay nada nuevo que guardar.

### Python aplicado a esta fase

**Rutas relativas al archivo, no a la terminal:** `os.path.join(os.path.dirname(__file__), 'credentials.json')` construye la ruta a partir de la carpeta donde vive el `.py`, así funciona igual sin importar desde qué carpeta se ejecute el programa. `os.path.join` une las partes sin escribir `\` a mano.

**Variable local vs `global`:** `creds` debe nacer dentro de la función (`creds = None` como primera línea). Con `global`, la variable sobrevive entre llamadas y la función ya no parte de cero cada vez, lo que hace el comportamiento más difícil de predecir. Dentro de una función, una variable local es lo normal y lo seguro.

**`try/except` con excepciones específicas:**
- `RefreshError`: el refresh token ya no sirve (por ejemplo, pasaron los 7 días del modo Testing).
- `TransportError`: falló la conexión al renovar (sin internet).
- Una excepción genérica (`except Exception`) alrededor del login atrapa lo demás, como que el usuario cierre el navegador sin aceptar.

**Meter dentro del `try` todo lo que depende de algo externo:** si `from_client_secrets_file` queda fuera del `try` y falta `credentials.json`, el programa se cae. Dentro del mismo `try` que el login, el error cae en el `except` y la función devuelve `None` con un mensaje.

**De qué librería viene cada excepción:** `RefreshError` y `TransportError` viven en `google.auth.exceptions` (la que renueva credenciales), no en `googleapiclient.errors`. Las dos librerías empiezan por "google", así que es fácil confundirlas.

**`if __name__ == "__main__":`:** el bloque solo se ejecuta cuando el archivo se corre directamente (`python correo.py`), no cuando otro archivo lo importa. Sirve para probar un módulo sin que corra solo al importarlo.

**Docstring vs comentario:** `#` es para encabezados de sección y para explicar pasos internos. Las triple comillas (`"""..."""`) solo valen como docstring si son **lo primero dentro de la función**, justo debajo del `def`: ahí describen qué hace y qué devuelve, y VS Code las muestra al pasar el cursor. Puestas antes del `def` o después de otra línea, son solo un texto suelto que no hace nada.

**Constantes en MAYÚSCULAS:** convención de Python para valores que no cambian (`SCOPES`, `CREDENTIALS_PATH`, `TOKEN_PATH`).

**Dónde va cada cosa:** `SCOPES` y las rutas de los JSON son detalles internos del módulo de correo, así que viven en `correo.py`. `config.py` guarda lo que el usuario personaliza (apps, páginas, carpetas, modos); ahí irá, más adelante, el interruptor para desactivar el correo en una versión pública.

### Buscar correos (`buscar_ids`)

**`list` devuelve identificadores, no correos:** `servicio.users().messages().list(...)` trae solo una lista de `id`. Para ver el contenido de cada mensaje hay que pedirlo aparte con `get`. `userId='me'` significa "el dueño de la cuenta autenticada".

**La respuesta es un diccionario anidado:** `respuesta['messages']` es una lista de diccionarios (`{'id': ..., 'threadId': ...}`). Para quedarse solo con los `id`, se recorre con un `for` y se van guardando con `.append()` en una lista nueva.

**`.get(clave, respaldo)` para el caso vacío:** cuando no hay correos que cumplan la búsqueda, la clave `'messages'` directamente no existe (no viene vacía). `respuesta['messages']` daría `KeyError`; `respuesta.get('messages', [])` devuelve una lista vacía y el `for` simplemente no se ejecuta.

**Armar un texto condicional con una lista y `" ".join(...)`:** se empieza con una lista que tiene la parte fija (`['category:primary']`), se agrega un pedazo por cada filtro usado (`if dias:`, `if remitente:`) y al final se unen con `" ".join(partes)`. Así no hay que controlar a mano dónde van los espacios.

**Parámetros con valor por defecto:** `def buscar_ids(servicio, cantidad=5, dias=None, remitente=None)`. Quien llama pasa solo lo que necesita. `None` significa "este filtro no se usa", y `if dias:` lo detecta.

**f-strings:** un texto con una `f` antes de las comillas reemplaza lo que va entre `{}` por el valor de la variable (`f"newer_than:{dias}d"`). Cuando el texto necesita llevar comillas dobles adentro, el exterior se escribe con comillas simples: `f'from:"{remitente}"'`.

**Un tope con constante y `min()`:** `MAX_CORREOS = 10` fija el máximo en un solo lugar, y `cantidad = min(cantidad, MAX_CORREOS)` se queda con el menor de los dos números. Pedir 500 devuelve 10, pedir 3 devuelve 3. El número se eligió por tres razones: cada correo es una petición aparte a Gmail (velocidad), un modelo de 3B pierde calidad con mucho texto, y una lista muy larga deja de ser útil al escucharla. Probar el tope solo sirve si la bandeja tiene más correos que el tope.

**Filtros de búsqueda de Gmail** (el mismo buscador de la web, pasado en el parámetro `q`):
- `category:primary`: solo la pestaña Principal.
- `newer_than:3d`: correos de los últimos 3 días. No confundir con `after:`, que espera una **fecha** (`after:2026/10/05`) y no una cantidad de días.
- `from:"Jaime Pérez"`: remitente. Sin las comillas, un nombre con espacios se interpreta mal.
- `is:unread`: no leídos.
- `maxResults`: no es parte de `q`, es un parámetro aparte que limita cuántos resultados vuelven.
- `resultSizeEstimate`: el total aproximado que coincide con la búsqueda; es una estimación, no un número exacto.

### Leer un correo (`leer_correo`)

**`format='metadata'` y `metadataHeaders`:** pide solo los encabezados que interesan (`From`, `Subject`, `Date`) y no el cuerpo entero, que es más ligero. El parámetro de la función se llama `id_correo` y no `id`, porque `id` ya es una función de Python.

**Una lista de diccionarios no se consulta por nombre:** los encabezados llegan en `mensaje['payload']['headers']` como una lista de fichas (`{'name': 'Subject', 'value': '...'}`). No se puede pedir `['Subject']` a una lista, y tampoco conviene usar posiciones, porque el orden de llegada no es el que se pidió. Se recorre con un `for` y se arma un diccionario nuevo: `encabezados[h['name']] = h['value']`.

**Etiqueta y contenido:** en `diccionario[ETIQUETA] = CONTENIDO`, lo que va entre corchetes es la etiqueta con la que se buscará después, y lo que va a la derecha es el dato. Invertirlos es un error común: el programa no se cae, pero el diccionario queda al revés y las búsquedas posteriores fallan.

**`.get(clave, respaldo)` para datos que pueden faltar:** un correo sin asunto no trae el encabezado `Subject`, y `encabezados['Subject']` daría `KeyError`. `encabezados.get('Subject', '(sin asunto)')` devuelve el respaldo en ese caso. Es el mismo método que se usó con `'messages'` en `buscar_ids`.

**Nombres propios en la salida:** la función devuelve `remitente`, `asunto`, `fecha` y `snippet`, y no los nombres que usa la API (`From`, `Subject`...). Quien use la función no depende de cómo los llama Google.

**El dato se devuelve tal cual llega:** el `snippet` de algunos correos de marketing trae decenas de caracteres invisibles, y el remitente viene como `Nombre <correo@dominio>`. `correo.py` no los limpia; quien los muestre o los lea en voz alta decide qué recortar.

### Unir todo y manejar errores (`obtener_correos`)

**Tres resultados con significado distinto:** `None` (algo falló: login, conexión o Gmail), `[]` (todo bien, pero no hay correos) y una lista con datos. Si los dos primeros se mezclaran, quien llame no podría distinguir "se cayó la conexión" de "la bandeja está vacía". Por eso se pregunta `is None` **antes** que `not correos`: `not correos` es verdadero para ambos.

**El `try` debe envolver todos los pasos que hablan con el servicio externo:** la primera versión protegía solo la búsqueda, pero el error de la prueba ocurrió en la lectura, fuera del `try`, y tumbó el programa. Se descubrió provocándolo a propósito.

**Cada `except` que atrapa un fallo debe terminar con `return None`:** sin él, el programa sigue hasta el final de la función y puede fallar con `UnboundLocalError` (la lista nunca se creó) o devolver una lista incompleta como si fuera el resultado normal.

**`except` separados para fallos distintos, y cada excepción vive en su librería:**
- `HttpError` (`googleapiclient.errors`): Gmail respondió, pero con un problema (id inválido, límite de peticiones, permiso revocado).
- `ServerNotFoundError` (`httplib2`): ni siquiera hubo respuesta, no hay conexión.
- `RefreshError` y `TransportError` (`google.auth.exceptions`): fallos al renovar el token.

**Leer un traceback de abajo hacia arriba:** la última línea dice qué pasó, y las de arriba dicen dónde (qué función llamó a cuál).

**Provocar los fallos a propósito para conocer la excepción real:** con un `id` inventado salió `HttpError 400`; con el wifi apagado salió `ServerNotFoundError`. No se adivinan los nombres de las excepciones, se observan. Con el uso real pueden aparecer otras (por ejemplo, un timeout) y se agregan entonces.

**El docstring describe todos los finales posibles,** no solo el feliz: lista, lista vacía y `None`.

### Conectar con `main.py`

**Orden de los bloques:** `main.py` revisa cada frase de arriba hacia abajo y el primer bloque que la reconoce gana, porque termina con `continue`. El bloque de correo va después de salir y antes de rutinas y acciones; si estuviera después, algunas frases caerían antes en otro bloque.

**Dos conjuntos y `and`:** `PALABRAS_CORREO` dice de qué se habla y `PALABRAS_LEER` qué se quiere hacer con eso. Se exigen las dos a la vez: "léeme mis correos" lee, "abre mis correos" no (sigue hacia las acciones) y "léeme un cuento" tampoco. Cada una se comprueba con el mismo patrón `any(palabra in texto for palabra in conjunto)` que ya usaba `PALABRAS_EJECUTAR`.

**Conjuntos (`set`) en vez de listas:** se escriben con llaves, no tienen orden y no repiten elementos. Para preguntar "¿está alguna de estas palabras?" funcionan igual que una lista.

**Detalles de la búsqueda por palabras:** las tildes no se normalizan (`léeme` y `leeme` son distintas, por eso se ponen ambas variantes), y se busca el trozo de texto, no la palabra completa (`mail` aparece dentro de `gmail`).

**`from correo import obtener_correos`:** importa solo la función. Con `import correo`, la variable `correo` de un `for` taparía al módulo.

**Límite de las palabras clave:** "entonces lee una hermosa mañana correo" también activa la lectura, porque tiene una palabra de cada conjunto. Hacerlo más estricto con más reglas sería código que se descarta en la Fase 3.5, cuando Ollama clasifique la intención con JSON. Se dejó como comportamiento conocido.

**Diagnóstico vs lo que dice Zoltrak:** los `print` de `correo.py` son mensajes técnicos para quien desarrolla (qué falló y por qué); el mensaje de `main.py` es lo que Zoltrak le dice al usuario, con su personalidad. Mientras todo sea consola conviven bien; con la voz habrá que separarlos.

**Un efecto lateral a tener presente:** lo que Zoltrak muestra de los correos no se guarda en el historial de la conversación, así que Ollama no puede responder preguntas sobre ese contenido.

### Diseño del módulo

**Las funciones devuelven datos, no texto final ni `print`:** `correo.py` devuelve listas y diccionarios (`remitente`, `asunto`, `fecha`, `snippet`). Quien los use decide qué hacer: imprimirlos hoy, pasarlos a voz en la Fase 3.5, o mandarlos a Ollama para que los explique. Así, cuando llegue la voz, `correo.py` no se toca. El texto de salida no se mezcla con la lógica que obtiene los datos.

**Cada módulo tiene un papel claro:**
- `acciones.py`: cosas que se hacen sobre el PC (`os.startfile`).
- `database.py`: acceso a un servicio externo (PostgreSQL).
- `correo.py`: acceso a otro servicio externo (Gmail), hermano de `database.py`.

**Dividir en capas pequeñas:** buscar, leer y armar el resultado final son funciones distintas (`buscar_ids`, `leer_correo`, `obtener_correos`), cada una con un solo trabajo y fácil de probar sola.

**No hace falta Ollama para todo:** para leer en voz alta los títulos de los correos basta armar una frase con los datos. Ollama solo hace falta cuando se necesita interpretar el contenido (resumir, explicar de qué trata cada correo).

### Forma de trabajar

**Esqueleto en comentarios antes del código:** escribir primero los pasos como comentarios, revisarlos, y recién después rellenar con código. Obliga a pensar el flujo antes de tocar el teclado y deja cada paso documentado.

**Construir y probar de a un paso:** primero la llamada sin filtros para ver qué responde la API, luego sacar solo los `id`, luego agregar los filtros. Cada paso se prueba antes de seguir, así un fallo se ubica rápido.

**Leer las sugerencias del autocompletado antes de aceptarlas:** el editor sugirió `after:{dias}`, que parece razonable pero cambia el significado de la búsqueda. En una API que no se conoce, una sugerencia plausible puede estar mal.

**Provocar los fallos a propósito:** probar con un id inventado y con el wifi apagado mostró dos errores reales que no se habrían visto con datos buenos (un `try` demasiado corto y un `return None` que faltaba). Una función no está probada hasta haber visto cómo falla.

**Probar los casos límite:** además del caso normal, se prueba el resultado vacío (por ejemplo, un remitente que no existe, que debe devolver `[]` sin error).

## Flujo de trabajo con Git

**Orden recomendado:**
1. Al empezar a trabajar: `git status` (ver que no haya cambios sueltos) → `git pull` (traer lo nuevo).
2. Antes de un commit: `git status` de nuevo, para revisar qué se va a subir.
3. Antes de un `push`: otro `git pull` si pasó tiempo, para evitar conflictos.

**Merge commit:** aparece automáticamente cuando Git une dos historias distintas (por ejemplo, un cambio hecho en GitHub y otro hecho en local). No es un error, es la forma en que Git resuelve que ambos lados tengan commits nuevos.

**Commits atómicos:** un commit por cambio con sentido propio, con un mensaje que describa qué se corrigió o agregó. Facilita revisar el historial después, sobre todo en un repo público.

**Conventional Commits:** prefijo en el mensaje (`feat:`, `fix:`, `refactor:`, `docs:` y `chore:`) que indica el tipo de cambio de un vistazo, en minúscula por convención. `chore:` cubre configuración y mantenimiento que no toca la lógica del programa (`.gitignore`, dependencias en `requirements.txt`); se agregó a la convención del proyecto porque esos cambios no encajaban en los otros cuatro. El estándar completo trae más prefijos (`test:`, `style:`, `build:`), pero el proyecto usa solo estos cinco. Con squash merge, el prefijo de cada commit intermedio no queda en el historial de `main`: queda el título del PR.

**GitHub Flow (el que usa este proyecto):** `main` siempre queda desplegable. Cada cambio va en una rama corta por tarea puntual (no por fase ni por funcionalidad completa), nombrada `tipo/nombre-corto` (ej. `feature/modo-estudio`, `fix/personalidad-zoltrak`). Al terminar, se abre un Pull Request a `main`, se revisa (Copilot code review cuando aplica), y se mergea con **squash** (condensa todos los commits de la rama en uno solo, para un historial de `main` limpio). La rama se borra después de mergeada — el historial completo (commits, diff, PR) queda disponible para siempre en los Pull Requests cerrados de GitHub, aunque la rama ya no exista.

**Commits separados por propósito:** un cambio de `.gitignore` y un cambio de `requirements.txt` van en commits distintos, aunque se hagan en la misma sesión. Cada commit se entiende solo y, si hay que revertir uno, no arrastra al otro.

**`git add <archivo>` en vez de `git add .`:** nombrar el archivo asegura que solo se sube lo que se quiere. Con `git add .` es fácil que se cuele algo sensible.

**Secretos en un repo público:** si un archivo con credenciales llega a un commit, queda en el historial aunque se borre después. Por eso la regla en `.gitignore` se escribe y se verifica **antes** de mover el archivo al proyecto.

**Regla en `.gitignore` con y sin barra:** `credentials.json` (sin barra) aplica en cualquier carpeta del repo; `/credentials.json` (con barra inicial) solo en la raíz. Ignorar un archivo que todavía no existe (como `token.json`, que se genera tras el primer login) es válido: Git aplica la regla cuando aparezca.

**`git check-ignore -v <ruta>`:** comprueba si Git ignora un archivo y muestra la línea del `.gitignore` que lo cubre. Si no imprime nada, el archivo no está protegido. Funciona aunque el archivo aún no exista.

**Nombres de archivo que revelan datos:** el `client_secret_...json` que descarga Google incluye el ID de cliente en el nombre. Poner ese nombre en un `.gitignore` público lo expone, así que se renombra a algo fijo (`credentials.json`) antes de escribir la regla.

**`git diff <archivo>` antes de un commit:** muestra línea por línea qué cambió (`+` agregado, `-` borrado). Para `requirements.txt` sirve para confirmar que sobrescribir con `pip freeze > ../requirements.txt` no borró nada de lo que ya estaba.

**El paginador de Git:** cuando un `git diff` o `git log` es largo, Git abre un visor con `:` al final. Espacio avanza una página y `q` sale; no es un error.

**`git commit --amend -m "mensaje"`:** reescribe el último commit (por ejemplo, para corregir el mensaje). Solo es seguro si todavía no se ha subido con `push`; si ya se subió, se deja como está.

**Qué ejecutar y desde dónde:** `pip freeze > ../requirements.txt` sobrescribe el archivo completo con lo instalado en el entorno virtual; el `..` sube una carpeta desde `brain/` hasta la raíz. Se usa CMD y no PowerShell, porque `>` en PowerShell guarda en UTF-16 y `pip install -r` falla después.

**Un arreglo ajeno a la tarea en curso va en su propia rama:** si mientras se trabaja en una funcionalidad aparece un problema que no tiene relación (por ejemplo, entradas vacías que se guardan en la base de datos), se anota, se termina la tarea actual y el arreglo sale de `main` en una rama `fix/nombre-corto`. Mezclarlo ensucia el PR y, con el squash, todo quedaría en un solo commit con un título que describe solo una de las dos cosas. Si dos ramas van a tocar el mismo archivo, conviene cerrar una antes de abrir la otra, para evitar conflictos.

**Git Flow (no se usa en este proyecto):** convención más formal de ramas (`main`, `develop`, `feature/*`, `release/*`, `hotfix/*`) y etiquetas de versión (`v1.0.0`, etc.), pensada para proyectos con varios colaboradores o releases formales que sí necesitan separar "lo estable" de "lo que viene". Vale la pena conocerlo porque es lo que se usa en equipos de trabajo reales y en otros proyectos (ej. el de la U con GitFlow).