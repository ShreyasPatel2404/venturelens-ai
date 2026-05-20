// frontend/src/components/HistorySidebar.jsx — DAY 7 (skeletons + mobile overlay)
import { useEffect, useState } from "react";
import { HistoryItemSkeleton } from "./Skeleton";

const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

const VERDICT_DOT = {
  "STRONG BUY":"bg-emerald-400","BUY":"bg-emerald-300","PROMISING":"bg-amber-400",
  "HOLD":"bg-yellow-400","NEUTRAL":"bg-gray-400","RISKY":"bg-orange-400","PASS":"bg-red-400",
};

function timeAgo(iso) {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff/60000);
  if (mins<1)  return "just now";
  if (mins<60) return `${mins}m ago`;
  const hrs = Math.floor(mins/60);
  if (hrs<24)  return `${hrs}h ago`;
  return `${Math.floor(hrs/24)}d ago`;
}

export default function HistorySidebar({ onSelect, selectedId, onClose, compareIds=[], onToggleCompare }) {
  const [items,setItems]     = useState([]);
  const [loading,setLoading] = useState(true);

  const fetchHistory = () => {
    setLoading(true);
    fetch(`${API_BASE}/history`)
      .then(r=>r.json())
      .then(d=>{setItems(d);setLoading(false);})
      .catch(()=>setLoading(false));
  };

  useEffect(()=>{fetchHistory();},[]);

  return (
    <>
      {/* Mobile backdrop */}
      <div className="fixed inset-0 bg-black/60 z-30 md:hidden" onClick={onClose}/>

      <aside className="fixed left-0 top-0 h-full w-72 bg-gray-950 border-r border-gray-800 z-40 flex flex-col"
             style={{fontFamily:"'DM Mono',monospace"}}>

        <div className="flex items-center justify-between px-4 py-4 border-b border-gray-800">
          <div>
            <p className="text-xs text-amber-400 tracking-widest">HISTORY</p>
            <p className="text-white text-sm font-semibold mt-0.5">{items.length} analyses</p>
          </div>
          <div className="flex gap-2">
            <button onClick={fetchHistory} className="text-gray-500 hover:text-amber-400 text-xs border border-gray-700 hover:border-amber-400 px-2 py-1 rounded transition-colors">↻</button>
            <button onClick={onClose}      className="text-gray-500 hover:text-white text-xs border border-gray-700 hover:border-gray-500 px-2 py-1 rounded transition-colors">✕</button>
          </div>
        </div>

        {compareIds.length>0&&(
          <div className="px-4 py-2 bg-amber-950 border-b border-amber-800">
            <p className="text-xs text-amber-400">
              {compareIds.length===1?"Select one more to compare →":`${compareIds.length} selected`}
            </p>
          </div>
        )}

        <div className="flex-1 overflow-y-auto">
          {loading&&[...Array(5)].map((_,i)=><HistoryItemSkeleton key={i}/>)}

          {!loading&&items.length===0&&(
            <div className="px-4 py-8 text-center">
              <p className="text-gray-600 text-xs">No analyses yet.</p>
            </div>
          )}

          {!loading&&items.map(item=>{
            const isSelected = item.id===selectedId;
            const isCompare  = compareIds.includes(item.id);
            return (
              <div key={item.id} className={`group border-b border-gray-800/60 transition-all ${isSelected?"bg-amber-950/40":"hover:bg-gray-900"}`}>
                <button onClick={()=>{onSelect(item.id);onClose();}} className="w-full text-left px-4 py-3">
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`w-2 h-2 rounded-full flex-shrink-0 ${VERDICT_DOT[item.verdict]||"bg-gray-500"}`}/>
                        <span className={`text-sm font-semibold truncate ${isSelected?"text-amber-400":"text-white"}`}>{item.startup_name}</span>
                      </div>
                      <div className="flex gap-2 text-xs text-gray-500 ml-4">
                        <span>{item.industry}</span><span>·</span><span>{item.stage}</span>
                      </div>
                    </div>
                    <div className="text-right flex-shrink-0">
                      <div className="text-white font-mono font-bold text-sm">{item.overall_score}</div>
                      <div className="text-gray-600 text-xs">{timeAgo(item.created_at)}</div>
                    </div>
                  </div>
                </button>
                {onToggleCompare&&(
                  <div className="px-4 pb-2">
                    <button onClick={()=>onToggleCompare(item.id)}
                      className={`text-xs px-2 py-0.5 rounded border transition-all ${isCompare?"border-amber-400 text-amber-400 bg-amber-950":"border-gray-700 text-gray-600 hover:border-gray-500 hover:text-gray-400"}`}>
                      {isCompare?"✓ comparing":"+ compare"}
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </aside>
    </>
  );
}