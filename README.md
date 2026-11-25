# 🧠 KnowledgeGraphLLM
### AI-Powered Knowledge Graph Extraction and Analysis System

KnowledgeGraphLLM is a Python-based application that extracts entities and relationships from unstructured text and converts them into interactive Knowledge Graphs using NLP and Graph Theory.

## 🚀 Features
- Entity and relationship extraction
- Coreference resolution
- Knowledge graph generation
- TXT, CSV, and JSON dataset processing
- Interactive graph visualization
- Centrality and PageRank analysis
- Community detection
- Shortest-path analysis
- JSON and GraphML export

## 🛠️ Technologies Used
- **Python** – Core programming
- **Streamlit** – User interface
- **spaCy** – NLP and entity recognition
- **FastCoref** – Coreference resolution
- **NetworkX** – Graph generation and analysis
- **Plotly** – Graph visualization
- **python-louvain** – Community detection
- **Pandas, NumPy, SciPy** – Data processing and computation

## ⚙️ Installation

**1. Clone the repository**
```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd KnowledgeGraphLLM
```

**2. Create and activate virtual environment**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Download spaCy model**
```bash
python -m spacy download en_core_web_sm
```

## ▶️ Run the Application

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

## 🔄 Working Process

1. Input text or upload a dataset.
2. Process text using spaCy and FastCoref.
3. Extract entities and relationships.
4. Generate a Knowledge Graph using NetworkX.
5. Visualize and analyze the graph.
6. Export results in JSON or GraphML format.

## 📁 Project Modules
- `core/` – NLP, entity, relationship, graph, and dataset processing.
- `algorithms/` – Centrality, community detection, and path analysis.
- `visualization/` – Interactive graph visualization.
- `config/` – Project configuration.
- `datasets/` – Input datasets.
- `exports/` – Generated graph files.
- `app.py` – Main Streamlit application.

## 🎯 Applications
- Document analysis
- Knowledge discovery
- Information extraction
- Relationship analysis
- Research and data intelligence

## 👨‍💻 Project Information
**Project:** KnowledgeGraphLLM  
**Domain:** Artificial Intelligence, NLP, and Graph Theory  
**Language:** Python  
**Framework:** Streamlit

