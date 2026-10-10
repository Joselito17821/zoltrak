# Zoltrak — Asistente virtual con mapa de viaje

## ¿Qué es?

Un asistente virtual personal (estilo Jarvis) al que se le puede hablar o escribir en lenguaje natural, con un tono calmado y contemplativo inspirado en la estética de Frieren (el proyecto no incluye ni distribuye al personaje ni su voz, por derechos de autor). No es solo un chatbot: cada interacción se refleja visualmente como avances en un **mapa de viaje**, dándole una capa ligera de videojuego a un asistente de tareas.

## Objetivos funcionales

1. Entender lenguaje natural (no comandos rígidos) usando un modelo de IA local (Ollama).
2. Ejecutar acciones reales sobre el sistema: abrir aplicaciones, carpetas, páginas web.
3. Leer y resumir correos nuevos (Gmail).
4. Responder por voz y texto, con personalidad definida y consistente.
5. Recordar todo entre sesiones (historial de conversación, progreso).
6. Mostrar una interfaz visual: orbe animado que reacciona al hablar/escuchar, más un mapa de viaje que se desbloquea con el uso.

## Lo que el proyecto NO es

- No es una IA de propósito general tipo ChatGPT sin límites — entiende un dominio de comandos/acciones que se amplía con el tiempo.
- No incluye ni distribuye el personaje, el modelo ni la voz de Frieren (ni de otros personajes con derechos) — estética "inspirada en", no una copia. Para uso personal, cada quien puede cargar sus propios modelos y voces bajo su responsabilidad y la licencia de cada uno; esos archivos nunca van al repositorio.
- No es un servicio en línea ni tiene cuentas de usuario: cada persona lo corre en su propio PC, con sus propios datos.

## Arquitectura

    zoltrak/
      brain/    → cerebro en Python (IA, acciones, voz, correo)
      ui/       → interfaz en Java + JavaFX (orbe, mapa, diálogo)
      db/       → esquema y scripts de PostgreSQL

