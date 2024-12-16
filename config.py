RPC_URLS = {
    "Arbitrum": "https://endpoints.omniatech.io/v1/arbitrum/one/public",
    "Optimism": "https://op-pokt.nodies.app",
    "Base": "https://1rpc.io/base"
    # "Base": "https://base-pokt.nodies.app"
}

EXPLORERS_URL = {
    "Arbitrum": "https://arbiscan.io/",
    "Optimism": "https://optimistic.etherscan.io/",
    "Base": "https://basescan.org/"
}

CHAIN_ID_BY_NAME = {
    'Arbitrum': 42161,
    'Optimism': 10,
    'Base': 8453
}
TOKENS_PER_CHAIN = {
    'Arbitrum': {
        "ETH": "0x0000000000000000000000000000000000000000",
        "DAI": "0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1"
    },
    'Optimism': {
        "ETH": "0x0000000000000000000000000000000000000000",
        "DAI":"0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1"
    },
    'Base': {
        "ETH": "0x0000000000000000000000000000000000000000",
        "DAI":"0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb"
    }
}
