# functions for tts-deck-import
# andy wong

import requests
import time
import json

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

def getbyfield(field, identifiers):

    # useful defines
    collectionAllowable = 75
    collectionURL = "https://api.scryfall.com/cards/collection"
    collectionHeaders = {"Content-Type": "application/JSON"}

    chunks = chunkify(identifiers, 75)
    cardData = []
    failures = []

    # for each chunk, get data on the collection of each chunk's cards
    # concat onto cardData, failures
    for chunk in chunks:
        identifiers = [{field: x} for x in chunk]

        collectionData = json.dumps({"pretty": False,
            "identifiers": identifiers
        })
        collection = getpost(
                url = collectionURL,
                data = collectionData,
                headers = collectionHeaders
        ).json()

        cardData += collection["data"]
        failures += collection["not_found"]

    return (cardData, failures)
