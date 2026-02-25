# src/app.py
import streamlit as st
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from gemini_interface import generate_sql, clear_history, generate_example_questions
from sql_executor import execute_query, UnsafeSQLError
from schema_inspector import get_schema_string
from utils import auto_visualise, load_uploaded_file, get_saved_databases

# ── Paths ────────────────────────────────────────────────
DEFAULT_DB = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "ecommerce.sqlite")
)
DEFAULT_LABEL = "ecommerce.sqlite (default)"

st.set_page_config(
    page_title="QueryMind",
    page_icon="🧠",
    layout="wide"
)

# ── Session state ────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "db_path" not in st.session_state:
    st.session_state.db_path = DEFAULT_DB
if "schema" not in st.session_state:
    st.session_state.schema = get_schema_string(DEFAULT_DB)
if "db_label" not in st.session_state:
    st.session_state.db_label = DEFAULT_LABEL
if "example_questions" not in st.session_state:
    st.session_state.example_questions = []
if "last_uploaded_filename" not in st.session_state:
    st.session_state.last_uploaded_filename = None

# ── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.image("https://em-content.zobj.net/source/google/387/brain_1f9e0.png", width=48)
    st.title("QueryMind")
    st.caption("Ask anything. Get answers.")
    st.divider()

    # ── Upload section ───────────────────────────────────
    st.subheader("📂 Upload Your Own Data")
    st.caption("Supports `.sqlite`, `.db`, `.csv`, `.xlsx`")

    uploaded = st.file_uploader(
        label="Drop a file here",
        type=["sqlite", "db", "csv", "xlsx", "xls"],
        label_visibility="collapsed"
    )

    if uploaded:
        if uploaded.name != st.session_state.last_uploaded_filename:
            with st.spinner(f"Loading {uploaded.name}..."):
                try:
                    db_path, tables = load_uploaded_file(uploaded)
                    schema = get_schema_string(db_path)

                    st.session_state.db_path = db_path
                    st.session_state.schema = schema
                    st.session_state.db_label = uploaded.name
                    st.session_state.history = []
                    st.session_state.last_uploaded_filename = uploaded.name
                    clear_history()

                    with st.spinner("✨ Generating example questions..."):
                        st.session_state.example_questions = generate_example_questions(schema)

                    st.success(f"✅ Loaded! Found {len(tables)} table(s): {', '.join(tables)}")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to load file: {e}")

    st.divider()

    # ── Saved databases selector ─────────────────────────
    st.subheader("🗄️ Select Database")

    saved_dbs = get_saved_databases()
    options = {DEFAULT_LABEL: DEFAULT_DB}
    options.update(saved_dbs)

    selected_label = st.radio(
        label="Choose active database",
        options=list(options.keys()),
        index=list(options.keys()).index(st.session_state.db_label)
              if st.session_state.db_label in options else 0,
        label_visibility="collapsed"
    )

    if selected_label != st.session_state.db_label:
        new_db_path = options[selected_label]
        new_schema = get_schema_string(new_db_path)

        st.session_state.db_path = new_db_path
        st.session_state.schema = new_schema
        st.session_state.db_label = selected_label
        st.session_state.history = []
        st.session_state.last_uploaded_filename = (
            None if selected_label == DEFAULT_LABEL else selected_label
        )
        clear_history()

        with st.spinner("✨ Generating example questions..."):
            st.session_state.example_questions = generate_example_questions(new_schema)

        st.rerun()

    st.divider()

    # ── Schema viewer ────────────────────────────────────
    st.subheader("📐 Schema")
    st.code(st.session_state.schema, language="sql")
    st.divider()

    # ── Example questions ────────────────────────────────
    st.subheader("💡 Try asking")

    examples = st.session_state.get("example_questions") or [
        "What are the top 10 rows in this dataset?",
        "Show me a summary of all tables",
        "What are the most common values in each column?",
        "Which rows have the highest values?",
        "Show monthly trends over time",
    ]

    for ex in examples:
        if st.button(ex, use_container_width=True, key=ex):
            st.session_state.prefill = ex

    st.divider()
    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.history = []
        clear_history()
        st.rerun()

# ── Main UI ──────────────────────────────────────────────
st.markdown("# 🧠 QueryMind")
st.markdown("### Ask anything. Get answers.")
st.caption(f"Active database: **{st.session_state.db_label}**")
st.divider()

# Conversation history
for item in st.session_state.history:
    with st.chat_message("user"):
        st.write(item["query"])
    with st.chat_message("assistant"):
        if item.get("error"):
            st.error(item["error"])
        else:
            with st.expander("🔍 Generated SQL", expanded=False):
                st.code(item["sql"], language="sql")
            st.dataframe(item["df"], use_container_width=True)
            fig = auto_visualise(item["df"])
            if fig:
                st.plotly_chart(fig, use_container_width=True)

# Input
prefill = st.session_state.pop("prefill", "")
user_query = st.chat_input("Ask a question about your data...")

if not user_query and prefill:
    user_query = prefill

if user_query:
    with st.chat_message("user"):
        st.write(user_query)

    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            try:
                sql = generate_sql(st.session_state.schema, user_query)

                with st.expander("🔍 Generated SQL", expanded=True):
                    st.code(sql, language="sql")

                df = execute_query(sql, st.session_state.db_path)

                if df.empty:
                    st.warning("Query returned no results. Try rephrasing.")
                    st.session_state.history.append(
                        {"query": user_query, "sql": sql, "df": df, "error": None}
                    )
                else:
                    st.success(f"✅ {len(df)} row(s) returned")
                    st.dataframe(df, use_container_width=True)
                    fig = auto_visualise(df)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    st.session_state.history.append(
                        {"query": user_query, "sql": sql, "df": df, "error": None}
                    )

            except UnsafeSQLError as e:
                st.error(str(e))
                st.session_state.history.append(
                    {"query": user_query, "sql": "", "df": None, "error": str(e)}
                )
            except Exception as e:
                friendly = f"❌ Could not execute query.\n\nError: `{str(e)}`\n\nTry rephrasing."
                st.error(friendly)
                st.session_state.history.append(
                    {"query": user_query, "sql": "", "df": None, "error": friendly}
                )