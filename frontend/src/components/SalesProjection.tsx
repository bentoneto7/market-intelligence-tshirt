"use client";

import { useEffect, useState } from "react";
import {
  SalesProjection as ProjectionData,
  ArtistProjection,
  fetchSalesProjection,
} from "@/lib/api";
import {
  TrendingUp,
  DollarSign,
  Target,
  BarChart3,
  ArrowUpRight,
  ArrowRight,
  ArrowDownRight,
  Zap,
} from "lucide-react";

function GrowthBadge({ level }: { level: string }) {
  const config: Record<string, { label: string; color: string; Icon: typeof ArrowUpRight }> = {
    alto: { label: "Alto", color: "bg-green-500/20 text-green-400", Icon: ArrowUpRight },
    medio: { label: "Médio", color: "bg-yellow-500/20 text-yellow-400", Icon: ArrowRight },
    baixo: { label: "Baixo", color: "bg-zinc-700 text-zinc-400", Icon: ArrowDownRight },
  };
  const cfg = config[level] || config.baixo;
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium ${cfg.color}`}>
      <cfg.Icon className="w-3 h-3" />
      {cfg.label}
    </span>
  );
}

function MarginBar({ pct }: { pct: number }) {
  const color = pct >= 50 ? "bg-green-500" : pct >= 35 ? "bg-yellow-500" : "bg-red-500";
  return (
    <div className="flex items-center gap-2">
      <div className="w-16 h-2 bg-zinc-800 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${Math.min(pct, 100)}%` }} />
      </div>
      <span className="text-xs font-medium">{pct}%</span>
    </div>
  );
}

