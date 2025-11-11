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
echo -e "${CYAN}${BOLD}║                         MESH AGENTS                                ║${NC}"
echo -e "${CYAN}${BOLD}║          Autonomous Agents • AI Bidding • Solana Payments          ║${NC}"
echo -e "${CYAN}${BOLD}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if services are running
echo -e "${DIM}Checking services...${NC}"
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo ""
    echo -e "${RED}${BOLD}❌ Error: Services not running!${NC}"
    echo ""
    echo "Start services first with:"
    echo -e "  ${CYAN}docker compose -f docker/docker-compose.yml up -d registry facilitator provider_001 provider_002${NC}"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ All services detected and running${NC}"
echo ""

echo -e "${CYAN}────────────────────────────────────────────────────────────────────${NC}"
echo -e "${BOLD}  🤖 Starting Portfolio Manager Agent${NC}"
echo -e "${CYAN}────────────────────────────────────────────────────────────────────${NC}"
echo ""
echo -e "${DIM}The Portfolio Manager will:${NC}"
echo -e "  ${GREEN}1.${NC} Broadcast RFP for SOL/USDC price data"
echo -e "  ${GREEN}2.${NC} Receive bids from competing providers (streaming)"
echo -e "  ${GREEN}3.${NC} Use AI (GPT-4) to evaluate and choose best provider"
echo -e "  ${GREEN}4.${NC} Execute x402 payment on Solana"
echo -e "  ${GREEN}5.${NC} Receive data and rate provider performance"
echo ""
echo -e "${CYAN}────────────────────────────────────────────────────────────────────${NC}"
echo ""

# Setup virtual environment if it doesn't exist
cd "$(dirname "$0")/.."

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Setting up Python virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip3 install -q -r agents/requirements.txt
    echo -e "${GREEN}✅ Setup complete!${NC}"
    echo ""
else
    source venv/bin/activate
fi

# Run Portfolio Manager locally
export REGISTRY_URL=http://localhost:8000
export FACILITATOR_URL=http://localhost:3000

python3 agents/src/portfolio_manager_agent.py

echo ""
