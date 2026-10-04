apps = {
    #Actualizar con las apps más usadas por mi
        "spotify": r"C:\Users\Jose Manuel\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Spotify.lnk",
        "discord": r"C:\Users\Jose Manuel\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Discord Inc\Discord.lnk",
        "steam": r"C:\Users\Jose Manuel\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Steam\Steam.lnk",
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

# Diccionario único que junta apps, paginas_web y carpetas
todo = {}
todo.update(apps)
todo.update(paginas_web)
todo.update(carpetas)

modos = {
    #Crear nuevos modos ( atajo para abir muchas apps que suelo usar juntas con un solo comando) 
    "modo estudio": ["estudio", "github", "onenote"],
    "modo juego": ["steam", "discord", "spotify"],
}