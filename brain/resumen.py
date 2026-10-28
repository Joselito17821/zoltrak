import unicodedata
from email.utils import parseaddr

#Función para limpiar el texto de caracteres no deseados y recortarlo a un máximo de caracteres
def limpiar_texto(texto, maximo):
    # 1. Normalizar el texto con unicodedata.normalize("NFC", texto)
    texto = unicodedata.normalize("NFC", texto)
    # 2. Quedarse solo con los caracteres cuya categoría no empiece por "C" ni "M"
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



if __name__ == "__main__":
    print(limpiar_texto("Hola \u034f \u034f mundo", 200))
    print(len(limpiar_texto("a" * 500, 200)))
    print(nombre_remitente('LinkedIn <jobs@linkedin.com>'))
    print(nombre_remitente('<solo@correo.com>'))