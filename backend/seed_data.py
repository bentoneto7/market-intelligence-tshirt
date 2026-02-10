"""Seed database with real Brazilian show/festival data for 2026."""

from datetime import datetime

from app.analysis.genre_classifier import classify_genre
from app.analysis.hype_calculator import HypeCalculator
from app.analysis.production_window import ProductionWindowCalculator
from app.analysis.sales_predictor import SalesPotentialCalculator
from app.database import SessionLocal, init_db
from app.models.artist import Artist
from app.models.event import Event
from app.models.event_snapshot import EventSnapshot
from app.models.venue import Venue
from app.utils.date_utils import normalize_artist_name

VENUES_DATA = [
    ("Allianz Parque", "São Paulo", "SP", 45000, "stadium"),
    ("MorumBIS", "São Paulo", "SP", 60000, "stadium"),
    ("Autódromo de Interlagos", "São Paulo", "SP", 100000, "outdoor"),
    ("Engenhão", "Rio de Janeiro", "RJ", 45000, "stadium"),
    ("Suhai Music Hall", "São Paulo", "SP", 8000, "arena"),
    ("Vibra São Paulo", "São Paulo", "SP", 6000, "arena"),
    ("Pedreira Paulo Leminski", "Curitiba", "PR", 30000, "outdoor"),
    ("Mercado Livre Arena Pacaembu", "São Paulo", "SP", 15000, "arena"),
    ("Tokio Marine Hall", "São Paulo", "SP", 3500, "arena"),
    ("KTO Arena", "Porto Alegre", "RS", 8000, "arena"),
    ("Vivo Rio", "Rio de Janeiro", "RJ", 4000, "arena"),
    ("Audio", "São Paulo", "SP", 5000, "club"),
    ("Terra SP", "São Paulo", "SP", 6000, "arena"),
    ("Memorial América Latina", "São Paulo", "SP", 10000, "outdoor"),
    ("Farmasi Arena", "Rio de Janeiro", "RJ", 15000, "arena"),
    ("Sacadura 154", "Rio de Janeiro", "RJ", 2000, "club"),
    ("Live Curitiba", "Curitiba", "PR", 5000, "arena"),
    ("Opinião", "Porto Alegre", "RS", 1500, "club"),
]

