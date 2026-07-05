from flask import Flask, request, jsonify
import database
from external_api import fetch_by_barcode, fetch_by_name, ExternalAPIError

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "message":"Inventory Management System API"
        "endpoints":{
            "GET /inventory": "list all items",
            "GET /inentory/<id>"": "get one item",
            "POST /inentory": "crete an item",
            "PATCH /inventory/<id>":"update an item",
            "DELETE /inventory/<id>":"delete an item",
            "GET /inventory/search?name=<name>": "search items by name",
            "GET /inventory/external?barcode=<code> or ?name=<name>": "preview a product from OpenFoodFacts",
            "POST /inventory/external":"fetch a product from OpenFoodFacts and add it to inventory",
        }
    })



@app.route("/inventory",methods=[POST])
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
        return jsonify({"error": f"Item{item_id} not found"}), 404
    return jsonify(item), 200


