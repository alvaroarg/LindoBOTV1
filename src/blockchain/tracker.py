import pandas as pd
from solana.rpc.api import Client
from solders.pubkey import Pubkey
from datetime import datetime
import time
import requests

# Configurar conexión al nodo RPC de Solana
solana_client = Client("https://api.mainnet-beta.solana.com")

# Dirección de la wallet que queremos rastrear
wallet_address = Pubkey("arsc4jbDnzaqcCLByyGo7fg7S2SmcFsWUzQuDtLZh2y")

# Función para obtener el precio de SOL en dólares (utilizando CoinGecko)
def get_sol_price():
    response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd")
    return response.json()["solana"]["usd"]

# Función para obtener información del token como market cap (utilizando CoinGecko)
def get_token_info(token_address):
    # Aquí deberías implementar la lógica para obtener la información del token
    # Este es un placeholder que debes reemplazar con una llamada a una API real
    return {"market_cap": 1000000}  # Placeholder

# Función para rastrear las transacciones
def track_transactions():
    transactions = []
    seen_signatures = set()
    while True:
        try:
            response = solana_client.get_confirmed_signature_for_address2(wallet_address, limit=10)
            for txn in response['result']:
                if txn['signature'] not in seen_signatures:
                    seen_signatures.add(txn['signature'])
                    txn_details = solana_client.get_confirmed_transaction(txn['signature'])
                    if txn_details['result'] and 'meta' in txn_details['result']:
                        meta = txn_details['result']['meta']
                        if 'innerInstructions' in meta and meta['innerInstructions']:
                            for instruction in meta['innerInstructions']:
                                for instruction_detail in instruction['instructions']:
                                    if instruction_detail['programId'] == "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA":
                                        price_sol = 0
                                        market_cap = get_token_info(instruction_detail['programId'])['market_cap']
                                        timestamp = txn_details['result']['blockTime']
                                        timestamp = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                                        transaction_data = {
                                            "token_address": instruction_detail['programId'],
                                            "price_usd": price_sol,
                                            "market_cap_usd": market_cap,
                                            "timestamp": timestamp
                                        }
                                        transactions.append(transaction_data)
                                        # Guardar en CSV
                                        df = pd.DataFrame(transactions)
                                        df.to_csv('transactions.csv', index=False)
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(10)

# Ejecutar el rastreador de transacciones
track_transactions()
