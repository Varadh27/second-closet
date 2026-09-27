"""Second Closet - a second-hand clothing marketplace.

CCA 2, Cloud Computing and DevOps (CSE30040), MIT-WPU.
Pages are rendered by the server from in-memory data on every request.
"""
import os

from flask import Flask, abort, jsonify, redirect, render_template, request, url_for

app = Flask(__name__)

# Render sets RENDER_GIT_COMMIT automatically; the Docker build passes GIT_SHA.
COMMIT = (os.getenv("RENDER_GIT_COMMIT") or os.getenv("GIT_SHA") or "local")[:7]

CATEGORIES = ["Tops", "Bottoms", "Dresses", "Outerwear", "Footwear", "Accessories"]
SIZES = ["XS", "S", "M", "L", "XL", "Free Size"]
CONDITIONS = ["New with tags", "Like new", "Good", "Fair"]
MAX_PRICE = 50000

items = []  # in-memory store: resets when the server restarts

SEED_ITEMS = [
    ("Vintage denim jacket", "Outerwear", "M", "Good", 1200, "Ananya"),
    ("Floral midi dress", "Dresses", "S", "Like new", 850, "Riya"),
    ("White canvas sneakers", "Footwear", "Free Size", "Good", 700, "Kabir"),
    ("Oversized graphic tee", "Tops", "L", "New with tags", 400, "Ishaan"),
]


def next_id():
    return max((item["id"] for item in items), default=0) + 1


def add_item(name, category, size, condition, price, seller):
    item = {
        "id": next_id(),
        "name": name,
        "category": category,
        "size": size,
        "condition": condition,
        "price": price,
        "seller": seller,
        "status": "Available",
    }
    items.append(item)
    return item


def reset_store(seed=True):
    """Clear all listings (used by tests) and optionally add demo listings."""
    items.clear()
    if seed:
        for row in SEED_ITEMS:
            add_item(*row)


def find_item(item_id):
    return next((item for item in items if item["id"] == item_id), None)


def validate_listing(form):
    """Return (clean_data, errors) for a submitted listing form."""
    errors = []
    name = form.get("name", "").strip()
    seller = form.get("seller", "").strip()
    category = form.get("category", "")
    size = form.get("size", "")
    condition = form.get("condition", "")

    if not name or len(name) > 60:
        errors.append("Item name is required (max 60 characters).")
    if not seller or len(seller) > 40:
        errors.append("Seller name is required (max 40 characters).")
    if category not in CATEGORIES:
        errors.append("Choose a valid category.")
    if size not in SIZES:
        errors.append("Choose a valid size.")
    if condition not in CONDITIONS:
        errors.append("Choose a valid condition.")

    price = None
    try:
        price = int(form.get("price", ""))
        if not 1 <= price <= MAX_PRICE:
            errors.append(f"Price must be between Rs 1 and Rs {MAX_PRICE}.")
    except ValueError:
        errors.append("Price must be a whole number.")

    data = {"name": name, "category": category, "size": size,
            "condition": condition, "price": price, "seller": seller}
    return data, errors


def render_home(errors=None, form=None, status_code=200):
    stats = {
        "available": sum(1 for i in items if i["status"] == "Available"),
        "sold": sum(1 for i in items if i["status"] == "Sold"),
    }
    page = render_template(
        "index.html", items=items, stats=stats, commit=COMMIT,
        categories=CATEGORIES, sizes=SIZES, conditions=CONDITIONS,
        errors=errors or [], form=form or {},
    )
    return page, status_code


@app.route("/")
def home():
    return render_home()


@app.route("/items", methods=["POST"])
def create_item():
    data, errors = validate_listing(request.form)
    if errors:
        return render_home(errors=errors, form=request.form, status_code=400)
    add_item(**data)
    return redirect(url_for("home"))


@app.route("/items/<int:item_id>/buy", methods=["POST"])
def buy_item(item_id):
    item = find_item(item_id)
    if item is None:
        abort(404)
    if item["status"] == "Sold":
        return "This item has already been sold.", 409
    item["status"] = "Sold"
    return redirect(url_for("home"))


@app.route("/api/items")
def api_items():
    return jsonify(items)


@app.route("/health")
def health():
    return jsonify({"status": "ok", "commit": COMMIT})


reset_store(seed=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
