// frontend/src/components/StickyNotes.jsx
// Per-section analyst notes, saved to localStorage keyed by analysisId + section.
import { useState, useEffect } from "react";

function getKey(analysisId, section) {
  return `vl_note_${analysisId}_${section}`;
}

/**
 * Props:
 *   analysisId — string/number key for this analysis
 *   section    — section name e.g. "executive_summary"
 *   label      — human readable label
 */
export default function StickyNote({ analysisId, section, label = "Section" }) {
  const key = getKey(analysisId || "draft", section);
  const [open, setOpen]   = useState(false);
  const [text, setText]   = useState(() => localStorage.getItem(key) || "");
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    localStorage.setItem(key, text);
    setSaved(true);
    setTimeout(() => setSaved(false), 1500);
  };

  const handleClear = () => {
    localStorage.removeItem(key);
    setText("");
  };

  const hasNote = text.trim().length > 0;

  return (
    <div className="relative inline-block">
      {/* Note trigger button */}
      <button
        onClick={() => setOpen(!open)}
        title={`${hasNote ? "Edit" : "Add"} note for ${label}`}
        className={`text-xs px-2 py-0.5 rounded border transition-all ${
          hasNote
            ? "border-amber-400/60 text-amber-400 bg-amber-950/30"
            : "border-gray-700 text-gray-600 hover:border-gray-500 hover:text-gray-400"
        }`}
      >
        {hasNote ? "📝 Note" : "+ Note"}
      </button>

      {/* Note popover */}
      {open && (
        <div className="absolute left-0 top-8 z-30 w-72 bg-gray-900 border border-gray-700 rounded-xl shadow-2xl p-4"
             style={{ fontFamily: "'DM Mono', monospace" }}>
          <div className="flex items-center justify-between mb-2">
            <p className="text-xs text-amber-400 tracking-widest truncate">{label}</p>
            <button onClick={() => setOpen(false)} className="text-gray-600 hover:text-white text-xs">✕</button>
          </div>
          <textarea
            value={text}
            onChange={e => setText(e.target.value)}
            placeholder="Add analyst notes..."
            rows={4}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-xs placeholder-gray-600 focus:outline-none focus:border-amber-400 resize-none"
          />
          <div className="flex gap-2 mt-2">
            <button onClick={handleSave}
              className="flex-1 text-xs bg-amber-400 hover:bg-amber-300 text-black font-bold py-1.5 rounded transition-all">
              {saved ? "✓ Saved" : "Save"}
            </button>
            {hasNote && (
              <button onClick={handleClear}
                className="text-xs border border-gray-700 hover:border-red-500 text-gray-500 hover:text-red-400 px-3 py-1.5 rounded transition-all">
                Clear
              </button>
            )}
          </div>
          <p className="text-gray-700 text-xs mt-2">Saved locally in your browser.</p>
        </div>
      )}
    </div>
  );
}