# src/utils.py
import pandas as pd
import plotly.express as px
import sqlite3
import os

UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "uploads")


def get_uploads_dir() -> str:
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    return os.path.abspath(UPLOADS_DIR)


def load_uploaded_file(uploaded_file) -> tuple[str, list[str]]:
    """
    Accepts a Streamlit uploaded file (SQLite, CSV, or Excel).
    Saves it persistently to data/uploads/ and converts to SQLite.
    Returns (db_path, list_of_table_names).
    """
    uploads_dir = get_uploads_dir()
    filename = uploaded_file.name
    ext = os.path.splitext(filename)[-1].lower()

    # Save raw uploaded file to uploads dir
    raw_path = os.path.join(uploads_dir, filename)
    with open(raw_path, "wb") as f:
        f.write(uploaded_file.read())

    if ext in (".sqlite", ".db"):
        db_path = raw_path
        conn = sqlite3.connect(db_path)
        tables = _get_table_names(conn)
        conn.close()

    elif ext == ".csv":
        db_path = raw_path.replace(ext, ".sqlite")
        df = pd.read_csv(raw_path)
        table_name = _sanitise_name(os.path.splitext(filename)[0])
        conn = sqlite3.connect(db_path)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        tables = [table_name]
        conn.close()

    elif ext in (".xlsx", ".xls"):
        db_path = raw_path.replace(ext, ".sqlite")
        conn = sqlite3.connect(db_path)
        xls = pd.ExcelFile(raw_path)
        tables = []
        for sheet in xls.sheet_names:
            df = pd.read_excel(raw_path, sheet_name=sheet)
            table_name = _sanitise_name(sheet)
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            tables.append(table_name)
        conn.close()

    else:
        raise ValueError(f"Unsupported file type: {ext}")

    return db_path, tables


def get_saved_databases() -> dict[str, str]:
    """
    Scans data/uploads/ for all .sqlite and .db files.
    Returns a dict of {display_name: db_path}.
    """
    uploads_dir = get_uploads_dir()
    dbs = {}
    for f in sorted(os.listdir(uploads_dir)):
        if f.endswith((".sqlite", ".db")):
            dbs[f] = os.path.join(uploads_dir, f)
    return dbs


def auto_visualise(df: pd.DataFrame):
    """Auto-generate a Plotly chart based on DataFrame shape."""
    if df.empty or len(df) < 2:
        return None

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    text_cols = df.select_dtypes(include="object").columns.tolist()

    if not numeric_cols:
        return None

    y_col = numeric_cols[0]

    date_cols = [c for c in df.columns if any(kw in c.lower()
                 for kw in ["date", "month", "year", "period", "week"])]
    if date_cols:
        return px.line(df, x=date_cols[0], y=y_col,
                       title=f"{y_col} over time", markers=True)

    if text_cols and len(df) <= 30:
        return px.bar(df, x=text_cols[0], y=y_col,
                      title=f"{y_col} by {text_cols[0]}",
                      color=y_col, color_continuous_scale="Blues")

    if len(df) <= 50:
        return px.bar(df, y=y_col, title=f"Distribution of {y_col}")

    return None


def _get_table_names(conn: sqlite3.Connection) -> list[str]:
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [row[0] for row in cursor.fetchall()]


def _sanitise_name(name: str) -> str:
    """Convert file/sheet names to valid SQL table names."""
    return name.strip().lower().replace(" ", "_").replace("-", "_")


def format_number(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)