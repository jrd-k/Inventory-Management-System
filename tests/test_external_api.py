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

