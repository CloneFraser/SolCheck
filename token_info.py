import requests


class Token:
    def __init__(self, address):
        self.token_address = address
        self.token_name = ''
        self.token_symbol = ''
        self.liquidity = 0
        self.market_cap = 0
        self.token_supply = 0
        self.image_url = ''
        self.holder_percentage = 0
        self.lp_burned = ''

        response = self.get_token_info()

        self.set_token_name(response)
        self.set_token_symbol(response)
        self.set_market_cap(response)
        self.set_liquidity(response)
        self.set_token_image(response)
        self.set_token_supply()
        self.get_largest_holders()
        self.get_lp_burned()

    def get_token_info(self):
        url = 'https://api.dexscreener.com/latest/dex/tokens/' + self.token_address
        response = requests.get(url)
        parsed = response.json()['pairs']
        return parsed

    def get_largest_holders(self):
        largest_accounts_response = requests.post('API_URL', json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTokenLargestAccounts",
            "params": [self.token_address]
        })

        parsed = largest_accounts_response.json()

        largest_accounts = parsed['result']['value']
        total_amount = 0

        for x in range(10):
            address = largest_accounts[x]['address']
            amount = largest_accounts[x]['uiAmount']

            total_amount += amount

        self.holder_percentage = self.calculate_percentages(total_amount)

    def get_token_supply(self):
        supply_response = requests.post('API_URL', json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTokenSupply",
            "params": [self.token_address]
        })

        parsed = supply_response.json()
        supply = parsed['result']['value']['uiAmountString']

        return supply

    def get_lp_mint_address(self):
        url = (f'https://api-v3.raydium.io/pools/info/mint?mint1={self.token_address}&'
               f'poolType=all&poolSortField=default&sortType=desc&pageSize=1000&page=1')

        response = requests.get(url)
        parsed = response.json()

        lp_mint = parsed['data']['data'][0]['lpMint']['address']
        return lp_mint

    def get_lp_burned(self):
        lp_mint_address = self.get_lp_mint_address()
        is_burned = False

        signature_response = requests.post('API_URL', json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [lp_mint_address]
        })

        parsed = signature_response.json()

        for transaction in parsed['result']:
            signature = transaction['signature']

            transaction_response = requests.post('API_URL', json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction",
                "params": [signature, {"maxSupportedTransactionVersion": 0}]
            })

            parsed = transaction_response.json()

            try:
                logs = parsed['result']['meta']['logMessages']

                if 'Program log: Instruction: Burn' in logs:
                    is_burned = True
                    break
            except:
                continue

        self.lp_burned = is_burned

    def calculate_percentages(self, amount):
        percentage = round((amount/self.token_supply)*100, 2)
        return percentage

    def set_token_image(self, response):
        self.image_url = response[0]['info']['imageUrl']

    def set_token_supply(self):
        supply = self.get_token_supply()
        self.token_supply = float(supply)

    def set_token_name(self, response):
        self.token_name = response[0]['baseToken']['name']

    def set_token_symbol(self, response):
        self.token_symbol = response[0]['baseToken']['symbol']

    def set_market_cap(self, response):
        self.market_cap = response[0]['fdv']

    def set_liquidity(self, response):
        self.liquidity = response[0]['liquidity']['usd']

