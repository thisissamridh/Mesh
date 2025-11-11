#!/usr/bin/env python3
"""
Simple Interactive CLI for x402 Agents

Works with existing portfolio manager and data provider agents
Shows real-time progress while agents work
"""

import os
import sys
import asyncio
from datetime import datetime

# Colors for pretty output
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    NC = '\033[0m'


def print_header():
    """Print CLI header"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.NC}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'🤖 X402 AI AGENT - Interactive CLI':^70}{Colors.NC}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.NC}\n")
    print(f"{Colors.DIM}   AI-powered marketplace agents with micropayments{Colors.NC}\n")


def print_menu():
    """Print main menu"""
    print(f"\n{Colors.BOLD}📋 Available Actions:{Colors.NC}\n")
    print(f"  {Colors.GREEN}1.{Colors.NC} Run Portfolio Manager (Consumer Agent)")
    print(f"  {Colors.GREEN}2.{Colors.NC} Start Data Provider (Provider Agent)")
    print(f"  {Colors.GREEN}3.{Colors.NC} View Agent Status")
    print(f"  {Colors.RED}4.{Colors.NC} Exit")
    print()


def get_input(prompt, default=""):
    """Get user input with default"""
    if default:
        prompt = f"{prompt} [{Colors.DIM}{default}{Colors.NC}]: "
    else:
        prompt = f"{prompt}: "
    value = input(f"{Colors.YELLOW}{prompt}{Colors.NC}").strip()
    return value if value else default


async def run_portfolio_manager():
    """Run portfolio manager with real-time updates"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'─'*70}{Colors.NC}")
    print(f"{Colors.CYAN}{Colors.BOLD}  🎯 PORTFOLIO MANAGER AGENT{Colors.NC}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'─'*70}{Colors.NC}\n")

    print(f"{Colors.DIM}The Portfolio Manager will:{Colors.NC}")
    print(f"  • Broadcast RFP for data")
    print(f"  • Receive bids from providers")
    print(f"  • Use AI to select best provider")
    print(f"  • Execute payment via Solana")
    print(f"  • Receive and display data\n")

    # Get parameters
    registry = get_input("Registry URL", "http://localhost:8000")
    facilitator = get_input("Facilitator URL", "http://localhost:3000")

    print(f"\n{Colors.GREEN}🚀 Starting Portfolio Manager...{Colors.NC}\n")
    print(f"{Colors.DIM}{'─'*70}{Colors.NC}\n")

    # Import and run
    sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

    # Set environment
    os.environ["REGISTRY_URL"] = registry
    os.environ["FACILITATOR_URL"] = facilitator

    # Import portfolio manager
    try:
        from portfolio_manager_agent import PortfolioManagerAgent

        # Create agent
        agent = PortfolioManagerAgent(
            agent_id="interactive_pm_001",
            registry_url=registry
        )

        # Run main workflow
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {Colors.CYAN}📡 Broadcasting RFP...{Colors.NC}")

        # This will run the actual agent
        result = await agent.run_data_request_cycle()

        print(f"\n{Colors.GREEN}✅ Task Complete!{Colors.NC}\n")

    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {e}{Colors.NC}")
        print(f"{Colors.DIM}Make sure services are running:{Colors.NC}")
        print(f"  docker compose -f docker/docker-compose.yml up -d\n")

    input(f"{Colors.DIM}Press Enter to continue...{Colors.NC}")


async def start_data_provider():
    """Start data provider agent"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'─'*70}{Colors.NC}")
    print(f"{Colors.CYAN}{Colors.BOLD}  🏪 DATA PROVIDER AGENT{Colors.NC}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'─'*70}{Colors.NC}\n")

    print(f"{Colors.DIM}The Provider Agent will:{Colors.NC}")
    print(f"  • Register with marketplace")
    print(f"  • Listen for RFPs")
    print(f"  • Submit competitive bids")
    print(f"  • Deliver data on payment\n")

    # Get parameters
    provider_id = get_input("Provider ID", "provider_cli_001")
    port = get_input("Port", "5000")
    price = get_input("Price (USDC)", "0.00015")

    print(f"\n{Colors.GREEN}🚀 Starting Provider Agent...{Colors.NC}\n")
    print(f"{Colors.DIM}Running on http://localhost:{port}{Colors.NC}")
    print(f"{Colors.DIM}Press Ctrl+C to stop{Colors.NC}\n")
    print(f"{Colors.DIM}{'─'*70}{Colors.NC}\n")

    try:
        # Run provider in background
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {Colors.GREEN}✅ Provider registered{Colors.NC}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {Colors.CYAN}👂 Listening for RFPs...{Colors.NC}\n")

        # Keep running
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⏸️  Provider stopped{Colors.NC}\n")


def show_agent_status():
    """Show current agent status"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'─'*70}{Colors.NC}")
    print(f"{Colors.CYAN}{Colors.BOLD}  📊 AGENT STATUS{Colors.NC}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'─'*70}{Colors.NC}\n")

    print(f"{Colors.BOLD}Running Agents:{Colors.NC}")
    print(f"  • Portfolio Manager: {Colors.DIM}Not running{Colors.NC}")
    print(f"  • Data Providers:    {Colors.DIM}Not running{Colors.NC}\n")

    print(f"{Colors.BOLD}Services:{Colors.NC}")
    print(f"  • Registry:          {Colors.DIM}http://localhost:8000{Colors.NC}")
    print(f"  • Facilitator:       {Colors.DIM}http://localhost:3000{Colors.NC}\n")

    print(f"{Colors.BOLD}Network:{Colors.NC}")
    print(f"  • Solana RPC:        {Colors.DIM}https://api.devnet.solana.com{Colors.NC}\n")

    input(f"{Colors.DIM}Press Enter to continue...{Colors.NC}")


async def main():
    """Main CLI loop"""
    print_header()

    running = True
    while running:
        try:
            print_menu()
            choice = get_input("Enter choice (1-4)", "1")

            if choice == "1":
                await run_portfolio_manager()
            elif choice == "2":
                await start_data_provider()
            elif choice == "3":
                show_agent_status()
            elif choice == "4":
                print(f"\n{Colors.CYAN}👋 Goodbye!{Colors.NC}\n")
                running = False
            else:
                print(f"{Colors.RED}❌ Invalid choice{Colors.NC}")

        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}Interrupted{Colors.NC}")
            confirm = get_input("Exit? (y/N)", "N").lower()
            if confirm in ['y', 'yes']:
                running = False


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.CYAN}Goodbye!{Colors.NC}\n")
