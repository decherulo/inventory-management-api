from flask import Flask, jsonify, request

app = Flask(__name__)


import requests

OPENFOODFACTS_BASE = "https://world.openfoodfacts.org"

# Mock database — simulates data an agrovet's inventory system might hold
inventory = [
    {
        "id": 1,
        "product_name": "Layers Mash 50kg",
        "brands": "Unga Farm Care",
        "ingredients_text": "Maize germ, soya, limestone, vitamins",
        "price": 3200,
        "stock": 15
    },
    {
        "id": 2,
        "product_name": "Broiler Starter Feed 50kg",
        "brands": "Sigma Feeds",
        "ingredients_text": "Maize, soybean meal, fish meal, premix",
        "price": 3450,
        "stock": 10
    },
    {
        "id": 3,
        "product_name": "Newcastle Disease Vaccine (100 dose)",
        "brands": "Kevevapi",
        "ingredients_text": "Live attenuated Newcastle disease virus",
        "price": 450,
        "stock": 30
    },
    {
        "id": 4,
        "product_name": "Day-Old Chicks (Kienyeji)",
        "brands": "Local Hatchery",
        "ingredients_text": "N/A",
        "price": 120,
        "stock": 200
    },
    {
        "id": 5,
        "product_name": "Poultry Multivitamins 100ml",
        "brands": "Agrivet",
        "ingredients_text": "Vitamin A, D3, E, B-complex, electrolytes",
        "price": 350,
        "stock": 25
    },
    {
        "id": 6,
        "product_name": "Layers Mash Feeders (Plastic)",
        "brands": "Generic",
        "ingredients_text": "N/A",
        "price": 600,
        "stock": 18
    }
]


@app.route("/inventory", methods=["GET"])
def get_inventory():
    return jsonify(inventory), 200


@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_item(item_id):
    for item in inventory:
        if item["id"] == item_id:
            return jsonify(item), 200
    return jsonify({"error": "Item not found"}), 404


@app.route("/inventory", methods=["POST"])
def add_item():
    data = request.get_json()

    if not data or "product_name" not in data:
        return jsonify({"error": "product_name is required"}), 400

    new_id = max(item["id"] for item in inventory) + 1

    new_item = {
        "id": new_id,
        "product_name": data.get("product_name"),
        "brands": data.get("brands", ""),
        "ingredients_text": data.get("ingredients_text", ""),
        "price": data.get("price", 0),
        "stock": data.get("stock", 0)
    }

    inventory.append(new_item)
    return jsonify(new_item), 201

@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    data = request.get_json()

    for item in inventory:
        if item["id"] == item_id:
            item["product_name"] = data.get("product_name", item["product_name"])
            item["brands"] = data.get("brands", item["brands"])
            item["ingredients_text"] = data.get("ingredients_text", item["ingredients_text"])
            item["price"] = data.get("price", item["price"])
            item["stock"] = data.get("stock", item["stock"])
            return jsonify(item), 200

    return jsonify({"error": "Item not found"}), 404

@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    for item in inventory:
        if item["id"] == item_id:
            inventory.remove(item)
            return jsonify({"message": f"Item {item_id} deleted"}), 200

    return jsonify({"error": "Item not found"}), 404


@app.route("/products/search", methods=["GET"])
def search_external_product():
    barcode = request.args.get("barcode")
    name = request.args.get("name")

    headers = {"User-Agent": "InventoryManagementApp - Debby - Educational Project"}

    if not barcode and not name:
        return jsonify({"error": "Provide a barcode or name query parameter"}), 400

    if barcode:
        url = f"{OPENFOODFACTS_BASE}/api/v2/product/{barcode}.json"
        response = requests.get(url, headers=headers)

        try:
            data = response.json()
        except ValueError:
            return jsonify({"error": "Invalid response from external API"}), 502

        if data.get("status") != 1:
            return jsonify({"error": "Product not found for that barcode"}), 404

        product = data["product"]
        result = {
            "product_name": product.get("product_name", "Unknown"),
            "brands": product.get("brands", "Unknown"),
            "ingredients_text": product.get("ingredients_text", "")
        }
        return jsonify(result), 200

    else:
        url = f"{OPENFOODFACTS_BASE}/cgi/search.pl"
        params = {"search_terms": name, "json": 1, "page_size": 5}
        response = requests.get(url, params=params, headers=headers)

        try:
            data = response.json()
        except ValueError:
            return jsonify({"error": "Invalid response from external API"}), 502

        products = data.get("products", [])
        if not products:
            return jsonify({"error": "No products found for that name"}), 404

        results = [
            {
                "product_name": p.get("product_name", "Unknown"),
                "brands": p.get("brands", "Unknown"),
                "ingredients_text": p.get("ingredients_text", "")
            }
            for p in products
        ]
        return jsonify(results), 200

@app.route("/products/import", methods=["POST"])
def import_external_product():
    data = request.get_json()
    barcode = data.get("barcode") if data else None
    name = data.get("name") if data else None

    if not barcode and not name:
        return jsonify({"error": "Provide a barcode or name in the request body"}), 400

    headers = {"User-Agent": "InventoryManagementApp - Debby - Educational Project"}

    if barcode:
        url = f"{OPENFOODFACTS_BASE}/api/v2/product/{barcode}.json"
        response = requests.get(url, headers=headers)
        try:
            ext_data = response.json()
        except ValueError:
            return jsonify({"error": "Invalid response from external API"}), 502

        if ext_data.get("status") != 1:
            return jsonify({"error": "Product not found for that barcode"}), 404

        product = ext_data["product"]

    else:
        url = f"{OPENFOODFACTS_BASE}/cgi/search.pl"
        params = {"search_terms": name, "json": 1, "page_size": 1}
        response = requests.get(url, params=params, headers=headers)
        try:
            ext_data = response.json()
        except ValueError:
            return jsonify({"error": "Invalid response from external API"}), 502

        products = ext_data.get("products", [])
        if not products:
            return jsonify({"error": "No products found for that name"}), 404

        product = products[0]

    new_id = max(item["id"] for item in inventory) + 1
    new_item = {
        "id": new_id,
        "product_name": product.get("product_name", "Unknown"),
        "brands": product.get("brands", "Unknown"),
        "ingredients_text": product.get("ingredients_text", ""),
        "price": data.get("price", 0),
        "stock": data.get("stock", 0)
    }

    inventory.append(new_item)
    return jsonify(new_item), 201



if __name__ == "__main__":
    app.run(debug=True)