from app.models.event import Event


class SalesPotentialCalculator:
    """Predict t-shirt sales potential (0-100)."""

    GENRE_MULTIPLIERS = {
        "metal": 1.6,
        "rock": 1.5,
        "punk": 1.4,
        "indie": 1.3,
        "rap": 1.2,
        "hip hop": 1.2,
        "pop": 1.0,
        "k-pop": 1.1,
        "eletronica": 0.9,
        "edm": 0.9,
        "sertanejo": 0.8,
        "funk": 0.7,
        "pagode": 0.7,
        "axe": 0.7,
    }

    CITY_MULTIPLIERS = {
        "são paulo": 1.2,
        "rio de janeiro": 1.1,
        "porto alegre": 1.05,
        "curitiba": 1.0,
        "belo horizonte": 1.0,
        "brasília": 0.95,
        "salvador": 0.9,
        "recife": 0.9,
        "fortaleza": 0.9,
    }

    def calculate(self, event: Event, hype_score: float) -> float:
        score = 0.0

        # Base from hype (0-40 points)
        score += hype_score * 0.4

        # Audience size (0-30 points)
        if event.estimated_audience:
            audience_score = min((event.estimated_audience / 10000) * 30, 30)
            score += audience_score
        elif event.venue and event.venue.capacity:
            audience_score = min((event.venue.capacity / 10000) * 20, 20)
            score += audience_score

        # Festival bonus (0-15 points)
        if event.is_festival:
            score += 15
        elif event.event_type == "tour_stop":
            score += 5

        # Genre multiplier
        genre = (event.artist.genre if event.artist and event.artist.genre else "pop").lower()
        genre_mult = self.GENRE_MULTIPLIERS.get(genre, 1.0)
        score *= genre_mult

        # City multiplier
        city = ""
        if event.venue and event.venue.city:
            city = event.venue.city.lower().strip()
        city_mult = self.CITY_MULTIPLIERS.get(city, 0.9)
        score *= city_mult

        return min(round(score, 1), 100.0)
