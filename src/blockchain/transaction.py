import os
import base64
import asyncio
from solana.rpc.api import Client
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction, TransactionInstruction
from solana.system_program import TransferParams, transfer
from solana.account import Account
from solana.publickey import PublicKey
from solana.rpc.types import TxOpts
from spl.token.client import Token
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import transfer_checked, TransferCheckedParams

# Load your wallet's private key from an environment variable
PRIVATE_KEY = os.getenv("SOLANA_PRIVATE_KEY")

# Decode the private key
private_key = base64.b64decode(PRIVATE_KEY)

# Create an account object
account = Account(private_key)

# Define the Solana cluster endpoint (mainnet, testnet, or devnet)
SOLANA_CLUSTER_URL = "https://api.mainnet-beta.solana.com"
client = AsyncClient(SOLANA_CLUSTER_URL)

# Token details
TOKEN_MINT_ADDRESS = "YourTokenMintAddressHere"
RECIPIENT_ADDRESS = "RecipientPublicKeyHere"

# Define slippage tolerance (e.g., 0.5% = 0.005)
slippage_tolerance = 0.005

# Define the amount of tokens to buy (adjusted for token decimals)
amount_to_buy = 1000000  # Example: 1 token with 6 decimals

# Create the token client
token = Token(client, PublicKey(TOKEN_MINT_ADDRESS), TOKEN_PROGRAM_ID, account)

async def buy_token():
    # Get the recipient public key
    recipient_public_key = PublicKey(RECIPIENT_ADDRESS)

    # Create associated token account if it doesn't exist
    recipient_token_account = await token.get_or_create_associated_account_info(recipient_public_key)
    
    # Get the current price (for demonstration, assume price fetching logic is implemented)
    current_price = await get_current_token_price()
    max_price = current_price * (1 + slippage_tolerance)
    
    # Construct the transaction
    transaction = Transaction()
    
    # Add the transfer instruction with slippage and priority settings
    transaction.add(
        transfer_checked(
            TransferCheckedParams(
                program_id=TOKEN_PROGRAM_ID,
                source=account.public_key(),
                mint=PublicKey(TOKEN_MINT_ADDRESS),
                dest=recipient_token_account.address,
                owner=account.public_key(),
                amount=amount_to_buy,
                decimals=6,  # Adjust this based on the token decimals
                signers=[]
            )
        )
    )

    # Send the transaction with custom options
    tx_opts = TxOpts(skip_confirmation=False, preflight_commitment="confirmed", skip_preflight=False)
    response = await client.send_transaction(transaction, account, opts=tx_opts)

    print(f"Transaction response: {response}")

async def get_current_token_price():
    # Implement logic to fetch the current price of the token
    # For demonstration purposes, returning a dummy price
    return 1.0

# Main function to run the async tasks
async def main():
    await buy_token()
    await client.close()

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
