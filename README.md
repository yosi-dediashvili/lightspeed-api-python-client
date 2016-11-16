# lightspeed-api-python-client

The Lightspeed API Client for Python is a client library for accessing Lightspeed APIs.

## Example Usage:

```python
from lightspeed_api import LightspeedAPI
api = LightspeedAPI("YOUR_OAUTH_TOKEN")
# Get product details

for category in api.leaf_categories().get('Category'):
    products = api.list_products(category['categoryID']).get('Item')
    print(
        "Products under category `{NAME}`: {COUNT}".format(
            NAME=category['name'],
            COUNT=len(products)
        )
    )
```


