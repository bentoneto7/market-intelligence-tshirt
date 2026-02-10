"use client";

import { useEffect, useState } from "react";
import { MarketplaceStats as Stats, fetchMarketplaceStats } from "@/lib/api";
import {
  ShoppingBag,
  DollarSign,
  TrendingUp,
  Users,
} from "lucide-react";

export default function MarketplaceStatsCards() {
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    fetchMarketplaceStats().then(setStats).catch(console.error);
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
      title: "Produtos Mapeados",
      value: stats.total_products,
      icon: ShoppingBag,
      color: "text-blue-400",
      bg: "bg-blue-400/10",
    },
    {
      title: "Preço Médio",
      value: `R$ ${stats.avg_price.toFixed(2)}`,
      icon: DollarSign,
      color: "text-green-400",
      bg: "bg-green-400/10",
    },
    {
      title: "Faixa de Preço",
      value: `R$ ${stats.price_range.min.toFixed(0)} - ${stats.price_range.max.toFixed(0)}`,
      icon: TrendingUp,
      color: "text-yellow-400",
      bg: "bg-yellow-400/10",
    },
    {
      title: "Vendedores",
      value: stats.top_sellers.length,
      subtitle: `Top: ${stats.top_sellers[0]?.seller || "-"}`,
      icon: Users,
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
              <p className="text-2xl font-bold mt-1">{card.value}</p>
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
