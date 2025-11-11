#!/usr/bin/env python3
"""
Interactive CLI for Token Launcher Agent

This CLI allows users to interactively launch and manage tokens
while the agent provides real-time progress updates.
"""

import asyncio
import sys
import os
from typing import Optional
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from agents.src.token_launcher_agent import TokenLauncherAgent, TokenLauncherProviderAgent


class Colors:
    """ANSI color codes for pretty CLI output"""
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    NC = '\033[0m'  # No Color


class TokenLauncherCLI:
    """Interactive CLI for Token Launcher Agent"""

    def __init__(self):
        self.agent: Optional[TokenLauncherAgent] = None
        self.running = True

    def print_header(self):
        """Print CLI header"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.NC}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'🚀 TOKEN LAUNCHER AI AGENT - Interactive CLI':^70}{Colors.NC}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.NC}\n")
        print(f"{Colors.DIM}   Launch and manage Solana tokens with AI assistance{Colors.NC}")
        print(f"{Colors.DIM}   Real-time progress updates • Automatic liquidity • Smart defaults{Colors.NC}\n")

    def print_menu(self):
        """Print main menu"""
        print(f"\n{Colors.BOLD}📋 What would you like to do?{Colors.NC}\n")
        print(f"  {Colors.GREEN}1.{Colors.NC} Launch a new token")
        print(f"  {Colors.GREEN}2.{Colors.NC} Get token information")
        print(f"  {Colors.GREEN}3.{Colors.NC} Monitor token health")
        print(f"  {Colors.GREEN}4.{Colors.NC} Show agent status")
        print(f"  {Colors.GREEN}5.{Colors.NC} View pricing")
        print(f"  {Colors.RED}6.{Colors.NC} Exit")
        print()

    def get_input(self, prompt: str, default: str = "") -> str:
        """Get user input with optional default"""
        if default:
            prompt = f"{prompt} [{Colors.DIM}{default}{Colors.NC}]: "
        else:
            prompt = f"{prompt}: "

        value = input(f"{Colors.YELLOW}{prompt}{Colors.NC}").strip()
        return value if value else default

    def get_yes_no(self, prompt: str, default: bool = False) -> bool:
        """Get yes/no input from user"""
        default_str = "Y/n" if default else "y/N"
        response = self.get_input(f"{prompt} ({default_str})", "").lower()

        if not response:
            return default

        return response in ['y', 'yes', 'true', '1']

    async def launch_token_interactive(self):
        """Interactive token launch wizard"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'─'*70}{Colors.NC}")
        print(f"{Colors.CYAN}{Colors.BOLD}  🚀 TOKEN LAUNCH WIZARD{Colors.NC}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'─'*70}{Colors.NC}\n")

        print(f"{Colors.DIM}Let's set up your token. I'll ask a few questions.{Colors.NC}\n")

        # Get token details
        name = self.get_input("Token Name (e.g., 'My Awesome Token')", "DemoToken")
        symbol = self.get_input("Token Symbol (e.g., 'MAT')", "DEMO")

        # Supply
        while True:
            supply_str = self.get_input("Initial Supply", "1000000")
            try:
                supply = int(supply_str.replace(",", ""))
                break
            except ValueError:
                print(f"{Colors.RED}❌ Please enter a valid number{Colors.NC}")

        # Decimals
        decimals_str = self.get_input("Decimals (9 is standard)", "9")
        decimals = int(decimals_str) if decimals_str.isdigit() else 9

        # Optional fields
        description = self.get_input("Description (optional)", "")
        image_url = self.get_input("Image URL (optional)", "")

        # Liquidity
        add_liquidity = self.get_yes_no("\nAdd liquidity to Raydium DEX?", False)
        initial_liquidity_sol = 0.0

        if add_liquidity:
            while True:
                liq_str = self.get_input("  SOL amount for initial liquidity", "5.0")
                try:
                    initial_liquidity_sol = float(liq_str)
                    break
                except ValueError:
                    print(f"{Colors.RED}  ❌ Please enter a valid number{Colors.NC}")

        # Confirm
        print(f"\n{Colors.BOLD}📋 Review Your Token:{Colors.NC}\n")
        print(f"  Name:        {Colors.CYAN}{name}{Colors.NC}")
        print(f"  Symbol:      {Colors.CYAN}{symbol}{Colors.NC}")
        print(f"  Supply:      {Colors.CYAN}{supply:,}{Colors.NC}")
        print(f"  Decimals:    {Colors.CYAN}{decimals}{Colors.NC}")
        if description:
            print(f"  Description: {Colors.DIM}{description[:50]}{Colors.NC}")
        if add_liquidity:
            print(f"  Liquidity:   {Colors.GREEN}{initial_liquidity_sol} SOL{Colors.NC}")

        print()
        if not self.get_yes_no("Proceed with launch?", True):
            print(f"{Colors.YELLOW}❌ Launch cancelled{Colors.NC}")
            return

        # Launch!
        print(f"\n{Colors.GREEN}{Colors.BOLD}🚀 Launching your token...{Colors.NC}\n")
        print(f"{Colors.DIM}{'─'*70}{Colors.NC}\n")

        result = await self.agent.launch_token(
            name=name,
            symbol=symbol,
            decimals=decimals,
            supply=supply,
            description=description,
            image_url=image_url,
            add_liquidity=add_liquidity,
            initial_liquidity_sol=initial_liquidity_sol
        )

        # Show results
        print(f"\n{Colors.DIM}{'─'*70}{Colors.NC}\n")

        if result["status"] == "success":
            print(f"{Colors.GREEN}{Colors.BOLD}✅ Token Launch Successful!{Colors.NC}\n")
            print(f"  {Colors.BOLD}Mint Address:{Colors.NC}  {Colors.CYAN}{result['mint_address']}{Colors.NC}")

            if result.get("pool_address"):
                print(f"  {Colors.BOLD}Pool Address:{Colors.NC}  {Colors.CYAN}{result['pool_address']}{Colors.NC}")

            print(f"\n  {Colors.BOLD}View on Explorer:{Colors.NC}")
            print(f"  {Colors.BLUE}https://explorer.solana.com/address/{result['mint_address']}?cluster=devnet{Colors.NC}")

            print(f"\n  {Colors.BOLD}Steps Completed:{Colors.NC}")
            for step in result["steps_completed"]:
                print(f"    • {step}")
        else:
            print(f"{Colors.RED}{Colors.BOLD}❌ Token Launch Failed{Colors.NC}\n")
            for error in result.get("errors", []):
                print(f"  {Colors.RED}Error: {error}{Colors.NC}")

        input(f"\n{Colors.DIM}Press Enter to continue...{Colors.NC}")

    async def get_token_info_interactive(self):
        """Get token information interactively"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'─'*70}{Colors.NC}")
        print(f"{Colors.CYAN}{Colors.BOLD}  🔍 TOKEN INFORMATION{Colors.NC}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'─'*70}{Colors.NC}\n")

        mint_address = self.get_input("Enter token mint address")

        if not mint_address:
            print(f"{Colors.RED}❌ Mint address required{Colors.NC}")
            return

        print()
        info = await self.agent.get_token_info(mint_address)

        if "error" in info:
            print(f"{Colors.RED}❌ Error: {info['error']}{Colors.NC}")
        else:
            print(f"{Colors.GREEN}✅ Token Found{Colors.NC}\n")
            print(f"  Mint:     {info['mint']}")
            print(f"  Supply:   {info['supply']:,}")
            print(f"  Decimals: {info['decimals']}")
            print(f"  Status:   {info['status']}")

        input(f"\n{Colors.DIM}Press Enter to continue...{Colors.NC}")

    async def monitor_token_interactive(self):
        """Monitor token health interactively"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'─'*70}{Colors.NC}")
        print(f"{Colors.CYAN}{Colors.BOLD}  👀 TOKEN MONITORING{Colors.NC}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'─'*70}{Colors.NC}\n")

        mint_address = self.get_input("Enter token mint address")

        if not mint_address:
            print(f"{Colors.RED}❌ Mint address required{Colors.NC}")
            return

        duration_str = self.get_input("Monitoring duration (minutes)", "5")
        duration = int(duration_str) if duration_str.isdigit() else 5

        print(f"\n{Colors.DIM}Starting monitoring... Press Ctrl+C to stop early{Colors.NC}\n")

        try:
            await self.agent.monitor_token(mint_address, duration)
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⏸️  Monitoring stopped by user{Colors.NC}")

        input(f"\n{Colors.DIM}Press Enter to continue...{Colors.NC}")

    def show_agent_status(self):
        """Show agent status"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'─'*70}{Colors.NC}")
        print(f"{Colors.CYAN}{Colors.BOLD}  🤖 AGENT STATUS{Colors.NC}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'─'*70}{Colors.NC}\n")

        print(f"  Agent ID:      {self.agent.agent_id}")
        print(f"  Wallet:        {self.agent.wallet.pubkey()}")
        print(f"  Network:       {self.agent.rpc_url}")
        print(f"  Status:        {Colors.GREEN}Online{Colors.NC}")

        input(f"\n{Colors.DIM}Press Enter to continue...{Colors.NC}")

    def show_pricing(self):
        """Show service pricing"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'─'*70}{Colors.NC}")
        print(f"{Colors.CYAN}{Colors.BOLD}  💰 SERVICE PRICING{Colors.NC}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'─'*70}{Colors.NC}\n")

        pricing = {
            "Token Deployment": "0.01 USDC",
            "Add Liquidity to DEX": "0.005 USDC",
            "Metadata Update": "0.002 USDC",
            "24h Monitoring": "0.1 USDC",
            "Full Launch Package": "0.05 USDC (Save 30%)"
        }

        for service, price in pricing.items():
            print(f"  {service:.<40} {Colors.GREEN}{price}{Colors.NC}")

        print(f"\n  {Colors.DIM}All prices in USDC. Paid via x402 micropayments.{Colors.NC}")

        input(f"\n{Colors.DIM}Press Enter to continue...{Colors.NC}")

    async def run(self):
        """Run the interactive CLI"""
        self.print_header()

        # Initialize agent
        print(f"{Colors.DIM}Initializing AI agent...{Colors.NC}\n")
        self.agent = TokenLauncherAgent(agent_id="interactive_launcher_001")

        print(f"{Colors.GREEN}✅ Agent ready!{Colors.NC}")

        # Main loop
        while self.running:
            try:
                self.print_menu()
                choice = self.get_input("Enter your choice (1-6)", "1")

                if choice == "1":
                    await self.launch_token_interactive()
                elif choice == "2":
                    await self.get_token_info_interactive()
                elif choice == "3":
                    await self.monitor_token_interactive()
                elif choice == "4":
                    self.show_agent_status()
                elif choice == "5":
                    self.show_pricing()
                elif choice == "6":
                    print(f"\n{Colors.CYAN}👋 Thanks for using Token Launcher AI!{Colors.NC}\n")
                    self.running = False
                else:
                    print(f"{Colors.RED}❌ Invalid choice. Please try again.{Colors.NC}")

            except KeyboardInterrupt:
                print(f"\n\n{Colors.YELLOW}⏸️  Operation interrupted{Colors.NC}")
                if not self.get_yes_no("\nExit?", True):
                    continue
                else:
                    self.running = False

        # Cleanup
        if self.agent:
            await self.agent.close()


async def main():
    """Main entry point"""
    cli = TokenLauncherCLI()
    await cli.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Goodbye!{Colors.NC}\n")
        sys.exit(0)
