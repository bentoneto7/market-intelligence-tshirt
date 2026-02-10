import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
});

export interface Artist {
  id: number;
  name: string;
  genre: string | null;
  popularity_score: number;
}

export interface Venue {
  id: number;
  name: string;
  city: string;
  state: string | null;
  capacity: number | null;
  venue_type: string | null;
}

export interface Event {
  id: number;
  title: string;
  event_date: string;
  artist: Artist | null;
  venue: Venue | null;
  source_platform: string | null;
  source_url: string | null;
  ticket_status: string | null;
  estimated_audience: number | null;
  ticket_price_min: number | null;
  ticket_price_max: number | null;
  event_type: string | null;
  is_festival: boolean;
  headliners: string[] | null;
  hype_score: number;
  sales_potential_score: number;
  production_start_date: string | null;
  production_deadline: string | null;
  is_active: boolean;
}

export interface PaginatedEvents {
  events: Event[];
  total: number;
  page: number;
  page_size: number;
}

export interface DashboardStats {
  total_events: number;
  high_hype_count: number;
  high_potential_count: number;
  events_this_month: number;
  events_next_month: number;
  top_cities: { city: string; count: number }[];
  top_genres: { genre: string; count: number }[];
}

export interface RankingResponse {
  events: Event[];
  metric: string;
}

export interface EventFilters {
  city?: string;
  date_from?: string;
  date_to?: string;
  min_hype?: number;
  min_sales_potential?: number;
  genre?: string;
  page?: number;
  page_size?: number;
}

export async function fetchEvents(filters: EventFilters = {}): Promise<PaginatedEvents> {
  const params = Object.fromEntries(
    Object.entries(filters).filter(([, v]) => v !== undefined && v !== "")
  );
  const { data } = await api.get<PaginatedEvents>("/events/", { params });
  return data;
}

export async function fetchDashboardStats(): Promise<DashboardStats> {
  const { data } = await api.get<DashboardStats>("/dashboard/stats");
  return data;
}

export async function fetchRankings(
  metric: string = "sales_potential_score",
  limit: number = 10
): Promise<RankingResponse> {
  const { data } = await api.get<RankingResponse>("/rankings/", {
    params: { metric, limit },
  });
  return data;
}

export async function triggerScraping(platforms?: string[]): Promise<{ status: string; message: string }> {
  const { data } = await api.post("/scraping/trigger", platforms ? { platforms } : {});
  return data;
}

// Marketplace types and functions
export interface MarketplaceProduct {
  id: number;
  title: string;
  description: string | null;
  image_url: string | null;
  product_url: string;
  price: number;
  original_price: number | null;
  sold_count: number;
  rating: number | null;
  review_count: number;
  seller_name: string | null;
  seller_location: string | null;
  platform: string;
  category: string | null;
  related_artist: string | null;
  related_event: string | null;
  search_term: string | null;
  last_scraped_at: string | null;
}

export interface PaginatedMarketplace {
  products: MarketplaceProduct[];
  total: number;
  page: number;
  page_size: number;
}

export interface MarketplaceStats {
  total_products: number;
  avg_price: number;
  top_sellers: { seller: string; products: number; avg_sold: number }[];
  top_artists: { artist: string; products: number; avg_price: number; total_sold: number }[];
  price_range: { min: number; max: number };
  platform_breakdown: { platform: string; count: number }[];
}

export interface MarketplaceFilters {
  platform?: string;
  related_artist?: string;
  category?: string;
  min_price?: number;
  max_price?: number;
  min_sold?: number;
  search?: string;
  sort_by?: string;
  page?: number;
  page_size?: number;
}

export async function fetchMarketplaceProducts(
  filters: MarketplaceFilters = {}
): Promise<PaginatedMarketplace> {
  const params = Object.fromEntries(
    Object.entries(filters).filter(([, v]) => v !== undefined && v !== "")
  );
  const { data } = await api.get<PaginatedMarketplace>("/marketplace/products", { params });
  return data;
}

export async function fetchMarketplaceStats(): Promise<MarketplaceStats> {
  const { data } = await api.get<MarketplaceStats>("/marketplace/stats");
  return data;
}

export interface ArtistProjection {
  artist: string;
  total_sold: number;
  avg_price: number;
  products_count: number;
  estimated_monthly_revenue: number;
  estimated_units_per_month: number;
  market_share_pct: number;
  growth_potential: string;
  suggested_price: number;
  profit_margin_pct: number;
}

export interface SalesProjection {
  total_market_revenue: number;
  total_units_sold: number;
  avg_ticket: number;
  projections: ArtistProjection[];
  category_breakdown: {
    category: string;
    products: number;
    total_sold: number;
    avg_price: number;
    revenue_estimate: number;
  }[];
  opportunity_score: {
    market_size: string;
    competition_level: string;
    avg_profit_margin: number;
    recommended_investment: number;
    projected_roi_pct: number;
  };
}

export async function fetchSalesProjection(): Promise<SalesProjection> {
  const { data } = await api.get<SalesProjection>("/marketplace/projection");
  return data;
}

export interface EventForecastItem {
  event_id: number;
  event_title: string;
  artist: string;
  venue: string;
  city: string;
  event_date: string;
  days_until: number;
  audience: number;
  ticket_status: string;
  hype_score: number;
  sales_potential: number;
  is_festival: boolean;
  matching_products: number;
  marketplace_avg_price: number;
  marketplace_total_sold: number;
  best_seller_title: string | null;
  best_seller_sold: number;
  best_seller_url: string | null;
  conversion_rate_pct: number;
  projected_units: number;
  suggested_price: number;
  projected_revenue: number;
  projected_profit: number;
}

export interface WeeklyForecast {
  week: string;
  events: number;
  units: number;
  revenue: number;
  profit: number;
}

export interface EventForecastResponse {
  period_days: number;
  total_events: number;
  total_audience: number;
  total_projected_units: number;
  total_projected_revenue: number;
  total_projected_profit: number;
  avg_conversion_rate_pct: number;
  avg_ticket: number;
  events: EventForecastItem[];
  weekly_forecast: WeeklyForecast[];
}

export async function fetchEventForecast(days: number = 90): Promise<EventForecastResponse> {
  const { data } = await api.get<EventForecastResponse>("/marketplace/event-forecast", {
    params: { days },
  });
  return data;
}
