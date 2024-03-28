import configparser
import json
import os
import time
import asyncio
import base58
import logging

from time import sleep
from typing import List, AsyncIterator, Tuple
from asyncstdlib import enumerate
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.rpc.config import RpcTransactionLogsFilterMentions
from solana.rpc.websocket_api import connect
from solana.rpc.commitment import Finalized
from solana.rpc.api import Client
from solana.exceptions import SolanaRpcException
from spl.token.instructions import get_associated_token_address
from websockets.exceptions import ConnectionClosedError, ProtocolError
from solana.rpc.commitment import Commitment
from solana.rpc.websocket_api import SolanaWsClientProtocol
from solders.rpc.responses import RpcLogsResponse, SubscriptionResult, LogsNotification
from solders.signature import Signature
from utils.layout import SPL_MINT_LAYOUT, MARKET_STATE_LAYOUT_V3


async def main():
    async for websocket in connect(wss_url):
        try:
            subscription_id = await subscribe_to_logs(
                websocket,
                RpcTransactionLogsFilterMentions(raydium_lp_v4),
                Finalized
            )
            async for i, signature in enumerate(process_messages(websocket, log_instruction)):  # type: ignore
                try:
                    get_tokens(signature, raydium_lp_v4)
                except SolanaRpcException as err:
                    print(f"sleep for 5 seconds and try again")
                    sleep(5)
                    continue
        except (ProtocolError, ConnectionClosedError) as err:
            continue
        except KeyboardInterrupt:
            if websocket:
                await websocket.logs_unsubscribe(subscription_id)


async def subscribe_to_logs(websocket: SolanaWsClientProtocol,
                            mentions: RpcTransactionLogsFilterMentions,
                            commitment: Commitment) -> int:
    await websocket.logs_subscribe(
        filter_=mentions,
        commitment=commitment
    )
    first_resp = await websocket.recv()
    return get_subscription_id(first_resp)  # type: ignore


def get_subscription_id(response: SubscriptionResult) -> int:
    return response[0].result


async def process_messages(websocket: SolanaWsClientProtocol,
                           instruction: str) -> AsyncIterator[Signature]:
    async for idx, msg in enumerate(websocket):
        value = get_msg_value(msg)
        if not idx % 100:
            print(f'Scanning Raydium: {idx}')
            pass
        for log in value.logs:
            if instruction not in log:
                continue
            yield value.signature


def get_msg_value(msg: List[LogsNotification]) -> RpcLogsResponse:
    return msg[0].result.value


def get_tokens(signature: Signature, raydium_lp_v4: Pubkey) -> None:
    transaction = solana_client.get_transaction(
        signature,
        encoding="jsonParsed",
        max_supported_transaction_version=0
    )

    instructions = get_instructions(transaction)
    filtred_instuctions = instructions_with_program_id(instructions, raydium_lp_v4)
    for instruction in filtred_instuctions:
        tokens = get_tokens_info(instruction)
        print_table(tokens)
        print(f"DexScreener : https://dexscreener.com/solana/{str(tokens[0])}\n")
        # print(f"signature info, https://solscan.io/tx/{signature}")
        get_pool_infos(tokens[3])
        break


def get_instructions(transaction):
    instructions = transaction \
        .value \
        .transaction \
        .transaction \
        .message \
        .instructions
    return instructions


def instructions_with_program_id(instructions, program_id):
    return (instruction for instruction in instructions
            if instruction.program_id == program_id)


