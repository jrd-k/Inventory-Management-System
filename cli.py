import argparse
import sys
import requests

API_BASE = "http://127.0.0.1:5000/inventory"


def _print_item(item):
    print(f"  [{item.get('id')}] {item.get('product_name')}  "
          f"qty={item.get('quantity')}  price={item.get('price')}  "
          f"barcode={item.get('barcode')}  source={item.get('source')}")


def _handle_connection_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.ConnectionError:
            print("Could not connect to the API. Is it running? Start it with: python app.py")
            sys.exit(1)
    return wrapper


@_handle_connection_error
def cmd_add(args):
    payload = {
        "product_name": args.name,
        "quantity": args.quantity,
        "price": args.price,
        "brands": args.brand,
        "barcode": args.barcode,
    }
    resp = requests.post(API_BASE, json=payload)
    if resp.status_code != 201:
        print(f"Error: {resp.json()}")
        return
    print("Added:")
    _print_item(resp.json())



@_handle_connection_error
def cmd_view(args):
    if args.id is not None:
        resp = requests.get(f"{API_BASE}/{args.id}")
        if resp.status_code == 404:
            print(f"Item {args.id} not found.")
            return
        resp.raise_for_status()
        _print_item(resp.json())
        return

    if args.name:
        resp = requests.get(f"{API_BASE}/search", params={"name": args.name})
        resp.raise_for_status()
        items = resp.json()
        if not items:
            print("No matches.")
            return
        for item in items:
            _print_item(item)
        return

    resp = requests.get(API_BASE)
    resp.raise_for_status()
    items = resp.json()
    if not items:
        print("No inventory items found.")
        return
    for item in items:
        _print_item(item)



@_handle_connection_error
def cmd_update(args):
    payload = {}
    if args.name is not None:
        payload["product_name"] = args.name
    if args.quantity is not None:
        payload["quantity"] = args.quantity
    if args.price is not None:
        payload["price"] = args.price

    if not payload:
        print("Nothing to update - provide at least one of --name, --quantity, --price.")
        return

    resp = requests.patch(f"{API_BASE}/{args.id}", json=payload)
    if resp.status_code == 404:
        print(f"Item {args.id} not found.")
        return
    resp.raise_for_status()
    print("Updated:")
    _print_item(resp.json())



@_handle_connection_error
def cmd_delete(args):
    resp = requests.delete(f"{API_BASE}/{args.id}")
    if resp.status_code == 404:
        print(f"Item {args.id} not found.")
        return
    resp.raise_for_status()
    print(resp.json()["message"])

@_handle_connection_error
def cmd_find(args):
    if not args.barcode and not args.name:
        print("Provide --barcode or --name to search the external API.")
        return

    if args.add:
        # Fetch AND add to the inventory array in one step
        payload = {"quantity": args.quantity, "price": args.price}
        if args.barcode:
            payload["barcode"] = args.barcode
        if args.name:
            payload["name"] = args.name

        resp = requests.post(f"{API_BASE}/external", json=payload)
        if resp.status_code != 201:
            print(f"Error: {resp.json()}")
            return
        print("Found on OpenFoodFacts and added to inventory:")
        _print_item(resp.json())
        return

    # Preview only - does not touch the inventory array
    params = {}
    if args.barcode:
        params["barcode"] = args.barcode
    if args.name:
        params["name"] = args.name

    resp = requests.get(f"{API_BASE}/external", params=params)
    if resp.status_code != 200:
        print(f"Error: {resp.json()}")
        return
    data = resp.json()
    print("Found on OpenFoodFacts (preview only, not saved):")
    for key, value in data.items():
        print(f"  {key}: {value}")


def build_parser():
    parser = argparse.ArgumentParser(description="Inventory Management System CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Add a new inventory item")
    p_add.add_argument("--name", required=True)
    p_add.add_argument("--quantity", type=int, default=0)
    p_add.add_argument("--price", type=float, default=0.0)
    p_add.add_argument("--brand", default=None)
    p_add.add_argument("--barcode", default=None)
    p_add.set_defaults(func=cmd_add)

    p_view = sub.add_parser("view", help="View inventory items")
    p_view.add_argument("--id", type=int, default=None, help="View a single item by id")
    p_view.add_argument("--name", default=None, help="Search items by name")
    p_view.set_defaults(func=cmd_view)

    p_update = sub.add_parser("update", help="Update an item's price or stock level")
    p_update.add_argument("id", type=int)
    p_update.add_argument("--name", default=None)
    p_update.add_argument("--quantity", type=int, default=None)
    p_update.add_argument("--price", type=float, default=None)
    p_update.set_defaults(func=cmd_update)

    p_delete = sub.add_parser("delete", help="Delete an inventory item")
    p_delete.add_argument("id", type=int)
    p_delete.set_defaults(func=cmd_delete)

    p_find = sub.add_parser("find", help="Find a product on OpenFoodFacts, optionally add it")
    p_find.add_argument("--barcode", default=None)
    p_find.add_argument("--name", default=None)
    p_find.add_argument("--add", action="store_true", help="Add the found product to inventory")
    p_find.add_argument("--quantity", type=int, default=0)
    p_find.add_argument("--price", type=float, default=0.0)
    p_find.set_defaults(func=cmd_find)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()