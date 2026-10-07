import argparse
import requests

BASE_URL = "http://127.0.0.1:5000/inventory"


def view_inventory():
  response = requests.get(BASE_URL)
  if response.status_code == 200:
    items = response.json()
    print("\n--- Current Inventory ---")
    for item in items:
      print(
          f"ID: {item['id']} | Name: {item['product_name']} | Brand:"
          f" {item['brands']} | Qty: {item['quantity']} | Price:"
          f" ${item['price']}"
      )
  else:
    print("Failed to fetch inventory.")


def add_item(name=None, barcode=None, quantity=10, price=1.99):
  payload = {
      "product_name": name,
      "barcode": barcode,
      "quantity": quantity,
      "price": price,
  }
  response = requests.post(BASE_URL, json=payload)
  if response.status_code == 201:
    print("Item added successfully:", response.json())
  else:
    print("Error adding item:", response.text)


def update_item(item_id, quantity=None, price=None):
  payload = {}
  if quantity is not None:
    payload["quantity"] = quantity
  if price is not None:
    payload["price"] = price

  response = requests.patch(f"{BASE_URL}/{item_id}", json=payload)
  if response.status_code == 200:
    print("Item updated successfully:", response.json())
  else:
    print("Error updating item:", response.text)


def delete_item(item_id):
  response = requests.delete(f"{BASE_URL}/{item_id}")
  if response.status_code == 200:
    print(response.json()["message"])
  else:
    print("Error deleting item:", response.text)


def search_api(query):
  url = f"https://world.openfoodfacts.org/api/v0/product/{query}.json"
  res = requests.get(url)
  if res.status_code == 200 and res.json().get("status") == 1:
    prod = res.json()["product"]
    print(f"\n[OpenFoodFacts Found]: {prod.get('product_name')}")
    print(f"Brand: {prod.get('brands')}")
    print(f"Ingredients: {prod.get('ingredients_text', 'N/A')}")
  else:
    print("Product not found on external API.")


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Inventory CLI Frontend")
  subparsers = parser.add_subparsers(dest="command")

  subparsers.add_parser("view", help="View all inventory items")

  add_p = subparsers.add_parser("add", help="Add new inventory item")
  add_p.add_argument("--name", help="Product Name")
  add_p.add_argument("--barcode", help="Product Barcode")
  add_p.add_argument("--qty", type=int, default=10, help="Quantity")
  add_p.add_argument("--price", type=float, default=1.99, help="Price")

  up_p = subparsers.add_parser("update", help="Update quantity or price")
  up_p.add_argument("id", type=int, help="Item ID")
  up_p.add_argument("--qty", type=int, help="New Quantity")
  up_p.add_argument("--price", type=float, help="New Price")

  del_p = subparsers.add_parser("delete", help="Delete item by ID")
  del_p.add_argument("id", type=int, help="Item ID")

  search_p = subparsers.add_parser(
      "search-api", help="Search OpenFoodFacts by barcode"
  )
  search_p.add_argument("query", help="Barcode or search term")

  args = parser.parse_args()

  if args.command == "view":
    view_inventory()
  elif args.command == "add":
    add_item(args.name, args.barcode, args.qty, args.price)
  elif args.command == "update":
    update_item(args.id, args.qty, args.price)
  elif args.command == "delete":
    delete_item(args.id)
  elif args.command == "search-api":
    search_api(args.query)
  else:
    parser.print_help()