EVENTS_DATA = [
    {
        "title": "My Chemical Romance - Long Live: The Black Parade Tour",
        "artist": "My Chemical Romance",
        "venue": "Allianz Parque",
        "city": "São Paulo",
        "date": "2026-02-05",
        "status": "selling_fast",
        "audience": 42000,
        "price_min": 280,
        "price_max": 890,
        "type": "tour_stop",
    },
    {
        "title": "My Chemical Romance - Long Live: The Black Parade Tour",
        "artist": "My Chemical Romance",
        "venue": "Allianz Parque",
        "city": "São Paulo",
        "date": "2026-02-06",
        "status": "available",
        "audience": 40000,
        "price_min": 280,
        "price_max": 890,
        "type": "tour_stop",
    },
    {
        "title": "Doja Cat - Ma Vie World Tour",
        "artist": "Doja Cat",
        "venue": "Suhai Music Hall",
        "city": "São Paulo",
        "date": "2026-02-05",
        "status": "selling_fast",
        "audience": 7500,
        "price_min": 350,
        "price_max": 1200,
        "type": "tour_stop",
    },
    {
        "title": "Kali Uchis",
        "artist": "Kali Uchis",
        "venue": "Vibra São Paulo",
        "city": "São Paulo",
        "date": "2026-02-08",
        "status": "available",
        "audience": 5000,
        "price_min": 200,
        "price_max": 600,
        "type": "concert",
    },
    {
        "title": "Bad Bunny - Debí Tirar Más Fotos World Tour",
        "artist": "Bad Bunny",
        "venue": "Allianz Parque",
        "city": "São Paulo",
        "date": "2026-02-20",
        "status": "selling_fast",
        "audience": 44000,
        "price_min": 300,
        "price_max": 1500,
        "type": "tour_stop",
    },
    {
        "title": "Bad Bunny - Debí Tirar Más Fotos World Tour",
        "artist": "Bad Bunny",
        "venue": "Allianz Parque",
        "city": "São Paulo",
        "date": "2026-02-21",
        "status": "available",
        "audience": 43000,
        "price_min": 300,
        "price_max": 1500,
        "type": "tour_stop",
    },
    {
        "title": "AC/DC - Power Up Tour",
        "artist": "AC/DC",
        "venue": "MorumBIS",
        "city": "São Paulo",
        "date": "2026-02-24",
        "status": "sold_out",
        "audience": 60000,
        "price_min": 350,
        "price_max": 1800,
        "type": "tour_stop",
    },
    {
        "title": "AC/DC - Power Up Tour",
        "artist": "AC/DC",
        "venue": "MorumBIS",
        "city": "São Paulo",
        "date": "2026-02-28",
        "status": "sold_out",
        "audience": 60000,
        "price_min": 350,
        "price_max": 1800,
        "type": "tour_stop",
    },
    {
        "title": "AC/DC - Power Up Tour",
        "artist": "AC/DC",
        "venue": "MorumBIS",
        "city": "São Paulo",
        "date": "2026-03-04",
        "status": "sold_out",
        "audience": 60000,
        "price_min": 350,
        "price_max": 1800,
        "type": "tour_stop",
    },
    {
        "title": "Rüfüs Du Sol",
        "artist": "Rüfüs Du Sol",
        "venue": "Pedreira Paulo Leminski",
        "city": "Curitiba",
        "date": "2026-02-25",
        "status": "available",
        "audience": 15000,
        "price_min": 200,
        "price_max": 650,
        "type": "concert",
    },
    {
        "title": "Rüfüs Du Sol",
        "artist": "Rüfüs Du Sol",
        "venue": "Mercado Livre Arena Pacaembu",
        "city": "São Paulo",
        "date": "2026-02-27",
        "status": "available",
        "audience": 12000,
        "price_min": 250,
        "price_max": 700,
        "type": "concert",
    },
    {
        "title": "Bryan Adams - Roll With The Punches Tour",
        "artist": "Bryan Adams",
        "venue": "Vivo Rio",
        "city": "Rio de Janeiro",
        "date": "2026-03-06",
        "status": "available",
        "audience": 3500,
        "price_min": 300,
        "price_max": 900,
        "type": "tour_stop",
    },
    {
        "title": "Cypress Hill",
        "artist": "Cypress Hill",
        "venue": "KTO Arena",
        "city": "Porto Alegre",
        "date": "2026-03-17",
        "status": "available",
        "audience": 6000,
        "price_min": 180,
        "price_max": 500,
        "type": "tour_stop",
    },
    {
        "title": "Interpol + Viagra Boys",
        "artist": "Interpol",
        "venue": "Audio",
        "city": "São Paulo",
        "date": "2026-03-19",
        "status": "available",
        "audience": 4500,
        "price_min": 220,
        "price_max": 550,
        "type": "concert",
    },
    {
        "title": "Lollapalooza Brasil 2026 - Dia 1",
        "artist": "Sabrina Carpenter",
        "venue": "Autódromo de Interlagos",
        "city": "São Paulo",
        "date": "2026-03-20",
        "status": "selling_fast",
        "audience": 100000,
        "price_min": 450,
        "price_max": 3500,
        "type": "festival",
        "is_festival": True,
        "headliners": ["Sabrina Carpenter", "Tyler The Creator", "Deftones", "Skrillex"],
    },
    {
        "title": "Lollapalooza Brasil 2026 - Dia 2",
        "artist": "Chappell Roan",
        "venue": "Autódromo de Interlagos",
        "city": "São Paulo",
        "date": "2026-03-21",
        "status": "selling_fast",
        "audience": 100000,
        "price_min": 450,
        "price_max": 3500,
        "type": "festival",
        "is_festival": True,
        "headliners": ["Chappell Roan", "Lorde", "Turnstile", "Doechii"],
    },
    {
        "title": "Lollapalooza Brasil 2026 - Dia 3",
        "artist": "Tyler The Creator",
        "venue": "Autódromo de Interlagos",
        "city": "São Paulo",
        "date": "2026-03-22",
        "status": "selling_fast",
        "audience": 100000,
        "price_min": 450,
        "price_max": 3500,
        "type": "festival",
        "is_festival": True,
        "headliners": ["Kygo", "Lewis Capaldi", "Cypress Hill", "Peggy Gou"],
    },
    {
        "title": "Monsters of Rock 2026 - Guns N' Roses",
        "artist": "Guns N' Roses",
        "venue": "Allianz Parque",
        "city": "São Paulo",
        "date": "2026-04-04",
        "status": "selling_fast",
        "audience": 45000,
        "price_min": 350,
        "price_max": 1600,
        "type": "festival",
        "is_festival": True,
        "headliners": ["Guns N' Roses", "Extreme", "Lynyrd Skynyrd", "Halestorm", "Yngwie Malmsteen"],
    },
    {
        "title": "Mac DeMarco - São Paulo",
        "artist": "Mac DeMarco",
        "venue": "Audio",
        "city": "São Paulo",
        "date": "2026-04-04",
        "status": "available",
        "audience": 4000,
        "price_min": 180,
        "price_max": 450,
        "type": "tour_stop",
    },
    {
        "title": "Jackson Wang",
        "artist": "Jackson Wang",
        "venue": "Suhai Music Hall",
        "city": "São Paulo",
        "date": "2026-04-23",
        "status": "available",
        "audience": 7000,
        "price_min": 250,
        "price_max": 800,
        "type": "tour_stop",
    },
    {
        "title": "Bangers Open Air 2026",
        "artist": "Black Label Society",
        "venue": "Memorial América Latina",
        "city": "São Paulo",
        "date": "2026-04-25",
        "status": "available",
        "audience": 8000,
        "price_min": 200,
        "price_max": 600,
        "type": "festival",
        "is_festival": True,
        "headliners": ["Black Label Society", "Primal Fear", "Tankard", "Nevermore"],
    },
    {
        "title": "The Weeknd - After Hours Til Dawn Tour",
        "artist": "The Weeknd",
        "venue": "Engenhão",
        "city": "Rio de Janeiro",
        "date": "2026-04-26",
        "status": "selling_fast",
        "audience": 45000,
        "price_min": 300,
        "price_max": 1400,
        "type": "tour_stop",
    },
    {
        "title": "The Weeknd - After Hours Til Dawn Tour",
        "artist": "The Weeknd",
        "venue": "MorumBIS",
        "city": "São Paulo",
        "date": "2026-04-30",
        "status": "available",
        "audience": 55000,
        "price_min": 300,
        "price_max": 1400,
        "type": "tour_stop",
    },
]


