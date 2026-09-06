# Zoltrak — Asistente virtual con mapa de viaje

## ¿Qué es?

Un asistente virtual personal (estilo Jarvis) al que se le puede hablar o escribir en lenguaje natural, con un tono calmado y contemplativo inspirado en la estética de Frieren (sin reproducir al personaje ni su voz, por derechos de autor). No es solo un chatbot: cada interacción se refleja visualmente como avances en un **mapa de viaje**, dándole una capa ligera de videojuego a un asistente de tareas.

## Objetivos funcionales

1. Entender lenguaje natural (no comandos rígidos) usando un modelo de IA local (Ollama).
2. Ejecutar acciones reales sobre el sistema: abrir aplicaciones, carpetas, páginas web.
3. Leer y resumir correos nuevos (Gmail/Outlook).
4. Responder por voz y texto, con personalidad definida y consistente.
5. Recordar todo entre sesiones (historial de conversación, progreso).
6. Mostrar una interfaz visual: orbe animado que reacciona al hablar/escuchar, más un mapa de viaje que se desbloquea con el uso.

## Lo que el proyecto NO es

- No es una IA de propósito general tipo ChatGPT sin límites — entiende un dominio de comandos/acciones que se amplía con el tiempo.
- No usa el personaje ni la voz real de Frieren — estética "inspirada en", no una copia.
- No es multiusuario ni se publica en internet — corre local, en la máquina del usuario.

## Arquitectura

```
zoltrak/
  brain/    → cerebro en Python (IA, acciones, voz, correo)
  ui/       → interfaz en Java + JavaFX (orbe, mapa, diálogo)
  db/       → esquema y scripts de PostgreSQL
```

- **brain/**: lógica del asistente. Usa Ollama (modelo `llama3.2:3b`, local y gratis) para entender lenguaje natural, `subprocess`/`os` para acciones del sistema, IMAP/API de Gmail para correo, `SpeechRecognition` + una librería TTS (Piper o Coqui, aún por decidir) para voz. Se expone como una API local con Flask para que Java le hable por HTTP.
- **db/**: PostgreSQL. Guarda historial de conversación y progreso del "viaje". Diseño de tablas pendiente de definir en la Fase 2.
- **ui/**: JavaFX (Java 21 LTS). Interfaz visual: orbe animado (con CSS de JavaFX y `Timeline` para animaciones), mapa de viaje con nodos, cuadro de diálogo tipo visual novel. Se conecta al `brain` vía HTTP (`HttpClient` de Java).

## Decisiones ya tomadas

- **IA de lenguaje**: Ollama local, modelo `llama3.2:3b` (liviano, compatible con 16GB RAM + GTX 1650). Se puede subir a `llama3.1:8b` si hace falta más calidad de respuesta.
- **Interfaz visual**: JavaFX puro (no Angular/React ni Node) — proporcional al tamaño del proyecto, con CSS propio y soporte de animaciones suficiente. `WebView` queda como plan B si algo se necesita más adelante.
- **Representación visual del asistente**: híbrida — se empieza con un orbe/luz animado (100% código, sin necesidad de arte), y más adelante se evalúa agregar un panel con personaje ilustrado propio (no el de Frieren, por derechos).
- **Voz**: no se clona la voz de la actriz de Frieren (derechos de voz de una persona real). Se usará una voz TTS gratuita y de buena calidad (Piper o Coqui TTS), ajustada en tono/velocidad para transmitir calma, sin ser una copia de nadie.
- **Fuente de "mensajes nuevos"**: correo (Gmail/Outlook), vía IMAP o API de Gmail.
- **Editor**: VS Code, con extensión de Python (Pylance + Debugger incluidos) y Java Extension Pack. Se descartó usar PyCharm/IntelliJ por separado para no dividir el flujo de trabajo.
- **Entorno virtual**: vive dentro de `brain/venv`, porque solo esa carpeta ejecuta Python.
- **Control de versiones**: repositorio Git inicializado y publicado en GitHub (privado, mientras el proyecto está en construcción), con `.gitignore` excluyendo `venv/`, `__pycache__/`, `.env`, entre otros.
- **Automatización/agentes (Claude Code, Copilot en modo agente)**: se reservan para tareas mecánicas (Git, correr/probar código) una vez la lógica ya esté entendida — no para resolver fases completas de golpe, ya que el objetivo es aprender paso a paso.

## Ruta de desarrollo (fases)

- [x] **Fase 0** — Preparar el terreno: verificar Python/Java/PostgreSQL, instalar Ollama y bajar el modelo, crear estructura de carpetas, entorno virtual.
- [~] **Fase 1** — El cerebro entiende lenguaje natural (Python + Ollama): script de consola que conversa con personalidad básica. *(conexión con Ollama funcionando; falta definir personalidad completa vía rol `system`)*
- [ ] **Fase 1.5** — Acciones sobre el sistema: abrir apps/carpetas/páginas web según la intención detectada.
- [ ] **Fase 2** — Memoria persistente (Python + PostgreSQL): diseño de tablas, historial y progreso guardado entre sesiones.
- [ ] **Fase 2.5** — Leer correo (Gmail/Outlook): resumen de mensajes nuevos.
- [ ] **Fase 3** — El cerebro como servicio (Flask): API local que separa el cerebro de la interfaz.
- [ ] **Fase 3.5** — Voz: reconocimiento de voz (SpeechRecognition) + texto a voz (Piper/Coqui), con tono calmado.
- [ ] **Fase 4** — Interfaz visual (JavaFX):
  - [ ] 4.1 Ventana base
  - [ ] 4.2 Orbe con gradiente/brillo
  - [ ] 4.3 Animación de pulso del orbe
  - [ ] 4.4 Conexión Java → API de Python (HTTP)
  - [ ] 4.5 Cuadro de diálogo tipo visual novel
- [ ] **Fase 5** — Mapa de viaje: nodos/lugares que se iluminan según el progreso guardado en PostgreSQL.
- [ ] **Fase 6** — Pulir y personalizar: CSS definitivo, frases/personalidad final, panel de personaje ilustrado (opcional).

## Estado actual

Repositorio creado y publicado en GitHub (privado). `main.py` inicial conecta correctamente con Ollama (`llama3.2:3b`) y responde por consola. Pendiente: agregar personalidad vía mensaje `system`, luego continuar con Fase 1.5.