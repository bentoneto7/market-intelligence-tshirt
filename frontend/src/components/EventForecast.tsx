"use client";

import { useEffect, useState, useMemo } from "react";
import {
  EventForecastResponse,
  EventForecastItem,
  fetchEventForecast,
} from "@/lib/api";
import {
  Calendar,
  TrendingUp,
  DollarSign,
  Users,
  ExternalLink,
  ShoppingBag,
  Zap,
  BarChart3,
  Target,
  Filter,
  ArrowUpDown,
  Shirt,
  Package,
} from "lucide-react";

function formatBRL(v: number) {
  return v.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}
function formatNum(v: number) {
  return v.toLocaleString("pt-BR");
}

const PRODUCTION_COST = 15.0;

function StatusBadge({ status }: { status: string }) {
  const cfg: Record<string, { label: string; cls: string }> = {
    sold_out: { label: "Esgotado", cls: "bg-red-500/20 text-red-400" },
    selling_fast: { label: "Vendendo Rápido", cls: "bg-yellow-500/20 text-yellow-400" },
    available: { label: "Disponível", cls: "bg-green-500/20 text-green-400" },
  };
  const c = cfg[status] || { label: status, cls: "bg-zinc-700 text-zinc-300" };
  return <span className={`px-2 py-0.5 rounded text-xs font-medium ${c.cls}`}>{c.label}</span>;
}

function DaysUntilBadge({ days }: { days: number }) {
  const cls =
    days <= 7 ? "text-red-400" : days <= 21 ? "text-yellow-400" : "text-green-400";
  return (
    <span className={`font-bold text-xs ${cls}`}>
      {days === 0 ? "Hoje" : days === 1 ? "Amanhã" : `${days}d`}
    </span>
  );
}

function PriorityBadge({ ev }: { ev: EventForecastItem }) {
  const score = ev.projected_profit * (1 / Math.max(ev.days_until, 1));
  const level = score > 50 ? "urgente" : score > 10 ? "alta" : ev.projected_units > 0 ? "normal" : "baixa";
  const cfg: Record<string, { label: string; cls: string }> = {
    urgente: { label: "URGENTE", cls: "bg-red-500/20 text-red-400 animate-pulse" },
    alta: { label: "Alta", cls: "bg-yellow-500/20 text-yellow-400" },
    normal: { label: "Normal", cls: "bg-blue-500/20 text-blue-400" },
    baixa: { label: "Baixa", cls: "bg-zinc-700 text-zinc-400" },
  };
  const c = cfg[level];
  return <span className={`px-2 py-0.5 rounded text-xs font-medium ${c.cls}`}>{c.label}</span>;
}

type SortField = "days_until" | "projected_units" | "projected_profit" | "conversion_rate_pct" | "audience";

