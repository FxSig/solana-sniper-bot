import os
import configparser

import base58
from spl.token.instructions import close_account, CloseAccountParams, get_associated_token_address, \
    create_associated_token_account
from solana.rpc.types import TokenAccountOpts
from solana.rpc.api import RPCException
from solana.transaction import Transaction
from solana.rpc.api import Client, Keypair, Pubkey

from utils.instruction_api import make_swap_instruction, fetch_local_pool_keys

from utils.init_logger import config_logger

logger = config_logger()


def sell(client, token_mint, payer=None, poolInfos=None):
    tokenPk = Pubkey.from_string(str(token_mint))
    sol = Pubkey.from_string("So11111111111111111111111111111111111111112")

    if not poolInfos:
        pool_keys = fetch_local_pool_keys(token_mint)
    else:
        pool_keys = poolInfos
    if pool_keys == "failed":
        return "failed"

    account_program_id = client.get_account_info_json_parsed(tokenPk)
    program_id_of_token = account_program_id.value.owner
    if not payer:
        logger.info('please config your payer info')
        return
    accounts = client.get_token_accounts_by_owner_json_parsed(payer.pubkey(), TokenAccountOpts(
        program_id=program_id_of_token)).value

    for account in accounts:
        mint_in_acc = account.account.data.parsed['info']['mint']
        if mint_in_acc == str(tokenPk):
            amount_in = int(account.account.data.parsed['info']['tokenAmount']['amount'])
            logger.info("Token Balance [Lamports]: ", amount_in)
            if not amount_in:
                logger.info('Insufficient balance')
                return False
            break
    account_data = client.get_token_accounts_by_owner(payer.pubkey(), TokenAccountOpts(tokenPk))
    if account_data.value:
        swap_token_account = account_data.value[0].pubkey
    else:
        logger.error('mint token not found')
        return "failed"

    if not swap_token_account:
        logger.error("swap_token_account not found...")
        return "failed"

    try:
        account_data = client.get_token_accounts_by_owner(payer.pubkey(), TokenAccountOpts(sol))
        wsol_token_account = account_data.value[0].pubkey
        wsol_token_account_Instructions = None
    except:
        wsol_token_account = get_associated_token_address(payer.pubkey(), sol)
        wsol_token_account_Instructions = create_associated_token_account(payer.pubkey(), payer.pubkey(), sol)

    instructions_swap = make_swap_instruction(amount_in, swap_token_account, wsol_token_account, pool_keys, tokenPk,
                                              client, payer)
    params = CloseAccountParams(account=wsol_token_account, dest=payer.pubkey(), owner=payer.pubkey(),
                                program_id=program_id_of_token)
    closeAcc = close_account(params)
    swap_tx = Transaction()
    signers = [payer]
    if wsol_token_account_Instructions != None:
        swap_tx.add(wsol_token_account_Instructions)
    swap_tx.add(instructions_swap)
    swap_tx.add(closeAcc)
    try:
        txn = client.send_transaction(swap_tx, *signers)
        txid_string_sig = txn.value
        logger.info(f'sell transaction info:, https://solscan.io/tx/{txid_string_sig}')
        return True
    except RPCException as e:
        logger.error(f"Error: [{e.args[0].message}]...\nRetrying...")
        return False


if __name__ == '__main__':
    os.environ["http_proxy"] = "http://127.0.0.1:10809"
    os.environ["https_proxy"] = "http://127.0.0.1:10809"
    url = "https://api.mainnet-beta.solana.com"

    client = Client(url)

    # read private key
    config = configparser.ConfigParser()
    config.read('../config.ini')
    private_key_string = config['user']['private_key']

    private_key_bytes = base58.b58decode(private_key_string)
    payer = Keypair.from_bytes(private_key_bytes)
    token_address = "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN"
    sell(client, token_address, payer)
