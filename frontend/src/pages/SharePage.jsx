// frontend/src/pages/SharePage.jsx
// Read-only view of a shared analysis — loaded via /share/:token URL
import { useState, useEffect } from "react";
import RadarChart   from "../components/RadarChart";
import ReportViewer from "../components/ReportViewer";

const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

const VERDICT_CONFIG = {
  "STRONG BUY":{ color:"text-emerald-400", bg:"bg-emerald-950 border-emerald-500" },
  "BUY":       { color:"text-emerald-300", bg:"bg-emerald-950 border-emerald-600" },
  "PROMISING": { color:"text-amber-300",   bg:"bg-amber-950 border-amber-500" },
  "HOLD":      { color:"text-yellow-400",  bg:"bg-yellow-950 border-yellow-600" },
  "NEUTRAL":   { color:"text-gray-300",    bg:"bg-gray-800 border-gray-600" },
  "RISKY":     { color:"text-orange-400",  bg:"bg-orange-950 border-orange-500" },
  "PASS":      { color:"text-red-400",     bg:"bg-red-950 border-red-500" },
};

const SCORE_LABELS = {
  market_opportunity:"Market Opportunity", team_strength:"Team Strength",
  product_differentiation:"Product Differentiation", traction:"Traction", financial_health:"Financial Health",
};

export default function SharePage({ token }) {
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState("");
  const [showReport, setShowReport] = useState(false);

  useEffect(() => {
    if (!token) return;
    fetch(`${API_BASE}/share/${token}`)
      .then(r => { if (!r.ok) throw new Error("Share link not found or expired."); return r.json(); })
      .then(d  => { setData(d); setLoading(false); })
      .catch(e => { setError(e.message); setLoading(false); });
  }, [token]);

  if (loading) return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center" style={{fontFamily:"'DM Mono',monospace"}}>
      <div className="text-center">
        <div className="w-8 h-8 rounded-full border-2 border-amber-400 border-t-transparent animate-spin mx-auto mb-4"/>
        <p className="text-gray-500 text-sm">Loading shared report...</p>
      </div>
    </div>
  );

  if (error) return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center" style={{fontFamily:"'DM Mono',monospace"}}>
      <div className="text-center">
        <p className="text-red-400 text-xl mb-2">⚠</p>
        <p className="text-gray-400">{error}</p>
      </div>
    </div>
  );

  const result = data?.result || {};
  const vc = VERDICT_CONFIG[result.verdict] || VERDICT_CONFIG["NEUTRAL"];

  return (
    <div className="min-h-screen bg-gray-950 text-white" style={{fontFamily:"'DM Mono',monospace"}}>
      <header className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded bg-amber-400 flex items-center justify-center">
            <span className="text-black font-bold text-sm">V</span>
          </div>
          <span className="text-white font-semibold tracking-widest text-sm">VENTURELENS AI</span>
          <span className="text-gray-600 text-xs ml-2">/ SHARED REPORT</span>
        </div>
        <span className="text-xs text-gray-600 border border-gray-800 px-3 py-1 rounded">READ ONLY</span>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-12 space-y-6">
        <div className="flex items-start justify-between flex-wrap gap-3">
          <div>
            <p className="text-xs text-amber-400 tracking-[0.3em] mb-1">SHARED ANALYSIS</p>
            <h2 className="text-3xl font-bold text-white">{result.startup_name}</h2>
            <p className="text-gray-400 text-sm mt-1">{data?.industry} · {data?.stage}</p>
          </div>
          <div className={`px-4 py-2 rounded-lg border text-sm font-bold tracking-widest ${vc.bg} ${vc.color}`}>
            {result.verdict}
          </div>
        </div>

        <div className="grid grid-cols-5 gap-6 bg-gray-900 rounded-xl p-6 border border-gray-800">
          <div className="col-span-2 text-center">
            <div className="text-6xl font-bold font-mono text-amber-400">{result.overall_score}</div>
            <p className="text-xs text-gray-500 mt-2 tracking-widest">OVERALL SCORE</p>
          </div>
          <div className="col-span-3 space-y-3 flex flex-col justify-center">
            {Object.entries(result.scores||{}).map(([k,v]) => (
              <div key={k} className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-gray-400">{SCORE_LABELS[k]||k}</span>
                  <span className="text-white font-mono">{v}</span>
                </div>
                <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
                  <div className="h-full bg-amber-400 rounded-full" style={{width:`${v}%`}}/>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
          <RadarChart scores={result.scores||{}} color="#F59E0B" size="md"/>
        </div>

        <div className="bg-gray-900 rounded-xl p-5 border border-gray-800">
          <p className="text-xs text-gray-400 tracking-widest mb-3">EXECUTIVE SUMMARY</p>
          <p className="text-gray-200 text-sm leading-relaxed">{result.summary}</p>
        </div>

        <button onClick={() => setShowReport(true)}
          className="w-full bg-amber-400 hover:bg-amber-300 text-black font-bold py-3 rounded-lg text-sm tracking-widest transition-all">
          📄 VIEW FULL REPORT
        </button>

        <p className="text-center text-gray-700 text-xs">
          Generated by VentureLens AI · Not financial advice
        </p>
      </main>

      {showReport && (
        <ReportViewer startupName={result.startup_name} onClose={() => setShowReport(false)}/>
      )}
    </div>
  );
}