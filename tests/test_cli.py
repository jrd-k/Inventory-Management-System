import unittest
from unittest.mock import patch, MagicMock
import argparse
import cli


def _mock_response(status_code=200, json_data=None):
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data or {}
    mock.raise_for_status = MagicMock()
    return mock


class CliAddTestCase(unittest.TestCase):
    @patch("cli.requests.post")
    def test_add_sends_correct_payload(self, mock_post):
        mock_post.return_value = _mock_response(201, {
            "id": 1, "product_name": "Blue Widget", "quantity": 10,
            "price": 250, "barcode": None, "source": "manual",
        })
        args = argparse.Namespace(name="Blue Widget", quantity=10, price=250,
                                   brand=None, barcode=None)
        cli.cmd_add(args)

        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs["json"]["product_name"], "Blue Widget")
        self.assertEqual(kwargs["json"]["quantity"], 10)


class CliViewTestCase(unittest.TestCase):
    @patch("cli.requests.get")
    def test_view_all_items(self, mock_get):
        mock_get.return_value = _mock_response(200, [
            {"id": 1, "product_name": "Widget", "quantity": 5, "price": 10,
             "barcode": None, "source": "manual"},
        ])
        args = argparse.Namespace(id=None, name=None)
        cli.cmd_view(args)
        mock_get.assert_called_once_with(cli.API_BASE)

    @patch("cli.requests.get")
    def test_view_single_item_by_id(self, mock_get):
        mock_get.return_value = _mock_response(200, {
            "id": 1, "product_name": "Widget", "quantity": 5, "price": 10,
            "barcode": None, "source": "manual",
        })
        args = argparse.Namespace(id=1, name=None)
        cli.cmd_view(args)
        mock_get.assert_called_once_with(f"{cli.API_BASE}/1")

    @patch("cli.requests.get")
    def test_view_missing_item(self, mock_get):
        mock_get.return_value = _mock_response(404, {"error": "not found"})
        args = argparse.Namespace(id=999, name=None)
        cli.cmd_view(args)


class CliUpdateTestCase(unittest.TestCase):
    @patch("cli.requests.patch")
    def test_update_price_and_quantity(self, mock_patch):
        mock_patch.return_value = _mock_response(200, {
            "id": 1, "product_name": "Widget", "quantity": 3, "price": 150,
            "barcode": None, "source": "manual",
        })
        args = argparse.Namespace(id=1, name=None, quantity=3, price=150)
        cli.cmd_update(args)

        mock_patch.assert_called_once()
        _, kwargs = mock_patch.call_args
        self.assertEqual(kwargs["json"], {"quantity": 3, "price": 150})

    @patch("cli.requests.patch")
    def test_update_with_no_fields_does_not_call_api(self, mock_patch):
        args = argparse.Namespace(id=1, name=None, quantity=None, price=None)
        cli.cmd_update(args)
        mock_patch.assert_not_called()
        

class CliDeleteTestCase(unittest.TestCase):
    @patch("cli.requests.delete")
    def test_delete_item(self, mock_delete):
        mock_delete.return_value = _mock_response(200, {"message": "Item 1 deleted"})
        args = argparse.Namespace(id=1)
        cli.cmd_delete(args)
        mock_delete.assert_called_once_with(f"{cli.API_BASE}/1")


class CliFindTestCase(unittest.TestCase):
    @patch("cli.requests.get")
    def test_find_preview_only(self, mock_get):
        mock_get.return_value = _mock_response(200, {
            "product_name": "Nutella", "barcode": "3017620422003", "source": "openfoodfacts",
        })
        args = argparse.Namespace(barcode="3017620422003", name=None, add=False,
                                   quantity=0, price=0.0)
        cli.cmd_find(args)
        mock_get.assert_called_once_with(f"{cli.API_BASE}/external",
                                          params={"barcode": "3017620422003"})

    @patch("cli.requests.post")
    def test_find_with_add_flag_calls_post(self, mock_post):
        mock_post.return_value = _mock_response(201, {
            "id": 1, "product_name": "Nutella", "quantity": 5, "price": 500,
            "barcode": "3017620422003", "source": "openfoodfacts",
        })
        args = argparse.Namespace(barcode="3017620422003", name=None, add=True,
                                   quantity=5, price=500)
        cli.cmd_find(args)

        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs["json"]["barcode"], "3017620422003")
        self.assertEqual(kwargs["json"]["quantity"], 5)

    def test_find_without_barcode_or_name_does_nothing(self):
        args = argparse.Namespace(barcode=None, name=None, add=False, quantity=0, price=0.0)
        # should just print a message and return, no network call attempted
        cli.cmd_find(args)


if __name__ == "__main__":
    unittest.main()