import os
import mysql.connector
from mysql.connector import Error
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Create OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def create_mysql_connection():
    """
    Create a connection to your MySQL database.
    All connection details are read from environment variables.
    """
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print("Error while connecting to MySQL:", e)
        raise


def get_database_schema(conn) -> str:
    """
    Fetch the schema of all tables in the connected MySQL database
    and return it as a human-readable text description.
    """
    cursor = conn.cursor()

    # Get all table names in the current database
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]

    schema_parts = []

    for table_name in tables:
        # Get column info for each table
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = cursor.fetchall()
        # Each row: (Field, Type, Null, Key, Default, Extra)
        col_defs = [f"{col[0]} ({col[1]})" for col in columns]
        schema_parts.append(f"Table '{table_name}': " + ", ".join(col_defs))

    cursor.close()
    return "\n".join(schema_parts)


def generate_sql_from_question(question: str, schema: str) -> str:
    """
    Use an LLM to convert a natural-language question into a SQL query,
    given the database schema.
    """
    system_message = {
        "role": "system",
        "content": (
            "You are a Text-to-SQL expert. "
            "Given a database schema and a user question, "
            "write a correct SQL query that answers the question. "
            "Return ONLY the SQL query, nothing else. "
            "Do not include explanations or markdown. "
            "Assume the database is MySQL. "
            "Use only SELECT queries (no INSERT, UPDATE, DELETE)."
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


def execute_sql_query(conn, sql_query: str):
    """
    Execute a SQL query on the MySQL connection and return columns + rows.
    If there is an error, return (None, error_message).
    """
    try:
        cursor = conn.cursor()
        cursor.execute(sql_query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        cursor.close()
        return columns, rows
    except Error as e:
        return None, str(e)


if __name__ == "__main__":
    # 1. Connect to MySQL
    conn = create_mysql_connection()

    # 2. Get database schema
    schema = get_database_schema(conn)

    print("MySQL Text-to-SQL Agent is ready!")
    print(f"Connected to database: {os.getenv('DB_NAME')}")
    print("Ask questions about your database in plain English.")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in ["exit", "quit"]:
            print("Agent: Goodbye!")
            break

        if not question:
            continue

        # 3. Generate SQL from the question
        sql_query = generate_sql_from_question(question, schema)
        print(f"\n Generated SQL:\n{sql_query}\n")

        # 4. Execute the SQL query
        columns, result = execute_sql_query(conn, sql_query)

        if columns is None:
            print("Error executing query:")
            print(result)
        else:
            print("Result:")
            print(" | ".join(columns))
            print("-" * 60)
            for row in result:
                print(" | ".join(str(val) for val in row))
            print()

    # 5. Close connection when done
    if conn.is_connected():
        conn.close()
