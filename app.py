from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import json, bcrypt

app = Flask(__name__)
# Add this route to app.py (after app = Flask(__name__))
@app.route("/")
def index():
    return jsonify({
        "message": "ShopZone API is running! 🚀",
        "endpoints": [
            "/api/products",
            "/api/login",
            "/api/register",
            "/api/order"
        ]
    })
CORS(app, origins=[
    "http://localhost:5173",
    "https://shopzone-frontend.vercel.app",  # ← your Vercel URL
    "https://*.vercel.app"
])

# ── Models ──────────────────────────────
class User(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(80), nullable=False)
    email    = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)

class Order(db.Model):
    id     = db.Column(db.Integer, primary_key=True)
    items  = db.Column(db.Text)
    total  = db.Column(db.Float)
    status = db.Column(db.String(20), default="confirmed")

# ── Products data ────────────────────────
products = [
    {"id":1,"title":"Wireless Headphones","price":49.99,
     "thumbnail":"https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400",
     "category":"electronics"},
    {"id":2,"title":"Smart Watch","price":89.99,
     "thumbnail":"https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400",
     "category":"electronics"},
    {"id":3,"title":"Laptop Stand","price":29.99,
     "thumbnail":"https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=400",
     "category":"accessories"},
    {"id":4,"title":"Mechanical Keyboard","price":69.99,
     "thumbnail":"https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=400",
     "category":"accessories"},
    {"id":5,"title":"USB-C Hub","price":39.99,
     "thumbnail":"https://images.unsplash.com/photo-1625895197185-efcec01cffe0?w=400",
     "category":"accessories"},
    {"id":6,"title":"Noise Cancelling Buds","price":59.99,
     "thumbnail":"https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400",
     "category":"electronics"},
]

# ── Product Routes ───────────────────────
@app.route("/api/products")
def get_products():
    return jsonify({"products": products})

@app.route("/api/products/<int:pid>")
def get_product(pid):
    p = next((p for p in products if p["id"] == pid), None)
    if p: return jsonify(p)
    return jsonify({"error": "Not found"}), 404

@app.route("/api/order", methods=["POST"])
def place_order():
    data = request.get_json()
    if not data or not data.get("items"):
        return jsonify({"success": False}), 400
    order = Order(
        items=json.dumps(data["items"]),
        total=data["total"])
    db.session.add(order)
    db.session.commit()
    return jsonify({"success": True, "order_id": order.id})

# ── Auth Routes ──────────────────────────
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()

    # Check all fields
    if not data.get("name") or not data.get("email") or not data.get("password"):
        return jsonify({"success": False,
                        "message": "All fields are required"}), 400

    # Check if email already exists
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"success": False,
                        "message": "Email already registered"}), 400

    # Hash password and save
    hashed = bcrypt.hashpw(
        data["password"].encode("utf-8"), bcrypt.gensalt())
    user = User(
        name=data["name"],
        email=data["email"],
        password=hashed)
    db.session.add(user)
    db.session.commit()

    return jsonify({"success": True,
                    "message": "Account created successfully!"})

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data.get("email") or not data.get("password"):
        return jsonify({"success": False,
                        "message": "Email and password required"}), 400

    user = User.query.filter_by(email=data["email"]).first()

    if user and bcrypt.checkpw(
        data["password"].encode("utf-8"), user.password):
        return jsonify({"success": True,
                        "user": {
                          "id":    user.id,
                          "name":  user.name,
                          "email": user.email
                        }})

    return jsonify({"success": False,
                    "message": "Invalid email or password"}), 401

@app.route("/api/logout", methods=["POST"])
def logout():
    return jsonify({"success": True, "message": "Logged out"})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database ready!")
    app.run(debug=True, port=5000)