function formatBRL(value: number): string {
  return value.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function formatNumber(value: number): string {
  return value.toLocaleString("pt-BR");
}

export default function SalesProjection() {
  const [data, setData] = useState<ProjectionData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSalesProjection()
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="bg-zinc-900 border border-zinc-800 rounded-lg p-6 animate-pulse h-40" />
        ))}
      </div>
    );
  }

  if (!data) return null;

  const opp = data.opportunity_score;
  const categoryLabels: Record<string, string> = {
    camiseta_banda: "Bandas",
    camiseta_artista: "Artistas",
    camiseta_festival: "Festivais",
    camiseta_generica: "Genérica",
    sem_categoria: "Outros",
  };

  return (
    <div className="space-y-6">
      {/* Revenue overview cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-zinc-400">Volume do Mercado na Shopee</p>
              <p className="text-2xl font-bold text-green-400 mt-1">
                {formatBRL(data.total_market_revenue)}
              </p>
              <p className="text-xs text-zinc-500 mt-1">camisetas vendidas pelos concorrentes/mês</p>
            </div>
            <div className="p-3 rounded-lg bg-green-400/10">
              <DollarSign className="w-6 h-6 text-green-400" />
            </div>
          </div>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-zinc-400">Camisetas Vendidas (Mercado)</p>
              <p className="text-2xl font-bold mt-1">{formatNumber(data.total_units_sold)}</p>
              <p className="text-xs text-zinc-500 mt-1">~{formatNumber(Math.round(data.total_units_sold / 3))}/mês na Shopee</p>
            </div>
            <div className="p-3 rounded-lg bg-blue-400/10">
              <BarChart3 className="w-6 h-6 text-blue-400" />
            </div>
          </div>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-zinc-400">Seu ROI por Camiseta</p>
              <p className="text-2xl font-bold text-yellow-400 mt-1">{opp.projected_roi_pct}%</p>
              <p className="text-xs text-zinc-500 mt-1">custo R$15 + taxa Shopee 12%</p>
            </div>
            <div className="p-3 rounded-lg bg-yellow-400/10">
              <TrendingUp className="w-6 h-6 text-yellow-400" />
            </div>
          </div>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-zinc-400">Investimento Inicial</p>
              <p className="text-2xl font-bold text-purple-400 mt-1">{formatBRL(opp.recommended_investment)}</p>
              <p className="text-xs text-zinc-500 mt-1">50 camisetas por artista</p>
            </div>
            <div className="p-3 rounded-lg bg-purple-400/10">
              <Target className="w-6 h-6 text-purple-400" />
            </div>
          </div>
        </div>
      </div>

      {/* Opportunity summary */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5">
        <div className="flex items-center gap-2 mb-4">
          <Zap className="w-5 h-5 text-yellow-400" />
          <h3 className="font-semibold">Análise do Mercado de Camisetas na Shopee</h3>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-xs text-zinc-400 uppercase tracking-wider">Demanda</p>
            <p className="text-lg font-bold capitalize mt-1">{opp.market_size}</p>
          </div>
          <div>
            <p className="text-xs text-zinc-400 uppercase tracking-wider">Concorrentes</p>
            <p className="text-lg font-bold capitalize mt-1">{opp.competition_level}</p>
          </div>
          <div>
            <p className="text-xs text-zinc-400 uppercase tracking-wider">Sua Margem</p>
            <p className="text-lg font-bold text-green-400 mt-1">{opp.avg_profit_margin}%</p>
          </div>
          <div>
            <p className="text-xs text-zinc-400 uppercase tracking-wider">Preço Médio Shopee</p>
            <p className="text-lg font-bold mt-1">{formatBRL(data.avg_ticket)}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Artist projections table */}
        <div className="lg:col-span-2 bg-zinc-900 border border-zinc-800 rounded-lg">
          <div className="p-4 border-b border-zinc-800">
            <h3 className="font-semibold">Sua Projeção de Vendas de Camisetas</h3>
            <p className="text-xs text-zinc-500 mt-1">Quanto você pode faturar vendendo camisetas na Shopee por artista</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-zinc-800 text-zinc-400">
                  <th className="px-4 py-3 text-left font-medium">Artista</th>
                  <th className="px-4 py-3 text-left font-medium">Vendidos</th>
                  <th className="px-4 py-3 text-left font-medium">Receita/Mês</th>
                  <th className="px-4 py-3 text-left font-medium">Preço Sugerido</th>
                  <th className="px-4 py-3 text-left font-medium">Margem</th>
                  <th className="px-4 py-3 text-left font-medium">Potencial</th>
                </tr>
              </thead>
              <tbody>
                {data.projections.map((proj) => (
                  <tr key={proj.artist} className="border-b border-zinc-800/50 hover:bg-zinc-800/30">
                    <td className="px-4 py-3">
                      <div className="font-medium">{proj.artist}</div>
                      <div className="text-xs text-zinc-500">{proj.products_count} produtos | {proj.market_share_pct}% mercado</div>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <div className="font-bold">{formatNumber(proj.total_sold)}</div>
                      <div className="text-xs text-zinc-500">~{formatNumber(proj.estimated_units_per_month)}/mês</div>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="font-bold text-green-400">{formatBRL(proj.estimated_monthly_revenue)}</span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <div className="font-medium">{formatBRL(proj.suggested_price)}</div>
                      <div className="text-xs text-zinc-500">Avg: {formatBRL(proj.avg_price)}</div>
                    </td>
                    <td className="px-4 py-3">
                      <MarginBar pct={proj.profit_margin_pct} />
                    </td>
                    <td className="px-4 py-3">
                      <GrowthBadge level={proj.growth_potential} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Category breakdown */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg">
          <div className="p-4 border-b border-zinc-800">
            <h3 className="font-semibold">Vendas de Camisetas por Categoria</h3>
          </div>
          <div className="p-4 space-y-4">
            {data.category_breakdown.map((cat) => {
              const maxRev = Math.max(...data.category_breakdown.map((c) => c.revenue_estimate));
              const pct = maxRev > 0 ? (cat.revenue_estimate / maxRev) * 100 : 0;
              return (
                <div key={cat.category}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium">{categoryLabels[cat.category] || cat.category}</span>
                    <span className="text-green-400 font-bold">{formatBRL(cat.revenue_estimate)}</span>
                  </div>
                  <div className="w-full h-2 bg-zinc-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-xs text-zinc-500 mt-1">
                    <span>{cat.products} produtos</span>
                    <span>{formatNumber(cat.total_sold)} vendidos</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
