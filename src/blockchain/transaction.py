import asyncio
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.transaction import Transaction
from solana.rpc.types import TxOpts
from pyserum.async_connection import async_conn
from pyserum.market import Market
from pyserum.enums import OrderType, Side

async def get_best_price(market):
    bids = await market.load_bids()
    best_bid = next(bids)
    return best_bid.info.price

async def buy_token(buyer_secret_key, base_wallet, quote_wallet, market_address, size):
    # Configuración de conexión
    client = AsyncClient("https://api.mainnet-beta.solana.com")
    serum_connection = await async_conn("https://api.mainnet-beta.solana.com")

    buyer_account = Keypair.from_secret_key(bytes(buyer_secret_key))

    # Obtén el mercado
    market = await Market.load(serum_connection, market_address)

    # Obtén el mejor precio del token
    price = await get_best_price(market)

    # Detalles de la orden
    order_type = OrderType.IOC  # Immediate or Cancel to ensure quick execution
    side = Side.BUY             # Puedes usar BUY o SELL

    # Configura las opciones de transacción para establecer la prioridad
    tx_opts = TxOpts(skip_confirmation=True, preflight_commitment='confirmed')

    # Coloca una orden de compra
    transaction = Transaction()
    transaction.add(
        market.make_new_order_instruction(
            owner=buyer_account.pubkey(),
            payer=quote_wallet,
            side=side,
            order_type=order_type,
            limit_price=price,
            max_quantity=size,
            client_id=12345,  # Puedes usar un identificador de cliente personalizado
        )
    )

    # Envía la transacción con las opciones configuradas
    response = await client.send_transaction(transaction, buyer_account, opts=tx_opts)
    print(f"Order placed. Transaction signature: {response['result']}")

    await client.close()

# Parámetros de entrada
buyer_secret_key = []
base_wallet = Pubkey.from_string("BaseTokenWalletPublicKey")
quote_wallet = Pubkey.from_string("QuoteTokenWalletPublicKey")
market_address = Pubkey.from_string("DESKZaNchWHE7n3UKGxP2Wvn2J4XB3p8g63H8VXojOQi")
size = 0.1  # Tamaño de la orden

# Ejecuta la compra de token de forma asincrónica
asyncio.run(buy_token(buyer_secret_key, base_wallet, quote_wallet, market_address, size))

