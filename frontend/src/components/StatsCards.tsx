"use client";

import { useEffect, useState } from "react";
import { DashboardStats, fetchDashboardStats } from "@/lib/api";
import {
  Calendar,
  TrendingUp,
  Flame,
  BarChart3,
} from "lucide-react";

export default function StatsCards() {
  const [stats, setStats] = useState<DashboardStats | null>(null);

  useEffect(() => {
    fetchDashboardStats().then(setStats).catch(console.error);
  }, []);

  if (!stats) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-zinc-900 border border-zinc-800 rounded-lg p-6 animate-pulse h-28" />
        ))}
      </div>
    );
  }

  const cards = [
    {
      title: "Total de Eventos",
      value: stats.total_events,
      icon: Calendar,
      color: "text-blue-400",
      bg: "bg-blue-400/10",
    },
    {
      title: "Alto Hype",
      value: stats.high_hype_count,
      icon: Flame,
      color: "text-orange-400",
      bg: "bg-orange-400/10",
    },
    {
      title: "Alto Potencial",
      value: stats.high_potential_count,
      icon: TrendingUp,
      color: "text-green-400",
      bg: "bg-green-400/10",
    },
    {
      title: "Este Mês",
      value: stats.events_this_month,
      subtitle: `Próximo mês: ${stats.events_next_month}`,
      icon: BarChart3,
      color: "text-purple-400",
      bg: "bg-purple-400/10",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => (
        <div
          key={card.title}
          className="bg-zinc-900 border border-zinc-800 rounded-lg p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-zinc-400">{card.title}</p>
              <p className="text-3xl font-bold mt-1">{card.value}</p>
              {card.subtitle && (
                <p className="text-xs text-zinc-500 mt-1">{card.subtitle}</p>
              )}
            </div>
            <div className={`p-3 rounded-lg ${card.bg}`}>
              <card.icon className={`w-6 h-6 ${card.color}`} />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
