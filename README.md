# Zoltrak

Asistente virtual personal (estilo Jarvis), con personalidad calmada inspirada en la estética de Frieren, que entiende lenguaje natural y ejecuta acciones reales sobre el sistema.

Proyecto de aprendizaje: se construye paso a paso, sin que la IA resuelva las fases completas de golpe.

## Estado actual

Fase 1.5 completa. Ver `Zoltrak proyecto.md` para la ruta de desarrollo completa y las decisiones de arquitectura.

## Stack

- **brain/** — Python + Ollama (modelo `llama3.2:3b`, local)
- **ui/** — Java + JavaFX (aún no iniciado); se evaluará VTube Studio (API por WebSocket) como alternativa para el personaje ilustrado final
- **db/** — PostgreSQL (aún no iniciado)

## Cómo correrlo

Requiere [Ollama](https://ollama.com) instalado con el modelo `llama3.2:3b` descargado (`ollama pull llama3.2:3b`).

```
cd brain
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Qué hace hoy

- Conversa con personalidad fija, manteniendo memoria de la sesión actual.
- Reconoce intención de acción ("abre X") y abre apps, páginas web o carpetas definidas en `main.py`.
- Tolera errores de tecleo en el nombre (`rapidfuzz`).
- No se cae si Ollama está apagado; avisa y sigue funcionando.

## Documentación

- `Zoltrak proyecto.md` — objetivo, arquitectura, decisiones tomadas y ruta de fases.
- `APRENDIZAJES.md` — conceptos de programación practicados en cada fase, como material de estudio.
