import sqlite3
import os
from mcp.server.fastmcp import FastMCP

# =====================================================================
# 1. INITIALIZE FASTMCP SERVER
# =====================================================================
# The name provided here is what the AI Host (like Claude Desktop) will see.
mcp = FastMCP("ECommerce_Database_Bridge")

DB_FILE = "store.db"
SAFE_DIR = os.path.abspath("./secure_analytics")

# Ensure a mock directory and database exist for the demo
os.makedirs(SAFE_DIR, exist_ok=True)

def init_mock_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT,
            status TEXT
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO users (username, email, status) VALUES (?, ?, ?)", [
            ("alex_dev", "alex@example.com", "Active"),
            ("sarah_m", "sarah@example.com", "Suspended"),
            ("tech_guru", "guru@example.com", "Active")
        ])
    conn.commit()
    conn.close()

init_mock_db()

# =====================================================================
# 2. DEFINE EXPOSED RESOURCES (Passive Streams of Data)
# =====================================================================

@mcp.resource("analytics://config")
def get_analytics_config() -> str:
    """Provides configuration contexts and operational guidelines for the system."""
    return "SYSTEM CONFIG: Region=US-East; Security_Level=High; Strict_Mode=True"

# =====================================================================
# 3. DEFINE EXPOSED TOOLS (Executable Functions for the AI)
# =====================================================================

@mcp.tool()
def fetch_user_metrics(user_id: int) -> str:
    """
    Fetches account details and operational metrics for a specific user ID 
    from the local production database. Use this tool when analyzing profiles.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT username, email, status FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return f"[DATABASE SUCCESS] User ID {user_id} -> Username: {row[0]}, Email: {row[1]}, Status: {row[2]}"
        return f"[DATABASE ERROR] User ID {user_id} does not exist."
    except Exception as e:
        return f"Database query execution failed: {str(e)}"


@mcp.tool()
def write_audit_log(filename: str, content: str) -> str:
    """
    Safely writes an analytical or operational audit summary report 
    to a designated secure file storage directory.
    """
    # Security Check: Enforce a strict file path directory jail (Least Privilege)
    target_path = os.path.abspath(os.path.join(SAFE_DIR, filename))
    if not target_path.startswith(SAFE_DIR):
        return "[SECURITY VIOLATION] Attempted directory traversal blocked! Access denied."
    
    try:
        with open(target_path, "w") as f:
            f.write(content)
        return f"[FILESYSTEM SUCCESS] Log written successfully to sandbox directory: {filename}"
    except Exception as e:
        return f"Failed to modify file system: {str(e)}"

# =====================================================================
# 4. RUN SERVER ENVIRONMENT
# =====================================================================
if __name__ == "__main__":
    print("\n🚀 [STARTING] Launching E-Commerce MCP Server over standard I/O (stdio)...")
    print("💡 Connect this server path to your Claude Desktop App configuration to interface with AI.")
    # FastMCP defaults to standard I/O (stdio) transport, making it natively plug-and-play
    mcp.run()
