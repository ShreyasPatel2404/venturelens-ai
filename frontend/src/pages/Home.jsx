// frontend/src/pages/Home.jsx — DAY 6 FINAL
import { useState, useRef, useCallback } from "react";
import { analyzeStartup, makeSessionId } from "../api/analyze";
import ProgressTracker  from "../components/ProgressTracker";
import ReportViewer     from "../components/ReportViewer";
import RadarChart       from "../components/RadarChart";
import HistorySidebar   from "../components/HistorySidebar";
import HistoryPage      from "./HistoryPage";
import CompetitorTable  from "../components/CompetitorTable";
import StickyNote       from "../components/StickyNotes";
import NewsFeed         from "../components/NewsFeed";

const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

const INDUSTRIES = ["Fintech","HealthTech","EdTech","SaaS","E-commerce","AI/ML","Logistics","Climate Tech","Cybersecurity","Web3","Other"];
const STAGES = [{value:"idea",label:"Idea"},{value:"pre-seed",label:"Pre-Seed"},{value:"seed",label:"Seed"},{value:"series-a",label:"Series A"},{value:"series-b+",label:"Series B+"}];
const VERDICT_CONFIG = {
  "STRONG BUY":{color:"text-emerald-400",bg:"bg-emerald-950 border-emerald-500",dot:"bg-emerald-400"},
  "BUY":{color:"text-emerald-300",bg:"bg-emerald-950 border-emerald-600",dot:"bg-emerald-300"},
  "PROMISING":{color:"text-amber-300",bg:"bg-amber-950 border-amber-500",dot:"bg-amber-300"},
  "HOLD":{color:"text-yellow-400",bg:"bg-yellow-950 border-yellow-600",dot:"bg-yellow-400"},
  "NEUTRAL":{color:"text-gray-300",bg:"bg-gray-800 border-gray-600",dot:"bg-gray-300"},
  "RISKY":{color:"text-orange-400",bg:"bg-orange-950 border-orange-500",dot:"bg-orange-400"},
  "PASS":{color:"text-red-400",bg:"bg-red-950 border-red-500",dot:"bg-red-400"},
};
const SCORE_LABELS = {
  market_opportunity:"Market Opportunity",team_strength:"Team Strength",
  product_differentiation:"Product Differentiation",traction:"Traction",financial_health:"Financial Health",
};

function ScoreRing({score}){
  const r=54,circ=2*Math.PI*r,offset=circ-(score/100)*circ;
  const color=score>=75?"#34d399":score>=50?"#fbbf24":"#f87171";
  return(
    <div className="relative w-32 h-32 mx-auto">
      <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r={r} fill="none" stroke="#1f2937" strokeWidth="10"/>
        <circle cx="60" cy="60" r={r} fill="none" stroke={color} strokeWidth="10"
          strokeDasharray={circ} strokeDashoffset={offset} strokeLinecap="round"
          style={{transition:"stroke-dashoffset 1s ease"}}/>
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-bold text-white font-mono">{score}</span>
        <span className="text-xs text-gray-400 tracking-widest">SCORE</span>
      </div>
    </div>
  );
}

function ScoreBar({label,value}){
  const color=value>=75?"from-emerald-600 to-emerald-400":value>=50?"from-amber-600 to-amber-400":"from-red-700 to-red-500";
  return(
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-gray-400">{label}</span>
        <span className="text-white font-mono font-semibold">{value}</span>
      </div>
      <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
        <div className={`h-full bg-gradient-to-r ${color} rounded-full transition-all duration-1000`} style={{width:`${value}%`}}/>
      </div>
    </div>
  );
}

