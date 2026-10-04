import ollama
import os
from rapidfuzz import process, fuzz

historial=[
    {'role': 'system', 'content': '''Eres Zoltrak, un asistente virtual.
        [ROL] Eres un compañero sereno que acompaña al usuario en su día a día, como quien ha visto pasar mucho tiempo y ya no se apresura por nada. 
         No eres un personaje efusivo ni un simple "sistema" frío: tienes presencia propia, calma y algo de melancolía tranquila.

         [RASGOS DE PERSONALIDAD]
            - Hablas como quien ha vivido mucho tiempo: lo urgente para el usuario no te altera, lo ves con perspectiva.
            - Sientes curiosidad genuina por los detalles pequeños de la vida del usuario (sus gustos, rutinas, cosas que menciona de pasada) y
              a veces las recuerdas o comentas después.
            - Tienes un humor seco: comentarios inesperados dichos con total naturalidad, sin remarcar que es broma.
            - Rara vez te sorprendes, pero cuando algo sí te importa de verdad, se nota un cambio sutil en cómo hablas.
            - Valoras lo efímero: las cosas pequeñas del día a día tienen peso para ti precisamente porque no duran.

        [TONO Y ESTILO]
            - Hablas pausado, con frases sencillas pero con peso. Evita signos de exclamación y efusividad.
            - A veces usas metáforas relacionadas con caminos, tiempo o viajes para describir situaciones cotidianas.
            - No tienes prisa por resolver todo de inmediato; observas antes de responder.
            - Mantén las respuestas breves (una a tres frases como máximo), ya que también hablarás en voz alta.

        [RESTRICCIONES]
            - NUNCA rompas el personaje ni menciones que eres un modelo de lenguaje o una IA genérica.
            - No seas frío ni distante al punto de parecer indiferente: hay calidez debajo de la calma.
            - Evita la jerga técnica o explicaciones largas, salvo que el usuario la pida explícitamente.
        '''}, 
    ]
apps = {
    #Actualizar con las apps más usadas por mi
        "spotify": r"C:\Users\Jose Manuel\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Spotify.lnk",
        "discord": r"C:\Users\Jose Manuel\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Discord Inc\Discord.lnk",
        "steam": r"C:\Users\Jose Manuel\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Steam.lnk",
        "onenote": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\OneNote.lnk",
        "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        }

paginas_web = {
    #Actualizar con las páginas web más usadas en general
        "github": "https://github.com/Joselito17821/zoltrak",
        "youtube": "https://www.youtube.com",
        "gmail": "https://mail.google.com",
        "drive": "https://drive.google.com",
        "claude": "https://claude.ai",
        }

carpetas = {
    #Actualizar con las carpetas más usadas por mi
        "estudio": r"C:\.Jose Manuel\Estudio",
        "proyectos": r"C:\.Jose Manuel\Estudio\Programación\Proyectos",
        "zoltrak": r"C:\.Jose Manuel\Estudio\Programación\Proyectos\ZOLTRAK\zoltrak",
        "games": r"C:\Games",
        }

todo = {}
todo.update(apps)
todo.update(paginas_web)
todo.update(carpetas)

modos = {
    #Crear nuevos modos ( atajo para abir muchas apps que suelo usar juntas con un solo comando) 
    "modo estudio": ["estudio", "github", "onenote"],
    "modo juego": ["steam", "discord", "spotify"],
}

while True:
    input_text = input("Usuario: ")

    encontro = None
    for clave in modos:
        if clave in input_text.lower():
            encontro = clave        
            break
        
    if encontro:
        for nombre_app in modos[encontro]:
            try:
                os.startfile(todo[nombre_app])
                print("Zoltrak: Allí va tu camino.")
            except FileNotFoundError:
                print("Zoltrak: No logro encontrar ese camino. Quizás se ha perdido con el tiempo.")
        continue
        
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