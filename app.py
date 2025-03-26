from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import secrets
from database_manager import DatabaseManager  

# Flask App Setup
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Improved secret key generation for security
app.config['UPLOAD_FOLDER'] = "static/images/"
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed file types for image uploads

# Initialize Database Manager
db = DatabaseManager()

# Utility function to check if file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            return render_template('login.html', error="Username and password are required!")

        user = db.get_user(username) 

        if user and check_password_hash(user[2], password):  # Check hashed password
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['is_admin'] = bool(user[3])  

            return redirect(url_for('admin' if session['is_admin'] else 'home'))  

        return render_template('login.html', error="Invalid username or password!")

    return render_template('login.html')

# Admin Page
@app.route('/admin')
def admin():
    if not session.get('is_admin'):
        return redirect(url_for('login'))

    products = db.get_all_products()
    return render_template('admin.html', products=products)

# Add Product
@app.route('/add_product', methods=['POST'])
def add_product():
    if not session.get('is_admin'):
        return redirect(url_for('login'))

    name = request.form['name']
    price = request.form['price']
    category = request.form['category']
    image = request.files['image']

    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        db.add_product(name, price, category, filename)
        return redirect(url_for('admin'))
    return render_template('add_product.html', error="Invalid image format! Allowed formats are .png, .jpg, .jpeg, .gif")

# Delete Product
@app.route('/delete_product/<int:product_id>')
def delete_product(product_id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))

    db.delete_product(product_id)
    return redirect(url_for('admin'))

# Edit Product
@app.route('/edit_product/<int:product_id>')
def edit_product(product_id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))

    product = db.get_product_by_id(product_id)

    if not product:
        return redirect(url_for('admin'))

    return render_template('edit_product.html', product=product)

@app.route('/update_product/<int:product_id>', methods=['POST'])
def update_product(product_id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))

    name = request.form['name']
    price = request.form['price']
    category = request.form['category']
    image = request.files['image']

    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        db.update_product(product_id, name, price, category, filename)
    else:
        db.update_product(product_id, name, price, category)

    return redirect(url_for('admin'))

@app.route('/')
def home():
    user_id = session.get('user_id')
    category = request.args.get('category', 'all')

    if category == 'all':
        products = db.get_all_products()
    else:
        products = db.get_products_by_category(category)

    return render_template('index.html', products=products, user_id=user_id)

@app.route('/profile')
def profile():
    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for('login'))

    user = db.get_user_details(user_id)

    return render_template('profile.html', user=user)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for('login'))

    email = request.form['email']
    address = request.form['address']

    db.update_user_details(user_id, email, address)

    return redirect(url_for('profile'))

@app.route('/product/<int:product_id>')
def product_details(product_id):
    product = db.get_product_by_id(product_id)
    if not product:
        return redirect(url_for('home'))

    return render_template('product_details.html', product=product)

@app.route('/cart/preview')
def cart_preview():
    user_id = session.get('user_id') 
    if not user_id:
        return jsonify({"items": [], "total": 0.00})

    cart_items = db.get_cart_items(user_id)  

    total_price = sum(item.get('price', 0) for item in cart_items)  

    return jsonify({"items": cart_items, "total": round(total_price, 2)}) 

@app.route('/cart')
def cart():
    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for('login'))

    cart_items = db.get_cart_items(user_id) 
    total_price = sum(item['price'] * item['quantity'] for item in cart_items)

    return render_template('cart.html', cart_items=cart_items, total_price=total_price, user_id=user_id)

@app.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for('login'))

    db.add_to_cart(user_id, product_id)

    return redirect(url_for('cart'))

@app.route('/cart/remove/<int:cart_id>', methods=['POST'])
def remove_from_cart(cart_id):
    if 'user_id' not in session:
        return redirect(url_for('login')) 

    db.remove_from_cart(cart_id)
    return redirect(url_for('cart'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        address = request.form['address']
        is_admin = 'is_admin' in request.form  

        if not username or not password or not email:
            return render_template('register.html', error="All fields are required!")

        hashed_password = generate_password_hash(password)

        if db.add_user(username, hashed_password, email, address, is_admin):
            return redirect(url_for('login'))
        else:
            return render_template('register.html', error="Username already taken!")

    return render_template('register.html')

@app.route('/buy_now/<int:product_id>', methods=['POST'])
def buy_now(product_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    product = db.get_product_by_id(product_id)
    if not product:
        return redirect(url_for('home'))

    return render_template('checkout.html', product=product, user_id=user_id)

@app.route('/checkout')
def checkout():
    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for('login')) 

    cart_items = db.get_cart_items(user_id)
    total_price = sum(item['price'] * item['quantity'] for item in cart_items)

    return render_template('checkout.html', cart_items=cart_items, total_price=total_price)

@app.route('/orders')
def orders():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    orders = db.get_user_orders(user_id)
    return render_template('orders.html', orders=orders, user_id=user_id)

@app.route('/confirm_order')
def confirm_order():
    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for('login'))

    cart_items = db.get_cart_items(user_id) 
    total_price = sum(item['price'] * item['quantity'] for item in cart_items)

    return render_template('confirm_order.html', cart_items=cart_items, total_price=total_price)

@app.route('/place_order', methods=['POST'])
def place_order():
    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for('login'))

    cart_items = db.get_cart_items(user_id) 
    if not cart_items:
        return redirect(url_for('cart'))

    total_price = sum(item['price'] * item['quantity'] for item in cart_items)

    order_id = db.create_order(user_id, total_price)

    for item in cart_items:
        db.add_order_item(order_id, item['product_id'], item['quantity'], item['price'])

    db.clear_cart(user_id)

    return redirect(url_for('order_success'))

@app.route('/order_success')
def order_success():
    return render_template('order_success.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    db.create_tables()
    db.insert_products()
    db.insert_test_user()
    app.run(debug=True)