def get_pool_infos(accounts):
    baseMintAccount = solana_client.get_account_info(accounts[8])
    quoteMintAccount = solana_client.get_account_info(accounts[9])
    marketAccount = solana_client.get_account_info(accounts[16])
    if baseMintAccount == None or quoteMintAccount == None or marketAccount == None:
        raise Exception('get account info error')

    baseMintInfo = SPL_MINT_LAYOUT.parse(baseMintAccount.value.data)
    quoteMintInfo = SPL_MINT_LAYOUT.parse(quoteMintAccount.value.data)
    marketInfo = MARKET_STATE_LAYOUT_V3.parse(marketAccount.value.data)
    poolInfos = {
        "id": accounts[4],
        "baseMint": accounts[8],
        "quoteMint": accounts[9],
        "lpMint": accounts[7],
        "baseDecimals": baseMintInfo.decimals,
        "quoteDecimals": quoteMintInfo.decimals,
        "lpDecimals": baseMintInfo.decimals,
        'version': 4,
        'authority': accounts[5],
        'openOrders': accounts[6],
        'targetOrders': accounts[12],
        'baseVault': accounts[10],
        'quoteVault': accounts[11],
        'marketVersion': 3,
        'marketProgramId': solana_client.get_account_info_json_parsed(accounts[16]).value.owner,
        'marketId': accounts[16],
        'marketAuthority': get_associated_token_address(marketInfo['ownAddress'], accounts[16]),
        'marketBaseVault': Pubkey.from_bytes(marketInfo.baseVault),
        'marketQuoteVault': Pubkey.from_bytes(marketInfo.quoteVault),
        'marketBids': Pubkey.from_bytes(marketInfo.bids),
        'marketAsks': Pubkey.from_bytes(marketInfo.asks),
        'marketEventQueue': Pubkey.from_bytes(marketInfo.eventQueue)
    }

    if not os.path.exists('pool_infos.json'):
        with open('pool_infos.json', 'w') as fw:
            fw.write('[]')

    with open('pool_infos.json', 'r') as fw:
        contents = json.load(fw)

    _poolInfos = {}
    for name, value in poolInfos.items():
        if isinstance(value, int):
            _poolInfos[name] = value
        else:
            _poolInfos[name] = str(value)

    pool_infos = {
        "name": str(accounts[8]),
        "value": _poolInfos,
    }
    contents.append(pool_infos)

    with open('pool_infos.json', 'w') as fw:
        json.dump(contents, fw)

    fw.close()
    result = solana_client.get_account_info_json_parsed(poolInfos.get('quoteVault')).value.lamports
    lamport_per_sol = 1000000000
    pool_number = result / lamport_per_sol
    print(f'pool size: {pool_number}')

    if pool_number > int(pool_size):
        if eval(is_buy):
            from utils.trade_utils import sell, buy
            private_key_bytes = base58.b58decode(private_key_string)
            payer = Keypair.from_bytes(private_key_bytes)
            token_address = str(accounts[8])
            print('START BUY ORDER')
            buy_flag = buy(solana_client, token_address, payer, float(sol_amount), poolInfos)
            logging.info('create buy order.')
            logging.info(f"dex trade, https://dexscreener.com/solana/{token_address}")
            if buy_flag:
                time.sleep(eval(wait_seconds))
                if not eval(is_sell):
                    logging.info('switch sell is off')
                else:
                    logging.info('create sell order.')
                    for _ in range(5):
                        sell_flag = sell(solana_client, token_address, payer, poolInfos)
                        if sell_flag:
                            break
                        else:
                            time.sleep(1)
            else:
                logging.info('switch buy is off')


def get_tokens_info(instruction):
    accounts = instruction.accounts
    pair = accounts[4]
    token0 = accounts[8]
    token1 = accounts[9]
    return token0, token1, pair, accounts


def print_table(tokens: Tuple[Pubkey, Pubkey, Pubkey]) -> None:
    data = [
        {'Token_Index': 'Token0', 'Account Public Key': tokens[0]},  # Token0
        {'Token_Index': 'Token1', 'Account Public Key': tokens[1]},  # Token1
        {'Token_Index': 'LP Pair', 'Account Public Key': tokens[2]}  # LP Pair
    ]
    print("============NEW POOL DETECTED====================")
    header = ["Token_Index", "Account Public Key"]
    print("│".join(f" {col.ljust(15)} " for col in header))
    print("|".rjust(18))
    for row in data:
        print("│".join(f" {str(row[col]).ljust(15)} " for col in header))


if __name__ == "__main__":
    # # config proxy
    # os.environ["http_proxy"] = "http://127.0.0.1:10809"
    # os.environ["https_proxy"] = "http://127.0.0.1:10809"

    config = configparser.ConfigParser()
    config.read('./config.ini')
    private_key_string = config['user']['private_key']
    is_buy = config['config']['is_buy']
    is_sell = config['config']['is_sell']
    pool_size = config['config']['pool_size']
    sol_amount = config['config']['sol_amount']
    wait_seconds = config['config']['wait_seconds']
    main_url = config['solanaConfig']['main_url']
    wss_url = config['solanaConfig']['wss_url']
    raydium_lp_v4 = config['solanaConfig']['raydium_lp_v4']
    log_instruction = config['solanaConfig']['log_instruction']

    solana_client = Client(main_url)
    raydium_lp_v4 = Pubkey.from_string(raydium_lp_v4)
    print(f"start solana sniper...")
    asyncio.run(main())
