# MESH - X402 Trustless Agent Framework

**Autonomous agents with AI bidding and Solana-based micropayments**

MESH enables AI agents to autonomously discover, negotiate, and pay for services using the x402 protocol (HTTP 402 Payment Required) on Solana blockchain.

## Project Structure

```
x402/
├── agents/              # AI agent implementations
│   └── src/            # Agent source code (portfolio manager, data providers)
├── facilitator/        # x402 payment handler with Kora integration
│   └── src/           # Facilitator source code
├── registry/           # Marketplace intelligence layer
│   └── src/           # Registry source code
├── shared/            # Shared schemas and types
├── demos/             # Demo scripts
│   ├── run_demo_local.sh       # Run demo with local services
│   ├── run_demo_docker.sh      # Run demo with Docker
│   ├── run_demo_kora.py        # Kora integration demo
│   ├── demo_payment_flow.sh    # Payment flow demonstration
│   └── demo_x402_flow.sh       # x402 protocol demonstration
├── docker/            # Docker configuration
│   ├── docker-compose.yml      # Service orchestration
│   ├── Dockerfile              # Main Dockerfile
│   └── Dockerfile.kora-provider # Kora provider Dockerfile
└── scripts/           # Utility scripts
    ├── setup_token_accounts.py # Token account setup
    └── start_kora.sh           # Start Kora RPC server

```

## Quick Start

### Option 1: Interactive CLI (Recommended)
Talk to agents interactively with real-time progress updates:
```bash
python3 agents/src/agent_cli.py
```

### Option 2: Run Demo Locally
```bash
./demos/run_demo_local.sh
```

### Option 3: Run Demo with Docker
```bash
# Start services
docker compose -f docker/docker-compose.yml up -d

# Run demo
./demos/run_demo_docker.sh
```

### Option 4: Token Launcher Demo (NEW!)
Launch Solana tokens with AI assistance:
```bash
./demos/demo_token_launcher.sh
```

## Configuration

- `.env` - Environment configuration
- `.env.example` - Example environment variables

## Requirements

- Python 3.8+
- Docker & Docker Compose
- Solana CLI tools (for Kora integration)
