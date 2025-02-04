from flask import Flask,render_template,request,session,redirect,url_for
from pymongo import MongoClient
from werkzeug.utils import secure_filename   
from bson import ObjectId
from datetime import datetime
import os

api=Flask(__name__)
api.secret_key="1234567890"

cluster=MongoClient("mongodb://127.0.0.1:27017")
db=cluster['project']
uregister=db['user']
viewproduct=db['auction']
addproduct=db['products']


UPLOAD_FOLDER = 'static/uploads/'  # Set your desired folder
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@api.route("/")
def index():
    print("hellow")
    return render_template("index.html")

@api.route("/ureg")
def ureg():
    return render_template("signup.html")

@api.route("/ulog")
def ulog():
    return render_template("login.html")

@api.route("/additem")
def additem():
    return render_template("sell_items.html")

@api.route("/additemss" ,methods=["post"])
def additemss():
    return render_template("sell_items.html")


@api.route("/partauction")
def partauction():
    return render_template("auction.html")

@api.route("/home" , methods=["post"])
def home():
    return render_template("home.html")

@api.route("/biditem")
def biditem():
    return render_template("biditem.html")

@api.route("/showsellitems")
def showsellitems():
    return render_template("show_sell_items_details.html")

@api.route("/biditems")
def biditems():
    return render_template("biditem.html")


@api.route("/userregister",methods=['post'])
def userregister():
    uname=request.form.get("username")
    uemail=request.form.get("email")
    upass=request.form.get("password")
    uconpass=request.form.get("confirm_password")
    print(uname,uemail,upass,uconpass)
    user = uregister.find_one({"username": uname})
    if upass!=uconpass:
        return render_template("signup.html",status="Passwords doesn't match")
    if user:
        return render_template("signup.html",status="User Already Existed")
    uregister.insert_one({"username": uname,"email": uemail,"password": upass})
    return render_template("signup.html",status="Registration Successful")

@api.route("/userlogin",methods=['post'])
def userlogin():
    uname=request.form.get("Username")
    upass=request.form.get("Password")
    print(uname,upass)
    user=uregister.find_one({"username": uname})
    if user:
        if user["password"] == upass:
            session['username']=uname
            return render_template("home.html")
       
    return render_template("login.html",status="Invalid Login Credentials")
    

@api.route('/additemdetails', methods=['POST'])
def additemdetails():
    try:
        # Retrieve form data
        item_name = request.form['itemName']
        category = request.form['category']
        description = request.form['description']
        base_price = float(request.form['basePrice'])  # Convert to float
        uploaded_files = request.files.getlist('images[]')

        # Validate and save uploaded files
        saved_file_paths = []
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(api.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                saved_file_paths.append(filepath)
            else:
                return "Invalid file type.", 400

        # Prepare data for MongoDB
        item_data = {
            "itemName": item_name,
            "category": category,
            "description": description,
            "basePrice": base_price,
            "images": saved_file_paths
        }

        # Insert data into MongoDB
        addproduct.insert_one(item_data)

        # Redirect to a success page or home
        return render_template("show_sell_items_details.html")

    except Exception as e:
        return f"An error occurred: {e}", 500


if __name__=="__main__":
    api.run(port=5000,debug=True)

