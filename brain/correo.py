# correo.py — Autenticación con Gmail (solo lectura)

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

# 3. FUNCIÓN obtener_servicio_gmail()
def obtener_servicio_gmail():
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

if __name__ == "__main__":
    servicio = obtener_servicio_gmail()
    print(servicio)