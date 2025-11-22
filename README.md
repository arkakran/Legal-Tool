# ⚖️ Legal Brief Analyzer

AI-powered tool that extracts and ranks key legal arguments from briefs, motions, and court opinions using NLP and LLM technology.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🚀 Features

- **Intelligent Argument Extraction** using Groq LLaMA 3.3
- **Semantic Search** with FAISS vector store
- **Smart Ranking** combining retrieval and importance scores
- **Page-Level Citations** for every argument
- **Universal Document Support** for all legal document types
- **Production-Ready** with secure file handling

## 📋 Prerequisites

- Python 3.9+
- Groq API key ([Get one](https://console.groq.com/))
- 4GB+ RAM

## 🛠️ Installation
```bash
# Clone repository
git clone https://github.com/yourusername/legal-brief-analyzer.git
cd legal-brief-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Add your GROQ_API_KEY and SECRET_KEY to .env
```

## 🎯 Quick Start
```bash
# Development
python run.py

# Production
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 wsgi:app
```

Visit `http://localhost:5000` and upload a legal PDF to analyze.

## 📖 API Usage
```bash
curl -X POST http://localhost:5000/api/analyze \
  -F "file=@path/to/legal-brief.pdf"
```

**Response includes:**
- Ranked legal arguments
- Importance scores
- Page citations
- Legal concepts
- Supporting quotes

## 🔧 Configuration

Edit `.env` file:
```env
SECRET_KEY=your-secret-key-minimum-32-characters
GROQ_API_KEY=your-groq-api-key
LLM_MODEL=llama-3.3-70b-versatile
CHUNK_SIZE=1500
TOP_K_RETRIEVAL=60
FINAL_OUTPUT_COUNT=10
```

## 🏗️ Project Structure
```
legal_brief_analyzer/
├── app/
│   ├── blueprints/      # Routes (main, api)
│   ├── services/        # Core logic (PDF, LLM, vectors)
│   ├── utils/           # Helpers, validators
│   └── templates/       # HTML templates
├── data/uploads/        # Temp file storage
├── requirements.txt
└── run.py
```

## 🔒 Security

- Secure file validation & cleanup
- Environment-based secrets
- File size limits (50MB default)
- Input validation with Pydantic

## 🐛 Troubleshooting
```bash
# NumPy version issues
pip install "numpy<2.0"

# Groq API errors
pip install groq==0.4.1 langchain-groq

# Verify setup
python verify.py
```

## 📊 Performance

- **Processing**: 15-30s for 20-30 page documents
- **Memory**: ~500MB-1GB during processing
- **Scalable**: Stateless design for horizontal scaling

## 📝 License

MIT License - see [LICENSE](LICENSE) file

## 👨‍💻 Author

**Aryan Kakran**
- Email: rnkakran@gmail.com
- GitHub: [@yourusername](https://github.com/yourusername)

## 🙏 Credits

Built with [Groq](https://groq.com/), [FAISS](https://github.com/facebookresearch/faiss), [Flask](https://flask.palletsprojects.com/), and [Sentence Transformers](https://www.sbert.net/)

---

**Built for attorneys and legal professionals** ⚖️