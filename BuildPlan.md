# AI VC Due Diligence — Full Product Build Plan
### React.js Frontend + Python Backend | 10-Day Roadmap

---

## 🧠 What Is This Project?

Imagine you're a venture capital analyst. Before investing in a startup, you must spend **2–3 days** researching:
- Who are the founders? Do they have a track record?
- How big is the market? Who are the competitors?
- What does the revenue trajectory look like? What's a realistic exit multiple?
- What could go wrong? Regulatory risk? Technical risk?
- Is the team capable of executing?

This product **automates that entire workflow** using a team of AI agents — each one a specialist — that work in sequence, passing their findings to the next agent, and ultimately producing a **professional investment report** in under 2 minutes.

**The GitHub repo** is a Python terminal demo (CLI). You are going to build it into a **real product**: a React frontend, a FastAPI backend, persistent history, PDF exports, live progress streaming, and competitor comparisons.

---

## 🏗️ Full Architecture (What You're Building)

```
┌──────────────────────────────────────────────────────┐
│                  React.js Frontend                    │
│  - Input form (company name / URL)                   │
│  - Live WebSocket progress bar (which agent is live) │
│  - Radar chart (6 dimension scores)                  │
│  - Full report viewer (markdown → styled HTML)       │
│  - PDF download button                               │
│  - History sidebar (past analyses)                   │
│  - Competitor comparison table                       │
│  - Analyst sticky notes                              │
└────────────────────┬─────────────────────────────────┘
                     │ HTTP / WebSocket
┌────────────────────▼─────────────────────────────────┐
│                  FastAPI Backend (Python)             │
│  - POST /analyze  → starts agent pipeline            │
│  - WS  /ws/{id}   → streams progress to frontend     │
│  - GET /history   → returns SQLite saved analyses    │
│  - GET /report/{id}/pdf → returns generated PDF      │
│  - GET /news/{company}  → SerpAPI news articles      │
└────────────────────┬─────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────┐
│            Agent Pipeline (Google ADK)               │
│  7 sequential agents using Gemini models             │
│  CompanyResearch → Market → Financial → Risk →       │
│  InvestorMemo → Report → Infographic                 │
└──────────────────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────┐
│                  Storage Layer                       │
│  SQLite (analysis history) + file system (PDFs)      │
└──────────────────────────────────────────────────────┘
```

---

## 📁 Project Folder Structure

