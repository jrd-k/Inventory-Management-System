import unittest
from unittest.mock import patch, MagicMock
import database
from app import app
from external_api import fetch_by_barcode, fetch_by_name, ExternalAPIError


SAMPLE_PRODUCT = {
    "product_name": "Organic Almond Milk",
    "brands": "Silk",
    "ingredients_text": "Filtered water, almonds, cane sugar",
    "code": "3017620422003",
    "categories": "Beverages,Plant-based beverages",
    "image_front_url": "https://example.com/almond-milk.jpg",
}

class ExternalApiFunctionTestCase(unittest.TestCase):
    """Tests for external_api.py in isolation."""

    @patch("external_api.requests.get")
    def test_fetch_by_barcode_success(self, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"status": 1, "product": SAMPLE_PRODUCT},
        )
        result = fetch_by_barcode("3017620422003")
        self.assertEqual(result["product_name"], "Organic Almond Milk")
        self.assertEqual(result["brands"], "Silk")
        self.assertEqual(result["barcode"], "3017620422003")
        self.assertEqual(result["source"], "openfoodfacts")

    @patch("external_api.requests.get")
    def test_fetch_by_barcode_not_found_raises(self, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"status": 0},
        )
        with self.assertRaises(ExternalAPIError):
            fetch_by_barcode("0000000000")

    @patch("external_api.requests.get")
    def test_fetch_by_name_success(self, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"products": [SAMPLE_PRODUCT]},
        )
        result = fetch_by_name("almond milk")
        self.assertEqual(result["product_name"], "Organic Almond Milk")

    @patch("external_api.requests.get")
    def test_fetch_by_name_no_results_raises(self, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"products": []},
        )
        with self.assertRaises(ExternalAPIError):
            fetch_by_name("nonexistentproductxyz")


class ExternalApiRouteTestCase(unittest.TestCase):
    """Tests for the /inventory/external routes."""

    def setUp(self):
        database._reset()
        self.client = app.test_client()

    @patch("app.fetch_by_barcode")
    def test_preview_external_product_does_not_save(self, mock_fetch):
        mock_fetch.return_value = {
            "product_name": "Organic Almond Milk", "brands": "Silk",
            "ingredients_text": "Filtered water, almonds", "barcode": "3017620422003",
            "category": "Beverages", "image_url": "https://example.com/img.jpg",
            "source": "openfoodfacts",
        }
        resp = self.client.get("/inventory/external", query_string={"barcode": "3017620422003"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["product_name"], "Organic Almond Milk")

        # confirm nothing was written to the inventory array
        listing = self.client.get("/inventory")
        self.assertEqual(listing.get_json(), [])

    def test_preview_requires_param(self):
        resp = self.client.get("/inventory/external")
        self.assertEqual(resp.status_code, 400)

    @patch("app.fetch_by_barcode")
    def test_fetch_external_and_store_adds_to_array(self, mock_fetch):
        mock_fetch.return_value = {
            "product_name": "Organic Almond Milk", "brands": "Silk",
            "ingredients_text": "Filtered water, almonds", "barcode": "3017620422003",
            "category": "Beverages", "image_url": "https://example.com/img.jpg",
            "source": "openfoodfacts",
        }
        resp = self.client.post("/inventory/external", json={
            "barcode": "3017620422003", "quantity": 5, "price": 500,
        })
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertEqual(data["product_name"], "Organic Almond Milk")
        self.assertEqual(data["quantity"], 5)
        self.assertEqual(data["source"], "openfoodfacts")
        self.assertIn("id", data)

        # confirm it actually landed in the inventory array
        listing = self.client.get("/inventory").get_json()
        self.assertEqual(len(listing), 1)

    def test_fetch_external_requires_barcode_or_name(self):
        resp = self.client.post("/inventory/external", json={})
        self.assertEqual(resp.status_code, 400)

    @patch("app.fetch_by_barcode")
    def test_fetch_external_not_found_returns_404(self, mock_fetch):
        mock_fetch.side_effect = ExternalAPIError("No product found")
        resp = self.client.post("/inventory/external", json={"barcode": "000"})
        self.assertEqual(resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()
