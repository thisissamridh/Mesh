# MESH - X402 Trustless Agent Framework

<div align="center">

**Autonomous AI agents with intelligent bidding and Solana-based micropayments**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Solana](https://img.shields.io/badge/Solana-Blockchain-9945FF?logo=solana)](https://solana.com/)

</div>

---

## Demo

### 🎥 Watch MESH in Action

[**▶️ View Demo Video**](https://drive.google.com/file/d/1E7Xf-7LC5ROqhas1rDl_-xHULWDcBeKc/view)

> Click above to watch a complete walkthrough of MESH's autonomous agent system, x402 payment protocol, and real-time Solana blockchain integration.

## Overview

MESH enables AI agents to autonomously discover, negotiate, and pay for services using the **x402 protocol** (HTTP 402 Payment Required) on the Solana blockchain. The system creates a trustless marketplace where agents can:

- 🤖 **Autonomously discover services** through an intelligent registry
- 💰 **Bid competitively** for data and services
- ⚡ **Execute micropayments** instantly on Solana
- 🔐 **Operate trustlessly** without intermediaries
- 🌐 **Integrate real blockchain data** from Jupiter and other providers

## Key Features

### 🎯 Intelligent Agent System
- **Portfolio Manager Agent** - Analyzes and manages token portfolios with AI-driven insights
- **Token Launcher Agent** - Create and deploy Solana tokens with guided assistance
- **Data Provider Agents** - Supply real-time blockchain data with competitive pricing
- **Interactive CLI** - Talk to agents naturally with real-time progress updates

### 💳 x402 Payment Protocol
- HTTP 402 (Payment Required) implementation for agent-to-agent transactions
- Facilitator service handles payment verification and coordination
- Seamless integration with Kora for Solana micropayments
- USDC-based payments on Solana devnet

### 📊 Real Data Providers (No Mocks!)
- **Jupiter Price Provider** - Live token prices from Jupiter Aggregator API
- **Jupiter Verification Provider** - Token verification, holder counts, liquidity stats
- **Real Solana Data** - Actual blockchain data, not simulated
- Extensible provider framework for custom data sources

### 🏪 Marketplace Registry
- RFP (Request for Proposal) system for service discovery
- Agent registration and capability advertisement
- Automated bid collection and evaluation
- Reputation tracking and service quality metrics

## Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  Agent Layer    │         │   Registry       │         │  Facilitator    │
│                 │         │                  │         │                 │
│ • Portfolio Mgr │◄───────►│ • RFP Manager   │◄───────►│ • x402 Handler  │
│ • Token Creator │  HTTP   │ • Agent Registry│  HTTP   │ • Kora Client   │
│ • Data Provider │         │ • Bid Collector │         │ • Payment Verify│
└─────────────────┘         └──────────────────┘         └─────────────────┘
        │                            │                            │
        │                            │                            │
        └────────────────────────────┴────────────────────────────┘
                                     │
                                     ▼
                           ┌──────────────────┐
                           │  Solana Blockchain│
                           │                  │
                           │ • USDC Payments  │
                           │ • Token Accounts │
                           │ • Kora Protocol  │
                           └──────────────────┘
```

## Project Structure

```
x402/
├── agents/                         # AI agent implementations
│   ├── src/
│   │   ├── portfolio_manager_agent.py    # Portfolio analysis agent
│   │   ├── token_launcher_agent.py       # Token creation agent
│   │   ├── jupiter_price_provider.py     # Real Jupiter price data
│   │   ├── jupiter_verification_provider.py # Token verification
│   │   ├── bidding_data_provider.py      # Competitive bidding agent
│   │   ├── agent_cli.py                  # Interactive CLI interface
│   │   ├── x402_client.py                # x402 protocol client
│   │   └── kora_provider.py              # Kora payment integration
│   └── requirements.txt
│
├── facilitator/                    # x402 payment handler
│   ├── src/
│   │   └── simple_facilitator.py         # Payment coordination
│   ├── kora.toml                         # Kora configuration
│   └── signers.toml                      # Signer configuration
│
├── registry/                       # Marketplace intelligence layer
│   ├── src/
│   │   ├── main.py                       # FastAPI server
│   │   ├── rfp_manager.py                # RFP/bidding logic
│   │   └── schemas.py                    # Data models
│   └── requirements.txt
│
├── shared/                         # Shared schemas and types
│
├── demos/                          # Demo scripts
│   ├── run_demo_local.sh                 # Local development demo
│   ├── run_demo_docker.sh                # Docker-based demo
│   ├── demo_token_launcher.sh            # Token creation demo
│   ├── demo_jupiter_real_data.sh         # Real Jupiter data demo
│   ├── demo_payment_flow.sh              # Payment flow demo
│   └── demo_x402_flow.sh                 # x402 protocol demo
│
├── docker/                         # Docker configuration
│   ├── docker-compose.yml                # Service orchestration
│   ├── Dockerfile                        # Main container
│   └── Dockerfile.kora-provider          # Kora provider container
│
└── scripts/                        # Utility scripts
    ├── setup_token_accounts.py           # Initialize token accounts
    └── start_kora.sh                     # Start Kora RPC server
```

## Quick Start

### Prerequisites

- **Python 3.8+**
- **Docker & Docker Compose** (for containerized setup)
- **Solana CLI tools** (for Kora integration)
- **Git**

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/thisissamridh/Mesh.git
cd Mesh
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Install dependencies**
```bash
# Install Python dependencies
pip install -r requirements.txt
pip install -r agents/requirements.txt
pip install -r registry/requirements.txt
```

### Running the System

#### Option 1: Interactive CLI (Recommended)
Talk to agents interactively with real-time progress updates:
```bash
python3 agents/src/agent_cli.py
```

Features:
- Natural language interaction with AI agents
- Real-time progress updates
- Portfolio analysis with live Jupiter data
- Token information lookup
- Guided workflows

#### Option 2: Run Demo Locally
```bash
./demos/run_demo_local.sh
```

Demonstrates:
- Agent registration
- RFP creation and bidding
- x402 payment flow
- Service consumption

#### Option 3: Run Demo with Docker
```bash
# Start all services
docker compose -f docker/docker-compose.yml up -d

# Run demo
./demos/run_demo_docker.sh

# View logs
docker compose -f docker/docker-compose.yml logs -f

# Stop services
docker compose -f docker/docker-compose.yml down
```

#### Option 4: Token Launcher Demo
Launch Solana tokens with AI assistance:
```bash
./demos/demo_token_launcher.sh
```

#### Option 5: Real Jupiter API Demo
Use real Solana blockchain data from Jupiter (no mocks!):
```bash
./demos/demo_jupiter_real_data.sh
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Solana Network
SOLANA_NETWORK=devnet
SOLANA_RPC_URL=https://api.devnet.solana.com

# Kora RPC
KORA_RPC_URL=http://localhost:8080
KORA_API_KEY=your_kora_api_key

# Keypairs (generate with: solana-keygen new)
KORA_SIGNER_ADDRESS=
KORA_SIGNER_PRIVATE_KEY=
PAYER_ADDRESS=
PAYER_PRIVATE_KEY=

# Agent Wallets
DATA_PROVIDER_ADDRESS=
DATA_PROVIDER_PRIVATE_KEY=
CONSUMER_ADDRESS=
CONSUMER_PRIVATE_KEY=

# Services
FACILITATOR_URL=http://localhost:3000
REGISTRY_URL=http://localhost:8000

# USDC Token (Devnet)
USDC_MINT_ADDRESS=4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU

# API Keys
JUPITER_API_URL=https://quote-api.jup.ag/v6
```

### Generating Solana Keypairs

```bash
# Install Solana CLI
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"

# Generate keypairs
solana-keygen new --outfile ~/.config/solana/payer.json
solana-keygen new --outfile ~/.config/solana/provider.json
solana-keygen new --outfile ~/.config/solana/consumer.json

# Get public keys
solana-keygen pubkey ~/.config/solana/payer.json
```

## Usage Examples

### Interactive Agent Conversation

```bash
$ python3 agents/src/agent_cli.py

🤖 Agent CLI Started
Type 'exit' to quit

You: Analyze SOL token for me

Agent: Let me fetch the latest data on SOL...
[Querying Jupiter Price Provider...]
[Payment: 0.01 USDC sent to provider]

SOL/USDC: $98.45
24h Change: +5.3%
Liquidity: $125M
Holder Count: 1.2M

Recommendation: Strong fundamentals, high liquidity
```

### Programmatic Agent Usage

```python
from agents.src.portfolio_manager_agent import PortfolioManagerAgent

# Initialize agent
agent = PortfolioManagerAgent(
    consumer_address="your_wallet_address",
    consumer_private_key="your_private_key"
)

# Analyze portfolio
result = await agent.analyze_portfolio(["SOL", "USDC", "BONK"])
print(result)
```

## Development

### Running Individual Services

**Registry (Port 8000)**
```bash
cd registry
python -m uvicorn src.main:app --reload --port 8000
```

**Facilitator (Port 3000)**
```bash
cd facilitator/src
python simple_facilitator.py
```

**Agents**
```bash
cd agents/src
python portfolio_manager_agent.py
```

### Testing

```bash
# Run all demos
./demos/run_demo_local.sh

# Test payment flow
./demos/demo_payment_flow.sh

# Test x402 protocol
./demos/demo_x402_flow.sh
```

## Technical Details

### x402 Protocol Flow

1. **Service Discovery**: Consumer queries registry for available providers
2. **RFP Creation**: Consumer creates request with requirements and budget
3. **Competitive Bidding**: Providers submit bids with price and capabilities
4. **Bid Selection**: Consumer selects best bid based on price/quality
5. **Payment Request**: Provider responds with HTTP 402 + payment details
6. **Payment Execution**: Consumer pays via Kora on Solana
7. **Service Delivery**: Provider verifies payment and delivers data

### Payment Flow

```
Consumer → Facilitator: Request data (HTTP 402)
Facilitator → Consumer: Payment required (amount, address)
Consumer → Solana: Transfer USDC
Consumer → Facilitator: Payment proof
Facilitator → Solana: Verify transaction
Facilitator → Consumer: Data delivery (HTTP 200)
```

## Dependencies

### Core Technologies
- **FastAPI** - Web framework for services
- **OpenAI** - AI agent intelligence
- **Solana** - Blockchain for payments
- **Kora** - Solana micropayment protocol
- **Jupiter** - Solana token aggregator

### Python Libraries
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `httpx` - HTTP client
- `openai` - OpenAI API
- `pydantic` - Data validation
- `python-dotenv` - Environment management
- `solders` - Solana Python SDK
- `base58` - Base58 encoding

## Roadmap

- [ ] Multi-chain support (Ethereum, Polygon)
- [ ] Advanced reputation system
- [ ] Service level agreements (SLAs)
- [ ] Privacy-preserving data exchange
- [ ] Machine learning model marketplace
- [ ] Cross-agent collaboration protocols
- [ ] Mobile agent interface
- [ ] Enhanced security audits

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- **Documentation**: [Coming soon]
- **Issues**: [GitHub Issues](https://github.com/thisissamridh/Mesh/issues)
- **Discord**: [Join our community]
- **Repository**: [GitHub](https://github.com/thisissamridh/Mesh)

## Acknowledgments

- Built on Solana blockchain
- Powered by Jupiter aggregator
- Integrated with Kora protocol
- Inspired by HTTP 402 Payment Required standard

---

<div align="center">
Made with ❤️ by the MESH team
</div>
