from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from engine import RulebookEngine
from retriever import build_hybrid_retriever

print("⏳ Initializing UniGuide AI Engine...")
retriever = build_hybrid_retriever("./corpus")
engine = RulebookEngine(retriever)
print("✅ Engine Ready!")

app = FastAPI(title="UniGuide AI Arbiter")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

@app.post("/api/audit")
async def audit_query(req: QueryRequest):
    try:
        verdict = engine.query(req.question)
        return verdict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta content="width=device-width, initial-scale=1.0" name="viewport">
<title>UniGuide Arbiter — Office of Academic Regulations & Institutional Compliance</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com" rel="preconnect">
<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,500&family=JetBrains+Mono:wght@500;600&display=swap" rel="stylesheet">
<script>
    tailwind.config = {
      theme: {
        extend: {
          fontFamily: {
            sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
            serif: ['Newsreader', 'Georgia', 'Cambria', 'serif'],
            mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
          }
        }
      }
    }
  </script>
<style>
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #f8fafc; }
    ::-webkit-scrollbar-thumb { background: #94a3b8; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #64748b; }
    .fade-enter {
      animation: fadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(4px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body class="bg-[#F8F9FA] text-slate-900 font-sans min-h-screen text-sm sm:text-base">
<header class="border-b border-slate-300 bg-white sticky top-0 z-40 shadow-sm">
<div class="max-w-4xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
<div class="flex items-center gap-3">
<div class="w-8 h-8 rounded border border-slate-400 bg-slate-900 text-white flex items-center justify-center font-serif text-base font-bold tracking-tighter">
    §
    </div>
<div class="border-l border-slate-300 pl-3">
<div class="flex items-center gap-2">
<span class="text-sm font-bold uppercase tracking-wider text-slate-900">UNIGUIDE</span>
</div>
</div>
</div>
</div>
</header>
<main class="max-w-4xl mx-auto px-4 sm:px-6 py-8 space-y-6">
<div class="space-y-2 border-b border-slate-300 pb-5">
<h1 class="text-3xl sm:text-4xl font-serif font-bold tracking-tight text-slate-900 leading-tight">
        UniGuide Arbiter
      </h1>
<p class="text-slate-800 text-base max-w-2xl leading-relaxed font-sans font-medium">
        Submit inquiries concerning university statutes, faculty Senate bylaws, and student codes. The arbiter detects textual divergence, jurisdictional precedence conflicts, and regulatory silences.
      </p>
</div>
<div class="space-y-2">
<div class="flex items-center justify-between">
<label class="text-sm font-bold uppercase tracking-wider text-slate-800" for="questionInput">
          Inquiry & Statutory Citation Search
        </label>
</div>
<form class="relative rounded-lg border-2 border-slate-300 bg-white shadow-sm focus-within:border-blue-600 focus-within:ring-1 focus-within:ring-blue-600 transition" id="auditForm" onsubmit="handleAudit(event)">
<div class="flex items-start px-3.5 py-2">
<svg class="w-5 h-5 text-slate-500 shrink-0 mr-3 mt-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
<path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
</svg>
<textarea rows="2" class="w-full py-2 text-base text-slate-900 placeholder:text-slate-500 font-medium bg-transparent border-0 focus:outline-none focus:ring-0 resize-none" id="questionInput" placeholder="State policy question, e.g., 'Can I take a supplementary exam with a D grade?'" required>If I voluntarily withdraw 10 days after the semester starts, am I eligible for an 80% tuition refund?</textarea>
<div class="flex items-center gap-2 ml-2 shrink-0 mt-1">
<button class="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-bold tracking-wide shadow-sm transition flex items-center justify-center gap-1.5" id="auditSubmitBtn" type="submit">
<span id="btnText">Audit</span>
<svg class="w-4 h-4" fill="none" id="btnIcon" stroke="currentColor" viewBox="0 0 24 24">
<path d="M14 5l7 7m0 0l-7 7m7-7H3" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
</svg>
</button>
</div>
</div>
</form>
</div>
<div class="fade-enter" id="resultsContainer"></div>
</main>
<script>
    function renderCard(data) {
      const container = document.getElementById('resultsContainer');
      container.innerHTML = '';
      container.className = 'fade-enter';

      const state = (data.state || 'UNADDRESSED').toUpperCase();
      const isResolved = state === 'RESOLVED';
      const isContradicted = state === 'CONTRADICTED';
      const isUnaddressed = state === 'UNADDRESSED';

      let statusBadge = '';
      if (isContradicted) {
        statusBadge = `
          <span class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-bold bg-red-100 text-red-900 border border-red-300 shadow-sm">
            <span class="w-2 h-2 rounded-full bg-red-600"></span>
            Statutory Contradiction Detected
          </span>
        `;
      } else if (isResolved) {
        statusBadge = `
          <span class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-bold bg-emerald-100 text-emerald-900 border border-emerald-300 shadow-sm">
            <span class="w-2 h-2 rounded-full bg-emerald-600"></span>
            Statute Harmonized & Resolved
          </span>
        `;
      } else {
        statusBadge = `
          <span class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-bold bg-slate-200 text-slate-800 border border-slate-400 shadow-sm">
            <span class="w-2 h-2 rounded-full bg-slate-500"></span>
            Unaddressed in Codex
          </span>
        `;
      }

      const confPercent = Math.round((data.confidence !== undefined ? data.confidence : 1.0) * 100);

      const card = document.createElement('article');
      card.className = "bg-white border-2 border-slate-200 rounded-xl shadow-md overflow-hidden mt-6";

      let memorandumHeader = `
        <div class="px-6 py-5 border-b border-slate-200 bg-slate-50 flex flex-wrap items-center justify-between gap-4">
          <div>
            <div class="flex items-center gap-2 mb-1">
              <span class="text-xs font-mono uppercase tracking-widest text-slate-600 font-bold">ARBITRATION MEMORANDUM</span>
              <span class="text-slate-400">&bull;</span>
              <span class="text-sm text-slate-600 font-mono font-bold">${data.docket || 'DOK-2026'}</span>
            </div>
            <h2 class="text-base font-bold text-slate-900">${data.question || ''}</h2>
          </div>
          <div class="flex items-center gap-4">
            ${statusBadge}
            <div class="hidden sm:block text-right border-l-2 border-slate-300 pl-4">
              <span class="block text-[11px] uppercase text-slate-600 font-bold font-mono mb-1">Confidence</span>
              <span class="text-sm font-mono font-bold text-slate-900">${confPercent}%</span>
            </div>
          </div>
        </div>

        <div class="p-6 sm:p-8 space-y-8">
          <div>
            <h3 class="text-sm font-bold uppercase tracking-wider text-slate-600 mb-3 font-mono">
              Executive Finding
            </h3>
            <div class="text-slate-900 text-base leading-relaxed bg-white p-5 rounded-lg border-2 border-slate-200 font-medium shadow-sm">
              ${data.answer || ''}
            </div>
          </div>
      `;

      let citationsContent = '';

      if (isContradicted) {
        // Robust routing logic in case LLM bundles both into conflicting_citations
        let c1 = { source: 'Pending Analysis', section: 'N/A', quote: 'No excerpt provided.' };
        let c2 = { source: 'Pending Analysis', section: 'N/A', quote: 'No excerpt provided.' };
        
        if (data.conflicting_citations && data.conflicting_citations.length >= 2) {
            c1 = data.conflicting_citations[0];
            c2 = data.conflicting_citations[1];
        } else if (data.citations && data.citations.length >= 2) {
            c1 = data.citations[0];
            c2 = data.citations[1];
        } else {
            if (data.citations && data.citations.length > 0) c1 = data.citations[0];
            if (data.conflicting_citations && data.conflicting_citations.length > 0) c2 = data.conflicting_citations[0];
        }

        citationsContent = `
          <div class="space-y-5">
            <div class="flex items-center justify-between border-b-2 border-slate-200 pb-2">
              <h3 class="text-sm font-bold uppercase tracking-wider text-slate-600 font-mono">
                Comparative Statutory Analysis
              </h3>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="border-2 border-slate-200 rounded-lg p-5 bg-white shadow-sm space-y-3">
                <div class="flex items-center justify-between">
                  <span class="text-xs font-mono text-blue-900 bg-blue-100 px-3 py-1 rounded border border-blue-300 font-bold uppercase tracking-wide">Authority A</span>
                </div>
                <div>
                  <h4 class="text-sm font-bold text-slate-900">${c1.source}</h4>
                  <p class="text-xs font-mono font-bold text-slate-600 mt-1">${c1.section}</p>
                </div>
                <blockquote class="font-serif text-base text-slate-800 leading-relaxed border-l-4 border-blue-500 pl-4 py-1 bg-slate-50 italic font-medium">
                  &ldquo;${c1.quote}&rdquo;
                </blockquote>
              </div>

              <div class="border-2 border-slate-200 rounded-lg p-5 bg-white shadow-sm space-y-3">
                <div class="flex items-center justify-between">
                  <span class="text-xs font-mono text-red-900 bg-red-100 px-3 py-1 rounded border border-red-300 font-bold uppercase tracking-wide">Authority B (Conflict)</span>
                </div>
                <div>
                  <h4 class="text-sm font-bold text-slate-900">${c2.source}</h4>
                  <p class="text-xs font-mono font-bold text-slate-600 mt-1">${c2.section}</p>
                </div>
                <blockquote class="font-serif text-base text-slate-800 leading-relaxed border-l-4 border-red-500 pl-4 py-1 bg-slate-50 italic font-medium">
                  &ldquo;${c2.quote}&rdquo;
                </blockquote>
              </div>
            </div>
          </div>
        `;
      } else if (isResolved) {
        const c1 = (data.citations && data.citations[0]) || { source: 'Corpus Document', section: 'Section X', quote: 'No quote available' };

        citationsContent = `
          <div class="space-y-4">
            <h3 class="text-sm font-bold uppercase tracking-wider text-slate-600 font-mono">
              Controlling Statutory Authority
            </h3>
            <div class="border-2 border-slate-200 rounded-lg p-5 bg-white shadow-sm space-y-3">
              <h4 class="text-sm font-bold text-slate-900">${c1.source}</h4>
              <p class="text-xs font-mono font-bold text-slate-600">${c1.section}</p>
              <blockquote class="font-serif text-base text-slate-800 leading-relaxed border-l-4 border-emerald-500 pl-4 py-1 bg-slate-50 italic font-medium">
                &ldquo;${c1.quote}&rdquo;
              </blockquote>
            </div>
          </div>
        `;
      } else {
        citationsContent = `
          <div class="space-y-4">
            <h3 class="text-sm font-bold uppercase tracking-wider text-slate-600 font-mono">
              Citation Verification
            </h3>
            <div class="p-8 border-2 border-slate-200 rounded-lg bg-slate-50 text-center space-y-3 shadow-sm">
              <div class="w-10 h-10 rounded-full border-2 border-slate-400 bg-white text-slate-700 flex items-center justify-center mx-auto text-base font-mono font-bold">
                0
              </div>
              <h4 class="text-sm font-bold text-slate-900">No Recognized Precedent in Corpus</h4>
              <p class="text-sm text-slate-600 font-medium max-w-md mx-auto leading-relaxed">
                The indexing engine identified zero statutory enactments, administrative circulars, or Faculty decrees regarding this subject matter.
              </p>
            </div>
          </div>
        `;
      }

      let memorandumFooter = `
        </div>
      `;

      card.innerHTML = memorandumHeader + citationsContent + memorandumFooter;
      container.appendChild(card);
    }

    async function handleAudit(event) {
      if (event) event.preventDefault();
      const question = document.getElementById('questionInput').value.trim();
      if (!question) return;

      showLoadingState();

      try {
        const response = await fetch('/api/audit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question })
        });

        if (!response.ok) throw new Error('Backend server error');
        
        const data = await response.json();
        
        const formattedData = {
            state: data.state,
            confidence: data.confidence !== undefined ? data.confidence : 1.0,
            docket: "DOK-" + Math.floor(Math.random() * 90000 + 10000),
            question: question,
            answer: data.answer,
            citations: data.citations || [],
            conflicting_citations: data.conflicting_citations || []
        };

        renderCard(formattedData);
      } catch (err) {
        alert("Engine Error: Ensure uvicorn is running and your API key is active.");
      } finally {
        resetSubmitBtn();
      }
    }

    function showLoadingState() {
      const btn = document.getElementById('auditSubmitBtn');
      const text = document.getElementById('btnText');
      const icon = document.getElementById('btnIcon');
      btn.disabled = true;
      btn.classList.add('opacity-75');
      text.innerText = 'Evaluating...';
      icon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>`;
      icon.classList.add('animate-spin');

      const container = document.getElementById('resultsContainer');
      container.innerHTML = `
        <div class="bg-white border-2 border-slate-200 rounded-xl p-10 mt-6 text-center space-y-4 shadow-sm">
          <div class="w-8 h-8 border-4 border-slate-300 border-t-blue-600 rounded-full animate-spin mx-auto"></div>
          <div>
            <h4 class="text-sm font-bold text-slate-900 uppercase tracking-wider font-mono">Conducting Statutory Synthesis</h4>
            <p class="text-sm text-slate-600 font-medium mt-1">Cross-referencing university codes against formal jurisdiction hierarchies...</p>
          </div>
        </div>
      `;
    }

    function resetSubmitBtn() {
      const btn = document.getElementById('auditSubmitBtn');
      const text = document.getElementById('btnText');
      const icon = document.getElementById('btnIcon');
      btn.disabled = false;
      btn.classList.remove('opacity-75');
      text.innerText = 'Audit';
      icon.classList.remove('animate-spin');
      icon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path>`;
    }
  
    document.getElementById('questionInput').addEventListener('keydown', function(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleAudit(e);
      }
    });
  </script>
</body>
</html>
"""