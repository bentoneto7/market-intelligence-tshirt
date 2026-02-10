"use client";

import { useEffect, useState } from "react";
import { Event, fetchEvents, fetchMarketplaceProducts, MarketplaceProduct } from "@/lib/api";
import { Calendar, ExternalLink, ShoppingBag, Star, Shirt, DollarSign, TrendingUp, Package } from "lucide-react";

const PRODUCTION_COST = 15.0;
const MARKETPLACE_FEE = 0.12;
const BASE_CONVERSION = 0.02;

function formatBRL(v: number) {
  return v.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

export default function EventProductFilter() {
  const [events, setEvents] = useState<Event[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [products, setProducts] = useState<MarketplaceProduct[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchEvents({ page_size: 50 })
      .then((res) => setEvents(res.events))
      .catch(console.error);
  }, []);

  useEffect(() => {
    if (!selectedEvent) {
      setProducts([]);
      return;
    }
    setLoading(true);
    const artistName = selectedEvent.artist?.name || "";
    fetchMarketplaceProducts({
      related_artist: artistName,
      sort_by: "sold_count",
      page_size: 20,
    })
      .then((res) => setProducts(res.products))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [selectedEvent]);

  // Calculate t-shirt projection for selected event
  const projection = selectedEvent && products.length > 0
    ? (() => {
        const audience = selectedEvent.estimated_audience || 0;
        const statusMult = { sold_out: 1.8, selling_fast: 1.4, available: 1.0 }[selectedEvent.ticket_status || "available"] || 1.0;
        const festivalMult = selectedEvent.is_festival ? 1.3 : 1.0;
        const hypeMult = 1.0 + (selectedEvent.hype_score / 200);
        const conversion = BASE_CONVERSION * statusMult * festivalMult * hypeMult;
        const units = Math.round(audience * conversion);
        const avgPrice = products.reduce((s, p) => s + p.price, 0) / products.length;
        const sellPrice = Math.max(avgPrice * 0.9, PRODUCTION_COST * 2.5);
        const investment = units * PRODUCTION_COST;
        const revenue = units * sellPrice;
        const netPerUnit = sellPrice - PRODUCTION_COST - (sellPrice * MARKETPLACE_FEE);
        const profit = units * netPerUnit;
        return { units, sellPrice, investment, revenue, profit, conversion: conversion * 100 };
      })()
    : null;

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg">
      <div className="p-4 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <Shirt className="w-5 h-5 text-blue-400" />
          <h3 className="font-semibold">Camisetas por Show</h3>
        </div>
        <p className="text-xs text-zinc-500 mt-1">
          Selecione um show para ver concorrentes e projeção de vendas
        </p>
      </div>

      <div className="p-4">
        <select
          className="w-full bg-zinc-800 border border-zinc-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
          onChange={(e) => {
            const ev = events.find((ev) => ev.id === Number(e.target.value));
            setSelectedEvent(ev || null);
          }}
          value={selectedEvent?.id || ""}
        >
          <option value="">Selecionar show...</option>
          {events.map((ev) => {
            const dt = new Date(ev.event_date + "T12:00:00");
            const dateStr = dt.toLocaleDateString("pt-BR", { day: "2-digit", month: "short" });
            return (
              <option key={ev.id} value={ev.id}>
                {ev.title} - {dateStr} - {ev.venue?.city || ""}
              </option>
            );
          })}
        </select>
      </div>

      {selectedEvent && (
        <div className="px-4 pb-2">
          <div className="bg-zinc-800/50 rounded-lg p-3 mb-3">
            <div className="flex justify-between items-start">
              <div>
                <div className="font-medium text-sm">{selectedEvent.title}</div>
                <div className="text-xs text-zinc-500 mt-1">
                  {selectedEvent.venue?.name} - {selectedEvent.venue?.city}
                  {" | "}
                  {new Date(selectedEvent.event_date + "T12:00:00").toLocaleDateString("pt-BR")}
                </div>
              </div>
              <div className="flex gap-1">
                <span className="px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 text-xs font-medium">
                  Hype {selectedEvent.hype_score.toFixed(0)}
                </span>
              </div>
            </div>
            <div className="flex gap-3 mt-2 text-xs text-zinc-400">
              <span>Público: {(selectedEvent.estimated_audience || 0).toLocaleString("pt-BR")}</span>
              <span>Ingresso: {formatBRL(selectedEvent.ticket_price_min || 0)} - {formatBRL(selectedEvent.ticket_price_max || 0)}</span>
            </div>
          </div>

          {/* T-shirt projection summary */}
          {projection && (
            <div className="bg-gradient-to-r from-green-500/10 to-blue-500/10 border border-green-500/20 rounded-lg p-3 mb-3">
              <div className="text-xs font-semibold text-green-400 uppercase mb-2 flex items-center gap-1">
                <TrendingUp className="w-3 h-3" />
                Sua Projeção de Camisetas
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-zinc-400">Produzir:</span>
                  <span className="font-bold text-blue-400 ml-1">{projection.units} un.</span>
                </div>
                <div>
                  <span className="text-zinc-400">Investir:</span>
                  <span className="font-bold text-purple-400 ml-1">{formatBRL(projection.investment)}</span>
                </div>
                <div>
                  <span className="text-zinc-400">Vender a:</span>
                  <span className="font-bold ml-1">{formatBRL(projection.sellPrice)}</span>
                </div>
                <div>
                  <span className="text-zinc-400">Seu Lucro:</span>
                  <span className="font-bold text-green-400 ml-1">{formatBRL(projection.profit)}</span>
                </div>
              </div>
              <div className="mt-2 text-xs text-zinc-500">
                Conversão: {projection.conversion.toFixed(2)}% | Faturamento: {formatBRL(projection.revenue)}
              </div>
            </div>
          )}
        </div>
      )}

      {loading && (
        <div className="px-4 pb-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-16 bg-zinc-800 rounded animate-pulse mb-2" />
          ))}
        </div>
      )}

      {!loading && selectedEvent && products.length === 0 && (
        <div className="px-4 pb-4 text-center text-zinc-500 text-sm py-4">
          Nenhum concorrente encontrado na Shopee para este artista
        </div>
      )}

      {!loading && products.length > 0 && (
        <div className="px-4 pb-4">
          <div className="text-xs text-zinc-400 mb-2 font-medium">
            {products.length} concorrentes na Shopee · {selectedEvent?.artist?.name}
          </div>
          <div className="space-y-2 max-h-[350px] overflow-y-auto">
            {products.map((p) => (
              <div
                key={p.id}
                className="flex items-center justify-between bg-zinc-800/50 rounded-lg p-3 hover:bg-zinc-800 transition-colors"
              >
                <div className="flex-1 min-w-0 mr-3">
                  <div className="font-medium text-sm truncate" title={p.title}>
                    {p.title}
                  </div>
                  <div className="flex items-center gap-3 mt-1 text-xs text-zinc-500">
                    <span className="font-bold text-green-400 text-sm">{formatBRL(p.price)}</span>
                    <span className="flex items-center gap-1">
                      <ShoppingBag className="w-3 h-3" />
                      {p.sold_count.toLocaleString("pt-BR")} vendidos
                    </span>
                    {p.rating && (
                      <span className="flex items-center gap-1">
                        <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                        {p.rating.toFixed(1)}
                      </span>
                    )}
                  </div>
                </div>
                <a
                  href={p.product_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 rounded hover:bg-zinc-700 transition-colors flex-shrink-0"
                >
                  <ExternalLink className="w-4 h-4 text-zinc-400" />
                </a>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
