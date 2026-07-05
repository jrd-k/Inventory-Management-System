def _reset():
    """Test helper: wipe the array and reset the id counter."""
    global inventory, _next_id
    inventory = []
    _next_id = 1


def _generate_id() -> int:
    global _next_id
    new_id = _next_id
    _next_id += 1
    return new_id


def add_item(data: dict) -> dict:
    """Create a new inventory item and append it to the array."""
    item = {
        "id": _generate_id(),
        "product_name": data.get("product_name", "Unknown product"),
        "brands": data.get("brands"),
        "ingredients_text": data.get("ingredients_text"),
        "barcode": data.get("barcode"),
        "category": data.get("category"),
        "image_url": data.get("image_url"),
        "quantity": data.get("quantity", 0),
        "price": data.get("price", 0.0),
        "source": data.get("source", "manual"),
    }
    inventory.append(item)
    return item

