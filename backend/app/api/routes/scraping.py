from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.event import ScrapingLogResponse, ScrapingTriggerRequest, ScrapingTriggerResponse
from app.services.scraping_service import ScrapingService

router = APIRouter(prefix="/scraping", tags=["scraping"])


@router.post("/trigger", response_model=ScrapingTriggerResponse)
async def trigger_scraping(
    request: ScrapingTriggerRequest | None = None,
    db: Session = Depends(get_db),
):
    service = ScrapingService(db)
    result = await service.run_scraping(
        platforms=request.platforms if request else None
    )
    return result


@router.get("/logs", response_model=list[ScrapingLogResponse])
def get_scraping_logs(
    platform: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = ScrapingService(db)
    return service.get_logs(platform=platform, limit=limit)


@router.get("/test-fetch")
async def test_fetch():
    """Debug endpoint to test if Eventbrite is reachable."""
    import httpx

    url = "https://www.eventbrite.com.br/d/brazil/shows-musicais/?page=1"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "pt-BR,pt;q=0.9",
    }
    try:
        async with httpx.AsyncClient(headers=headers, timeout=20, follow_redirects=True) as client:
            resp = await client.get(url)
            html = resp.text
            import re
            ld_blocks = re.findall(
                r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>',
                html, re.DOTALL | re.IGNORECASE,
            )
            return {
                "status_code": resp.status_code,
                "html_size": len(html),
                "ld_json_blocks": len(ld_blocks),
                "has_itemlist": any("ItemList" in b for b in ld_blocks),
                "title": html[:200] if len(html) < 500 else "HTML received OK",
            }
    except Exception as e:
        return {"error": str(e)}
