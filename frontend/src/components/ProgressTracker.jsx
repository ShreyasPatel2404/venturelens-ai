// frontend/src/components/ProgressTracker.jsx
import { useEffect, useState } from "react";
import { openProgressSocket } from "../api/analyze";

const STAGE_META = [
  { key: "company_info",    label: "Company Research",    icon: "🔍" },
  { key: "market_analysis", label: "Market Analysis",     icon: "📊" },
  { key: "financial_model", label: "Financial Modeling",  icon: "💹" },
  { key: "risk_assessment", label: "Risk Assessment",     icon: "⚠️" },
  { key: "investor_memo",   label: "Investor Memo",       icon: "📝" },
  { key: "report_result",   label: "Report Generation",   icon: "📄" },
  { key: "score_card_raw",  label: "Final Scoring",       icon: "🎯" },
];

const statusStyles = {
  waiting: "text-gray-500 border-gray-700 bg-gray-900",
  running: "text-amber-400 border-amber-400 bg-amber-950 shadow-amber-400/20 shadow-lg animate-pulse",
  done:    "text-emerald-400 border-emerald-500 bg-emerald-950",
  error:   "text-red-400 border-red-500 bg-red-950",
};

const connectorStyles = {
  waiting: "bg-gray-700",
  running: "bg-amber-400",
  done:    "bg-emerald-500",
  error:   "bg-red-500",
};

/**
 * Props:
 *   sessionId  — string UUID, used to open WebSocket
 *   onReady    — callback() fired once WS is open → caller should start HTTP /analyze
 *   onResult   — callback(resultData) when type==="result"
 *   onError    — callback(message) when type==="error"
 */
export default function ProgressTracker({ sessionId, onReady, onResult, onError }) {
  const [stages, setStages] = useState(() =>
    STAGE_META.map((s) => ({ ...s, status: "waiting", message: "" }))
  );

  useEffect(() => {
    if (!sessionId) return;

    const ws = openProgressSocket(sessionId);

    // ── KEY FIX: only signal "ready" once the socket is actually open ──────────
    ws.onopen = () => {
      onReady?.();
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);

        if (msg.type === "progress") {
          setStages((prev) =>
            prev.map((s) =>
              s.key === msg.stage
                ? { ...s, status: msg.status, message: msg.message }
                : s
            )
          );
        } else if (msg.type === "result") {
          onResult?.(msg.data);
        } else if (msg.type === "error") {
          onError?.(msg.message);
        }
      } catch (e) {
        console.error("WS message parse error:", e);
      }
    };

    ws.onerror = (e) => {
      console.error("WebSocket error:", e);
      onError?.("WebSocket connection failed. Check that the backend is running on port 8000.");
    };

    ws.onclose = (e) => {
      // Code 1000 = normal close (pipeline finished). Anything else = unexpected.
      if (e.code !== 1000 && e.code !== 1001) {
        console.warn("WebSocket closed unexpectedly:", e.code, e.reason);
      }
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
        ws.close(1000, "component unmounted");
      }
    };
  }, [sessionId]);

  const doneCount = stages.filter((s) => s.status === "done").length;
  const progress  = Math.round((doneCount / stages.length) * 100);

  return (
    <div className="w-full max-w-lg mx-auto">
      {/* Progress bar */}
      <div className="mb-8">
        <div className="flex justify-between text-xs text-gray-400 mb-2 font-mono">
          <span>ANALYSIS PROGRESS</span>
          <span>{progress}%</span>
        </div>
        <div className="h-1 bg-gray-800 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-amber-500 to-amber-300 rounded-full transition-all duration-700"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Stage stepper */}
      <div className="space-y-0">
        {stages.map((stage, idx) => (
          <div key={stage.key} className="flex gap-4">
            {/* Left: icon + connector line */}
            <div className="flex flex-col items-center">
              <div
                className={`w-10 h-10 rounded-full border flex items-center justify-center text-sm flex-shrink-0 transition-all duration-500 ${statusStyles[stage.status]}`}
              >
                {stage.status === "done" ? (
                  <svg className="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                  </svg>
                ) : stage.status === "running" ? (
                  <div className="w-3 h-3 rounded-full bg-amber-400 animate-ping" />
                ) : (
                  <span>{stage.icon}</span>
                )}
              </div>
              {idx < stages.length - 1 && (
                <div className={`w-0.5 h-8 transition-all duration-700 ${connectorStyles[stage.status]}`} />
              )}
            </div>

            {/* Right: label + message */}
            <div className="pb-8 pt-2 min-w-0">
              <p className={`text-sm font-semibold tracking-wide transition-colors duration-300 ${
                stage.status === "done"    ? "text-emerald-400" :
                stage.status === "running" ? "text-amber-300" :
                stage.status === "error"   ? "text-red-400" :
                "text-gray-500"
              }`}>
                {stage.label}
              </p>
              {stage.message && (
                <p className="text-xs text-gray-500 mt-0.5 truncate">{stage.message}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
