import sqlite3

DB_FILE = 'inventory.db'

def connect_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        raise Exception(f"Failed to connect to database: {str(e)}")

def create_tables():
    conn = None
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity >= 0),
            price REAL NOT NULL CHECK(price >= 0),
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
        ''')
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_user_id ON inventory(user_id)
        ''')
        cursor.execute("PRAGMA table_info(inventory)")
        cols = [row[1] for row in cursor.fetchall()]
        if 'product_no' not in cols:
            cursor.execute("ALTER TABLE inventory ADD COLUMN product_no INTEGER")
            cursor.execute("SELECT DISTINCT user_id FROM inventory")
            user_ids = [row[0] for row in cursor.fetchall()]
            for uid in user_ids:
                cursor.execute("SELECT id FROM inventory WHERE user_id = ? ORDER BY id ASC", (uid,))
                ids = [row[0] for row in cursor.fetchall()]
                for idx, inv_id in enumerate(ids, start=1):
                    cursor.execute("UPDATE inventory SET product_no = ? WHERE id = ?", (idx, inv_id))
        cursor.execute('''
        CREATE UNIQUE INDEX IF NOT EXISTS ux_inventory_user_product_no
        ON inventory(user_id, product_no)
        ''')
        conn.commit()
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise Exception(f"Failed to create tables: {str(e)}")
    finally:
        if conn:
            conn.close()

def register_user(username, password):
    if not username or not password:
        raise ValueError("Username and password are required")
    
    conn = None
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                      (username.strip(), password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise Exception(f"Database error during registration: {str(e)}")
    finally:
        if conn:
            conn.close()

def check_user(username, password):
    if not username or not password:
        return None
    
    conn = None
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username = ?", (username.strip(),))
        user_data = cursor.fetchone()
        if user_data:
            user_id, stored_password = user_data
            if stored_password == password:
                return user_id
        return None
    except sqlite3.Error as e:
        raise Exception(f"Database error during login: {str(e)}")
    finally:
        if conn:
            conn.close()

def add_product(user_id, name, quantity, price):
    if not user_id:
        raise ValueError("User ID is required")
    if not name or not name.strip():
        raise ValueError("Product name is required")
    if quantity < 0:
        raise ValueError("Quantity cannot be negative")
    if price < 0:
        raise ValueError("Price cannot be negative")
    
    conn = None
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(MAX(product_no), 0) + 1 FROM inventory WHERE user_id = ?", (user_id,))
        next_no = cursor.fetchone()[0]
        cursor.execute("INSERT INTO inventory (user_id, product_name, quantity, price, product_no) VALUES (?, ?, ?, ?, ?)",
                      (user_id, name.strip(), quantity, price, next_no))
        conn.commit()
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise Exception(f"Failed to add product: {str(e)}")
    finally:
        if conn:
            conn.close()

def view_products(user_id):
    if not user_id:
        raise ValueError("User ID is required")
    
    conn = None
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT product_no, product_name, quantity, price FROM inventory WHERE user_id = ? ORDER BY product_no DESC", 
                      (user_id,))
        rows = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        raise Exception(f"Failed to retrieve products: {str(e)}")
    finally:
        if conn:
            conn.close()

def update_product(user_id, product_no, name, quantity, price):
    if not user_id or not product_no:
        raise ValueError("User ID and product number are required")
    if not name or not name.strip():
        raise ValueError("Product name is required")
    if quantity < 0:
        raise ValueError("Quantity cannot be negative")
    if price < 0:
        raise ValueError("Price cannot be negative")
    
    conn = None
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE inventory SET product_name = ?, quantity = ?, price = ? WHERE user_id = ? AND product_no = ?",
                      (name.strip(), quantity, price, user_id, product_no))
        if cursor.rowcount == 0:
            raise ValueError(f"Product with number {product_no} not found for this user")
        conn.commit()
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise Exception(f"Failed to update product: {str(e)}")
    finally:
        if conn:
            conn.close()

def delete_product(user_id, product_no):
    if not user_id or not product_no:
        raise ValueError("User ID and product number are required")
    
    conn = None
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventory WHERE user_id = ? AND product_no = ?", (user_id, product_no))
        if cursor.rowcount == 0:
            raise ValueError(f"Product with number {product_no} not found for this user")
        conn.commit()
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise Exception(f"Failed to delete product: {str(e)}")
    finally:
        if conn:
            conn.close()

try:
    create_tables()
except Exception as e:
    print(f"Warning: Database initialization failed: {str(e)}")
