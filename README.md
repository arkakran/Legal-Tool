# ⚖️ Legal Brief Analyzer

> AI-Powered Legal Document Analysis System

A Flask application that extracts and ranks key legal arguments from PDF documents using AI, vector search, and natural language processing.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [File Details](#-file-details)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)

---

## ✨ Features

-  PDF document processing and text extraction
-  AI-powered legal argument extraction using LLM
-  Semantic search with FAISS vector database
-  Intelligent ranking and scoring of arguments
-  Page reference and metadata extraction

---

## 🛠️ Tech Stack

- **Flask** - Web framework
- **Groq + LangChain** - LLM integration
- **FAISS** - Vector similarity search
- **Sentence Transformers** - Text embeddings
- **PDFPlumber** - PDF text extraction
- **Pydantic** - Data validation
- **Loguru** - Logging

---

## 📁 Project Structure

```
legal-brief-analyzer/
│
├── app/                           # Main application package
│   ├── __init__.py                # Flask app factory
│   ├── config.py                  # Configuration with Pydantic
│   ├── extensions.py              # Extensions initialization
│   │
│   ├── blueprints/                # Route blueprints
│   │   ├── api/                   # API routes
│   │   │   ├── __init__.py
│   │   │   └── routes.py          # API endpoints
│   │   └── main/                  # Web routes
│   │       ├── __init__.py
│   │       └── routes.py          # Web pages
│   │
│   ├── models/                    # Data models
│   │   ├── __init__.py
│   │   └── schemas.py             # Pydantic schemas
│   │
│   ├── services/                  # Business logic
│   │   ├── __init__.py
│   │   ├── pdf_processor.py       # PDF parsing
│   │   ├── metadata_extractor.py  # Metadata extraction
│   │   ├── vector_store.py        # FAISS operations
│   │   ├── llm_analyzer.py        # LLM analysis
│   │   ├── post_processor.py      # Result processing
│   │   └── pipeline.py            # Main pipeline
│   │
│   ├── utils/                     # Utilities
│   │   ├── __init__.py
│   │   ├── embeddings.py          # Embedding service
│   │   ├── helpers.py             # Helper functions
│   │   └── validators.py          # Input validation
│   │
│   ├── static/                    # Frontend assets
│   │   ├── css/
│   │   │   └── style.css          # Styling
│   │   └── js/
│   │       └── main.js            # Frontend logic
│   │
│   └── templates/                 # HTML templates
│       ├── base.html              # Base template
│       ├── index.html             # Upload page
│       └── results.html           # Results page
│
├── data/
│   └── uploads/                   # Temporary file storage
│
├── logs/                          # Application logs
│   └── app.log
│
├── .env                           # Environment variables
├── requirements.txt               # Dependencies
├── run.py                         # Application entry point
└── README.md                    # This file
```

---

## 📄 File Details

### **Core Application Files**

#### `app/__init__.py`
Flask application factory that creates and configures the Flask app.
- Loads configuration using Pydantic
- Initializes Flask app with settings
- Registers blueprints (main and api routes)
- Sets up extensions and logging

#### `app/config.py`
Centralized configuration management using Pydantic Settings.
- Loads environment variables from `.env` file
- Validates API keys and configuration values
- Sets defaults for all parameters (chunk size, model names, etc.)
- Auto-creates required directories (uploads, logs)
- Provides `get_config()` function for safe configuration loading

#### `app/extensions.py`
Initializes Flask extensions and logging system.
- Configures Loguru logger for console and file logging
- Sets up log rotation (5MB files, 7-day retention)
- Creates logs directory if needed

---

### **Blueprint Files (Routes)**

#### `app/blueprints/main/routes.py`
Web interface routes.
- `GET /` - Upload page (renders index.html)
- `GET /results/<doc_id>` - Results page (renders results.html)

#### `app/blueprints/api/routes.py`
RESTful API endpoints.
- `POST /api/analyze` - Upload and analyze PDF document
  - Validates file (PDF check, size limit)
  - Saves file temporarily
  - Runs analysis pipeline
  - Returns JSON with extracted arguments
  - Cleans up temporary files
- `GET /api/health` - Health check endpoint

---

### **Data Models**

#### `app/models/schemas.py`
Pydantic models for type-safe data structures.

**Enums:**
- `DocumentType` - Document classification (brief, motion, opinion, etc.)
- `Stance` - Argument position (plaintiff, defendant, amicus, neutral, etc.)
- `ArgumentCategory` - Argument type (constitutional, statutory, case_law, etc.)

**Models:**
- `ExtractedPoint` - Single legal argument with metadata
  - summary, importance, stance, supporting_quote
  - legal_concepts, page_start/end, category
  - retrieval_score, combined_score
- `FinalKeyPoint` - Extends ExtractedPoint with final_rank
- `LLMAnalysisOutput` - LLM response wrapper with extracted_points and confidence

---

### **Service Layer**

#### `app/services/pdf_processor.py`
Handles PDF parsing and text chunking.
- Opens PDF with PDFPlumber
- Extracts text page by page
- Splits text into overlapping chunks (configurable size/overlap)
- Preserves page numbers and metadata in each chunk
- Returns list of chunks with metadata

#### `app/services/metadata_extractor.py`
Extracts document-level metadata.
- Analyzes chunks to determine total pages
- Counts total chunks
- Stores document name and ID
- Returns metadata dictionary

#### `app/services/vector_store.py`
Manages FAISS vector database for semantic search.
- Initializes HNSW (Hierarchical Navigable Small World) index
- Embeds text chunks using sentence transformers
- Adds embeddings to FAISS index
- Performs semantic similarity search
- Converts distances to similarity scores (0-1 range)
- Handles NaN/Inf values gracefully

#### `app/services/llm_analyzer.py`
LLM-based legal argument extraction.
- Connects to Groq API with LangChain
- Prepares context from retrieved chunks
- Sends structured prompt to LLM requesting legal argument extraction
- Parses JSON response from LLM
- Validates and creates ExtractedPoint objects
- Maps stance and category enums
- Returns LLMAnalysisOutput with all extracted arguments

**Prompt Engineering:**
- Acts as "Supreme Court-level legal analyst"
- Requests: summary, importance, stance, supporting quotes, legal concepts, page numbers, categories
- Enforces JSON output format

#### `app/services/post_processor.py`
Post-processes and ranks extracted arguments.
- Calculates combined score from:
  - 50% importance_score (from LLM)
  - 30% retrieval_score (from vector search)
  - 20% match_confidence (fuzzy matching)
- Uses RapidFuzz to verify supporting quotes against actual chunks
- Updates page numbers if better match found
- Sorts by combined score (descending)
- Limits to top K results
- Assigns final ranks (1, 2, 3...)

#### `app/services/pipeline.py`
Main orchestration pipeline coordinating all steps.

**8-Step Process:**
1. Validate file path and calculate content hash (document ID)
2. Process PDF into text chunks
3. Extract metadata (pages, chunks)
4. Initialize FAISS vector store
5. Embed chunks and add to index
6. Retrieve top relevant chunks via semantic search
7. Analyze with LLM to extract arguments
8. Post-process and rank final results

Returns complete analysis result as JSON.

---

### **Utility Files**

#### `app/utils/embeddings.py`
Text embedding service using Sentence Transformers.
- Loads pre-trained model (default: all-MiniLM-L6-v2)
- Generates normalized vector embeddings
- Supports batch processing
- Returns numpy arrays for FAISS

#### `app/utils/helpers.py`
Helper functions for common operations.

**Functions:**
- `calculate_content_hash(content)` - SHA-256 hash for unique document IDs
- `parse_json_response(response_text)` - Robust JSON parsing from LLM
  - Handles markdown code blocks
  - Extracts JSON from mixed text
  - Multiple fallback strategies
- `clean_text(text)` - Normalizes whitespace

#### `app/utils/validators.py`
Input validation and security checks.

**Functions:**
- `validate_pdf(file)` - Validates PDF files
  - Checks file extension (.pdf)
  - Validates MIME type
  - Verifies PDF magic bytes (%PDF header)
  - Blocks disguised executables (e.g., file.pdf.exe)
- `validate_file_size(file, max_size)` - Enforces size limits
  - Checks file isn't empty
  - Ensures file under max size (50MB default)

---

### **Frontend Files**

#### `app/templates/base.html`
Base HTML template with common layout.
- Header with logo and title
- Main content block for child templates
- Links to CSS and JavaScript files

#### `app/templates/index.html`
Upload page for document submission.
- File upload form (PDF only)
- Custom styled file input with icon
- Submit button with loading state
- Progress bar during analysis
- Error message display area
- "How it works" section with 3 steps

**JavaScript Features:**
- Updates filename on file selection
- Validates file type before submission
- Shows/hides loading indicators
- Sends file to `/api/analyze` endpoint
- Stores results in sessionStorage
- Redirects to results page on success
- Displays error messages on failure

#### `app/templates/results.html`
Results display page showing analysis output.
- Document information card (name, pages, processing time, argument count)
- List of key legal arguments as cards
- Each card shows:
  - Rank number
  - Stance badge (color-coded)
  - Category badge
  - Combined score percentage
  - Summary and importance
  - Supporting quote in blockquote
  - Legal concepts as tags
  - Page references

**JavaScript Features:**
- Loads results from sessionStorage
- Dynamically generates argument cards
- Formats scores as percentages
- Color-codes stance badges
- Handles missing data gracefully

#### `app/static/css/style.css`
Complete application styling.
- Purple gradient background theme
- Card-based responsive layouts
- Modern button styles with hover effects
- Animated progress bar
- Badge color coding:
  - Plaintiff: Green
  - Defendant: Red  
  - Neutral: Blue
  - Category badges: Light blue
  - Concept tags: Yellow
- Smooth transitions and box shadows

#### `app/static/js/main.js`
Frontend utility functions.
- `formatFileSize()` - Converts bytes to human-readable format
- `showToast()` - Optional toast notifications
- Console logging for debugging

---

### **Entry Point**

#### `run.py`
Application entry point for development server.
- Imports Flask app factory from `app/__init__.py`
- Creates app instance
- Runs development server on localhost:5000
- Enables debug mode for development

**Usage:** `python run.py`

---

### **Configuration & Dependencies**

#### `requirements.txt`
Python package dependencies.

**Key Packages:**
- `Flask==3.0.0` - Web framework
- `pydantic==2.5.0` - Data validation
- `pydantic-settings==2.1.0` - Settings management
- `pdfplumber==0.10.3` - PDF text extraction
- `faiss-cpu==1.7.4` - Vector similarity search
- `sentence-transformers==2.7.0` - Text embeddings
- `torch==2.1.0` - Deep learning framework
- `groq==0.4.1` - LLM API client
- `rapidfuzz==3.5.2` - Fuzzy string matching
- `loguru==0.7.2` - Logging
- `gunicorn==21.2.0` - Production WSGI server

#### `.env` File
Environment variables for configuration (not in repository).

**Required:**
```env
GROQ_API_KEY=your-groq-api-key-here
SECRET_KEY=your-secret-key-here
```

**Optional:**
```env
FLASK_ENV=production
DEBUG=False
LLM_MODEL=llama-3.3-70b-versatile
CHUNK_SIZE=1500
CHUNK_OVERLAP=200
TOP_K_RETRIEVAL=60
MAX_CONTENT_LENGTH=52428800
```

---

## 📦 Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Groq API key ([Get one here](https://console.groq.com))

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/arkakran/Legal-Tool.git
cd Legal-Tool
```

**2. Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Create `.env` file**
```bash
# Create .env file in project root
touch .env
```

**5. Add environment variables to `.env`**
```env
GROQ_API_KEY=your-groq-api-key-here
SECRET_KEY=your-secret-key-here
```

Generate SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**6. Run the application**
```bash
python run.py
```

**7. Open browser**
```
http://127.0.0.1:5000
```

---

## ⚙️ Configuration

Configuration is managed in `app/config.py` using Pydantic Settings.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq API key (required) | - |
| `SECRET_KEY` | Flask secret key | Auto-generated |
| `FLASK_ENV` | Environment mode | production |
| `DEBUG` | Debug mode | False |
| `LLM_MODEL` | LLM model name | llama-3.3-70b-versatile |
| `LLM_TEMPERATURE` | LLM temperature | 0.0 |
| `EMBEDDING_MODEL` | Sentence transformer model | all-MiniLM-L6-v2 |
| `EMBEDDING_DEVICE` | CPU or CUDA | cpu |
| `CHUNK_SIZE` | Text chunk size | 1500 |
| `CHUNK_OVERLAP` | Chunk overlap | 200 |
| `TOP_K_RETRIEVAL` | Chunks to retrieve | 60 |
| `TOP_K_RERANKED` | Chunks to rerank | 25 |
| `FINAL_OUTPUT_COUNT` | Final results to return | 10 |
| `UPLOAD_FOLDER` | Upload directory | data/uploads |
| `MAX_CONTENT_LENGTH` | Max file size (bytes) | 52428800 (50MB) |

---

## 🚀 Usage

### Web Interface

1. Navigate to `http://127.0.0.1:5000`
2. Click "Choose PDF file" and select a legal document
3. Click "Analyze Document"
4. Wait 30-60 seconds for processing
5. View ranked legal arguments with page references

### API Usage

**Analyze Document:**
```bash
curl -X POST http://127.0.0.1:5000/api/analyze \
  -F "file=@legal_brief.pdf"
```

**Response Example:**
```json
{
  "document_id": "a3f2c1b9e...",
  "document_name": "legal_brief.pdf",
  "total_pages": 45,
  "total_chunks": 123,
  "processing_time": 42.5,
  "key_points": [
    {
      "final_rank": 1,
      "summary": "Constitutional challenge to statute violates due process",
      "importance": "Core constitutional argument",
      "importance_score": 0.95,
      "stance": "plaintiff",
      "supporting_quote": "The statute violates fundamental rights...",
      "legal_concepts": ["constitutional law", "due process"],
      "page_start": 12,
      "category": "constitutional",
      "combined_score": 0.92
    }
  ]
}
```

**Health Check:**
```bash
curl http://127.0.0.1:5000/api/health
```

---

## 📊 Analysis Pipeline Flow

```
PDF Upload
    ↓
File Validation
    ↓
PDF Parsing & Text Extraction
    ↓
Text Chunking (with overlap)
    ↓
Embedding Generation
    ↓
FAISS Indexing
    ↓
Semantic Search (retrieve relevant chunks)
    ↓
LLM Analysis (extract arguments)
    ↓
Post-Processing (scoring & ranking)
    ↓
Return Top 10 Arguments
```

---

## 🔐 Security Features

-  PDF magic bytes validation
-  MIME type checking
-  File size limits (50MB)
-  Secure filename handling
-  Temporary file cleanup
-  API key validation
-  No sensitive data in error messages

---