```
vc-due-diligence/
├── backend/
│   ├── main.py               ← FastAPI entry point
│   ├── agents/
│   │   ├── pipeline.py       ← SequentialAgent orchestrator
│   │   ├── tools.py          ← Web search, chart gen tools
│   │   └── prompts.py        ← All agent system prompts
│   ├── services/
│   │   ├── pdf_generator.py  ← reportlab PDF creation
│   │   ├── news_service.py   ← SerpAPI news integration
│   │   └── db.py             ← SQLite history storage
│   ├── models.py             ← Pydantic request/response models
│   ├── websocket_manager.py  ← WebSocket connection manager
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── pages/
│   │   │   ├── HomePage.jsx      ← Input form + recent analyses
│   │   │   ├── AnalysisPage.jsx  ← Live progress + full report
│   │   │   └── HistoryPage.jsx   ← All past analyses
│   │   ├── components/
│   │   │   ├── AnalysisForm.jsx
│   │   │   ├── ProgressTracker.jsx   ← WebSocket live feed
│   │   │   ├── RadarChart.jsx        ← Recharts radar
│   │   │   ├── ReportViewer.jsx      ← Markdown renderer
│   │   │   ├── CompetitorTable.jsx
│   │   │   ├── StickyNotes.jsx
│   │   │   ├── NewsFeed.jsx
│   │   │   └── HistorySidebar.jsx
│   │   ├── hooks/
│   │   │   ├── useWebSocket.js
│   │   │   └── useAnalysis.js
│   │   └── api/
│   │       └── client.js         ← Axios API calls
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

---

## 🔑 Key Technologies

| Layer | Tech | Why |
|---|---|---|
| Frontend framework | React.js + Vite | Fast dev, component-based |
| Styling | Tailwind CSS | Utility-first, rapid UI |
| Charts | Recharts | RadarChart built-in |
| HTTP client | Axios | Clean async API calls |
| Backend | FastAPI (Python) | Async, WebSocket support |
| Agent framework | Google ADK | SequentialAgent pipeline |
| AI models | Gemini 2.0 Flash | Fast, multimodal |
| Web search | Google Search tool (ADK) | Real-time company data |
| PDF generation | ReportLab | Branded PDF export |
| Database | SQLite + SQLAlchemy | Zero-config persistence |
| Real-time | WebSockets | Live agent progress |
| News | SerpAPI | Latest company news |
| Environment | python-dotenv | API key management |

---

## 📅 10-Day Build Plan

> **How to use this plan with Claude's daily limit:**
> Each day is a self-contained session. At the start of each session, paste "DAY N" into Claude and request only that day's code. Each day ends at a testable checkpoint, so nothing is wasted if a session ends early.

---

### DAY 1 — Project Setup + Backend Skeleton
**Goal:** Running FastAPI server with a dummy analysis endpoint.

**What to ask Claude:**
> "Give me DAY 1 of the VC due diligence project: Set up the FastAPI backend skeleton with `main.py`, `models.py`, and a dummy `POST /analyze` endpoint that returns a fake response. Include `requirements.txt` and a `.env.example`."

**Deliverables:**
- `backend/main.py` — FastAPI app with CORS
- `backend/models.py` — Pydantic request/response models
- `backend/requirements.txt`
- `.env.example`
- Frontend: `npm create vite@latest` + Tailwind CSS setup

**Test:** `uvicorn main:app --reload` starts, `POST /analyze` returns 200.

---

### DAY 2 — Agent Pipeline (Core Backend)
**Goal:** Real 7-agent pipeline from the GitHub repo working in Python.

**What to ask Claude:**
> "Give me DAY 2: Implement the Google ADK SequentialAgent pipeline in `backend/agents/pipeline.py` and `tools.py`. The 7 agents: CompanyResearch, MarketAnalysis, FinancialModeling, RiskAssessment, InvestorMemo, ReportGenerator, InfographicGenerator. Use Gemini 2.0 Flash and Google Search tool. Wire it to the `/analyze` endpoint."

**Deliverables:**
- `backend/agents/pipeline.py`
- `backend/agents/tools.py`
- `backend/agents/prompts.py`

**Test:** Run a real analysis from terminal/Postman for "OpenAI" or "Stripe".

---

### DAY 3 — WebSocket Live Progress (HIGH PRIORITY)
**Goal:** Frontend sees which agent is running in real-time.

**What to ask Claude:**
> "Give me DAY 3: Add WebSocket support to FastAPI. Create `websocket_manager.py` that broadcasts agent progress events. Each agent should emit: {stage: 'company_research', status: 'running'|'done', message: '...'}. Create `frontend/src/hooks/useWebSocket.js` and `ProgressTracker.jsx` that shows a vertical stepper of agent stages."

**Deliverables:**
- `backend/websocket_manager.py`
- Updated `pipeline.py` with progress callbacks
- `frontend/src/hooks/useWebSocket.js`
- `frontend/src/components/ProgressTracker.jsx`

**Test:** Start analysis, see stages light up in real-time on frontend.

---

### DAY 4 — Report Viewer + Basic UI
**Goal:** Full analysis report rendered beautifully in React.

**What to ask Claude:**
> "Give me DAY 4: Build `ReportViewer.jsx` that takes a markdown string and renders it with syntax highlighting and styled sections (Executive Summary, Market Analysis, Financial Projections, Risk Assessment, Recommendation). Also build `AnalysisPage.jsx` that shows ProgressTracker while running, then switches to ReportViewer when done."

**Deliverables:**
- `frontend/src/components/ReportViewer.jsx` (use react-markdown)
- `frontend/src/pages/AnalysisPage.jsx`
- `frontend/src/pages/HomePage.jsx` with AnalysisForm

**Test:** Submit a company, watch progress, see full report render.

---

### DAY 5 — Radar Chart Score Visualization (HIGH PRIORITY)
**Goal:** 6-dimension radar chart showing investment scores.

**What to ask Claude:**
> "Give me DAY 5: Add score extraction to the backend — after the pipeline runs, parse the memo output to extract 6 scores (Team, Market, Product, Financials, Traction, Risk) on a 0-10 scale using a small Gemini call. Return scores in the API response. Build `RadarChart.jsx` using Recharts RadarChart component to display these 6 dimensions."

**Deliverables:**
- `backend/services/score_extractor.py`
- Updated API response model with `scores` field
- `frontend/src/components/RadarChart.jsx`

**Test:** Radar chart appears on report page with real scores.

---

### DAY 6 — PDF Report Download (HIGH PRIORITY)
**Goal:** One-click branded PDF export of the full report.

**What to ask Claude:**
> "Give me DAY 6: Build `backend/services/pdf_generator.py` using ReportLab to generate a branded PDF with: cover page (company name + date + logo placeholder), executive summary, all report sections, and the 6 radar scores as a table. Add a `GET /report/{analysis_id}/pdf` endpoint. Add a download button in the React frontend."

**Deliverables:**
- `backend/services/pdf_generator.py`
- PDF endpoint in `main.py`
- Download button in `ReportViewer.jsx`

**Test:** Click download, get a professional PDF.

---

### DAY 7 — Analysis History + SQLite (MEDIUM)
**Goal:** Save every analysis, show history, compare two companies.

**What to ask Claude:**
> "Give me DAY 7: Implement SQLite persistence using SQLAlchemy in `backend/services/db.py`. Save each completed analysis (company, timestamp, scores, full report markdown). Add `GET /history` and `GET /report/{id}` endpoints. Build `HistorySidebar.jsx` and `HistoryPage.jsx` in React. Add side-by-side comparison: load two analyses and show their radar charts next to each other."

**Deliverables:**
- `backend/services/db.py`
- History endpoints
- `frontend/src/components/HistorySidebar.jsx`
- `frontend/src/pages/HistoryPage.jsx`
- Comparison view (two RadarCharts side by side)

**Test:** Run 2 analyses, compare them side by side.

---

### DAY 8 — Competitor Comparison Table (MEDIUM)
**Goal:** Auto-generated startup vs top 3 competitor table.

**What to ask Claude:**
> "Give me DAY 8: Add a CompetitorAnalysis agent (or extend MarketAnalysis) that outputs structured JSON: top 3 competitors with fields [name, founded, funding, revenue_est, team_size, key_differentiator]. Build `CompetitorTable.jsx` in React that renders this as a styled table with the analyzed startup highlighted."

**Deliverables:**
- Updated pipeline with competitor JSON output
- `frontend/src/components/CompetitorTable.jsx`

**Test:** Table appears in report with real competitor data.

---

### DAY 9 — Analyst Notes + News Feed (MEDIUM + NICE-TO-HAVE)
**Goal:** Sticky notes on report sections + latest news articles.

**What to ask Claude:**
> "Give me DAY 9: (1) Build `StickyNotes.jsx` — each report section gets a note icon, clicking opens a textarea that saves text to localStorage keyed by analysis_id + section. (2) Build `NewsFeed.jsx` and `backend/services/news_service.py` using SerpAPI to fetch the 5 latest news articles about the company. Show them in a sidebar on the report page."

**Deliverables:**
- `frontend/src/components/StickyNotes.jsx`
- `frontend/src/components/NewsFeed.jsx`
- `backend/services/news_service.py`

**Test:** Add a note to a section, reload page — note persists. News articles show up.

---

### DAY 10 — Investment Thesis Generator + Polish + Deployment
**Goal:** One-click thesis memo + final polish + deploy instructions.

**What to ask Claude:**
> "Give me DAY 10: (1) Add an InvestmentThesisGenerator button in the report — calls a small FastAPI endpoint that uses Gemini to write a 200-word 'why invest / why not invest' memo based on the report. (2) Add share link support: generate a UUID URL that loads a read-only report from SQLite. (3) Give me a Dockerfile for the backend and a Vercel deploy config for the frontend."

**Deliverables:**
- Thesis generator endpoint + UI button
- Share URL feature
- `Dockerfile` for backend
- `vercel.json` for frontend
- Updated `README.md` with full setup instructions

**Test:** Share link opens a read-only report. Docker build works.

---

## 🔐 API Keys You Need

| Service | Key | Where to get |
|---|---|---|
| Google Gemini | `GOOGLE_API_KEY` | aistudio.google.com |
| SerpAPI (news) | `SERPAPI_KEY` | serpapi.com (100 free/month) |

---

## ⚙️ Initial Setup Commands (Run Once Before Day 1)

```bash
# Clone the reference repo
git clone https://github.com/Shubhamsaboo/awesome-llm-apps.git
cd awesome-llm-apps/advanced_ai_agents/multi_agent_apps/agent_teams/ai_vc_due_diligence_agent_team

