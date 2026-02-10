"use client";

import { useState, useMemo } from "react";
import {
  Calculator,
  Shirt,
  DollarSign,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
} from "lucide-react";

function formatBRL(v: number) {
  return v.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

export default function ScenarioSimulator() {
  const [costPerUnit, setCostPerUnit] = useState(15);
  const [sellPrice, setSellPrice] = useState(45);
  const [units, setUnits] = useState(500);
  const [marketplaceFee, setMarketplaceFee] = useState(12);

  const results = useMemo(() => {
    const investment = costPerUnit * units;
    const grossRevenue = sellPrice * units;
    const feeAmount = grossRevenue * (marketplaceFee / 100);
    const netRevenue = grossRevenue - feeAmount;
    const profit = netRevenue - investment;
    const roi = investment > 0 ? (profit / investment) * 100 : 0;
    const marginPct = grossRevenue > 0 ? (profit / grossRevenue) * 100 : 0;
    const breakeven = sellPrice - (sellPrice * marketplaceFee / 100) > 0
      ? Math.ceil(investment / (sellPrice - (sellPrice * marketplaceFee / 100)))
      : 0;

    return {
      investment,
      grossRevenue,
      feeAmount,
      netRevenue,
      profit,
      roi,
      marginPct,
      breakeven,
    };
  }, [costPerUnit, sellPrice, units, marketplaceFee]);

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg">
      <div className="p-4 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <Calculator className="w-5 h-5 text-cyan-400" />
          <h3 className="font-semibold">Simulador de Cenários</h3>
        </div>
        <p className="text-xs text-zinc-500 mt-1">
          Ajuste preço, custo e volume para simular o impacto no lucro
        </p>
      </div>

      <div className="p-5">
        {/* Inputs */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div>
            <label className="text-xs text-zinc-400 block mb-1.5">
              Custo por unidade (R$)
            </label>
            <input
              type="range"
              min={5}
              max={40}
              step={0.5}
              value={costPerUnit}
              onChange={(e) => setCostPerUnit(Number(e.target.value))}
              className="w-full accent-purple-500"
            />
            <div className="flex justify-between mt-1">
              <span className="text-xs text-zinc-500">R$5</span>
              <span className="text-sm font-bold text-purple-400">{formatBRL(costPerUnit)}</span>
              <span className="text-xs text-zinc-500">R$40</span>
            </div>
          </div>

          <div>
            <label className="text-xs text-zinc-400 block mb-1.5">
              Preço de venda (R$)
            </label>
            <input
              type="range"
              min={25}
              max={120}
              step={1}
              value={sellPrice}
              onChange={(e) => setSellPrice(Number(e.target.value))}
              className="w-full accent-yellow-500"
            />
            <div className="flex justify-between mt-1">
              <span className="text-xs text-zinc-500">R$25</span>
              <span className="text-sm font-bold text-yellow-400">{formatBRL(sellPrice)}</span>
              <span className="text-xs text-zinc-500">R$120</span>
            </div>
          </div>

          <div>
            <label className="text-xs text-zinc-400 block mb-1.5">
              Volume de produção
            </label>
            <input
              type="range"
              min={50}
              max={5000}
              step={50}
              value={units}
              onChange={(e) => setUnits(Number(e.target.value))}
              className="w-full accent-blue-500"
            />
            <div className="flex justify-between mt-1">
              <span className="text-xs text-zinc-500">50</span>
              <span className="text-sm font-bold text-blue-400">{units.toLocaleString("pt-BR")} un.</span>
              <span className="text-xs text-zinc-500">5.000</span>
            </div>
          </div>

          <div>
            <label className="text-xs text-zinc-400 block mb-1.5">
              Taxa marketplace (%)
            </label>
            <input
              type="range"
              min={0}
              max={25}
              step={1}
              value={marketplaceFee}
              onChange={(e) => setMarketplaceFee(Number(e.target.value))}
              className="w-full accent-orange-500"
            />
            <div className="flex justify-between mt-1">
              <span className="text-xs text-zinc-500">0%</span>
              <span className="text-sm font-bold text-orange-400">{marketplaceFee}%</span>
              <span className="text-xs text-zinc-500">25%</span>
            </div>
          </div>
        </div>

        {/* Results */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
          <div className="bg-zinc-800/50 rounded-lg p-3 border border-zinc-700/50">
            <div className="flex items-center gap-1 text-xs text-zinc-400 mb-1">
              <Shirt className="w-3 h-3 text-purple-400" /> Investimento
            </div>
            <p className="text-lg font-bold text-purple-400">{formatBRL(results.investment)}</p>
          </div>

          <div className="bg-zinc-800/50 rounded-lg p-3 border border-zinc-700/50">
            <div className="flex items-center gap-1 text-xs text-zinc-400 mb-1">
              <DollarSign className="w-3 h-3 text-yellow-400" /> Faturamento Bruto
            </div>
            <p className="text-lg font-bold text-yellow-400">{formatBRL(results.grossRevenue)}</p>
            <p className="text-xs text-zinc-500">- {formatBRL(results.feeAmount)} taxa</p>
          </div>

          <div className="bg-zinc-800/50 rounded-lg p-3 border border-zinc-700/50">
            <div className="flex items-center gap-1 text-xs text-zinc-400 mb-1">
              <TrendingUp className="w-3 h-3 text-green-400" /> Lucro Líquido
            </div>
            <p className={`text-lg font-bold ${results.profit >= 0 ? "text-green-400" : "text-red-400"}`}>
              {formatBRL(results.profit)}
            </p>
            <p className="text-xs text-zinc-500">margem: {results.marginPct.toFixed(1)}%</p>
          </div>

          <div className="bg-zinc-800/50 rounded-lg p-3 border border-zinc-700/50">
            <div className="flex items-center gap-1 text-xs text-zinc-400 mb-1">
              {results.roi >= 0 ? (
                <CheckCircle className="w-3 h-3 text-green-400" />
              ) : (
                <AlertTriangle className="w-3 h-3 text-red-400" />
              )}
              ROI
            </div>
            <p className={`text-lg font-bold ${results.roi >= 0 ? "text-green-400" : "text-red-400"}`}>
              {results.roi.toFixed(0)}%
            </p>
            <p className="text-xs text-zinc-500">breakeven: {results.breakeven} un.</p>
          </div>
        </div>

        {/* Visual profit bar */}
        <div className="bg-zinc-800/30 rounded-lg p-3">
          <div className="flex items-center justify-between text-xs text-zinc-400 mb-2">
            <span>Composição do Preço</span>
            <span>{formatBRL(sellPrice)}/un.</span>
          </div>
          <div className="flex h-6 rounded-full overflow-hidden">
            {(() => {
              const fee = sellPrice * (marketplaceFee / 100);
              const cost = costPerUnit;
              const profitPerUnit = sellPrice - fee - cost;
              const costPct = Math.max(0, (cost / sellPrice) * 100);
              const feePct = Math.max(0, (fee / sellPrice) * 100);
              const profitPct = Math.max(0, (profitPerUnit / sellPrice) * 100);
              return (
                <>
                  <div
                    className="bg-purple-500/70 flex items-center justify-center text-[10px] font-medium"
                    style={{ width: `${costPct}%` }}
                    title={`Custo: ${formatBRL(cost)}`}
                  >
                    {costPct > 15 && "Custo"}
                  </div>
                  <div
                    className="bg-orange-500/70 flex items-center justify-center text-[10px] font-medium"
                    style={{ width: `${feePct}%` }}
                    title={`Taxa: ${formatBRL(fee)}`}
                  >
                    {feePct > 10 && "Taxa"}
                  </div>
                  <div
                    className={`${profitPerUnit >= 0 ? "bg-green-500/70" : "bg-red-500/70"} flex items-center justify-center text-[10px] font-medium`}
                    style={{ width: `${Math.abs(profitPct)}%` }}
                    title={`Lucro: ${formatBRL(profitPerUnit)}`}
                  >
                    {profitPct > 15 && "Lucro"}
                  </div>
                </>
              );
            })()}
          </div>
          <div className="flex justify-between mt-1.5 text-[10px] text-zinc-500">
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-purple-500/70" /> Custo
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-orange-500/70" /> Taxa Shopee
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-green-500/70" /> Seu Lucro
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
