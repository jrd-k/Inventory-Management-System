import requests

BASE_URL = "https://world.openfoodfacts.org"
TIMEOUT = 10

# OpenFoodFacts blocks requests with no/generic User-Agent (403 Forbidden),
# so every call identifies itself per their usage guidelines.
HEADERS = {"User-Agent": "InventoryManagementSystem/1.0 (student project; contact: jared.kiprop@student.moringaschool.com)"}


class ExternalAPIError(Exception):
    """Raised when the external API call fails or returns no usable data."""


def fetch_by_barcode(barcode: str) -> dict:
    """Fetch a single product by its barcode (OpenFoodFacts 'code')."""
    url = f"{BASE_URL}/api/v2/product/{barcode}.json"
    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    data = response.json()

    if data.get("status") != 1 or "product" not in data:
        raise ExternalAPIError(f"No product found for barcode '{barcode}'")

    return _to_inventory_fields(data["product"], barcode=barcode)