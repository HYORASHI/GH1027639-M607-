# E-Commerce Web Application

## Overview
This is a Flask-based e-commerce web application that allows users to browse products, add them to a cart, and place orders. It includes user authentication, an admin panel for product management, and database integration using SQLite.

## Features
- User authentication (login, logout, register)
- Admin panel for managing products
- Product browsing and category filtering
- Shopping cart functionality
- Order placement and checkout
- User profile management

## Technologies Used
- **Backend:** Flask (Python)
- **Database:** SQLite
- **Frontend:** HTML, CSS, Jinja2 templates
- **Security:** Password hashing with `werkzeug.security`
- **File Uploads:** `werkzeug.utils.secure_filename`

## Installation and Setup
### Prerequisites
- Python 3.x installed
- Flask and dependencies installed (`pip install flask werkzeug`)

### Steps
1. Clone this repository:
   ```sh
   git clone https://github.com/yourrepo/ecommerce-app.git
   cd ecommerce-app
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the application:
   ```sh
   python app.py
   ```
4. Access the application at `http://127.0.0.1:5000/`

## Project Structure
```
|-- static/
|-- templates/
|-- app.py
|-- database_manager.py
|-- requirements.txt
|-- README.md
```

## API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page with product listings |
| `/login` | GET, POST | User login |
| `/register` | GET, POST | User registration |
| `/logout` | GET | User logout |
| `/profile` | GET | User profile page |
| `/update_profile` | POST | Update user profile |
| `/admin` | GET | Admin panel |
| `/add_product` | POST | Add a new product (Admin only) |
| `/delete_product/<id>` | GET | Delete a product (Admin only) |
| `/edit_product/<id>` | GET | Edit product details (Admin only) |
| `/update_product/<id>` | POST | Update product (Admin only) |
| `/cart` | GET | View cart |
| `/cart/add/<id>` | POST | Add item to cart |
| `/cart/remove/<id>` | POST | Remove item from cart |
| `/checkout` | GET | Checkout page |
| `/place_order` | POST | Place an order |
| `/orders` | GET | View user orders |

## Admin Credentials
- Default Admin Username: `admin`
- Default Password: `adminpassword`

## Security Considerations
- User passwords are hashed before storage.
- Sessions are used for authentication.
- Product images are stored securely.

## Future Improvements
- Add a payment gateway integration.
- Implement a recommendation system for users.
- Improve UI with responsive design.

## License
This project is licensed under the MIT License.

