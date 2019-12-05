# main script for tts-deck-import
# andy wong
# medecinqui AT gmail.com

import requests

def download(url, fileName):
    # open in binary mode
    with open(fileName, "wb") as file:
        # get request
        response = requests.get(url)
        file.write(response.content)

download("https://img.scryfall.com/cards/large/front/1/9/19e95422-c6fe-4750-916b-43bf22ae193a.jpg?1562177934", "scryingsheets.jpg")
