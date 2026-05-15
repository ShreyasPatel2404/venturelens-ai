// frontend/src/components/ReportViewer.jsx
// Full-screen modal that fetches + renders the Markdown report.
// Includes: copy to clipboard, PDF print export, keyboard close (Esc).
import { useEffect, useState, useCallback } from "react";
import ReactMarkdown from "react-markdown";

const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

export default function ReportViewer({ startupName, onClose }) {
  const [markdown, setMarkdown] = useState("");
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState("");
  const [copied, setCopied]     = useState(false);

  // Fetch report from backend
  useEffect(() => {
    if (!startupName) return;
    setLoading(true);
    setError("");

    fetch(`${API_BASE}/report/${encodeURIComponent(startupName)}`)
      .then((r) => {
        if (!r.ok) throw new Error(`Report not found (${r.status})`);
        return r.text();
      })
      .then((text) => { setMarkdown(text); setLoading(false); })
      .catch((e)  => { setError(e.message); setLoading(false); });
  }, [startupName]);

  // Close on Escape
  useEffect(() => {
    const handler = (e) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onClose]);

  // Lock body scroll while modal is open
  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = ""; };
  }, []);

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(markdown).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }, [markdown]);

  const handlePrint = () => {
    window.print();
  };

  return (
    // Backdrop
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-black/80 backdrop-blur-sm pt-8 pb-8 px-4"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      {/* Modal panel */}
      <div className="relative w-full max-w-4xl max-h-[90vh] flex flex-col bg-gray-950 border border-gray-700 rounded-2xl shadow-2xl overflow-hidden"
           id="report-modal">

        {/* ── Toolbar ── */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-800 flex-shrink-0 bg-gray-900">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-amber-400" />
            <span className="text-xs text-gray-400 tracking-widest font-mono uppercase">
              Full Investment Report — {startupName}
            </span>
          </div>
          <div className="flex items-center gap-2">
            {/* Copy button */}
            <button
              onClick={handleCopy}
              disabled={loading || !!error}
              className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border border-gray-700 hover:border-amber-400 text-gray-400 hover:text-amber-400 transition-all disabled:opacity-40"
            >
              {copied ? (
                <><span>✓</span> Copied</>
              ) : (
                <><span>⎘</span> Copy</>
              )}
            </button>
            {/* PDF button */}
            <button
              onClick={handlePrint}
              disabled={loading || !!error}
              className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border border-gray-700 hover:border-emerald-400 text-gray-400 hover:text-emerald-400 transition-all disabled:opacity-40"
            >
              ↓ PDF
            </button>
            {/* Close */}
            <button
              onClick={onClose}
              className="ml-2 w-7 h-7 flex items-center justify-center rounded-lg border border-gray-700 hover:border-red-500 text-gray-400 hover:text-red-400 transition-all text-sm"
            >
              ✕
            </button>
          </div>
        </div>

        {/* ── Content ── */}
        <div className="flex-1 overflow-y-auto px-8 py-8 report-content">
          {loading && (
            <div className="flex flex-col items-center justify-center h-48 gap-4">
              <div className="w-8 h-8 rounded-full border-2 border-amber-400 border-t-transparent animate-spin" />
              <p className="text-gray-500 text-sm font-mono">Loading report...</p>
            </div>
          )}

          {error && (
            <div className="flex flex-col items-center justify-center h-48 gap-3">
              <p className="text-red-400 text-2xl">⚠</p>
              <p className="text-red-400 text-sm">{error}</p>
              <p className="text-gray-500 text-xs max-w-sm text-center">
                The report file is saved in <code className="text-amber-400">backend/outputs/</code> after analysis completes.
              </p>
            </div>
          )}

          {!loading && !error && markdown && (
            <div className="prose-report">
              <ReactMarkdown
                components={{
                  h1: ({ children }) => (
                    <h1 className="text-2xl font-bold text-white mb-6 pb-3 border-b border-amber-400/30 font-mono tracking-wide">
                      {children}
                    </h1>
                  ),
                  h2: ({ children }) => (
                    <h2 className="text-lg font-bold text-amber-400 mt-8 mb-3 tracking-widest uppercase text-xs">
                      ── {children}
                    </h2>
                  ),
                  h3: ({ children }) => (
                    <h3 className="text-base font-semibold text-gray-200 mt-5 mb-2">
                      {children}
                    </h3>
                  ),
                  p: ({ children }) => (
                    <p className="text-gray-300 text-sm leading-7 mb-4">{children}</p>
                  ),
                  ul: ({ children }) => (
                    <ul className="space-y-1.5 mb-4 ml-4">{children}</ul>
                  ),
                  li: ({ children }) => (
                    <li className="text-gray-300 text-sm flex gap-2">
                      <span className="text-amber-500 flex-shrink-0 mt-1">▸</span>
                      <span>{children}</span>
                    </li>
                  ),
                  strong: ({ children }) => (
                    <strong className="text-white font-semibold">{children}</strong>
                  ),
                  em: ({ children }) => (
                    <em className="text-amber-300 not-italic">{children}</em>
                  ),
                  blockquote: ({ children }) => (
                    <blockquote className="border-l-2 border-amber-400 pl-4 my-4 text-gray-400 italic text-sm">
                      {children}
                    </blockquote>
                  ),
                  code: ({ children }) => (
                    <code className="bg-gray-800 text-amber-300 px-1.5 py-0.5 rounded text-xs font-mono">
                      {children}
                    </code>
                  ),
                  hr: () => (
                    <hr className="border-gray-800 my-6" />
                  ),
                  table: ({ children }) => (
                    <div className="overflow-x-auto my-4">
                      <table className="w-full text-sm border-collapse">{children}</table>
                    </div>
                  ),
                  th: ({ children }) => (
                    <th className="text-left text-xs text-amber-400 tracking-widest uppercase px-3 py-2 border-b border-gray-700">
                      {children}
                    </th>
                  ),
                  td: ({ children }) => (
                    <td className="text-gray-300 text-xs px-3 py-2 border-b border-gray-800">
                      {children}
                    </td>
                  ),
                }}
              >
                {markdown}
              </ReactMarkdown>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}