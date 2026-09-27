"""Second Closet - a second-hand clothing marketplace.

CCA 2, Cloud Computing and DevOps (CSE30040), MIT-WPU.
Pages are rendered by the server from in-memory data on every request.
"""
import os

from flask import Flask, jsonify, render_template

app = Flask(__name__)

# Render sets RENDER_GIT_COMMIT automatically; the Docker build passes GIT_SHA.
COMMIT = (os.getenv("RENDER_GIT_COMMIT") or os.getenv("GIT_SHA") or "local")[:7]

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


@app.route("/")
def home():
    return render_template("index.html", items=items, commit=COMMIT)


@app.route("/health")
def health():
    return jsonify({"status": "ok", "commit": COMMIT})


reset_store(seed=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