export default function EventForecast() {
  const [data, setData] = useState<EventForecastResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(90);
  const [filterArtist, setFilterArtist] = useState("");
  const [filterCity, setFilterCity] = useState("");
  const [sortField, setSortField] = useState<SortField>("projected_profit");
  const [sortAsc, setSortAsc] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetchEventForecast(days)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [days]);

  // Extract unique artists and cities for filters
  const { artists, cities } = useMemo(() => {
    if (!data) return { artists: [], cities: [] };
    const artistSet = new Set(data.events.map((e) => e.artist).filter(Boolean));
    const citySet = new Set(data.events.map((e) => e.city).filter(Boolean));
    return {
      artists: Array.from(artistSet).sort(),
      cities: Array.from(citySet).sort(),
    };
  }, [data]);

  // Filter and sort events
  const filteredEvents = useMemo(() => {
    if (!data) return [];
    let events = [...data.events];
    if (filterArtist) events = events.filter((e) => e.artist === filterArtist);
    if (filterCity) events = events.filter((e) => e.city === filterCity);
    events.sort((a, b) => {
      const va = a[sortField];
      const vb = b[sortField];
      return sortAsc ? (va as number) - (vb as number) : (vb as number) - (va as number);
    });
    return events;
  }, [data, filterArtist, filterCity, sortField, sortAsc]);

  // Filtered totals
  const filteredTotals = useMemo(() => {
    const totalUnits = filteredEvents.reduce((s, e) => s + e.projected_units, 0);
    const totalRevenue = filteredEvents.reduce((s, e) => s + e.projected_revenue, 0);
    const totalProfit = filteredEvents.reduce((s, e) => s + e.projected_profit, 0);
    const totalAudience = filteredEvents.reduce((s, e) => s + e.audience, 0);
    const totalInvestment = totalUnits * PRODUCTION_COST;
    const avgConversion = totalAudience > 0 ? (totalUnits / totalAudience) * 100 : 0;
    return { totalUnits, totalRevenue, totalProfit, totalAudience, totalInvestment, avgConversion };
  }, [filteredEvents]);

  const handleSort = (field: SortField) => {
    if (sortField === field) setSortAsc(!sortAsc);
    else { setSortField(field); setSortAsc(false); }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-zinc-900 border border-zinc-800 rounded-lg p-6 animate-pulse h-32" />
        ))}
      </div>
    );
  }

  if (!data) return null;

  const isFiltered = filterArtist || filterCity;

  return (
    <div className="space-y-6">
      {/* Controls: Period + Filters */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 text-zinc-400" />
            <span className="text-sm text-zinc-400">Período:</span>
            {[30, 60, 90, 180].map((d) => (
              <button
                key={d}
                onClick={() => setDays(d)}
                className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${
                  days === d
                    ? "bg-blue-600 text-white"
                    : "bg-zinc-800 text-zinc-400 hover:text-white"
                }`}
              >
                {d}d
              </button>
            ))}
          </div>

          <div className="h-6 w-px bg-zinc-700" />

          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-zinc-400" />
            <select
              className="bg-zinc-800 border border-zinc-700 rounded px-2 py-1.5 text-sm focus:outline-none focus:border-blue-500"
              value={filterArtist}
              onChange={(e) => setFilterArtist(e.target.value)}
            >
              <option value="">Todos artistas</option>
              {artists.map((a) => (
                <option key={a} value={a}>{a}</option>
              ))}
            </select>
            <select
              className="bg-zinc-800 border border-zinc-700 rounded px-2 py-1.5 text-sm focus:outline-none focus:border-blue-500"
              value={filterCity}
              onChange={(e) => setFilterCity(e.target.value)}
            >
              <option value="">Todas cidades</option>
              {cities.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
            {isFiltered && (
              <button
                onClick={() => { setFilterArtist(""); setFilterCity(""); }}
                className="text-xs text-blue-400 hover:text-blue-300"
              >
                Limpar filtros
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
          <p className="text-xs text-zinc-400 uppercase">Shows</p>
          <p className="text-xl font-bold mt-1">{filteredEvents.length}</p>
          <p className="text-xs text-zinc-500">em {days} dias</p>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
          <p className="text-xs text-zinc-400 uppercase">Público</p>
          <p className="text-xl font-bold mt-1">{formatNum(filteredTotals.totalAudience)}</p>
          <p className="text-xs text-zinc-500">compradores potenciais</p>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
          <p className="text-xs text-zinc-400 uppercase">Conversão</p>
          <p className="text-xl font-bold text-yellow-400 mt-1">{filteredTotals.avgConversion.toFixed(2)}%</p>
          <p className="text-xs text-zinc-500">público → camiseta</p>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
          <div className="flex items-center gap-1">
            <Shirt className="w-3 h-3 text-blue-400" />
            <p className="text-xs text-zinc-400 uppercase">Camisetas</p>
          </div>
          <p className="text-xl font-bold mt-1">{formatNum(filteredTotals.totalUnits)}</p>
          <p className="text-xs text-zinc-500">unidades p/ produzir</p>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
          <div className="flex items-center gap-1">
            <Package className="w-3 h-3 text-purple-400" />
            <p className="text-xs text-zinc-400 uppercase">Investimento</p>
          </div>
          <p className="text-xl font-bold text-purple-400 mt-1">{formatBRL(filteredTotals.totalInvestment)}</p>
          <p className="text-xs text-zinc-500">custo de produção</p>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
          <div className="flex items-center gap-1">
            <DollarSign className="w-3 h-3 text-green-400" />
            <p className="text-xs text-zinc-400 uppercase">Seu Lucro</p>
          </div>
          <p className="text-xl font-bold text-green-400 mt-1">{formatBRL(filteredTotals.totalProfit)}</p>
          <p className="text-xs text-zinc-500">faturamento: {formatBRL(filteredTotals.totalRevenue)}</p>
        </div>
      </div>

      {/* Weekly timeline */}
      {data.weekly_forecast.length > 0 && !isFiltered && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 className="w-5 h-5 text-blue-400" />
            <h3 className="font-semibold">Produção Semanal de Camisetas</h3>
            <span className="text-xs text-zinc-500 ml-auto">camisetas para produzir + lucro por semana</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            {data.weekly_forecast.map((w) => {
              const maxUnits = Math.max(...data.weekly_forecast.map((x) => x.units));
              const pct = maxUnits > 0 ? (w.units / maxUnits) * 100 : 0;
              const weekDate = new Date(w.week + "T12:00:00");
              const label = weekDate.toLocaleDateString("pt-BR", { day: "2-digit", month: "short" });
              const investment = w.units * PRODUCTION_COST;
              return (
                <div key={w.week} className="bg-zinc-800/50 rounded-lg p-3">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium">Semana {label}</span>
                    <span className="text-xs text-zinc-500">{w.events} shows</span>
                  </div>
                  <div className="w-full h-2 bg-zinc-700 rounded-full overflow-hidden mb-2">
                    <div
                      className="h-full bg-gradient-to-r from-blue-500 to-green-500 rounded-full"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="flex items-center gap-1">
                      <Shirt className="w-3 h-3" />
                      {formatNum(w.units)} un.
                    </span>
                    <span className="text-green-400 font-medium">{formatBRL(w.profit)}</span>
                  </div>
                  <div className="flex justify-between text-xs text-zinc-500 mt-1">
                    <span>Investir: {formatBRL(investment)}</span>
                    <span>Faturar: {formatBRL(w.revenue)}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Events table */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg">
        <div className="p-4 border-b border-zinc-800">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2">
                <Shirt className="w-5 h-5 text-yellow-400" />
                <h3 className="font-semibold">Plano de Produção de Camisetas por Show</h3>
              </div>
              <p className="text-xs text-zinc-500 mt-1">
                Quantas camisetas produzir, investimento necessário e lucro esperado na Shopee
              </p>
            </div>
            <div className="text-xs text-zinc-500">
              {filteredEvents.length} shows {isFiltered && "(filtrado)"}
            </div>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-zinc-800 text-zinc-400">
                <th className="px-4 py-3 text-left font-medium">Prioridade</th>
                <th className="px-4 py-3 text-left font-medium">Show / Evento</th>
                <th
                  className="px-4 py-3 text-left font-medium cursor-pointer hover:text-white"
                  onClick={() => handleSort("days_until")}
                >
                  <span className="flex items-center gap-1">
                    Data {sortField === "days_until" && <ArrowUpDown className="w-3 h-3" />}
                  </span>
                </th>
                <th className="px-4 py-3 text-left font-medium">Ingresso</th>
                <th
                  className="px-4 py-3 text-left font-medium cursor-pointer hover:text-white"
                  onClick={() => handleSort("audience")}
                >
                  <span className="flex items-center gap-1">
                    Público {sortField === "audience" && <ArrowUpDown className="w-3 h-3" />}
                  </span>
                </th>
                <th
                  className="px-4 py-3 text-left font-medium cursor-pointer hover:text-white"
                  onClick={() => handleSort("conversion_rate_pct")}
                >
                  <span className="flex items-center gap-1">
                    Conversão {sortField === "conversion_rate_pct" && <ArrowUpDown className="w-3 h-3" />}
                  </span>
                </th>
                <th
                  className="px-4 py-3 text-left font-medium cursor-pointer hover:text-white"
                  onClick={() => handleSort("projected_units")}
                >
                  <span className="flex items-center gap-1">
                    Camisetas {sortField === "projected_units" && <ArrowUpDown className="w-3 h-3" />}
                  </span>
                </th>
                <th className="px-4 py-3 text-left font-medium">Investir</th>
                <th className="px-4 py-3 text-left font-medium">Preço Venda</th>
                <th
                  className="px-4 py-3 text-left font-medium cursor-pointer hover:text-white"
                  onClick={() => handleSort("projected_profit")}
                >
                  <span className="flex items-center gap-1">
                    Seu Lucro {sortField === "projected_profit" && <ArrowUpDown className="w-3 h-3" />}
                  </span>
                </th>
                <th className="px-4 py-3 text-left font-medium">Concorrentes</th>
                <th className="px-4 py-3 text-left font-medium">Ref. Shopee</th>
              </tr>
            </thead>
            <tbody>
              {filteredEvents.map((ev) => {
                const investment = ev.projected_units * PRODUCTION_COST;
                return (
                  <tr key={`${ev.event_id}-${ev.event_date}`} className="border-b border-zinc-800/50 hover:bg-zinc-800/30">
                    <td className="px-4 py-3">
                      <PriorityBadge ev={ev} />
                    </td>
                    <td className="px-4 py-3">
                      <div className="font-medium max-w-[180px] truncate" title={ev.event_title}>
                        {ev.event_title}
                      </div>
                      <div className="text-xs text-zinc-500">
                        {ev.artist} · {ev.city}
                      </div>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <div className="text-sm">
                        {new Date(ev.event_date + "T12:00:00").toLocaleDateString("pt-BR", {
                          day: "2-digit",
                          month: "short",
                        })}
                      </div>
                      <DaysUntilBadge days={ev.days_until} />
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={ev.ticket_status} />
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap font-medium">
                      {formatNum(ev.audience)}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="font-medium text-yellow-400">{ev.conversion_rate_pct}%</span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="font-bold text-blue-400">{formatNum(ev.projected_units)}</span>
                      <span className="text-xs text-zinc-500 ml-1">un.</span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="text-purple-400 font-medium">{formatBRL(investment)}</span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      {formatBRL(ev.suggested_price)}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <div className="font-bold text-green-400">{formatBRL(ev.projected_profit)}</div>
                      <div className="text-xs text-zinc-500">{formatBRL(ev.projected_revenue)} bruto</div>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className={`font-bold ${ev.matching_products > 0 ? "text-orange-400" : "text-zinc-500"}`}>
                        {ev.matching_products}
                      </span>
                      <span className="text-xs text-zinc-500 ml-1">na Shopee</span>
                    </td>
                    <td className="px-4 py-3">
                      {ev.best_seller_url ? (
                        <a
                          href={ev.best_seller_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-1 text-blue-400 hover:text-blue-300 text-xs max-w-[130px]"
                          title={ev.best_seller_title || ""}
                        >
                          <span className="truncate">{ev.best_seller_title}</span>
                          <ExternalLink className="w-3 h-3 flex-shrink-0" />
                        </a>
                      ) : (
                        <span className="text-zinc-500 text-xs">Sem dados</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
