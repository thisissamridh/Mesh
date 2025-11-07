#!/usr/bin/env node

/**
 * Setup script to generate Solana keypairs for the x402 demo
 */

import { Keypair } from '@solana/web3.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function generateKeypair(name) {
  const keypair = Keypair.generate();
  const publicKey = keypair.publicKey.toBase58();
  const secretKey = Buffer.from(keypair.secretKey).toString('base64');

  return {
    name,
    publicKey,
    secretKey,
    secretKeyArray: `[${Array.from(keypair.secretKey).join(',')}]`,
  };
}

function main() {
  console.log('\n='.repeat(60));
  console.log('  Solana Keypair Generator for x402 Demo');
  console.log('='.repeat(60));

  // Generate keypairs
  console.log('\n🔑 Generating keypairs...\n');

  const keypairs = {
    koraSigner: generateKeypair('Kora Signer'),
    payer: generateKeypair('Payer'),
    dataProvider: generateKeypair('Data Provider'),
    consumer: generateKeypair('Consumer'),
  };

  // Display generated keypairs
  console.log('Generated Keypairs:\n');
  for (const [key, kp] of Object.entries(keypairs)) {
    console.log(`${kp.name}:`);
    console.log(`  Address: ${kp.publicKey}`);
    console.log('');
  }

  // Create/update .env file
  const envPath = path.join(__dirname, '..', '.env');
  let envContent = '';

  if (fs.existsSync(envPath)) {
    console.log('📝 Updating existing .env file...\n');
    envContent = fs.readFileSync(envPath, 'utf8');
  } else {
    console.log('📝 Creating new .env file...\n');
    // Copy from .env.example
    const examplePath = path.join(__dirname, '..', '.env.example');
    if (fs.existsSync(examplePath)) {
      envContent = fs.readFileSync(examplePath, 'utf8');
    }
  }

  // Update keypair values
  envContent = updateEnvVar(envContent, 'KORA_SIGNER_ADDRESS', keypairs.koraSigner.publicKey);
  envContent = updateEnvVar(envContent, 'KORA_SIGNER_PRIVATE_KEY', keypairs.koraSigner.secretKeyArray);

  envContent = updateEnvVar(envContent, 'PAYER_ADDRESS', keypairs.payer.publicKey);
  envContent = updateEnvVar(envContent, 'PAYER_PRIVATE_KEY', keypairs.payer.secretKeyArray);

  envContent = updateEnvVar(envContent, 'DATA_PROVIDER_ADDRESS', keypairs.dataProvider.publicKey);
  envContent = updateEnvVar(envContent, 'DATA_PROVIDER_PRIVATE_KEY', keypairs.dataProvider.secretKey);

  envContent = updateEnvVar(envContent, 'CONSUMER_ADDRESS', keypairs.consumer.publicKey);
  envContent = updateEnvVar(envContent, 'CONSUMER_PRIVATE_KEY', keypairs.consumer.secretKey);

  // Write to .env
  fs.writeFileSync(envPath, envContent);

  console.log('✅ Keypairs saved to .env\n');
  console.log('='.repeat(60));
  console.log('  Next Steps');
  console.log('='.repeat(60));
  console.log('\n1. Fund accounts with SOL (devnet):');
  console.log(`   solana airdrop 1 ${keypairs.koraSigner.publicKey} --url devnet`);
  console.log(`   solana airdrop 1 ${keypairs.consumer.publicKey} --url devnet`);

  console.log('\n2. Get USDC (devnet) for consumer:');
  console.log('   Visit: https://faucet.circle.com/');
  console.log(`   Address: ${keypairs.consumer.publicKey}`);

  console.log('\n3. Install dependencies:');
  console.log('   pnpm install:all');

  console.log('\n4. Start services (in separate terminals):');
  console.log('   Terminal 1: pnpm run start:registry');
  console.log('   Terminal 2: pnpm run start:kora');
  console.log('   Terminal 3: pnpm run start:facilitator');
  console.log('   Terminal 4: python agents/src/data_provider_agent.py');

  console.log('\n5. Run demo:');
  console.log('   pnpm run demo\n');
}

function updateEnvVar(content, key, value) {
  const regex = new RegExp(`^${key}=.*$`, 'm');
  const newLine = `${key}=${value}`;

  if (regex.test(content)) {
    return content.replace(regex, newLine);
  } else {
    return content + `\n${newLine}`;
  }
}

main();
