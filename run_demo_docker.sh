#!/bin/bash

echo "============================================================"
echo "  x402 AI Marketplace Demo"
echo "============================================================"
echo ""

# Check if services are running
if ! docker ps | grep -q "x402_registry"; then
    echo "❌ Error: Services not running!"
    echo ""
    echo "Start services first with:"
    echo "  docker-compose up -d"
    echo ""
    exit 1
fi

echo "✅ Services detected"
echo ""
echo "Waiting for services to be fully ready..."
sleep 5

echo ""
echo "============================================================"
echo "  Starting Portfolio Manager (Consumer with AI)"
echo "============================================================"
echo ""
echo "Portfolio Manager will:"
echo "  1. Broadcast RFP for SOL/USDC price data"
echo "  2. Receive bids from 2 competing providers"
echo "  3. Use AI to evaluate and choose best provider"
echo "  4. Execute x402 payment on Solana"
echo "  5. Receive data and rate provider"
echo ""
echo "============================================================"
echo ""

# Run Portfolio Manager (connects to dockerized services)
docker run --rm \
    --network x402_x402_network \
    --env-file .env \
    -e REGISTRY_URL=http://registry:8000 \
    -e FACILITATOR_URL=http://facilitator:3000 \
    x402:latest \
    python3 agents/src/portfolio_manager_agent.py

echo ""
echo "============================================================"
echo "  Demo Complete!"
echo "============================================================"
