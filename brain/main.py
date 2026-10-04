import ollama
from rapidfuzz import process, fuzz
import config
import personalidad
import acciones

PALABRAS_EJECUTAR = {"ejecutar", "haz esto", "haz aquello", "realiza esto", "realiza aquello", "abre"}
CLAVES_SALIR = {"salir", "adios", "chao", "bye", "hasta luego", "nos vemos", "adiós"}

while True:
    input_text = input("Usuario: ")

    # --- Salida del programa (se revisa primero, antes de gastar ciclos en lo demás) ---
    if input_text.lower().strip() in CLAVES_SALIR:
        print("Zoltrak: Que tu camino sea tranquilo.")
        break

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

    print("Zoltrak: " + respuesta['message']['content'])

    personalidad.historial.append(respuesta['message'])