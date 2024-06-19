import base58
from solana.rpc.api import Client
from solders.pubkey import Pubkey
import csv

solana_client = Client("https://bold-solemn-pond.solana-devnet.quiknode.pro/d053298b3e7e632c65395864392b56c5d6ed0195/")

encoded_pubkey = "Vote111111111111111111111111111111111111111"
decoded_pubkey = base58.b58decode(encoded_pubkey)

print(len(decoded_pubkey)) #32 bytes

address = Pubkey(decoded_pubkey)

response = solana_client.get_signatures_for_address(address, limit=1000)

# Crear y escribir en el archivo CSV
csv_file = "solana_transactions.csv"

# Encabezados para el archivo CSV
fields = ['Signature', 'BlockTime', 'ConfirmationStatus', 'Error', 'Memo', 'Slot']

with open(csv_file, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()

    for transaction in response.value:
        # Extraer información relevante
        signature = transaction.signature
        block_time = transaction.block_time
        confirmation_status = transaction.confirmation_status
        error = transaction.err
        memo = transaction.memo
        slot = transaction.slot
        
        # Escribir la fila en el archivo CSV
        writer.writerow({
            'Signature': signature,
            'BlockTime': block_time,
            'ConfirmationStatus': confirmation_status,
            'Error': error,
            'Memo': memo,
            'Slot': slot
        })

print('Datos volcados en solana_transactions.csv')
