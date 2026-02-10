"use client";

import { useEffect, useState } from "react";
import {
  MarketplaceProduct,
  MarketplaceFilters,
  fetchMarketplaceProducts,
} from "@/lib/api";
import {
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  Star,
} from "lucide-react";

function PriceBadge({ price, original }: { price: number; original: number | null }) {
  const discount = original ? Math.round(((original - price) / original) * 100) : 0;
  return (
    <div className="flex items-center gap-2">
      <span className="font-bold text-green-400">
        R$ {price.toFixed(2)}
      </span>
      {original && discount > 0 && (
        <>
          <span className="text-xs text-zinc-500 line-through">
            R$ {original.toFixed(2)}
          </span>
          <span className="text-xs px-1.5 py-0.5 rounded bg-red-500/20 text-red-400 font-bold">
            -{discount}%
          </span>
        </>
      )}
    </div>
  );
}

function RatingStars({ rating, count }: { rating: number | null; count: number }) {
  if (!rating) return <span className="text-zinc-500 text-xs">Sem avaliação</span>;
  return (
    <div className="flex items-center gap-1">
      <Star className="w-3.5 h-3.5 fill-yellow-400 text-yellow-400" />
      <span className="text-sm font-medium">{rating.toFixed(1)}</span>
      <span className="text-xs text-zinc-500">({count})</span>
    </div>
  );
}

function CategoryBadge({ category }: { category: string | null }) {
  if (!category) return null;
  const labels: Record<string, { label: string; color: string }> = {
    camiseta_banda: { label: "Banda", color: "bg-purple-500/20 text-purple-400" },
    camiseta_artista: { label: "Artista", color: "bg-blue-500/20 text-blue-400" },
    camiseta_festival: { label: "Festival", color: "bg-orange-500/20 text-orange-400" },
    camiseta_generica: { label: "Genérica", color: "bg-zinc-700 text-zinc-300" },
  };
  const cfg = labels[category] || { label: category, color: "bg-zinc-700 text-zinc-300" };
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-medium ${cfg.color}`}>
      {cfg.label}
    </span>
  );
}

export default function MarketplaceTable() {
  const [products, setProducts] = useState<MarketplaceProduct[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState<string>("sold_count");
  const [filters, setFilters] = useState<MarketplaceFilters>({});
  const pageSize = 20;

  useEffect(() => {
    setLoading(true);
    fetchMarketplaceProducts({ ...filters, sort_by: sortBy, page, page_size: pageSize })
      .then((res) => {
        setProducts(res.products);
        setTotal(res.total);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [filters, sortBy, page]);

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg">
      <div className="p-4 border-b border-zinc-800">
        <h2 className="text-lg font-semibold">Produtos no Marketplace</h2>
        <div className="flex flex-wrap gap-2 mt-3">
          <input
            type="text"
            placeholder="Buscar produto..."
            className="bg-zinc-800 border border-zinc-700 rounded px-3 py-1.5 text-sm focus:outline-none focus:border-blue-500 w-64"
            onChange={(e) => {
              setPage(1);
              setFilters((f) => ({ ...f, search: e.target.value || undefined }));
            }}
          />
          <input
            type="text"
            placeholder="Filtrar por artista..."
            className="bg-zinc-800 border border-zinc-700 rounded px-3 py-1.5 text-sm focus:outline-none focus:border-blue-500"
            onChange={(e) => {
              setPage(1);
              setFilters((f) => ({ ...f, related_artist: e.target.value || undefined }));
            }}
          />
          <select
            className="bg-zinc-800 border border-zinc-700 rounded px-3 py-1.5 text-sm"
            onChange={(e) => {
              setPage(1);
              setFilters((f) => ({ ...f, category: e.target.value || undefined }));
            }}
          >
            <option value="">Todas categorias</option>
            <option value="camiseta_banda">Banda</option>
            <option value="camiseta_artista">Artista</option>
            <option value="camiseta_festival">Festival</option>
            <option value="camiseta_generica">Genérica</option>
          </select>
          <select
            className="bg-zinc-800 border border-zinc-700 rounded px-3 py-1.5 text-sm"
            value={sortBy}
            onChange={(e) => {
              setPage(1);
              setSortBy(e.target.value);
            }}
          >
            <option value="sold_count">Mais vendidos</option>
            <option value="price_asc">Menor preço</option>
            <option value="price_desc">Maior preço</option>
            <option value="rating">Melhor avaliação</option>
          </select>
          <select
            className="bg-zinc-800 border border-zinc-700 rounded px-3 py-1.5 text-sm"
            onChange={(e) => {
              setPage(1);
              setFilters((f) => ({
                ...f,
                min_sold: e.target.value ? Number(e.target.value) : undefined,
              }));
            }}
          >
            <option value="">Qualquer qtd vendida</option>
            <option value="1000">1.000+ vendidos</option>
            <option value="3000">3.000+ vendidos</option>
            <option value="5000">5.000+ vendidos</option>
          </select>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-zinc-800 text-zinc-400">
              {[
                { key: "title", label: "Produto" },
                { key: "price", label: "Preço" },
                { key: "sold_count", label: "Vendidos" },
                { key: "rating", label: "Avaliação" },
                { key: "seller", label: "Vendedor" },
                { key: "category", label: "Tipo" },
                { key: "artist", label: "Artista/Evento" },
                { key: "link", label: "" },
              ].map((col) => (
                <th
                  key={col.key}
                  className="px-4 py-3 text-left font-medium"
                >
                  <div className="flex items-center gap-1">
                    {col.label}
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
            ) : products.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-4 py-8 text-center text-zinc-500">
                  Nenhum produto encontrado
                </td>
              </tr>
            ) : (
              products.map((product) => (
                <tr
                  key={product.id}
                  className="border-b border-zinc-800/50 hover:bg-zinc-800/30 transition-colors"
                >
                  <td className="px-4 py-3 max-w-xs">
                    <div className="font-medium truncate" title={product.title}>
                      {product.title}
                    </div>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <PriceBadge price={product.price} original={product.original_price} />
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span className="font-bold text-lg">
                      {product.sold_count.toLocaleString("pt-BR")}
                    </span>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <RatingStars rating={product.rating} count={product.review_count} />
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <div className="text-sm">{product.seller_name || "-"}</div>
                    <div className="text-xs text-zinc-500">
                      {product.seller_location || ""}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <CategoryBadge category={product.category} />
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm">
                    {product.related_artist || product.related_event || (
                      <span className="text-zinc-500">-</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <a
                      href={product.product_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-1.5 rounded hover:bg-zinc-700 transition-colors inline-flex"
                    >
                      <ExternalLink className="w-4 h-4 text-zinc-400" />
                    </a>
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
            {total} produtos encontrados
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
