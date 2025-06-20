import streamlit as st
import os, glob, yaml, json, re, shutil
import tempfile, zipfile, subprocess
from openai import OpenAI
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import pandas as pd

st.set_page_config(page_title="DBT Model Analyzer", layout="wide")
st.title("📊 DBT Model Analyzer with GPT + Lineage")

# Load config from secrets
try:
    config = {
        "provider": st.secrets["provider"],
        "api_key": st.secrets["api_key"],
        "api_base": st.secrets.get("api_base", None),
        "deployment_name": st.secrets.get("deployment_name", "gpt-3.5-turbo")
    }
except Exception:
    st.error("❌ Missing secrets. Please check your `.streamlit/secrets.toml` or Streamlit Cloud settings.")
    st.stop()

# Configure OpenAI client
openai.api_key = config["api_key"]
if config["provider"] == "azure":
    openai.api_base = config["api_base"]
    openai.api_type = "azure"
    openai.api_version = "2023-05-15"

source_type = st.sidebar.radio("Choose Project Source", ["📁 Upload ZIP", "🌐 GitHub Repo"])
folder = None

if source_type == "📁 Upload ZIP":
    zip_file = st.sidebar.file_uploader("Upload DBT Project ZIP", type=["zip"])
    if zip_file:
        tmpdir = tempfile.mkdtemp()
        with open(os.path.join(tmpdir, "dbt.zip"), "wb") as f:
            f.write(zip_file.read())
        with zipfile.ZipFile(os.path.join(tmpdir, "dbt.zip")) as z:
            z.extractall(tmpdir)
        contents = [os.path.join(tmpdir, d) for d in os.listdir(tmpdir)]
        subdirs = [d for d in contents if os.path.isdir(d)]
        folder = subdirs[0] if len(subdirs) == 1 else tmpdir
        st.success("✅ ZIP extracted successfully")
        st.text_input("Extracted Path", value=folder, disabled=True)

elif source_type == "🌐 GitHub Repo":
    github_url = st.sidebar.text_input("Paste Public GitHub Repo URL")
    if github_url and st.sidebar.button("Clone Repo"):
        tmpdir = tempfile.mkdtemp()
        try:
            subprocess.run(["git", "clone", github_url, tmpdir], check=True)
            folder = tmpdir
            st.success("✅ Repo cloned successfully")
            st.text_input("Cloned Path", value=folder, disabled=True)
        except Exception as e:
            st.error(f"❌ Clone failed: {e}")

