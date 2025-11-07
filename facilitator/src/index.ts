import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { KoraClient } from '@kora-labs/kora-sdk';
import { Connection } from '@solana/web3.js';

dotenv.config({ path: '../.env' });

const app = express();
const PORT = process.env.FACILITATOR_PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Initialize Kora client
const koraClient = new KoraClient({
  url: process.env.KORA_RPC_URL || 'http://localhost:8080',
  apiKey: process.env.KORA_API_KEY || '',
});

// Initialize Solana connection
const connection = new Connection(
  process.env.SOLANA_RPC_URL || 'https://api.devnet.solana.com',
  'confirmed'
);

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'x402-facilitator' });
});

// Supported endpoint - advertises facilitator capabilities
app.get('/supported', async (req, res) => {
  try {
    const payerSigner = await koraClient.getPayerSigner();

    res.json({
      x402Version: '1.0.0',
      scheme: 'exact',
      network: 'solana-devnet',
      feePayer: payerSigner.publicKey.toString(),
      supportedTokens: [
        process.env.USDC_MINT_ADDRESS || '4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU'
      ],
    });
  } catch (error) {
    console.error('Error in /supported:', error);
    res.status(500).json({ error: 'Failed to get facilitator info' });
  }
});

// Verify endpoint - validates payment without broadcasting
app.post('/verify', async (req, res) => {
  try {
    const { payment } = req.body;

    if (!payment) {
      return res.status(400).json({ error: 'Missing payment data' });
    }

    // Extract transaction from x402 payment payload
    const transactionBuffer = Buffer.from(payment.transaction, 'base64');

    // Verify transaction with Kora (signs but doesn't broadcast)
    const verification = await koraClient.signTransaction(transactionBuffer);

    res.json({
      isValid: verification.success,
      message: verification.success ? 'Payment verified' : 'Invalid payment',
    });
  } catch (error) {
    console.error('Error in /verify:', error);
    res.status(500).json({ error: 'Verification failed', isValid: false });
  }
});

// Settle endpoint - broadcasts verified payment to Solana
app.post('/settle', async (req, res) => {
  try {
    const { payment } = req.body;

    if (!payment) {
      return res.status(400).json({ error: 'Missing payment data' });
    }

    // Extract transaction from x402 payment payload
    const transactionBuffer = Buffer.from(payment.transaction, 'base64');

    // Sign and send transaction via Kora
    const result = await koraClient.signAndSendTransaction(transactionBuffer);

    if (!result.success) {
      return res.status(400).json({
        error: 'Settlement failed',
        details: result.error
      });
    }

    res.json({
      success: true,
      transactionSignature: result.signature,
      network: 'solana-devnet',
      message: 'Payment settled on-chain',
    });
  } catch (error) {
    console.error('Error in /settle:', error);
    res.status(500).json({ error: 'Settlement failed' });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  console.log(`  x402 Facilitator running on port ${PORT}`);
  console.log(`  Kora RPC: ${process.env.KORA_RPC_URL}`);
  console.log(`  Network: ${process.env.SOLANA_NETWORK}`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
});
