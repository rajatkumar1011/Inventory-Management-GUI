import sqlite3
import os

DB_FILE = 'inventory_app.db'

def connect_db():
    """Create and return a database connection"""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        raise Exception(f"Failed to connect to database: {str(e)}")

def create_tables():
    """Create necessary database tables if they don't exist"""
    conn = None
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        ''')
        
        # Create inventory table
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
        
        # Create index for better performance
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_user_id ON inventory(user_id)
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
    """
    Register a new user
    Returns True if successful, False if username already exists
    """
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
    """
    Check if username and password are valid
    Returns user_id if valid, None otherwise
    """
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
    """Add a new product to inventory"""
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
        
        cursor.execute("INSERT INTO inventory (user_id, product_name, quantity, price) VALUES (?, ?, ?, ?)",
                      (user_id, name.strip(), quantity, price))
        conn.commit()
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise Exception(f"Failed to add product: {str(e)}")
    finally:
        if conn:
            conn.close()

def view_products(user_id):
    """Get all products for a specific user"""
    if not user_id:
        raise ValueError("User ID is required")
    
    conn = None
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, product_name, quantity, price FROM inventory WHERE user_id = ? ORDER BY id DESC", 
                      (user_id,))
        rows = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        raise Exception(f"Failed to retrieve products: {str(e)}")
    finally:
        if conn:
            conn.close()

def update_product(product_id, name, quantity, price):
    """Update an existing product"""
    if not product_id:
        raise ValueError("Product ID is required")
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
        
        cursor.execute("UPDATE inventory SET product_name = ?, quantity = ?, price = ? WHERE id = ?",
                      (name.strip(), quantity, price, product_id))
        
        if cursor.rowcount == 0:
            raise ValueError(f"Product with ID {product_id} not found")
        
        conn.commit()
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise Exception(f"Failed to update product: {str(e)}")
    finally:
        if conn:
            conn.close()

def delete_product(product_id):
    """Delete a product from inventory"""
    if not product_id:
        raise ValueError("Product ID is required")
    
    conn = None
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM inventory WHERE id = ?", (product_id,))
        
        if cursor.rowcount == 0:
            raise ValueError(f"Product with ID {product_id} not found")
        
        conn.commit()
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise Exception(f"Failed to delete product: {str(e)}")
    finally:
        if conn:
            conn.close()

# Initialize database tables when module is imported
try:
    create_tables()
except Exception as e:
    print(f"Warning: Database initialization failed: {str(e)}")
