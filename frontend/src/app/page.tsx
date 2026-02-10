import StatsCards from "@/components/StatsCards";
import EventsTable from "@/components/EventsTable";
import RankingPanel from "@/components/RankingPanel";
import ProductionTimeline from "@/components/ProductionTimeline";

export default function Home() {
  return (
    <main className="max-w-[1400px] mx-auto px-6 py-6 space-y-6">
      <StatsCards />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <EventsTable />
        </div>
        <div className="space-y-6">
          <RankingPanel />
          <ProductionTimeline />
        </div>
      </div>
    </main>
  );
}
