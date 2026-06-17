---
title: Research Paper Recommender
emoji: 📚
colorFrom: indigo
colorTo: blue
sdk: streamlit
sdk_version: 1.35.0
python_version: "3.11"
app_file: app.py
pinned: false
license: mit
tags:
- research
- nlp
- sentence-transformers
- semantic-search
---

# 📚 Research Paper Recommender

> *An AI-powered semantic search engine that helps researchers find the most relevant papers from their library based on what they are writing.*

[![Open in Spaces](https://img.shields.io/badge/🤗-Open%20in%20Spaces-blue)](https://huggingface.co/spaces/ShetyeRupa/research-paper-recommender)
[![Streamlit](https://img.shields.io/badge/Powered%20by-Streamlit-FF4B4B)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🚀 Live Demo

The application is deployed on Hugging Face Spaces:

🔗 **Live URL:** https://huggingface.co/spaces/ShetyeRupa/research-paper-recommender

## 🎯 Problem Statement

Graduate students and researchers waste hours searching their own paper libraries for relevant citations. They know a paper exists. They have read it. But when writing mid-paragraph, they cannot retrieve it. This leads to:

- ⏱️ **Hours lost** searching through folders and reference managers
- 📝 **Missed citations** that weaken literature reviews
- ❌ **Mentor rejections** due to incomplete references
- 🎓 **Delayed graduation** from repeated revisions

**Our solution:** An intelligent paper recommender that reads your writing and instantly surfaces the most semantically relevant papers from your library.

---

## ✨ Features

| Feature | Description |
|:---|:---|
| 🔍 **Semantic Search** | Uses Sentence-BERT embeddings to understand meaning, not just keywords |
| 📄 **PDF Processing** | Extract text from research papers automatically |
| 🎯 **Relevance Scoring** | Each recommendation includes 0-100% similarity score |
| 👩‍💻 **Human-in-the-Loop** | Users control which papers to cite |
| 🚩 **Flag Bad Recommendations** | Provide feedback to improve the system |
| ⚠️ **Confidence Threshold** | Silent failure mitigation when no strong matches found |
| 📋 **Export Citations** | Download cited papers as formatted text |
| 💾 **Persistent Library** | Your uploaded papers saved between sessions |

---

## 🏗️ Architecture

```
[PDF Upload] → [Text Extractor] → [Section Segmenter] → [Output]
                                                              ↓
[Writing Section] → [Embedding Generator] → [Similarity Calculator] ← [Library Cache]
```

### AI Model Selection

| Component | Choice | Rationale |
|:---|:---|:---|
| **Embedding Model** | `all-MiniLM-L6-v2` (Sentence-BERT) | 384-dim, CPU-friendly, 0.5s per 100 papers |
| **Similarity Search** | FAISS (IndexFlatIP) | Cosine similarity after L2 normalization |
| **PDF Extraction** | pdfplumber + PyPDF2 | Dual fallback for maximum compatibility |

### Why Semantic Similarity Over Keyword Search?

| Approach | Limitation | Our Solution |
|:---|:---|:---|
| **BM25 / TF-IDF** | Fails on synonymy ("attention mechanism" ≈ "transformer self-attention") | Dense embeddings map semantically similar texts close together |
| **Keyword Matching** | Cannot distinguish methods vs. discussion relevance | Section-aware embedding generation |

---

### Try These Example Queries

```
How does congestion pricing affect taxi ridership and traffic safety in urban areas?
```

```
What are the best practices for extracting destination hotspots from taxi trajectory data?
```

```
How can reinforcement learning be used to optimize driver revenue in ride-on-demand services?
```

---

## 🛠️ Tech Stack

| Category | Technologies |
|:---|:---|
| **Frontend** | Streamlit |
| **AI/ML** | Sentence-BERT, FAISS, Transformers |
| **PDF Processing** | pdfplumber, PyPDF2 |
| **Data Processing** | NumPy, Pandas |
| **Deployment** | Hugging Face Spaces |

---

## 📦 Installation (Local Development)

### Prerequisites

- Python 3.11 or higher
- pip or conda

### Setup

```bash
# Clone the repository
git clone https://github.com/ShetyeRupa/research-paper-recommender.git
cd research-paper-recommender

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Using Conda

```bash
conda create --name paper_recommender python=3.11 -y
conda activate paper_recommender
conda install -c conda-forge streamlit sentence-transformers pypdf2 pdfplumber numpy pandas faiss-cpu pytorch -y
pip install huggingface-hub
streamlit run app.py
```

---

## 🧪 Evaluation Metrics

| Metric | Target | Achieved |
|:---|:---|:---|
| **Recall@5** | >0.70 | Validated on held-out test set |
| **Precision@5** | >0.65 | Validated on held-out test set |
| **Latency (p95)** | <3 seconds | ~1.5s per query on CPU |

---

## 🤖 Responsible AI

Every AI system has risks. Our mitigations:

| Risk | Mitigation |
|:---|:---|
| **Over-reliance** | Warning message: "AI may miss papers. Always verify." |
| **Missing relevant papers** | Similarity scores displayed; user can search manually |
| **Domain drift (new terminology)** | Weekly re-embedding + manual keyword override |
| **Silent failure** | Confidence threshold (below 0.5 triggers "No strong matches found") |
| **User bias** | Flagging system collects feedback for improvement |

### Human-in-the-Loop Design

- ✅ User decides which papers to cite
- ✅ Similarity scores displayed with every recommendation
- ✅ Confidence threshold filter (adjustable by user)
- ✅ Flag bad recommendations to improve the system
- ✅ Export citations for verification

---

## 📁 Project Structure

```
research_paper_recommender/
├── app.py                 # Streamlit web application
├── recommender.py         # Core AI engine (Sentence-BERT + FAISS)
├── pdf_processor.py       # PDF text extraction and section parsing
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── Dockerfile             # Container configuration (optional)
```

---

## 👥 Team

| Role | Name |
|:---|:---|
| **AI Engineer** | Rupali Shetye |
| **Backend Developer** | Kartavya |

**Track:** Graduate

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **USAII®** for organizing the Global AI Hackathon 2026
- **Sentence-BERT** team for the embedding model
- **FAISS** team for efficient similarity search
- **Streamlit** for making ML app deployment seamless

---

## 📧 Contact

For questions or feedback:
- **Email:** shetyerupa93@gmail.com
- **Project Repository:** [https://github.com/ShetyeRupa/research-paper-recommender.git]

---

## 🔧 Troubleshooting

| Issue | Solution |
|:---|:---|
| `ModuleNotFoundError: No module named 'torchvision'` | Install: `pip install torchvision` |
| FAISS import error | Use conda: `conda install -c conda-forge faiss-cpu` |
| PDF text extraction empty | Ensure PDF is text-based (not scanned image) |
| Slow performance on first run | Model downloads on first load; subsequent runs are cached |

---

## 🗺️ Roadmap

- [ ] Integration with Zotero/Mendeley APIs
- [ ] Multi-language paper support
- [ ] Collaborative library sharing
- [ ] Citation graph visualization
- [ ] Browser extension for direct PDF import

---

**Built with ❤️**
