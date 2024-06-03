import os
import asyncio
from solana.rpc.async_api import AsyncClient
from solana.publickey import PublicKey
from solana.rpc.types import MemcmpOpts, TransactionInstruction, AccountInfo, DataSliceOpts

# Solana RPC endpoint
SOLANA_CLUSTER_URL = "https://api.mainnet-beta.solana.com"

# Initialize the Solana client
client = AsyncClient(SOLANA_CLUSTER_URL)

# Function to get the latest slot
async def get_latest_slot():
    response = await client.get_slot()
    return response['result']

# Function to get confirmed signatures for a given slot
async def get_confirmed_signatures_for_slot(slot):
    response = await client.get_confirmed_signatures_for_address2(PublicKey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), before=slot)
    return response['result']

# Function to get transaction details for a given signature
async def get_transaction_details(signature):
    response = await client.get_transaction(signature)
    return response['result']

# Function to check if a transaction is a token mint
def is_token_mint(transaction):
    if not transaction or not transaction.get('meta'):
        return False
    inner_instructions = transaction['meta'].get('innerInstructions', [])
    for instruction_set in inner_instructions:
        for instruction in instruction_set['instructions']:
            program_id = instruction['programId']
            if program_id == 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA':
                # Check for the mint instruction type
                if instruction['data'][:2] == '02':
                    return True
    return False

# Function to poll for new token mints
async def poll_new_tokens(last_checked_slot):
    current_slot = await get_latest_slot()
    new_tokens = []

    while last_checked_slot < current_slot:
        signatures = await get_confirmed_signatures_for_slot(last_checked_slot)
        for signature in signatures:
            transaction = await get_transaction_details(signature['signature'])
            if is_token_mint(transaction):
                new_tokens.append(transaction)
        last_checked_slot += 1

    return new_tokens, current_slot

async def main():
    # Initialize the last checked slot
    last_checked_slot = await get_latest_slot()

    while True:
        new_tokens, last_checked_slot = await poll_new_tokens(last_checked_slot)
        if new_tokens:
            print(f"New tokens found: {new_tokens}")
        else:
            print("No new tokens found.")
        
        # Wait for a minute before polling again
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
