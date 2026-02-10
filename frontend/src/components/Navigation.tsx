"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Shirt, Calendar, ShoppingBag, TrendingUp } from "lucide-react";
import ScrapeButton from "./ScrapeButton";

const tabs = [
  { href: "/", label: "Eventos", icon: Calendar },
  { href: "/marketplace", label: "Marketplace", icon: ShoppingBag },
  { href: "/projecoes", label: "Projeções", icon: TrendingUp },
];

export default function Navigation() {
  const pathname = usePathname();

  return (
    <header className="border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-[1400px] mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <Link href="/" className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-blue-600">
              <Shirt className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-xl font-bold">Market Intelligence</h1>
              <p className="text-xs text-zinc-500">Estamparia de Camisetas</p>
            </div>
          </Link>

          <nav className="flex items-center gap-1 ml-4">
            {tabs.map((tab) => {
              const isActive = pathname === tab.href;
              return (
                <Link
                  key={tab.href}
                  href={tab.href}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-zinc-800 text-white"
                      : "text-zinc-400 hover:text-white hover:bg-zinc-800/50"
                  }`}
                >
                  <tab.icon className="w-4 h-4" />
                  {tab.label}
                </Link>
              );
            })}
          </nav>
        </div>

        <ScrapeButton />
      </div>
    </header>
  );
}
