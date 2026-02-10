"use client";

import { useEffect, useState } from "react";
import { Event, EventFilters as Filters, fetchEvents } from "@/lib/api";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import {
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
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

export default function EventsTable() {
  const [events, setEvents] = useState<Event[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState<string>("event_date");
  const [filters, setFilters] = useState<Filters>({});
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

  const sortedEvents = [...events].sort((a, b) => {
    if (sortBy === "event_date") return new Date(a.event_date).getTime() - new Date(b.event_date).getTime();
    if (sortBy === "hype_score") return b.hype_score - a.hype_score;
    if (sortBy === "sales_potential_score") return b.sales_potential_score - a.sales_potential_score;
    if (sortBy === "city") return (a.venue?.city || "").localeCompare(b.venue?.city || "");
    return 0;
  });

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg">
      <div className="p-4 border-b border-zinc-800">
        <h2 className="text-lg font-semibold">Próximos Eventos</h2>
        <div className="flex flex-wrap gap-2 mt-3">
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
              setFilters((f) => ({
                ...f,
                genre: e.target.value || undefined,
              }));
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

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-zinc-800 text-zinc-400">
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
                  <td colSpan={8} className="px-4 py-4">
                    <div className="h-4 bg-zinc-800 rounded animate-pulse" />
                  </td>
                </tr>
              ))
            ) : sortedEvents.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-4 py-8 text-center text-zinc-500">
                  Nenhum evento encontrado
                </td>
              </tr>
            ) : (
              sortedEvents.map((event) => (
                <tr
                  key={event.id}
                  className="border-b border-zinc-800/50 hover:bg-zinc-800/30 transition-colors"
                >
                  <td className="px-4 py-3 whitespace-nowrap">
                    {format(new Date(event.event_date), "dd MMM yyyy", { locale: ptBR })}
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
