# Text-to-SQL AI Agent (SQLite) – Beginner Project

Build a simple AI agent that converts natural language questions into SQL queries, executes them on a SQLite database, and returns the results.  
This project is designed for beginners who know basic Python and SQL.

🎥 **Tutorial video:** [Build a Text-to-SQL AI Agent in Python – Step-by-Step (SQLite)](YOUR_VIDEO_LINK_HERE)

---

## What This Project Does

- Creates an in-memory SQLite database with a sample `employees` table.
- Takes your question in plain English (e.g., “Show me employees with salary greater than 50000”).
- Uses an AI model (OpenAI) to generate a SQL query from your question.
- Executes the SQL query on the database.
- Prints both the generated SQL and the query results.

This is a minimal but complete example of a **Text-to-SQL agent**, similar to many AI database assistants. [71][91][96]

---

## Prerequisites

- Python 3.8+ installed
- Basic knowledge of:
  - Python (functions, loops, imports)
  - SQL (`SELECT`, `WHERE`, basic queries)
- An [OpenAI API key](https://platform.openai.com/api-keys)

---

## Project Structure

```text
text-to-sql-agent/
├─ .env.example          # Template for environment variables
├─ .gitignore
├─ requirements.txt      # Python dependencies
├─ text_to_sql_agent.py  # Main agent script
└─ README.md
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/text-to-sql-agent.git
cd text-to-sql-agent
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:

- `openai` – to call the OpenAI API
- `python-dotenv` – to load your API key from a `.env` file

### 3. Configure Your API Key

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Open `.env` and add your OpenAI API key:

   ```env
   OPENAI_API_KEY=sk-your-openai-api-key-here
   ```

> Never commit your `.env` file to Git. It’s already in `.gitignore`.

---

## How to Run

From the project folder:

```bash
python text_to_sql_agent.py
```

You’ll see:

```text
Text-to-SQL Agent is ready!
Ask questions about the 'employees' table in plain English.
Type 'exit' to quit.
```

Then you can ask questions like:

- `Show me all employees`
- `Show me employees with salary greater than 50000`
- `What is the average salary in Engineering?`

The agent will:

1. Generate a SQL query from your question.
2. Execute it on the in-memory SQLite database.
3. Print the SQL and the results.

Example:

```text
You: Show me employees with salary greater than 50000

Generated SQL:
SELECT * FROM employees WHERE salary > 50000

Result:
id | name | department | salary | hire_date
----------------------------------------
1 | Alice | Engineering | 120000 | 2023-01-15
2 | Bob | Engineering | 95000 | 2022-07-10
5 | Eve | Engineering | 110000 | 2023-06-01
```

---

## How It Works (High Level)

1. **Database setup**  
   - `create_sample_db()` creates an in-memory SQLite database with an `employees` table and sample data.

2. **Schema extraction**  
   - `get_database_schema()` reads the table structure and returns a text description like:  
     `Table 'employees': id (INTEGER), name (TEXT), department (TEXT), salary (INTEGER), hire_date (TEXT)`

3. **Text-to-SQL generation**  
   - `generate_sql_from_question(question, schema)` sends:
     - The schema
     - Your question  
     to the OpenAI model with a system prompt like:  
     “You are a Text-to-SQL expert. Given a schema and a question, write a correct SQL query. Return ONLY the SQL.”  
   - The model returns a SQL query string. [71][91][97]

4. **Query execution**  
   - `execute_sql_query(conn, sql_query)` runs the SQL on the SQLite connection and returns columns + rows, or an error message if the SQL is invalid. [71]

5. **Interactive loop**  
   - The `if __name__ == "__main__":` block:
     - Creates the DB
     - Fetches the schema
     - Repeatedly asks you for questions, generates SQL, executes it, and prints results.

---

## Customization Ideas

Once you’re comfortable with the code, try:

- Adding more tables (e.g., `departments`, `projects`) and asking cross-table questions.
- Changing the system prompt to:
  - Return explanations along with SQL.
  - Enforce safety rules (e.g., only `SELECT`, no `DELETE`/`UPDATE`).
- Building a MySQL version that connects to your own database.  
  (This is covered in the next video on the channel.)

---

## Common Issues & Tips

- **`OPENAI_API_KEY` not found**  
  - Make sure you created a `.env` file (not just `.env.example`) and added your key.
  - Ensure you’re running the script from the project folder.

- **Invalid SQL or errors**  
  - Check the generated SQL printed in the terminal.
  - Try rephrasing your question more clearly (e.g., “Show me employees in Engineering with salary greater than 50000”).

- **No results returned**  
  - Your query might be correct but simply match no rows. Try a broader condition.


## License

This project is for educational purposes. Feel free to use and modify it for learning and your own projects.
