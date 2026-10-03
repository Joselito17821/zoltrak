# Zoltrak — Funcionalidades futuras (Fase 7)

Este documento detalla, una por una, las funcionalidades que se evaluaron como parte de la futura distribución de Zoltrak. No son parte de la fase actual (Fase 1.5 en adelante hasta la 6); se retoman cuando el asistente esté terminado para uso personal y se quiera compartir o pulir más allá de eso. Sirve como memoria detallada para no perder ninguna idea discutida.

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

## Nota — tolerancia de lenguaje natural

Ya quedó decidido (no es una funcionalidad nueva de esta fase): la detección estricta de palabras exactas como "abre" se reemplaza en la Fase 3.5 por el JSON estructurado de Ollama, que sí entiende variantes como "ábreme", "ejecútame" o "ayúdame a abrir" sin necesitar que la palabra exacta esté escrita.