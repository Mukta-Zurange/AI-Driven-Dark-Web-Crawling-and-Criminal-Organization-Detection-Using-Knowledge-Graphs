# AI-Driven Dark Web Crawling and Criminal Organization Detection Using Knowledge Graphs

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0-green.svg)](https://www.mongodb.com/)
[![Tor](https://img.shields.io/badge/Tor-SOCKS5-purple.svg)](https://www.torproject.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **B.E. Information Technology Final Year Project**  
> Pune Vidyarthi Griha's College of Engineering, Technology and Management (PVGCOET), Pune  
> Academic Year 2026–27

## Overview

A unified, end-to-end pipeline that crawls `.onion` sites on the Tor network, extracts external identifiers, classifies pages by crime type using both traditional ML and Agentic AI (LLM-based reasoning), constructs a knowledge graph linking domains to operators, and clusters connected websites into criminal organizations — all surfaced through an interactive Streamlit dashboard.

**Key Contribution:** Unlike existing systems that solve individual stages (crawling OR classification OR clustering), this project unifies all stages into a single, continuously operating investigative platform with agentic verification of low-confidence clusters.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PIPELINE OVERVIEW                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐    ┌───────────┐    ┌──────────┐    ┌─────────────┐  │
│  │ Tor BFS  │───>│ Identifier│───>│ MongoDB  │───>│    ML       │  │
│  │ Crawler  │    │ Extractor │    │ Storage  │    │ Classifier  │  │
│  │(SOCKS5)  │    │ (7 types) │    │(5 colls) │    │(TF-IDF+RF)  │  │
│  └──────────┘    └───────────┘    └──────────┘    └──────┬──────┘  │
│                                                          │         │
│  ┌──────────────┐    ┌──────────┐    ┌──────────┐        │         │
│  │  Streamlit   │<───│ Org      │<───│Knowledge │<───────┘         │
│  │  Dashboard   │    │ Detector │    │  Graph   │                  │
│  │  (6 pages)   │    │(UnionFind│    │(NetworkX)│   ┌──────────┐   │
│  └──────────────┘    │+Jaccard) │    └──────────┘   │ Agentic  │   │
│                      │+Agentic  │<──────────────────│Classifier│   │
│                      │ Verify)  │                   │(Claude/  │   │
│                      └──────────┘                   │ Groq)    │   │
│                                                     └──────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## Features

- **Tor BFS Crawler** — Breadth-first crawling over SOCKS5 proxy with configurable `max_depth` (default 2), respecting rate limits and handling Tor circuit failures
- **7-Type Identifier Extraction** — Email, Telegram, Twitter/X, Bitcoin (BTC), Monero (XMR), PGP public keys, Tox IDs
- **Dual Classification** — Comparative ML (TF-IDF + Random Forest / SVM / Logistic Regression / Naive Bayes) vs. Agentic AI (Claude / Groq LLM-based reasoning)
- **Knowledge Graph** — Domain → Subdomain → Identifier graph with centrality metrics (degree, betweenness, PageRank)
- **Union-Find Clustering** — Groups domains sharing identifiers; validates with Jaccard HTML similarity (threshold ≥ 0.77)
- **Agentic Verification** — LLM reasons about ambiguous clusters that fall below the similarity threshold
- **Interactive Dashboard** — 6-page Streamlit app: Overview, Knowledge Graph, Organizations, Search, Alerts, Reports

## Project Structure

```
dark_web_project/
│
├── config.py                          # Central configuration (Tor, MongoDB, regex, categories)
├── run_pipeline.py                    # CLI to run all 7 stages or individual steps
├── requirements.txt                   # Python dependencies
├── README.md
│
├── crawler/
│   └── tor_crawler.py                 # BFS crawler through Tor SOCKS5 proxy
│
├── extractor/
│   └── identifier_extractor.py        # Regex-based extraction of 7 identifier types
│
├── preprocessing/
│   └── preprocessor.py                # HTML stripping, tokenization, stopword removal
│
├── classifier/
│   ├── ml_classifier.py               # TF-IDF + scikit-learn (RF/SVM/LR/NB)
│   └── agentic_classifier.py          # Claude/Groq API LLM classification
│
├── knowledge_graph/
│   └── graph_builder.py               # NetworkX graph construction + centrality
│
├── clustering/
│   ├── union_find.py                  # Union-Find data structure
│   └── organization_detector.py       # Clustering + HTML similarity validation
│
├── verification/
│   └── agentic_verifier.py            # LLM-based verification of ambiguous clusters
│
├── dashboard/
│   └── app.py                         # 6-page Streamlit dashboard
│
├── database/
│   └── mongo_handler.py               # MongoDB CRUD (5 collections)
│
└── utils/
    └── helpers.py                     # CSV/JSON export + report generation
```

## Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.10+ | Runtime |
| Tor | Latest | Anonymous crawling via SOCKS5 proxy |
| MongoDB | 7.0+ | Data storage (5 collections) |
| Ubuntu | 22.04+ | Recommended OS (or any Linux with Tor) |

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/dark-web-criminal-network-detection.git
cd dark-web-criminal-network-detection
```

### 2. Set up Python environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Install and start Tor

```bash
sudo apt install -y tor
sudo systemctl start tor
sudo systemctl enable tor

# Verify SOCKS5 proxy is listening
ss -tlnp | grep 9050
```

### 4. Install and start MongoDB

```bash
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor

echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

sudo apt update && sudo apt install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod
```

### 5. Configure API keys (for Agentic AI)

Create a `.env` file in the project root:

```env
ANTHROPIC_API_KEY=your_claude_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

## Usage

### Run the full pipeline

```bash
python run_pipeline.py --all
```

### Run individual stages

```bash
python run_pipeline.py --crawl              # Stage 1: Crawl .onion sites
python run_pipeline.py --extract            # Stage 2: Extract identifiers
python run_pipeline.py --preprocess         # Stage 3: Preprocess text
python run_pipeline.py --classify-ml        # Stage 4: ML classification
python run_pipeline.py --classify-agentic   # Stage 5: Agentic AI classification
python run_pipeline.py --build-graph        # Stage 6: Build knowledge graph
python run_pipeline.py --detect-orgs        # Stage 7: Detect organizations
```

### Launch the dashboard

```bash
streamlit run dashboard/app.py
```

The dashboard opens at `http://localhost:8501` with 6 pages:

| Page | Description |
|------|-------------|
| **Overview** | Pipeline stats, crawl progress, classification summary |
| **Knowledge Graph** | Interactive graph visualization (Plotly) |
| **Organizations** | Detected clusters with confidence scores |
| **Search** | Query by domain, identifier, or crime category |
| **Alerts** | High-confidence criminal organizations flagged |
| **Reports** | Export investigation reports (CSV/JSON/PDF) |

## MongoDB Schema

The project uses 5 collections in a database named `dark_web_db`:

| Collection | Key Fields | Purpose |
|------------|-----------|---------|
| `crawled_pages` | url, html, timestamp, depth, status | Raw crawled HTML content |
| `identifiers` | page_url, type, value, normalized | Extracted identifiers (7 types) |
| `classifications` | page_url, ml_label, agentic_label, confidence | Crime category labels |
| `graph_data` | source, target, edge_type, weight | Knowledge graph edges |
| `organizations` | cluster_id, domains, identifiers, confidence | Detected organizations |

## Crime Categories

Pages are classified into one of the following categories:

| Category | Description |
|----------|-------------|
| Drugs | Drug marketplaces and listings |
| Hacking | Hacking tools, services, tutorials |
| Fraud | Financial fraud, carding, scams |
| Weapons | Arms trading and sales |
| Counterfeit | Fake documents, currency |
| Violence | Hired violence, threats |
| Leaked Data | Data dumps, credential leaks |
| Other Illegal | Miscellaneous illegal activity |
| Legitimate | Legal content (forums, privacy tools) |

## Configuration

All settings are centralized in `config.py`:

```python
# Tor SOCKS5 Proxy
TOR_PROXY = "socks5h://127.0.0.1:9050"

# Crawler settings
MAX_DEPTH = 2
MAX_PAGES = 500
REQUEST_TIMEOUT = 60
CRAWL_DELAY = 2  # seconds between requests

# MongoDB
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "dark_web_db"

# Clustering
JACCARD_THRESHOLD = 0.77

# Seed URLs (dark web search engines)
SEED_URLS = [
    "http://torch...",   # Torch search engine
    "http://ahmia...",   # Ahmia search engine
]
```

## Methodology

### Stage 1: Data Acquisition
BFS crawler traverses `.onion` sites through Tor's SOCKS5 proxy, starting from seed URLs obtained from dark web search engines (Torch, Ahmia). The crawler saves raw HTML and follows outbound `.onion` links up to `max_depth=2`.

### Stage 2: Identifier Extraction
Regex patterns extract 7 types of external identifiers from page HTML. Identifiers are normalized (case folding, whitespace removal, canonical formatting) before storage.

### Stage 3: ML Classification
Text is preprocessed (HTML stripping → tokenization → stopword removal → TF-IDF vectorization). Four models are trained and the best by F1-score is selected.

### Stage 4: Agentic AI Classification
Page content is sent to an LLM (Claude or Groq) with structured prompts. The model returns a JSON classification with category, confidence, and reasoning.

### Stage 5: Knowledge Graph
A NetworkX graph is built where domains are root nodes, identifiers attach to domains, and shared identifiers create cross-domain edges. Centrality metrics identify key nodes.

### Stage 6: Organization Detection
Union-Find groups domains sharing identifiers. Jaccard HTML similarity (≥ 0.77) validates clusters. Clusters below the threshold are sent to the agentic verifier for LLM-based reasoning.

## Results

| Metric | Value |
|--------|-------|
| Pages crawled | — |
| Identifiers extracted | — |
| ML best model (F1) | — |
| Organizations detected | — |
| Avg. cluster confidence | — |

> Results will be populated after full pipeline execution on live data.

## Team

| Name | Role |
|------|------|
| **Mukta Zurange** | Team Member |
| **Avyay Joshi** | Team Member |
| **Anushka Nilakh** | Team Member |
| **Sakshi Kapase** | Team Member |

**Project Guide:** Prof. S.G. Kamble  
**Department:** Information Technology, PVGCOET, Pune

## References

1. AlKhatib & Basheer, "Crawling the Dark Web: A Conceptual Review," IEEE CSDE, 2019.
2. Koloveas et al., "Crawler for Clear/Social/Dark Web IoT Threat Intelligence," IEEE Access, 2019.
3. Xu et al., "Dark Web Monitoring Crawler on TOR," IEEE ICDCN, 2021.
4. Nair et al., "Template Clustering for Dark Web Analysis," IEEE BigData, 2021.
5. Alaidi et al., "Dark Web Illegal Activity Crawling and Classifying Using Data Mining," IJAAS, 2022.
6. Cascavilla et al., "Illicit Darkweb Classification via NLP," Elsevier ESWA, 2022.
7. Rajawat et al., "Dark Web Data Classification Using Neural Network," Comp. Electr. Eng., 2022.
8. Shin et al., "Dark Web Classification via TextCNN and Topic Modeling," IEEE Access, 2024.
9. Rahman et al., "Hybrid TF-IDF + RNN Multi-Label Classification," MDPI, 2023.
10. Pastor-Galindo et al., "Big Data Architecture for Dark Web Site ID," Cluster Computing, 2024.
11. Pete et al., "SNA of Six Dark Web Forums," IEEE EuroS&PW, 2020.
12. Nazah et al., "Unsupervised Model for Dark Web Forums," Concurrency & Comp., 2021.
13. Nikoletos & Raftopoulou, "SNA Applied to Dark Web Communities," 2022.
14. Yang et al., "Dark Web Clusters via Temporal Coherence," USENIX, 2011.
15. Zheng et al., "Hidden Buyer ID via Dirichlet Hawkes Process," IEEE TKDE, 2021.
16. Kang & Kim, "Criminal Networks via External Identifier Clustering," IEEE Access, vol. 14, 2026.

## License

This project is developed for academic purposes as part of the B.E. IT curriculum at PVGCOET, Pune.

## Disclaimer

This project is intended **strictly for academic research and educational purposes**. The tools developed are designed to aid law enforcement and cybersecurity researchers in understanding criminal networks on the dark web. **Do not use this software for any illegal activity.** The authors are not responsible for any misuse of the tools or techniques described herein.
