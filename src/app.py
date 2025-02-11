import os
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from bson import ObjectId
from datetime import datetime

app = Flask(__name__)
app.secret_key = "1234567890"

# Database Connection
cluster = MongoClient("mongodb://127.0.0.1:27017")
db = cluster['auction_project']
users = db['users']
items = db['auction_items']
bids = db['bids']

# File Upload Configuration
UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    """Render the homepage."""
    return render_template("index.html")

@app.route("/register")
def register_page():
    """Render the signup page."""
    return render_template("signup.html")

@app.route("/login")
def login_page():
    """Render the login page."""
    return render_template("login.html")

@app.route("/home")
def home_page():
    return render_template("home.html")

@app.route("/item")
def add_items():
    return render_template("sell_items.html")

@app.route("/signup", methods=['POST'])
def user_register():
    """Handle user signup."""
    username = request.form["Username"]
    email = request.form["Email"]
    password = request.form["Password"]
    confirm_password = request.form["ConfirmPassword"]

    if password != confirm_password:
        return render_template("signup.html", status="Passwords don't match")

    if users.find_one({"username": username}):
        return render_template("signup.html", status="User already exists")

    users.insert_one({"username": username, "email": email, "password": password})
    return render_template("signup.html", status="Registration Successful")

@app.route("/login", methods=['POST'])
def user_login():
    """Handle user login."""
    username = request.form.get("Username")
    password = request.form.get("Password")

    user = users.find_one({"username": username})
    if user and user["password"] == password:
        session['username'] = username
        return redirect("/home")

    return render_template("login.html", status="Invalid Login Credentials")

@app.route("/sellitems")
def sell_items():
    """Render the Sell Items page."""
    if 'username' not in session:
        return redirect(url_for('login_page'))
    return render_template("sellitems.html")

@app.route("/additem", methods=['POST'])
def add_item():
    """Handle form submission for adding auction items."""
    if 'username' not in session:
        return redirect(url_for('login_page'))

    item_name = request.form["itemName"]
    category = request.form["category"]
    description = request.form["description"]
    base_price = int(request.form["basePrice"])
    seller = session["username"]

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Handle image uploads
    image_urls = []
    if 'images[]' in request.files:
        images = request.files.getlist('images[]')  # Indentation fixed
        for image in images:
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                print(filepath)
                try:
                    print(f"Saving image to: {filepath}")
                    image.save(filepath)
                    print(f"✅ Successfully saved: {filepath}")
                    image_urls.append(filename)  # Store only the filename
                except Exception as e:
                    print(f"❌ Error saving image: {e}")

    # Store item details in MongoDB
    item = {
        "name": item_name,
        "category": category,
        "description": description,
        "base_price": base_price,
        "current_price": base_price,
        "highest_bidder": None,
        "seller": seller,
        "images": image_urls,  # Store only the filenames
        "created_at": datetime.utcnow()
    }
    items.insert_one(item)

    return redirect(url_for('home_page'))

@app.route("/bid/<item_id>", methods=['POST'])
def place_bid(item_id):
    """Allows a user to place a bid on an auction item."""
    if 'username' not in session:
        return jsonify({"error": "You must be logged in to place a bid"}), 401

    username = session["username"]
    bid_amount = int(request.form["bidAmount"])

    item = items.find_one({"_id": ObjectId(item_id)})
    if not item:
        return jsonify({"error": "Item not found"}), 404

    if bid_amount <= item["current_price"]:
        return jsonify({"error": "Bid must be higher than the current price"}), 400

    items.update_one(
        {"_id": ObjectId(item_id)},
        {"$set": {"current_price": bid_amount, "highest_bidder": username}}
    )

    # Store bid in separate collection
    bids.insert_one({
        "item_id": ObjectId(item_id),  # Fixing item_id to be stored as ObjectId
        "bidder": username,
        "amount": bid_amount,
        "timestamp": datetime.utcnow()
    })

    return jsonify({"success": "Bid placed successfully!"})

@app.route("/get_auction_items", methods=['GET'])
def get_auction_items():
    """API to fetch all auction items."""
    items_list = list(items.find({}))
    for item in items_list:
        item["_id"] = str(item["_id"])
        # Generate full URLs for the images
        item["images"] = [url_for('static', filename=f'uploads/{filename}', _external=True) for filename in item["images"]]
    return jsonify(items_list)

@app.route("/logout")
def logout():
    """Handle user logout."""
    session.pop('username', None)
    return redirect(url_for('login_page'))

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000, debug=True)