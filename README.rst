.. |...| unicode:: U+2026   .. ellipsis

===================
lightspeed-api-python-client
===================

The Lightspeed API Client for Python is a client library for accessing Lightspeed APIs.

Example Usage
=======

.. code:: python

    from api import LightSpeedApi
    api = LightSpeedApi()
    # Get product details
    item_id = 'SAMPLEITEMID'
    details = api.product_detail(item_id)



