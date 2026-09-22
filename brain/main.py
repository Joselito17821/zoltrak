import ollama
import os
from rapidfuzz import process, fuzz

historial=[
    {'role': 'system', 'content': '''Eres Zoltrak, un asistente virtual.
    ...
    '''},
    ]
apps = {
        "spotify": r"C:\Users\Jose Manuel\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Spotify.lnk",
        "discord": r"C:\Users\Jose Manuel\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Discord Inc\Discord.lnk",
        "steam": r"C:\Users\Jose Manuel\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Steam.lnk",
        "onenote": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\OneNote.lnk",
        "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        }

paginas_web = {
        "github": "https://github.com/Joselito17821/zoltrak",
        "youtube": "https://www.youtube.com",
        "gmail": "https://mail.google.com",
        "drive": "https://drive.google.com",
        "claude": "https://claude.ai",
        }

carpetas = {
        "estudio": r"C:\.Jose Manuel\Estudio",
        "proyectos": r"C:\.Jose Manuel\Estudio\Programación\Proyectos",
        "zoltrak": r"C:\.Jose Manuel\Estudio\Programación\Proyectos\ZOLTRAK\zoltrak",
        "games": r"C:\Games",
        }

todo = {}
todo.update(apps)
todo.update(paginas_web)
todo.update(carpetas)

while True:
    input_text = input("Usuario: ")

    palabras_claves_para_ejecutar = ["ejecutar", "haz esto", "haz aquello", "realiza esto", "realiza aquello", "abre"]
    if any(palabra in input_text.lower() for palabra in palabras_claves_para_ejecutar):
        palabras_input = input_text.lower().split()
        encontro = None
        for palabra in palabras_input:
            match = process.extractOne(palabra, todo.keys(), scorer=fuzz.ratio, score_cutoff=80)
            if match:
                encontro = match[0]
                break

        if encontro:
            try:
                os.startfile(todo[encontro])
                print("Zoltrak: Allí va tu camino.")
            except FileNotFoundError:
                print("Zoltrak: No logro encontrar ese camino. Quizás se ha perdido con el tiempo.")
        else:
            print("Zoltrak: No reconozco ese camino.")
        continue

    clave_para_salir = ["salir", "adios", "chao", "bye", "hasta luego", "nos vemos", "adiós"]
    if input_text.lower().strip() in clave_para_salir:
        print("Zoltrak: Que tu camino sea tranquilo.")
        break

    historial.append({'role': 'user', 'content': input_text})

    try:
        respuesta = ollama.chat(
        model='llama3.2:3b',
        messages=historial
    )
    except ConnectionError:
        print("Zoltrak: Estoy durmiendo, intenta más tarde.")
        continue

    print("Zoltrak: " + respuesta['message']['content'])

    historial.append(respuesta['message'])