# Study the original files: pipeline.py, tools.py, app.py

# Create your product repo
mkdir vc-due-diligence && cd vc-due-diligence
git init

# Backend setup
mkdir backend && cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install fastapi uvicorn google-adk python-dotenv reportlab sqlalchemy aiofiles websockets

# Frontend setup
cd ..
npm create vite@latest frontend -- --template react
cd frontend
npm install
npm install tailwindcss axios recharts react-markdown react-router-dom
npx tailwindcss init -p
```

---

## 💡 How to Use Claude Efficiently Each Day

1. **Start each session** by pasting this context:
   > "I'm building an AI VC Due Diligence product. React frontend + FastAPI backend + Google ADK agents. Here's my current folder structure: [paste tree]. Today is DAY N."

2. **Ask for one file at a time** if the limit is close — each file is independently useful.

3. **Save a "resume prompt"** at the end of each day:
   > "What we built today: [list]. What's next: DAY N+1 — [goal]."

4. **Test after every day** before starting the next. Never skip testing.

---

## 🎯 Feature Priority Summary

| Day | Feature | Priority |
|---|---|---|
| 1 | Project skeleton | Foundation |
| 2 | Agent pipeline | Foundation |
| 3 | WebSocket progress | 🔴 High |
| 4 | Report viewer | 🔴 High |
| 5 | Radar chart | 🔴 High |
| 6 | PDF export | 🔴 High |
| 7 | History + comparison | 🟡 Medium |
| 8 | Competitor table | 🟡 Medium |
| 9 | Notes + news | 🟡 Medium |
| 10 | Thesis + share + deploy | 🟢 Nice-to-have |

**MVP (days 1-6)** is a fully usable, impressive product on its own.