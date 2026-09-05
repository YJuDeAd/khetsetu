import React from "react";
import { Sprout, ShieldCheck, Truck, Activity } from "lucide-react";

export const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-between">
      <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sprout className="w-8 h-8 text-emerald-600" />
          <div>
            <h1 className="text-xl font-bold text-slate-800">KhetSetu</h1>
            <p className="text-xs text-slate-500">Direct Farm-to-Buyer Marketplace</p>
          </div>
        </div>
        <div className="flex items-center gap-2 px-3 py-1 bg-emerald-50 text-emerald-700 text-xs font-semibold rounded-full border border-emerald-200">
          <Activity className="w-3.5 h-3.5 animate-pulse" />
          <span>Backend Ready (FastAPI + WebSockets)</span>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-12 text-center">
        <div className="inline-flex p-3 bg-emerald-100 rounded-2xl text-emerald-700 mb-6">
          <Sprout className="w-10 h-10" />
        </div>
        <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight sm:text-4xl">
          FPO & Bulk Buyer Web Portal
        </h2>
        <p className="mt-4 text-base text-slate-600 max-w-2xl mx-auto">
          Eliminating intermediaries through direct produce listing, transparent dynamic price discovery, pooled cold-chain logistics, and an escrow-protected transaction cycle.
        </p>

        <div className="mt-10 grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <ShieldCheck className="w-6 h-6 text-emerald-600 mb-3" />
            <h3 className="font-semibold text-slate-800 mb-1">Escrow Protection</h3>
            <p className="text-sm text-slate-500">
              Guaranteed payment locking and verification before payout releases.
            </p>
          </div>
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <Truck className="w-6 h-6 text-emerald-600 mb-3" />
            <h3 className="font-semibold text-slate-800 mb-1">Pooled Routing</h3>
            <p className="text-sm text-slate-500">
              Cold-chain vehicle routing optimization to cut transit time and food spoilage.
            </p>
          </div>
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <Activity className="w-6 h-6 text-emerald-600 mb-3" />
            <h3 className="font-semibold text-slate-800 mb-1">Live Mandi Discovery</h3>
            <p className="text-sm text-slate-500">
              Resilient dynamic pricing with fail-safe historical averages.
            </p>
          </div>
        </div>
      </main>

      <footer className="border-t border-slate-200 bg-white py-4 px-6 text-center text-xs text-slate-500">
        SIH 2026 Problem Statement 26033 • KhetSetu Marketplace
      </footer>
    </div>
  );
};

export default App;
