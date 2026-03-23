import os
import re

cards_info = [
    {"id": 0,  "numero": 1,  "palo": 0},
    {"id": 1,  "numero": 1,  "palo": 1},
    {"id": 2,  "numero": 7,  "palo": 0},
    {"id": 3,  "numero": 7,  "palo": 2},
    {"id": 4,  "numero": 3,  "palo": 0},
    {"id": 5,  "numero": 3,  "palo": 1},
    {"id": 6,  "numero": 3,  "palo": 2},
    {"id": 7,  "numero": 3,  "palo": 3},
    {"id": 8,  "numero": 2,  "palo": 0},
    {"id": 9,  "numero": 2,  "palo": 1},
    {"id": 10, "numero": 2,  "palo": 2},
    {"id": 11, "numero": 2,  "palo": 3},
    {"id": 12, "numero": 1,  "palo": 2},
    {"id": 13, "numero": 1,  "palo": 3},
    {"id": 14, "numero": 12, "palo": 0},
    {"id": 15, "numero": 12, "palo": 1},
    {"id": 16, "numero": 12, "palo": 2},
    {"id": 17, "numero": 12, "palo": 3},
    {"id": 18, "numero": 11, "palo": 0},
    {"id": 19, "numero": 11, "palo": 1},
    {"id": 20, "numero": 11, "palo": 2},
    {"id": 21, "numero": 11, "palo": 3},
    {"id": 22, "numero": 10, "palo": 0},
    {"id": 23, "numero": 10, "palo": 1},
    {"id": 24, "numero": 10, "palo": 2},
    {"id": 25, "numero": 10, "palo": 3},
    {"id": 26, "numero": 7,  "palo": 1},
    {"id": 27, "numero": 7,  "palo": 3},
    {"id": 28, "numero": 6,  "palo": 0},
    {"id": 29, "numero": 6,  "palo": 1},
    {"id": 30, "numero": 6,  "palo": 2},
    {"id": 31, "numero": 6,  "palo": 3},
    {"id": 32, "numero": 5,  "palo": 0},
    {"id": 33, "numero": 5,  "palo": 1},
    {"id": 34, "numero": 5,  "palo": 2},
    {"id": 35, "numero": 5,  "palo": 3},
    {"id": 36, "numero": 4,  "palo": 0},
    {"id": 37, "numero": 4,  "palo": 1},
    {"id": 38, "numero": 4,  "palo": 2},
    {"id": 39, "numero": 4,  "palo": 3},
]

palo_map = {
    "espadas": 0,
    "bastos": 1,
    "oros": 2,
    "copas": 3
}

images = os.listdir(".")
for image in images:
    parsed = re.match(r"(\d+)-(\w+)\.png", image)
    if parsed:
        for card in cards_info:
            if card["numero"] == int(parsed.group(1)) and card["palo"] == palo_map[parsed.group(2)]:
                os.rename(image, str(card["id"]) + ".png")