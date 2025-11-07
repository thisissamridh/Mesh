# Agent-to-Agent Settlement Layer on Solana

> The missing link for autonomous agent commerce on Solana x402

An open-source SDK enabling autonomous AI agents to discover, negotiate, and pay each other directly using the x402 micropayment protocol on Solana.

## Overview

This project introduces a **trustless settlement layer** that allows AI agents to:
- **Register** services with pricing and capabilities
- **Discover** other agents through a decentralized registry
- **Negotiate** and agree on payment terms
- **Settle** micropayments instantly on Solana via x402
- **Execute** tasks autonomously without intermediaries

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Python Agents  │────▶│  Agent Registry  │────▶│ x402 Facilitator│
│  (Pydantic AI)  │     │   (FastAPI)      │     │  (TypeScript)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │                          │
                               ▼                          ▼
                        ┌──────────────┐          ┌─────────────┐
                        │   Database   │          │  Kora RPC   │
                        │   (Registry) │          │  + Solana   │
                        └──────────────┘          └─────────────┘
```

## Components

### 1. x402 Facilitator (TypeScript)
Payment verification and settlement service using Kora for gasless Solana transactions.

### 2. Agent Registry (FastAPI)
Decentralized marketplace where agents register services and discover other agents.

### 3. Python Agents (Pydantic AI)
Autonomous agents that offer or consume services:
- **DataProviderAgent**: Offers real-time price data
- **ConsumerAgent**: Discovers and pays for data

### 4. Shared Schemas
Common types and protocols for agent-to-agent communication.

## Quick Start

### Prerequisites
- Node.js (LTS) + pnpm
- Python 3.11+
- Rust (latest stable)
- Solana CLI

### Installation

```bash
# Clone and navigate
cd x402

# Install facilitator dependencies
cd facilitator && pnpm install && cd ..

# Install Python dependencies
cd agents && pip install -r requirements.txt && cd ..
cd registry && pip install -r requirements.txt && cd ..

# Configure environment
cp .env.example .env
# Edit .env with your Solana keypairs
```

### Running the Demo

```bash
# Terminal 1: Start Kora RPC
pnpm run start:kora

# Terminal 2: Start Facilitator
pnpm run start:facilitator

# Terminal 3: Start Registry
pnpm run start:registry

# Terminal 4: Run Demo
pnpm run demo
```

## Example Flow

1. **DataProviderAgent** registers: "I provide SOL/USDC prices for 0.0001 USDC per call"
2. **ConsumerAgent** queries registry: "Who provides price data?"
3. Registry returns DataProvider details + pricing
4. ConsumerAgent creates x402 payment transaction
5. Payment settles on Solana via facilitator
6. DataProvider returns price data with receipt

## Tech Stack

- **Blockchain**: Solana (devnet/mainnet)
- **Payment Protocol**: x402 + Kora
- **Agent Framework**: Pydantic AI
- **Backend**: FastAPI (Python), Express (TypeScript)
- **Database**: Supabase / PostgreSQL

## Hackathon Tracks

This project targets:
- **Best Trustless Agent** ($10k)
- **Best x402 API Integration** ($10k)

## License

MIT License - Open source for the agent economy

## Documentation

See `/docs` folder for:
- Setup guide
- API reference
- Architecture details
- Example use cases

---

Built for the Solana x402 Hackathon 2025
