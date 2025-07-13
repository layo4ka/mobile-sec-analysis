import requests
import json

MOBSF_URL = "http://localhost:8000"
API_KEY = "0881f8b9935920c129af3664cf05a4ce77ac89bba7f3643fd09025caced57faa"

def upload_app(file_instance):
    headers = {"Authorization": API_KEY}
    uploadURL = f"{MOBSF_URL}/api/v1/upload"
    toPost = {"file":file_instance}
    response = requests.post(uploadURL, files=toPost, headers=headers)

    if response.status_code == 200:
        result = response.json()
        file_hash = result.get("hash")
        return file_hash
    return "Ошибка"

def static_analysis(file_hash):
    headers = {"Authorization": API_KEY}
    uploadURL = f"{MOBSF_URL}/api/v1/scan"
    toPost = {"hash":file_hash}
    response = requests.post(uploadURL, data=toPost, headers=headers)
    if response.status_code == 200:
        return response.json
    else:
        return "Ошибка"
