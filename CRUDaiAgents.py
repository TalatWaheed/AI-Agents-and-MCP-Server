import os
import sqlite3
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain import hubs

# ==========================================
# 1. DATABASE SETUP (SQLite)
# ==========================================
DB_FILE = "inventory.db"

def init_db():
    """Initializes a local SQLite database with a sample inventory table."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    """)
    # Insert some dummy data if the table is empty
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO products (name, price, stock) VALUES (?, ?, ?)
        """, [
            ("Wireless Headphones", 99.99, 50),
            ("Gaming Mouse", 49.50, 30),
            ("Mechanical Keyboard", 120.00, 15)
        ])
    conn.commit()
    conn.close()

# Initialize the database immediately on script run
init_db()


# ==========================================
# 2. DEFINING THE CRUD TOOLS FOR THE AI
# ==========================================

@tool
def create_product(name: str, price: float, stock: int) -> str:
    """Use this tool to add/create a new product in the database inventory."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", 
            (name, price, stock)
        )
        conn.commit()
        conn.close()
        return f"Successfully created product: {name} with price ${price} and stock {stock}."
    except sqlite3.IntegrityError:
        return f"Error: Product '{name}' already exists. Use update tools instead."

@tool
def read_product(name: str) -> str:
    """Use this tool to retrieve or check details of a specific product from the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name, price, stock FROM products WHERE name LIKE ?", (f"%{name}%",))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return f"Product Found -> Name: {row[0]}, Price: ${row[1]}, Stock: {row[2]}"
    return f"Product '{name}' not found in the inventory database."

@tool
def update_stock(name: str, new_stock: int) -> str:
    """Use this tool to update the stock inventory level of an existing product."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET stock = ? WHERE name LIKE ?", (new_stock, f"%{name}%"))
    conn.commit()
    changes = conn.total_changes
    conn.close()
    
    if changes > 0:
        return f"Successfully updated stock for '{name}' to {new_stock}."
    return f"Could not update stock. Product '{name}' not found."

@tool
def delete_product(name: str) -> str:
    """Use this tool to permanently delete/remove a product from the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE name LIKE ?", (f"%{name}%",))
    conn.commit()
    changes = conn.total_changes
    conn.close()
    
    if changes > 0:
        return f"Successfully deleted product '{name}' from the database."
    return f"Could not delete. Product '{name}' not found."


# ==========================================
# 3. INITIALIZING THE AI AGENT
# ==========================================

# 🔴 Paste your OpenAI API Key here if it's not set in your system environment variables:
# os.environ["OPENAI_API_KEY"] = "your-openai-api-key-here"

if "OPENAI_API_KEY" not in os.environ:
    raise ValueError("Please set the OPENAI_API_KEY environment variable or paste it inside the script.")

# Group the tools into a list the agent can access
tools = [create_product, read_product, update_stock, delete_product]

# Define the Language Model (Using GPT-4o mini for smart execution and cost efficiency)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Pull a standard system prompt structured for tool usage from the LangChain Hub
prompt = hubs.pull("hwchase17/openai-functions-agent")

# Construct the Agent logic
agent = create_openai_functions_agent(llm, tools, prompt)

# Create the Agent Executor runtime environment
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


# ==========================================
# 4. RUNNING TEST PROMPTS (EXECUTION)
# ==========================================
if __name__ == "__main__":
    print("--- AI CRUD Agent Initialized ---\n")

    # Example 1: Read operation
    print("Executing Example 1: Reading data...")
    response1 = agent_executor.invoke({"input": "Do we have any Gaming Mice in stock? How many?"})
    print(f"\nAI Response:\n{response1['output']}\n" + "-"*40)

    # Example 2: Multi-step Conditional (Create/Update logic handled autonomously)
    print("\nExecuting Example 2: Complex multi-step instructions...")
    complex_prompt = (
        "Check if we have an item called '4K Monitor'. "
        "If we don't have it, create it with a price of $299 and 15 units in stock. "
        "If we do have it, just increase its stock by 5."
    )
    response2 = agent_executor.invoke({"input": complex_prompt})
    print(f"\nAI Response:\n{response2['output']}\n" + "-"*40)

    # Example 3: Verifying the changes (Read operation)
    print("\nExecuting Example 3: Verifying the database changed...")
    response3 = agent_executor.invoke({"input": "Can you check the details of the 4K Monitor now?"})
    print(f"\nAI Response:\n{response3['output']}\n" + "-"*40)
