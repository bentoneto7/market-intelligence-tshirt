import EventForecast from "@/components/EventForecast";
import SalesProjection from "@/components/SalesProjection";

export default function ProjecoesPage() {
  return (
    <main className="max-w-[1400px] mx-auto px-6 py-6 space-y-10">
      <section>
        <div className="mb-6">
          <h2 className="text-2xl font-bold">Projeção de Vendas de Camisetas por Show</h2>
          <p className="text-sm text-zinc-400 mt-1">
            Quantas camisetas produzir, preço de venda e seu faturamento estimado na Shopee por evento
          </p>
        </div>
        <EventForecast />
      </section>

      <div className="border-t border-zinc-800" />

      <section>
        <div className="mb-6">
          <h2 className="text-2xl font-bold">Inteligência de Mercado: Camisetas na Shopee</h2>
          <p className="text-sm text-zinc-400 mt-1">
            Análise de concorrentes, preços praticados, margens e oportunidade de faturamento por artista
          </p>
        </div>
        <SalesProjection />
      </section>
    </main>
  );
}
