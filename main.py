import os 
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/drive']

creds = None

if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
        
        
try:
    service = build('drive', 'v3', credentials=creds)
    
    response = service.files().list(
        q ="name= 'BackupFolder' and mimeType='application/vnd.google-apps.folder'",
        spaces='drive'
    ).execute()
    
    if not response.get('files'):
        file_metadata = {
            'name': 'BackupFolder',
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        file = service.files().create(body=file_metadata, fields='id').execute()
        
        folder_id = file.get('id')
    else:
        folder_id = response.get('files')[0].get('id')
        
    for file in os.listdir('backupfiles'):
        file_metadata = {
            "name" : file,
            "parents": [folder_id]
        }    
        
        media = MediaFileUpload(f"backupfiles/{file}")
        upload_file = service.files().create(body=file_metadata,
                                             media_body = media,
                                             fields= "id").execute()
        print("Backed up file: " + file)
    
        
except HttpError as e:
    print("Error: " + str(e)) 