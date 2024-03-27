import time

from spl.token.core import _TokenCore
from spl.token.instructions import close_account, CloseAccountParams, get_associated_token_address, \
    create_associated_token_account
from solana.rpc.types import TokenAccountOpts
from solana.rpc.api import RPCException
from solana.transaction import Transaction
from solana.rpc.api import Pubkey
from spl.token.client import Token
from solana.rpc.commitment import Commitment

from utils.check_token_accounts_by_owner import check_token_accounts_by_owner
from utils.instruction_api import make_swap_instruction, fetch_local_pool_keys, get_token_account

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
        return False

    account_program_id = client.get_account_info_json_parsed(tokenPk)
    program_id_of_token = account_program_id.value.owner
    if not payer:
        logger.info('please config your payer info')
        return
    accounts = client.get_token_accounts_by_owner_json_parsed(payer.pubkey(), TokenAccountOpts(
        program_id=program_id_of_token)).value
    amount_in = 0
    for account in accounts:
        mint_in_acc = account.account.data.parsed['info']['mint']
        if mint_in_acc == str(tokenPk):
            amount_in = int(account.account.data.parsed['info']['tokenAmount']['amount'])
            logger.info("Token Balance [Lamports]: ", amount_in)
            break

    account_data = client.get_token_accounts_by_owner(payer.pubkey(), TokenAccountOpts(tokenPk))
    if account_data.value:
        swap_token_account = account_data.value[0].pubkey
    else:
        logger.error('mint token not found')
        return False

    if not swap_token_account:
        logger.error("swap_token_account not found...")
        return False

    try:
        account_data = client.get_token_accounts_by_owner(payer.pubkey(), TokenAccountOpts(sol))
        wsol_token_account = account_data.value[0].pubkey
        wsol_token_account_Instructions = None
    except:
        wsol_token_account = get_associated_token_address(payer.pubkey(), sol)
        wsol_token_account_Instructions = create_associated_token_account(payer.pubkey(), payer.pubkey(), sol)

    instructions_swap = make_swap_instruction(amount_in, swap_token_account, wsol_token_account, poolInfos, tokenPk,
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
        logger.info(f'sell transaction info: https://solscan.io/tx/{txid_string_sig}')
        return True
    except RPCException as e:
        logger.error(f"Error: [{e.args[0].message}]...\nRetrying...")
        return False


def buy(solana_client, token_mint, payer, amount, poolInfos=None):
    amount_in = int(amount * 1000000000)
    mint = Pubkey.from_string(token_mint)

    if not poolInfos:
        pool_keys = fetch_local_pool_keys(token_mint)
    else:
        pool_keys = poolInfos
    if pool_keys == "failed":
        logger.error("pool keys not found .")
        return False
    accountProgramId = solana_client.get_account_info_json_parsed(mint)
    TOKEN_PROGRAM_ID = accountProgramId.value.owner
    check_token_accounts_by_owner()
    swap_associated_token_address, swap_token_account_Instructions = get_token_account(solana_client, payer.pubkey(),
                                                                                       mint)

    balance_needed = Token.get_min_balance_rent_for_exempt_for_account(solana_client)
    new_pair_pk, swap_tx, payer, new_pair, opts, = _TokenCore._create_wrapped_native_account_args(
        TOKEN_PROGRAM_ID, payer.pubkey(), payer, amount_in,
        False, balance_needed, Commitment("confirmed"))

    instructions_swap = make_swap_instruction(amount_in,
                                              new_pair_pk,
                                              swap_associated_token_address,
                                              pool_keys,
                                              mint,
                                              solana_client,
                                              payer
                                              )
    params = CloseAccountParams(account=new_pair_pk, dest=payer.pubkey(), owner=payer.pubkey(),
                                program_id=TOKEN_PROGRAM_ID)
    closeAcc = (close_account(params))
    if swap_token_account_Instructions != None:
        swap_tx.add(swap_token_account_Instructions)
    swap_tx.add(instructions_swap)
    swap_tx.add(closeAcc)

    try:
        txn = solana_client.send_transaction(swap_tx, payer, new_pair)
        txid_string_sig = txn.value
        logger.info(f'buy transaction info:, https://solscan.io/tx/{txid_string_sig}')
        return True
    except:
        logger.error('buy transaction error!!')
        return False
