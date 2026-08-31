import sqlite3
import random
import string
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "store.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        language TEXT DEFAULT 'en',
        region TEXT DEFAULT 'PK',
        balance_pkr REAL DEFAULT 0.0,
        balance_usd REAL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Products table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        price_pkr REAL NOT NULL,
        price_usd REAL NOT NULL,
        stock_count INTEGER DEFAULT 10,
        icon TEXT DEFAULT '📦',
        active INTEGER DEFAULT 1
    );
    """)

    # Orders table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        price_paid REAL NOT NULL,
        currency TEXT NOT NULL,
        status TEXT DEFAULT 'PENDING_DELIVERY',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    );
    """)

    # Deposits / Payments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS deposits (
        deposit_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        payment_method TEXT NOT NULL,
        amount REAL NOT NULL,
        currency TEXT NOT NULL,
        tx_reference TEXT,
        status TEXT DEFAULT 'PENDING',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Replacements / Claims table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS replacements (
        claim_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        issue_details TEXT NOT NULL,
        status TEXT DEFAULT 'OPEN',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()
    seed_default_products()

def seed_default_products():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as count FROM products")
    if cursor.fetchone()['count'] == 0:
        default_items = [
            # Category, Name, Desc, Price PKR, Price USD, Stock, Icon
            ("AI Tools", "ChatGPT Plus (Shared)", "Shared ChatGPT Plus Account 1 Month", 850.0, 3.0, 50, "🤖"),
            ("AI Tools", "ChatGPT Plus (Private)", "Private ChatGPT Plus Account 1 Month", 5500.0, 20.0, 20, "🤖"),
            ("AI Tools", "Gemini Pro / Advanced", "Google Gemini Advanced 1 Month", 1200.0, 4.5, 30, "🤖"),
            ("Design", "Canva Pro (Private/Invite)", "Canva Pro Invite Link / Private 1 Year", 500.0, 2.0, 100, "🎨"),
            ("Design", "Envato Elements", "Envato Elements Unlimited Downloads 1 Month", 1500.0, 5.5, 25, "🎨"),
            ("Design", "CapCut Pro", "CapCut Pro Desktop & Mobile 1 Month", 950.0, 3.5, 40, "🎨"),
            ("Streaming", "Netflix Premium 4K UHD", "Private Profile with PIN 1 Month", 1100.0, 4.0, 50, "🎬"),
            ("Streaming", "Amazon Prime Video", "Private Screen 1 Month", 450.0, 1.8, 30, "🎬"),
            ("Streaming", "HBO Max", "HBO Max Private Screen 1 Month", 800.0, 3.0, 20, "🎬"),
            ("Streaming", "Paramount+", "Paramount Plus Private Profile 1 Month", 750.0, 2.8, 15, "🎬"),
            ("Streaming", "IPTV Premium (1 Year)", "10,000+ Channels & VOD 1 Year", 3500.0, 13.0, 50, "📺"),
            ("VPN", "NordVPN Premium", "NordVPN Shared/Private 1 Year", 990.0, 3.8, 40, "🛡️"),
            ("VPN", "ExpressVPN Premium", "ExpressVPN Premium Key/Account 1 Month", 1450.0, 5.2, 25, "🛡️"),
            ("VPN", "TunnelBear VPN", "TunnelBear Unlimited Data 1 Year", 900.0, 3.5, 30, "🛡️"),
        ]
        
        cursor.executemany("""
        INSERT INTO products (category, name, description, price_pkr, price_usd, stock_count, icon)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, default_items)
        conn.commit()
    conn.close()

def generate_order_id():
    """Generates an indigenous, unique order ID like AHG-8F92K"""
    rand_str = ''.join(random.choices(string.ascii_upper_case + string.digits, k=5))
    return f"AHG-{rand_str}"

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
