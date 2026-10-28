import unicodedata
from email.utils import parseaddr

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