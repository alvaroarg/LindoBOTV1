import { Connection, clusterApiUrl, LAMPORTS_PER_SOL } from '@solana/web3.js';
import { createObjectCsvWriter } from 'csv-writer';
import HttpsProxyAgent from 'https-proxy-agent';
import fetch from 'node-fetch';

const proxies = [
  'http://localhost:3128',
  'http://localhost:3129',
  'http://localhost:3130'
];

let proxyIndex = 0;

function getNextProxy() {
  const proxy = proxies[proxyIndex];
  proxyIndex = (proxyIndex + 1) % proxies.length;
  return proxy;
}

const csvWriter = createObjectCsvWriter({
  path: 'pending_transactions.csv',
  header: [
    { id: 'signature', title: 'Signature' },      // Transaction identifier
    { id: 'slot', title: 'Slot' },                // Slot number
    { id: 'blockTime', title: 'BlockTime' },      // Block time (timestamp)
    { id: 'fee', title: 'Fee (SOL)' },            // Transaction fee in SOL
    { id: 'err', title: 'Error' },                // Error status
    { id: 'preBalances', title: 'PreBalances' },  // Balances before transaction
    { id: 'postBalances', title: 'PostBalances' },// Balances after transaction
    { id: 'tokenTransfers', title: 'TokenTransfers' } // Token transfer details
  ]
});

async function getConnection() {
  const proxy = getNextProxy();
  const agent = new HttpsProxyAgent.HttpsProxyAgent(proxy);
  return new Connection(
    clusterApiUrl('mainnet-beta'),
    {
      fetch: (url, options) => fetch(url, { ...options, agent })
    }
  );
}

async function getTransactionDetails(signature, retries = 5) {
  try {
    const connection = await getConnection();
    const confirmedTransaction = await connection.getParsedConfirmedTransaction(signature, 'confirmed');

    if (confirmedTransaction && confirmedTransaction.meta && confirmedTransaction.meta.status && !confirmedTransaction.meta.status.Err) {
      const transactionData = {
        signature: confirmedTransaction.transaction.signatures[0],
        slot: confirmedTransaction.slot,
        blockTime: confirmedTransaction.blockTime,
        fee: confirmedTransaction.meta.fee / LAMPORTS_PER_SOL, // Convert fee to SOL
        err: confirmedTransaction.meta.err,
        preBalances: confirmedTransaction.meta.preBalances.map(balance => balance / LAMPORTS_PER_SOL).join(', '), // Convert balances to SOL
        postBalances: confirmedTransaction.meta.postBalances.map(balance => balance / LAMPORTS_PER_SOL).join(', '), // Convert balances to SOL
        tokenTransfers: confirmedTransaction.meta.innerInstructions
          ? confirmedTransaction.meta.innerInstructions.map(ix => ix.instructions).flat().map(i => JSON.stringify(i)).join('; ')
          : ''
      };

      await csvWriter.writeRecords([transactionData]);
      console.log('Pending transaction detected and saved to CSV:', transactionData);
    }
  } catch (error) {
    if (error.message.includes('429') || error.message.includes('ECONNRESET')) {
      if (retries > 0) {
        const delay = (6 - retries) * 5000; // Exponential backoff
        console.error(`Error: ${error.message}. Retrying in ${delay / 1000} seconds...`);
        await new Promise(resolve => setTimeout(resolve, delay));
        await getTransactionDetails(signature, retries - 1); // Retry the call
      } else {
        console.error(`Failed to fetch transaction details after multiple attempts: ${error.message}`);
      }
    } else {
      console.error('Error fetching transaction details:', error);
    }
  }
}

async function listenForTransactions() {
  console.log('Listening for all transactions...');

  const connection = await getConnection();
  const subscriptionId = connection.onLogs(
    'all', // Listen to all transaction logs
    async (logInfo) => {
      const signature = logInfo.signature;
      await new Promise(resolve => setTimeout(resolve, 1000)); // Add a 1-second delay between calls
      await getTransactionDetails(signature);
    }
  );

  setTimeout(() => {
    connection.removeOnLogsListener(subscriptionId);
    console.log('Stopped listening for transactions.');
  }, 60000);
}

listenForTransactions().catch(err => {
  console.error('Error listening for transactions:', err);
});
