import asyncio

from web3 import AsyncWeb3, AsyncHTTPProvider
from web3.exceptions import TransactionNotFound
from config import RPC_URLS, EXPLORERS_URL, CHAIN_ID_BY_NAME


class Client:
    def __init__(self, private_key, chain_name_code, logger = None):
        self.logger = logger
        self.private_key = private_key
        # request_kwargs = {'proxy': f'http://{proxy}'}
        rpc_url = RPC_URLS[chain_name_code]
        self.chain_name_code = chain_name_code
        # self.chain_token = 'ETH'
        self.chain_id = CHAIN_ID_BY_NAME[chain_name_code]
        # self.proxy = proxy
        self.eip_1559 = True
        self.explorer_url = EXPLORERS_URL[chain_name_code]
        self.w3 = AsyncWeb3(AsyncHTTPProvider(rpc_url))
        self.address = self.w3.to_checksum_address(self.w3.eth.account.from_key(self.private_key).address)


    def validate_address(self):
        return self.w3.is_address(self.address)

    def to_wei_custom(self, number: int | float, decimals: int = 18):

        unit_name = {
            6: 'mwei',
            9: 'gwei',
            18: 'ether',
        }.get(decimals)

        if not unit_name:
            raise RuntimeError(f'Can not find unit name with decimals: {decimals}')

        return self.w3.to_wei(number, unit_name)

    def from_wei_custom(self, number: int | float, decimals: int):

        unit_name = {
            6: 'mwei',
            9: 'gwei',
            18: 'ether',
        }.get(decimals)

        if not unit_name:
            raise RuntimeError(f'Can not find unit name with decimals: {decimals}')

        return self.w3.from_wei(number, unit_name)


    async def get_balance(self):
        try:
            return await self.w3.eth.get_balance(self.address)
        except Exception as e:
            print(f"Ошибка при получении баланса: {e}")
            return None

    async def send_transaction(self, transaction=None):
        signed_raw_tx = self.w3.eth.account.sign_transaction(transaction, self.private_key).rawTransaction
        self.logger.info('Successfully signed transaction!')

        tx_hash_bytes = await self.w3.eth.send_raw_transaction(signed_raw_tx)
        self.logger.info('Successfully sent transaction!')

        tx_hash_hex = self.w3.to_hex(tx_hash_bytes)

        return await self.wait_tx(tx_hash_hex)

    async def wait_tx(self, tx_hash):
        total_time = 0
        timeout = 120
        poll_latency = 10
        while True:
            try:
                receipts = await self.w3.eth.get_transaction_receipt(tx_hash)
                status = receipts.get("status")
                if status == 1:
                    self.logger.info(f'Transaction was successful: {self.explorer_url}tx/{tx_hash}')
                    return True
                elif status is None:
                    await asyncio.sleep(poll_latency)
                else:
                    self.logger.error(f'Transaction failed: {self.explorer_url}tx/{tx_hash}')
                    return False
            except TransactionNotFound:
                if total_time > timeout:
                    self.logger.warning(f"Transaction is not in the chain after {timeout} seconds")
                    return False
                total_time += poll_latency
                await asyncio.sleep(poll_latency)
