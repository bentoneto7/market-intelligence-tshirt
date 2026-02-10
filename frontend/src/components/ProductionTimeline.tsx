"use client";

import { useEffect, useState } from "react";
import { Event, fetchEvents } from "@/lib/api";
import { format, addMonths, differenceInDays } from "date-fns";
import { ptBR } from "date-fns/locale";
import { Factory } from "lucide-react";

export default function ProductionTimeline() {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const today = new Date().toISOString().split("T")[0];
    const future = addMonths(new Date(), 3).toISOString().split("T")[0];

    fetchEvents({
      date_from: today,
      date_to: future,
      min_sales_potential: 30,
      page_size: 50,
    })
      .then((res) => setEvents(res.events))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
        <div className="h-48 bg-zinc-800 rounded animate-pulse" />
      </div>
    );
  }

  const today = new Date();
  const sorted = [...events]
    .filter((e) => e.production_start_date)
    .sort(
      (a, b) =>
        new Date(a.production_start_date!).getTime() -
        new Date(b.production_start_date!).getTime()
    );

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg">
      <div className="p-4 border-b border-zinc-800 flex items-center gap-2">
        <Factory className="w-5 h-5 text-blue-400" />
        <h2 className="text-lg font-semibold">Timeline de Produção</h2>
        <span className="text-xs text-zinc-500 ml-2">Próximos 3 meses</span>
      </div>

      <div className="p-4 space-y-2 max-h-96 overflow-y-auto">
        {sorted.length === 0 ? (
          <p className="text-center text-zinc-500 py-4">
            Nenhum evento com janela de produção
          </p>
        ) : (
          sorted.map((event) => {
            const prodStart = new Date(event.production_start_date!);
            const prodDeadline = event.production_deadline
              ? new Date(event.production_deadline)
              : null;
            const eventDate = new Date(event.event_date);
            const daysUntilStart = differenceInDays(prodStart, today);
            const daysUntilEvent = differenceInDays(eventDate, today);

            let urgency = "border-zinc-700";
            let urgencyLabel = "";
            if (daysUntilStart <= 0) {
              urgency = "border-red-500 bg-red-500/5";
              urgencyLabel = "AGORA";
            } else if (daysUntilStart <= 7) {
              urgency = "border-orange-500 bg-orange-500/5";
              urgencyLabel = `${daysUntilStart}d`;
            } else if (daysUntilStart <= 14) {
              urgency = "border-yellow-500 bg-yellow-500/5";
              urgencyLabel = `${daysUntilStart}d`;
            }

            return (
              <div
                key={event.id}
                className={`border rounded-lg p-3 ${urgency} transition-colors`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-sm">
                        {event.artist?.name || event.title}
                      </span>
                      {urgencyLabel && (
                        <span
                          className={`text-xs px-1.5 py-0.5 rounded font-bold ${
                            daysUntilStart <= 0
                              ? "bg-red-500/20 text-red-400"
                              : daysUntilStart <= 7
                              ? "bg-orange-500/20 text-orange-400"
                              : "bg-yellow-500/20 text-yellow-400"
                          }`}
                        >
                          {urgencyLabel}
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-zinc-500 mt-1">
                      {event.venue?.city} &bull; Show:{" "}
                      {format(eventDate, "dd/MM/yyyy")} &bull; Potencial:{" "}
                      {event.sales_potential_score.toFixed(0)}
                    </div>
                  </div>
                  <div className="text-right text-xs">
                    <div className="text-zinc-400">
                      Produzir: {format(prodStart, "dd/MM", { locale: ptBR })}
                      {prodDeadline && (
                        <span className="text-zinc-600">
                          {" → "}
                          {format(prodDeadline, "dd/MM", { locale: ptBR })}
                        </span>
                      )}
                    </div>
                    <div className="text-zinc-600">
                      {daysUntilEvent}d até o show
                    </div>
                  </div>
                </div>

                {/* Progress bar */}
                <div className="mt-2 flex items-center gap-1 text-[10px] text-zinc-600">
                  <span>Hoje</span>
                  <div className="flex-1 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-500 to-green-500 rounded-full"
                      style={{
                        width: `${Math.max(
                          5,
                          Math.min(
                            100,
                            ((daysUntilEvent - daysUntilStart) / daysUntilEvent) * 100
                          )
                        )}%`,
                      }}
                    />
                  </div>
                  <span>Show</span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
