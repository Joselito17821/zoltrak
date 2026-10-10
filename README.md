# Zoltrak

Asistente virtual personal (estilo Jarvis), con personalidad calmada inspirada en la estética de Frieren, que entiende lenguaje natural y ejecuta acciones reales sobre el sistema.

Proyecto de aprendizaje: se construye paso a paso, sin que la IA resuelva las fases completas de golpe.

## Estado actual

Fase 2 (memoria persistente) completa. Fase 2.5 (lectura de correo de Gmail) en progreso: ya lee los últimos correos de la bandeja principal; falta el resumen con Ollama. Ver `docs/Zoltrak proyecto.md` para la ruta de desarrollo completa y las decisiones de arquitectura.

## Stack

- **brain/** — Python + Ollama (modelo `llama3.2:3b`, local) + API de Gmail (solo lectura)
- **ui/** — Java + JavaFX (aún no iniciado); se evaluará VTube Studio (API por WebSocket) como alternativa para el personaje ilustrado final
- **db/** — PostgreSQL (historial de conversación persistente)

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
 
Si el entorno virtual todavía no existe, créalo con `python -m venv venv`. Si ya existe la carpeta `venv`, puedes saltar ese paso.

```text
cd brain
python -m venv venv
venv\Scripts\activate
pip install -r ..\requirements.txt
python main.py
```

## Configurar la lectura de correo (opcional)

Zoltrak lee tu correo con la API de Gmail, en modo solo lectura (`gmail.readonly`): no puede enviar, borrar ni marcar mensajes. Si no configuras esto, el resto de Zoltrak funciona igual y solo falla la lectura de correo.

El archivo `credentials.json` identifica a la aplicación ante Google y **no viene en el repositorio** (cada quien crea el suyo). Para conseguirlo, en [Google Cloud Console](https://console.cloud.google.com) (los nombres de los menús pueden variar un poco):

1. Crea un proyecto (por ejemplo, `zoltrak`).
2. Activa la **Gmail API** en "APIs y servicios".
3. En **Google Auth Platform**, configura la pantalla de consentimiento: usuarios externos, modo **Testing**.
4. En **Público**, agrega tu correo como usuario de prueba.
5. En **Acceso a los datos**, agrega el permiso `.../auth/gmail.readonly` y guarda.
6. En **Clientes**, crea un cliente OAuth de tipo **App de escritorio** y descarga el JSON.
7. Renombra el archivo a `credentials.json` y colócalo en `brain/`.

La primera vez que pidas leer correos se abrirá el navegador para iniciar sesión. Google mostrará el aviso "no ha verificado esta aplicación" (es normal en modo Testing): pulsa **Avanzado** y continúa, y marca la casilla del permiso de correo. Con eso se genera solo `brain/token.json`.

Notas:

- `credentials.json` y `token.json` están en `.gitignore`. No los subas a ningún repositorio.
- En modo Testing, Google invalida el permiso a los **7 días**. No hay que hacer nada especial: Zoltrak abrirá el navegador de nuevo para reautorizar.
- Solo pueden usar la lectura de correo las cuentas agregadas como usuarios de prueba (hasta 100).

## Qué hace hoy

- Conversa con personalidad fija, con memoria persistente entre sesiones (PostgreSQL).
- Reconoce intención de acción ("abre X") y abre apps, páginas web o carpetas definidas en `config.py`.
- Reconoce rutinas ("modo estudio") que abren varias cosas a la vez.
- Tolera errores de tecleo en el nombre (`rapidfuzz`).
- No se cae si Ollama está apagado; avisa y sigue funcionando.
- Lee los últimos correos de tu bandeja principal ("revisa mis correos", "léeme mis últimos mensajes") y muestra remitente y asunto. No se cae si falla el login, la conexión o la API de Gmail.
- Abre Gmail en el navegador con "abre mis correos" (o "abre gmail").
- Ignora las entradas vacías: si pulsas Enter sin escribir nada, vuelve a pedir otra frase.

## Documentación

- `docs/Zoltrak proyecto.md` — objetivo, arquitectura, decisiones tomadas y ruta de fases.
- `docs/Funcionalidades Futuras.md` — funcionalidades evaluadas para más adelante (distribución, voces, personajes, etc.).
- `docs/aprendizajes.md` — conceptos de programación practicados en cada fase, como material de estudio.