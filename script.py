# main script for tts-deck-import
# andy wong

import json
from PIL import Image
from functions import *

# step 1: process decklist
# step 2: get collection from scryfall
# step 3: download card images
# step 4: stitch together card images for tts
# step 5: create json for tts

def main():

    deckName = "lordwimdy"
    cardNames, cardFrequency = processDecklist("lordwimdy.txt")
    cardData, tokenData = cardCollection(cardNames)
    if cardData is None:
        print("end")
        return
    downloadImages(cardData)
    downloadImages(tokenData, token=True)
    stitchImages(deckName, len(cardData), len(tokenData))
    generateJSON(cardData, tokenData)
    print("deck generated")

def processDecklist(deckName):

    with open("decklists/" + deckName, "r") as deckFile:
        print("opening " + deckName)
        zippedCards = [tuple(line.rstrip().split(maxsplit=1)) for line in deckFile if line.rstrip()]
        cardFrequencyStr, cardNames = zip(*zippedCards)
        cardFrequency = [int(str) for str in cardFrequencyStr]
    return cardNames, cardFrequency

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
        # if it's a transform card
        if "card_faces" in cardInfo:
            getpost(
                url = cardInfo["card_faces"][0]["image_uris"]["normal"],
                filename = ".temp/" + append + str(x) + ".jpg"
            )
            getpost(
                url = cardInfo["card_faces"][1]["image_uris"]["normal"],
                filename = ".temp/b" + append + str(x) + ".jpg"
            )
        else:
            getpost(
                url = cardInfo["image_uris"]["normal"],
                filename = ".temp/" + append + str(x) + ".jpg"
            )

def stitchImages(deckName, numCards, numTokens):

    # stitch card images into a 5x5 grid
    imageNames = [".temp/" + str(num) + ".jpg" for num in range(numCards)]
    chunks = chunkify(imageNames, 24)
    for i, chunk in enumerate(chunks):
        images = [Image.open(imageName) for imageName in chunk]
        width, height = images[0].size
        stitchedImage = Image.new("RGB", (5*width, 5*height))
        for j, image in enumerate(images):
            stitchedImage.paste(image, (j%5*width, int(j/5)*(height)))
        stitchedImage.save(".temp/_" + str(i) + ".jpg")

    # stitch token images


def generateJSON(cardData, tokenData):
    cardNames = [cardData[x]["name"] for x in range(len(cardData))]
    return ""

if __name__ == "__main__": main()
