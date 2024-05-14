import os
from dotenv import load_dotenv

load_dotenv()
#SELECTED COORDINATES
LAT = os.getenv('LAT')
LON = os.getenv('LON')

FOLDER_INPUT = os.path.join(
    os.getcwd(),
    'misc',
)
FOLDER_OUTPUT = os.path.join(
    os.getcwd(),
    'output'
)
SEPARATORS = [
    ';',
    ' ',   
]
SEPARATORS_LAN_LOT = [
    ',',
    '. ',
    ' ',
]
SEPARATORS_LAN_LOT_TEXT = [
    '-',
    '—',
]