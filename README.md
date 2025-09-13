# lawgic: Our solution for a Legal Tech Hackathon

A RAG-based legal analysis system that processes user queries about Singapore's Personal Data Protection Act (PDPA) and provides structured legal analysis with relevant provisions.

## System Overview

This system uses a multi-stage pipeline to analyze legal scenarios and identify the most relevant PDPA provisions:

1. **Term Extraction** - Extract key legal terms from user queries using Legal-BERT and custom regex/entity logic.
2. **Context Building** - Build comprehensive legal context through 4-layer validation and semantic similarity.
3. **Legal Analysis** - Generate structured legal analysis using Gemini LLM with RAG.

---

## Project Structure

```
lawgic-hackathon/
├── backend/                  # Backend API and processing
│   ├── main.py               # FastAPI backend and CLI
│   ├── term.py               # Legal term extraction (Legal-BERT)
│   ├── context.py            # Context processing and RAG builder
│   ├── requirements.txt      # Python dependencies
│   ├── output.json           # Latest analysis result
│   └── data/                 # Legal knowledge base files
│       ├── pdpa.json
│       ├── interpretation.json
│       ├── schedule.json
│       └── subsidiary.json
├── frontend/                 # Next.js + shadcn/ui frontend
│   └── app/
│       └── page.tsx          # Main UI page
├── .env                      # Gemini API key (create this file)
├── .gitignore                # Git ignore patterns
└── README.md                 # This file
```

---

## Quick Start

### 1. Run the Backend

```bash
cd backend
python -m venv my-env
my-env\Scripts\activate      # On Windows (Command Prompt)
# OR
source my-env/bin/activate   # On macOS/Linux

pip install -r requirements.txt
uvicorn main:app --reload
```

- Backend API available at [http://localhost:8000](http://localhost:8000)

### 2. Run the Frontend

```bash
cd frontend
npm install
npm run dev
```

- Access the app at [http://localhost:3000](http://localhost:3000)



---

## Environment Setup

1. **Create `.env` in backend directory:**

   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

2. **Ensure all data files exist in `backend/data/`:**
   - `pdpa.json`
   - `interpretation.json`
   - `schedule.json`
   - `subsidiary.json`

---

## How It Works

- **Frontend:**  
  User enters a legal scenario. The query is sent to the backend via POST `/query`. The frontend polls `/static/output.json` for the analysis result and displays it in a readable format.

- **Backend:**  
  Receives query, extracts key terms, builds legal context, generates analysis using Gemini, and saves the result to `output.json`.

---

## Troubleshooting

- **Missing API Key:**  
  Create `.env` with your Gemini API key.

- **Missing Python Packages:**  
  Run `pip install -r requirements.txt` in your virtual environment.

- **Data File Not Found:**  
  Ensure all required `.json` files are present in `backend/data/`.

- **Frontend/Backend Not Connecting:**  
  Make sure both servers are running and CORS is enabled in backend.

---

## Technologies Used

- FastAPI, Uvicorn, Python, transformers, sentence-transformers, Gemini API
- Next.js, React, TailwindCSS, shadcn/ui

---

## Logic and Model Details

### 1. Term Extraction (`backend/term.py`)

- **Legal-BERT NER:** Uses the `nlpaueb/legal-bert-base-uncased` model via HuggingFace `transformers` pipeline for named entity recognition on legal text.
- **Keyword Extraction:** Custom regex and word lists extract core PDPA terms, actions, data types, entities, and context modifiers.
- **Entity/Data Type Extraction:** Regex patterns match specific data types (e.g., "email", "performance appraisals") and known organizations/countries.
- **Context Words:** Extracts negations, qualifiers, and other contextually important words.
- **Combination & Deduplication:** All terms are combined, deduplicated, and scored for relevance using a custom scoring function. Top 15 terms are selected for context matching.

### 2. Context Building (`backend/context.py`)

- **Layer 1: PDPA Category Matching**

  - Loads PDPA categories and provisions from `pdpa.json`.
  - Uses `sentence-transformers` (MiniLM) to embed both extracted terms and PDPA categories.
  - Computes cosine similarity to match user terms to relevant PDPA categories.
  - Selects top matches and appends their full legal text to the context.

- **Layer 2: Interpretation Definitions**

  - Loads definitions from `interpretation.json`.
  - Scans context for defined terms and appends their definitions if found.

- **Layer 3: Schedule References**

  - Scans context for mentions of "schedule" (e.g., "Fifth Schedule").
  - Appends the relevant schedule content from `schedule.json`.

- **Layer 4: Subsidiary Legislation**

  - Loads subsidiary legislation mapping from `subsidiary.json`.
  - Matches section numbers from Layer 1 to subsidiary legislation and appends relevant details.

- **Final Context:** All layers are concatenated to form a comprehensive legal context for the LLM.

### 3. Legal Analysis (`backend/main.py`)

- **Prompt Construction:** Builds a detailed prompt for Gemini, including the user scenario, appended legal context, and strict instructions for output format.
- **Gemini LLM Call:** Sends the prompt to Gemini via the `google-generativeai` API, requesting a JSON-formatted analysis.
- **Output Filtering:** Removes any keys containing "Definition" and ensures only valid provision keys are saved.
- **Result Saving:** Writes the final structured analysis to `output.json` for frontend consumption.

### 4. Frontend Logic (`frontend/app/page.tsx`)

- **User Input:** Accepts legal scenario queries from the user.
- **Backend Communication:** Sends the query to the backend `/query` endpoint via POST.
- **Polling for Results:** Polls `/static/output.json` until the analysis result is updated.
- **Result Presentation:** Formats the JSON output for readability, displaying each provision and its reasoning in a clear, presentable way.

---
