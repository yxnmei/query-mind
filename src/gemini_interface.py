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
- When filtering by year on a column stored as 'YYYY-MM' text (e.g. '2023-01'), use LIKE '2023%' instead of strftime(). Only use strftime() on full date columns stored as 'YYYY-MM-DD'.
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
    prompt = f"""You are a friendly data analyst helping a non-technical business user explore a dataset.
Generate exactly 5 questions they might naturally ask in casual conversation.

STRICT RULES:
- Write like a human talking to another human, not like a programmer
- NEVER use column names, backticks, quotes around values, or raw data values
- NEVER mention specific codes like '2023-01', '4 ROOM', '416A', 'FERNVALE LINK'
- Instead say: "in 2023", "4-room flats", "high-floor units", "last year"

GOOD questions (write like these):
- Which neighbourhood had the highest average resale price last year?
- How have resale prices changed over the years?
- Which flat type tends to sell for the most?
- Which areas are the most affordable for larger flats?
- How do prices differ between high and low floor units?

BAD questions (never write like these):
- What is the average resale_price for flat_type '4 ROOM' in month '2023-01'?
- Which town has the highest resale_price for flat_model 'Improved'?

SCHEMA:
{schema}

Write 5 natural, human-sounding questions as a numbered list:"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    lines = response.text.strip().split("\n")
    questions = []
    for line in lines:
        line = line.strip()
        if line and line[0].isdigit():
            question = line.split(".", 1)[-1].strip().split(")", 1)[-1].strip()
            if question:
                questions.append(question)

    return questions[:5]