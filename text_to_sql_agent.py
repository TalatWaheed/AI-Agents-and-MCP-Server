import os
import sqlite3
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Create OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def create_sample_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            department TEXT,
            salary INTEGER,
            hire_date TEXT
        )
    """)

    employees_data = [
        ("Alice", "Engineering", 120000, "2023-01-15"),
        ("Bob", "Engineering", 95000, "2022-07-10"),
        ("Charlie", "Sales", 80000, "2021-03-22"),
        ("Diana", "HR", 70000, "2020-11-05"),
        ("Eve", "Engineering", 110000, "2023-06-01"),
    ]

    cursor.executemany(
        "INSERT INTO employees (name, department, salary, hire_date) VALUES (?, ?, ?, ?)",
        employees_data
    )

    conn.commit()
    return conn


def get_database_schema(conn: sqlite3.Connection) -> str:
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    schema_parts = []
    for (table_name,) in tables:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        col_defs = [f"{col[1]} ({col[2]})" for col in columns]
        schema_parts.append(f"Table '{table_name}': " + ", ".join(col_defs))

    return "\n".join(schema_parts)


def generate_sql_from_question(question: str, schema: str) -> str:
    system_message = {
        "role": "system",
        "content": (
            "You are a Text-to-SQL expert. "
            "Given a database schema and a user question, "
            "write a correct SQL query that answers the question. "
            "Return ONLY the SQL query, nothing else. "
            "Do not include explanations or markdown."
        )
    }

    user_message = {
        "role": "user",
        "content": (
            f"Database schema:\n{schema}\n\n"
            f"Question: {question}\n\n"
            "SQL query:"
        )
    }

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[system_message, user_message],
        max_tokens=200
    )

    sql_query = response.choices[0].message.content.strip()
    return sql_query


def execute_sql_query(conn: sqlite3.Connection, sql_query: str):
    try:
        cursor = conn.cursor()
        cursor.execute(sql_query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        return columns, rows
    except Exception as e:
        return None, str(e)


if __name__ == "__main__":
    conn = create_sample_db()
    schema = get_database_schema(conn)

    print("Text-to-SQL Agent is ready!")
    print("Ask questions about the 'employees' table in plain English.")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in ["exit", "quit"]:
            print("Agent: Goodbye!")
            break

        if not question:
            continue

        sql_query = generate_sql_from_question(question, schema)
        print(f"\n Generated SQL:\n{sql_query}\n")

        columns, result = execute_sql_query(conn, sql_query)

        if columns is None:
            print("Error executing query:")
            print(result)
        else:
            print("Result:")
            print(" | ".join(columns))
            print("-" * 40)
            for row in result:
                print(" | ".join(str(val) for val in row))
            print()
