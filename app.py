import asyncio
import logging

from client import Client
from config import RPC_URLS

from odos import Odos

# Настройка логгера
def init_logger():
    logging.basicConfig(filename='myapp.log',level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    logger = logging.getLogger(__name__)

    return logger

# указание пользователем сети блокчейна
def init_chain_by_input(logger):
    while True:
        chain_name = input("Available blockchains for mint: \"Base\", \"Arbitrum\", \"Optimism\"\n"
                      "Enter blockchain for swap: ")
        if chain_name in RPC_URLS.keys():
            logger.info("Blockchain correctly!")
            return chain_name
        else:
            print("Blockchain not correctly! Please try again!\n")
            logger.warning("input blockchain not correctly!")

# указание пользователем приватного ключа
def init_pk_by_input(logger, chain_name):
    while True:
        pk = input("Enter private key: ")
        try:
            client = Client(pk, chain_name)
            if client.validate_address() and (len(pk) == 66 or len(pk) == 64):
                logger.info("Private  key correctly")
                return pk
            else:
                print("Private key not correctly!")
                logger.warning(f"input private key {pk} not correctly!")
        except Exception as exc:
            print("Private key not correctly!")
            logger.warning(exc)

# указание пользователем кол-ва нативного токена для обмена
async def init_amount_native_token_for_swap_by_input(client: Client, logger):
    while True:
        try:
            amount_native_token_for_swap = float(input("\nEnter value of native token for swap in ETH (format example-\"0.0001\") : "))
            amount_native_token_for_swap_in_wei = client.to_wei_custom(amount_native_token_for_swap)
            if await check_balance_for_swap(client, logger, amount_native_token_for_swap_in_wei):
                logger.info(f"check_balance_for_swap_by_amount for {amount_native_token_for_swap} is True")
                return amount_native_token_for_swap_in_wei
            else:
                print("\nNot enough balance for this amount! Please change amount!\n")
                logger.warning("Balance not enough for input amount nft!")
        except ValueError:
            print("Amount not number! Please try again!\n")
            logger.warning("input amount nft not correctly!")

# проверка баланса на возможность транзакции с учетом указанного  пользователем кол-ва токена
async def check_balance_for_swap(client, logger, amount_native_token_for_swap_in_wei):

    gas_price_wei = await client.w3.eth.gas_price
    logger.info(f"gas_estimate: {gas_price_wei} WEI")
    full_estimate_cost_swap = gas_price_wei + amount_native_token_for_swap_in_wei
    logger.info(f"client balance: {await client.get_balance()} WEI")

    if await client.get_balance() > full_estimate_cost_swap:
        return True

    return False

async def main():
    logger = init_logger()
    chain_name = init_chain_by_input(logger)
    pk = init_pk_by_input(logger, chain_name)
    client = Client(pk, chain_name, logger)
    amount_for_swap_in_wei = await init_amount_native_token_for_swap_by_input(client, logger)

    odos = Odos(client)
    await odos.swap(client=client, amount_in_wei=amount_for_swap_in_wei)

if __name__ == "__main__":
    asyncio.run(main())
