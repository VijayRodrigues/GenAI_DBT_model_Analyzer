# 🧠 DBT Model Analyzer with GPT + Lineage

An AI-powered visual dashboard to explore, document, and audit your DBT (Data Build Tool) projects using OpenAI or Azure OpenAI's GPT models.

Built with Streamlit, this tool provides natural-language summaries, lineage graphs, column-level usage, and model metrics — all generated from your DBT project structure and SQL.

---

## 📌 Table of Contents

- [✨ Features](#-features)
- [📸 Screenshots](#-screenshots)
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

## 📸 Screenshots

| Lineage Graph                     | Column Usage Viewer                |
|----------------------------------|------------------------------------|
| ![lineage](screenshots/lineage.png) | ![columns](screenshots/columns.png) |

---

## 📂 Project Structure

```bash
dbt-model-analyzer/
├── app.py                   # Main Streamlit app
├── config.json              # LLM config file
├── requirements.txt         # Python dependencies
├── screenshots/             # UI screenshots (optional)
└── README.md
