"use client";

import { useEffect, useState } from "react";
import { MarketplaceStats, fetchMarketplaceStats } from "@/lib/api";
import { Music, Package, DollarSign } from "lucide-react";

export default function TopArtistsPanel() {
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
        <Music className="w-5 h-5 text-purple-400" />
        <h2 className="text-lg font-semibold">Top Artistas no Marketplace</h2>
      </div>

      <div className="p-4 space-y-3">
        {loading || !stats ? (
          [...Array(5)].map((_, i) => (
            <div key={i} className="h-14 bg-zinc-800 rounded animate-pulse" />
          ))
        ) : (
          stats.top_artists.map((artist, index) => (
            <div
              key={artist.artist}
              className="flex items-center gap-3 p-2 rounded-lg hover:bg-zinc-800/50 transition-colors"
            >
              <div
                className={`flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-sm font-bold ${
                  index < 3
                    ? "text-yellow-400 bg-zinc-800"
                    : "text-zinc-500 bg-zinc-800/50"
                }`}
              >
                {index + 1}
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-medium text-sm">{artist.artist}</div>
                <div className="flex items-center gap-3 text-xs text-zinc-500 mt-0.5">
                  <span className="flex items-center gap-1">
                    <Package className="w-3 h-3" />
                    {artist.products} produtos
                  </span>
                  <span className="flex items-center gap-1">
                    <DollarSign className="w-3 h-3" />
                    R$ {artist.avg_price.toFixed(0)} médio
                  </span>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm font-bold text-green-400">
                  {artist.total_sold.toLocaleString("pt-BR")}
                </div>
                <div className="text-[10px] text-zinc-500">vendidos</div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
