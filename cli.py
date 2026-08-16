import requests

BASE_URL = "http://127.0.0.1:5000"


def view_inventory():
    try:
        response = requests.get(f"{BASE_URL}/inventory")
        items = response.json()
        print("\n--- Inventory ---")
        for item in items:
            print(f"ID: {item['id']} | {item['product_name']} | "
                  f"Brand: {item['brands']} | Price: KES {item['price']} | Stock: {item['stock']}")
    except requests.exceptions.RequestException:
        print("Error: Could not connect to the API. Is the server running?")


def add_item():
    product_name = input("Product name: ").strip()
    brands = input("Brand: ").strip()
    ingredients = input("Description/ingredients: ").strip()

    try:
        price = float(input("Price: "))
        stock = int(input("Stock: "))
    except ValueError:
        print("Error: Price must be a number and stock must be a whole number.")
        return

    payload = {
        "product_name": product_name,
        "brands": brands,
        "ingredients_text": ingredients,
        "price": price,
        "stock": stock
    }

    try:
        response = requests.post(f"{BASE_URL}/inventory", json=payload)
        if response.status_code == 201:
            print("Item added successfully:", response.json())
        else:
            print("Error adding item:", response.json())
    except requests.exceptions.RequestException:
        print("Error: Could not connect to the API.")


def update_item():
    try:
        item_id = int(input("Enter the ID of the item to update: "))
    except ValueError:
        print("Error: ID must be a number.")
        return

    print("Leave a field blank to keep it unchanged.")
    price = input("New price: ").strip()
    stock = input("New stock: ").strip()

    payload = {}
    if price:
        try:
            payload["price"] = float(price)
        except ValueError:
            print("Error: Price must be a number.")
            return
    if stock:
        try:
            payload["stock"] = int(stock)
        except ValueError:
            print("Error: Stock must be a whole number.")
            return

    if not payload:
        print("Nothing to update.")
        return

    try:
        response = requests.patch(f"{BASE_URL}/inventory/{item_id}", json=payload)
        if response.status_code == 200:
            print("Item updated successfully:", response.json())
        else:
            print("Error:", response.json())
    except requests.exceptions.RequestException:
        print("Error: Could not connect to the API.")


def delete_item():
    try:
        item_id = int(input("Enter the ID of the item to delete: "))
    except ValueError:
        print("Error: ID must be a number.")
        return

    try:
        response = requests.delete(f"{BASE_URL}/inventory/{item_id}")
        if response.status_code == 200:
            print(response.json().get("message"))
        else:
            print("Error:", response.json())
    except requests.exceptions.RequestException:
        print("Error: Could not connect to the API.")


def find_item_on_api():
    query_type = input("Search by (1) barcode or (2) name? Enter 1 or 2: ").strip()

    params = {}
    if query_type == "1":
        params["barcode"] = input("Enter barcode: ").strip()
    elif query_type == "2":
        params["name"] = input("Enter product name: ").strip()
    else:
        print("Invalid choice.")
        return

    try:
        response = requests.get(f"{BASE_URL}/products/search", params=params)
        if response.status_code == 200:
            print("\n--- Search Results ---")
            print(response.json())
        else:
            print("Error:", response.json())
    except requests.exceptions.RequestException:
        print("Error: Could not connect to the API.")


def main():
    while True:
        print("\n===== Agrovet Inventory Manager =====")
        print("1. View inventory")
        print("2. Add new item")
        print("3. Update item price/stock")
        print("4. Delete item")
        print("5. Find item on external API")
        print("6. Exit")

        choice = input("Choose an option (1-6): ").strip()

        if choice == "1":
            view_inventory()
        elif choice == "2":
            add_item()
        elif choice == "3":
            update_item()
        elif choice == "4":
            delete_item()
        elif choice == "5":
            find_item_on_api()
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid option, please choose 1-6.")


if __name__ == "__main__":
    main()