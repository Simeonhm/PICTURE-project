import os
import glob

# Vervang 'jouwMapPad' met het pad naar de map waar je de ZIP-bestanden wilt verwijderen
map_pad = '/Users/simeonhailemariam/Downloads/archive/BraTS2021_Training_Data'

# Creëert een pad dat verwijst naar alle ZIP-bestanden in de map
zip_bestanden_pad = os.path.join(map_pad, '*.zip')

# Vindt alle ZIP-bestanden in de map
zip_bestanden = glob.glob(zip_bestanden_pad)

# Gaat door elk ZIP-bestand en verwijdert het
for zip_bestand in zip_bestanden:
    try:
        os.remove(zip_bestand)
        print(f'Verwijderd: {zip_bestand}')
    except Exception as e:
        print(f'Fout bij het verwijderen van {zip_bestand}: {e}')

print("Klaar met het verwijderen van alle ZIP-bestanden.")

#--------------------------------------------------------------------------


import requests
import re
import os
from zipfile import ZipFile
import subprocess
import time

def login_get_api_key(login_url, email, password):
    data = {'email': email, 'password': password}
    response = requests.post(login_url, data=data)

    
    if response.status_code == 200:
        print('Het POST-verzoek 1 was succesvol!')
        match = re.search(r'"apiKey":"([^"]+)"', response.text)
        if match:
            api_key = match.group(1)
            return api_key
        else:
            print("Kon de API key niet extraheren uit de response.")
            return None
           
    else:
        print('Er is een fout opgetreden bij het doen van het POST-verzoek.')
        print(response.text)
        return None

def zip_subfolder(folder):
    zip_name = f"{folder}.zip"
    with ZipFile(zip_name, 'w') as zipObj:
        for foldername, subfolders, filenames in os.walk(folder):
            for filename in filenames:
                filePath = os.path.join(foldername, filename)
                zipObj.write(filePath, os.path.relpath(filePath, folder))
    print(f"{zip_name} gemaakt.")
    return zip_name

def segmentatie_bestand_bestaat(extracted_name, documenten_folder):
    segmentatie_bestand = f'{documenten_folder}/{extracted_name}_segmentation.nii'
    return os.path.exists(segmentatie_bestand)

def upload_brain_map(upload_url, bestandspad, api_key):
    headers = {'Authorization': f'Bearer {api_key}'}
    with open(bestandspad, 'rb') as bestand:
        files = {'file': (os.path.basename(bestandspad), bestand, 'application/zip')}
        response = requests.post(upload_url, files=files, headers=headers)
        
    if response.status_code == 201:
        print(f'{os.path.basename(bestandspad)} succesvol geüpload!')
        
        # Extract de noodzakelijke informatie
        extracted_name = re.search(r'BraTS2021_Training_Data/(.*?)\.zip', bestandspad).group(1) if re.search(r'BraTS2021_Training_Data/(.*?)\.zip', bestandspad) else "Onbekend"
        upload_id = re.search(r'"uploadId":"([^"]+)"', response.text).group(1) if re.search(r'"uploadId":"([^"]+)"', response.text) else "Onbekend"

        return extracted_name, upload_id
    else:
        print(f'Fout bij het uploaden van {os.path.basename(bestandspad)}: {response.status_code}')
        print(response.text)
        return "Onbekend", "Onbekend", "Onbekend"    

    # if response.status_code == 201:
    #     print(f'{os.path.basename(bestandspad)} succesvol geüpload!')
        
    #     # Voer de zoekopdracht uit om de gewenste deel uit zip_name te halen
    #     match = re.search(r'BraTS2021_Training_Data/(.*?)\.zip', bestandspad)
    #     if match:
    #         extracted_name = match.group(1)
    #         print(f"Gevonden deel: {extracted_name}")
    #         return extracted_name
    #     else:
    #         print("Geen overeenkomst gevonden voor de naam extractie.")

    #     # Zoek naar het uploadId in de response
    #     match_upload = re.search(r'"uploadId":"([^"]+)"', response.text)
    #     if match_upload:
    #         upload_id = match_upload.group(1)
    #         print(f'Upload ID: {upload_id} .')
    #         return upload_id
    #     else:
    #         print('Upload ID kon niet worden gevonden in de response.')
    #         upload_id = None

    #     # Zoek naar het brainMapId in de response
    #     match_brain = re.search(r'"brainMapId":"([^"]+)"', response.text)
    #     if match_brain:
    #         brain_map_id = match_brain.group(1)
    #         print(f'Brain Map ID: {brain_map_id}')
    #         return brain_map_id
    #     else:
    #         print('Brain Map ID kon niet worden gevonden in de response.')
    #         brain_map_id = None

    # else:
    #     print(f'Fout bij het uploaden van {os.path.basename(bestandspad)}: {response.status_code}')
    #     print(response.text)
    #     return None, None


