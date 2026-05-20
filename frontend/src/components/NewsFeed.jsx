// frontend/src/components/NewsFeed.jsx
import { useState, useEffect } from "react";

const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

export default function NewsFeed({ startupName }) {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState("");

  useEffect(() => {
    if (!startupName) return;
    setLoading(true);
    fetch(`${API_BASE}/news/${encodeURIComponent(startupName)}`)
      .then(r => r.json())
      .then(data => { setArticles(data.articles || []); setLoading(false); })
      .catch(e  => { setError(e.message); setLoading(false); });
  }, [startupName]);

  return (
    <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
      <p className="text-xs text-amber-400 tracking-widest mb-4">LATEST NEWS</p>

      {loading && (
        <div className="flex items-center gap-2 text-gray-500 text-xs py-4">
          <div className="w-4 h-4 rounded-full border-2 border-amber-400 border-t-transparent animate-spin" />
          Fetching news...
        </div>
      )}

      {error && (
        <p className="text-gray-600 text-xs py-4">
          News unavailable (SERP_API_KEY not configured).
        </p>
      )}

      {!loading && articles.length === 0 && !error && (
        <p className="text-gray-600 text-xs py-4">
          No recent news found. Set SERP_API_KEY in .env to enable live news.
        </p>
      )}

      <div className="space-y-3">
        {articles.map((a, i) => (
          <a key={i} href={a.url} target="_blank" rel="noopener noreferrer"
            className="block group">
            <div className="border border-gray-800 hover:border-amber-400/30 rounded-lg p-3 transition-all">
              <p className="text-white text-xs font-semibold group-hover:text-amber-400 transition-colors line-clamp-2 mb-1">
                {a.title}
              </p>
              <div className="flex items-center gap-2 text-gray-600 text-xs">
                <span>{a.source}</span>
                {a.date && <><span>·</span><span>{a.date}</span></>}
              </div>
              {a.snippet && (
                <p className="text-gray-500 text-xs mt-1 line-clamp-2">{a.snippet}</p>
              )}
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}