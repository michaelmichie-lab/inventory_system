from flask import Flask, jsonify, request
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
    }
]


def fetch_open_food_facts(query):

  if query.isdigit():
    url = f"https://world.openfoodfacts.org/api/v0/product/{query}.json"
    response = requests.get(url)
    if response.status_code == 200:
      data = response.json()
      if data.get("status") == 1:
        prod = data.get("product", {})
        return {
            "barcode": query,
            "product_name": prod.get("product_name", "Unknown"),
            "brands": prod.get("brands", "Unknown"),
            "ingredients_text": prod.get(
                "ingredients_text", "No ingredients listed"
            ),
        }
  else:
   
    url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={query}&search_simple=1&action=process&json=1"
    response = requests.get(url)
    if response.status_code == 200:
      data = response.json()
      products = data.get("products", [])
      if products:
        prod = products[0]
        return {
            "barcode": prod.get("code", "N/A"),
            "product_name": prod.get("product_name", "Unknown"),
            "brands": prod.get("brands", "Unknown"),
            "ingredients_text": prod.get(
                "ingredients_text", "No ingredients listed"
            ),
        }
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

  new_id = max([i["id"] for i in inventory], default=0) + 1

  new_item = {
      "id": new_id,
      "barcode": data.get("barcode")
      or external_data.get("barcode", "0000000000"),
      "product_name": data.get("product_name")
      or external_data.get("product_name", "New Item"),
      "brands": data.get("brands") or external_data.get("brands", "Generic"),
      "quantity": data.get("quantity", 10),
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