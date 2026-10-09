import requests

BASE_URL = "http://127.0.0.1:5000"


def print_menu():
    print("\n   INVENTORY MANAGEMENT SYSTEM")
    print("================================")
    print("1. View inventory")
    print("2. Add product")
    print("3. Update product")
    print("4. Delete product")
    print("5. Search/import OpenFoodFacts")
    print("6. Exit")


def view_inventory():
    try:
        res = requests.get(f"{BASE_URL}/inventory")
        if res.status_code == 200:
            items = res.json()
            if not items:
                print("\nInventory is currently empty.")
                return
            print("\n--- CURRENT INVENTORY ---")
            for item in items:
                print(
                    f"ID: {item['id']} | Name: {item['product_name']} | "
                    f"Brand: {item['brands']} | Qty: {item['quantity']} | Price: ${item['price']}"
                )
        else:
            print(f"Error fetching inventory: {res.status_code}")
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to Flask server. Make sure app.py is running!")


def add_product():
    print("\n--- ADD PRODUCT ---")
    barcode = input("Barcode (optional): ").strip()
    product_name = input("Product Name (optional): ").strip()
    brands = input("Brand (optional): ").strip()
    quantity_input = input("Quantity (default 10): ").strip()
    price_input = input("Price (default 1.99): ").strip()
    ingredients = input("Ingredients (optional): ").strip()

    payload = {}
    if barcode:
        payload["barcode"] = barcode
    if product_name:
        payload["product_name"] = product_name
    if brands:
        payload["brands"] = brands
    if quantity_input:
        try:
            payload["quantity"] = int(quantity_input)
        except ValueError:
            print("Invalid quantity. Using default.")
    if price_input:
        try:
            payload["price"] = float(price_input)
        except ValueError:
            print("Invalid price. Using default.")
    if ingredients:
        payload["ingredients_text"] = ingredients

    res = requests.post(f"{BASE_URL}/inventory", json=payload)
    if res.status_code in [200, 201]:
        print("Product added successfully!")
        print(res.json())
    else:
        print("Failed to add product:", res.json())


def update_product():
    print("\n--- UPDATE PRODUCT ---")
    item_id = input("Enter Product ID to update: ").strip()
    if not item_id.isdigit():
        print("Invalid ID.")
        return

    print("Leave blank for any field you do not want to change:")
    product_name = input("New Product Name: ").strip()
    brands = input("New Brand: ").strip()
    quantity_input = input("New Quantity: ").strip()
    price_input = input("New Price: ").strip()
    ingredients = input("New Ingredients: ").strip()

    payload = {}
    if product_name:
        payload["product_name"] = product_name
    if brands:
        payload["brands"] = brands
    if quantity_input:
        try:
            payload["quantity"] = int(quantity_input)
        except ValueError:
            print("Invalid quantity format.")
    if price_input:
        try:
            payload["price"] = float(price_input)
        except ValueError:
            print("Invalid price format.")
    if ingredients:
        payload["ingredients_text"] = ingredients

    res = requests.patch(f"{BASE_URL}/inventory/{item_id}", json=payload)
    if res.status_code == 200:
        print("Product updated successfully!")
        print(res.json())
    else:
        print("Failed to update product:", res.json())


def delete_product():
    print("\n--- DELETE PRODUCT ---")
    item_id = input("Enter Product ID to delete: ").strip()
    if not item_id.isdigit():
        print("Invalid ID.")
        return

    res = requests.delete(f"{BASE_URL}/inventory/{item_id}")
    if res.status_code == 200:
        print(f"Product {item_id} deleted successfully.")
    else:
        print("Failed to delete product:", res.json())


def search_open_food_facts():
    print("\n--- SEARCH / IMPORT OPENFOODFACTS ---")
    query = input("Enter Barcode or Product Search Term: ").strip()
    if not query:
        print("Search term cannot be empty.")
        return

    res = requests.post(f"{BASE_URL}/inventory", json={"query": query})
    if res.status_code in [200, 201]:
        item = res.json()
        print("\nProduct imported into inventory:")
        print(f"ID: {item['id']}")
        print(f"Name: {item['product_name']}")
        print(f"Brand: {item['brands']}")
        print(f"Barcode: {item['barcode']}")
        print(f"Ingredients: {item['ingredients_text']}")
    else:
        print("Product not found or import failed.")


def main():
    while True:
        print_menu()
        choice = input("Choose an option: ").strip()

        if choice == "1":
            view_inventory()
        elif choice == "2":
            add_product()
        elif choice == "3":
            update_product()
        elif choice == "4":
            delete_product()
        elif choice == "5":
            search_open_food_facts()
        elif choice == "6":
            print("\nExiting program. Goodbye!")
            break
        else:
            print("Invalid option. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    main()
