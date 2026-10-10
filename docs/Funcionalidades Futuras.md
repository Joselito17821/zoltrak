# Zoltrak — Funcionalidades futuras (Fase 7)

Este documento detalla, una por una, las funcionalidades que se evaluaron como parte de la futura distribución de Zoltrak. No son parte de las fases 0 a 6 (el asistente para uso personal); se retoman cuando el asistente esté terminado para uso personal y se quiera compartir o pulir más allá de eso. Sirve como memoria detallada para no perder ninguna idea discutida.

## 1. Empaquetar la app

Queremos poder compartir Zoltrak con otras personas sin que tengan que instalar Python ni tocar código. El empaquetado del script en sí (con PyInstaller, por ejemplo) no es el problema — el problema es Ollama, que corre aparte del código de Zoltrak.

Se evalúan dos versiones:

- **v1 — Ollama instalado por separado (elegida para ahora):** cada persona instala Ollama por su cuenta, igual que lo hizo Jose. Ventaja: cero costo, no aumenta el peso del instalador. Desventaja: no es "descargar y listo", tiene un paso extra.
- **v2 — Ollama embebido en el instalador (evaluar más adelante):** el instalador de Zoltrak trae Ollama y el modelo incluidos. Ventaja: instalación en un solo paso. Desventaja: el modelo (`llama3.2:3b`) pesa varios GB, así que el instalador final pesaría eso también. Se decide si vale la pena una vez la app esté terminada y se sepa cuánto pesa todo lo demás.

Se descartó mover el modelo a una API de pago en la nube: tendría costo por cada uso, y como no hay plan de cobrar por la app, no se justifica el gasto. Si en algún momento se considerara vender Zoltrak, ahí sí valdría la pena recalcular esta opción.

## 2. Rutas portables

Hoy las rutas están escritas a mano con el nombre de usuario de Jose (`C:\Users\Jose Manuel\...`), así que en el PC de otra persona simplemente no existen. Para las carpetas estándar de Windows (AppData, Escritorio, Documentos, Descargas) se puede usar una variable de entorno en vez de escribir el nombre de usuario a mano:

```python
os.getenv("APPDATA")
os.path.expanduser("~")
```

Esto devuelve la ruta correcta sin importar en qué PC corra el programa. No sirve para carpetas organizadas a gusto de cada quien (como "universidad, semestre 8"), esas siguen necesitando configuración manual (ver punto 5).

## 3. Detección automática de apps y juegos instalados

Para software instalado "de verdad" (con instalador oficial), Windows deja rastro que se puede leer por código, sin que el usuario escriba cada ruta a mano:

- **Registro de Windows** (librería `winreg`): la mayoría de programas con instalador oficial registran ahí dónde quedaron instalados.
- **Carpeta del Menú Inicio**: se puede escanear con `os.listdir()` para armar una lista de accesos directos existentes.
- **Steam**: guarda un archivo (`libraryfolders.vdf`) con las rutas donde están instalados los juegos, legible desde Python.

Limitación importante: esto solo funciona con software "bien portado". Un juego o programa pirata/portable, bajado por torrent y simplemente descomprimido, no pasa por ningún instalador que registre nada en un lugar central — no hay forma automática de encontrarlo, y toca pedirle la ruta al usuario a mano.

## 4. Selector de archivos (configuración sin tocar código)

Para cuando ni la detección automática ni escribir una ruta a mano son una opción amigable (pensando en alguien sin conocimientos de programación), Python ya trae incluida una librería (`tkinter.filedialog`) que abre un diálogo nativo de Windows: la persona navega con el mouse hasta la carpeta o el `.exe`, y el programa guarda esa ruta solo. Es la misma experiencia de subir un archivo a WhatsApp o Discord.

## 5. Flujo de "no está registrado" (auto-registro)

Cuando se pide algo que no existe en la biblioteca (app, página web o carpeta), el flujo acordado es:

1. Zoltrak avisa que no está registrado y pregunta si se quiere agregar ya o después.
2. Si se agrega ya, se redirige a la pantalla de agregar (un diálogo, en la interfaz final).
3. El usuario escribe el nombre de nuevo.
4. El sistema intenta resolverlo solo:
   - **Páginas web:** probando el patrón `https://www.<nombre>.com` con una petición HTTP (librería `requests`), para ver si existe.
   - **Apps/juegos:** buscando en el Registro de Windows, Steam o el Menú Inicio (punto 3).
