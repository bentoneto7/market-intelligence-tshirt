"use client";

import { useEffect, useState } from "react";
import { MarketplaceStats, fetchMarketplaceStats } from "@/lib/api";
import { Store, Package, TrendingUp } from "lucide-react";

export default function TopSellersPanel() {
  const [stats, setStats] = useState<MarketplaceStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMarketplaceStats()
      .then(setStats)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg">
      <div className="p-4 border-b border-zinc-800 flex items-center gap-2">
        <Store className="w-5 h-5 text-orange-400" />
        <h2 className="text-lg font-semibold">Top Vendedores</h2>
      </div>

      <div className="p-4 space-y-3">
        {loading || !stats ? (
          [...Array(5)].map((_, i) => (
            <div key={i} className="h-14 bg-zinc-800 rounded animate-pulse" />
          ))
        ) : (
          stats.top_sellers.slice(0, 8).map((seller, index) => (
            <div
              key={seller.seller}
              className="flex items-center gap-3 p-2 rounded-lg hover:bg-zinc-800/50 transition-colors"
            >
              <div
                className={`flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-sm font-bold ${
                  index < 3
                    ? "text-orange-400 bg-zinc-800"
                    : "text-zinc-500 bg-zinc-800/50"
                }`}
              >
                {index + 1}
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-medium text-sm">{seller.seller}</div>
                <div className="flex items-center gap-3 text-xs text-zinc-500 mt-0.5">
                  <span className="flex items-center gap-1">
                    <Package className="w-3 h-3" />
                    {seller.products} produtos
                  </span>
                </div>
              </div>
              <div className="text-right">
                <div className="flex items-center gap-1 text-sm font-bold text-blue-400">
                  <TrendingUp className="w-3 h-3" />
                  {seller.avg_sold.toLocaleString("pt-BR")}
                </div>
                <div className="text-[10px] text-zinc-500">média vendas</div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
