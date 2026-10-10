import ollama
from rapidfuzz import process, fuzz
import database
import config
import personalidad
import acciones
from correo import obtener_correos

PALABRAS_CORREO = {"correo", "correos", "gmail", "mail", "mails"}
PALABRAS_LEER = {"léeme", "leeme", "lee", "resúmeme", "resumeme", "resume",
                 "infórmame", "informame", "revisa", "dime", "tengo", "llegaron"}
PALABRAS_EJECUTAR = {"ejecutar", "haz esto", "haz aquello", "realiza esto", "realiza aquello", "abre", "abir"}
CLAVES_SALIR = {"salir", "adios", "chao", "bye", "hasta luego", "nos vemos", "adiós"}

# Se traduce el rol de los mensajes guardados en la base de datos a los roles que usa Ollama
mapa_roles = {'usuario': 'user', 'asistente': 'assistant'}

mensajes_guardados = database.obtener_historial_mensajes()

# Se cargan los mensajes guardados en la base de datos al historial de la personalidad
for rol, contenido in mensajes_guardados:
        rol_traducido = mapa_roles[rol]
        personalidad.historial.append({'role': rol_traducido, 'content': contenido})

while True:
    input_text = input("Usuario: ")
    if not input_text.strip():
        print("Zoltrak: No entendí eso, por favor escribe algo.")
        continue

    # --- Salida del programa (se revisa primero, antes de gastar ciclos en lo demás) ---
    if input_text.lower().strip() in CLAVES_SALIR:
        print("Zoltrak: Que tu camino sea tranquilo.")
        break

    # --- Correo (antes de rutinas y acciones) ---
    # Si el texto tiene una palabra de correo Y una palabra de lectura:
    if any(palabra in input_text.lower() for palabra in PALABRAS_LEER) and any(palabra in input_text.lower() for palabra in PALABRAS_CORREO):
        # Pedir los correos (con los valores por defecto)
        correos = obtener_correos()
        # Si es None: avisar que no se pudo revisar
        if correos is None:
            print("Zoltrak: No se pudieron obtener los correos.")
        # Si es una lista vacía: avisar que no hay correos
        elif not correos:
            print("Zoltrak: No encontré correos en tu bandeja principal.")
        # Si hay correos: mostrar remitente y asunto de cada uno
        else:
            print("Zoltrak: Estos son los correos que encontré:")
            for correo in correos:
                print(f"  - {correo['remitente']}: {correo['asunto']}")
        # continue
        continue

    # --- Rutinas (modo estudio, modo juego, etc.) ---
    # Busca si el texto contiene la frase completa de alguna rutina
    encontro = None
    for clave in config.modos:
        if clave in input_text.lower():
            encontro = clave        
            break
     # Abre cada app/carpeta/web que forme parte de la rutina encontrada
    if encontro:
        for nombre_app in config.modos[encontro]:
            acciones.abrir(config.todo[nombre_app])
        continue

    # --- Acciones puntuales (abrir una sola app/carpeta/web) ---   
    if any(palabra in input_text.lower() for palabra in PALABRAS_EJECUTAR):
        palabras_input = input_text.lower().split()
        encontro = None
        # Fuzzy matching: tolera errores de tecleo al buscar la clave en todo
        for palabra in palabras_input:
            match = process.extractOne(palabra, config.todo.keys(), scorer=fuzz.ratio, score_cutoff=80)
            if match:
                encontro = match[0]
                break

        if encontro:
            acciones.abrir(config.todo[encontro])
        else:
            print("Zoltrak: No reconozco ese camino.")
        continue

    # --- Conversación normal con Ollama ---
    personalidad.historial.append({'role': 'user', 'content': input_text})


    try:
        respuesta = ollama.chat(
        model='llama3.2:3b',
        messages=personalidad.historial
    )
    except ConnectionError:
        # Ollama no está corriendo (apagado o aún no inicia)
        print("Zoltrak: Estoy durmiendo, intenta más tarde.")
        # se saca el mensaje del usuario que quedó sin respuesta para no dejar el historial incompleto
        personalidad.historial.pop()
        continue

    database.guardar_mensajes('usuario', input_text)


    print("Zoltrak: " + respuesta['message']['content'])

    personalidad.historial.append(respuesta['message'])
    database.guardar_mensajes('asistente', respuesta['message']['content'])

  