- **brain/**: lógica del asistente. Usa Ollama (modelo `llama3.2:3b`, local y gratis) para entender lenguaje natural, `subprocess`/`os` para acciones del sistema, API de Gmail (solo lectura) para correo, `SpeechRecognition` + TTS para la voz (Piper por defecto; Coqui y Fish Audio como opciones, ver Decisiones). Se expone como una API local con Flask para que Java le hable por HTTP.
- **db/**: PostgreSQL. Guarda historial de conversación (`mensajes`), datos sueltos del usuario por categoría (`hechos`) y, más adelante, el progreso del "viaje". Esquema en `db/schema.sql`.
- **ui/**: JavaFX (Java 21 LTS). Interfaz visual: orbe animado (con CSS de JavaFX y `Timeline` para animaciones), mapa de viaje con nodos, cuadro de diálogo tipo visual novel. Se conecta al `brain` vía HTTP (`HttpClient` de Java).

## Decisiones ya tomadas

- **IA de lenguaje**: Ollama local, modelo `llama3.2:3b` (liviano, compatible con 16GB RAM + GTX 1650). Decisión fija, no se reconsidera `llama3.1:8b` salvo pedido explícito.
- **Interfaz visual**: JavaFX puro (no Angular/React ni Node) — proporcional al tamaño del proyecto, con CSS propio y soporte de animaciones suficiente. `WebView` queda como plan B si algo se necesita más adelante.
- **Representación visual del asistente**: empieza con un orbe/luz animado (100% código, sin necesidad de arte) como paso intermedio. La meta es un personaje ilustrado estilo anime; el repositorio no incluye el de Frieren (por derechos), pero cada quien puede cargar su propio modelo para uso personal — se evaluará VTube Studio (modelo Live2D + API por WebSocket) como alternativa a construir la animación a mano en JavaFX.
- **Voz**: el repositorio y las versiones compartidas no incluyen ni clonan la voz de la actriz de Frieren (derechos de voz de una persona real). El motor por defecto es Piper (local, gratis y sin internet), con una voz neutral y variante masculina/femenina, ajustada para transmitir calma. Coqui TTS (local) es un motor opcional de la versión personal. Fish Audio (nube) es solo para uso de Jose, con su propia clave, y no va en ninguna versión que se comparta. El motor es intercambiable detrás de una sola función; ver `Funcionalidades Futuras.md`, puntos 7 y 14.
- **Fuente de "mensajes nuevos"**: correo de Gmail vía su API (no IMAP), con el permiso `gmail.readonly` (solo lectura) y la app en modo **Testing**: gratis, hasta 100 usuarios de prueba agregados a mano, y cada cuenta debe reautorizar cada 7 días. La verificación completa de Google se descartó por costo (auditoría CASA Tier 2, de $15,000 a $75,000 USD). Si algún día se distribuye Zoltrak públicamente, la lectura de correo se desactiva en esa versión con un interruptor en `config.py`; el resto no se ve afectado. Alternativa sin límite de usuarios, a reconsiderar: IMAP con contraseña de aplicación. Detalle en `Funcionalidades Futuras.md`.
- **Detección de intención**: por palabras clave hasta la Fase 3.5, donde se reemplaza por JSON estructurado de Ollama. Se decidió no parchear los falsos positivos con más reglas, porque ese código se descartaría.
- **Versión personal y versión pública**: la personal (Jose y círculo cercano) tiene la lectura de correo y Coqui como opción; Fish Audio queda solo en la instalación de Jose. La pública solo trae Piper y el orbe, sin Gmail, Coqui ni Fish Audio. Cargar y cambiar el modelo de VTuber está disponible en ambas; los modelos incluidos de fábrica son solo los que Jose haya verificado como redistribuibles. Las voces de personajes con derechos no se incluyen en ninguna. Se implementa con interruptores en la Fase 7 (ver `Funcionalidades Futuras.md`, punto 14).
- **Credenciales de Google**: `credentials.json` (identidad de la app) y `token.json` (permiso del usuario) viven en `brain/` y están en `.gitignore`.
- **Editor**: VS Code, con extensión de Python (Pylance + Debugger incluidos) y Java Extension Pack. Se descartó usar PyCharm/IntelliJ por separado para no dividir el flujo de trabajo.
- **Entorno virtual**: vive dentro de `brain/venv`, porque solo esa carpeta ejecuta Python.
- **Control de versiones**: repositorio Git inicializado y publicado en GitHub (público), con `.gitignore` excluyendo `venv/`, `__pycache__/`, `.env`, entre otros.
- **Automatización/agentes (Claude Code, Copilot en modo agente)**: se reservan para tareas mecánicas (Git, correr/probar código) una vez la lógica ya esté entendida — no para resolver fases completas de golpe, ya que el objetivo es aprender paso a paso.

## Ruta de desarrollo (fases)

- [x] **Fase 0** — Preparar el terreno: verificar Python/Java/PostgreSQL, instalar Ollama y bajar el modelo, crear estructura de carpetas, entorno virtual.
- [x] **Fase 1** — El cerebro entiende lenguaje natural (Python + Ollama): script de consola que conversa con personalidad básica. *(conexión con Ollama funcionando; personalidad definida vía rol `system`)*
- [x] **Fase 1.5** — Acciones sobre el sistema: abrir apps/carpetas/páginas web según la intención detectada.
- [x] **Fase 2** — Memoria persistente (Python + PostgreSQL): diseño de tablas, historial y progreso guardado entre sesiones. *(conectar `hechos` a la conversación pasa a la Fase 3.5, para no construir una detección manual que se descartaría)*
- [~] **Fase 2.5** — Leer correo (Gmail): resumen de mensajes nuevos.
  - [x] Configuración de Google Cloud Console (proyecto, Gmail API, consentimiento OAuth, usuarios de prueba, permiso `gmail.readonly`)
  - [x] Autenticación OAuth con renovación automática del token (`obtener_servicio_gmail`)
  - [x] Búsqueda por cantidad, días y remitente en la pestaña Principal, con tope `MAX_CORREOS` (`buscar_ids`)
  - [x] Lectura de remitente, asunto, fecha y snippet, con manejo de errores de la API y de conexión (`leer_correo`, `obtener_correos`)
  - [x] Conexión con `main.py` por palabras clave (una palabra de correo y una de lectura)
  - [ ] Resumen con Ollama (modo detalle), en la rama `feature/resumen-correo`
  - [x] Que "abre mis correos" abra Gmail en el navegador (entrada en `config.py`)
- [ ] **Fase 3** — El cerebro como servicio (Flask): API local que separa el cerebro de la interfaz.
- [ ] **Fase 3.5** — Voz: reconocimiento de voz (SpeechRecognition) + texto a voz (Piper/Coqui), con tono calmado. Incluye reemplazar la detección por palabras clave por JSON estructurado de Ollama (entiende variantes como "ábreme" o "los de los últimos tres días") y conectar `hechos` a la conversación.
- [ ] **Fase 4** — Interfaz visual (JavaFX):
  - [ ] 4.1 Ventana base
  - [ ] 4.2 Orbe con gradiente/brillo
  - [ ] 4.3 Animación de pulso del orbe
  - [ ] 4.4 Conexión Java → API de Python (HTTP)
  - [ ] 4.5 Cuadro de diálogo tipo visual novel
- [ ] **Fase 5** — Mapa de viaje: nodos/lugares que se iluminan según el progreso guardado en PostgreSQL.
- [ ] **Fase 6** — Pulir y personalizar: CSS definitivo, frases/personalidad final, panel de personaje ilustrado (opcional).

## Funcionalidades futuras

- [ ] **Fase 7** — Empaquetar la app: llevar Zoltrak de prototipo personal a algo compartible.
  - [ ] 7.1 Distribuir v1 con Ollama instalado por separado (gratis); evaluar v2 con Ollama embebido cuando se sepa el peso final de la app
  - [ ] 7.2 Rutas portables con variables de entorno de Windows (`os.getenv`, `os.path.expanduser`)
  - [ ] 7.3 Detección automática de apps/juegos instalados (Registro de Windows, Menú Inicio, `libraryfolders.vdf` de Steam)
  - [ ] 7.4 Flujo de "no está registrado": buscar automático, confirmar con el usuario, pedir ruta/URL a mano (o selector de archivos) si falla
  - [ ] 7.5 Biblioteca de +50 páginas web comunes incluida de fábrica
  - [ ] 7.6 Varias voces TTS para elegir (Piper por defecto; Coqui opcional en la versión personal; Fish Audio solo para Jose)
  - [ ] 7.7 Varios modos de representación visual (bolita simple tipo Siri, VTuber/Live2D)
  - [ ] 7.8 Cargar un modelo propio de Ollama (si el usuario tiene uno de pago/personalizado)
  - [ ] 7.9 Evaluar abrir contenido específico por nombre (video de YouTube, canción de Spotify, repo de GitHub)
  - [ ] 7.10 Personalidad y voz configurable por personaje visual (elegir, generar aleatoria o escribir la propia)
  - [ ] 7.11 Interruptores de versión personal y pública (correo, Coqui, Fish Audio), y revisión de licencias de los modelos de VTuber que se incluyan de fábrica
- [ ] **Fase 8** — Buscar/abrir archivos por nombre y crear documentos (con confirmación): búsqueda de archivos existentes en carpetas por nombre (extensión de `abrir()`); creación de documentos (PowerPoint, Word) con doble confirmación obligatoria, sin capacidad de borrar ni sobrescribir

## Estado actual

Fase 1.5 completa — Zoltrak detecta acciones por palabras clave y abre apps, páginas web y carpetas desde tres diccionarios separados (`apps`, `paginas_web`, `carpetas`), unidos en uno solo (`todo`) para la búsqueda. Usa `rapidfuzz` para tolerar errores de tecleo en el nombre. Incluye rutinas (`modos`) que agrupan varias entradas de `todo` bajo un nombre (ej. "modo estudio"). Código modularizado en `config.py`, `personalidad.py`, `acciones.py` y `database.py`, con GitHub Flow (rama por tarea + PR) como flujo de Git.

Fase 2 completa — memoria persistente con PostgreSQL: tablas `mensajes` y `hechos`, conexión vía `.env` + `psycopg2`, e historial de conversación persistente entre sesiones (Zoltrak recuerda lo hablado aunque se cierre y reabra el programa). Los `hechos` ya tienen sus funciones de guardado y lectura en `database.py`, pero no están conectados a la conversación: eso se hará en la Fase 3.5.

Fase 2.5 en progreso — lectura de correo con la API de Gmail. `correo.py` autentica con OAuth (renueva el token solo y vuelve a pedir login si pasan los 7 días del modo Testing), busca correos por cantidad, días y remitente en la pestaña Principal (con tope `MAX_CORREOS`) y devuelve remitente, asunto, fecha y snippet, o `None` si falla el login, la conexión o la API. `main.py` lo activa cuando la frase tiene una palabra de correo y una de lectura (por ejemplo, "revisa mis correos"), antes de los bloques de rutinas y acciones. Con la entrada `correo` en `config.py`, "abre mis correos" abre Gmail en el navegador. Pendiente: resumen con Ollama (rama aparte).

## Comportamientos conocidos (por diseño, se resuelven en la Fase 3.5)

- **"abreme algo"** activa el bloque de acciones por contener "abre" y responde "No reconozco ese camino". Se mantiene el aviso para no ocultar fallos de rutas reales.
- **"bye luego hablamos"** no cierra el programa; solo "bye" exacto. Es intencional, para evitar cierres falsos.
- **Correo: falsos positivos.** Cualquier frase con una palabra de lectura y una de correo activa la lectura, aunque no sea una petición (por ejemplo, "lee una hermosa mañana correo"). "Abre mis correos" no la activa, porque "abre" no es palabra de lectura.
- **Lo que Zoltrak muestra de los correos no entra al historial** de la conversación, así que Ollama no sabe de qué se habló.
- **Los mensajes de diagnóstico de `correo.py`** (errores de login, conexión o API) se imprimen en consola. Cuando llegue la voz habrá que separarlos de lo que Zoltrak dice al usuario.