def update_brain_map_info(upload_id, api_key, data):
    put_url = f'https://tool.pictureproject.nl/api/brain-maps/upload-segmented/{upload_id}'
    headers = {'Authorization': f'Bearer {api_key}'}
    
    while True:
        # Voer het PUT-verzoek uit
        put_response = requests.put(put_url, json=data, headers=headers)
        
        if put_response.status_code == 200:
            print(f"PUT-verzoek succesvol uitgevoerd voor upload ID: {upload_id}")
            
            # Analyseer de respons om te zien of niftiMetadata en anonymizedNiftiFileURL gevuld zijn
            niftiMetadata_filled = re.search(r'"niftiMetadata":\s*\[.+?\]', put_response.text)
            anonymizedNiftiFileURL_filled = re.search(r'"anonymizedNiftiFileURL":\s*".+?"', put_response.text)
            
            if niftiMetadata_filled and anonymizedNiftiFileURL_filled:
                print("niftiMetadata en anonymizedNiftiFileURL zijn nu gevuld.")
                break  # Beëindig de lus als de data gevuld is
            else:
                print("niftiMetadata en anonymizedNiftiFileURL zijn nog steeds leeg. Proberen opnieuw na een pauze...")
                time.sleep(60)  # Wacht 60 seconden voordat je het opnieuw probeert
        else:
            print(f"Fout bij het uitvoeren van het PUT-verzoek: {put_response.status_code}, {put_response.text}")
            break  # Beëindig de lus bij een fout tijdens PUT
    
