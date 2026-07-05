# Inventory-Management-System

A Flask REST API for a small retail company's admin portal. It supports full
CRUD on inventory items stored in an in-memory array, pulls real product data
from the [OpenFoodFacts API](https://world.openfoodfacts.org/data) by barcode
or name, and ships with a CLI client and an automated test suite.

# Features

- Flask REST API — CRUD endpoints for inventory items (`/inventory`), plus a search helper route.
- Simulated data storage — a plain Python list acting as a mock database, with each item shaped like OpenFoodFacts' own schema (`product_name`, `brands`, `ingredients_text`) plus retail fields (`quantity`, `price`, `barcode`).
- External API integration — fetch product details from OpenFoodFacts by barcode or name, preview them, or add them straight into the inventory array.
- CLI client — add, view, update, delete, and find items, all via HTTP calls to the API.
- Automated tests — separate suites for API endpoints, CLI commands, and external API interactions (with all external HTTP calls mocked, so tests run offline).

## Project Structure
inventory-management-system/
├── app.py                    # Flask app + all routes
├── database.py                # In-memory array acting as the "database"
├── external_api.py            # OpenFoodFacts client
├── cli.py                     # CLI client
├── tests/
│   ├── test_api.py            # CRUD endpoint tests
│   ├── test_cli.py            # CLI command tests (mocked HTTP)
│   └── test_external_api.py   # External API tests (mocked HTTP)
├── requirements.txt
├── .gitignore
└── README.md

## Setup

```bash
# 1. Clone and enter the repo
git clone https://github.com/jrd-k/Inventory-Management-System
cd inventory-management-system

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate       

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the API
python app.py
```

The API runs at `http://127.0.0.1:5000`. Data lives only in memory — restarting
the server clears the inventory array, since there's no database file.

## API Endpoints

| Method | Endpoint                                     | Description                                            |
|--------|-----------------------------------------------|----------------------------------------------------------|
| GET    | `/inventory`                                  | Fetch all inventory items                               |
| GET    | `/inventory/<id>`                             | Fetch a single item                                      |
| POST   | `/inventory`                                  | Add a new item                                           |
| PATCH  | `/inventory/<id>`                             | Update an item (price, quantity, etc.)                   |
| DELETE | `/inventory/<id>`                             | Remove an item                                            |
| GET    | `/inventory/search?name=<name>`               | Helper route — search items by name                      |
| GET    | `/inventory/external?barcode=<code>` or `?name=<name>` | Preview a product from OpenFoodFacts without saving |
| POST   | `/inventory/external`                         | Fetch a product from OpenFoodFacts and add it to inventory |

### Example: create an item

```bash
curl -X POST http://127.0.0.1:5000/inventory \
  -H "Content-Type: application/json" \
  -d '{"product_name": "Blue Widget", "quantity": 10, "price": 250, "brands": "Acme"}'
```

### Example: fetch a real product from OpenFoodFacts and store it

```bash
curl -X POST http://127.0.0.1:5000/inventory/external \
  -H "Content-Type: application/json" \
  -d '{"barcode": "3017620422003", "quantity": 5, "price": 500}'
```

## CLI Usage

With the API running in one terminal, use the CLI in another:

```bash
python cli.py add --name "Blue Widget" --quantity 10 --price 250
python cli.py view                       
python cli.py view --id 1                  
python cli.py view --name "widget"       
python cli.py update 1 --price 300 --quantity 5
python cli.py delete 1

# External API integration
python cli.py find --barcode 3017620422003              # preview only, doesn't save
python cli.py find --barcode 3017620422003 --add --quantity 5 --price 350
python cli.py find --name "nutella" --add --quantity 5 --price 500
```

## Running Tests

```bash
pip install pytest   # if not already installed
pytest tests/ -v
```

Test suites, matching each feature built:

- `tests/test_api.py` — GET, POST, PATCH, DELETE on the Flask routes
- `tests/test_cli.py` — CLI command logic, with `requests` mocked
- `tests/test_external_api.py` — OpenFoodFacts integration, with HTTP calls mocked via `unittest.mock`

All external HTTP calls are mocked, so the full suite runs offline and doesn't
depend on OpenFoodFacts being reachable.

