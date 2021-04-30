from Google import Create_Service
import pandas as pd
import os
import io
from googleapiclient.http import MediaIoBaseDownload
import uuid

CLIENT_SECRET_FILE = 'credentials.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

def download_folder(id,name):
    query = f"parents = '{id}'"
    response = service.files().list(q=query).execute()
    files = response.get('files')
    nextPageToken = response.get('nextPageToken')

    while nextPageToken:
        response = service.files().list(q=query).execute()
        files.extend(response.get('files'))
        nextPageToken = response.get('nextPageToken')

    df = pd.DataFrame(files)
    folder_ids = []
    folder_names = []
    file_ids = []
    file_names = []
    print(df)
    for x in range(len(df.index)):
        if(str(df.iloc[x]['mimeType']) == 'application/vnd.google-apps.folder'):
            folder_ids.append(str(df.iloc[x]['id']))
            folder_names.append(str(df.iloc[x]['name']))
    print("here")
    for folder_id, folder_name in zip(folder_ids, folder_names):
        download_folder(folder_id,os.path.join(name,folder_name))
    print("here2")
    for y in range(len(df.index)):
        if(str(df.iloc[y]['mimeType']) != 'application/vnd.google-apps.folder'):
            file_ids.append(str(df.iloc[y]['id']))
            file_names.append(str(df.iloc[y]['name']))
    download_files(file_ids,file_names,name)


def download_files(file_ids,file_names,path):
    for file_id, file_name in zip(file_ids, file_names):
        if not os.path.exists(path):
            os.makedirs(path)
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fd=fh, request=request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print('Download progess {0}'.format(status.progress() * 100))
            fh.seek(0)

        with open(os.path.join(path, file_name), 'wb') as f:
            f.write(fh.read())
            f.close()
        



with open('urlsToRead.txt','r') as fileDesc:
    Lines = fileDesc.readlines()
    count = 0
    for line in Lines:
        count += 1
        url = line.strip()
        folder_id = str(url).split('?')[0].split('/')[-1]
    download_folder(folder_id,os.path.join(os.getcwd(),folder_id))
        

