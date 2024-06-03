
import asyncio
import websockets
import json
from datetime import datetime

# Define the trading pairs we are interested in
trading_pairs = ['btcusdt', 'ethusdt', 'solusdt', 'bnbusdt', 'coinusdt']

# Binance WebSocket base URL
binance_ws_url = "wss://stream.binance.com:9443/ws/"

# Function to handle incoming WebSocket messages
async def handle_message(pair, message):
    data = json.loads(message)
    if data.get('e') == 'trade':
        timestamp = datetime.utcfromtimestamp(data['T'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
        trade_id = data['t']
        price = data['p']
        quantity = data['q']
        buyer = data['m']
        print(f"Pair: {pair.upper()} | Trade ID: {data['t']} | Price: {data['p']} | Quantity: {data['q']} | Buyer: {data['m']}")

# Function to subscribe to a WebSocket stream
async def subscribe(pair):
    async with websockets.connect(binance_ws_url + pair + "@trade") as websocket:
        print(f"Subscribed to {pair.upper()} stream")
        async for message in websocket:
            await handle_message(pair, message)

# Main function to run the WebSocket client
async def main():
    # Create tasks for each trading pair subscription
    tasks = [subscribe(pair) for pair in trading_pairs]
    await asyncio.gather(*tasks)

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
