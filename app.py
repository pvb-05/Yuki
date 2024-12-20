import os
from dotenv import load_dotenv
import random
from payos import PaymentData, PayOS

import uuid
from functools import wraps
from flask_bcrypt import Bcrypt, check_password_hash
from flask import Flask, flash, render_template, request, redirect, session, jsonify
from cs50 import SQL
from flask_session import Session
 
# Cấu hình ứng dụng
app = Flask(__name__, static_folder='static',static_url_path='/static',template_folder='templates')

# Tạo đối tượng tạo mã băm
bcrypt = Bcrypt(app)

# Tạo khóa để dùng flash
app.secret_key = '15112005'

# Cấu hình phiên người dùng
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

load_dotenv()

# Cấu hình payos
payOS = PayOS(
    client_id = os.environ.get('PAYOS_CLIENT_ID'), 
    api_key = os.environ.get('PAYOS_API_KEY'), 
    checksum_key = os.environ.get('PAYOS_CHECKSUM_KEY')
)

# Tạo đối tượng con trỏ vào SQL của CS50
db = SQL("sqlite:///yuki.db")

# Hàm yêu cầu đăng nhập trước khi thao tác
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def get_user():
    if session.get("user_id"):
        user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        if user:
            return user  # Trả về thông tin người dùng
        session.clear()  # Xóa phiên nếu không tìm thấy người dùng
    return None

def get_items(item_id=None):
    if item_id:
        return db.execute("SELECT * FROM items WHERE id = ?",item_id)
    return db.execute("SELECT * FROM items")

# Chạy hàm khi ấn vô trang chủ
@app.route("/")
def index():
    # Nếu có id trong phiên tức là người dùng đã đăng nhập thì đổi trang chủ thành tên người dùng
    if session.get("user_id"): 
        # Lấy hàng dữ liệu chứa id người dùng và lưu dưới dạng dang sách từ điển (mỗi hàng là một từ điển)
        user = get_user()
        # Truyền đối số vào trang chủ để hiển thị chào mừng người dùng
        return render_template("index.html", user=user) 
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    # Xóa bỏ phiên người dùng trước nếu còn tồn tại 
    session.clear()
    
    if request.method == "GET":
        return render_template("login.html")
    else:
        account = request.form.get("account")
        gmail = request.form.get("email")
        password = request.form.get("password")
        user = db.execute("SELECT * FROM users WHERE account = ? AND email = ?",account,gmail)
        # Kiểm độ dài của danh sách = 0 (tức là không tồn tại tài khoản trên)
        if not user or len(user)!=1:
            return render_template("login.html")
        # Kiểm tra mật khẩu khớp với mật khẩu đã đăng kí hay chưa
        elif not check_password_hash(user[0]["password"],password):
            return render_template("login.html")
        else:
        # Tạo phiên người dùng sau khi đăng nhập thành công
            session["user_id"] = user[0]["id"]
            return redirect("/")
        
@app.route("/logout")
def logout():
    # Xóa bỏ phiên người dùng khi ấn đăng xuất
    session.clear()
    flash("You have been logged out.", "success")
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        account = request.form.get('account')
        gmail = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        # Kiểm tra mật khẩu khớp với mật khẩu nhập lại chưa
        if confirm != password:
            return render_template("register.html")
        else:
        # Kiểm tra người dùng có tồn tại trong cơ sở dữ liệu chưa
            existing_user = db.execute("SELECT * FROM users WHERE account = ? OR email = ?", account, gmail)
            if existing_user:
                return render_template("register.html")
            else:
                unique_uuid = "YUKI" + str(uuid.uuid4())[:8]
                password = bcrypt.generate_password_hash(password).decode('utf-8')
                db.execute("INSERT INTO users(id, account,email,password) VALUES(?,?,?,?)", unique_uuid, account,gmail,password)
                return redirect("/")
    
@app.route("/help", methods=["GET", "POST"])
@login_required
def help():
    if request.method == "GET":
        return render_template("help.html")
    else:
        return redirect("/")
    
@app.route("/collection")
@login_required
def collection():
    user = get_user()
    items = get_items()
    if request.method == "GET":
        return render_template("collection.html",user=user,items=items)

