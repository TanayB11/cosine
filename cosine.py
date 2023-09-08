import os, argparse
import requests, urllib
import shutil, json
from tabulate import tabulate
import textwrap

API_URL = 'http://localhost:8000/api'

def upload(vault_location) -> None:
    # Zip directory to a file
    zip_filename = 'cosine_temp'
    shutil.make_archive(zip_filename, 'zip', vault_location)

    # Make POST request to upload zip file
    with open(f'{zip_filename}.zip','rb') as zipped: # streamed for large files
        files=[ ('directory', (f'{zip_filename}.zip', zipped, 'application/zip')) ]

        response = requests.post(f'{API_URL}/reindex/', files=files)

        if response.status_code != 200:
          print('Upload failed with status code:', response.status_code)

    # Delete zip file
    os.remove(f'{zip_filename}.zip')

def search(query: str):
    payload = json.dumps({ "query": query })
    headers =  { 'Content-Type': 'application/json' }
    response = requests.request("POST", f'{API_URL}/query/', headers=headers, data=payload)
    
    if response.status_code != 200:
      print('Upload failed with status code:', response.status_code)

    # print(json.loads(response.text)['message']['documents'][0][0])
    return json.loads(response.text)['message']

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["upload", "search"])
    parser.add_argument("query", nargs="?")
    args = parser.parse_args()

    if args.command == "upload":
        if (args.query != None):
            upload(args.query)
        else:
            print("No vault directory provided")
    elif args.command == "search":
        if args.query:
            results = search(args.query)

            term_width = os.get_terminal_size().columns
            messages = [
                {
                    "File": results['metadata'][idx].split('/')[-1],
                    # "File": f"obsidian://advanced-uri?vault=Obsidian&filepath={urllib.parse.quote(results['metadatas'][0][idx]['source'].split('uploads/decompressed/')[-1], safe='')}",
                    "Text": textwrap.fill(message, width=int(term_width * 2//3))
                }
              for (idx, message) in enumerate(results['text'])
            ]
            headers = {"ID": "ID", "Message": "Message"}
            table = tabulate(messages, headers=headers, tablefmt="grid")
            print(table, "\n")
        else:
            print("No search query provided")

if __name__ == '__main__':
    main()

