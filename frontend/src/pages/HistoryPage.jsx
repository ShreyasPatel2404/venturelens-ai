// frontend/src/pages/HistoryPage.jsx
// Shows two analyses side-by-side with radar charts for comparison.
import { useState, useEffect } from "react";
import RadarChart from "../components/RadarChart";
import ReportViewer from "../components/ReportViewer";

const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

const VERDICT_CONFIG = {
  "STRONG BUY": { color: "text-emerald-400", bg: "bg-emerald-950 border-emerald-500" },
  "BUY":        { color: "text-emerald-300", bg: "bg-emerald-950 border-emerald-600" },
  "PROMISING":  { color: "text-amber-300",   bg: "bg-amber-950 border-amber-500" },
  "HOLD":       { color: "text-yellow-400",  bg: "bg-yellow-950 border-yellow-600" },
  "NEUTRAL":    { color: "text-gray-300",    bg: "bg-gray-800 border-gray-600" },
  "RISKY":      { color: "text-orange-400",  bg: "bg-orange-950 border-orange-500" },
  "PASS":       { color: "text-red-400",     bg: "bg-red-950 border-red-500" },
};

const SCORE_LABELS = {
  market_opportunity:      "Market",
  team_strength:           "Team",
  product_differentiation: "Product",
  traction:                "Traction",
  financial_health:        "Finance",
};

const RADAR_COLORS = ["#F59E0B", "#34D399"]; // amber, emerald

function ScoreRow({ label, a, b }) {
  const winner = a > b ? "a" : b > a ? "b" : "tie";
  return (
    <div className="grid grid-cols-7 items-center text-xs py-1.5 border-b border-gray-800">
      <div className={`col-span-2 text-right pr-3 font-mono ${winner === "a" ? "text-white font-bold" : "text-gray-500"}`}>{a}</div>
      <div className="col-span-3 text-center text-gray-500 truncate px-1">{label}</div>
      <div className={`col-span-2 text-left pl-3 font-mono ${winner === "b" ? "text-white font-bold" : "text-gray-500"}`}>{b}</div>
    </div>
  );
}

function AnalysisCard({ data, color, onViewReport }) {
  if (!data) return (
    <div className="flex items-center justify-center h-48 border border-dashed border-gray-700 rounded-xl text-gray-600 text-sm">
      Select analysis from sidebar
    </div>
  );

  const result = data.result || data;
  const vc = VERDICT_CONFIG[result.verdict] || VERDICT_CONFIG["NEUTRAL"];

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-xl font-bold text-white">{result.startup_name}</h3>
          <p className="text-gray-500 text-xs mt-0.5">{data.industry} · {data.stage}</p>
        </div>
        <div className={`px-3 py-1 rounded border text-xs font-bold ${vc.bg} ${vc.color}`}>
          {result.verdict}
        </div>
      </div>

      {/* Overall score */}
      <div className="text-center py-3 bg-gray-900 rounded-xl border border-gray-800">
        <div className="text-5xl font-bold font-mono" style={{ color }}>{result.overall_score}</div>
        <div className="text-gray-500 text-xs tracking-widest mt-1">OVERALL SCORE</div>
      </div>

      {/* Radar */}
      <RadarChart scores={result.scores || {}} color={color} size="md" />

      {/* View report button */}
      <button onClick={() => onViewReport(result.startup_name)}
        className="w-full border py-2 rounded-lg text-xs tracking-widest transition-all"
        style={{ borderColor: color, color }}>
        📄 VIEW FULL REPORT
      </button>
    </div>
  );
}

/**
 * Props:
 *   compareIds — array of 1 or 2 analysis IDs to show side by side
 *   onBack     — go back to main page
 */
