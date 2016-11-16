import constants

import json
import requests
import logging

from urlparse import urljoin


class LightspeedAPIException(Exception):
    pass


class LightspeedAPIUnavailable(LightspeedAPIException):
    def __init__(self, url, message=None):
        self.message = message or "API is unavailable"
        self.url = url

    def __str__(self):
        return self.message


class LightspeedAPIRequestError(LightspeedAPIException):
    def __init__(self, message):
        super(LightspeedAPIRequestError, self).__init__(message)


class LightspeedAPI:
    """
    Lightspeed api client
    """

    def __init__(self, auth_token, log_level=logging.DEBUG):
        self.retry_count = 0

        self.MAX_RETRIES = constants.MAX_RETRIES
        self.AUTH_TOKEN = auth_token
        self.HEADER = {"Authorization": "Bearer {}".format(self.AUTH_TOKEN)}
        self.ACCOUNT_ID = self.get_account().get('accountID')
        self.URL = constants.BASE_URL.format(ACCOUNT_ID=self.ACCOUNT_ID)

        logging.basicConfig(level=log_level)

    def get_account(self):
      return self._get_response(None, constants.ACCOUNT_URL, {}).get('Account')

    def _create_request(self, action, url=None, **kwargs):
        datas = {}
        datas.update(kwargs)
        req_url = url or constants.URL_MAP.get(action, '/')
        request_url = self._get_url(req_url)
        return request_url, datas

    def _get_url(self, pathname):
        """ For each pathname returns corresponding URL  """

        return urljoin(self.URL, pathname)

    def _get_response(self, action, request_url, datas):
        """Perform json-request to API

        :param action: method action (name of the function in API)
        :type action: str
        :param request_url: Absolute url to API.
        :type request_url: str
        :param headers: header contents to API.
        :type request_url: dict
        :param datas: Datas to send to the API.
        :type datas: dict
        :return: json response
        :rtype: dict
        """
        json_response = {}
        try:
            req = requests.get(
                request_url,
                params=datas,
                headers=self.HEADER)
            content = req.content
            logging.debug(content)
        except requests.exceptions.RequestException as e:
            """ API not available """
            raise LightspeedAPIUnavailable(self.URL, str(e))
        try:
            json_response = req.json()
        except Exception as e:
            raise LightspeedAPIRequestError(e)
        return json_response

    def _retry_request(self, action, url, request_url, json_response, **kwargs):
        if self.retry_count <= self.MAX_RETRIES:
            self.retry_count += 1
            logging.warning(
                "Error found in request, action:%s, Request"
                "Url:%s, retry count:%s, kwargs:%s, error:%s" % (
                    action, request_url, self.retry_count,
                    kwargs, json_response.get(
                        'error') or json_response.get('errors')))
            return self.request(action, url=url, **kwargs)
        elif self.retry_count > self.MAX_RETRIES:
            logging.warning(
                "Request aborting, max retryes"
                "completed. Action:%s, Request"
                "Url:%s, retry count:%s ,kwargs:%s, error:%s" % (
                    action, request_url, self.retry_count,
                    kwargs, json_response.get(
                        'error') or json_response.get('errors')))
        self.retry_count = 0
        return {}

    def request(self, action, url=None, **kwargs):
        """Create and perform json-request to API

        :param action: method action (name of the function in API)
        :type action: str
        :param url: If this is a specific url, url should be given.
        :type action: str
        :return: json response
        :rtype: dict
        """
        request_url, datas = self._create_request(
            action, url, **kwargs)
        json_response = {}
        try:
            json_response = self._get_response(
                action, request_url, datas)
        except LightspeedAPIUnavailable:
            return self._retry_request(
                action, url, request_url, json_response, **kwargs)
        if not json_response:
            raise LightspeedAPIRequestError("Response contains no data")
        if json_response.get('errorClass'):
            logging.warning(
                "Error response received, "
                "Action:%s, Request"
                "Url:%s, kwargs:%s, error:%s" % (
                    action, request_url,
                    kwargs, json_response.get(
                        'message')))
        return json_response

    def post_request(self, action, url=None, post_json=None, **kwargs):
        """Create and perform json-request to API

        :param action: method action (name of the function in API)
        :type action: str
        :param url: If this is a specific url, url should be given.
        :type action: str
        :return: json response
        :rtype: dict
        """
        request_url, datas = self._create_request(
            action, url, **kwargs)
        json_response = {}
        try:
            json_response = self._get_response_post(
                action, request_url, datas, post_json)
        except LightspeedAPIUnavailable:
            return self._retry_request(
                action, url, request_url, json_response, **kwargs)
        if not json_response:
            raise LightspeedAPIRequestError("Response contains no data")
        if json_response.get('errorClass'):
            logging.warning(
                "Error response received, "
                "Action:%s, Request"
                "Url:%s, kwargs:%s, error:%s" % (
                    action, request_url,
                    kwargs, json_response.get(
                        'message')))
        return json_response

    def _get_response_post(self, action, request_url, datas, post_json):
        """Perform json-request to API

        :param action: method action (name of the function in API)
        :type action: str
        :param request_url: Absolute url to API.
        :type request_url: str
        :param headers: header contents to API.
        :type request_url: dict
        :param datas: Datas to send to the API.
        :type datas: dict
        :return: json response
        :rtype: dict
        """
        json_response = {}
        try:
            req = requests.post(
                request_url,
                params=datas,
                json=post_json,
                headers=self.HEADER)
            content = req.json()
            logging.debug(content)
        except requests.exceptions.RequestException as e:
            """ API not available """
            raise LightspeedAPIUnavailable(self.URL, str(e))
        try:
            json_response = req.json()
        except Exception as e:
            raise LightspeedAPIRequestError(e)
        return json_response

    def _get_response_put(self, action, request_url, datas, post_json):
        """Perform json-request to API

        :param action: method action (name of the function in API)
        :type action: str
        :param request_url: Absolute url to API.
        :type request_url: str
        :param headers: header contents to API.
        :type request_url: dict
        :param datas: Datas to send to the API.
        :type datas: dict
        :return: json response
        :rtype: dict
        """
        json_response = {}
        try:
            req = requests.put(
                request_url,
                params=datas,
                json=json.loads(post_json),
                headers=self.HEADER)
            content = req.json()
            logging.debug(content)
        except requests.exceptions.RequestException as e:
            """ API not available """
            raise LightspeedAPIUnavailable(self.URL, str(e))
        try:
            json_response = req.json()
        except Exception as e:
            raise LightspeedAPIRequestError(e)
        return json_response

    def post_request_xml(self, action, url=None, post_xml=None, **kwargs):
        """Create and perform json-request to API

        :param action: method action (name of the function in API)
        :type action: str
        :param url: If this is a specific url, url should be given.
        :type action: str
        :return: json response
        :rtype: dict
        """
        request_url, datas = self._create_request(
            action, url, **kwargs)
        xml_response = ''
        try:
            xml_response, status_code = self._get_response_post_xml(
                action, request_url, datas, post_xml)
        except:
            pass
        if not xml_response:
            raise LightspeedAPIRequestError("Response contains no data")
        return xml_response, status_code

    def _get_response_post_xml(self, action, request_url, datas, post_xml):
        """Perform xml to API

        :param action: method action (name of the function in API)
        :type action: str
        :param request_url: Absolute url to API.
        :type request_url: str
        :param headers: header contents to API.
        :type headers: dict
        :param datas: Datas to send to the API.
        :type datas: dict
        :return: xml response
        :rtype: xml
        """
        xml_response = ''
        try:
            req = requests.post(
                request_url,
                params=datas,
                data=post_xml,
                headers=self.HEADER)
        except requests.exceptions.RequestException as e:
            """ API not available """
            raise LightspeedAPIUnavailable(self.URL, str(e))
        try:
            xml_response = req.content
        except Exception as e:
            raise LightspeedAPIRequestError(e)
        else:
            return xml_response, req.status_code

    def put_request(self, action, url=None, put_json=None, **kwargs):
        """Create and perform json-request to API

        :param action: method action (name of the function in API)
        :type action: str
        :param url: If this is a specific url, url should be given.
        :type action: str
        :return: json response
        :rtype: dict
        """
        request_url, datas = self._create_request(
            action, url, **kwargs)
        json_response = {}
        try:
            json_response = self._get_response_put(
                action, request_url, datas, put_json)
        except LightspeedAPIUnavailable:
            pass
        if not json_response:
            raise LightspeedAPIRequestError("Response contains no data")
        if json_response.get('errorClass'):
            logging.warning(
                "Error response received, "
                "Action:%s, Request"
                "Url:%s, kwargs:%s, error:%s" % (
                    action, request_url,
                    kwargs, json_response.get(
                        'message')))
        return json_response

    def leaf_categories(self):
        """
        :return: Level 1 categories in lightspeed.
        """
        querystring = {'nodeDepth': '1'}
        leaf_categories = self.request(action='category', **querystring)
        return leaf_categories if 'Category' in leaf_categories else None

    def categories(self):
        """
        :return: All of the categories in lightspeed.
        """
        categories = self.request(action='category')
        return categories if 'Category' in categories else None

    def manufacturers(self, offset=0):
        """

        :return: all the manufacturers.
        """
        querystring = {'offset': offset}
        manufacturers = self.request(action='manufacturer', **querystring)
        return manufacturers if 'Manufacturer' in manufacturers else None

    def product_detail(self, item_id):
        """

        :param item_id: Item id in lightspeed.
        :return: Returns product details.
        """
        querystring = {'itemID': item_id, 'load_relations': '["Images", "ItemShops", "Manufacturer", "CustomFieldValues", "ItemVendorNums"]'}
        product = self.request(action='item', **querystring)
        return product if 'Item' in product else None

    def list_products(self, cat_list, tag=None, offset=0, limit=60, reorder_level=None, shop_id=None):
        """
        :return: Returns products under a category.
        """
        querystring = {'categoryID': "IN,{0}".format(cat_list), 'offset': offset,
                       'load_relations': '["Images", "Manufacturer", "ItemShops", "Tags"]', 'limit': limit,
                       'orderby': 'createTime', 'orderby_desc': '1'}
        querystring['or'] = 'ItemShops.reorderLevel=>,0|ItemShops.qoh=>,0'
        if shop_id is not None:
            querystring['ItemShops.shopID'] = shop_id
        if tag is not None:
            querystring['tag'] = tag
        products = self.request(action='item', **querystring)
        return products if 'Item' in products else None

    def get_products(self, item_ids):
        """

        :param item_ids: list containing item_id of products.
        :return: Return products corresponding to the passed ids.
        """
        item_ids = ','.join(str(item_id) for item_id in item_ids)
        querystring = {'load_relations': '["Images", "ItemShops", "Manufacturer"]', 'itemID': 'IN,[%s]' %(item_ids)}
        products = self.request(action='item', **querystring)
        return products if 'Item' in products else None

    def search_products(self, search_query, offset=0, limit=60, reorder_level=None, shop_id=None, cat_list=[]):
        """

        :param search_query: search query.
        :return: products matching the search query.
        """
        search_query = '~,%{0}%'.format(search_query)
        querystring = {'description': search_query,
                       'load_relations': '["Images", "Manufacturer", "ItemShops", "Category", "Tags"]',
                       'limit': limit, 'offset': offset, 'orderby': 'createTime', 'orderby_desc': '1'}
        if len(cat_list):
            querystring.update({'categoryID': "IN,{}".format(cat_list)})

        # querystring['ItemShops.reorderLevel'] = '>=,{0}'.format(reorder_level)
        querystring['or'] = 'ItemShops.reorderLevel=>,0|ItemShops.qoh=>,0'
        if shop_id is not None:
            querystring['ItemShops.shopID'] = shop_id
        products = self.request(action='item', **querystring)
        return products if 'Item' in products else None

    def search_products_brand(self, brand, offset=0, limit=60, reorder_level=None, shop_id=None, cat_list=[]):
        """

        :param search_query: search query.
        :return: products matching the search query.
        """

        querystring = {'Manufacturer.manufacturerID': brand,
                       'load_relations': '["Images", "Manufacturer", "ItemShops", "Category", "Tags"]',
                       'limit': limit, 'offset': offset, 'orderby': 'createTime', 'orderby_desc': '1'}
        if len(cat_list):
            querystring.update({'categoryID': "IN,{}".format(cat_list)})

        querystring['or'] = 'ItemShops.reorderLevel=>,0|ItemShops.qoh=>,0'
        if shop_id is not None:
            querystring['ItemShops.shopID'] = shop_id
        products = self.request(action='item', **querystring)
        return products if 'Item' in products else None

    def get_customers(self, email_id):
        """
        Fetches Customer matching the given email id
        :param email: email id of the Customer
        :return: returns Customers having given email id.
        """
        querystring = {'load_relations': '["Contact"]', 'Contact.email': email_id}
        customers = self.request(action='customer', **querystring)
        return customers if 'Customer' in customers else None

    def create_customer(self, customer_dict):
        """
        :param customer_dict: Dictionary containing customer data to post.
        :return:
        """

        created = self.post_request(action='customer', post_json=customer_dict)
        return created if 'Customer' in created else None

    def get_sales(self, customer_id, ordering='1'):
        """

        :param customer_id: CustomerID retrieved from lightspeed.
        :return: returns Sales records of the customer.
        """
        querystring = {'load_relations': 'all',
                       'Customer.customerID': customer_id,
                       'orderby': 'timeStamp', 'orderby_desc': ordering}
        sales = self.request(action='sale', **querystring)
        return sales if 'Sale' in sales else None

    def generate_sale(self, sale_xml):
        sale_xml, status_code = self.post_request_xml(action='sale_xml', post_xml=sale_xml)
        return sale_xml, status_code

    def generate_coupon(self, coupon_xml):
        sale_xml, status_code = self.post_request_xml(action='item-xml', post_xml=coupon_xml)
        return sale_xml, status_code

    def update_customer(self, customer_id, customer_dict):
        """

        :param customer_id:
        :param customer_dict:
        :return:
        """
        request_url = 'Customer/{}.json'.format(customer_id)
        updated = self.put_request(action='customer', url=request_url, put_json=customer_dict)
        return updated if 'Customer' in updated else None

    def get_customer_using_id(self, customer_id):
        querystring = {'customerID': customer_id}
        customers = self.request(action='customer', **querystring)
        return customers if 'Customer' in customers else None

    def get_vendors(self, offset=0):
        querystring = {'offset': offset}
        vendors = self.request(action='vendor', **querystring)
        return vendors if 'Vendor' in vendors else None

    def fetch_all_products(self, offset=0, limit=100, reorder_level=None, shop_id=None):
        """
        :return: Returns all the products
        """
        querystring = {'offset': offset,
                       'load_relations': '["Images", "Manufacturer", "ItemShops", "Tags"]', 'limit': limit,
                       'orderby': 'createTime', 'orderby_desc': '1'}

        products = self.request(action='item', **querystring)
        return products if 'Item' in products else None
