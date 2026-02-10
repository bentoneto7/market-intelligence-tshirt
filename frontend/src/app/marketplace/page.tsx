import MarketplaceStatsCards from "@/components/MarketplaceStats";
import MarketplaceTable from "@/components/MarketplaceTable";
import TopArtistsPanel from "@/components/TopArtistsPanel";
import TopSellersPanel from "@/components/TopSellersPanel";
import EventProductFilter from "@/components/EventProductFilter";

export default function MarketplacePage() {
  return (
    <main className="max-w-[1400px] mx-auto px-6 py-6 space-y-6">
      <MarketplaceStatsCards />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <MarketplaceTable />
        </div>
        <div className="space-y-6">
          <EventProductFilter />
          <TopArtistsPanel />
          <TopSellersPanel />
        </div>
      </div>
    </main>
  );
}