@app.route("/item/<string:item_id>")
@login_required
def item(item_id):
    user = get_user()
    item = get_items(item_id)
    if not item:
        return "Item not found", 404
    if request.method == "GET":
        return render_template("item.html",user=user,item=item)
    
@app.route("/transfer/<string:item_id>", methods=["GET", "POST"])
@login_required
def transfer(item_id):
    user = get_user()
    item = get_items(item_id)
    if not item:
        return "Item not found", 404
    if request.method == "GET":
        return render_template("transfer.html",user=user,item=item)
    elif request.method == "POST":
        address = request.form.get('address')
        phone = request.form.get('phone')
        if not address or not phone:  # Nếu thiếu thông tin, hiển thị lỗi
            flash("Address and phone are required.", "danger")
            return render_template("transfer.html", user=user, item=item)

        # Cập nhật thông tin vào cơ sở dữ liệu nếu hợp lệ
        db.execute("UPDATE users SET address = ? WHERE id = ?", address, user[0]['id'])
        db.execute("UPDATE users SET phone = ? WHERE id = ?", phone, user[0]['id'])
        try:
            price_str = request.form.get("price")
        except:
            flash("Price is missing.", "danger")
            return redirect(f"/transfer/{item_id}")
        try:
            price = int(price_str.replace('.', '').replace(' VNĐ',''))  # Loại bỏ dấu '.' và 'VNĐ'
        except ValueError:
            flash("Invalid price format.", "danger")
            return redirect(f"/transfer/{item_id}")
        
        domain = "https://yuki-glhj.onrender.com"
        try:
            paymentData = PaymentData(orderCode=random.randint(1000, 999999), 
                                      amount=price,
                                      description=f"PAY ITEM CODE {item_id}",
                                      cancelUrl=f"{domain}/cancel", 
                                      returnUrl=f"{domain}/success_transfer?item_id={item_id}")
            payosCreatePayment = payOS.createPaymentLink(paymentData)
            return jsonify(payosCreatePayment.to_json())
        except Exception as e:
            return jsonify(error=str(e)), 403
        
@app.route("/cash/<string:item_id>", methods=["GET", "POST"])
@login_required
def cash(item_id):
    user = get_user()
    item = get_items(item_id)

    if not item:
        return "Item not found", 404
    if request.method == "GET":
        return render_template("cash.html",user=user,item=item)
    elif request.method == "POST":
        address = request.form.get('address')
        phone = request.form.get('phone')
        order_code = random.randint(1000, 999999)
        try:
            order_code = str(order_code)
        except TypeError:
            flash("Create order code fail!")
            return redirect("/")
        
        if not address or not phone:  # Nếu thiếu thông tin, hiển thị lỗi
            flash("Address and phone are required.", "danger")
            return render_template("cash.html", user=user, item=item)

        # Cập nhật thông tin vào cơ sở dữ liệu nếu hợp lệ
        db.execute("UPDATE users SET address = ? WHERE id = ?", address, user[0]['id'])
        db.execute("UPDATE users SET phone = ? WHERE id = ?", phone, user[0]['id'])
        
        try:
        # Save transaction details to the database
            db.execute("INSERT INTO transactions (user_id, item_id, order_code, pay, status) VALUES (?, ?, ?, ?, ?)", session["user_id"], item_id, order_code, "UNPAID", "Waiting for order confirmation ...")
            return redirect("/success_cash")
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")
            return redirect("/")

@app.route("/success_transfer")
@login_required
def success_transfer():
    
    # Extract data sent by PayOS upon successful payment
    order_code = request.args.get("orderCode")
    pay = request.args.get("status", "success")  # Default status
    item_id = request.args.get("item_id")

    # Check if all required parameters exist
    if not order_code:
        flash("Missing payment data.", "danger")
        return redirect("/")
    
    try:
        # Save transaction details to the database
        db.execute("INSERT INTO transactions (user_id, item_id, order_code, pay, status) VALUES (?, ?, ?, ?, ?)", session["user_id"], item_id, order_code, pay, "Waiting for order confirmation ...")
        return redirect("/transaction")
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect("/")
    
@app.route("/success_cash")
@login_required
def success_cash():
    return render_template("/succes_cash.html")

@app.route("/cancel")
@login_required
def cancel():
    return render_template("cancel.html")
   