def perform_get_request(api_key):
    url = 'https://tool.pictureproject.nl/api/brain-maps/upload'
    headers = {'Authorization': f'Bearer {api_key}'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        try:
            response_json = response.json()
            print('Het GET-verzoek was succesvol!')
            print(response_json)
            return response_json
        except ValueError:  # Inclusief JSONDecodeError
            print("Kan response niet omzetten naar JSON.")
            return None
    else:
        print(f'Er is een fout opgetreden bij het doen van het GET-verzoek. Statuscode: {response.status_code}')
        print(response.text)
        return None

def extract_file_ids_from_response(response_json):
    try:
        file_ids = {'selectedFLAIRFileId': None, 'selectedT1wFileId': None, 'selectedT1cFileId': None, 'selectedT2wFileId': None}
        
        for file in response_json['data']['niftiMetadata']:
          if '_t1ce' in file['fileName'].lower():
            file_ids['selectedT1cFileId'] = file['fileId']  
          elif '_t1' in file['fileName'].lower():
            file_ids['selectedT1wFileId'] = file['fileId']                      
          elif 'flair' in file['fileName'].lower():
            file_ids['selectedFLAIRFileId'] = file['fileId']
          elif '_t2' in file['fileName'].lower():
            file_ids['selectedT2wFileId'] = file['fileId']   
        print(file_ids)
                
        # Controleer of we alle benodigde file IDs hebben gevonden
        if None in file_ids.values():
            print("Niet alle benodigde file IDs zijn gevonden.")
            return None
        return file_ids
    except KeyError:
        print("De verwachte datastructuur komt niet overeen met de response.")
        return None
    
def apply_auto_segmentation(upload_id, api_key, file_ids, data):
    if not file_ids:  # Controleer of file_ids niet None is
        print("Geen geldige file IDs doorgegeven aan apply_auto_segmentation.")
        return
    print(upload_id)
    print(api_key2)
    print(data)
    url = f'https://tool.pictureproject.nl/api/brain-maps/upload/{upload_id}'
    headers = {'Authorization': f'Bearer {api_key}'}
    response = requests.put(url, json=data, headers=headers)
    
    if response.status_code == 200:
        print("Automatische segmentatie succesvol toegepast.")
        print(response.text)
        match_brain = re.search(r'"brainMapId":"([^"]+)"', response.text)
        brain_map_id = match_brain.group(1) if match_brain else None
        print(brain_map_id)
        return brain_map_id
    else:
        print(f"Fout bij het toepassen van automatische segmentatie: {response.status_code}")
        print(response.text)
        

# def get_brain_maps(api_key, param, data):
#     url = f'https://tool.pictureproject.nl/api/brain-map/{param}'
#     headers = {'Authorization': f'Bearer {api_key}'}
#     response = requests.get(url, json=data, headers=headers)
    
#     if response.status_code == 200:
#         print('gelukt met get!')
#         print(response.text)
#         match_segmentation_url = re.search(r'"segmentationFileURL":"([^"]+)"', response.text)
#         segmentation_url = match_segmentation_url.group(1) if match_segmentation_url else None
#         print(segmentation_url)
#         return segmentation_url
#     else:
#         print(f"Fout bij het uitvoeren van het GET-verzoek met brain map id. Status code: {response.status_code}")
#         print("Foutbericht:", response.text)
#         return None, None
    
# def get_brain_maps(api_key, param, data):
#     url = f'https://tool.pictureproject.nl/api/brain-map/{param}'
#     headers = {'Authorization': f'Bearer {api_key}'}

#     while True:
#         response = requests.get(url, json=data, headers=headers)
        
#         if response.status_code == 200:
#             print('Antwoord van get_brain_maps ontvangen.')
#             print(response.text)

#             # Zoek naar lowResBrainMap en highResBrainMap in de response tekst
#             lowResBrainMap_search = re.search(r'"lowResBrainMap":("([^"]+)"|null)', response.text)
#             highResBrainMap_search = re.search(r'"highResBrainMap":("([^"]+)"|null)', response.text)

#             if lowResBrainMap_search and highResBrainMap_search:
#                 lowResBrainMap = lowResBrainMap_search.group(2)
#                 highResBrainMap = highResBrainMap_search.group(2)

#                 if lowResBrainMap is not None and highResBrainMap is not None:
#                     print('lowResBrainMap en highResBrainMap zijn nu gevuld.')
#                     # Zoek naar segmentationFileURL in de response tekst
#                     match_segmentation_url = re.search(r'"segmentationFileURL":"([^"]+)"', response.text)
#                     segmentation_url = match_segmentation_url.group(1) if match_segmentation_url else None
#                     return segmentation_url
#                 else:
#                     print("lowResBrainMap en highResBrainMap zijn nog steeds null. Wachten en opnieuw proberen...")
#                     time.sleep(60)  # Wacht 60 seconden voordat je het opnieuw probeert
#             else:
#                 print("Kon lowResBrainMap of highResBrainMap niet vinden in de respons. Wachten en opnieuw proberen...")
#                 time.sleep(60)  # Mogelijk een probleem met de respons structuur; wacht en probeer opnieuw
#         else:
#             print(f"Fout bij het uitvoeren van het GET-verzoek met brain map id. Status code: {response.status_code}")
#             print("Foutbericht:", response.text)
#             return None

def get_brain_maps(api_key, param, data):
    url = f'https://tool.pictureproject.nl/api/brain-map/{param}'
    headers = {'Authorization': f'Bearer {api_key}'}
    start_time = time.time()  # Starttijd vastleggen

    while True:
        # Controleer of 5 minuten zijn verstreken
        if time.time() - start_time > 300:  # 300 seconden = 5 minuten
            print("De get request duurde langer dan 5 minuten.")
            return None
        
        response = requests.get(url, json=data, headers=headers)
        
        if response.status_code == 200:
            print('Antwoord van get_brain_maps ontvangen.')
            response_data = response.json()  # Zet de respons om naar een dictionary
            print(response_data)
            
            # Controleer of 'lowResBrainMap' en 'highResBrainMap' bestaan en niet None zijn
            if 'lowResBrainMap' in response_data['data'] and response_data['data']['lowResBrainMap'] is not None and \
               'highResBrainMap' in response_data['data'] and response_data['data']['highResBrainMap'] is not None:
                print('lowResBrainMap en highResBrainMap zijn nu gevuld.')
                
                # Als segmentationFileURL aanwezig is, retourneer deze
                if 'segmentationFileURL' in response_data['data']['lowResBrainMap']:
                    segmentation_url = response_data['data']['lowResBrainMap']['segmentationFileURL']
                    print(f'Segmentatie URL gevonden: {segmentation_url}')
                    return segmentation_url
                else:
                    print("Segmentatie URL niet gevonden in lowResBrainMap.")
                    return None
            else:
                print("lowResBrainMap en highResBrainMap zijn nog steeds leeg. Proberen opnieuw na een pauze...")
                time.sleep(60)  # Wacht 60 seconden voordat je het opnieuw probeert
        else:
            print(f"Fout bij het uitvoeren van het GET-verzoek met brain map id. Status code: {response.status_code}")
            print("Foutbericht:", response.text)
            return None

        
def download_output_naar_lokale_pc(browser_like, segmentation_url, extracted_name): 
    # Verwijder alle backslashes uit de URL
    clean_url = segmentation_url.replace('\\', '')
    print('De clean url is:', clean_url)

    # Stel het lokale pad in waar het bestand opgeslagen moet worden
    local_file_path = f'/Users/simeonhailemariam/Documents/{extracted_name}_segmentation.nii'

    # Bouw het commando om het bestand te downloaden
    if browser_like:
        command = ['curl', clean_url, '-o', local_file_path]
    else:
        command = ['wget', clean_url, '-O', local_file_path]

    # Voer het commando uit
    try:
        subprocess.run(command, check=True)
        print(f'Download voltooid en opgeslagen op: {local_file_path}')
    except subprocess.CalledProcessError as e:
        print(f'Fout bij het downloaden van het bestand: {e}')   
        
def delete_get_brain_maps(api_key, param):
    url = f'https://tool.pictureproject.nl/api/brain-map/{param}'
    headers = {'Authorization': f'Bearer {api_key}'}
    response = requests.delete(url, json=data, headers=headers)
    
    if response.status_code == 200:
        print('succesvol verwijderd!')
        print(response.text)
    else:
        print(f"Fout bij het verwijderen van de brain map. Status code: {response.status_code}")
        print("Foutbericht:", response.text)
        return None, None
    
# def delete_zip_file(zip_file_path):
#     try:
#         os.remove(zip_file_path)
#         print(f"Verwijderd: {zip_file_path}")
#     except Exception as e:
#         print(f"Fout bij het verwijderen van {zip_file_path}: {e}")
    
# De workflow van het script
parent_folder = '/Users/simeonhailemariam/Downloads/archive/BraTS2021_Training_Data'  # Pas dit aan naar de locatie van de hoofdmap
login_url = 'https://tool.pictureproject.nl/api/user/login'  # Pas dit aan naar de werkelijke login URL
upload_url = 'https://tool.pictureproject.nl/api/brain-maps/upload'  # Pas dit aan naar de werkelijke upload URL
email = 'simeon.hm@hotmail.com'  # Pas dit aan naar de werkelijke e-mail
password = 'Simeon890'  # Pas dit aan naar het werkelijke wachtwoord
login_url2 = 'https://tool.pictureproject.nl/api/user/login'  # Pas dit aan naar de werkelijke login URL
email2 = 'simeon@activecollective.nl'
password2 = '*V9jLMy^RiHjJQIW'

# Hier invullen: Vervang dit met de daadwerkelijke data die nodig is voor het PUT-verzoek
data = {
    # Voorbeeld data, pas dit aan aan jouw vereisten
    # Vul de velden in met logische waarden
    "uploadId": "{upload_id}",
    "age": 35,
    "GBM": "Type A",
    "brainMapClassification": "Class 1",
    "sharedBrainMap": True,
    "isResearch": False,
    "folderName": "My brain maps",  # Alleen invullen als het een atlas is
    "brainMapName": "Patient Brain Map",
    "brainMapNotes": "Patient's brain map notes",
    "mriDate": "2024-03-21",
    #"lowResBrainMapFileURL": "http://localhost:90/lowres_map",
    #"highResBrainMapFileURL": "http://localhost:90/highres_map"
}

api_key = login_get_api_key(login_url, email, password)
api_key2 = login_get_api_key(login_url2, email2, password2)

# if api_key:
#     print("API key succesvol verkregen.")
#     zip_files = zip_subfolders(parent_folder)
#     for zip_file in zip_files:
#         upload_id = upload_brain_map(upload_url, zip_file, api_key)
#         if upload_id:
#             update_brain_map_info(upload_id, api_key, data)
#             # Voorbeeld van hoe je deze functies in de workflow zou kunnen opnemen
#             response_json = perform_get_request(api_key)  # Zorg ervoor dat deze functie nu een JSON-object retourneert
#             file_ids = extract_file_ids_from_response(response_json)
#             apply_auto_segmentation(upload_id, api_key, file_ids)

# if api_key:
#     print("API key succesvol verkregen.")
#     zip_files = zip_subfolders(parent_folder)
#     for zip_file in zip_files:
#         upload_id = upload_brain_map(upload_url, zip_file, api_key)
#         if upload_id:
#             update_brain_map_info(upload_id, api_key, data)
documenten_folder = '/Users/simeonhailemariam/Documents'  # Definieer de map waar de segmentatiebestanden worden opgeslagen  
         
# Workflow implementatie
if api_key2:
    print("API key succesvol verkregen.")
    subfolders = [f.path for f in os.scandir(parent_folder) if f.is_dir()]
    print(f"Subfolders gevonden: {len(subfolders)}")

    for folder in subfolders[19:121]:
        print(f"Verwerken van: {folder}")
        zip_file = zip_subfolder(folder)
        extracted_name = os.path.basename(zip_file)[:-4]  # Verwijder '.zip' van de bestandsnaam

        if not segmentatie_bestand_bestaat(extracted_name, documenten_folder):
            print(f"Segmentatiebestand bestaat niet, doorgaan met verwerking voor: {extracted_name}")
            extracted_name, upload_id = upload_brain_map(upload_url, zip_file, api_key2)
            if upload_id != "Onbekend":
                print(f"Upload ID verkregen: {upload_id}, doorgaan met bijwerken van informatie.")
                update_brain_map_info(upload_id, api_key2, data)
                response_json = perform_get_request(api_key2)
                if response_json:
                    file_ids = extract_file_ids_from_response(response_json)
                    if file_ids:
                        data = {
                            "uploadId": upload_id,  # Zorg ervoor dat de variabele upload_id hier correct is gedefinieerd
                            "applyAutoSegmentation": True,
                            "selectedFLAIRFileId": file_ids['selectedFLAIRFileId'], 
                            "selectedT1wFileId": file_ids['selectedT1wFileId'], 
                            "selectedT1cFileId": file_ids['selectedT1cFileId'], 
                            "selectedT2wFileId": file_ids['selectedT2wFileId']
                        }                        
                        print(f"File IDs verkregen, toepassen van automatische segmentatie.")
                        brain_map_id = apply_auto_segmentation(upload_id, api_key2, file_ids, data)
                        if brain_map_id: 
                            data = {
                                "param": brain_map_id  # Zorg ervoor dat de variabele upload_id hier correct is gedefinieerd
                            }   
                            segmentation_url = get_brain_maps(api_key2, brain_map_id, data)
                            if segmentation_url:
                                print(f"Segmentatie URL verkregen: {segmentation_url}, downloaden naar lokale PC.")
                                download_output_naar_lokale_pc(True, segmentation_url, extracted_name)
                                # delete_get_brain_maps(api_key2, brain_map_id)
                            else:
                                print("Kon de segmentatie URL niet ophalen.")
                    else:
                        print("Kon file IDs niet extraheren uit de response.")
                else:
                    print("Kon geen response JSON verkrijgen van de server.")
            else:
                print("Upload ID is onbekend, kan geen verdere acties uitvoeren.")
        else:
            print(f"Segmentatiebestand voor {extracted_name} bestaat al, wordt overgeslagen.")

        #delete_zip_file(zip_file)
        time.sleep(10)  # Pauzeer voor 20 minuten
else:
    print("Kon geen API key verkrijgen.")  
    
    
    