5. Si encuentra una coincidencia, confirma con el usuario ("¿es esta?").
6. Si el usuario dice que no, o no se encontró nada, se pide la ruta/URL completa a mano, o con el selector de archivos (punto 4) para apps/carpetas.
7. Se guarda la respuesta para la próxima vez — la biblioteca "aprende" sobre la marcha.

## 6. Biblioteca de páginas web incluida de fábrica

Para que Zoltrak sirva sin configuración desde el primer uso, se incluye un set grande (50-100+) de páginas web comunes ya resueltas de antemano (YouTube, Instagram, LinkedIn, ChatGPT, Claude, Netflix, Gmail, GitHub, etc.). Es trabajo manual una sola vez al construir la lista, pero automático para quien use la app. Si falta alguna, se agrega en cualquier momento con el flujo del punto 5.

## 7. Personalización de voz

Varias voces TTS para elegir (masculina, femenina, tipo robot, tipo animal), en vez de una sola voz fija, para que cada persona pueda ajustar Zoltrak a su gusto.

El motor de voz debe ser intercambiable: el resto de Zoltrak llama a una sola función (por ejemplo, `hablar(texto)`) y el motor concreto queda detrás de ella. Así se puede rotar entre motores sin reescribir código:

- **Piper** — motor por defecto. Local, gratis y sin internet. Voz neutral, con variante masculina y femenina, pensada para quien no tiene un personaje específico.
- **Coqui TTS** — opcional, también local. A revisar en su momento: licencia del modelo, y si sirve para acercarse a la voz de un personaje a partir de una muestra de audio, sin salir del PC.
- **Fish Audio** — en la nube, con la clave de API propia de Jose (ver la nota al final de este documento). Es solo para uso de Jose: no se ofrece a otras personas ni va en ninguna versión que se comparta.

Cada personaje o apariencia tiene asignada su voz: una voz genérica de Piper o una voz más cercana al personaje (ver el punto 12).

## 8. Modos de representación visual

Varias opciones de apariencia disponibles de fábrica, no solo el personaje ilustrado final:

- Una "bolita" simple animada, tipo Siri, como alternativa ligera.
- Algunas opciones de VTuber/Live2D gratuitas, para quien quiera algo más elaborado sin construir su propio modelo.

## 9. Animaciones reactivas por acción

(Nota: esto pertenece a las fases 4-6, interfaz visual, no a la Fase 7 — se deja anotado aquí para no perderlo.) El personaje "reacciona" visualmente a una acción concreta (por ejemplo, "agarra" algo cuando se abre una app). Con VTube Studio se logra disparando sus hotkeys desde la API del `brain` (Fase 3, Flask); con JavaFX puro, habría que dibujar o conseguir cada pose a mano. Se evalúa cuando la interfaz base ya esté funcionando.

## 10. Cargar un modelo propio de Ollama

Una sección de configuración para poder apuntar Zoltrak a un modelo distinto al `llama3.2:3b` por defecto — por ejemplo, si el usuario descarga o compra un modelo distinto y quiere que Zoltrak lo use en vez del modelo incluido por defecto.

## 11. Abrir contenido específico por nombre (evaluación)

Pregunta abierta: ¿se puede pedir "ábreme YouTube y reproduce *Hola Juanito de Nilo Gea*" o "abre Spotify y pon esta canción", en vez de solo abrir la app y que el usuario busque? La sospecha inicial era que esto requeriría una API de pago — **no es necesariamente así**:

- **YouTube:** se puede construir una URL de búsqueda (`youtube.com/results?search_query=...`) sin ninguna API, gratis — pero solo muestra resultados, no reproduce directo. Para reproducir el primer resultado automáticamente hace falta una herramienta que resuelva la búsqueda (como `yt-dlp`), gratuita y sin clave de API. La API oficial de YouTube (Data API v3) también tiene una cuota gratuita diaria que alcanzaría para este uso, sin pagar, salvo un uso muy intensivo.
- **Spotify:** la API web de Spotify es gratuita (requiere una cuenta de desarrollador gratuita) para buscar canciones. Reproducir automáticamente en el dispositivo del usuario (Spotify Connect) generalmente requiere cuenta Premium del usuario; abrir directamente un enlace de canción (`spotify:track:ID`) con `os.startfile` abre la app en esa canción, aunque puede necesitar que el usuario le dé play.
- **GitHub:** abrir un repo específico es solo un patrón de URL conocido (`github.com/usuario/repo`), sin necesidad de ninguna API; buscar por nombre sin conocer el dueño sí usaría la API pública de búsqueda de GitHub, también gratuita.

