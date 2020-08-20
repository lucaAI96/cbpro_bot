import cbpro
import json


"""
An extension of the authenticated_client class from the cbpro module.

Args:
    api_config (json): a json file containing key, secret, passphrase & API URL
"""

class Client(cbpro.AuthenticatedClient):

    def __init__(self, api_config):
        with open(api_config) as json_file:
            config = json.load(json_file)
        key = config["COINBASE_API_KEY"]
        secret = config["COINBASE_API_SECRET"]
        passphrase = config["COINBASE_API_PASSPHRASE"]
        api_url = config["COINBASE_API_URL"]
        super().__init__(key, secret, passphrase, api_url=api_url)