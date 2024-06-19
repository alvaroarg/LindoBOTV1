import base58
from solana.rpc.api import Client
from solders.pubkey import Pubkey
import csv
import time

solana_client = Client("https://bold-solemn-pond.solana-devnet.quiknode.pro/d053298b3e7e632c65395864392b56c5d6ed0195/")
while True:
    slot = solana_client.get_slot()
    val = slot.value
    print(val)
    blk = solana_client.get_block(val, "jsonParsed", max_supported_transaction_version=0)
    signatures = list()
    for tx in blk.value.transactions:
        tx_signature = tx.transaction.signatures
        signatures.append(tx_signature[0])
    for i in range (len(signatures)):
        tx_status = solana_client.get_signature_statuses(signatures)
        print(f"Transaction Signature: {signatures[i]}")
         # Get the transaction status
        
        confirmation_status = tx_status.value[i].confirmation_status
        print(f"Confirmation Status: {confirmation_status}")
        print("-" * 40)
    time.sleep(1)

print('Datos volcados en solana_transactions.csv')
