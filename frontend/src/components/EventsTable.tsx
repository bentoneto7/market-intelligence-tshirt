"use client";

import { useEffect, useState } from "react";
import { Event, EventFilters as Filters, fetchEvents } from "@/lib/api";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import {
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  ChevronUp,
  Search,
  X,
  MapPin,
  Users,
  Shirt,
} from "lucide-react";

function HypeBadge({ score }: { score: number }) {
  let color = "bg-zinc-700 text-zinc-300";
  let label = "Baixo";
  if (score >= 70) {
    color = "bg-red-500/20 text-red-400";
    label = "Alto";
  } else if (score >= 40) {
    color = "bg-yellow-500/20 text-yellow-400";
    label = "Médio";
  }
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${color}`}>
      {score.toFixed(0)} - {label}
    </span>
  );
}

function StatusBadge({ status }: { status: string | null }) {
  if (!status) return <span className="text-zinc-500">-</span>;
  const map: Record<string, string> = {
    sold_out: "bg-red-500/20 text-red-400",
    selling_fast: "bg-orange-500/20 text-orange-400",
    available: "bg-green-500/20 text-green-400",
  };
  const labels: Record<string, string> = {
    sold_out: "Esgotado",
    selling_fast: "Vendendo rápido",
    available: "Disponível",
  };
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${map[status] || "bg-zinc-700 text-zinc-300"}`}>
      {labels[status] || status}
    </span>
  );
}

function DaysUntilBadge({ date }: { date: string }) {
  const days = Math.ceil(
    (new Date(date).getTime() - Date.now()) / (1000 * 60 * 60 * 24)
  );
  if (days < 0) return null;
  const cls =
    days <= 7 ? "text-red-400" : days <= 21 ? "text-yellow-400" : "text-green-400";
  return (
    <span className={`text-[10px] font-bold ${cls}`}>
      {days === 0 ? "HOJE" : days === 1 ? "Amanhã" : `em ${days}d`}
    </span>
  );
}

function EventExpandedRow({ event }: { event: Event }) {
  const audience = event.estimated_audience || 0;
  const conversionRate = 0.02;
  const units = Math.round(audience * conversionRate);
  const costPerUnit = 15;
  const sellPrice = event.ticket_price_min
    ? Math.round(event.ticket_price_min * 0.12 + 35)
    : 45;
  const investment = units * costPerUnit;
  const revenue = units * sellPrice;
  const profit = revenue - investment;

  return (
    <tr className="bg-zinc-800/30 border-b border-zinc-800/50">
      <td colSpan={8} className="px-4 py-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-zinc-900/50 rounded-lg p-3">
            <div className="flex items-center gap-1.5 text-xs text-zinc-400 mb-1">
              <Shirt className="w-3 h-3" /> Projeção de Camisetas
            </div>
            <p className="text-lg font-bold text-blue-400">{units.toLocaleString("pt-BR")} un.</p>
            <p className="text-xs text-zinc-500">conversão {(conversionRate * 100).toFixed(1)}%</p>
          </div>
          <div className="bg-zinc-900/50 rounded-lg p-3">
            <div className="text-xs text-zinc-400 mb-1">Investimento</div>
            <p className="text-lg font-bold text-purple-400">
              {investment.toLocaleString("pt-BR", { style: "currency", currency: "BRL" })}
            </p>
            <p className="text-xs text-zinc-500">R${costPerUnit}/un.</p>
          </div>
          <div className="bg-zinc-900/50 rounded-lg p-3">
            <div className="text-xs text-zinc-400 mb-1">Preço Venda</div>
            <p className="text-lg font-bold text-yellow-400">
              {sellPrice.toLocaleString("pt-BR", { style: "currency", currency: "BRL" })}
            </p>
            <p className="text-xs text-zinc-500">Shopee (c/ taxa 12%)</p>
          </div>
          <div className="bg-zinc-900/50 rounded-lg p-3">
            <div className="text-xs text-zinc-400 mb-1">Lucro Esperado</div>
            <p className={`text-lg font-bold ${profit > 0 ? "text-green-400" : "text-red-400"}`}>
              {profit.toLocaleString("pt-BR", { style: "currency", currency: "BRL" })}
            </p>
            <p className="text-xs text-zinc-500">
              ROI: {investment > 0 ? ((profit / investment) * 100).toFixed(0) : 0}%
            </p>
          </div>
        </div>
        {event.headliners && event.headliners.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1.5">
            <span className="text-xs text-zinc-400">Headliners:</span>
            {event.headliners.map((h) => (
              <span key={h} className="text-xs px-2 py-0.5 rounded bg-purple-500/20 text-purple-400">
                {h}
              </span>
            ))}
          </div>
        )}
      </td>
    </tr>
  );
}