**Conclusión:** es viable sin costo para una primera versión, pero necesita más investigación concreta (cuál herramienta usar en cada caso) al llegar a esa fase. Se incluye como funcionalidad futura a evaluar en detalle, no se descarta.

## 12. Personalidad y voz por personaje

Cada apariencia visual (bolita Zoltrak, un VTuber descargado, Frieren, Fern, Miku, etc.) tendría su propia personalidad y voz asociadas, no una personalidad fija para todo el asistente:

- Al cambiar de imagen, el asistente se presenta con el nombre y la personalidad de ese personaje (ej. cambiar a Frieren hace que se presente como Frieren, con su forma de hablar).
- **Voces:** para la bolita, voces genéricas (masculina/femenina/robot). Para un personaje conocido (VTuber existente, Frieren, Miku), buscar su voz real o replicarla con IA; si no es posible, una voz creada a mano que le quede bien al personaje.
- **Configuración de personalidad:** debe ser tan configurable como la de Zoltrak hoy (reglas, tono, rasgos definidos por el usuario). Para cuando alguien cargue una imagen sin personalidad definida (ej. un familiar con su propia VTuber descargada o comprada), se le ofrecen tres opciones:
  1. Elegir una personalidad ya creada (ej. "personalidad de Frieren").
  2. Generar una personalidad aleatoria.
  3. Escribir la suya propia, con los mismos campos que ya existen para Zoltrak (reglas, tono, rasgos).

**Modelos de VTuber:** cargar un modelo propio y cambiar entre modelos está disponible en **todas** las versiones, incluida la pública. Lo que cambia es qué modelos trae la app de fábrica: solo los que Jose haya verificado que su licencia permite redistribuir. Cada modelo tiene su propia licencia (muchos prohíben redistribuirlos, incluso gratis), así que ante la duda no se incluye y cada persona lo consigue en la fuente original.

**Voces de personajes con derechos:** Zoltrak no las incluye ni las distribuye. Cada persona puede cargar las suyas para uso personal, bajo su responsabilidad y según la licencia de cada archivo.

Los archivos de terceros que no tengan licencia de redistribución viven en una carpeta ignorada por Git y nunca se suben al repositorio, que es público.

## 13. Buscar/abrir archivos por nombre y crear documentos (con confirmación)

Dos capacidades nuevas, de riesgo y complejidad distintos — no se mezclan en el mismo flujo:

**Buscar y abrir un archivo existente por nombre, dentro de una carpeta** (bajo riesgo, extensión natural de `acciones.abrir()`):
- El usuario pide, por ejemplo, "ábreme el Word que se llama X" o "el PDF de la carpeta Y".
- Zoltrak busca dentro de la(s) carpeta(s) indicadas (`os.walk()` o similar) un archivo cuyo nombre coincida, con tolerancia a errores de tecleo (mismo fuzzy matching que ya usa con apps).
- Al encontrarlo, lo abre con `os.startfile()` — es solo lectura del sistema de archivos, no modifica nada.

**Crear documentos nuevos** (mayor riesgo, funcionalidad separada con reglas propias):
- El usuario pide algo como "créame en la carpeta Clases de Bases de Datos un PowerPoint y llámalo X".
- Requiere una librería por tipo de archivo (`python-pptx`, `python-docx`, etc.) y que Ollama genere el contenido (título, estructura) a partir de lo que pida el usuario.
- **Doble confirmación obligatoria**: Zoltrak repite qué va a crear y dónde, antes de ejecutar — mismo patrón que el auto-registro de apps/webs (Fase 7).
- **Solo crear, nunca borrar ni sobrescribir**: la función nunca tiene acceso a comandos de borrado; si ya existe un archivo con ese nombre, avisa en vez de reemplazarlo.

## 14. Versión personal y versión pública (interruptores)

Zoltrak se puede compartir de dos maneras, con funciones distintas:

