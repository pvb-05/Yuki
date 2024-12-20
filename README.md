# Yuki Shop
#### Video Demo: <https://youtu.be/sWNq20JYtl4>
#### Description:

**Yuki** is a comprehensive e-commerce web application built using the Flask framework. This project is designed to provide users with a seamless shopping experience, featuring functionalities such as user registration, login, product browsing, transaction management, and payment integration via PayOS. The project emphasizes simplicity, user-friendliness, and secure financial transactions. Yuki aims to bridge the gap between buyers and sellers by offering an intuitive and efficient platform for online shopping.

---

## Project Structure

### `static` Directory
This folder contains all the static assets required for the application, including images, CSS files, and other resources:
- **Images**:
  - `background`: Contains background images for various pages.
  - `carousel`: Houses images used in the carousel slider.
  - `top sale`: Includes images of top-selling products.
  - `collection`: Stores product images for the collection page.
- **CSS Files**: Stylesheets that define the design of specific pages:
  - `cancel.css`: Styling for the transaction cancellation page.
  - `cash.css`: Styling for cash payment pages.
  - `layout.css`: Defines the overall layout for the application.
  - `login.css` and `register.css`: Dedicated styles for login and registration forms.
  - `transaction.css`: Styles for the transaction history page.
- **Other Assets**: The `favicon` logo is also stored in this directory for branding.

### `templates` Directory
This folder contains the HTML templates used to render pages dynamically:
- **Base Template**:
  - `layout.html`: A reusable layout that provides a consistent structure for all pages.
- **Individual Pages**:
  - `index.html`: The homepage featuring highlighted products.
  - `login.html` and `register.html`: Templates for user authentication.
  - `collection.html` and `collection_search.html`: Pages for browsing and searching collections.
  - `transaction.html`: Displays user transaction history.
  - `success_cash.html` and `success_transfer.html`: Confirmations for successful transactions.
  - `cancel.html`: A page to display transaction cancellation details.
  - `help.html`: A support page for user assistance.

### `.env` File
This file stores sensitive configuration data required for PayOS payment integration:
- `PAYOS_CLIENT_ID`: The client ID used to authenticate with PayOS.
- `PAYOS_API_KEY`: API key for secure communication with PayOS services.
- `PAYOS_CHECKSUM_KEY`: A checksum key to ensure data integrity during transactions.

### `.gitignore` File
Contains a list of files and directories that should not be tracked by Git, including:
- `.env`: To prevent sensitive data from being exposed.

### `Procfile`
Used for deployment on platforms like Render. It specifies the entry point for the application:
```web: gunicorn app:app```


### `requirements.txt` File
Lists all the Python dependencies required to run the project:
- `Flask==3.1.0`
- `bcrypt==4.2.1`
- `Flask-Session==0.8.0`
- `mysql-connector-python==9.1.0`
- `gunicorn==23.0.0`
- `payos==0.1.8`
# Additional libraries for functionality...

### `yuki.db`
The SQLite database that powers the backend of the application. It contains three main tables:
- `items`: Stores product information.
- `users`: Manages user data, including encrypted passwords.
- `transactions`: Logs all user transactions for future reference.

### `myvirtualenvironment` Directory
This folder is created when setting up a Python virtual environment for the project. It contains all the installed libraries and dependencies.

### `app.py`
The core of the Yuki application, containing all the routes and backend logic. Key functionalities include:
Home Page (/): Displays featured products and promotional banners.
Authentication:
-`login`: Allows users to log into their accounts.
- `register`: Enables new users to create accounts.
- `logout`: Logs users out and clears session data.
Product Pages:
- `collection`: Displays all products grouped by categories.
- `item/<item_id>`: Shows detailed information about a specific product.
Transactions:
- `transfer/<item_id>`: Handles payments via PayOS.
- `cash/<item_id>`: Facilitates cash-on-delivery payments.
- `transaction`: Lists all past user transactions.
Utility Pages:
- `help`: Provides assistance to users.
- `cancel`: Displays information about canceled transactions.


## Design Choices
- **Flask Framework**: Flask was chosen for its simplicity and flexibility, making it ideal for small to medium-scale projects. Its lightweight nature allows for faster development and easier debugging.
- **PayOS Integration**: PayOS was selected for its ease of use and robust API for secure financial transactions.
- **Database**: SQLite was used for rapid prototyping and simplicity. Future versions may migrate to MySQL for better scalability.

---

## Setup and Usage
**Set up a virtual environment**:
- python -m venv myvirtualenvironment
- source myvirtualenvironment/bin/activate 

**Install dependencies**:
- pip install -r requirements.txt

**Configure environment variables**:
Create a .env file with the following keys:
- PAYOS_CLIENT_ID=<your_client_id>
- PAYOS_API_KEY=<your_api_key>
- PAYOS_CHECKSUM_KEY=<your_checksum_key>

**Run the application**:
- python app.py
- Access the app at http://127.0.0.1:5000.