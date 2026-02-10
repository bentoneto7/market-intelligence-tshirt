import re
import unicodedata
from datetime import datetime

from dateutil import parser

MONTHS_PT = {
    "janeiro": "january",
    "fevereiro": "february",
    "março": "march",
    "abril": "april",
    "maio": "may",
    "junho": "june",
    "julho": "july",
    "agosto": "august",
    "setembro": "september",
    "outubro": "october",
    "novembro": "november",
    "dezembro": "december",
    "jan": "jan",
    "fev": "feb",
    "mar": "mar",
    "abr": "apr",
    "mai": "may",
    "jun": "jun",
    "jul": "jul",
    "ago": "aug",
    "set": "sep",
    "out": "oct",
    "nov": "nov",
    "dez": "dec",
}

WEEKDAYS_PT = [
    "segunda",
    "terça",
    "quarta",
    "quinta",
    "sexta",
    "sábado",
    "domingo",
    "segunda-feira",
    "terça-feira",
    "quarta-feira",
    "quinta-feira",
    "sexta-feira",
]


def parse_brazilian_date(date_string: str) -> datetime:
    """Parse dates in various Brazilian formats."""
    text = date_string.strip().lower()

    # Remove weekday names
    for wd in WEEKDAYS_PT:
        text = text.replace(wd, "")
    text = re.sub(r"^[,\s]+", "", text)

    # Remove "de" preposition
    text = text.replace(" de ", " ")

    # Replace Portuguese month names
    for pt, en in MONTHS_PT.items():
        text = text.replace(pt, en)

    return parser.parse(text, fuzzy=True, dayfirst=True)


def normalize_artist_name(name: str) -> str:
    """Normalize artist name for dedup matching."""
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")
    name = name.lower()
    name = re.sub(r"\([^)]*\)", "", name)
    name = re.sub(r"[^a-z0-9]", "", name)
    return name.strip()
