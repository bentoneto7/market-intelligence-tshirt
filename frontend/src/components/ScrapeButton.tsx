"use client";

import { useState } from "react";
import { triggerScraping } from "@/lib/api";
import { RefreshCw } from "lucide-react";

export default function ScrapeButton() {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const handleScrape = async () => {
    setLoading(true);
    setMessage(null);
    try {
      const result = await triggerScraping();
      setMessage(result.message);
      setTimeout(() => setMessage(null), 5000);
    } catch {
      setMessage("Erro ao executar scraping");
      setTimeout(() => setMessage(null), 5000);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center gap-3">
      <button
        onClick={handleScrape}
        disabled={loading}
        className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-lg text-sm font-medium transition-colors"
      >
        <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
        {loading ? "Buscando..." : "Buscar Novos Eventos"}
      </button>
      {message && (
        <span className="text-sm text-zinc-400">{message}</span>
      )}
    </div>
  );
}
