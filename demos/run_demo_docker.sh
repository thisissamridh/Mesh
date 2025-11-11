#!/bin/bash

# ANSI Color codes
CYAN='\033[96m'
GREEN='\033[92m'
YELLOW='\033[93m'
RED='\033[91m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m' # No Color

# Clear screen for clean demo
clear

echo ""
echo -e "${CYAN}${BOLD}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}${BOLD}║                  x402 AI MARKETPLACE DEMO                          ║${NC}"
echo -e "${CYAN}${BOLD}║          Autonomous Agents • AI Bidding • Solana Payments          ║${NC}"
echo -e "${CYAN}${BOLD}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if services are running
echo -e "${DIM}Checking services...${NC}"
if ! docker ps | grep -q "x402_registry"; then
    echo ""
    echo -e "${RED}${BOLD}❌ Error: Services not running!${NC}"
    echo ""
    echo "Start services first with:"
    echo -e "  ${CYAN}docker compose -f docker/docker-compose.yml up -d${NC}"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ All services detected and running${NC}"
echo ""
echo -e "${YELLOW}⏳ Waiting for services to be fully ready...${NC}"
sleep 5

echo ""
echo -e "${CYAN}────────────────────────────────────────────────────────────────────${NC}"
echo -e "${BOLD}  🤖 Starting Portfolio Manager Agent${NC}"
echo -e "${CYAN}────────────────────────────────────────────────────────────────────${NC}"
echo ""
echo -e "${DIM}The Portfolio Manager will:${NC}"
echo -e "  ${GREEN}1.${NC} Broadcast RFP for SOL/USDC price data"
echo -e "  ${GREEN}2.${NC} Receive bids from competing providers"
echo -e "  ${GREEN}3.${NC} Use AI (GPT-4) to evaluate and choose best provider"
echo -e "  ${GREEN}4.${NC} Execute x402 payment on Solana"
echo -e "  ${GREEN}5.${NC} Receive data and rate provider performance"
echo ""
echo -e "${CYAN}────────────────────────────────────────────────────────────────────${NC}"
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
