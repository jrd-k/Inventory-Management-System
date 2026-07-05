import unittest
import database
from app import app


class ApiEndpointTestCase(unittest.TestCase):
    def setUp(self):
        database._reset()  # start each test with an empty inventory array
        self.client = app.test_client()

    def _create_sample_item(self):
        return self.client.post("/inventory", json={
            "product_name": "Widget",
            "quantity": 10,
            "price": 99.5,
            "brands": "Acme",
            "barcode": "1234567890",
        })

    # ---- POST /inventory ----
    def test_create_item(self):
        resp = self._create_sample_item()
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertEqual(data["product_name"], "Widget")
        self.assertEqual(data["quantity"], 10)
        self.assertIn("id", data)

    def test_create_item_requires_product_name(self):
        resp = self.client.post("/inventory", json={"quantity": 5})
        self.assertEqual(resp.status_code, 400)