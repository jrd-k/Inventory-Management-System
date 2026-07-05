from flask import Flask, request, jsonify
import database
from external_api import fetch_by_barcode, fetch_by_name, ExternalAPIError

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "message": "Inventory Management System API",
        "endpoints": {
            "GET /inventory": "list all items",
            "GET /inventory/<id>": "get one item",
            "POST /inventory": "create an item",
            "PATCH /inventory/<id>": "update an item",
            "DELETE /inventory/<id>": "delete an item",
            "GET /inventory/search?name=<name>": "search items by name",
            "GET /inventory/external?barcode=<code> or ?name=<name>": "preview a product from OpenFoodFacts",
            "POST /inventory/external": "fetch a product from OpenFoodFacts and add it to inventory",
        }
    })


@app.route("/inventory", methods=["POST"])
def create_item():
    payload = request.get_json(silent=True) or {}

    if not payload.get("product_name"):
        return jsonify({"error": "'product_name' is required"}), 400

    item = database.add_item(payload)
    return jsonify(item), 201


@app.route("/inventory", methods=["GET"])
def get_items():
    return jsonify(database.get_all_items()), 200


@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = database.get_item(item_id)
    if item is None:
        return jsonify({"error": f"Item {item_id} not found"}), 404
    return jsonify(item), 200


@app.route("/inventory/search", methods=["GET"])
def search_items():
    name = request.args.get("name", "").strip()
    if not name:
        return jsonify({"error": "'name' query parameter is required"}), 400
    return jsonify(database.search_items(name)), 200


@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    payload = request.get_json(silent=True) or {}
    item = database.update_item(item_id, payload)
    if item is None:
        return jsonify({"error": f"Item {item_id} not found"}), 404
    return jsonify(item), 200


@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    deleted = database.delete_item(item_id)
    if not deleted:
        return jsonify({"error": f"Item {item_id} not found"}), 404
    return jsonify({"message": f"Item {item_id} deleted"}), 200


@app.route("/inventory/external", methods=["GET"])
def preview_external_product():
    barcode = request.args.get("barcode")
    name = request.args.get("name")

    if not barcode and not name:
        return jsonify({"error": "Provide either 'barcode' or 'name' as a query parameter"}), 400

    try:
        data = fetch_by_barcode(barcode) if barcode else fetch_by_name(name)
    except ExternalAPIError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:  # network / parsing failures
        return jsonify({"error": f"External API request failed: {exc}"}), 502

    return jsonify(data), 200


@app.route("/inventory/external", methods=["POST"])
def fetch_external_and_store():
    payload = request.get_json(silent=True) or {}
    barcode = payload.get("barcode")
    name = payload.get("name")

    if not barcode and not name:
        return jsonify({"error": "Provide either 'barcode' or 'name' in the JSON body"}), 400

    try:
        data = fetch_by_barcode(barcode) if barcode else fetch_by_name(name)
    except ExternalAPIError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        return jsonify({"error": f"External API request failed: {exc}"}), 502

    # OpenFoodFacts doesn't know retail quantity/price - let the caller supply them
    data["quantity"] = payload.get("quantity", 0)
    data["price"] = payload.get("price", 0.0)

    item = database.add_item(data)
    return jsonify(item), 201


if __name__ == "__main__":
    app.run(debug=True, port=5000)