GENRE_KEYWORDS: dict[str, list[str]] = {
    "rock": [
        "rock", "alternative", "grunge", "hard rock", "classic rock",
        "ac/dc", "foo fighters", "guns n' roses", "iron maiden",
        "pearl jam", "nirvana", "queen", "led zeppelin", "u2",
        "my chemical romance", "green day", "radiohead", "coldplay",
        "muse", "arctic monkeys", "oasis", "the killers",
    ],
    "metal": [
        "metal", "heavy metal", "death metal", "thrash", "metalcore",
        "black sabbath", "metallica", "slayer", "megadeth", "pantera",
        "avenged sevenfold", "bring me the horizon", "slipknot",
        "black label society", "yngwie malmsteen",
    ],
    "punk": [
        "punk", "hardcore", "pop punk", "emo",
        "ramones", "sex pistols", "the offspring", "blink",
    ],
    "pop": [
        "pop", "dance pop", "synth pop",
        "taylor swift", "dua lipa", "harry styles", "sabrina carpenter",
        "chappell roan", "lorde", "addison rae", "doja cat",
        "the weeknd", "bad bunny", "lewis capaldi",
    ],
    "rap": [
        "rap", "hip hop", "trap",
        "tyler", "kendrick", "drake", "kanye",
        "matuê", "wiu", "teto",
    ],
    "sertanejo": [
        "sertanejo", "modão", "universitário",
        "gusttavo lima", "marília mendonça", "jorge e mateus",
        "henrique e juliano", "zé neto", "simone mendes",
        "joão gomes", "ana castela",
    ],
    "funk": [
        "funk", "baile funk", "funk carioca",
        "ludmilla", "anitta funk",
    ],
    "eletronica": [
        "eletronica", "techno", "house", "trance", "edm",
        "alok", "vintage culture", "skrillex", "kygo",
        "charlotte de witte", "richie hawtin",
    ],
    "indie": [
        "indie", "alternativo",
        "mac demarco", "tv girl", "interpol", "turnstile",
        "the xx", "wolf alice", "lykke li", "beirut",
    ],
    "k-pop": [
        "k-pop", "kpop",
        "bts", "stray kids", "enhypen", "blackpink", "katseye",
    ],
}


def classify_genre(title: str, artist_name: str = "") -> str:
    """Classify genre based on event title and artist name."""
    text = f"{title} {artist_name}".lower()

    scores: dict[str, int] = {}
    for genre, keywords in GENRE_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                scores[genre] = scores.get(genre, 0) + 1

    if not scores:
        return "pop"

    return max(scores, key=scores.get)
