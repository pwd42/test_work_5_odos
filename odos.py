from aiohttp import ClientSession

from client import Client

from config import TOKENS_PER_CHAIN

class Odos:
    def __init__(self, client: Client):
        self.client = client
        self.base_api_url = "https://api.odos.xyz"

    @staticmethod
    async def make_request(
            method: str = 'GET', url: str = None, params: dict = None, headers: dict = None, json: dict = None
    ):

        async with ClientSession() as session:
            async with session.request(method=method, url=url, params=params, headers=headers, json=json) as response:
                if response.status in [200, 201]:
                    return await response.json()
                raise RuntimeError(f"Bad request to Odos API. Response status: {response.status} \n"
                                   f"Response full: {await response.json()}")

    async def get_path(self, amount_in_wei: int, chain_name_for_swap: str = "Base"):
        url = f'{self.base_api_url}/sor/quote/v2'
        tokens_config = TOKENS_PER_CHAIN[chain_name_for_swap]
        from_token_address = tokens_config["ETH"]
        to_token_address = tokens_config["DAI"]

        json_request_body = {
            "chainId": self.client.chain_id,
            "inputTokens":  [
                {
                  "amount": f"{amount_in_wei}",
                  "tokenAddress": from_token_address
                }
            ],
            "outputTokens": [
                {
                  "proportion": 1,
                  "tokenAddress": to_token_address
                }
            ],
            "slippageLimitPercent": 0.5,
            "userAddr": self.client.address
        }

        response = await self.make_request(method = 'POST', url=url, json=json_request_body)
        self.client.logger.info(f"Response get_path(): {response}")
        return response

    async def get_swap_data(self, client: Client, amount_in_wei: int):
        url = f'{self.base_api_url}/sor/assemble'
        response_get_path = await self.get_path(amount_in_wei, client.chain_name_code)

        json_request_body = {
            "pathId": response_get_path["pathId"],
            "simulate": False,
            "userAddr": client.address
        }

        response = await self.make_request(method = 'POST', url=url, json=json_request_body)
        self.client.logger.info(f"Response get_swap_data(): {response}")
        return response

    async def swap(self, client: Client, amount_in_wei: int):
        response = await self.get_swap_data(client, amount_in_wei)

        transaction_response = response['transaction']
        transaction_response['value'] = int(response['transaction']['value'])

        self.client.logger.info(f"Prepared transaction by API: {transaction_response}")
        return await self.client.send_transaction(transaction=transaction_response)
