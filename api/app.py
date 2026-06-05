import json
from flask import Flask, jsonify, request
from db import (
    get_all_products_from_db,
    get_product_by_id_from_db,
    insert_product_into_db,
)
from cache import (
    get_cached_products,
    set_cached_products,
    clear_products_cache,
)

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/products")
def get_products():
    # ✅ TODO Uppgift 12-15 - Check Redis first, fall back to PostgreSQL
    cached = get_cached_products()
    if cached is not None:
        print("CACHE HIT")
        return app.response_class(response=cached, status=200, mimetype="application/json")

    print("CACHE MISS")
    products = get_all_products_from_db()

    # Convert list to JSON string before saving to Redis
    json_string = json.dumps(products)
    set_cached_products(json_string)
    
    return jsonify(products), 200


@app.get("/products/<int:product_id>")
def get_product(product_id):
    # ✅ TODO Uppgift 5 & 6 - Return product or 404
    product = get_product_by_id_from_db(product_id)
    if product is None:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product), 200


@app.post("/products")
def create_product():
    data = request.get_json(silent=True)

    # ✅ TODO Uppgift 10 - Validate input
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    if "name" not in data or not data["name"]:
        return jsonify({"error": "Missing required field: name"}), 400
    if "price" not in data:
        return jsonify({"error": "Missing required field: price"}), 400
    if not isinstance(data["price"], (int, float)) or data["price"] < 0:
        return jsonify({"error": "price must be a non-negative number"}), 400

    # ✅ TODO Uppgift 8 - Insert into PostgreSQL
    product = insert_product_into_db(data)

    # ✅ TODO Uppgift 17 - Invalidate cache so GET /products reflects the new product
    clear_products_cache()

    return jsonify(product), 201


@app.get("/crash")
def crash():
    raise Exception("Simulated server error")


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)