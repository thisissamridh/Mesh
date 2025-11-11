"""
Portfolio Manager Agent - Consumer agent that uses AI to make decisions
Demonstrates how any agent can use ConsumerMixin for marketplace interactions
"""

import os
import base58
from openai import OpenAI
from solders.keypair import Keypair
from dotenv import load_dotenv

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from consumer_mixin import ConsumerMixin, Colors, print_box, print_section
from x402_client import X402Client
from shared.schemas.negotiation import TaskType

# Load .env from project root
dotenv_path = os.path.join(os.path.dirname(__file__), "../../.env")
load_dotenv(dotenv_path=dotenv_path)


class PortfolioManagerAgent(ConsumerMixin):
    """
    Portfolio Manager that needs data/services from marketplace

    Uses AI to:
    - Evaluate provider bids
    - Decide who to pay
    - Rate providers after delivery
    """

    def __init__(
        self,
        agent_id: str,
        registry_url: str = "http://localhost:8000",
        openai_api_key: str = None,
        model: str = "gpt-4o-2024-08-06",
    ):
        self.agent_id = agent_id
        self.registry_url = registry_url

        # Initialize OpenAI
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", model)
        openai_client = OpenAI(api_key=api_key)

        # Initialize x402 client for payments
        private_key = os.getenv("PORTFOLIO_MANAGER_PRIVATE_KEY")
        if private_key:
            payer_keypair = Keypair.from_bytes(base58.b58decode(private_key))
            x402_client = X402Client(
                payer_keypair=payer_keypair,
                facilitator_url=os.getenv("FACILITATOR_URL", "http://localhost:3000"),
                network="solana-devnet",
            )
            self.has_wallet = True
            wallet_address = str(payer_keypair.pubkey())
            print(f"\n{Colors.GREEN}💳 x402 Payment Enabled{Colors.ENDC}")
            print(f"{Colors.DIM}   Wallet: {wallet_address}{Colors.ENDC}")
        else:
            x402_client = None
            self.has_wallet = False
            print(f"\n{Colors.YELLOW}⚠️  x402 disabled (no wallet key){Colors.ENDC}")

        # Setup consumer capabilities
        self.setup_consumer(
            openai_client=openai_client,
            x402_client=x402_client,
            registry_url=registry_url,
            agent_id=agent_id,
            model=self.model,
        )

        print_box("🤖 PORTFOLIO MANAGER INITIALIZED", Colors.CYAN, 70)
        print(f"{Colors.BOLD}Agent ID:{Colors.ENDC}      {Colors.CYAN}{self.agent_id}{Colors.ENDC}")
        print(f"{Colors.BOLD}Registry:{Colors.ENDC}      {Colors.DIM}{self.registry_url}{Colors.ENDC}")
        print(f"{Colors.BOLD}AI Model:{Colors.ENDC}      {Colors.HEADER}{self.model}{Colors.ENDC}")
        print(f"{Colors.BOLD}Consumer:{Colors.ENDC}      {Colors.GREEN}✅ Enabled{Colors.ENDC}\n")

    def get_portfolio_price_data(self, symbol: str = "SOL/USDC"):
        """
        Request price data from marketplace
        AI will evaluate bids and select best provider
        """

        result = self.request_service_from_marketplace(
            task_type=TaskType.PRICE_DATA.value,
            task_description=f"Get real-time {symbol} price data",
            max_budget_usdc=0.001,
            wait_for_bids_seconds=10,
        )

        return result

    def analyze_portfolio_performance(self):
        """
        Request analytics service from marketplace
        AI will evaluate analytics providers
        """

        result = self.request_service_from_marketplace(
            task_type=TaskType.ANALYTICS.value,
            task_description="Analyze portfolio performance and provide recommendations",
            max_budget_usdc=0.005,
            wait_for_bids_seconds=10,
        )

        return result


if __name__ == "__main__":
    # Demo: Portfolio Manager requests services

    portfolio_agent = PortfolioManagerAgent(
        agent_id="portfolio_manager_001",
        registry_url=os.getenv("REGISTRY_URL", "http://localhost:8000"),
    )

    print_box("🎯 DEMO: Requesting SOL/USDC Price Data", Colors.HEADER, 70)

    # Request price data - AI will evaluate bids and choose provider
    result = portfolio_agent.get_portfolio_price_data()

    if result["success"]:
        print_box("🎉 DEMO COMPLETED SUCCESSFULLY", Colors.GREEN, 70)
        print(f"{Colors.BOLD}Provider:{Colors.ENDC}     {Colors.CYAN}{result['assignment']['provider_id']}{Colors.ENDC}")
        print(f"{Colors.BOLD}Price Paid:{Colors.ENDC}   {Colors.GREEN}{result['assignment']['agreed_price_usdc']} USDC{Colors.ENDC}")
        print(f"{Colors.BOLD}Total Bids:{Colors.ENDC}   {Colors.YELLOW}{result['total_bids']}{Colors.ENDC}")
        print(f"{Colors.BOLD}Tx Hash:{Colors.ENDC}      {Colors.GREEN}{result.get('payment_tx', 'N/A')}{Colors.ENDC}")

        # Show received data
        data = result.get('data', {})
        if data:
            print(f"\n{Colors.BOLD}📊 Received Data:{Colors.ENDC}")
            if 'data' in data:
                inner_data = data['data']
                print(f"   {Colors.CYAN}Symbol:{Colors.ENDC} {inner_data.get('symbol', 'N/A')}")
                print(f"   {Colors.GREEN}{Colors.BOLD}Price:{Colors.ENDC} ${inner_data.get('price', 0)}")
                print(f"   {Colors.DIM}Source: {inner_data.get('source', 'N/A')}{Colors.ENDC}")
        print()
    else:
        print_box("❌ DEMO FAILED", Colors.RED, 70)
        print(f"{Colors.RED}Error: {result.get('error', 'Unknown error')}{Colors.ENDC}\n")