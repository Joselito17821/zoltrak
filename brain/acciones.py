import os

"""Abre una app, carpeta o página web a partir de su ruta/URL."""
def abrir(ruta):
    try:
        os.startfile(ruta)
        print("Zoltrak: Allí va tu camino.")
    except FileNotFoundError:
        print("Zoltrak: No logro encontrar ese camino. Quizás se ha perdido con el tiempo.")