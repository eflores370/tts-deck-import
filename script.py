# main script for tts-deck-import
# andy wong

import json
from shutil import copyfile
from functions import *

# step 1: process decklist
# step 2: get collection from scryfall
# step 3: download card images
# step 4: stitch together card images for tts
# step 5: create json for tts

def main():

    deckName = "thrasiossmash"
    cardNames, cardFrequency = processDecklist("thrasiossmash.txt")
    cardData, tokenData = cardCollection(cardNames)
    if cardData is None:
        print("end")
        return
    flipCardNums = downloadImages(cardData)
    flipCardNums += downloadImages(tokenData, token=True)
    stitchImages(deckName, len(cardData), len(tokenData), flipCardNums)
    generateJSON(deckName, cardData, cardFrequency, tokenData, flipCardNums)
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
    flipCardNums = []
    for x, cardInfo in enumerate(cardData):
        # if it's a transform card
        if "card_faces" in cardInfo:
            flipCardNums += [x]
            getpost(
                url = cardInfo["card_faces"][0]["image_uris"]["normal"],
                filename = ".temp/" + append + str(x) + ".jpg"
            )
            # make a flip card copy too
            copyfile(".temp/" + append + str(x) + ".jpg", ".temp/tf" + append + str(x) + ".jpg")
            getpost(
                url = cardInfo["card_faces"][1]["image_uris"]["normal"],
                filename = ".temp/tb" + append + str(x) + ".jpg"
            )
        else:
            getpost(
                url = cardInfo["image_uris"]["normal"],
                filename = ".temp/" + append + str(x) + ".jpg"
            )
    return flipCardNums

def stitchImages(deckName, numCards, numTokens, flipCardNums):

    # stitch card images into a 5x5 grid
    stitcher(deckName, list(range(numCards)))

    # stitch token images
    stitcher(deckName, list(range(numTokens)), "t")

    # stitch transform cards
    if len(flipCardNums):
        stitcher(deckName, flipCardNums, "tf")
        stitcher(deckName, flipCardNums, "tb")

def generateJSON(deckName, cardData, cardFrequency, tokenData, flipCardNums, cardBack = "magenta"):

    # main deck
    cardNames = [cardData[x]["name"] for x in range(len(cardData))]
    cardIDs = [cardIDGen(x) for x in range(len(cardData))]

    chunks = chunkify(cardIDs)
    numChunks = len(chunks)
    chunkLengths = [len(chunk) for chunk in chunks]
    deckImageList = zip(
        [str(x) for x in range(1, numChunks + 1)],
        [imageObject(
            *stitchDimensions(chunkLengths[x]),
            "images/" + deckName + "_" + str(x) + ".jpg",
            "assets/" + cardBack + ".jpg"
        ) for x in range(numChunks)]
    )
    deckImage = dict(deckImageList)

    cN = []
    cIDs = []
    for name, id, freq in zip(cardNames, cardIDs, cardFrequency):
        cN += freq * [name]
        cIDs += freq * [id]
    cardNames = cN
    cardIDs = cIDs

    mainDeck = {
        "Transform": transformObject(posY = 1),
        "Name": "DeckCustom",
        "ContainedObjects": [cardObject(name, id) for name, id in zip(cardNames, cardIDs)],
        "DeckIDs": cardIDs,
        "CustomDeck": deckImage
    }

    objectStates = [mainDeck]

    prevDeckNumber = numChunks

    if tokenData:
        # token deck
        tokenNames = [tokenData[x]["name"] for x in range(len(tokenData))]
        tokenIDs = [cardIDGen(x, prevDeckNumber*100) for x in range(len(tokenData))]

        chunks = chunkify(tokenIDs)
        numChunks = len(chunks)
        chunkLengths = [len(chunk) for chunk in chunks]
        tokenImageList = zip(
            [str(x) for x in range(prevDeckNumber + 1, prevDeckNumber + numChunks + 1)],
            [imageObject(
                *stitchDimensions(chunkLengths[x]),
                "images/" + deckName + "_t" + str(x) + ".jpg",
                "assets/" + cardBack + ".jpg"
            ) for x in range(numChunks)]
        )
        tokenImage = dict(tokenImageList)

        tokenDeck = {
            "Transform": transformObject(posY = 1, posX = -4),
            "Name": "DeckCustom",
            "ContainedObjects": [cardObject(name, id) for name, id in zip(tokenNames, tokenIDs)],
            "DeckIDs": tokenIDs,
            "CustomDeck": tokenImage
        }

        objectStates += [tokenDeck]

        prevDeckNumber += numChunks

    if flipCardNums:
        transformNames = [cardData[x]["name"] for x in flipCardNums]
        transformIDs = [cardIDGen(x, prevDeckNumber*100) for x in range(len(flipCardNums))]

        chunks = chunkify(transformIDs)
        numChunks = len(chunks)
        chunkLengths = [len(chunk) for chunk in chunks]
        frontImageList = zip(
            [str(x) for x in range(prevDeckNumber + 1, prevDeckNumber + numChunks + 1)],
            [imageObject(
                *stitchDimensions(chunkLengths[x]),
                "images/" + deckName + "_tf" + str(x) + ".jpg",
                "assets/" + cardBack + ".jpg"
            ) for x in range(numChunks)]
        )
        transformImageList = zip(
            [str(x) for x in range(prevDeckNumber + 1, prevDeckNumber + numChunks + 1)],
            [imageObject(
                *stitchDimensions(chunkLengths[x]),
                "images/" + deckName + "_tb" + str(x) + ".jpg",
                "images/" + deckName + "_tb" + str(x) + ".jpg",
                uniqueBack = True
            ) for x in range(numChunks)]
        )
        transformImage = dict(transformImageList)

        transformDeck = {
            "Transform": transformObject(posY = 1, posX = -8),
            "Name": "DeckCustom",
            "ContainedObjects": [cardObject(name, id) for name, id in zip(transformNames, transformIDs)],
            "DeckIDs": transformIDs,
            "CustomDeck": transformImage
        }

        objectStates += [transformDeck]

    jsonFile = json.dumps(
        {"ObjectStates": objectStates},
        indent = 2
    )

    with open("outputs/" + deckName + ".json", "w+") as file:
        file.write(jsonFile)

if __name__ == "__main__": main()