export default function EventsTable() {
  const [events, setEvents] = useState<Event[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState<string>("event_date");
  const [filters, setFilters] = useState<Filters>({});
  const [searchText, setSearchText] = useState("");
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const pageSize = 15;

  useEffect(() => {
    setLoading(true);
    fetchEvents({ ...filters, page, page_size: pageSize })
      .then((res) => {
        setEvents(res.events);
        setTotal(res.total);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [filters, page]);

  const totalPages = Math.ceil(total / pageSize);

  const sortedEvents = [...events]
    .filter((e) => {
      if (!searchText) return true;
      const s = searchText.toLowerCase();
      return (
        e.title.toLowerCase().includes(s) ||
        (e.artist?.name || "").toLowerCase().includes(s) ||
        (e.venue?.city || "").toLowerCase().includes(s)
      );
    })
    .sort((a, b) => {
      if (sortBy === "event_date") return new Date(a.event_date).getTime() - new Date(b.event_date).getTime();
      if (sortBy === "hype_score") return b.hype_score - a.hype_score;
      if (sortBy === "sales_potential_score") return b.sales_potential_score - a.sales_potential_score;
      if (sortBy === "city") return (a.venue?.city || "").localeCompare(b.venue?.city || "");
      return 0;
    });

  // Active filters count
  const activeFilters = [filters.city, filters.genre, filters.min_hype].filter(Boolean).length;

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg">
      <div className="p-4 border-b border-zinc-800">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold">Próximos Eventos</h2>
          {activeFilters > 0 && (
            <span className="text-xs px-2 py-1 rounded-full bg-blue-500/20 text-blue-400">
              {activeFilters} filtro{activeFilters > 1 ? "s" : ""} ativo{activeFilters > 1 ? "s" : ""}
            </span>
          )}
        </div>
        <div className="flex flex-wrap gap-2">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-500" />
            <input
              type="text"
              placeholder="Buscar evento, artista..."
              className="bg-zinc-800 border border-zinc-700 rounded pl-8 pr-7 py-1.5 text-sm focus:outline-none focus:border-blue-500 w-52"
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
            />
            {searchText && (
              <button
                onClick={() => setSearchText("")}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-white"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          <input
            type="text"
            placeholder="Filtrar por cidade..."
            className="bg-zinc-800 border border-zinc-700 rounded px-3 py-1.5 text-sm focus:outline-none focus:border-blue-500"
            onChange={(e) => {
              setPage(1);
              setFilters((f) => ({ ...f, city: e.target.value || undefined }));
            }}
          />
          <select
            className="bg-zinc-800 border border-zinc-700 rounded px-3 py-1.5 text-sm focus:outline-none focus:border-blue-500"
            onChange={(e) => {
              setPage(1);
              setFilters((f) => ({ ...f, genre: e.target.value || undefined }));
            }}
          >
            <option value="">Todos os gêneros</option>
            <option value="rock">Rock</option>
            <option value="metal">Metal</option>
            <option value="pop">Pop</option>
            <option value="rap">Rap</option>
            <option value="indie">Indie</option>
            <option value="eletronica">Eletrônica</option>
            <option value="sertanejo">Sertanejo</option>
            <option value="funk">Funk</option>
          </select>
          <select
            className="bg-zinc-800 border border-zinc-700 rounded px-3 py-1.5 text-sm focus:outline-none focus:border-blue-500"
            onChange={(e) => {
              setPage(1);
              setFilters((f) => ({
                ...f,
                min_hype: e.target.value ? Number(e.target.value) : undefined,
              }));
            }}
          >
            <option value="">Qualquer hype</option>
            <option value="70">Alto hype (70+)</option>
            <option value="40">Médio+ hype (40+)</option>
          </select>
        </div>
      </div>

      {/* Mobile: Cards view */}
      <div className="block md:hidden p-4 space-y-3">
        {loading ? (
          [...Array(3)].map((_, i) => (
            <div key={i} className="h-24 bg-zinc-800 rounded-lg animate-pulse" />
          ))
        ) : sortedEvents.length === 0 ? (
          <p className="text-center text-zinc-500 py-8">Nenhum evento encontrado</p>
        ) : (
          sortedEvents.map((event) => (
            <div
              key={event.id}
              className="bg-zinc-800/50 rounded-lg p-4 border border-zinc-700/50"
              onClick={() => setExpandedId(expandedId === event.id ? null : event.id)}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="font-medium text-sm">{event.artist?.name || event.title}</div>
                  <div className="text-xs text-zinc-500 mt-0.5">
                    {event.venue?.city && (
                      <span className="inline-flex items-center gap-0.5">
                        <MapPin className="w-3 h-3" />
                        {event.venue.city}{event.venue.state && `/${event.venue.state}`}
                      </span>
                    )}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium">
                    {format(new Date(event.event_date), "dd MMM", { locale: ptBR })}
                  </div>
                  <DaysUntilBadge date={event.event_date} />
                </div>
              </div>
              <div className="flex items-center gap-2 mt-2">
                <StatusBadge status={event.ticket_status} />
                <HypeBadge score={event.hype_score} />
                {event.estimated_audience && (
                  <span className="inline-flex items-center gap-0.5 text-xs text-zinc-400">
                    <Users className="w-3 h-3" />
                    {event.estimated_audience.toLocaleString("pt-BR")}
                  </span>
                )}
              </div>
              {expandedId === event.id && (
                <div className="mt-3 pt-3 border-t border-zinc-700 grid grid-cols-2 gap-2">
                  <div>
                    <span className="text-xs text-zinc-400">Potencial</span>
                    <div className="flex items-center gap-2">
                      <div className="w-16 bg-zinc-700 rounded-full h-1.5">
                        <div
                          className="h-full rounded-full bg-gradient-to-r from-yellow-500 to-green-500"
                          style={{ width: `${Math.min(event.sales_potential_score, 100)}%` }}
                        />
                      </div>
                      <span className="text-xs font-mono font-bold">{event.sales_potential_score.toFixed(0)}</span>
                    </div>
                  </div>
                  <div>
                    <span className="text-xs text-zinc-400">Produção</span>
                    <div className="text-xs">
                      {event.production_start_date
                        ? format(new Date(event.production_start_date), "dd/MM")
                        : "-"}
                      {event.production_deadline && (
                        <span className="text-zinc-500">
                          {" → "}
                          {format(new Date(event.production_deadline), "dd/MM")}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Desktop: Table view */}
      <div className="hidden md:block overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-zinc-800 text-zinc-400">
              <th className="px-2 py-3 w-8"></th>
              {[
                { key: "event_date", label: "Data" },
                { key: "title", label: "Evento" },
                { key: "city", label: "Cidade" },
                { key: "audience", label: "Público" },
                { key: "status", label: "Ingressos" },
                { key: "hype_score", label: "Hype" },
                { key: "sales_potential_score", label: "Potencial" },
                { key: "production", label: "Iniciar Produção" },
              ].map((col) => (
                <th
                  key={col.key}
                  className="px-4 py-3 text-left font-medium cursor-pointer hover:text-white transition-colors"
                  onClick={() => setSortBy(col.key)}
                >
                  <div className="flex items-center gap-1">
                    {col.label}
                    {sortBy === col.key && <ArrowUpDown className="w-3 h-3" />}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              [...Array(5)].map((_, i) => (
                <tr key={i} className="border-b border-zinc-800/50">
                  <td colSpan={9} className="px-4 py-4">
                    <div className="h-4 bg-zinc-800 rounded animate-pulse" />
                  </td>
                </tr>
              ))
            ) : sortedEvents.length === 0 ? (
              <tr>
                <td colSpan={9} className="px-4 py-8 text-center text-zinc-500">
                  Nenhum evento encontrado
                </td>
              </tr>
            ) : (
              sortedEvents.map((event) => (
                <>
                  <tr
                    key={event.id}
                    className="border-b border-zinc-800/50 hover:bg-zinc-800/30 transition-colors cursor-pointer"
                    onClick={() => setExpandedId(expandedId === event.id ? null : event.id)}
                  >
                    <td className="px-2 py-3 text-zinc-500">
                      {expandedId === event.id ? (
                        <ChevronUp className="w-4 h-4" />
                      ) : (
                        <ChevronDown className="w-4 h-4" />
                      )}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <div>{format(new Date(event.event_date), "dd MMM yyyy", { locale: ptBR })}</div>
                      <DaysUntilBadge date={event.event_date} />
                    </td>
                    <td className="px-4 py-3">
                      <div className="font-medium">{event.title}</div>
                      <div className="text-xs text-zinc-500">
                        {event.artist?.genre || "-"}{" "}
                        {event.is_festival && (
                          <span className="ml-1 px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-400">
                            Festival
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      {event.venue?.city || "-"}
                      {event.venue?.state && (
                        <span className="text-zinc-500 ml-1">/ {event.venue.state}</span>
                      )}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      {event.estimated_audience
                        ? event.estimated_audience.toLocaleString("pt-BR")
                        : "-"}
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={event.ticket_status} />
                    </td>
                    <td className="px-4 py-3">
                      <HypeBadge score={event.hype_score} />
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-zinc-800 rounded-full h-2">
                          <div
                            className="h-2 rounded-full bg-gradient-to-r from-yellow-500 to-green-500"
                            style={{ width: `${Math.min(event.sales_potential_score, 100)}%` }}
                          />
                        </div>
                        <span className="text-xs font-mono">
                          {event.sales_potential_score.toFixed(0)}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-xs">
                      {event.production_start_date
                        ? format(new Date(event.production_start_date), "dd/MM")
                        : "-"}
                      {event.production_deadline && (
                        <span className="text-zinc-500">
                          {" → "}
                          {format(new Date(event.production_deadline), "dd/MM")}
                        </span>
                      )}
                    </td>
                  </tr>
                  {expandedId === event.id && <EventExpandedRow event={event} />}
                </>
              ))
            )}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between px-4 py-3 border-t border-zinc-800">
          <span className="text-sm text-zinc-400">
            {total} eventos encontrados
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="p-1 rounded hover:bg-zinc-800 disabled:opacity-30"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="text-sm">
              {page} / {totalPages}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="p-1 rounded hover:bg-zinc-800 disabled:opacity-30"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
