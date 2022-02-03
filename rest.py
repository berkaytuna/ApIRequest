import json, hmac, hashlib, time, requests, base64, logging
from requests.auth import AuthBase
from time import sleep

class CoinbaseExchangeAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(int(time.time()))
        message = timestamp + request.method + request.path_url + (request.body or '')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message.encode(), hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest())

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request

url_limit = 'https://api.pro.coinbase.com/orders'
url_orders = 'https://api.pro.coinbase.com/orders?sortedBy=created_at&sorting=desc&limit=100'
url_price = 'https://api.pro.coinbase.com/products/ETH-EUR/ticker'

# api, secret, pass
auth = CoinbaseExchangeAuth("", "", "")

body = {
    "type": "limit",
    "side": "buy",
    "price": "1",
    "size": "0.01",
    "product_id": "ETH-EUR",
}

logging.basicConfig(filename='rest.log', encoding='utf-8', format='%(asctime)s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

try:
  response = requests.request("DELETE", url_limit, auth=auth, timeout=5)
  logging.info("cancel orders: " + response.text)
  sleep(500 / 1000)
except requests.exceptions.Timeout as e:
  logging.info(e.message)

counter = 0
while True:
  try:
    response = requests.request("GET", url_orders, auth=auth, timeout=5)
    data = json.loads(response.text)
    length = len(data)
  except requests.exceptions.Timeout as e:
    logging.info(e.message)

  if length == 1 or length > 2:
    logging.info("length; " + str(length))

    try:
      response = requests.request("DELETE", url_limit, auth=auth, timeout=5)
      logging.info("cancel orders: " + response.text)
      sleep(500 / 1000)
    except requests.exceptions.Timeout as e:
      logging.info(e.message)

  elif length == 0:
    price = "0"

    try:
      response = requests.request("GET", url_price, auth=auth, timeout=5)
      data = json.loads(response.text)
      price = data['price']
      logging.info("price: " + price)
      logging.info("sell count: " + str(sell_count))
    except requests.exceptions.Timeout as e:
      logging.info(e.message)

    body['side'] = "sell"
    body['price'] = str("2800")
      
    try:
      response = requests.request("POST", url_limit, json=body, auth=auth, timeout=5)
      logging.info("sell order: " + response.text)
    except requests.exceptions.Timeout as e:
      logging.info(e.message)

    body['side'] = "buy"
    body['price'] = str("2450")

    try:
      response = requests.request("POST", url_limit, json=body, auth=auth, timeout=5)
      logging.info("buy order: " + response.text)
    except requests.exceptions.Timeout as e:
      logging.info(e.message)

  sleep(500 / 1000)
  counter = counter + 1
  if counter == 100:
    counter = 0

    try:
      response = requests.request("GET", url_price, auth=auth, timeout=5)
      data = json.loads(response.text)
      price = data['price']
      logging.info("price: " + price)
    except requests.exceptions.Timeout as e:
      logging.info(e.message)
