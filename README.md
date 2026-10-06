# Zoltrak

Asistente virtual personal (estilo Jarvis), con personalidad calmada inspirada en la estética de Frieren, que entiende lenguaje natural y ejecuta acciones reales sobre el sistema.

Proyecto de aprendizaje: se construye paso a paso, sin que la IA resuelva las fases completas de golpe.

## Estado actual

Fase 1.5 completa, Fase 2 (memoria persistente) en progreso. Ver `Zoltrak proyecto.md` para la ruta de desarrollo completa y las decisiones de arquitectura.

## Stack

- **brain/** — Python + Ollama (modelo `llama3.2:3b`, local)
- **ui/** — Java + JavaFX (aún no iniciado); se evaluará VTube Studio (API por WebSocket) como alternativa para el personaje ilustrado final
- **db/** — PostgreSQL (en progreso: historial de conversación persistente)

## Cómo correrlo en etapa de desarrollo
 
Requiere [Ollama](https://ollama.com) instalado con el modelo `llama3.2:3b` descargado (`ollama pull llama3.2:3b`), y [PostgreSQL](https://www.postgresql.org/) corriendo localmente con una base de datos creada a partir de `db/schema.sql`.
 
Crea un archivo `.env` en la raíz del proyecto con tus credenciales de PostgreSQL:
 
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=zoltrak
DB_USER=postgres
DB_PASSWORD=tu_contraseña
```
 
```
cd brain
venv\Scripts\activate
pip install -r ../requirements.txt
python main.py
```

## Qué hace hoy

- Conversa con personalidad fija, con memoria persistente entre sesiones (PostgreSQL).
- Reconoce intención de acción ("abre X") y abre apps, páginas web o carpetas definidas en `config.py`.
- Reconoce rutinas ("modo estudio") que abren varias cosas a la vez.
- Tolera errores de tecleo en el nombre (`rapidfuzz`).
- No se cae si Ollama está apagado; avisa y sigue funcionando.

## Documentación

- `Zoltrak proyecto.md` — objetivo, arquitectura, decisiones tomadas y ruta de fases.
- `APRENDIZAJES.md` — conceptos de programación practicados en cada fase, como material de estudio.
