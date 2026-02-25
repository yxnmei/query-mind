# src/sql_executor.py
import pandas as pd
from sqlalchemy import create_engine, text
import re

# These keywords should never appear in a generated query
FORBIDDEN_KEYWORDS = [
    r"\bDROP\b", r"\bDELETE\b", r"\bINSERT\b",
    r"\bUPDATE\b", r"\bALTER\b", r"\bCREATE\b",
    r"\bTRUNCATE\b", r"\bEXEC\b", r"\bEXECUTE\b",
]

class UnsafeSQLError(Exception):
    pass

def is_safe(sql: str) -> bool:
    """Reject any SQL containing dangerous mutation keywords."""
    upper = sql.upper()
    for pattern in FORBIDDEN_KEYWORDS:
        if re.search(pattern, upper):
            return False
    return True

def execute_query(sql: str, db_path: str) -> pd.DataFrame:
    """
    Validates and executes a SQL query against the SQLite database.
    Returns a pandas DataFrame of results.
    """
    if not is_safe(sql):
        raise UnsafeSQLError(
            "⚠️ Unsafe query detected. Only SELECT statements are allowed."
        )
    
    if not sql.strip().upper().startswith("SELECT"):
        raise UnsafeSQLError(
            "⚠️ Only SELECT queries are permitted."
        )
    
    engine = create_engine(f"sqlite:///{db_path}")
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn)
    
    return df