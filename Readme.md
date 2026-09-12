# UniGuide AI Arbiter

An advanced Retrieval-Augmented Generation (RAG) engine designed to audit complex university policy documents, detect statutory contradictions, and enforce epistemic calibration (admitting ignorance).

## 🎯 The Problem
University rulebooks are notoriously contradictory. A student asking a policy question usually receives an unverified guess. Standard LLM chatbots fail here because they hallucinate or blend conflicting rules into a single confident (but wrong) answer.

## 🚀 The Solution
This engine utilizes a custom Reciprocal Rank Fusion (RRF) hybrid retriever (BM25 Keyword + Gemini Semantic) coupled with a Gemini Flash-Lite reasoning arbiter. It forces the LLM into one of three strict states using structured outputs:
1. **RESOLVED:** Extracts a single, unambiguous fact with exact citations.
2. **CONTRADICTED:** Detects overlapping or opposing rules, refuses to pick a side, and presents both conflicting citations.
3. **UNADDRESSED:** Admits ignorance when the query falls outside the provided corpus.

## ⚙️ Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd uniguide
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables:**
   Create a `.env` file in the root directory and add your Google AI Studio API key:
   ```env
   GOOGLE_API_KEY=your_api_key_here
   ```

4. **Run the Engine:**
   ```bash
   uvicorn main:app --reload
   ```
   Navigate to `http://localhost:8000` to interact with the UI.

## 🧪 Evaluation
Run the automated test suite to verify the engine's accuracy across all three states (Resolved, Contradicted, Unaddressed):
```bash
python eval.py
```