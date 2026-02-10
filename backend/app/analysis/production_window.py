from datetime import date, timedelta

from app.models.event import Event


class ProductionWindowCalculator:
    """Suggest when to start t-shirt production."""

    def calculate(
        self, event: Event, hype_score: float, sales_potential: float
    ) -> tuple[date, date]:
        """Returns (production_start_date, production_deadline)."""
        event_date = event.event_date.date()

        if sales_potential >= 70:
            start = event_date - timedelta(days=45)
            deadline = event_date - timedelta(days=21)
        elif sales_potential >= 40:
            start = event_date - timedelta(days=30)
            deadline = event_date - timedelta(days=14)
        else:
            start = event_date - timedelta(days=21)
            deadline = event_date - timedelta(days=10)

        today = date.today()
        if start < today:
            start = today
        if deadline < today:
            deadline = today

        return start, deadline
