# main script for tts-deck-import
# andy wong

import json
from functions import *

# step 1: process decklist
# step 2: get collection from scryfall
# step 3: download card images
# step 4: stitch together card images for tts
# step 5: create json for tts

def main():

    # deckData, deckFrequency = processDecklist()
    # placeholder
    cardNames = ["bloodstained mire", "luxury suite", "lord windgrace", "swamp"]
    cardFrequency = [1, 1, 1, 40]
    cardData = cardCollection(cardNames)
    if cardData is None:
        print("end")
        return
    downloadImages(cardData)
    stitchImages()
    generateJSON(cardData)
    print("deck generated")

def processDecklist():
    return ""

def cardCollection(cardNames):

    collectionAllowable = 75
    collectionURL = "https://api.scryfall.com/cards/collection"
    collectionHeaders = {"Content-Type": "application/JSON"}

    chunks = chunkify(cardNames, 75)
    cardData = []
    failures = []

    for chunk in chunks:
        identifiers = [{"name": x} for x in chunk]

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

    # test success
    print("# failures: " + str(len(failures)) + "; " + str(failures))
    if len(failures) > 0: return None
    else: return cardData

def downloadImages(cardData):
    for x, cardInfo in enumerate(cardData):
        getpost(
            url = cardInfo["image_uris"]["normal"],
            filename = "images/" + str(x) + ".jpg"
        )

def stitchImages():
    return ""

def generateJSON(cardData):
    cardNames = [cardData[x]["name"] for x in range(len(cardData))]
    return ""

if __name__ == "__main__": main()
