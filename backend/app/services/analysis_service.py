from datetime import datetime

from sqlalchemy.orm import Session

from app.analysis.hype_calculator import HypeCalculator
from app.analysis.production_window import ProductionWindowCalculator
from app.analysis.sales_predictor import SalesPotentialCalculator
from app.models.event import Event
from app.models.event_snapshot import EventSnapshot
from app.utils.logger import setup_logger

logger = setup_logger("analysis_service")


class AnalysisService:
    def __init__(self, db: Session):
        self.db = db
        self.hype_calc = HypeCalculator()
        self.sales_calc = SalesPotentialCalculator()
        self.production_calc = ProductionWindowCalculator()

    def recalculate_all(self):
        """Recalculate scores for all active future events."""
        events = (
            self.db.query(Event)
            .filter(Event.is_active.is_(True), Event.event_date >= datetime.utcnow())
            .all()
        )

        for event in events:
            snapshots = (
                self.db.query(EventSnapshot)
                .filter(EventSnapshot.event_id == event.id)
                .order_by(EventSnapshot.snapshot_at.asc())
                .all()
            )

            hype = self.hype_calc.calculate(event, snapshots)
            event.hype_score = hype

            sales = self.sales_calc.calculate(event, hype)
            event.sales_potential_score = sales

            start, deadline = self.production_calc.calculate(event, hype, sales)
            event.production_start_date = start
            event.production_deadline = deadline

        self.db.commit()
        logger.info(f"Recalculated scores for {len(events)} events")
