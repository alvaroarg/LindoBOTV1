import { Connection, clusterApiUrl } from '@solana/web3.js';
import WebSocket from 'ws';
import { createObjectCsvWriter as createCsvWriter } from 'csv-writer';

const connection = new Connection(
  clusterApiUrl('mainnet-beta'), // Use Solana's mainnet-beta endpoint
  'confirmed'
);

const csvWriter = createCsvWriter({
  path: 'pending_transactions.csv',
  header: [
    { id: 'timestamp', title: 'Timestamp' },      // Insertion timestamp
    { id: 'signature', title: 'Signature' },      // Transaction identifier
    { id: 'slot', title: 'Slot' },                // Slot number
    { id: 'fee', title: 'Transaction Fee' },      // Transaction fee
    { id: 'slippage', title: 'Slippage' }         // Slippage
  ]
});

async function fetchTransactionDetailsWithRetry(signature, retries = 3, delay = 2000) {
  for (let i = 0; i < retries; i++) {
    try {
      const transactionDetails = await connection.getTransaction(signature, { commitment: 'confirmed' });
      return transactionDetails;
    } catch (error) {
      if (i === retries - 1) {
        throw error;
      }
      console.error(`Error fetching transaction details. Retry ${i + 1} of ${retries}. Error: ${error}`);
      await new Promise(res => setTimeout(res, delay));
    }
  }
}

async function subscribeToTransactions() {
  const ws = new WebSocket('wss://api.mainnet-beta.solana.com'); // Public Solana WebSocket endpoint

  ws.on('open', function open() {
    console.log('WebSocket connection opened');
    ws.send(JSON.stringify({
      "jsonrpc": "2.0",
      "id": 1,
      "method": "logsSubscribe",
      "params": [
        { "mentions": ["11111111111111111111111111111111"] }, // Native Solana program ID
        { "commitment": "processed" }
      ]
    }));
    console.log('Sent logsSubscribe request');
  });

  ws.on('message', async function incoming(data) {
    const message = data.toString();
    console.log('WebSocket message received:', message);

    const response = JSON.parse(message);
    console.log('Parsed response:', response);

    if (response.method === 'logsNotification') {
      const result = response.params.result.value;
      const signature = result.signature || 'No signature';
      const slot = response.params.result.context.slot || 'No slot';
      const timestamp = new Date().toISOString(); // UTC timestamp

      try {
        // Fetch the transaction fee from the Solana API with retries
        const transactionDetails = await fetchTransactionDetailsWithRetry(signature);
        const fee = transactionDetails?.meta?.fee || 'No fee available';

        // Calculate slippage based on your logic
        const slippage = calculateSlippage(result);  // Replace with actual calculation logic

        console.log('Received logsNotification with signature:', signature);

        const transactionData = {
          timestamp,
          signature,
          slot,
          fee,
          slippage
        };

        console.log('Pending transaction data:', transactionData); // Log the transaction data

        await csvWriter.writeRecords([transactionData]);
        console.log('Pending transaction detected and saved to CSV:', transactionData);
      } catch (error) {
        console.error('Failed to fetch transaction details after retries:', error);
      }
    }
  });

  ws.on('error', (error) => {
    console.error('WebSocket error:', error);
  });

  ws.on('close', () => {
    console.log('WebSocket connection closed');
  });
}

function calculateSlippage(result) {
  // Implement your logic to calculate slippage based on the result
  return 0; // Placeholder value
}

subscribeToTransactions().catch(err => {
  console.error('Error subscribing to transactions:', err);
});
