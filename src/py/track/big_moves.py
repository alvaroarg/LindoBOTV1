
import asyncio
import websockets
import json
from datetime import datetime
import csv

# Define the trading pairs we are interested in
trading_pairs = ['btcusdt', 'ethusdt', 'solusdt', 'bnbusdt', 'coinusdt']

# Binance WebSocket base URL
binance_ws_url = "wss://stream.binance.com:9443/ws/"

tracking_limit = 500

csv_file = 'C:\\Users\\Alvaro\\Documents\\LindoBOTV1\\data\\trades.csv'

def initialize_csv():
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Pair", "Trade ID", "Price in USD", "Quantity", "Volume", "Buyer"])

async def handle_message(pair, message):
    data = json.loads(message)
    if data.get('e') == 'trade':
        timestamp = datetime.utcfromtimestamp(data['T'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
        trade_id = data['t']
        price = float(data['p'])
        quantity = float(data['q'])
        volume = quantity * price
        buyer = data['m']
        
        if volume > tracking_limit:
        
            # Write the trade data to the CSV file
            with open(csv_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, pair.upper(), trade_id, price, quantity, volume ,buyer])

                print(f"Pair: {pair.upper()} | Trade ID: {trade_id} | Price: {price} | Quantity: {quantity} | Volume:{volume} |Buyer: {data['m']}")


# Function to subscribe to a WebSocket stream
async def subscribe(pair):
    async with websockets.connect(binance_ws_url + pair + "@trade") as websocket:
        print(f"Subscribed to {pair.upper()} stream")
        async for message in websocket:
            await handle_message(pair, message)

# Main function to run the WebSocket client
async def main():
    initialize_csv()
    # Create tasks for each trading pair subscription
    tasks = [subscribe(pair) for pair in trading_pairs]
    await asyncio.gather(*tasks)

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