def seed():
    init_db()
    db = SessionLocal()
    hype_calc = HypeCalculator()
    sales_calc = SalesPotentialCalculator()
    prod_calc = ProductionWindowCalculator()

    try:
        # Create venues
        venue_map = {}
        for name, city, state, capacity, vtype in VENUES_DATA:
            venue = Venue(
                name=name, city=city, state=state, capacity=capacity, venue_type=vtype
            )
            db.add(venue)
            db.flush()
            venue_map[name] = venue

        # Create events
        artist_map = {}
        for data in EVENTS_DATA:
            # Artist
            artist_name = data["artist"]
            normalized = normalize_artist_name(artist_name)
            if normalized not in artist_map:
                genre = classify_genre(data["title"], artist_name)
                artist = Artist(
                    name=artist_name,
                    normalized_name=normalized,
                    genre=genre,
                    popularity_score=70.0 if data["status"] == "sold_out" else 50.0,
                )
                db.add(artist)
                db.flush()
                artist_map[normalized] = artist
            else:
                artist = artist_map[normalized]

            venue = venue_map.get(data["venue"])
            event = Event(
                title=data["title"],
                artist_id=artist.id,
                venue_id=venue.id if venue else None,
                event_date=datetime.strptime(data["date"], "%Y-%m-%d"),
                source_platform="seed",
                source_url=f"seed://{normalized}/{data['date']}",
                ticket_status=data["status"],
                estimated_audience=data.get("audience"),
                ticket_price_min=data.get("price_min"),
                ticket_price_max=data.get("price_max"),
                event_type=data.get("type", "concert"),
                is_festival=data.get("is_festival", False),
                headliners=data.get("headliners"),
            )
            db.add(event)
            db.flush()

            # Initial snapshot
            snapshot = EventSnapshot(
                event_id=event.id,
                ticket_status=event.ticket_status,
                estimated_audience=event.estimated_audience,
                ticket_price_min=event.ticket_price_min,
                ticket_price_max=event.ticket_price_max,
            )
            db.add(snapshot)

            # Calculate scores
            hype = hype_calc.calculate(event, [])
            event.hype_score = hype
            sales = sales_calc.calculate(event, hype)
            event.sales_potential_score = sales
            start, deadline = prod_calc.calculate(event, hype, sales)
            event.production_start_date = start
            event.production_deadline = deadline

        db.commit()
        print(f"Seeded {len(EVENTS_DATA)} events, {len(artist_map)} artists, {len(venue_map)} venues")

    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
