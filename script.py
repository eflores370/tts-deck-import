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

    cardNames, cardFrequency = processDecklist("testdecklist.txt")
    print(cardNames)
    print(cardFrequency)
    cardData, tokenData = cardCollection(cardNames)
    if cardData is None:
        print("end")
        return
    downloadImages(cardData)
    downloadImages(tokenData, token=True)
    stitchImages()
    generateJSON(cardData)
    print("deck generated")

def processDecklist(deckName):

    with open("decklists/" + deckName, "r") as deckFile:
        print("opening " + deckName)
        zippedCards = [tuple(line.rstrip().split(maxsplit=1)) for line in deckFile if line]
        cardFrequencyStr, cardNames = zip(*zippedCards)
        cardFrequency = [int(str) for str in cardFrequencyStr]
    return cardNames, cardFrequency

    return ""

def cardCollection(cardNames):

    # get card data
    cardData, failures = getbyfield("name", cardNames)

    # show failures, end run of code if any failures
    if len(failures) > 0:
        print("# failures: " + str(len(failures)) + "; " + str(failures))
        return None

    # check for tokens, get token data
    tokenIDs = [
        part["id"]
        for card in cardData if "all_parts" in card
        for part in card["all_parts"] if part["component"] == "token"
    ]
    tokenData, __ = getbyfield("id", tokenIDs)

    return (cardData, tokenData)

def downloadImages(cardData, token=False):
    append = "t" if token else ""
    for x, cardInfo in enumerate(cardData):
        getpost(
            url = cardInfo["image_uris"]["normal"],
            filename = ".temp/" + append + str(x) + ".jpg"
        )

def stitchImages():
    return ""

def generateJSON(cardData):
    cardNames = [cardData[x]["name"] for x in range(len(cardData))]
    return ""

if __name__ == "__main__": main()
