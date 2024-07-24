import requests
import os

def downloadFile(url : str): 
    print("downloading document")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    file_name = os.path.basename(url)
    print(f"FileName : {file_name}")
    
    if not os.path.exists("./files"):
        os.makedirs("files")
    destination_directory = "./files/"
    file_path = os.path.join(destination_directory,  file_name)
    response = requests.get(url, headers=headers)
    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_path