from flask import Flask, jsonify, request
import urllib.parse
import requests

app = Flask(__name__)

inventory = [
    {
        "id": 1,
        "barcode": "025293600350",
        "product_name": "Organic Almond Milk",
        "brands": "Silk",
        "quantity": 40,
        "price": 3.99,
        "ingredients_text": "Filtered water, almonds, cane sugar, calcium carbonate...",
    },
    {
        "id": 2,
        "barcode": "007323000004",
        "product_name": "Sparkling Water - Lime",
        "brands": "LaCroix",
        "quantity": 50,
        "price": 4.99,
        "ingredients_text": "Only naturally-essenced sparkling water",
    },
    {
        "id": 3,
        "barcode": "004119691075",
        "product_name": "Chunky Peanut Butter",
        "brands": "Skippy",
        "quantity": 25,
        "price": 3.49,
        "ingredients_text": "Roasted peanuts, sugar, hydrogenated vegetable oil, salt",
    },
    {
        "id": 4,
        "barcode": "001600027526",
        "product_name": "Honey Nut Cheerios",
        "brands": "General Mills",
        "quantity": 30,
        "price": 4.29,
        "ingredients_text": "Whole grain oats, sugar, oat bran, corn starch, honey, salt",
    },
]


def fetch_open_food_facts(query):
    query = str(query).strip()

    for item in inventory:
        if (
            query.lower() == item["barcode"].lower()
            or query.lower() in item["product_name"].lower()
        ):
            return {
                "barcode": item["barcode"],
                "product_name": item["product_name"],
                "brands": item["brands"],
                "ingredients_text": item["ingredients_text"],
            }

    headers = {
        "User-Agent": "InventoryManagementApp/1.0 (contact@example.com)"
    }

    if query.isdigit():
        barcodes_to_try = [query, query.lstrip("0")]
        for bc in barcodes_to_try:
            if not bc:
                continue
            url = f"https://world.openfoodfacts.org/api/v0/product/{bc}.json"
            try:
                response = requests.get(url, headers=headers, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == 1:
                        prod = data.get("product", {})
                        return {
                            "barcode": bc,
                            "product_name": prod.get("product_name")
                            or prod.get("product_name_en", "Unknown"),
                            "brands": prod.get("brands", "Unknown"),
                            "ingredients_text": prod.get(
                                "ingredients_text", "No ingredients listed"
                            ),
                        }
            except requests.RequestException:
                pass

    encoded_query = urllib.parse.quote(query)
    search_url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={encoded_query}&search_simple=1&action=process&json=1"

    try:
        response = requests.get(search_url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            products = data.get("products", [])
            if products:
                prod = products[0]
                return {
                    "barcode": prod.get("code", "N/A"),
                    "product_name": prod.get("product_name")
                    or prod.get("product_name_en", "Unknown"),
                    "brands": prod.get("brands", "Unknown"),
                    "ingredients_text": prod.get(
                        "ingredients_text", "No ingredients listed"
                    ),
                }
    except requests.RequestException:
        pass

    return None


@app.route("/inventory", methods=["GET"])
def get_inventory():
    return jsonify(inventory), 200


@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = next((i for i in inventory if i["id"] == item_id), None)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200


@app.route("/inventory", methods=["POST"])
def add_item():
    data = request.get_json() or {}

    query = data.get("query") or data.get("barcode") or data.get("product_name")
    external_data = {}
    if query:
        external_data = fetch_open_food_facts(str(query)) or {}

    target_barcode = data.get("barcode") or external_data.get("barcode")
    quantity_to_add = data.get("quantity", 10)

    if target_barcode and target_barcode != "0000000000":
        existing_item = next(
            (i for i in inventory if i["barcode"] == target_barcode), None
        )
        if existing_item:
            existing_item["quantity"] += quantity_to_add
            return jsonify(existing_item), 200

    new_id = max([i["id"] for i in inventory], default=0) + 1

    new_item = {
        "id": new_id,
        "barcode": target_barcode or "0000000000",
        "product_name": data.get("product_name")
        or external_data.get("product_name", "New Item"),
        "brands": data.get("brands") or external_data.get("brands", "Generic"),
        "quantity": quantity_to_add,
        "price": data.get("price", 1.99),
        "ingredients_text": data.get("ingredients_text")
        or external_data.get("ingredients_text", "N/A"),
    }

    inventory.append(new_item)
    return jsonify(new_item), 201


@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = next((i for i in inventory if i["id"] == item_id), None)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json() or {}
    item["product_name"] = data.get("product_name", item["product_name"])
    item["brands"] = data.get("brands", item["brands"])
    item["quantity"] = data.get("quantity", item["quantity"])
    item["price"] = data.get("price", item["price"])
    item["ingredients_text"] = data.get(
        "ingredients_text", item["ingredients_text"]
    )

    return jsonify(item), 200


@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    global inventory
    item = next((i for i in inventory if i["id"] == item_id), None)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    inventory = [i for i in inventory if i["id"] != item_id]
    return jsonify({"message": f"Item {item_id} deleted successfully"}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