export default function Home() {
  const [form,setForm]       = useState({startup_name:"",industry:"Fintech",stage:"seed",description:""});
  const [phase,setPhase]     = useState("idle");
  const [result,setResult]   = useState(null);
  const [analysisId,setAnalysisId] = useState(null);
  const [errorMsg,setErrorMsg]     = useState("");
  const [sessionId,setSessionId]   = useState(null);

  // UI state
  const [showReport,setShowReport]     = useState(false);
  const [showSidebar,setShowSidebar]   = useState(false);
  const [showHistory,setShowHistory]   = useState(false);
  const [compareIds,setCompareIds]     = useState([]);
  const [scoresCopied,setScoresCopied] = useState(false);
  const [pdfLoading,setPdfLoading]     = useState(false);

  // DAY 6 state
  const [thesis,setThesis]           = useState("");
  const [thesisLoading,setThesisLoading] = useState(false);
  const [shareUrl,setShareUrl]       = useState("");
  const [shareCopied,setShareCopied] = useState(false);
  const [showNews,setShowNews]       = useState(false);

  const pendingForm      = useRef(null);
  const pendingSessionId = useRef(null);
  const resultsRef       = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    const sid = makeSessionId();
    pendingForm.current = {...form};
    pendingSessionId.current = sid;
    setResult(null); setErrorMsg(""); setSessionId(sid);
    setPhase("loading"); setAnalysisId(null);
    setThesis(""); setShareUrl("");
  };

  const handleWsReady = useCallback(async () => {
    const sid=pendingSessionId.current, data=pendingForm.current;
    if (!sid||!data) return;
    try {
      const res = await analyzeStartup(data, sid);
      setResult(res); setPhase("done");
      setTimeout(()=>resultsRef.current?.scrollIntoView({behavior:"smooth"}),100);
    } catch(err){ setErrorMsg(err.message); setPhase("error"); }
  },[]);

  const handleReset = () => {
    setPhase("idle"); setResult(null); setErrorMsg("");
    setSessionId(null); setShowReport(false); setAnalysisId(null);
    setThesis(""); setShareUrl("");
    pendingForm.current=null; pendingSessionId.current=null;
  };

  const handleHistorySelect = async (id) => {
    const res = await fetch(`${API_BASE}/history/${id}`).then(r=>r.json());
    setResult(res.result||res); setAnalysisId(id); setPhase("done");
    setShowSidebar(false); setThesis(""); setShareUrl("");
    setTimeout(()=>resultsRef.current?.scrollIntoView({behavior:"smooth"}),100);
  };

  const handleToggleCompare = (id) => {
    setCompareIds(prev=>prev.includes(id)?prev.filter(x=>x!==id):prev.length<2?[...prev,id]:[prev[1],id]);
  };

  const handleCopyScores = useCallback(()=>{
    if(!result) return;
    const text=[
      `VentureLens AI — ${result.startup_name}`,
      `Overall: ${result.overall_score}/100 · ${result.verdict}`,"",...Object.entries(result.scores||{}).map(([k,v])=>`${SCORE_LABELS[k]||k}: ${v}`),``,`Summary: ${result.summary}`,
    ].join("\n");
    navigator.clipboard.writeText(text).then(()=>{setScoresCopied(true);setTimeout(()=>setScoresCopied(false),2000);});
  },[result]);

  const handlePdfDownload = async () => {
    if(!analysisId){alert("Re-run analysis to get PDF.");return;}
    setPdfLoading(true);
    try{
      const res=await fetch(`${API_BASE}/report/${analysisId}/pdf`);
      if(!res.ok) throw new Error(`PDF failed (${res.status})`);
      const blob=await res.blob();
      const url=URL.createObjectURL(blob);
      const a=document.createElement("a");
      a.href=url; a.download=`${result.startup_name.toLowerCase()}_venturelens.pdf`; a.click();
      URL.revokeObjectURL(url);
    }catch(err){alert(err.message);}
    finally{setPdfLoading(false);}
  };

  const handleGenerateThesis = async () => {
    if(!analysisId){alert("Run analysis first.");return;}
    setThesisLoading(true);
    try{
      const res=await fetch(`${API_BASE}/thesis`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({analysis_id:analysisId})});
      const data=await res.json();
      setThesis(data.thesis||"");
    }catch(e){alert("Thesis generation failed.")}
    finally{setThesisLoading(false);}
  };

  const handleShare = async () => {
    if(!analysisId){alert("Run analysis first.");return;}
    try{
      const res=await fetch(`${API_BASE}/share/${analysisId}`,{method:"POST"});
      const data=await res.json();
      setShareUrl(data.share_url||"");
    }catch(e){alert("Share link generation failed.");}
  };

  const handleCopyShareUrl = () => {
    navigator.clipboard.writeText(shareUrl).then(()=>{setShareCopied(true);setTimeout(()=>setShareCopied(false),2000);});
  };

  const vc = result?(VERDICT_CONFIG[result.verdict]||VERDICT_CONFIG["NEUTRAL"]):null;

  if(showHistory||compareIds.length>0) return (
    <>
      {showSidebar&&<HistorySidebar selectedId={analysisId} onSelect={handleHistorySelect} onClose={()=>setShowSidebar(false)} compareIds={compareIds} onToggleCompare={handleToggleCompare}/>}
      <HistoryPage compareIds={compareIds} onBack={()=>{setShowHistory(false);setCompareIds([]);}}/>
    </>
  );

  return (
    <div className="min-h-screen bg-gray-950 text-white" style={{fontFamily:"'DM Mono',monospace"}}>
      {showSidebar&&<HistorySidebar selectedId={analysisId} onSelect={handleHistorySelect} onClose={()=>setShowSidebar(false)} compareIds={compareIds} onToggleCompare={handleToggleCompare}/>}

      <header className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded bg-amber-400 flex items-center justify-center">
            <span className="text-black font-bold text-sm">V</span>
          </div>
          <span className="text-white font-semibold tracking-widest text-sm">VENTURELENS AI</span>
        </div>
        <div className="flex items-center gap-2">
          {compareIds.length===2&&(
            <button onClick={()=>setShowHistory(true)} className="text-xs bg-amber-400 hover:bg-amber-300 text-black font-bold px-3 py-1.5 rounded transition-all">
              Compare ({compareIds.length}) →
            </button>
          )}
          <button onClick={()=>setShowSidebar(!showSidebar)} className="text-xs text-gray-400 hover:text-white border border-gray-700 hover:border-amber-400 px-3 py-1.5 rounded transition-all">☰ History</button>
          {phase!=="idle"&&<button onClick={handleReset} className="text-xs text-gray-400 hover:text-white border border-gray-700 hover:border-gray-500 px-3 py-1.5 rounded transition-all">← New</button>}
        </div>
      </header>

      <main className={`max-w-3xl mx-auto px-6 py-12 transition-all ${showSidebar?"ml-72":""}`}>

        {phase==="idle"&&(
          <div>
            <div className="mb-10 text-center">
              <p className="text-xs text-amber-400 tracking-[0.3em] mb-3">INSTITUTIONAL-GRADE</p>
              <h1 className="text-4xl font-bold text-white leading-tight">AI Due Diligence<br/><span className="text-amber-400">in Minutes</span></h1>
              <p className="text-gray-400 mt-4 text-sm max-w-md mx-auto">7-agent pipeline — research, market, financials, risk, memo, automated.</p>
            </div>
            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2 space-y-1.5">
                  <label className="text-xs text-gray-400 tracking-widest">STARTUP NAME</label>
                  <input type="text" placeholder="e.g. Stripe" value={form.startup_name} onChange={e=>setForm({...form,startup_name:e.target.value})} required className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-600 focus:outline-none focus:border-amber-400 transition-colors"/>
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs text-gray-400 tracking-widest">INDUSTRY</label>
                  <select value={form.industry} onChange={e=>setForm({...form,industry:e.target.value})} className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-amber-400 transition-colors">
                    {INDUSTRIES.map(i=><option key={i}>{i}</option>)}
                  </select>
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs text-gray-400 tracking-widest">STAGE</label>
                  <select value={form.stage} onChange={e=>setForm({...form,stage:e.target.value})} className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-amber-400 transition-colors">
                    {STAGES.map(s=><option key={s.value} value={s.value}>{s.label}</option>)}
                  </select>
                </div>
                <div className="col-span-2 space-y-1.5">
                  <label className="text-xs text-gray-400 tracking-widest">DESCRIPTION</label>
                  <textarea placeholder="Describe the startup..." value={form.description} onChange={e=>setForm({...form,description:e.target.value})} required rows={4} className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-600 focus:outline-none focus:border-amber-400 transition-colors resize-none"/>
                </div>
              </div>
              <button type="submit" className="w-full bg-amber-400 hover:bg-amber-300 text-black font-bold py-4 rounded-lg tracking-widest text-sm transition-all">RUN DUE DILIGENCE →</button>
            </form>
          </div>
        )}

        {phase==="loading"&&(
          <div>
            <div className="text-center mb-10">
              <p className="text-xs text-amber-400 tracking-[0.3em] mb-2">ANALYZING</p>
              <h2 className="text-2xl font-bold text-white">{form.startup_name}</h2>
              <p className="text-gray-500 text-sm mt-1">7 agents · ~90 seconds</p>
            </div>
            <ProgressTracker sessionId={sessionId} onReady={handleWsReady}
              onResult={(data)=>{setResult(data);if(data.analysis_id)setAnalysisId(data.analysis_id);setPhase("done");}}
              onError={(msg)=>{setErrorMsg(msg);setPhase("error");}}/>
          </div>
        )}

        {phase==="error"&&(
          <div className="text-center space-y-4">
            <div className="text-5xl">⚠️</div>
            <h2 className="text-xl font-bold text-red-400">Analysis Failed</h2>
            <p className="text-gray-400 text-sm max-w-sm mx-auto break-words">{errorMsg}</p>
            <button onClick={handleReset} className="mt-4 border border-gray-600 hover:border-amber-400 text-gray-300 hover:text-amber-400 px-6 py-2 rounded-lg text-sm transition-all">Try Again</button>
          </div>
        )}

        {phase==="done"&&result&&(
          <div ref={resultsRef} className="space-y-6">
            {/* Header */}
            <div className="flex items-start justify-between flex-wrap gap-3">
              <div>
                <p className="text-xs text-amber-400 tracking-[0.3em] mb-1">ANALYSIS COMPLETE</p>
                <h2 className="text-3xl font-bold text-white">{result.startup_name}</h2>
                <p className="text-gray-400 text-sm mt-1">{form.industry||result.industry} · {form.stage||result.stage}</p>
              </div>
              <div className={`px-4 py-2 rounded-lg border text-sm font-bold tracking-widest ${vc.bg} ${vc.color}`}>
                <span className={`inline-block w-2 h-2 rounded-full mr-2 ${vc.dot}`}/>
                {result.verdict}
              </div>
            </div>

            {/* Score */}
            <div className="grid grid-cols-5 gap-6 bg-gray-900 rounded-xl p-6 border border-gray-800">
              <div className="col-span-2 flex flex-col items-center justify-center">
                <ScoreRing score={result.overall_score}/>
                <p className="text-xs text-gray-500 mt-2 tracking-widest">OVERALL SCORE</p>
              </div>
              <div className="col-span-3 space-y-4 flex flex-col justify-center">
                {Object.entries(result.scores||{}).map(([k,v])=><ScoreBar key={k} label={SCORE_LABELS[k]||k} value={v}/>)}
              </div>
            </div>

            {/* Radar */}
            <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs text-gray-400 tracking-widest">RADAR ANALYSIS</p>
                <StickyNote analysisId={analysisId} section="radar" label="Radar Analysis"/>
              </div>
              <RadarChart scores={result.scores||{}} color="#F59E0B" size="md"/>
            </div>

            {/* Summary */}
            <div className="bg-gray-900 rounded-xl p-5 border border-gray-800">
              <div className="flex items-center justify-between mb-3">
                <p className="text-xs text-gray-400 tracking-widest">EXECUTIVE SUMMARY</p>
                <StickyNote analysisId={analysisId} section="summary" label="Executive Summary"/>
              </div>
              <p className="text-gray-200 text-sm leading-relaxed">{result.summary}</p>
            </div>

            {/* Flags */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-900 rounded-xl p-5 border border-emerald-900">
                <div className="flex items-center justify-between mb-3">
                  <p className="text-xs text-emerald-400 tracking-widest">✓ GREEN FLAGS</p>
                  <StickyNote analysisId={analysisId} section="green_flags" label="Green Flags"/>
                </div>
                <ul className="space-y-2">
                  {(result.green_flags||[]).map((f,i)=><li key={i} className="text-xs text-gray-300 flex gap-2"><span className="text-emerald-500 flex-shrink-0 mt-0.5">▸</span><span>{f}</span></li>)}
                </ul>
              </div>
              <div className="bg-gray-900 rounded-xl p-5 border border-red-900">
                <div className="flex items-center justify-between mb-3">
                  <p className="text-xs text-red-400 tracking-widest">✗ RED FLAGS</p>
                  <StickyNote analysisId={analysisId} section="red_flags" label="Red Flags"/>
                </div>
                <ul className="space-y-2">
                  {(result.red_flags||[]).map((f,i)=><li key={i} className="text-xs text-gray-300 flex gap-2"><span className="text-red-500 flex-shrink-0 mt-0.5">▸</span><span>{f}</span></li>)}
                </ul>
              </div>
            </div>

            {/* ── DAY 6: Investment Thesis ── */}
            <div className="bg-gray-900 rounded-xl p-5 border border-gray-800">
              <div className="flex items-center justify-between mb-3">
                <p className="text-xs text-amber-400 tracking-widest">INVESTMENT THESIS</p>
                {!thesis&&(
                  <button onClick={handleGenerateThesis} disabled={thesisLoading||!analysisId}
                    className="text-xs border border-amber-400/40 hover:border-amber-400 text-amber-400 px-3 py-1 rounded-lg transition-all disabled:opacity-40">
                    {thesisLoading?"⏳ Generating...":"⚡ Generate Thesis"}
                  </button>
                )}
              </div>
              {thesis?(
                <div className="text-gray-200 text-sm leading-relaxed whitespace-pre-wrap">{thesis}</div>
              ):(
                <p className="text-gray-600 text-xs">Click "Generate Thesis" for a 200-word bull/bear investment memo.</p>
              )}
            </div>

            {/* ── DAY 6: Competitor Table ── */}
            <CompetitorTable analysisId={analysisId} startupName={result.startup_name}/>

            {/* ── DAY 6: News Feed ── */}
            <div>
              <button onClick={()=>setShowNews(!showNews)}
                className="w-full flex items-center justify-between bg-gray-900 border border-gray-800 rounded-xl px-5 py-3 text-xs text-gray-400 hover:border-amber-400/30 transition-all mb-0">
                <span className="text-amber-400 tracking-widest">LATEST NEWS</span>
                <span>{showNews?"▲ Hide":"▼ Show"}</span>
              </button>
              {showNews&&<NewsFeed startupName={result.startup_name}/>}
            </div>

            {/* Action buttons */}
            <div className="grid grid-cols-3 gap-3">
              <button onClick={()=>setShowReport(true)} className="bg-amber-400 hover:bg-amber-300 text-black font-bold py-3 rounded-lg text-xs tracking-widest transition-all">📄 VIEW REPORT</button>
              <button onClick={handlePdfDownload} disabled={pdfLoading||!analysisId} className="border border-emerald-600 hover:bg-emerald-950 text-emerald-400 py-3 rounded-lg text-xs tracking-widest transition-all disabled:opacity-40">
                {pdfLoading?"⏳...":"↓ PDF"}
              </button>
              <button onClick={handleCopyScores} className="border border-gray-700 hover:border-amber-400 text-gray-400 hover:text-amber-400 py-3 rounded-lg text-xs tracking-widest transition-all">
                {scoresCopied?"✓ Copied":"⎘ SCORES"}
              </button>
            </div>

            {/* ── DAY 6: Share link ── */}
            <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
              <div className="flex items-center justify-between">
                <p className="text-xs text-gray-400 tracking-widest">SHARE REPORT</p>
                {!shareUrl&&(
                  <button onClick={handleShare} disabled={!analysisId}
                    className="text-xs border border-gray-700 hover:border-amber-400 text-gray-400 hover:text-amber-400 px-3 py-1 rounded-lg transition-all disabled:opacity-40">
                    🔗 Generate Share Link
                  </button>
                )}
              </div>
              {shareUrl&&(
                <div className="flex gap-2 mt-3">
                  <input readOnly value={shareUrl} className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-xs text-gray-300 focus:outline-none"/>
                  <button onClick={handleCopyShareUrl} className="text-xs border border-amber-400/40 hover:border-amber-400 text-amber-400 px-3 py-2 rounded-lg transition-all">
                    {shareCopied?"✓":"Copy"}
                  </button>
                </div>
              )}
            </div>

            {result.sources?.length>0&&(
              <div className="bg-gray-900 rounded-xl p-5 border border-gray-800">
                <p className="text-xs text-gray-400 tracking-widest mb-3">SOURCES</p>
                <div className="flex flex-wrap gap-2">
                  {result.sources.map((s,i)=><span key={i} className="text-xs text-gray-500 bg-gray-800 px-2 py-1 rounded border border-gray-700">{s}</span>)}
                </div>
              </div>
            )}

            <button onClick={handleReset} className="w-full border border-gray-700 hover:border-amber-400 text-gray-400 hover:text-amber-400 py-3 rounded-lg text-xs tracking-widest transition-all">← ANALYZE ANOTHER STARTUP</button>
          </div>
        )}
      </main>

      {showReport&&result&&<ReportViewer startupName={result.startup_name} onClose={()=>setShowReport(false)}/>}
    </div>
  );
}