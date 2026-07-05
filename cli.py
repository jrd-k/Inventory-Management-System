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
