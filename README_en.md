# Security Research Paper Collection and Processing Project

## Project Overview
This project is designed to collect research paper data from top-tier cybersecurity conferences, perform structured processing, and apply intelligent labeling. It supports the following features:
1. Multi-source web crawlers to fetch conference paper metadata.
2. Cleaning of paper data from Excel files and conversion to JSON format.
3. LLM-based paper keyword extraction and automatic classification.

## File Structure

├── web_of_science/          # Web of Science Data Processing Module
│   ├── webofscience_paper_extract_*.py
│   └── labels.txt           # Main classification system file
├── 4_security_top_conference/
│   ├── labels.txt           # Modified classification system
│   └── paper_collect/       # Scrapy crawler project
└── Output Files:
    ├── *.json               # Raw paper data
    ├── *_keywords.json      # Data with keyword annotations
    └── *_keywords_only.json # Keyword-only data snapshot

    
## Functional Modules
### 1. Web Crawling Module
Includes data collectors for the following conferences:
- `css_papers.py` - Collects CCS conference papers from DBLP.
- `usenix_papers.py` - Collects USENIX Security conference papers.
- `ndss_papers.py` - Collects NDSS conference papers.
- `aaai_papers.py` - Collects security-related papers from AAAI conference.

### 2. Data Processing Module
- `webofscience_paper_extract_*.py`
  - Supports converting CCS/SP conference Excel files exported from Web of Science to JSON format.
  - Extracts fields: Title, Authors, Abstract, Year, DOI.

### 3. Intelligent Labeling Module
- `llm_labels.py/llm4_labels.py`
  - Uses Qwen Large Language Model (LLM) to automatically generate paper keywords.
  - Automatically matches them against the cybersecurity classification system (see `labels.txt`).
  - Supports two model versions: qwen-plus and qwen3.

### 4. Classification System File
- `labels.txt` defines 9 core security domains and their subcategories:
  - Cyberspace Theory
  - Cryptography and Applications
  - Network and System Security
  - Information Content Security
  - Security of Emerging Information Technologies
  - Data Security and Privacy
  - Artificial Intelligence Security
  - Blockchain Security
  - Internet of Things (IoT) Security

## Dependencies
```bash
pip install scrapy pandas langchain langchain-community openpyxl tqdm
```

## Usage Guide
### 1. Data Collection
```bash
# Run crawlers (Example: Collect USENIX papers)
cd paper_collect
scrapy crawl usenix -o usenix_papers.json
```
Alternatively, convert Excel files exported from Web of Science to JSON format:
```bash
# Run data processing scripts
python webofscience_paper_extract_ccs.py
python webofscience_paper_extract_sp.py
```

### 2. Intelligent Labeling
```bash
# Configure API Key (modify llm_labels.py)
export TONGYI_API_KEY=your_api_key

# Execute keyword extraction (select the appropriate input file)
python llm_labels.py  # Process SP24.json
python llm4_labels.py  # Process usenix_papers.json
```

## Notes
- **API Configuration**: A valid Tongyi API key must be configured in `llm_labels.py` and `llm4_labels.py`.
- **Path Configuration**: Ensure the input file path matches `INPUT_PAPERS_FILE` in the scripts.
- **Model Selection**: Choose the appropriate Qwen version (qwen-plus or qwen3) based on your needs, or modify the code to use other AI models.
- **Classification Updates**: If extending the classification system, `labels.txt` in both relevant directories must be updated accordingly.
- **Data Cleaning**: Raw crawled data, especially author fields, may require manual verification and formatting.