from datetime import datetime

from app.models.event import Event
from app.models.event_snapshot import EventSnapshot


class HypeCalculator:
    """Calculate event hype score (0-100) based on multiple factors."""

    def calculate(self, event: Event, snapshots: list[EventSnapshot] | None = None) -> float:
        score = 0.0

        # Factor 1: Ticket sell-out speed (0-30 points)
        score += self._sellout_speed_score(event, snapshots or [])

        # Factor 2: Venue fill rate (0-25 points)
        if event.venue and event.venue.capacity and event.estimated_audience:
            fill_rate = event.estimated_audience / event.venue.capacity
            score += min(fill_rate * 25, 25)
        elif event.ticket_status == "sold_out":
            score += 20

        # Factor 3: Artist popularity (0-25 points)
        if event.artist and event.artist.popularity_score > 0:
            score += event.artist.popularity_score * 0.25

        # Factor 4: Urgency - proximity + sold out (0-10 points)
        days_until = (event.event_date - datetime.utcnow()).days
        if event.ticket_status == "sold_out":
            if days_until < 30:
                score += 10
            elif days_until < 60:
                score += 7
            else:
                score += 5
        elif event.ticket_status == "selling_fast":
            score += 5

        # Factor 5: Event type bonus (0-10 points)
        if event.is_festival:
            score += 10
        elif event.event_type == "tour_stop":
            score += 3

        return min(round(score, 1), 100.0)

    def _sellout_speed_score(self, event: Event, snapshots: list[EventSnapshot]) -> float:
        if len(snapshots) < 2:
            # No history - use current status as proxy
            if event.ticket_status == "sold_out":
                return 25
            elif event.ticket_status == "selling_fast":
                return 15
            return 5

        # Check how fast status changed
        first = snapshots[0]
        for snap in snapshots[1:]:
            if first.ticket_status == "available" and snap.ticket_status == "sold_out":
                days_to_sellout = (snap.snapshot_at - first.snapshot_at).days
                if days_to_sellout <= 1:
                    return 30
                elif days_to_sellout <= 7:
                    return 25
                elif days_to_sellout <= 14:
                    return 20
                else:
                    return 15

        return 5
