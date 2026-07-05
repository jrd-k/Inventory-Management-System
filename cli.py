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
