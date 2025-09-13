# lawgic: Our solution for a Legal Tech Hackathon

A RAG-based legal analysis system that processes user queries about Singapore's Personal Data Protection Act (PDPA) and provides structured legal analysis with relevant provisions.

## System Overview

This system uses a multi-stage pipeline to analyze legal scenarios and identify the most relevant PDPA provisions:

1. **Term Extraction** - Extract key legal terms from user queries using Legal-BERT
2. **Context Building** - Build comprehensive legal context through 4-layer validation
3. **Legal Analysis** - Generate structured legal analysis using LLM with RAG

## Project Structure

```
lawgic-hackathon/
├── backend/              # Backend processing components
├── data/                 # Legal knowledge base files
│   ├── pdpa.json         # Main PDPA provisions and categories
│   ├── interpretation.json # Legal term definitions
│   ├── schedule.json     # PDPA schedules content
│   └── subsidiary.json   # Subsidiary legislation mapping
├── frontend/             # Frontend user interface components
├── src/                  # Core application logic
│   ├── main.py           # Main application and user interface
│   ├── term.py           # Legal term extraction using Legal-BERT
│   └── context.py        # Context processing and RAG knowledge base builder
├── .env                  # Environment variables (API keys) - create this file
├── .gitignore           # Git ignore patterns
├── README.md            # This file
└── template.yaml        # Project template configuration
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd lawgic-hackathon
```

2. Install dependencies:
```bash
pip install transformers torch google-generativeai python-dotenv numpy scikit-learn
```

3. Create environment file:
```bash
# Create .env file in root directory with:
GEMINI_API_KEY=your_gemini_api_key_here
```

4. Run the system:
```bash
cd src
python main.py
```

## Dependencies

The project requires the following Python packages:

- **transformers**: For Legal-BERT model and tokenization
- **torch**: PyTorch backend for transformer models
- **google-generativeai**: Gemini AI API client
- **python-dotenv**: Environment variable management
- **numpy**: Numerical computations
- **scikit-learn**: Vector similarity calculations

## File Descriptions

### Core Application Files (`src/`)

#### `src/main.py`
- **Purpose**: Main application entry point and user interface
- **Key Functions**:
  - `main()` - Interactive command-line interface
  - `create_legal_analysis_prompt()` - Generates structured prompts for LLM
  - `analyze_legal_scenario()` - Interfaces with Gemini AI for analysis
  - `save_to_output_json()` - Saves results with hardcoded definition filtering
  - `process_query()` - Orchestrates the full analysis pipeline
  - `test_with_sample_query()` - Testing function

#### `src/term.py`
- **Purpose**: Legal term extraction using Legal-BERT for Named Entity Recognition (NER)
- **Key Functions**:
  - `extract_terms_from_query()` - Extracts key legal terms from user queries
- **Technology**: Uses transformers pipeline for legal domain NER
- **Output**: List of identified legal terms for context matching

#### `src/context.py`
- **Purpose**: RAG knowledge base builder - constructs comprehensive legal context
- **Key Functions**:
  - `process_context()` - Main orchestrator for 4-layer context building
  - **Layer 1**: PDPA category matching against extracted terms
  - **Layer 2**: Interpretation definitions lookup
  - **Layer 3**: Schedule content inclusion
  - **Layer 4**: Subsidiary legislation mapping
- **Output**: Concatenated legal context for LLM analysis

### Data Files (`data/`)

#### `data/pdpa.json`
- **Purpose**: Main PDPA provisions organized by categories
- **Structure**: Contains legal categories and their associated provisions
- **Usage**: Primary source for legal provisions matching

#### `data/interpretation.json`
- **Purpose**: Legal term definitions and interpretations
- **Usage**: Appended to context when terms appear in extracted keywords

#### `data/schedule.json`
- **Purpose**: PDPA schedules content (First Schedule, Fifth Schedule, etc.)
- **Usage**: Added to context when "schedule" mentioned in existing context

#### `data/subsidiary.json`
- **Purpose**: Subsidiary legislation mapping and content
- **Usage**: Included when section IDs match primary PDPA provisions

