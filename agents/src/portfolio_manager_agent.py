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

from consumer_mixin import ConsumerMixin
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
        private_key = os.getenv("ORCHESTRATOR_PRIVATE_KEY")  # Reuse orchestrator wallet
        if private_key:
            payer_keypair = Keypair.from_bytes(base58.b58decode(private_key))
            x402_client = X402Client(
                payer_keypair=payer_keypair,
                facilitator_url=os.getenv("FACILITATOR_URL", "http://localhost:3000"),
                network="solana-devnet",
            )
            self.has_wallet = True
            print(f"   💳 x402 Payment Enabled: {payer_keypair.pubkey()}")
        else:
            x402_client = None
            self.has_wallet = False
            print(f"   ⚠️  x402 disabled (no wallet key)")

        # Setup consumer capabilities
        self.setup_consumer(
            openai_client=openai_client,
            x402_client=x402_client,
            registry_url=registry_url,
            agent_id=agent_id,
            model=self.model,
        )

        print(f"\n{'='*60}")
        print(f"  Portfolio Manager Agent Initialized")
        print(f"{'='*60}")
        print(f"  Agent ID: {self.agent_id}")
        print(f"  Registry: {self.registry_url}")
        print(f"  AI Model: {self.model}")
        print(f"  Consumer Capabilities: ✅")
        print(f"{'='*60}\n")

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
    )

    print("\n" + "="*60)
    print("  DEMO: Portfolio Manager Requesting Price Data")
    print("="*60 + "\n")

    # Request price data - AI will evaluate bids and choose provider
    result = portfolio_agent.get_portfolio_price_data()

    if result["success"]:
        print(f"\n✅ SUCCESS!")
        print(f"   Provider: {result['assignment']['provider_id']}")
        print(f"   Price Paid: {result['assignment']['agreed_price_usdc']} USDC")
        print(f"   Total Bids: {result['total_bids']}")
        print(f"   Transaction: {result.get('payment_tx', 'N/A')}")
        print(f"   Data: {result.get('data', {})}")
    else:
        print(f"\n❌ FAILED: {result.get('error', 'Unknown error')}")