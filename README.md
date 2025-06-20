# 🧠 DBT Model Analyzer with GPT + Lineage

An AI-powered visual dashboard to explore, document, and audit your DBT (Data Build Tool) projects using OpenAI or Azure OpenAI's GPT models.

Built with Streamlit, this tool provides natural-language summaries, lineage graphs, column-level usage, and model metrics — all generated from your DBT project structure and SQL.

---

## 📌 Table of Contents

- [✨ Features](#-features)
- [🚀 Live Demo](#-live-demo)
- [🚀 Demo Preview](#-demo-preview)
- [📂 Project Structure](#-project-structure)
- [⚙️ Setup Instructions](#️-setup-instructions)
- [🧠 How GPT is Used](#-how-gpt-is-used)
- [📁 Supported Input Types](#-supported-input-types)
- [💡 Use Cases](#-use-cases)
- [📤 Export Capabilities](#-export-capabilities)
- [🛠 Tech Stack](#-tech-stack)
- [🪪 License](#-license)
- [🙌 Acknowledgements](#-acknowledgements)

---

## ✨ Features

| Feature Category         | Description                                                                 |
|--------------------------|-----------------------------------------------------------------------------|
| 📄 GPT Model Summarizer   | Generate GPT-based explanations of each DBT model                           |
| 📊 Lineage Graph          | Interactive visual DAG of `ref()` relationships                             |
| 🌳 Ref Tree Explorer      | Explore upstream/downstream dependencies per model                          |
| 📁 Folder Summary         | GPT summary of entire folders (e.g. staging, marts, reporting)              |
| 📋 Model Metadata Table   | View description, columns, references for all models                        |
| 🔍 Search Tool            | Search by column name, model name, or SQL content                           |
| 🧬 Column Lineage Viewer  | Trace how each column is used across your DBT project                       |
| 🧭 Categorization Viewer  | Categorize models as staging, dim, fact, or other based on prefix           |
| 📈 Complexity Analyzer    | Auto-classify models based on size and reference depth                      |
| 📤 Export Options         | Export GPT summaries, lineage graphs, and metrics                           |

---


## 🚀 Live Demo

🌐 [Try it on Streamlit Cloud](https://genai-dbt-model-analyzer.streamlit.app/)  

---


## 🚀 Demo Preview
![genai_document_gif](https://github.com/user-attachments/assets/cbb73204-81b5-4444-a4cb-bdaee94fda6a)


---

## 📂 Project Structure

```bash
dbt-model-analyzer/
├── app.py                   # Main Streamlit app
├── config.json              # LLM config file
├── requirements.txt         # Python dependencies
├── screenshots/             # UI screenshots (optional)
└── README.md
```

---

## 📁 Supported Input Types

| Input Type        | Description                                      |
|-------------------|--------------------------------------------------|
| 📁 ZIP File Upload | Upload your DBT project as a `.zip` archive      |
| 🌐 GitHub Clone    | Clone any public GitHub repo containing DBT code |

---

## 💡 Use Cases

- 🧠 Understand unfamiliar DBT models and folders
- 🗂 Auto-document large legacy DBT projects
- 🔍 Trace where each column is used
- 📈 Find complex models with too many refs or lines
- 📊 Export summaries for reporting or onboarding
- 📁 Explore staging vs mart models folder by folder

---

## 📤 Export Capabilities

| Type               | Format         |
|--------------------|----------------|
| GPT Summaries      | `.md`          |
| Lineage Graph      | `.html`        |
| Model Metadata     | `.csv` or table |
| Column Lineage     | `.csv` or table |
| Complexity Metrics | DataFrame view |

---

## 🛠 Tech Stack

- **Streamlit** – frontend dashboard framework  
- **OpenAI Python SDK** – GPT-3.5/4 integrations  
- **PyVis** – interactive visual DAGs and networks  
- **NetworkX** – lineage and DAG graph construction  
- **YAML / Pandas / Regex** – model and metadata parsing
