"use client";

import { useState } from "react";
import { triggerScraping } from "@/lib/api";
import { RefreshCw, CheckCircle, AlertCircle } from "lucide-react";

export default function ScrapeButton({ onComplete }: { onComplete?: () => void }) {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [isError, setIsError] = useState(false);

  const handleScrape = async () => {
    setLoading(true);
    setMessage(null);
    setIsError(false);
    try {
      const result = await triggerScraping();
      setMessage(result.message || "Scraping concluído!");
      setIsError(false);
      // Reload page data after successful scraping
      if (onComplete) {
        onComplete();
      } else {
        setTimeout(() => window.location.reload(), 2000);
      }
      setTimeout(() => setMessage(null), 8000);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Erro desconhecido";
      if (errorMsg.includes("timeout") || errorMsg.includes("ECONNABORTED")) {
        setMessage("Timeout - o scraping pode estar demorando. Tente novamente em 1 minuto.");
      } else if (errorMsg.includes("Network Error")) {
        setMessage("Erro de rede - verifique se o backend está online.");
      } else {
        setMessage("Erro ao executar scraping. Tente novamente.");
      }
      setIsError(true);
      setTimeout(() => setMessage(null), 8000);
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
        {loading ? "Buscando eventos..." : "Buscar Novos Eventos"}
      </button>
      {message && (
        <div className={`flex items-center gap-1.5 text-sm ${isError ? "text-red-400" : "text-green-400"}`}>
          {isError ? <AlertCircle className="w-4 h-4" /> : <CheckCircle className="w-4 h-4" />}
          <span>{message}</span>
        </div>
      )}
    </div>
  );
}