export default function HistoryPage({ compareIds = [], onBack }) {
  const [analyses, setAnalyses] = useState({});
  const [loading, setLoading]   = useState(false);
  const [reportFor, setReportFor] = useState(null);

  useEffect(() => {
    if (!compareIds.length) return;
    setLoading(true);
    Promise.all(
      compareIds.map(id =>
        fetch(`${API_BASE}/history/${id}`).then(r => r.json())
      )
    ).then(results => {
      const map = {};
      results.forEach((r, i) => { map[compareIds[i]] = r; });
      setAnalyses(map);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [compareIds.join(",")]);

  const items = compareIds.map(id => analyses[id]).filter(Boolean);
  const [a, b] = items;

  const scoreKeys = Object.keys(SCORE_LABELS);

  return (
    <div className="min-h-screen bg-gray-950 text-white" style={{ fontFamily: "'DM Mono', monospace" }}>
      <header className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded bg-amber-400 flex items-center justify-center">
            <span className="text-black font-bold text-sm">V</span>
          </div>
          <span className="text-white font-semibold tracking-widest text-sm">VENTURELENS AI</span>
          <span className="text-gray-600 text-xs ml-2">/ COMPARISON</span>
        </div>
        <button onClick={onBack}
          className="text-xs text-gray-400 hover:text-white border border-gray-700 hover:border-gray-500 px-3 py-1.5 rounded transition-all">
          ← Back
        </button>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-10">
        {loading && (
          <div className="flex items-center justify-center h-48">
            <div className="w-8 h-8 rounded-full border-2 border-amber-400 border-t-transparent animate-spin" />
          </div>
        )}

        {!loading && items.length === 0 && (
          <div className="text-center py-20">
            <p className="text-gray-500">No analyses selected for comparison.</p>
            <button onClick={onBack} className="mt-4 text-amber-400 text-sm hover:underline">
              ← Go back and select analyses
            </button>
          </div>
        )}

        {!loading && items.length > 0 && (
          <div className="space-y-8">
            <div className="text-center">
              <p className="text-xs text-amber-400 tracking-[0.3em] mb-2">SIDE-BY-SIDE COMPARISON</p>
              <h2 className="text-2xl font-bold text-white">
                {items.map(i => (i.result || i).startup_name).join(" vs ")}
              </h2>
            </div>

            {/* Side-by-side cards */}
            <div className="grid grid-cols-2 gap-6">
              {items.map((item, idx) => (
                <AnalysisCard
                  key={compareIds[idx]}
                  data={item}
                  color={RADAR_COLORS[idx]}
                  onViewReport={setReportFor}
                />
              ))}
            </div>

            {/* Score comparison table */}
            {items.length === 2 && (
              <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
                <p className="text-xs text-amber-400 tracking-widest mb-4 text-center">SCORE BREAKDOWN</p>

                {/* Column headers */}
                <div className="grid grid-cols-7 text-xs text-gray-500 mb-2 pb-2 border-b border-gray-700">
                  <div className="col-span-2 text-right pr-3" style={{ color: RADAR_COLORS[0] }}>
                    {(a.result || a).startup_name}
                  </div>
                  <div className="col-span-3 text-center">DIMENSION</div>
                  <div className="col-span-2 text-left pl-3" style={{ color: RADAR_COLORS[1] }}>
                    {(b.result || b).startup_name}
                  </div>
                </div>

                {/* Overall */}
                <ScoreRow
                  label="OVERALL"
                  a={(a.result || a).overall_score}
                  b={(b.result || b).overall_score}
                />

                {/* Dimension rows */}
                {scoreKeys.map(key => (
                  <ScoreRow
                    key={key}
                    label={SCORE_LABELS[key]}
                    a={(a.result || a).scores?.[key] ?? 0}
                    b={(b.result || b).scores?.[key] ?? 0}
                  />
                ))}

                <p className="text-xs text-gray-600 text-center mt-3">Bold = higher score</p>
              </div>
            )}

            {/* Single analysis radar if only one selected */}
            {items.length === 1 && (
              <div className="text-center text-gray-500 text-sm">
                Select a second analysis from the sidebar to compare.
              </div>
            )}
          </div>
        )}
      </main>

      {reportFor && (
        <ReportViewer startupName={reportFor} onClose={() => setReportFor(null)} />
      )}
    </div>
  );
}