@app.route("/transaction")
@login_required
def transaction():
    user = get_user()
    transactions = db.execute("SELECT transactions.id AS transaction_id, transactions.order_code, transactions.pay, transactions.status, datetime(transactions.transaction_date, '+7 hours') AS transaction_date, items.id AS item_id, items.name AS item_name, items.price AS item_price FROM transactions JOIN items ON transactions.item_id = items.id WHERE transactions.user_id = ? ORDER BY transactions.transaction_date DESC", user[0]['id'])
    return render_template("transaction.html", user=user, transactions=transactions)

@app.route('/search', methods=['GET'])
@login_required
def search():
    user = get_user()
    query = request.args.get('q', '').lower()

    if not query:
        flash("Search query cannot be empty.", "danger")
        return redirect("/")
    
    items = db.execute("SELECT * FROM items WHERE LOWER(name) LIKE ?", f'%{query}%')

    if len(items) == 1:
        return redirect(f"/item/{items[0]['id']}")
    elif len(items) > 1:
        return render_template("/collection_search.html",user=user,items=items)
    else:
        # Nếu không tìm thấy kết quả
        flash("No items found matching your search.", "info")
        return redirect("/") 
    
if __name__ == "__main__":
    app.run(debug = True)



'''Chuẩn bị ứng dụng Flask
Trước khi triển khai, bạn cần đảm bảo:

Cấu trúc dự án rõ ràng:
arduino
Copy code
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── static/
│   └── templates/
├── requirements.txt
├── run.py
└── config.py
Tệp requirements.txt: Chứa danh sách thư viện Python cần thiết. Tạo bằng lệnh: pip freeze > requirements.txt'''

'''1. Chuẩn bị ứng dụng Flask
Cấu trúc thư mục
Đảm bảo ứng dụng của bạn có cấu trúc chuẩn, ví dụ:

css
Sao chép mã
my_flask_app/
│
├── app.py              # File chính
├── requirements.txt    # Các thư viện cần thiết
├── Procfile            # File cấu hình (quan trọng để triển khai)
├── templates/          # Thư mục chứa các file HTML
├── static/             # Thư mục chứa CSS, JS, hình ảnh
Tạo requirements.txt
Sử dụng lệnh sau để tạo file requirements.txt:

bash
Sao chép mã
pip freeze > requirements.txt
File này chứa danh sách các thư viện cần thiết để ứng dụng của bạn hoạt động.

Ví dụ nội dung requirements.txt:

makefile
Sao chép mã
Flask==2.3.2
gunicorn==21.2.0
Tạo Procfile
File Procfile hướng dẫn Render cách chạy ứng dụng của bạn. Tạo file này ở thư mục gốc và thêm nội dung:

makefile
Sao chép mã
web: gunicorn app:app
Trong đó:

app:app nghĩa là app.py là file chính và app là biến Flask của bạn.
2. Đăng ứng dụng lên Render
Tạo tài khoản Render
Truy cập Render.com và đăng ký tài khoản (nếu chưa có).
Liên kết tài khoản Render với GitHub hoặc GitLab để tự động triển khai từ repository của bạn.
Đưa ứng dụng lên GitHub
Nếu chưa có repository trên GitHub:

Khởi tạo Git trong thư mục ứng dụng:

bash
Sao chép mã
git init
git add .
git commit -m "Initial commit"
Tạo repository trên GitHub và đẩy code lên:

bash
Sao chép mã
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git branch -M main
git push -u origin main
Triển khai ứng dụng trên Render
Truy cập Render Dashboard.

Nhấn New > Web Service.

Chọn repository GitHub của bạn.

Điền các thông tin:

Name: Tên ứng dụng của bạn.
Branch: main hoặc nhánh bạn muốn triển khai.
Build Command: (Để trống, Render tự phát hiện Flask).
Start Command: gunicorn app:app.
Nhấn Create Web Service.

Render sẽ tự động build và triển khai ứng dụng của bạn. Sau khi hoàn tất, bạn sẽ nhận được URL của ứng dụng (ví dụ: https://my-flask-app.onrender.com).

3. Kiểm tra và cập nhật
Mỗi khi bạn cập nhật ứng dụng, chỉ cần git push code lên GitHub, Render sẽ tự động cập nhật phiên bản mới.
Kiểm tra log tại Render Dashboard nếu gặp lỗi.
'''