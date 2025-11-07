"""
ConsumerAgent - Discovers and pays DataProviderAgent for price data using Pydantic AI
"""

import os
import httpx
from pydantic_ai import Agent
from pydantic import BaseModel
from typing import Optional, List
from dataclasses import dataclass
from dotenv import load_dotenv
from solders.keypair import Keypair
import base58

from x402_client import X402Client, X402PaymentResponse

load_dotenv(dotenv_path="../../.env")


class AgentInfo(BaseModel):
    """Agent information from registry"""
    agent_id: str
    name: str
    service_type: str
    wallet_address: str
    endpoint_url: str
    capabilities: List[dict]
    status: str


class PriceRequest(BaseModel):
    """Price data request"""
    symbol: str = "SOL/USDC"


@dataclass
class Dependencies:
    """Dependencies injected into Pydantic AI agent"""
    registry_url: str
    x402_client: X402Client
    http_client: httpx.Client


class ConsumerAgent:
    """
    Consumer agent that discovers and pays other agents for services
    Uses Pydantic AI for agent logic and x402 for payments
    """

    def __init__(
        self,
        agent_id: str,
        payer_keypair: Keypair,
        registry_url: str = "http://localhost:8000",
        facilitator_url: str = "http://localhost:3000",
    ):
        self.agent_id = agent_id
        self.payer = payer_keypair
        self.registry_url = registry_url
        self.facilitator_url = facilitator_url

        # Initialize x402 client
        self.x402_client = X402Client(
            payer_keypair=payer_keypair,
            facilitator_url=facilitator_url,
        )

        self.http_client = httpx.Client(timeout=30.0)

        # Initialize Pydantic AI agent
        self.agent = Agent(
            'openai:gpt-4o',  # Can use any model
            deps_type=Dependencies,
            system_prompt=(
                "You are an autonomous AI agent that can discover and pay other agents "
                "for services using the x402 micropayment protocol on Solana. "
                "You can query the registry, evaluate options, and make payments."
            ),
        )

        # Register tools
        self._register_tools()

    def _register_tools(self):
        """Register tools that the agent can use"""

        @self.agent.tool
        def discover_agents(
            ctx,
            service_type: Optional[str] = None,
            capability_name: Optional[str] = None,
        ) -> List[AgentInfo]:
            """
            Discover agents in the registry by service type or capability

            Args:
                service_type: Filter by service type (e.g., "data_provider")
                capability_name: Search by capability name (e.g., "price")

            Returns:
                List of matching agents with their details
            """
            params = {}
            if service_type:
                params["service_type"] = service_type
            if capability_name:
                params["capability_name"] = capability_name

            try:
                response = ctx.deps.http_client.get(
                    f"{ctx.deps.registry_url}/agents",
                    params=params,
                )

                if response.status_code == 200:
                    data = response.json()
                    return [AgentInfo(**agent) for agent in data["agents"]]
                else:
                    return []

            except Exception as e:
                print(f"❌ Discovery error: {str(e)}")
                return []

        @self.agent.tool
        def call_agent_with_payment(
            ctx,
            agent_id: str,
            endpoint_url: str,
            path: str = "/price/sol-usdc",
        ) -> dict:
            """
            Call an agent's endpoint with x402 payment

            Args:
                agent_id: The agent to call
                endpoint_url: Base URL of the agent
                path: API path to call

            Returns:
                Response data from the agent
            """
            full_url = f"{endpoint_url.rstrip('/')}{path}"

            print(f"\n💳 Calling {agent_id} at {full_url}")
            print(f"   Using x402 payment...")

            # Use x402 client to handle payment automatically
            response = ctx.deps.x402_client.fetch_with_payment(
                url=full_url,
                method="GET",
            )

            if response.success:
                print(f"✅ Payment successful!")
                print(f"   Transaction: {response.transaction_signature}")
                return response.data
            else:
                print(f"❌ Payment failed: {response.error}")
                return {"error": response.error}

    def run_task(self, task: str):
        """
        Run a task using the Pydantic AI agent

        Example tasks:
        - "Find me a price data provider and get SOL/USDC price"
        - "Discover all data providers"
        """

        deps = Dependencies(
            registry_url=self.registry_url,
            x402_client=self.x402_client,
            http_client=self.http_client,
        )

        print(f"\n{'='*60}")
        print(f"  ConsumerAgent Task")
        print(f"{'='*60}")
        print(f"  Agent ID: {self.agent_id}")
        print(f"  Task: {task}")
        print(f"{'='*60}\n")

        try:
            result = self.agent.run_sync(task, deps=deps)
            print(f"\n{'='*60}")
            print(f"  Task Result")
            print(f"{'='*60}")
            print(f"{result.data}")
            print(f"{'='*60}\n")

            return result.data

        except Exception as e:
            print(f"\n❌ Task failed: {str(e)}")
            return None

    def discover_and_call_provider(self):
        """
        Simple workflow: Discover data provider and get price
        """

        print(f"\n{'='*60}")
        print(f"  Agent Discovery & Payment Workflow")
        print(f"{'='*60}\n")

        # Step 1: Discover data providers
        print("1️⃣ Discovering data providers...")
        try:
            response = self.http_client.get(
                f"{self.registry_url}/agents",
                params={"service_type": "data_provider"},
            )

            if response.status_code == 200:
                agents_data = response.json()
                agents = agents_data.get("agents", [])

                if not agents:
                    print("❌ No data providers found in registry")
                    return None

                provider = agents[0]
                print(f"✅ Found: {provider['name']}")
                print(f"   Agent ID: {provider['agent_id']}")
                print(f"   Endpoint: {provider['endpoint_url']}")
                print(f"   Price: {provider['capabilities'][0]['price_usdc']} USDC")

                # Step 2: Call provider with payment
                print(f"\n2️⃣ Requesting price data from {provider['name']}...")

                payment_response = self.x402_client.fetch_with_payment(
                    url=f"{provider['endpoint_url']}/price/sol-usdc",
                    method="GET",
                )

                if payment_response.success:
                    print(f"\n✅ Payment Successful!")
                    print(f"   Transaction: {payment_response.transaction_signature}")
                    print(f"\n📊 Price Data Received:")
                    print(f"   {payment_response.data}")

                    return payment_response.data
                else:
                    print(f"\n❌ Payment Failed: {payment_response.error}")
                    return None

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None

    def close(self):
        """Cleanup resources"""
        self.x402_client.close()
        self.http_client.close()


if __name__ == "__main__":
    # Load keypair from environment
    payer_private_key = os.getenv("CONSUMER_PRIVATE_KEY", "")

    if not payer_private_key:
        print("❌ CONSUMER_PRIVATE_KEY not set in .env")
        exit(1)

    # Create keypair from private key
    payer_keypair = Keypair.from_bytes(base58.b58decode(payer_private_key))

    # Initialize consumer agent
    consumer = ConsumerAgent(
        agent_id="consumer_001",
        payer_keypair=payer_keypair,
    )

    try:
        # Run discovery and payment workflow
        consumer.discover_and_call_provider()

    finally:
        consumer.close()
