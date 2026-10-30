import re
import unicodedata
from email.utils import parseaddr

import ollama
import personalidad

MAX_CONTENIDO = 200
MAX_ASUNTO = 120


# Función para limpiar el texto de caracteres no deseados y recortarlo a un máximo de caracteres
def limpiar_texto(texto, maximo):
    # 1. Normalizar el texto con unicodedata.normalize("NFC", texto)
    texto = unicodedata.normalize("NFC", texto)
    # 2. Quedarse solo con los caracteres cuya categoría no empiece por "C" ni "M"
    #    (los espacios en blanco se conservan para que el paso 3 los junte)
    texto = ''.join(c for c in texto if c.isspace() or not unicodedata.category(c).startswith(('C', 'M')))
    # 3. Juntar los espacios sobrantes
    texto = ' '.join(texto.split())
    # 4. Recortar a "maximo" caracteres y devolverlo
    return texto[:maximo]


# Función para obtener el nombre del remitente a partir de su dirección de correo
def nombre_remitente(remitente):
    # 1. Separar nombre y dirección con parseaddr
    nombre, direccion = parseaddr(remitente)
    # 2. Si hay nombre, devolverlo; si viene vacío, devolver la dirección
    return nombre if nombre else direccion


# Función para preparar los correos obtenidos de Gmail, limpiando el texto y recortando a un máximo de caracteres
def preparar_correos(correos):
    """Devuelve una lista NUEVA de diccionarios con nombre, asunto, fecha y contenido ya limpios.

    No modifica los diccionarios originales. Si un correo no trae contenido,
    su 'contenido' queda como texto vacío.
    """
    # 1. Crear una lista vacía para los correos preparados
    correos_preparados = []
    # 2. Recorrer los correos originales
    for correo in correos:
        # 2.1 Crear un diccionario NUEVO con los datos ya limpios
        correo_preparado = {
            'nombre': nombre_remitente(correo['remitente']),
            'asunto': limpiar_texto(correo['asunto'], MAX_ASUNTO),
            'fecha': correo['fecha'],
            'contenido': limpiar_texto(correo['snippet'], MAX_CONTENIDO),
        }
        # 2.2 Añadir el correo preparado a la lista
        correos_preparados.append(correo_preparado)
    # 3. Devolver la lista de correos preparados
    return correos_preparados


# Función para armar el texto numerado que se le manda al modelo, con De, Asunto, Fecha y Contenido
def armar_texto_correos(correos):
    # 1. Crear una lista vacía para las líneas
    lineas = []
    # 2. Recorrer los correos con su número (empezando en 1)
    for i, correo in enumerate(correos, start=1):
        # 2.1 Armar la línea con el formato acordado y añadirla a la lista
        lineas.append(f"{i}. De: {correo['nombre']} | Asunto: {correo['asunto']} | Fecha: {correo['fecha']} | Contenido: {correo['contenido']}")
    # 3. Unir las líneas con saltos de línea y devolver el texto
    return '\n'.join(lineas)


# Función para extraer las frases de la respuesta del modelo, que viene en líneas numeradas
def extraer_frases(texto):
    """Devuelve una lista con la frase de cada línea numerada, sin el número.

    Acepta '1.' y '1)', ignora introducciones y líneas en blanco.
    """
    # 1. Crear una lista vacía para las frases
    frases = []
    # 2. Separar el texto en líneas
    lineas = texto.splitlines()
    # 3. Recorrer las líneas
    for linea in lineas:
        # 3.1 Intentar sacar el número y la frase de la línea
        m = re.match(r"\s*(\d+)[.)]\s*(.*)", linea)
        # 3.2 Si la línea empieza con un número, añadir solo la frase (sin espacios sobrantes)
        if m:
            frases.append(m.group(2).strip())
    # 4. Devolver la lista
    return frases


