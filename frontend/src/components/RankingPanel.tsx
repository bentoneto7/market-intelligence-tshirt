"use client";

import { useEffect, useState } from "react";
import { Event, fetchRankings } from "@/lib/api";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import { Trophy } from "lucide-react";

export default function RankingPanel() {
  const [events, setEvents] = useState<Event[]>([]);
  const [metric, setMetric] = useState<string>("sales_potential_score");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchRankings(metric, 10)
      .then((res) => setEvents(res.events))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [metric]);

  const medalColors = ["text-yellow-400", "text-zinc-300", "text-amber-600"];

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg">
      <div className="p-4 border-b border-zinc-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Trophy className="w-5 h-5 text-yellow-400" />
            <h2 className="text-lg font-semibold">Top Oportunidades</h2>
          </div>
          <select
            className="bg-zinc-800 border border-zinc-700 rounded px-2 py-1 text-xs"
            value={metric}
            onChange={(e) => setMetric(e.target.value)}
          >
            <option value="sales_potential_score">Potencial de Vendas</option>
            <option value="hype_score">Hype Score</option>
          </select>
        </div>
      </div>

      <div className="p-4 space-y-3">
        {loading ? (
          [...Array(5)].map((_, i) => (
            <div key={i} className="h-14 bg-zinc-800 rounded animate-pulse" />
          ))
        ) : events.length === 0 ? (
          <p className="text-center text-zinc-500 py-4">Nenhum evento encontrado</p>
        ) : (
          events.map((event, index) => {
            const score =
              metric === "sales_potential_score"
                ? event.sales_potential_score
                : event.hype_score;

            return (
              <div
                key={event.id}
                className="flex items-center gap-3 p-2 rounded-lg hover:bg-zinc-800/50 transition-colors"
              >
                <div
                  className={`flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-sm font-bold ${
                    index < 3
                      ? `${medalColors[index]} bg-zinc-800`
                      : "text-zinc-500 bg-zinc-800/50"
                  }`}
                >
                  {index + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-sm truncate">
                    {event.artist?.name || event.title}
                  </div>
                  <div className="text-xs text-zinc-500">
                    {event.venue?.city || "-"} &bull;{" "}
                    {format(new Date(event.event_date), "dd MMM", { locale: ptBR })}
                    {event.is_festival && (
                      <span className="ml-1 px-1 py-0.5 rounded bg-purple-500/20 text-purple-400">
                        Festival
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex-shrink-0">
                  <div
                    className={`text-sm font-bold ${
                      score >= 70
                        ? "text-green-400"
                        : score >= 40
                        ? "text-yellow-400"
                        : "text-zinc-400"
                    }`}
                  >
                    {score.toFixed(0)}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
