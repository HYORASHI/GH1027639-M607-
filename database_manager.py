import sqlite3
from werkzeug.security import generate_password_hash # type: ignore

class DatabaseManager:
    def __init__(self, db_name='ecommerce.db'):
        self.db_name = db_name
        self.create_tables()

    def connect(self):
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        """Create users, products, and cart tables if they do not exist."""
        conn = self.connect()

        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          username TEXT UNIQUE NOT NULL,
                          password TEXT NOT NULL,
                          email TEXT,
                          address TEXT,
                          is_admin INTEGER DEFAULT 0)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT NOT NULL,
                          price REAL NOT NULL,
                          category TEXT NOT NULL,
                          image_url TEXT)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS cart (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            product_id INTEGER NOT NULL,
                            quantity INTEGER DEFAULT 1,
                            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                            FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
                          ) ''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            total_price REAL NOT NULL,
                            date TEXT DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                            )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS order_items (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            order_id INTEGER NOT NULL,
                            product_id INTEGER NOT NULL,
                            quantity INTEGER NOT NULL,
                            price REAL NOT NULL,
                            FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE,
                            FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
                        )''')

        conn.commit()
        conn.close()

    def create_admin_user(self):
        """Creates an admin user if none exists"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE is_admin = 1")
        existing_admin = cursor.fetchone()

        if not existing_admin:
            hashed_password = generate_password_hash("adminpassword", method="pbkdf2:sha256")
            cursor.execute(
                "INSERT INTO users (username, password, email, address, is_admin) VALUES (?, ?, ?, ?, ?)",
                ("admin", hashed_password, "admin@gmail.com", "123 Admin St", 1)
            )
            conn.commit()
            print("✅ Admin user created successfully!")
        else:
            print("⚠️ Admin user already exists.")

        conn.close()

    def add_user(self, username, password, email, address, is_admin=False):
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (username, password, email, address, is_admin) VALUES (?, ?, ?, ?, ?)",
                            (username, password, email, address, 1 if is_admin else 0))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
    
    def update_user_details(self, user_id, email, address):
        """Update user details (email, address) in the database."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET email = ?, address = ? WHERE id = ?", (email, address, user_id))
            conn.commit()

    def insert_test_user(self):
        """Insert a test admin user with a hashed password if it does not exist."""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        existing_admin = cursor.fetchone()

        if not existing_admin:
            hashed_password = generate_password_hash("adminpassword", method="pbkdf2:sha256")
            cursor.execute("INSERT INTO users (username, password, email, address, is_admin) VALUES (?, ?, ?, ?, ?)",
                        ("admin", hashed_password, "admin@gmail.com", "123 Main St, Anytown, USA", 1))
            conn.commit()
            print("✅ Admin user created successfully!")
        else:
            print("⚠️ Admin user already exists.")

        conn.close()

    def insert_products(self):
        """Insert products only if the database is empty."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]

        if count == 0:
            products = [
                ('Laptop', 1000.00, 'Electronics', 'laptop.jpg'),
                ('Phone', 700.00, 'Electronics', 'phone.jpg'),
                ('Smartwatch', 250.00, 'Accessories', 'smartwatch.jpg'),
                ('Microwave', 200.00, 'Home Appliance', 'microwave.jpg'),
                ('Vacuum Cleaner', 300.00, 'Home Appliance', 'vacuum_cleaner.jpg'),
                ('Blender', 50.00, 'Home Appliance', 'blender.jpg'),
                ('Sneaker', 30.00, 'Fashion', 'sneaker.jpg'),
                ('Handbag', 100.00, 'Fashion', 'handbag.jpg'),
                ('Sunglass', 150.00, 'Fashion', 'sunglass.jpg'),
                ('Hoodie', 20.00, 'Fashion', 'Hoodie.jpg') 
            ]
            cursor.executemany("INSERT INTO products (name, price, category, image_url) VALUES (?, ?, ?, ?)", products)
            conn.commit()

        conn.close()

    def get_all_products(self):
        """Retrieve all products from the database."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        conn.close()
        return products

    def get_product_by_id(self, product_id):
        """Retrieve product details by ID."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
            return cursor.fetchone()

    def get_recommendations(self, product_id):
        """Get recommended products based on the same category."""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT category FROM products WHERE id=?", (product_id,))
        category = cursor.fetchone()

        if category:
            cursor.execute("SELECT id, name, price, image_url FROM products WHERE category=? AND id!=?", (category[0], product_id))
            recommendations = cursor.fetchall()
        else:
            recommendations = []

        conn.close()
        return [{'id': p[0], 'name': p[1], 'price': p[2], 'image_url': p[3]} for p in recommendations]

    def get_cart_items(self, user_id):
        """Retrieve cart items for a specific user."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT cart.id, products.name, products.price, cart.quantity, products.image_url, products.id 
                FROM cart 
                JOIN products ON cart.product_id = products.id 
                WHERE cart.user_id = ?
            ''', (user_id,))
            cart_items = cursor.fetchall()

            return [{'id': item[0], 'name': item[1], 'price': item[2], 'quantity': item[3], 'image_url': item[4], 'product_id': item[5]} for item in cart_items]

    def add_to_cart(self, user_id, product_id):
        """Add product to cart, increasing quantity if already exists."""
        with self.connect() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT quantity FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
            item = cursor.fetchone()

            if item:
                cursor.execute("UPDATE cart SET quantity = quantity + 1 WHERE user_id = ? AND product_id = ?", (user_id, product_id))
            else:
                cursor.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, 1)", (user_id, product_id))
            
            conn.commit()

    def remove_from_cart(self, cart_id):
        """Remove a product from the cart."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cart WHERE id=?", (cart_id,))
        conn.commit()
        conn.close()

    def get_user(self, username):
        """Retrieve user details for authentication (without checking password in SQL)."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, password, is_admin FROM users WHERE username=?", (username,))
            return cursor.fetchone()

    def get_user_details(self, user_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username, email, address FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            if user:
                return {"username": user[0], "email": user[1], "address": user[2]}
            return None

    def get_user_orders(self, user_id):
        """Retrieve all orders for a specific user, including products."""
        with self.connect() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id, total_price, date FROM orders WHERE user_id = ?", (user_id,))
            orders = cursor.fetchall()

            all_orders = []
            for order in orders:
                order_id, total_price, date = order

                cursor.execute("""
                    SELECT products.name, order_items.quantity, order_items.price, products.image_url
                    FROM order_items
                    JOIN products ON order_items.product_id = products.id
                    WHERE order_items.order_id = ?
                """, (order_id,))
                items = cursor.fetchall()

                all_orders.append({
                    "id": order_id,
                    "total_price": total_price,
                    "date": date,
                    "items": [{"name": item[0], "quantity": item[1], "price": item[2], "image_url": item[3]} for item in items]
                })

            return all_orders

    def add_product(self, name, price, category, image_filename):
        """Insert a new product into the products table."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO products (name, price, category, image_url) VALUES (?, ?, ?, ?)",
                        (name, price, category, image_filename))
            conn.commit()

    def update_product(self, product_id, name, price, category, image_filename=None):
        """Update product details in the database."""
        with self.connect() as conn:
            cursor = conn.cursor()

            if image_filename:
                cursor.execute("UPDATE products SET name = ?, price = ?, category = ?, image_url = ? WHERE id = ?",
                            (name, price, category, image_filename, product_id))
            else:
                cursor.execute("UPDATE products SET name = ?, price = ?, category = ? WHERE id = ?",
                            (name, price, category, product_id))

            conn.commit()

    def delete_product(self, product_id):
        """Remove a product from the database."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()

    def create_order(self, user_id, total_price):
        """Insert a new order into the orders table and return the order ID."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO orders (user_id, total_price) VALUES (?, ?)", (user_id, total_price))
            conn.commit()
            return cursor.lastrowid  

    def add_order_item(self, order_id, product_id, quantity, price):
        """Insert order items into the order_items table."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                        (order_id, product_id, quantity, price))
            conn.commit()

    def clear_cart(self, user_id):
        """Remove all items from the user's cart after order placement."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
            conn.commit()

if __name__ == "__main__":
    db = DatabaseManager()
    db.create_admin_user()
