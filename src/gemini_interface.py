# src/gemini_interface.py
from google import genai
from dotenv import load_dotenv
import os
import re

from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Conversation history for follow-up support
_chat_history = []

SYSTEM_PREAMBLE = """You are an expert SQLite SQL assistant embedded in an e-commerce analytics app.
Your ONLY job is to return a single, valid SQLite SQL SELECT query.

Rules:
- Return ONLY the raw SQL query — no explanation, no markdown, no backticks.
- Only use SELECT statements. Never use INSERT, UPDATE, DELETE, DROP, ALTER, or CREATE.
- Always alias calculated columns with meaningful names (e.g., SUM(revenue) AS total_revenue).
- Use table names and column names exactly as provided in the schema.
- When filtering dates, use SQLite date functions (e.g., strftime('%Y-%m', order_date) = '2024-03').
- If a question is ambiguous, make a reasonable assumption and answer it.
- Revenue for an order item = quantity * unit_price.
"""

def build_prompt(schema: str, user_query: str) -> str:
    context = ""
    if _chat_history:
        context = "CONVERSATION CONTEXT (for follow-up queries):\n"
        context += "\n".join([f"Previous Q: {h['q']}\nPrevious SQL: {h['sql']}"
                               for h in _chat_history[-3:]])
        context += "\n\n"

    return f"""{SYSTEM_PREAMBLE}

{context}DATABASE SCHEMA:
{schema}

USER QUESTION: {user_query}

SQL QUERY:"""

def generate_sql(schema: str, user_query: str) -> str:
    prompt = build_prompt(schema, user_query)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    sql = response.text.strip()
    sql = re.sub(r"```sql|```", "", sql).strip()

    _chat_history.append({"q": user_query, "sql": sql})
    return sql

def clear_history():
    _chat_history.clear()

def generate_example_questions(schema: str) -> list[str]:
    """Ask Gemini to suggest 5 interesting questions for the given schema."""
    prompt = f"""You are a data analyst. Given this database schema, suggest exactly 5 interesting and varied 
questions a business user might ask. Make them specific to the actual table and column names.

Rules:
- Return ONLY a numbered list (1. 2. 3. 4. 5.)
- No explanations, no extra text
- Questions should range from simple lookups to interesting aggregations
- Use actual column and table names from the schema

SCHEMA:
{schema}

5 QUESTIONS:"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    lines = response.text.strip().split("\n")
    questions = []
    for line in lines:
        line = line.strip()
        if line and line[0].isdigit():
            # Strip the number prefix (e.g. "1. " or "1) ")
            question = line.split(".", 1)[-1].strip().split(")", 1)[-1].strip()
            if question:
                questions.append(question)

    return questions[:5]