# Función principal: resume los correos con Ollama y devuelve una frase por correo
def resumir_correos(correos):
    """Devuelve una lista con una frase por correo, en el mismo orden que 'correos'.

    - Un correo sin contenido lleva una frase vacía ('') para que main.py ponga la suya.
    - Si el modelo devuelve menos frases de las esperadas, se usa 'nombre: asunto'.
    - Devuelve None si Ollama no responde.
    """
    # 1. Preparar los correos (limpios y en diccionarios nuevos)
    preparados = preparar_correos(correos)
    # 2. Separar los que tienen contenido de los que no
    con_contenido = []
    for c in preparados:
        if c['contenido']:
            con_contenido.append(c)
    # 3. Si ninguno tiene contenido: una frase vacía por correo, sin llamar a Ollama
    if not con_contenido:
        return [""] * len(preparados)
    # 4. Armar el texto numerado SOLO con los que tienen contenido
    texto = armar_texto_correos(con_contenido)
    # 5. Llamar a Ollama; si falla, avisar y devolver None
    try:
        respuesta = ollama.chat(
            model='llama3.2:3b',  # mismo modelo que main.py
            messages=[
                {'role': 'system', 'content': personalidad.PERSONALIDAD + personalidad.TAREA_RESUMEN},
                {'role': 'user', 'content': "Correos:\n" + texto + "\n\nEscribe ahora el resumen: una frase corta por correo, sin copiar las líneas."},
            ],
            options={'temperature': 0.2, 'num_predict': 400},
        )
    except (ConnectionError, ollama.ResponseError) as error:
        print(f"Error al consultar Ollama: {error}")
        return None
    # 6. Extraer las frases de la respuesta del modelo
    frases = extraer_frases(respuesta['message']['content'])
    # 7. Armar la lista final en el orden original
    resultado = []
    indice = 0
    for c in preparados:
        if c['contenido']:
            # Con contenido: la siguiente frase del modelo, o un respaldo si ya no quedan
            if indice < len(frases):
                resultado.append(frases[indice])
            else:
                resultado.append(f"{c['nombre']}: {c['asunto']}")
            indice += 1
        else:
            # Sin contenido: frase vacía (main.py pondrá la suya)
            resultado.append("")
    # 8. Devolver la lista
    return resultado


# PRUEBA MANUAL (solo corre al ejecutar este archivo directamente)
if __name__ == "__main__":
    print(limpiar_texto("Hola \u034f \u034f mundo", 200))
    print(limpiar_texto("Hola\nmundo\tadiós", 200))
    print(len(limpiar_texto("a" * 500, 200)))
    print(nombre_remitente('LinkedIn <jobs@linkedin.com>'))
    print(nombre_remitente('<solo@correo.com>'))

    prueba = [
        {'remitente': 'LinkedIn <jobs@linkedin.com>', 'asunto': 'Nuevos empleos', 'fecha': '10 Oct 2026', 'snippet': 'Hay 5 \u034f empleos'},
        {'remitente': '<solo@correo.com>', 'asunto': 'Sin texto', 'fecha': '9 Oct 2026', 'snippet': ''},
    ]
    preparados = preparar_correos(prueba)
    print(preparados)
    print(repr(prueba[0]['snippet']))  # debe conservar el carácter invisible

    entrada = [
        {'nombre': 'LinkedIn', 'asunto': 'Nuevos empleos', 'fecha': '10 Oct 2026', 'contenido': 'Hay 5 empleos'},
        {'nombre': 'Google', 'asunto': 'Aviso de seguridad', 'fecha': '9 Oct 2026', 'contenido': 'Se inició sesión'},
    ]
    print(armar_texto_correos(entrada))
    print(repr(armar_texto_correos([])))

    print(extraer_frases("1. LinkedIn: avisa de empleos\n2. Google: avisa de un inicio de sesión"))
    print(extraer_frases("Aquí tienes el resumen:\n\n1) LinkedIn: avisa de empleos\n2) Google: aviso de seguridad"))
    print(extraer_frases("1) Google: aviso. Revisa tu cuenta"))
    print(extraer_frases(""))
    print(extraer_frases("Lo siento, no puedo resumir esto."))

    # --- Pruebas de resumir_correos (la primera llama a Ollama y puede tardar) ---
    correos_prueba = [
        {'remitente': 'LinkedIn <jobs@linkedin.com>', 'asunto': 'Nuevos empleos', 'fecha': '10 Oct 2026', 'snippet': 'Hay 5 empleos de diseño que encajan con tu perfil'},
        {'remitente': '<solo@correo.com>', 'asunto': 'Sin texto', 'fecha': '9 Oct 2026', 'snippet': ''},
        {'remitente': 'Google <noreply@google.com>', 'asunto': 'Alerta de seguridad', 'fecha': '9 Oct 2026', 'snippet': 'Se inició sesión en tu cuenta \u034f \u034f \u034f desde un dispositivo nuevo'},
        {'remitente': 'Universidad <ext@udea.edu.co>', 'asunto': 'Charla abierta', 'fecha': '8 Oct 2026', 'snippet': 'Te invitamos a la charla sobre seguridad alimentaria el próximo viernes a las 3 pm en el bloque 14. ' * 5},
        {'remitente': 'Banco <aviso@banco.com>', 'asunto': 'Extracto disponible', 'fecha': '7 Oct 2026', 'snippet': 'Tu extracto de septiembre ya está disponible'},
    ]
    print(resumir_correos(correos_prueba))
    print(resumir_correos([correos_prueba[1]]))