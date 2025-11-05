NeuronIQ AI - Intelligent HR Platform

An AI-powered Human Resources Management System that revolutionizes recruitment and compliance workflows using Azure OpenAI and advanced NLP techniques.

---

Overview

NeuronIQ AI is a cutting-edge HR platform that leverages artificial intelligence to streamline three critical HR workflows:

1. AI Resume Screening - Automatically analyze and rank candidates against job requirements
2. GDPR Compliance Chatbot - Get instant answers about GDPR regulations and AI ethics
3. Job Description Generator - Create professional, structured JDs in seconds

Built with privacy-first principles, all data is processed securely and deleted after use.

---

Features

AI Resume Screening
- Intelligent Matching: AI-powered resume analysis
- Batch Processing: Screen multiple resumes simultaneously
- Custom Criteria: Filter by experience, skills, and preferred organizations
- Detailed Reports: Get comprehensive candidate evaluations with:
  - Match scores (0-100%)
  - Strengths and concerns analysis
  - Skills extraction
  - Recommendation categories (Strong/Good/Moderate/Weak Fit)
- Export Options: Download results as Excel or JSON

GDPR Compliance Chatbot
- RAG Architecture: Retrieval-Augmented Generation using ChromaDB
- Official Sources: Based on EU 2016/679 and 2025 HR-AI guidelines
- Contextual Answers: Citations from relevant GDPR articles
- Real-time Query: Instant responses to compliance questions

Job Description Generator
- Template-Driven: Follows NeuronIQ AI's company culture and tone
- Structured Output: JSON-formatted JDs with:
  - Role overview
  - Key responsibilities
  - Required and preferred skills
  - Employment details
- One-Click Export: Copy to clipboard or download as JSON

---

Tech Stack

 Backend
- Framework: Flask 2.3.0
- AI/ML: 
  - Azure OpenAI 
  - SentenceTransformers (all-MiniLM-L6-v2)
- Vector Database: ChromaDB
- Document Processing: PyPDF2, python-docx
- Data Export: openpyxl

 Frontend
- HTML5/CSS3: Modern, responsive design
- JavaScript: Vanilla JS (no frameworks)
- Design: Netflix-inspired dark theme

 Infrastructure
- Python: 3.8+
- Database: In-memory (MVP) → PostgreSQL/MongoDB (Production)
- Storage: Local filesystem → Cloud storage (Production)

---

Prerequisites

Before installation, ensure you have:

- Python 3.8 or higher
- pip (Python package manager)
- Azure OpenAI API access with:
  - API endpoint
  - API key
  - Deployment name
- Git (for cloning the repository)

Optional:
- Virtual environment tool (venv, virtualenv, conda)
- GDPR PDF documents for chatbot indexing

---

Project Structure

```
neuroniq-ai-hr/
├── app.py                      # Flask application & routes
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (gitignored)           
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
│
├── services/                   # Business logic layer
│   ├── __init__.py
│   ├── gdpr_service.py         # GDPR chatbot with RAG
│   ├── jd_service.py           # Job description generator
│   ├── llm_service.py          # Azure OpenAI integration
│   ├── resume_parser.py        # PDF/DOCX text extraction
│   └── screening_engine.py     # Resume screening orchestration
│
├── utils/                      # Utility functions
│   ├── __init__.py
│   ├── file_handler.py         # File upload handling
│   └── output_generator.py     # Excel/JSON export
│
├── templates/                  # HTML templates
│   ├── index.html              # Landing page
│   ├── screening.html          # Resume screening page
│   ├── results.html            # Screening results
│   ├── gdpr_chatbot.html       # GDPR chatbot interface
│   └── jd_creator.html         # JD generator form
│
├── uploads/                    # Uploaded resumes (gitignored)
├── outputs/                    # Generated reports (gitignored)
├── gdpr_chroma/                # Vector DB storage (gitignored)      