// frontend/src/components/CompetitorTable.jsx
import { useState, useEffect } from "react";

const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

/**
 * Props:
 *   analysisId   — DB id to fetch competitors for
 *   startupName  — name of analyzed startup (for highlight row)
 */
export default function CompetitorTable({ analysisId, startupName }) {
  const [competitors, setCompetitors] = useState([]);
  const [loading, setLoading]         = useState(false);
  const [error, setError]             = useState("");
  const [fetched, setFetched]         = useState(false);

  const fetchCompetitors = async () => {
    if (!analysisId) return;
    setLoading(true); setError("");
    try {
      const res = await fetch(`${API_BASE}/competitors/${analysisId}`);
      if (!res.ok) throw new Error(`Failed (${res.status})`);
      const data = await res.json();
      setCompetitors(data.competitors || []);
      setFetched(true);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const COLS = ["Company", "Founded", "Funding", "Revenue Est.", "Team Size", "Key Differentiator"];

  return (
    <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
      <div className="flex items-center justify-between mb-4">
        <p className="text-xs text-amber-400 tracking-widest">COMPETITOR ANALYSIS</p>
        {!fetched && (
          <button onClick={fetchCompetitors} disabled={loading || !analysisId}
            className="text-xs border border-amber-400/40 hover:border-amber-400 text-amber-400 px-3 py-1.5 rounded-lg transition-all disabled:opacity-40">
            {loading ? "⏳ Loading..." : "⚡ Generate Competitors"}
          </button>
        )}
      </div>

      {error && <p className="text-red-400 text-xs">{error}</p>}

      {!fetched && !loading && (
        <p className="text-gray-600 text-xs text-center py-6">
          Click "Generate Competitors" to run a live competitive analysis.
        </p>
      )}

      {fetched && competitors.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr>
                {COLS.map(c => (
                  <th key={c} className="text-left text-amber-400/70 tracking-widest pb-3 pr-4 font-normal border-b border-gray-800">
                    {c.toUpperCase()}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {competitors.map((c, i) => (
                <tr key={i} className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors">
                  <td className="py-3 pr-4">
                    <a href={c.website} target="_blank" rel="noopener noreferrer"
                       className="text-white hover:text-amber-400 font-semibold transition-colors">
                      {c.name}
                    </a>
                  </td>
                  <td className="py-3 pr-4 text-gray-400">{c.founded}</td>
                  <td className="py-3 pr-4 text-gray-300">{c.funding}</td>
                  <td className="py-3 pr-4 text-gray-300">{c.revenue_est}</td>
                  <td className="py-3 pr-4 text-gray-400">{c.team_size}</td>
                  <td className="py-3 text-gray-400 max-w-xs">{c.key_differentiator}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}