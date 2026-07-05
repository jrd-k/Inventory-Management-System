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

    #POST
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
  
    #GET
    def test_get_all_items(self):
        self._create_sample_item()
        self._create_sample_item()
        resp = self.client.get("/inventory")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.get_json()), 2)

    def test_get_all_items_empty(self):
        resp = self.client.get("/inventory")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), [])

    def test_get_single_item(self):
        created = self._create_sample_item().get_json()
        resp = self.client.get(f"/inventory/{created['id']}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["product_name"], "Widget")

    def test_get_missing_item_returns_404(self):
        resp = self.client.get("/inventory/999")
        self.assertEqual(resp.status_code, 404)

    
    def test_search_items_by_name(self):
        self._create_sample_item()
        resp = self.client.get("/inventory/search", query_string={"name": "wid"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.get_json()), 1)

    def test_search_requires_name_param(self):
        resp = self.client.get("/inventory/search")
        self.assertEqual(resp.status_code, 400)

    def test_update_item_price_and_quantity(self):
        created = self._create_sample_item().get_json()
        resp = self.client.patch(f"/inventory/{created['id']}", json={"price": 150, "quantity": 3})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["price"], 150)
        self.assertEqual(data["quantity"], 3)
        self.assertEqual(data["product_name"], "Widget")

    def test_update_missing_item_returns_404(self):
        resp = self.client.patch("/inventory/999", json={"quantity": 5})
        self.assertEqual(resp.status_code, 404)
