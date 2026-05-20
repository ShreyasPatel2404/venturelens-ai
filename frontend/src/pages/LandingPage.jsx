// frontend/src/pages/LandingPage.jsx
// Dark editorial VC aesthetic — deep black + amber gold + sharp mono type
import { useState, useEffect } from "react";

const FEATURES = [
  { icon: "🔍", title: "Company Research",    desc: "Live web search across Crunchbase, LinkedIn, TechCrunch. Funding history, team backgrounds, product deep-dive." },
  { icon: "📊", title: "Market Analysis",     desc: "TAM/SAM/SOM with real data. Competitive landscape, growth drivers, regulatory signals." },
  { icon: "💹", title: "Financial Modeling",  desc: "Bear/Base/Bull 5-year projections. MOIC, IRR, and exit multiple calculations with stated assumptions." },
  { icon: "⚠️", title: "Risk Assessment",     desc: "5-category risk scoring: market, execution, financial, regulatory, exit. Severity ratings + mitigants." },
  { icon: "📝", title: "Investor Memo",       desc: "Full investment committee memo with recommendation, thesis, and due diligence checklist." },
  { icon: "🎯", title: "Score Card",          desc: "Quantitative 0–100 score across 5 dimensions. Verdict: STRONG BUY to PASS." },
];

const STATS = [
  { value: "7",    label: "AI Agents" },
  { value: "~90s", label: "Per Analysis" },
  { value: "10+",  label: "Page Report" },
  { value: "100%", label: "AI-Powered" },
];

const SAMPLE_SCORES = [
  { label: "Market Opportunity",      value: 93 },
  { label: "Team Strength",           value: 91 },
  { label: "Product Differentiation", value: 95 },
  { label: "Traction",                value: 98 },
  { label: "Financial Health",        value: 83 },
];