| Función | Versión personal (Jose y círculo cercano) | Versión pública (descarga abierta) |
|---|---|---|
| Lectura de correo (Gmail) | Activada, para cuentas agregadas como usuarios de prueba | Desactivada |
| Voz con Piper (local) | Sí | Sí, único motor de voz |
| Voz con Coqui (local) | Opcional | No incluida |
| Voz con Fish Audio (nube) | Solo en la instalación de Jose, con su clave | Desactivada |
| Orbe / bolita animada | Sí | Sí |
| Cargar y cambiar el modelo de VTuber | Sí | Sí |
| Modelos de VTuber incluidos de fábrica | Solo los verificados como redistribuibles | Solo los verificados como redistribuibles |
| Voces de personajes con derechos | Las aporta cada usuario, para uso personal | No se incluyen |

Cómo se implementa: interruptores en `config.py` (por ejemplo, `LEER_CORREO_ACTIVADO` y la lista de motores de voz disponibles) o builds separados. Se construye en la Fase 7, no antes: hoy no hay una versión pública que necesite apagar nada.

Reglas que valen siempre:

- Ningún asset de terceros (modelo, imagen o voz) entra al repositorio sin haber verificado antes que su licencia permite redistribuirlo. El repositorio es público.
- Ninguna clave ni credencial propia (Gmail, Fish Audio) viaja en una versión compartida.
- Como la versión personal no se cobra, no hay ingreso de por medio, pero eso no resuelve por sí solo los derechos de los assets de terceros: cada archivo tiene su propia licencia.

## Nota — tolerancia de lenguaje natural

Ya quedó decidido (no es una funcionalidad nueva de esta fase): la detección estricta de palabras exactas como "abre" se reemplaza en la Fase 3.5 por el JSON estructurado de Ollama, que sí entiende variantes como "ábreme", "ejecútame" o "ayúdame a abrir" sin necesitar que la palabra exacta esté escrita.

### Nota — lectura de correo (Gmail) y distribución pública

La API de Gmail, para leer correo (`gmail.readonly`), es gratis de usar, pero publicar la app en modo "Production" sin el límite de usuarios requiere pasar una auditoría de seguridad obligatoria de Google (CASA Tier 2), con un costo de $15,000 a $75,000 USD, renovable cada 12 meses — inviable para este proyecto.

Mientras la app esté en modo "Testing" (gratis), solo pueden usar la lectura de correo hasta 100 cuentas agregadas manualmente por el desarrollador, y cada una debe reautorizar el acceso cada 7 días.

Decisión: para uso personal (Jose + círculo cercano), se mantiene en modo Testing sin verificar — cubre el caso real de uso. Si en algún momento se distribuye Zoltrak más ampliamente (descarga pública desde una página web), la funcionalidad de lectura de correo se desactiva para esa versión (feature flag en `config.py`, o un build separado sin esa función compilada) — el resto de funcionalidades de Zoltrak no se ve afectado. Alternativa sin este límite, a reconsiderar si se necesita más adelante: IMAP con contraseña de aplicación (gratis, sin tope de usuarios, pero más fricción de configuración para cada persona).

### Nota — Fish Audio (voces en la nube)

Fish Audio es un servicio en la nube de texto a voz y clonación, con API y una biblioteca de voces de la comunidad. Lo que se pudo verificar (reseñas de terceros y el blog de la empresa, mediados de 2026):

- Tiene un modelo gratuito en su API bajo uso razonable, sin garantía de disponibilidad ni de latencia. El plan de pago por API ronda los 15 dólares por millón de caracteres.
- Las fuentes no coinciden en si el plan gratuito permite uso comercial (algunas dicen que solo uso personal). **Verificar en la documentación y los términos oficiales antes de depender de ello.**
- No es algo que se "distribuya": es un servicio al que se accede con una cuenta y una clave de API. En Zoltrak solo lo usa Jose, con su propia clave en el `.env` (por ejemplo, `FISH_API_KEY`). Esa clave no se comparte ni va en ningún build: gastaría su cuota, podría filtrarse y probablemente va contra los términos del servicio.
- **Privacidad:** el texto que Zoltrak diga sale a los servidores de Fish Audio, incluido lo que lea de los correos. Con Piper o Coqui todo queda en el PC.
- Necesita internet. Sin conexión, Zoltrak debe caer a Piper.
- Las voces de la comunidad son de terceros y pueden ser clones de personas reales o de personajes. Son para el uso personal de Jose; no se incluyen ni se redistribuyen con Zoltrak.