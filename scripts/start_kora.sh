#!/bin/bash

# Start Kora RPC Server for x402 Gasless Payments

echo "============================================================"
echo "  Starting Kora RPC Server"
echo "============================================================"
echo ""

# Change to facilitator directory
cd "$(dirname "$0")/../facilitator"

# Export environment variable from .env
export KORA_SIGNER_PRIVATE_KEY="4y26XrBAYQNfVPm3BhiMesESGNxqK8VWaug1AinSAqG7Y6jezKQ75GcpRM7b49Gha7DN25JAbiuFtmG5reTqbDjp"

echo "Configuration:"
echo "  - Config: kora.toml"
echo "  - Signers: signers.toml"
echo "  - Port: 8080"
echo ""
echo "Starting server..."
echo ""

# Start Kora RPC
kora --config kora.toml rpc start --signers-config signers.toml
