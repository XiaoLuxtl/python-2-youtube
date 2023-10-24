import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# Especifica los alcances necesarios para la API de YouTube
scopes = ['https://www.googleapis.com/auth/youtube.upload']

# Ruta al archivo JSON de credenciales
CREDENTIALS_FILE = 'client_secrets.json'  # desktop app

# Ruta al archivo JSON que contendrá el token de acceso
TOKEN_FILE = 'token.json'

# Ruta al archivo de video que deseas subir
video_file_path = 'test.mkv'

# Datos del video
video_title = TITLE
video_description = TTS_TEXT
video_tags = ['etiqueta1', 'etiqueta2']
privacy_status = 'unlisted'  # Puede ser 'public', 'private', o 'unlisted'

def get_authenticated_service():
    # Cargar o iniciar el flujo de autenticación
    creds = None
    # No está cargando bien el token habrá que ver
    # if os.path.exists(TOKEN_FILE):
    #     creds = Credentials.from_authorized_user_file(TOKEN_FILE, scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(InstalledAppFlow.get_authorization_url(scopes))
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, scopes=scopes)
            creds = flow.run_local_server(port=0)

        # Guardar las credenciales en un archivo para uso posterior
        with open(TOKEN_FILE, 'w') as token_file:
            token_file.write(creds.to_json())

    # Crear una instancia del servicio de YouTube
    youtube = build('youtube', 'v3', credentials=creds)
    return youtube

def initialize_upload(youtube, video_path, title, description, tags, privacy_status):
    tags = tags if tags else []
    body = {
        'snippet': {
            'categoryId': '22',  # Categoría de entretenimiento
            'title': title,
            'description': description,
            'tags': tags,
        },
        'status': {
            'privacyStatus': privacy_status
        }
    }

    # Iniciar la solicitud de carga
    insert_request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
    )

    # Ejecutar la carga
    response = resumable_upload(insert_request)
    video_id = response['id']
    print(f'Video subido con éxito. ID del video: {video_id}')

def resumable_upload(insert_request):
    response = None
    while response is None:
        try:
            print("Subiendo el video...")
            status, response = insert_request.next_chunk()
            if 'id' in response:
                return response
        except HttpError as e:
            if e.resp.status in [500, 502, 503, 504]:
                continue

# Ejecutar la función principal
youtube = get_authenticated_service()
# initialize_upload(youtube, video_file_path, video_title, video_description, video_tags, privacy_status)
