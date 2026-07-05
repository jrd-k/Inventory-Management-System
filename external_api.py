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



def fetch_by_name(name: str) -> dict:
    """Search for a product by name and return the best (first) match."""
    url = f"{BASE_URL}/cgi/search.pl"
    params = {
        "search_terms": name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 1,
    }
    response = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    data = response.json()

    products = data.get("products", [])
    if not products:
        raise ExternalAPIError(f"No product found matching name '{name}'")

    return _to_inventory_fields(products[0])