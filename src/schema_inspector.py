# src/schema_inspector.py
from sqlalchemy import create_engine, inspect, text

def get_schema_string(db_path: str) -> str:
    """
    Auto-introspects the SQLite database and returns a 
    human-readable schema string for Gemini's prompt.
    """
    engine = create_engine(f"sqlite:///{db_path}")
    inspector = inspect(engine)
    
    schema_parts = []
    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        fks = inspector.get_foreign_keys(table_name)
        
        col_lines = []
        for col in columns:
            col_type = str(col["type"])
            pk_marker = " [PRIMARY KEY]" if col.get("primary_key") else ""
            col_lines.append(f"    {col['name']} ({col_type}){pk_marker}")
        
        fk_lines = []
        for fk in fks:
            fk_lines.append(
                f"    FK: {fk['constrained_columns']} → {fk['referred_table']}({fk['referred_columns']})"
            )
        
        block = f"Table: {table_name}\n" + "\n".join(col_lines)
        if fk_lines:
            block += "\n" + "\n".join(fk_lines)
        schema_parts.append(block)
    
    return "\n\n".join(schema_parts)