#!/bin/bash

# Token Launcher Agent Demo
# Interactive demo showing AI-powered token launching

# ANSI Color codes
CYAN='\033[96m'
GREEN='\033[92m'
YELLOW='\033[93m'
RED='\033[91m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m' # No Color

clear

echo ""
echo -e "${CYAN}${BOLD}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}${BOLD}║              🚀 TOKEN LAUNCHER AI AGENT DEMO                       ║${NC}"
echo -e "${CYAN}${BOLD}║          Launch Solana Tokens with AI Assistance                  ║${NC}"
echo -e "${CYAN}${BOLD}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Change to project root
cd "$(dirname "$0")/.."

echo -e "${DIM}Checking environment...${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating one...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${YELLOW}📦 Installing dependencies...${NC}"
    pip install -q -r agents/requirements.txt
    echo -e "${GREEN}✅ Setup complete!${NC}"
    echo ""
else
    source venv/bin/activate
fi

# Check Python dependencies
echo -e "${DIM}Verifying dependencies...${NC}"
python3 -c "import solders, httpx, solana" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Missing dependencies. Installing...${NC}"
    pip install -q -r agents/requirements.txt
fi

echo -e "${GREEN}✅ Environment ready${NC}"
echo ""

# Show demo options
echo -e "${CYAN}────────────────────────────────────────────────────────────────────${NC}"
echo -e "${BOLD}  Choose Demo Mode:${NC}"
echo -e "${CYAN}────────────────────────────────────────────────────────────────────${NC}"
echo ""
echo -e "  ${GREEN}1.${NC} Interactive CLI Mode (Recommended)"
echo -e "     ${DIM}↳ Talk to the agent, launch tokens interactively${NC}"
echo ""
echo -e "  ${GREEN}2.${NC} Quick Demo Mode"
echo -e "     ${DIM}↳ Run automated demo with sample token${NC}"
echo ""
echo -e "  ${GREEN}3.${NC} Provider Agent Mode"
echo -e "     ${DIM}↳ Start as x402 marketplace provider${NC}"
echo ""

read -p "$(echo -e ${YELLOW}"Enter choice (1-3) [1]: "${NC})" choice
choice=${choice:-1}

echo ""

case $choice in
    1)
        echo -e "${GREEN}🚀 Starting Interactive CLI...${NC}"
        echo ""
        python3 agents/src/token_launcher_cli.py
        ;;
    2)
        echo -e "${GREEN}🚀 Running Quick Demo...${NC}"
        echo ""
        python3 agents/src/token_launcher_agent.py
        ;;
    3)
        echo -e "${GREEN}🚀 Starting Provider Agent...${NC}"
        echo ""
        echo -e "${CYAN}${BOLD}╔════════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${CYAN}${BOLD}║                    PROVIDER AGENT MODE                             ║${NC}"
        echo -e "${CYAN}${BOLD}╚════════════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo -e "${DIM}This mode registers the agent with x402 marketplace${NC}"
        echo -e "${DIM}Consumers can discover and pay for token launching services${NC}"
        echo ""
        echo -e "${YELLOW}Note: Make sure Registry and Facilitator are running:${NC}"
        echo -e "  ${CYAN}docker compose -f docker/docker-compose.yml up -d registry facilitator${NC}"
        echo ""
        read -p "$(echo -e ${YELLOW}"Continue? (Y/n): "${NC})" confirm
        confirm=${confirm:-Y}

        if [[ $confirm =~ ^[Yy] ]]; then
            python3 -c "
import asyncio
from agents.src.token_launcher_agent import TokenLauncherProviderAgent

async def main():
    provider = TokenLauncherProviderAgent(
        agent_id='token_launcher_provider_001',
        endpoint_url='http://localhost:6000'
    )
    await provider.start()

    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print('\n👋 Shutting down provider agent...')

asyncio.run(main())
"
        fi
        ;;
    *)
        echo -e "${RED}❌ Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${CYAN}────────────────────────────────────────────────────────────────────${NC}"
echo -e "${GREEN}✅ Demo complete!${NC}"
echo ""
echo -e "${DIM}Next steps:${NC}"
echo -e "  • Launch tokens on devnet: ${CYAN}./demos/demo_token_launcher.sh${NC}"
echo -e "  • Read the docs: ${CYAN}cat README.md${NC}"
echo -e "  • Integrate with your app: ${CYAN}Import TokenLauncherAgent${NC}"
echo ""
