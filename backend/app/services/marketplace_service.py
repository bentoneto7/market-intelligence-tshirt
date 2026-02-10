from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.artist import Artist
from app.models.event import Event
from app.models.marketplace_product import MarketplaceProduct
from app.models.venue import Venue


class MarketplaceService:
    def __init__(self, db: Session):
        self.db = db

    def list_products(
        self,
        platform: str | None = None,
        related_artist: str | None = None,
        category: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        min_sold: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        page: int = 1,
        page_size: int = 30,
    ) -> dict:
        query = self.db.query(MarketplaceProduct)

        if platform:
            query = query.filter(MarketplaceProduct.platform == platform)
        if related_artist:
            query = query.filter(
                MarketplaceProduct.related_artist.ilike(f"%{related_artist}%")
            )
        if category:
            query = query.filter(MarketplaceProduct.category.ilike(f"%{category}%"))
        if min_price is not None:
            query = query.filter(MarketplaceProduct.price >= min_price)
        if max_price is not None:
            query = query.filter(MarketplaceProduct.price <= max_price)
        if min_sold is not None:
            query = query.filter(MarketplaceProduct.sold_count >= min_sold)
        if search:
            query = query.filter(MarketplaceProduct.title.ilike(f"%{search}%"))

        total = query.count()

        # Sorting
        if sort_by == "price_asc":
            query = query.order_by(MarketplaceProduct.price.asc())
        elif sort_by == "price_desc":
            query = query.order_by(MarketplaceProduct.price.desc())
        elif sort_by == "sold_count":
            query = query.order_by(MarketplaceProduct.sold_count.desc())
        elif sort_by == "rating":
            query = query.order_by(MarketplaceProduct.rating.desc().nullslast())
        else:
            query = query.order_by(MarketplaceProduct.sold_count.desc())

        products = query.offset((page - 1) * page_size).limit(page_size).all()

        return {
            "products": products,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_stats(self) -> dict:
        base = self.db.query(MarketplaceProduct)
        total = base.count()

        avg_price_val = (
            self.db.query(func.avg(MarketplaceProduct.price)).scalar() or 0
        )

        # Top sellers by product count
        top_sellers_rows = (
            self.db.query(
                MarketplaceProduct.seller_name,
                func.count(MarketplaceProduct.id).label("count"),
                func.avg(MarketplaceProduct.sold_count).label("avg_sold"),
            )
            .filter(MarketplaceProduct.seller_name.isnot(None))
            .group_by(MarketplaceProduct.seller_name)
            .order_by(func.sum(MarketplaceProduct.sold_count).desc())
            .limit(10)
            .all()
        )
        top_sellers = [
            {
                "seller": row[0],
                "products": row[1],
                "avg_sold": round(row[2] or 0, 0),
            }
            for row in top_sellers_rows
        ]

        # Top artists by product count
        top_artists_rows = (
            self.db.query(
                MarketplaceProduct.related_artist,
                func.count(MarketplaceProduct.id).label("count"),
                func.avg(MarketplaceProduct.price).label("avg_price"),
                func.sum(MarketplaceProduct.sold_count).label("total_sold"),
            )
            .filter(MarketplaceProduct.related_artist.isnot(None))
            .group_by(MarketplaceProduct.related_artist)
            .order_by(func.sum(MarketplaceProduct.sold_count).desc())
            .limit(10)
            .all()
        )
        top_artists = [
            {
                "artist": row[0],
                "products": row[1],
                "avg_price": round(row[2] or 0, 2),
                "total_sold": row[3] or 0,
            }
            for row in top_artists_rows
        ]

        # Price range
        min_price = self.db.query(func.min(MarketplaceProduct.price)).scalar() or 0
        max_price = self.db.query(func.max(MarketplaceProduct.price)).scalar() or 0

        # Platform breakdown
        platform_rows = (
            self.db.query(
                MarketplaceProduct.platform,
                func.count(MarketplaceProduct.id).label("count"),
            )
            .group_by(MarketplaceProduct.platform)
            .all()
        )
        platform_breakdown = [
            {"platform": row[0], "count": row[1]} for row in platform_rows
        ]

        return {
            "total_products": total,
            "avg_price": round(avg_price_val, 2),
            "top_sellers": top_sellers,
            "top_artists": top_artists,
            "price_range": {"min": min_price, "max": max_price},
            "platform_breakdown": platform_breakdown,
        }

    def get_sales_projection(self) -> dict:
        """Calculate sales projections and revenue forecast per artist."""

        # Production cost estimates (R$)
        PRODUCTION_COST = 15.0  # cost per unit (blank + print)
        MARKETPLACE_FEE_PCT = 0.12  # 12% Shopee fee
        MONTHLY_GROWTH_FACTOR = 1.15  # 15% monthly growth for event-related products

        # Get all products grouped by artist
        artist_rows = (
            self.db.query(
                MarketplaceProduct.related_artist,
                func.count(MarketplaceProduct.id).label("count"),
                func.avg(MarketplaceProduct.price).label("avg_price"),
                func.sum(MarketplaceProduct.sold_count).label("total_sold"),
                func.max(MarketplaceProduct.sold_count).label("max_sold"),
                func.min(MarketplaceProduct.price).label("min_price"),
                func.max(MarketplaceProduct.price).label("max_price"),
            )
            .filter(MarketplaceProduct.related_artist.isnot(None))
            .group_by(MarketplaceProduct.related_artist)
            .order_by(func.sum(MarketplaceProduct.sold_count).desc())
            .all()
        )

        # Category breakdown
        category_rows = (
            self.db.query(
                MarketplaceProduct.category,
                func.count(MarketplaceProduct.id).label("count"),
                func.sum(MarketplaceProduct.sold_count).label("total_sold"),
                func.avg(MarketplaceProduct.price).label("avg_price"),
            )
            .group_by(MarketplaceProduct.category)
            .order_by(func.sum(MarketplaceProduct.sold_count).desc())
            .all()
        )

        grand_total_sold = sum(row[3] or 0 for row in artist_rows)
        total_market_revenue = 0
        projections = []

        for row in artist_rows:
            artist_name = row[0]
            products_count = row[1]
            avg_price = round(row[2] or 0, 2)
            total_sold = row[3] or 0
            max_sold = row[4] or 0

            # Market share
            market_share = (total_sold / grand_total_sold * 100) if grand_total_sold > 0 else 0

            # Estimate monthly units (assume data represents ~3 months of sales)
            est_monthly_units = int(total_sold / 3)

            # Revenue calculation
            est_monthly_revenue = est_monthly_units * avg_price

            # Suggested price: competitive but profitable
            suggested_price = round(max(avg_price * 0.9, PRODUCTION_COST * 2.5), 2)

            # Profit margin
            net_per_unit = suggested_price - PRODUCTION_COST - (suggested_price * MARKETPLACE_FEE_PCT)
            profit_margin = (net_per_unit / suggested_price * 100) if suggested_price > 0 else 0

            # Growth potential based on sold volume and product count
            if total_sold > 10000 and products_count >= 3:
                growth = "alto"
            elif total_sold > 5000 or products_count >= 3:
                growth = "medio"
            else:
                growth = "baixo"

            total_market_revenue += est_monthly_revenue

            projections.append({
                "artist": artist_name,
                "total_sold": total_sold,
                "avg_price": avg_price,
                "products_count": products_count,
                "estimated_monthly_revenue": round(est_monthly_revenue, 2),
                "estimated_units_per_month": est_monthly_units,
                "market_share_pct": round(market_share, 1),
                "growth_potential": growth,
                "suggested_price": suggested_price,
                "profit_margin_pct": round(profit_margin, 1),
            })

        # Category breakdown result
        category_breakdown = [
            {
                "category": row[0] or "sem_categoria",
                "products": row[1],
                "total_sold": row[2] or 0,
                "avg_price": round(row[3] or 0, 2),
                "revenue_estimate": round((row[2] or 0) / 3 * (row[3] or 0), 2),
            }
            for row in category_rows
        ]

        # Opportunity score
        total_products = self.db.query(MarketplaceProduct).count()
        avg_price_all = self.db.query(func.avg(MarketplaceProduct.price)).scalar() or 0
        total_sold_all = self.db.query(func.sum(MarketplaceProduct.sold_count)).scalar() or 0

        opportunity_score = {
            "market_size": "grande" if total_sold_all > 50000 else "medio" if total_sold_all > 20000 else "pequeno",
            "competition_level": "alta" if total_products > 50 else "media" if total_products > 20 else "baixa",
            "avg_profit_margin": round(
                ((avg_price_all - PRODUCTION_COST - avg_price_all * MARKETPLACE_FEE_PCT) / avg_price_all * 100)
                if avg_price_all > 0 else 0, 1
            ),
            "recommended_investment": round(PRODUCTION_COST * 50 * len(projections), 2),  # 50 units per artist
            "projected_roi_pct": round(
                ((avg_price_all - PRODUCTION_COST - avg_price_all * MARKETPLACE_FEE_PCT) / PRODUCTION_COST * 100)
                if PRODUCTION_COST > 0 else 0, 1
            ),
        }

        return {
            "total_market_revenue": round(total_market_revenue, 2),
            "total_units_sold": int(total_sold_all or 0),
            "avg_ticket": round(avg_price_all, 2),
            "projections": projections,
            "category_breakdown": category_breakdown,
            "opportunity_score": opportunity_score,
        }

    def get_event_forecast(self, days_ahead: int = 90) -> dict:
        """
        Cross-reference events with marketplace products to create:
        - Products linked to each event/show
        - Volume projection for the next X days
        - Conversion rate (camisetas per show attendee)
        - Revenue forecast per event
        """
        PRODUCTION_COST = 15.0
        MARKETPLACE_FEE_PCT = 0.12
        # Estimated conversion: % of show audience that buys a t-shirt online
        BASE_CONVERSION_RATE = 0.02  # 2% of audience buys online

        now = datetime.utcnow()
        cutoff = now + timedelta(days=days_ahead)

        # Get upcoming events with artist info
        events = (
            self.db.query(Event)
            .join(Artist, Event.artist_id == Artist.id)
            .outerjoin(Venue, Event.venue_id == Venue.id)
            .filter(Event.event_date >= now, Event.event_date <= cutoff)
            .filter(Event.is_active == True)
            .order_by(Event.event_date.asc())
            .all()
        )

        # Get all marketplace products indexed by artist name (lowered)
        all_products = self.db.query(MarketplaceProduct).all()
        products_by_artist: dict[str, list] = {}
        for p in all_products:
            if p.related_artist:
                key = p.related_artist.lower().strip()
                products_by_artist.setdefault(key, []).append(p)

        event_forecasts = []
        total_projected_units = 0
        total_projected_revenue = 0
        total_projected_profit = 0

        for event in events:
            artist_name = event.artist.name if event.artist else ""
            artist_key = artist_name.lower().strip()
            venue_name = event.venue.name if event.venue else ""
            city = event.venue.city if event.venue else ""
            audience = event.estimated_audience or 0

            # Find matching products
            matching = products_by_artist.get(artist_key, [])

            # Also check headliners for festivals
            if event.is_festival and event.headliners:
                headliner_list = event.headliners if isinstance(event.headliners, list) else []
                for h in headliner_list:
                    h_key = h.lower().strip()
                    if h_key != artist_key:
                        matching.extend(products_by_artist.get(h_key, []))

            # Deduplicate products
            seen_ids = set()
            unique_products = []
            for p in matching:
                if p.id not in seen_ids:
                    seen_ids.add(p.id)
                    unique_products.append(p)

            # Calculate marketplace averages for this event's products
            if unique_products:
                avg_price = sum(p.price for p in unique_products) / len(unique_products)
                avg_sold = sum(p.sold_count for p in unique_products) / len(unique_products)
                total_sold = sum(p.sold_count for p in unique_products)
                best_seller = max(unique_products, key=lambda p: p.sold_count)
            else:
                avg_price = 0
                avg_sold = 0
                total_sold = 0
                best_seller = None

            # Conversion multipliers
            status_mult = {"sold_out": 1.8, "selling_fast": 1.4, "available": 1.0}.get(event.ticket_status or "", 1.0)
            festival_mult = 1.3 if event.is_festival else 1.0
            hype_mult = 1.0 + (event.hype_score / 200)  # 0-100 hype adds 0-50% boost

            conversion_rate = BASE_CONVERSION_RATE * status_mult * festival_mult * hype_mult

            # Projected units for this event
            projected_units = int(audience * conversion_rate)

            # Use suggested price (10% below avg competitor or min 2.5x cost)
            suggested_price = round(max(avg_price * 0.9, PRODUCTION_COST * 2.5), 2) if avg_price > 0 else 37.50

            # Revenue & profit
            projected_revenue = projected_units * suggested_price
            net_per_unit = suggested_price - PRODUCTION_COST - (suggested_price * MARKETPLACE_FEE_PCT)
            projected_profit = projected_units * net_per_unit

            # Days until event
            days_until = (event.event_date - now).days

            total_projected_units += projected_units
            total_projected_revenue += projected_revenue
            total_projected_profit += projected_profit

            event_forecasts.append({
                "event_id": event.id,
                "event_title": event.title,
                "artist": artist_name,
                "venue": venue_name,
                "city": city,
                "event_date": event.event_date.strftime("%Y-%m-%d"),
                "days_until": max(days_until, 0),
                "audience": audience,
                "ticket_status": event.ticket_status,
                "hype_score": round(event.hype_score, 1),
                "sales_potential": round(event.sales_potential_score, 1),
                "is_festival": event.is_festival,
                "matching_products": len(unique_products),
                "marketplace_avg_price": round(avg_price, 2),
                "marketplace_total_sold": total_sold,
                "best_seller_title": best_seller.title if best_seller else None,
                "best_seller_sold": best_seller.sold_count if best_seller else 0,
                "best_seller_url": best_seller.product_url if best_seller else None,
                "conversion_rate_pct": round(conversion_rate * 100, 2),
                "projected_units": projected_units,
                "suggested_price": suggested_price,
                "projected_revenue": round(projected_revenue, 2),
                "projected_profit": round(projected_profit, 2),
            })

        # Overall conversion stats
        total_audience = sum(ef["audience"] for ef in event_forecasts)
        avg_conversion = (total_projected_units / total_audience * 100) if total_audience > 0 else 0

        # Timeline: group by week
        weekly_forecast = {}
        for ef in event_forecasts:
            event_dt = datetime.strptime(ef["event_date"], "%Y-%m-%d")
            week_start = event_dt - timedelta(days=event_dt.weekday())
            week_key = week_start.strftime("%Y-%m-%d")
            if week_key not in weekly_forecast:
                weekly_forecast[week_key] = {"week": week_key, "events": 0, "units": 0, "revenue": 0, "profit": 0}
            weekly_forecast[week_key]["events"] += 1
            weekly_forecast[week_key]["units"] += ef["projected_units"]
            weekly_forecast[week_key]["revenue"] += ef["projected_revenue"]
            weekly_forecast[week_key]["profit"] += ef["projected_profit"]

        weekly_list = sorted(weekly_forecast.values(), key=lambda w: w["week"])
        for w in weekly_list:
            w["revenue"] = round(w["revenue"], 2)
            w["profit"] = round(w["profit"], 2)

        return {
            "period_days": days_ahead,
            "total_events": len(event_forecasts),
            "total_audience": total_audience,
            "total_projected_units": total_projected_units,
            "total_projected_revenue": round(total_projected_revenue, 2),
            "total_projected_profit": round(total_projected_profit, 2),
            "avg_conversion_rate_pct": round(avg_conversion, 2),
            "avg_ticket": round(total_projected_revenue / total_projected_units, 2) if total_projected_units > 0 else 0,
            "events": event_forecasts,
            "weekly_forecast": weekly_list,
        }
