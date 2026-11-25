<<<<<<< HEAD
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
=======
# KnowledgeGraphLLM

An AI-powered Knowledge Graph Extraction and Analysis System that transforms unstructured text into structured knowledge graphs using Natural Language Processing (NLP), coreference resolution, graph algorithms, and interactive visualization.

## Overview

KnowledgeGraphLLM extracts entities and relationships from text, resolves references, builds knowledge graphs, and analyzes connections between entities.

The system uses locally running NLP models instead of external AI APIs, making it suitable for offline processing after the required models and dependencies have been downloaded.

## Features

- **Entity Extraction:** Identifies people, organizations, locations, dates, and other entities.
- **Relation Extraction:** Extracts relationships between entities using grammatical analysis and custom rules.
- **Coreference Resolution:** Resolves pronouns and references using FastCoref.
- **Knowledge Graph Generation:** Creates directed multigraphs using NetworkX.
- **Dataset Processing:** Supports TXT, CSV, and JSON files.
- **Interactive Visualization:** Visualizes entities and relationships using Plotly.
- **Graph Analysis:** Degree Centrality, Betweenness Centrality, Closeness Centrality, and PageRank.
- **Community Detection:** Identifies related groups using the Louvain algorithm.
- **Shortest Path Analysis:** Finds connections between entities.
- **Graph Export:** Supports JSON and GraphML formats.
- **Offline Processing:** Uses local NLP models without external API calls.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core development |
| Streamlit | Web interface |
| spaCy | NLP and entity recognition |
| FastCoref | Coreference resolution |
| NetworkX | Knowledge graph construction and analysis |
| Plotly | Interactive graph visualization |
| python-louvain | Community detection |
| Pandas | Dataset processing |

## System Architecture

```text
Input Text / Dataset
        |
        v
    NLP Engine
      (spaCy)
        |
        v
Coreference Resolution
    (FastCoref)
        |
        v
 Entity Extraction
        |
        v
Relation Extraction
        |
        v
Knowledge Graph Builder
     (NetworkX)
        |
        v
Graph Visualization
      (Plotly)
        |
        v
Graph Analysis & Export
```

## Graph Algorithms

- Degree Centrality
- Betweenness Centrality
- Closeness Centrality
- PageRank
- Louvain Community Detection
- Shortest Path Analysis (BFS for unweighted graphs)

## Supported Dataset Formats

- TXT
- CSV
- JSON

## Project Structure

```text
KnowledgeGraphLLM/
├── app.py
├── config/
├── core/
├── algorithms/
├── visualization/
├── datasets/
│   ├── raw/
│   ├── processed/
│   └── samples/
├── exports/
├── models/
├── tests/
├── requirements.txt
└── README.md
```

## Installation

### 1. Clone the repository

>>>>>>> 86e057bb8820c8a108d5c66e4fdb2ab06b801988
```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd KnowledgeGraphLLM
```

<<<<<<< HEAD
**2. Create and activate virtual environment**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**3. Install dependencies**
=======
### 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

>>>>>>> 86e057bb8820c8a108d5c66e4fdb2ab06b801988
```bash
pip install -r requirements.txt
```

<<<<<<< HEAD
**4. Download spaCy model**
=======
### 4. Download the spaCy model

>>>>>>> 86e057bb8820c8a108d5c66e4fdb2ab06b801988
```bash
python -m spacy download en_core_web_sm
```

<<<<<<< HEAD
## ▶️ Run the Application
=======
FastCoref's pretrained model weights are downloaded during initial model setup/use if not already available locally.

### 5. Run the application
>>>>>>> 86e057bb8820c8a108d5c66e4fdb2ab06b801988

```bash
streamlit run app.py
```

<<<<<<< HEAD
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

=======
Open the application in your browser:

```text
http://localhost:8501
```

## How It Works

1. Input text or upload a dataset.
2. The NLP engine processes the text.
3. Coreference resolution identifies references to previously mentioned entities.
4. Entities and relationships are extracted.
5. A knowledge graph is constructed.
6. The graph is visualized interactively.
7. Graph algorithms analyze entity importance, communities, and paths.
8. The graph can be exported as JSON or GraphML.

## Applications

- Knowledge discovery
- Information extraction
- Document analysis
- Relationship analysis
- Research data exploration
- Entity network analysis

## Project Information

**Project:** KnowledgeGraphLLM  
**Category:** Artificial Intelligence / Natural Language Processing / Graph Analytics  
**Language:** Python

---

*Developed as an AI-powered system for automated knowledge extraction, graph generation, and relationship analysis.*
>>>>>>> 86e057bb8820c8a108d5c66e4fdb2ab06b801988
