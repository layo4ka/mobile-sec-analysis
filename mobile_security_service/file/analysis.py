import requests
import json

MOBSF_URL = "http://mobsf:8000"
API_KEY = "abf1e023d641ec0f8d1c5d1e723fb2e21d324ece74afd78d9d9bd354a110dc81"

#Для вывода
def dict_to_strings(d, parent_key='', separator=':'):
    result = []
    for k, v in d.items():
        new_key = f"{parent_key}{separator}{k}" if parent_key else k
        if isinstance(v, dict):
            result.extend(dict_to_strings(v, new_key, separator))
        else:
            result.append(f"{new_key}{separator}{v}")
    return result


def upload_app(file_instance, path):
    headers = {"Authorization": API_KEY}
    uploadURL = f"{MOBSF_URL}/api/v1/upload"
    toPost = {"file":(path, file_instance, 'application/octet-stream')}
    response = requests.post(uploadURL, files=toPost, headers=headers, timeout=20)

    if response.status_code == 200:
        result = response.json()
        file_hash = result.get("hash")
        return file_hash
    else:
        return f"Ошибка {response.status_code}; {response.json}; {response.text}"

def static_analysis(file_hash):
    headers = {"Authorization": API_KEY}
    uploadURL = f"{MOBSF_URL}/api/v1/scan"
    toPost = {"hash":file_hash}
    response = requests.post(uploadURL, data=toPost, headers=headers)
    if response.status_code == 200:
        return "Done"
    else:
        return f"Ошибка: {response.json}; {response.text}"

def get_results_report(status, file_hash):
    if(status == "Done"):

        headers = {"Authorization": API_KEY}
        uploadURL = f"{MOBSF_URL}/api/v1/report_json"
        toPost = {"hash":file_hash}
        response = requests.post(uploadURL, data=toPost, headers=headers)
        if response.status_code == 200:
            respJson = response.json()
            result={}

            result['Основная информация'] = {
                "Название приложения":respJson['app_name'],
                "Имя пакета":respJson['package_name'],
                "Размер приложения":respJson['size'],
                "Основная активность":respJson['main_activity'],
                "Версия":respJson['version']
            }
            services={}
            for i in range(len(respJson['services'])):
                services.update({f"{i+1})":f"{respJson['services'][i]}"})
            result['Сервисы']=services
            permissions={}
            for x in respJson['permissions']:
                perm={"Имя разрешения":x, "Безопасность разрешения":respJson['permissions'].get(x).get('status')}
                permissions.update(perm)
            result['Разрешения'].update(permissions)

            trackers={}
            trackers.update({"Всего трекеров":respJson['trackers']['total_trackers'], "Засечённых трекеров":respJson['trackers']['detected_trackers']})
            for x in respJson['trackers']['trackers']:
                tracker = {"Название":x['name'], "Категория":x['categories']}
                trackers.update(tracker)
            result['Трекеры']=trackers
            appsec=respJson['appsec']   
            result['Безопасность']={"Оценка безопасности":f"{appsec['security_score']}/100"}
            if(f"{respJson['virus_total']}"=="null"):
                result['Вирусы']={"Всего вирусов":0}
            else:
                result['Вирусы']={"Всего вирусов":respJson['virus_total']}
            finalResult=dict_to_strings(result)

            return finalResult
        else:
            return f"Ошибка: {response.status_code}; {response.text}"
    else:
        return status

def get_report_pdf(status, file_hash):
    if(status=="Done"):
        headers = {"Authorization": API_KEY}
        uploadURL = f"{MOBSF_URL}/api/v1/download_pdf"
        toPost = {"hash":file_hash}
        response = requests.post(uploadURL, data=toPost, headers=headers)
        if response.status_code==200:
            pass
    else:
        return status
    

#Фигня какая-то честно говоря, но удалять не буду, пусть здесь пока побудет.

# def get_scan_results(status, file_hash):
#     if(status=="Done"):
#         headers = {"Authorization": API_KEY}
#         uploadURL = f"{MOBSF_URL}/api/v1/search"
#         toPost = {"hash":file_hash}
#         response = requests.post(uploadURL, data=toPost, headers=headers)
#         if response.status_code == 200:
#             return json.dumps(response.json, indent=4, ensure_ascii=False)
#     else:
#         return f"Ошибка: {response.status_code}; {response.text}"
