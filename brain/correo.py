
# 1. IMPORTAR LIBRERÍAS
#    (os, las clases de google-auth, google-auth-oauthlib y google-api-python-client)
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError, TransportError

# 2. CONSTANTES
#    - SCOPES: lista con el permiso gmail.readonly
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
#    - Ruta de credentials.json (junto a este archivo)
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), 'credentials.json')
#    - Ruta de token.json (junto a este archivo)
TOKEN_PATH = os.path.join(os.path.dirname(__file__), 'token.json')
#    - MAX_CORREOS: máximo de correos que se pueden pedir en una búsqueda
MAX_CORREOS = 10


# 3. FUNCIÓN obtener_servicio_gmail()
def obtener_servicio_gmail():
    """Devuelve el objeto de Gmail listo para usar, o None si el login falla."""
    # 3.1 Empezar con creds = None
    creds = None
    # 3.2 Si token.json existe -> cargarlo en creds
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    # 3.3 Si creds no existe o no es válida:
    if not creds or not creds.valid:
        # 3.3.1 Si caducó Y tiene refresh token:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except (RefreshError, TransportError):
                # Dejar creds = None para ir al login completo
                creds = None
        # 3.3.2 Si creds sigue sin existir (no había token, o falló la renovación):
        if not creds:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                print("Error durante el login: ", e)
                return None
        # 3.3.3 Guardar creds en token.json (solo si hubo renovación o login)
        with open(TOKEN_PATH, 'w') as token_file:
            token_file.write(creds.to_json())
    # 3.4 Construir el objeto de Gmail con las credenciales
    service = build('gmail', 'v1', credentials=creds)
    # 3.5 Devolver ese objeto
    return service


# 4. FUNCIÓN buscar_ids(servicio, cantidad=5, dias=None, remitente=None)
def buscar_ids(servicio, cantidad=5, dias=None, remitente=None):
    """Devuelve una lista con los id de los correos que cumplan los filtros.

    La búsqueda siempre se limita a la pestaña Principal y a un máximo de
    MAX_CORREOS resultados, aunque se pida una cantidad mayor. Si no hay
    resultados, devuelve una lista vacía.
    """
    # 4.0 Limitar la cantidad pedida al máximo permitido
    cantidad = min(cantidad, MAX_CORREOS)
    # 4.1 Armar el texto de búsqueda (q) como una lista de pedazos
    #     La parte fija: solo la pestaña Principal
    partes = ['category:primary']
    # 4.2 Si se pidió filtrar por días, agregar el filtro (ej. newer_than:3d)
    if dias:
        partes.append(f"newer_than:{dias}d")
    # 4.3 Si se pidió un remitente, agregarlo entre comillas dobles
    #     (así Gmail toma el nombre completo y no solo la primera palabra)
    if remitente:
        partes.append(f'from:"{remitente}"')
    # 4.4 Unir los pedazos con espacios para formar el texto final de búsqueda
    texto_q = " ".join(partes)
    # 4.5 Pedir a Gmail la lista de mensajes que cumplen la búsqueda
    #     (devuelve solo identificadores, no el contenido del correo)
    respuesta = servicio.users().messages().list(
        userId='me', q=texto_q, maxResults=cantidad
    ).execute()
    # 4.6 Sacar solo los id de la respuesta
    #     .get('messages', []) evita el error cuando no hay correos
    #     (en ese caso la clave 'messages' no existe)
    ids = []
    for mensaje in respuesta.get('messages', []):
        ids.append(mensaje['id'])
    # 4.7 Devolver la lista de id (vacía si no hubo resultados)
    return ids

# 5. FUNCIÓN leer_correos(servicio, id_correo)
def leer_correo(servicio, id_correo):
    """Devuelve un diccionario con remitente, asunto, fecha y snippet del correo."""
    mensaje = servicio.users().messages().get(
        userId='me', id=id_correo, format='metadata',
        metadataHeaders=['From', 'Subject', 'Date']
    ).execute()
    encabezados = {}
    for h in mensaje['payload']['headers']:
        encabezados[h['name']] = h['value']
    return {
        'remitente': encabezados.get('From', 'Remitente desconocido'),
        'asunto': encabezados.get('Subject', '(sin asunto)'),
        'fecha': encabezados.get('Date', 'Fecha desconocida'),
        'snippet': mensaje.get('snippet', '(sin snippet)'),
    }


#PRUEBA MANUAL (solo corre al ejecutar este archivo directamente)
if __name__ == "__main__":
    servicio = obtener_servicio_gmail()
    ids = buscar_ids(servicio, cantidad=3)
    for id_correo in ids:
        print(leer_correo(servicio, id_correo))