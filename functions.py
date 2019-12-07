# functions for tts-deck-import
# andy wong

import requests
import time

def getpost(url, data = None, headers = None, filename = None):
    if data is None:
        response = requests.get(url)
    else:
        response = requests.post(url, data = data, headers = headers)
    time.sleep(0.1)
    if filename is None:
        return response
    else:
        with open(filename, "wb") as file:
            file.write(response.content)

def chunkify(arr, size):
    return [arr[x:x + size] for x in range(0, len(arr), size)]