function AnimatedScore({ value, delay = 0 }) {
  const [displayed, setDisplayed] = useState(0);
  useEffect(() => {
    const timer = setTimeout(() => {
      let start = 0;
      const step = () => {
        start += 3;
        if (start >= value) { setDisplayed(value); return; }
        setDisplayed(start);
        requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    }, delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  const color = displayed >= 80 ? "#34d399" : displayed >= 60 ? "#fbbf24" : "#f87171";
  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 h-1.5 bg-gray-800 rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all duration-100"
          style={{ width: `${displayed}%`, backgroundColor: color }} />
      </div>
      <span className="text-white font-mono text-sm w-8 text-right">{displayed}</span>
    </div>
  );
}

export default function LandingPage({ onGetStarted }) {
  const [visible, setVisible] = useState(false);
  useEffect(() => { setTimeout(() => setVisible(true), 100); }, []);

  return (
    <div className="min-h-screen bg-black text-white overflow-x-hidden"
         style={{ fontFamily: "'DM Mono', monospace" }}>

      {/* ── Noise texture overlay ── */}
      <div className="fixed inset-0 pointer-events-none z-0 opacity-[0.03]"
           style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E\")" }} />

      {/* ── Nav ── */}
      <nav className="relative z-10 flex items-center justify-between px-8 py-5 border-b border-gray-900">
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 rounded bg-amber-400 flex items-center justify-center">
            <span className="text-black font-bold text-xs">V</span>
          </div>
          <span className="text-white font-bold tracking-[0.2em] text-sm">VENTURELENS AI</span>
        </div>
        <div className="flex items-center gap-6">
          <a href="#features" className="text-gray-500 hover:text-white text-xs tracking-widest transition-colors">FEATURES</a>
          <a href="#how-it-works" className="text-gray-500 hover:text-white text-xs tracking-widest transition-colors">HOW IT WORKS</a>
          <button onClick={onGetStarted}
            className="text-xs text-black font-bold bg-amber-400 hover:bg-amber-300 px-4 py-2 rounded tracking-widest transition-all">
            LAUNCH APP →
          </button>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="relative z-10 max-w-6xl mx-auto px-8 pt-24 pb-20">
        <div className="grid grid-cols-2 gap-16 items-center">
          <div className={`transition-all duration-700 ${visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}>
            <div className="inline-flex items-center gap-2 border border-amber-400/30 bg-amber-400/5 px-3 py-1.5 rounded-full mb-6">
              <div className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
              <span className="text-amber-400 text-xs tracking-widest">POWERED BY GOOGLE ADK + GEMINI</span>
            </div>
            <h1 className="text-6xl font-bold leading-[1.05] tracking-tight mb-6">
              Institutional<br />
              <span className="text-amber-400">Due Diligence</span><br />
              in 90 Seconds
            </h1>
            <p className="text-gray-400 text-base leading-relaxed mb-8 max-w-md">
              7 specialized AI agents run in sequence — company research, market analysis, financial modeling, risk assessment — producing a 10-page investment memo automatically.
            </p>
            <div className="flex gap-3">
              <button onClick={onGetStarted}
                className="bg-amber-400 hover:bg-amber-300 text-black font-bold px-6 py-3.5 rounded-lg tracking-widest text-sm transition-all hover:shadow-lg hover:shadow-amber-400/20">
                RUN FREE ANALYSIS →
              </button>
              <a href="#how-it-works"
                className="border border-gray-700 hover:border-gray-500 text-gray-400 hover:text-white px-6 py-3.5 rounded-lg text-sm tracking-widest transition-all">
                SEE HOW IT WORKS
              </a>
            </div>
          </div>

          {/* Sample report card */}
          <div className={`transition-all duration-700 delay-200 ${visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}>
            <div className="bg-gray-950 border border-gray-800 rounded-2xl p-6 shadow-2xl">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="text-xs text-amber-400 tracking-widest mb-1">SAMPLE ANALYSIS</p>
                  <h3 className="text-xl font-bold text-white">Stripe</h3>
                  <p className="text-gray-500 text-xs">Fintech · Series B+</p>
                </div>
                <div className="text-right">
                  <div className="text-4xl font-bold font-mono text-white">95</div>
                  <div className="text-xs text-gray-500 tracking-widest">SCORE</div>
                </div>
              </div>

              <div className="inline-flex items-center gap-2 bg-emerald-950 border border-emerald-600 px-3 py-1.5 rounded-lg mb-5">
                <div className="w-2 h-2 rounded-full bg-emerald-400" />
                <span className="text-emerald-400 text-xs font-bold tracking-widest">STRONG BUY</span>
              </div>

              <div className="space-y-3">
                {SAMPLE_SCORES.map((s, i) => (
                  <div key={s.label}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-gray-500">{s.label}</span>
                    </div>
                    <AnimatedScore value={s.value} delay={600 + i * 120} />
                  </div>
                ))}
              </div>

              <div className="mt-5 pt-4 border-t border-gray-800">
                <p className="text-gray-500 text-xs leading-relaxed">
                  "Stripe is a dominant FinTech leader with $1.9T payment volume, exceptional developer ecosystem, and deep competitive moats..."
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Stats row */}
        <div className="grid grid-cols-4 gap-6 mt-16 pt-16 border-t border-gray-900">
          {STATS.map((s, i) => (
            <div key={i} className="text-center">
              <div className="text-3xl font-bold font-mono text-amber-400 mb-1">{s.value}</div>
              <div className="text-gray-600 text-xs tracking-widest">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Features ── */}
      <section id="features" className="relative z-10 max-w-6xl mx-auto px-8 py-20">
        <div className="text-center mb-12">
          <p className="text-xs text-amber-400 tracking-[0.3em] mb-3">WHAT IT DOES</p>
          <h2 className="text-3xl font-bold text-white">7 Agents. One Pipeline.</h2>
        </div>
        <div className="grid grid-cols-3 gap-4">
          {FEATURES.map((f, i) => (
            <div key={i} className="bg-gray-950 border border-gray-800 hover:border-amber-400/30 rounded-xl p-5 transition-all group">
              <div className="text-2xl mb-3">{f.icon}</div>
              <h3 className="text-white font-bold text-sm mb-2 group-hover:text-amber-400 transition-colors">{f.title}</h3>
              <p className="text-gray-500 text-xs leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── How it works ── */}
      <section id="how-it-works" className="relative z-10 max-w-4xl mx-auto px-8 py-20">
        <div className="text-center mb-12">
          <p className="text-xs text-amber-400 tracking-[0.3em] mb-3">THE PROCESS</p>
          <h2 className="text-3xl font-bold text-white">From Input to Report in 3 Steps</h2>
        </div>
        <div className="space-y-4">
          {[
            { n:"01", title:"Enter startup details", desc:"Name, industry, stage, and a brief description. That's all you need." },
            { n:"02", title:"Watch 7 agents work live", desc:"Real-time WebSocket progress shows each agent as it completes — research, analysis, modeling, memo." },
            { n:"03", title:"Get your investment report", desc:"Score card, radar chart, green/red flags, full 10-page memo, PDF download, and comparison tools." },
          ].map((step) => (
            <div key={step.n} className="flex gap-6 items-start bg-gray-950 border border-gray-800 rounded-xl p-6">
              <div className="text-3xl font-bold font-mono text-amber-400/40 flex-shrink-0 w-12">{step.n}</div>
              <div>
                <h3 className="text-white font-bold mb-1">{step.title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{step.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="relative z-10 max-w-2xl mx-auto px-8 py-20 text-center">
        <div className="bg-gradient-to-b from-amber-400/10 to-transparent border border-amber-400/20 rounded-2xl p-12">
          <h2 className="text-3xl font-bold text-white mb-4">Ready to run your first analysis?</h2>
          <p className="text-gray-400 text-sm mb-8">Free to use. No sign-up required. Powered by Gemini 2.5 Flash.</p>
          <button onClick={onGetStarted}
            className="bg-amber-400 hover:bg-amber-300 text-black font-bold px-8 py-4 rounded-lg tracking-widest transition-all hover:shadow-xl hover:shadow-amber-400/20 text-sm">
            START FREE ANALYSIS →
          </button>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="relative z-10 border-t border-gray-900 px-8 py-6 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 rounded bg-amber-400 flex items-center justify-center">
            <span className="text-black font-bold text-xs">V</span>
          </div>
          <span className="text-gray-600 text-xs">VENTURELENS AI</span>
        </div>
        <p className="text-gray-700 text-xs">Not financial advice. For research purposes only.</p>
      </footer>
    </div>
  );
}