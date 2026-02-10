from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import dashboard, events, marketplace, rankings, scraping
from app.config import settings
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # Auto-seed if database is empty
    _auto_seed()
    yield


def _auto_seed():
    """Seed database with initial data if empty."""
    from app.database import SessionLocal
    from app.models.event import Event
    from app.models.marketplace_product import MarketplaceProduct

    db = SessionLocal()
    try:
        if db.query(Event).count() == 0:
            db.close()
            import subprocess
            import sys
            subprocess.run([sys.executable, "seed_data.py"], check=True)
            subprocess.run([sys.executable, "seed_marketplace.py"], check=True)
        else:
            db.close()
    except Exception:
        db.close()


app = FastAPI(
    title="Market Intelligence - T-shirt Printing",
    description="Sistema de inteligência de mercado para estamparia de camisetas",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router, prefix="/api/v1")
app.include_router(rankings.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(scraping.router, prefix="/api/v1")
app.include_router(marketplace.router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok"}
