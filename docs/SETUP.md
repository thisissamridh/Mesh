# Setup Guide - x402 Agent-to-Agent Settlement Layer

Complete guide to set up and run the agent-to-agent settlement demo.

## Prerequisites

Before starting, ensure you have:

- **Node.js** (v20 or later) + **pnpm** package manager
- **Python** 3.11 or later + **pip**
- **Rust** (latest stable) - for Kora
- **Solana CLI** - for airdrops and account management

### Installing Prerequisites

**macOS:**
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install node pnpm python@3.11 rust
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
```

**Linux:**
```bash
# Install Node.js & pnpm
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
npm install -g pnpm

# Install Python
sudo apt-get install python3.11 python3-pip

# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install Solana CLI
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
```

## Installation Steps

### 1. Clone and Setup Project

```bash
cd /Users/samridh/Documents/cadboost/x402

# Generate Solana keypairs
pnpm run setup

# This will:
# - Generate 4 keypairs (Kora signer, payer, data provider, consumer)
# - Create/update .env file with addresses and private keys
```

### 2. Install Dependencies

**TypeScript (Facilitator):**
```bash
cd facilitator
pnpm install
cd ..
```

**Python (Agents & Registry):**
```bash
# Registry
cd registry
pip install -r requirements.txt
cd ..

# Agents
cd agents
pip install -r requirements.txt
cd ..
```

### 3. Build Kora

```bash
# Clone Kora repository
git clone https://github.com/solana-foundation/kora.git ~/kora
cd ~/kora

# Checkout release branch
git checkout release/feature-freeze-for-audit

# Build and install
make install

# Verify installation
kora --version
```

### 4. Fund Accounts

The setup generates 4 accounts that need funding:

**Get Devnet SOL:**
```bash
# Fund Kora signer (pays transaction fees)
solana airdrop 1 <KORA_SIGNER_ADDRESS> --url devnet

# Fund consumer (makes payments)
solana airdrop 1 <CONSUMER_ADDRESS> --url devnet
```

Replace `<KORA_SIGNER_ADDRESS>` and `<CONSUMER_ADDRESS>` with values from your `.env` file.

**Get Devnet USDC:**
1. Visit [Circle USDC Faucet](https://faucet.circle.com/)
2. Select "Solana Devnet"
3. Enter your `CONSUMER_ADDRESS` (from `.env`)
4. Request USDC (get at least 0.01 USDC for testing)

### 5. Verify Configuration

Check your `.env` file contains:
```bash
# Solana
SOLANA_NETWORK=devnet
SOLANA_RPC_URL=https://api.devnet.solana.com

# Keypairs (auto-generated)
KORA_SIGNER_ADDRESS=<generated>
KORA_SIGNER_PRIVATE_KEY=<generated>
CONSUMER_ADDRESS=<generated>
CONSUMER_PRIVATE_KEY=<generated>
DATA_PROVIDER_ADDRESS=<generated>
DATA_PROVIDER_PRIVATE_KEY=<generated>

# Service URLs
REGISTRY_URL=http://localhost:8000
FACILITATOR_URL=http://localhost:3000

# USDC Token
USDC_MINT_ADDRESS=4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU
```

## Running the Demo

You need **4 terminal windows** to run all services:

### Terminal 1: Registry API

```bash
cd /Users/samridh/Documents/cadboost/x402
pnpm run start:registry
```

Expected output:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2: Kora RPC

```bash
cd /Users/samridh/Documents/cadboost/x402
pnpm run start:kora
```

Expected output:
```
INFO kora_lib::rpc_server::server: RPC server started on 0.0.0.0:8080
```

### Terminal 3: x402 Facilitator

```bash
cd /Users/samridh/Documents/cadboost/x402
pnpm run start:facilitator
```

Expected output:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  x402 Facilitator running on port 3000
  Kora RPC: http://localhost:8080
  Network: devnet
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Terminal 4: DataProvider Agent

```bash
cd /Users/samridh/Documents/cadboost/x402
python agents/src/data_provider_agent.py
```

Expected output:
```
==================================================
  DataProviderAgent Starting
==================================================
  Agent ID: data_provider_001
  Wallet: <DATA_PROVIDER_ADDRESS>
  Port: 5000
  Price: 0.0001 USDC per request
==================================================

✅ Agent data_provider_001 registered successfully
INFO:     Uvicorn running on http://0.0.0.0:5000
```

### Terminal 5: Run Demo

```bash
cd /Users/samridh/Documents/cadboost/x402
pnpm run demo
```

## Expected Demo Output

```
==================================================================
  x402 Agent-to-Agent Settlement Demo
==================================================================

📋 Pre-flight Checklist:
   ✓ Environment variables loaded
   ⏳ Checking services...

Required Services:
   1. Registry API:     http://localhost:8000
   2. Facilitator:      http://localhost:3000
   3. Kora RPC:         http://localhost:8080
   4. DataProvider:     http://localhost:5000

==================================================================
  Starting Agent Discovery & Payment Flow
==================================================================

1️⃣ Discovering data providers...
✅ Found: SOL Price Provider
   Agent ID: data_provider_001
   Endpoint: http://localhost:5000
   Price: 0.0001 USDC

2️⃣ Requesting price data from SOL Price Provider...

💳 Calling data_provider_001 at http://localhost:5000/price/sol-usdc
   Using x402 payment...
✅ Payment successful!
   Transaction: 5ULZpdeThaMAy6hcEGfAoMFqJqPpCtxdCxb6JYUV6nA4...

📊 Price Data Received:
   {'symbol': 'SOL/USDC', 'price': 142.35, 'timestamp': '2025-11-07T...', 'source': 'mock_oracle'}

==================================================================
  ✅ Demo Completed Successfully!
==================================================================
```

## Troubleshooting

### Issue: "Connection refused" errors

**Solution:** Make sure all 4 services are running in separate terminals.

### Issue: "Insufficient funds" error

**Solution:**
```bash
# Check balance
solana balance <CONSUMER_ADDRESS> --url devnet

# If low, airdrop more SOL
solana airdrop 1 <CONSUMER_ADDRESS> --url devnet
```

### Issue: Kora won't start

**Solution:**
```bash
# Make sure you're on the correct branch
cd ~/kora
git checkout release/feature-freeze-for-audit

# Rebuild
make clean
make install
```

### Issue: Python import errors

**Solution:**
```bash
# Make sure you're in the correct directory
cd agents
pip install -r requirements.txt --upgrade
```

## Next Steps

After successfully running the demo:

1. **Explore the code** - Check out the agent implementations
2. **Customize pricing** - Modify the `price_usdc` in DataProviderAgent
3. **Add more agents** - Create new agent types (executor, simulator, etc.)
4. **Deploy to mainnet** - Change `SOLANA_NETWORK=mainnet-beta` (use real USDC)

## Resources

- [Solana Documentation](https://docs.solana.com/)
- [x402 Protocol](https://x402.org/)
- [Kora GitHub](https://github.com/solana-foundation/kora)
- [Pydantic AI](https://ai.pydantic.dev/)