# Continue if folder is set
if folder:
    all_sql_files = glob.glob(os.path.join(folder, "**", "*.sql"), recursive=True)
    folder_map = {}
    for file in all_sql_files:
        rel_folder = os.path.relpath(os.path.dirname(file), folder)
        folder_map.setdefault(rel_folder, []).append(file)

    if not folder_map:
        st.warning("⚠️ No SQL models found.")
        st.stop()

    selected_folder = st.sidebar.selectbox("📂 Select DBT Folder to Analyze", list(folder_map.keys()))
    selected_folder_path = os.path.join(folder, selected_folder)

    sql_files = glob.glob(os.path.join(selected_folder_path, "**", "*.sql"), recursive=True)
    yml_files = glob.glob(os.path.join(selected_folder_path, "**", "*.yml"), recursive=True)

    yml_meta = {}
    for yml in yml_files:
        try:
            with open(yml) as f:
                data = yaml.safe_load(f)
                for m in data.get("models", []):
                    yml_meta[m["name"]] = {
                        "description": m.get("description", ""),
                        "columns": {c["name"]: c.get("description", "") for c in m.get("columns", [])}
                    }
        except: continue

    sql_map = {}
    model_refs = {}
    ref_graph = nx.DiGraph()

    for path in sql_files:
        name = os.path.splitext(os.path.basename(path))[0]
        sql = open(path).read()
        refs = re.findall(r"ref\\(['\"](.*?)['\"]\\)", sql)
        sql_map[name] = sql
        model_refs[name] = refs
        for r in refs:
            ref_graph.add_edge(r, name)

    summaries = {}

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
    "📄 Summaries", "📊 Lineage Graph", "🧬 Column Info", "📋 Model Table",
    "🧭 Categorization", "🔍 Search", "🌳 Ref Tree", "📤 Export & Complexity",
    "🧬 Column Lineage", "📁 Folder Summary"
    ])

    with tab1:
        st.markdown("### 🧠 Summarize Selected Models")
        selected_models = st.multiselect("Choose models to summarize:", list(sql_map.keys()))
        if selected_models and st.button("Run GPT Summarization"):
            for name in selected_models:
                sql = sql_map[name]
                refs = model_refs.get(name, [])
                meta = yml_meta.get(name, {})
                prompt = f"""You are a data engineer.
Model: {name}
SQL:
{sql}
Refs: {', '.join(refs)}
Metadata: {meta}
Explain its purpose, logic, and output structure."""
                st.markdown(f"### 🧩 `{name}`")
                with st.spinner("Summarizing..."):
                    try:
                        res = openai.ChatCompletion.create(
                            model=config["deployment_name"] if config["provider"] == "azure" else "gpt-3.5-turbo",
                            messages=[{"role": "user", "content": prompt}]
                        )
                        text = res.choices[0].message.content
                        st.markdown(text)
                        summaries[name] = text
                    except Exception as e:
                        st.error(f"Error in `{name}`: {e}")
        elif not selected_models:
            st.info("Please select one or more models to summarize.")

    with tab2:
        st.markdown("### 📊 DBT Lineage Graph")

        net = Network(height="600px", directed=True)
        added_nodes = set()

        for path in sql_files:
            with open(path, "r") as f:
                sql = f.read()

            model_name = os.path.splitext(os.path.basename(path))[0]
            refs = re.findall(r"ref\(['\"](.*?)['\"]\)", sql)

            # 🎨 Color by prefix
            if model_name.startswith("stg_"):
                color = "#00BFFF"  # blue
            elif model_name.startswith("field_da_"):
                color = "#32CD32"  # green
            else:
                color = "#CCCCCC"  # default grey

            if model_name not in added_nodes:
                net.add_node(model_name, label=model_name, color=color, title=model_name, shape="box")
                added_nodes.add(model_name)

            for ref_model in refs:
                # fallback coloring for ref nodes
                if ref_model not in added_nodes:
                    if ref_model.startswith("stg_"):
                        ref_color = "#00BFFF"
                    elif ref_model.startswith("field_da_"):
                        ref_color = "#32CD32"
                    else:
                        ref_color = "#CCCCCC"

                    net.add_node(ref_model, label=ref_model, color=ref_color, title=ref_model, shape="box")
                    added_nodes.add(ref_model)

                net.add_edge(ref_model, model_name)

        net.repulsion(node_distance=250, spring_length=200)

        net.set_options("""
        var options = {
            "edges": {
                "arrows": {
                    "to": { "enabled": true, "scaleFactor": 1 }
                },
                "color": { "inherit": true },
                "smooth": { "enabled": true, "type": "dynamic" },
                "shadow": true
            },
            "nodes": {
                "font": { "size": 16 },
                "shape": "box",
                "shadow": true
            },
            "physics": {
                "enabled": true,
                "stabilization": { "iterations": 300 }
            }
        }
        """)

        graph_file = os.path.join(folder, "lineage_graph.html")
        net.save_graph(graph_file)

        with open(graph_file, "r", encoding="utf-8") as f:
            graph_html = f.read()

        components.html(graph_html, height=620, scrolling=True)

    with tab3:
        st.markdown("### 🧬 Column Descriptions")
        for m, meta in yml_meta.items():
            st.markdown(f"#### `{m}`")
            for col, desc in meta["columns"].items():
                st.markdown(f"- **{col}**: {desc or '_No description_'}")

    with tab4:
        rows = []
        for m in sql_map:
            refs = model_refs.get(m, [])
            desc = yml_meta.get(m, {}).get("description", "")
            cols = len(yml_meta.get(m, {}).get("columns", {}))
            rows.append({"Model": m, "Description": desc, "Refs": ", ".join(refs), "Columns": cols})
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

    with tab5:
        st.markdown("### 🧭 Model Categorization")
        cats = {"stg": [], "dim": [], "fct": [], "others": []}
        for m in sql_map:
            if m.startswith("stg_"): cats["stg"].append(m)
            elif m.startswith("dim_"): cats["dim"].append(m)
            elif m.startswith("fct_"): cats["fct"].append(m)
            else: cats["others"].append(m)
        for c, models in cats.items():
            st.subheader(f"{c.upper()} Models")
            for m in models:
                st.markdown(f"- `{m}`")

    with tab6:
        st.markdown("### 🔍 Search by Column or Keyword")
        q = st.text_input("Search:")
        if q:
            matches = []
            for m, sql in sql_map.items():
                if q.lower() in sql.lower():
                    matches.append(m)
                elif q.lower() in yml_meta.get(m, {}).get("description", "").lower():
                    matches.append(m)
                elif any(q.lower() in col.lower() for col in yml_meta.get(m, {}).get("columns", {})):
                    matches.append(m)
            if matches:
                st.success(f"Found {len(matches)} match(es):")
                for m in matches:
                    st.markdown(f"- ✅ `{m}`")
            else:
                st.warning("No match found.")

    with tab7:
        st.markdown("### 🌳 Ref Tree for a Model")
        model = st.selectbox("Choose model:", list(sql_map.keys()))
        
        if model:
            if model not in sql_map:
                st.warning(f"⚠️ Model `{model}` not found in the loaded SQL map.")
            else:
                subgraph = nx.DiGraph()
                subgraph.add_node(model)

                if model in ref_graph:
                    for u in nx.ancestors(ref_graph, model):
                        subgraph.add_edge(u, model)
                    for d in nx.descendants(ref_graph, model):
                        subgraph.add_edge(model, d)

                tree = Network(height="600px", directed=True)
                for n in subgraph.nodes():
                    tree.add_node(n, label=n, title=n, shape="ellipse")
                for u, v in subgraph.edges():
                    tree.add_edge(u, v)

                tree_path = os.path.join(folder, "ref_tree.html")
                tree.save_graph(tree_path)
                components.html(open(tree_path).read(), height=640, scrolling=True)

    with tab8:
        st.markdown("### 📤 Export GPT Summaries & Lineage Graph")
        if summaries:
            summary_md = "\n\n".join([f"## {m}\n{txt}" for m, txt in summaries.items()])
            st.download_button("📄 Download Summaries (.md)", summary_md, file_name="dbt_summaries.md")
        else:
            st.info("⚠️ Run summarization first.")
        if os.path.exists(graph_file):
            with open(graph_file, "r", encoding="utf-8") as f:
                graph_html = f.read()
            st.download_button("📊 Download Lineage Graph (.html)", graph_html, file_name="dbt_lineage_graph.html")

        st.markdown("---")
        st.markdown("### 📈 Model Complexity Score")
        complexity = []
        for model, sql in sql_map.items():
            refs = model_refs.get(model, [])
            lines = len(sql.strip().splitlines())
            score = "Low"
            if len(refs) >= 2 or lines >= 10:
                score = "High"
            elif len(refs) == 1 or lines >= 5:
                score = "Medium"
            complexity.append({
                "Model": model,
                "Refs": len(refs),
                "Lines of SQL": lines,
                "Complexity": score
            })
        df = pd.DataFrame(complexity)
        st.dataframe(df, use_container_width=True)


    with tab9:
        st.markdown("### 🧬 Column Lineage Viewer")

        lineage = []

        for model, sql in sql_map.items():
            cleaned_sql = sql.lower().replace("\n", " ")

            select_match = re.search(r"select (.+?) from", cleaned_sql)
            if select_match:
                cols = select_match.group(1)
                cols = re.split(r",\s*", cols)
                for col in cols:
                    col = col.strip().split(" as ")[-1].strip()
                    lineage.append({"Column": col, "Used In Model": model})

        df_lineage = pd.DataFrame(lineage)
        summary = df_lineage.groupby("Column")["Used In Model"].apply(list).reset_index()
        summary["# of Models"] = summary["Used In Model"].apply(len)

        # Search box
        q = st.text_input("🔍 Search for a column:")
        if q:
            summary = summary[summary["Column"].str.contains(q, case=False)]

        st.dataframe(summary, use_container_width=True)


    with tab10:
        st.markdown("### 📁 Auto-Summarize Selected Folder")

        # Collect model info
        model_count = len(sql_map)
        ref_counts = {}
        prefix_counts = {"stg": 0, "dim": 0, "fct": 0, "field_da": 0, "other": 0}
        all_refs = []

        for model, refs in model_refs.items():
            all_refs.extend(refs)
            if model.startswith("stg_"):
                prefix_counts["stg"] += 1
            elif model.startswith("dim_"):
                prefix_counts["dim"] += 1
            elif model.startswith("fct_"):
                prefix_counts["fct"] += 1
            elif model.startswith("field_da_"):
                prefix_counts["field_da"] += 1
            else:
                prefix_counts["other"] += 1

        unique_refs = list(set(all_refs))

        summary_prompt = f"""
    You are a data engineer. Summarize this DBT folder based on the following metadata:

    - Total models: {model_count}
    - Model types:
    - Staging: {prefix_counts['stg']}
    - Dim: {prefix_counts['dim']}
    - Fact: {prefix_counts['fct']}
    - Field_DA: {prefix_counts['field_da']}
    - Others: {prefix_counts['other']}
    - Ref targets used: {', '.join(unique_refs)}

    Write 2–4 bullet points describing what this folder is likely doing and what it depends on.
    """

        if st.button("🧠 Generate Folder Summary"):
            with st.spinner("Asking GPT..."):
                try:
                    res = openai.ChatCompletion.create(
                        model=config["deployment_name"] if config["provider"] == "azure" else "gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    folder_summary = res.choices[0].message.content
                    st.success("✅ Summary generated")
                    st.markdown(folder_summary)
                except Exception as e:
                    st.error(f"❌ GPT failed: {e}")    