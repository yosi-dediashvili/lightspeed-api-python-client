"""
Lightspeed SDK Configuration
"""

ACCOUNT_URL = "https://api.merchantos.com/API/Account.json"

BASE_URL = "https://api.merchantos.com/API/Account/{ACCOUNT_ID}/"
MAX_RETRIES = 5
DEBUG = False

URL_MAP = {
  "category": "Category.json",
  "item": "Item.json",
  "customer": "Customer.json",
  'sale': "Sale.json",
  'sale_xml': 'Sale',
  'manufacturer': 'Manufacturer.json',
  'vendor': 'Vendor.json',
  'item-xml': 'Item',
  'department': "Department.json",
  'price_level': "PriceLevel.json"
}