### Frontend (`frontend/`)
- User interface components for the legal analysis system

### Backend (`backend/`)
- Backend processing and API components

## Processing Pipeline

### Stage 1: Term Extraction (`src/term.py`)
```python
key_terms = extract_terms_from_query(user_query)
```
- Uses Legal-BERT for Named Entity Recognition
- Identifies legal concepts, entities, and terminology
- Provides foundation for context matching

### Stage 2: Context Building (`src/context.py`)
```python
legal_context = process_context(
    key_terms=key_terms,
    pdpa_path="../data/pdpa.json",
    interpretation_path="../data/interpretation.json",
    schedule_path="../data/schedule.json", 
    subsidiary_path="../data/subsidiary.json"
)
```

**4-Layer Validation Process:**

1. **Layer 1 - PDPA Category Matching**:
   - Vectorizes extracted terms
   - Compares against vectorized key terms from `pdpa.json`
   - Appends matching PDPA provisions to context

2. **Layer 2 - Interpretation Definitions**:
   - Checks if any extracted terms appear in `interpretation.json`
   - Appends relevant legal definitions to context

3. **Layer 3 - Schedule References**:
   - Scans context for mentions of "schedule"
   - Appends relevant schedule content from `schedule.json`

4. **Layer 4 - Subsidiary Legislation**:
   - Matches section IDs from Layer 1 against `subsidiary.json`
   - Includes relevant subsidiary legislation details

### Stage 3: LLM Analysis (`src/main.py`)
```python
analysis = analyze_legal_scenario(user_query, legal_context)
```
- Uses compiled context as RAG knowledge base
- Generates structured legal analysis via Gemini AI
- Enforces strict output format validation

## Output Format

The system generates structured JSON output saved to `output.json` with strict key formatting:

```json
{
  "S 21(1) and (2) PDPA": "Legal reasoning for why this section applies...",
  "Ss 21(5) and (7) PDPA": "Legal reasoning for multiple sections...",
  "para 1(a) of Fifth Schedule PDPA": "Legal reasoning for schedule reference...",
  "Reg 4 PDPR": "Legal reasoning for regulation..."
}
```

**Accepted Key Formats:**
- `"S [number] PDPA"` - PDPA sections
- `"Reg [number] PDPR"` - Regulations  
- `"para [reference] of [Schedule] PDPA"` - Schedule paragraphs

**Hardcoded Filtering:**
- Automatically removes any keys containing "Definition"
- Ensures only valid provision keys are saved to `output.json`

## Usage Examples

### Interactive Mode
```bash
cd src
python main.py
```

### Sample Query
```
Enter your legal scenario:
> An employee asks her former employer for a copy of all personal data held about her, including performance appraisals. Must the employer disclose this data?
```

### Expected Output
The system will:
1. Extract key terms: ["employee", "personal data", "access", "performance appraisals"]
2. Build legal context through 4-layer validation
3. Generate structured analysis with relevant PDPA sections
4. Save results to `output.json`

## Key Technologies

- **Legal-BERT**: Named Entity Recognition for legal domain
- **Vector Similarity**: Term matching between queries and legal provisions
- **RAG (Retrieval-Augmented Generation)**: Context-aware legal analysis
- **Gemini AI**: Large Language Model for legal reasoning
- **Multi-layer Validation**: Comprehensive context building

## Configuration Files

- `.env`: Environment variables (create this file with your API keys)
- `.gitignore`: Git ignore patterns for the repository
- `template.yaml`: Project template configuration

## Troubleshooting

### Common Issues

1. **Missing API Key**:
   ```
   ERROR: GEMINI_API_KEY not found in environment variables
   ```
   Solution: Create `.env` file with your Gemini API key

2. **Module Import Errors**:
   ```
   ModuleNotFoundError: No module named 'transformers'
   ```
   Solution: Install required packages as listed in Installation section

3. **Data File Not Found**:
   ```
   FileNotFoundError: [Errno 2] No such file or directory: '../data/pdpa.json'
   ```
   Solution: Ensure you're running from the `src/` directory and data files exist

---

*This system provides structured legal analysis for educational and reference purposes. It should not replace professional legal advice.*