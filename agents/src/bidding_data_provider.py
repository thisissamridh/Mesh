"""
BiddingDataProviderAgent - Enhanced DataProvider that can bid on RFPs
Uses OpenAI to make intelligent bidding decisions
"""

import os
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import json
import threading
import time

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from shared.schemas.negotiation import TaskType
from shared.schemas.prompts import DATA_PROVIDER_AGENT_PROMPT

load_dotenv(dotenv_path="../../.env")


class PriceData(BaseModel):
    """Price data response"""
    symbol: str
    price: float
    timestamp: str
    source: str


class BiddingDataProviderAgent:
    """
    Data Provider that can:
    1. Serve price data via x402
    2. Listen for RFPs
    3. Decide whether to bid (using OpenAI)
    4. Submit competitive bids
    """

    def __init__(
        self,
        agent_id: str,
        agent_name: str,
        wallet_address: str,
        registry_url: str = "http://localhost:8000",
        endpoint_url: Optional[str] = None,
        port: int = 5000,
        base_price_usdc: float = 0.0001,
        openai_api_key: Optional[str] = None,
        model: str = "gpt-4o-2024-08-06",
    ):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.wallet_address = wallet_address
        self.registry_url = registry_url
        self.endpoint_url = endpoint_url or f"http://localhost:{port}"
        self.port = port
        self.base_price_usdc = base_price_usdc
        self.app = FastAPI(title=f"BiddingDataProvider-{agent_id}")

        # OpenAI client
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", model)
        self.openai_client = OpenAI(api_key=api_key)

        # HTTP client for registry communication
        self.http_client = httpx.Client(timeout=30.0)

        # System prompt
        self.system_prompt = DATA_PROVIDER_AGENT_PROMPT

        # Stats
        self.bids_submitted = 0
        self.bids_won = 0
        self.total_revenue = 0.0

        # Setup routes
        self._setup_routes()

    def _setup_routes(self):
        """Setup FastAPI routes"""

        @self.app.get("/")
        def root():
            return {
                "agent_id": self.agent_id,
                "name": self.agent_name,
                "service": "Bidding Price Data Provider",
                "status": "active",
                "stats": {
                    "bids_submitted": self.bids_submitted,
                    "bids_won": self.bids_won,
                    "total_revenue": self.total_revenue,
                },
            }

        @self.app.get("/price/sol-usdc")
        async def get_sol_price(request: Request):
            """Get SOL/USDC price - requires x402 payment"""

            payment_proof = request.headers.get("X-Payment-Response")

            if not payment_proof:
                return JSONResponse(
                    status_code=402,
                    content={
                        "error": "Payment required",
                        "recipient": self.wallet_address,
                        "amount": str(self.base_price_usdc),
                        "token_mint": os.getenv(
                            "USDC_MINT_ADDRESS",
                            "4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU"
                        ),
                        "network": "solana-devnet",
                    },
                )

            # Payment verified - fetch and return price data
            price_data = await self._fetch_sol_price()

            return {
                "data": price_data.model_dump(),
                "payment_received": True,
                "agent_id": self.agent_id,
            }

        @self.app.post("/deliver")
        async def deliver_data(request: Request):
            """
            Deliver data after winning bid - requires x402 payment
            This is called by orchestrator after task assignment
            """
            payment_proof = request.headers.get("X-Payment-Response")

            if not payment_proof:
                # Return 402 with payment details
                return JSONResponse(
                    status_code=402,
                    content={
                        "error": "Payment required",
                        "recipient": self.wallet_address,
                        "amount": str(self.base_price_usdc),
                        "token_mint": os.getenv(
                            "USDC_MINT_ADDRESS",
                            "4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU"
                        ),
                        "network": "solana-devnet",
                        "facilitator_url": os.getenv("FACILITATOR_URL", "http://localhost:3000"),
                    },
                )

            # Payment received! Deliver the data
            print(f"\n💰 Payment received! Delivering data...")
            print(f"   Payment proof: {payment_proof[:50]}...")

            price_data = await self._fetch_sol_price()

            return {
                "success": True,
                "data": price_data.model_dump(),
                "payment_confirmed": True,
                "agent_id": self.agent_id,
                "message": "Data delivered successfully",
            }

    async def _fetch_sol_price(self) -> PriceData:
        """Fetch real SOL/USDC price - Mock for now"""
        return PriceData(
            symbol="SOL/USDC",
            price=142.35,
            timestamp=datetime.utcnow().isoformat(),
            source="mock_oracle",
        )

    def ask_llm(self, user_message: str) -> str:
        """Ask OpenAI for bidding decisions"""

        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
        )

        return response.choices[0].message.content

    def should_bid_on_rfp(self, rfp: dict) -> bool:
        """
        Use OpenAI to decide if we should bid on this RFP
        """

        prompt = f"""
You received an RFP:

Task Type: {rfp['task_type']}
Description: {rfp['task_description']}
Max Budget: {rfp.get('max_budget_usdc', 'Not specified')} USDC
Requirements: {rfp.get('requirements', {})}

Your capabilities:
- Real-time SOL/USDC price data
- Base price: {self.base_price_usdc} USDC
- Reputation: Good (mock)

Should you bid on this RFP? Consider:
1. Can you fulfill the requirement?
2. Is the budget acceptable?
3. Is it worth your time?

Respond in JSON:
{{
    "should_bid": true/false,
    "reasoning": "why or why not"
}}
"""

        llm_response = self.ask_llm(prompt)

        try:
            # Extract JSON
            if "```json" in llm_response:
                json_str = llm_response.split("```json")[1].split("```")[0].strip()
            elif "```" in llm_response:
                json_str = llm_response.split("```")[1].split("```")[0].strip()
            else:
                json_str = llm_response.strip()

            decision = json.loads(json_str)

            print(f"\n🤔 Bid Decision for RFP {rfp['rfp_id']}:")
            print(f"   Should Bid: {decision['should_bid']}")
            print(f"   Reasoning: {decision['reasoning']}")

            return decision["should_bid"]

        except Exception as e:
            print(f"⚠️  Failed to parse LLM decision, defaulting to bid")
            # Default: bid if budget is acceptable
            max_budget = rfp.get("max_budget_usdc")
            return max_budget is None or max_budget >= self.base_price_usdc

    def calculate_bid_price(self, rfp: dict) -> float:
        """
        Use OpenAI to calculate competitive bid price
        """

        prompt = f"""
You're bidding on an RFP:

Task: {rfp['task_description']}
Max Budget: {rfp.get('max_budget_usdc', 'Not specified')} USDC
Your Base Price: {self.base_price_usdc} USDC

Calculate a competitive bid price. Consider:
1. Underbid competitors while maximizing profit
2. Don't go below cost
3. Account for task complexity

Respond in JSON:
{{
    "bid_price_usdc": 0.00XX,
    "reasoning": "why this price"
}}
"""

        llm_response = self.ask_llm(prompt)

        try:
            if "```json" in llm_response:
                json_str = llm_response.split("```json")[1].split("```")[0].strip()
            elif "```" in llm_response:
                json_str = llm_response.split("```")[1].split("```")[0].strip()
            else:
                json_str = llm_response.strip()

            decision = json.loads(json_str)
            bid_price = decision["bid_price_usdc"]

            print(f"   💰 Calculated Bid: {bid_price} USDC")
            print(f"   Reasoning: {decision['reasoning']}")

            return bid_price

        except Exception as e:
            print(f"⚠️  Failed to calculate bid, using base price")
            return self.base_price_usdc

    def submit_bid(self, rfp_id: str, price_usdc: float):
        """Submit a bid to the registry"""

        print(f"\n📤 Submitting bid for RFP {rfp_id}")
        print(f"   Price: {price_usdc} USDC")

        response = self.http_client.post(
            f"{self.registry_url}/rfp/{rfp_id}/bid",
            params={
                "rfp_id": rfp_id,
                "bidder_id": self.agent_id,
                "bidder_name": self.agent_name,
                "price_usdc": price_usdc,
                "estimated_completion_time_ms": 500,
                "capabilities_summary": "Real-time SOL/USDC price data with sub-second latency",
                "reputation_score": 0.95,
            },
            json={
                "total_requests_served": 1000,
                "average_response_time_ms": 250,
            }
        )

        if response.status_code == 200:
            self.bids_submitted += 1
            print(f"✅ Bid submitted successfully")
            return response.json()
        else:
            print(f"❌ Bid submission failed: {response.text}")
            return None

    def poll_for_rfps(self, interval_seconds: int = 3):
        """
        Background thread that polls for new RFPs
        """

        print(f"\n🔄 Starting RFP polling (every {interval_seconds}s)")

        seen_rfps = set()

        while True:
            try:
                # Get open RFPs for price_data tasks
                response = self.http_client.get(
                    f"{self.registry_url}/rfp/open",
                    params={"task_type": TaskType.PRICE_DATA.value}
                )

                if response.status_code == 200:
                    data = response.json()

                    # Handle different response formats
                    if isinstance(data, dict):
                        rfps = data.get("rfps", [])
                    elif isinstance(data, list):
                        rfps = data
                    else:
                        rfps = []

                    if rfps:
                        print(f"📋 Found {len(rfps)} open RFPs")

                    for rfp in rfps:
                        rfp_id = rfp["rfp_id"]

                        # Skip if already seen
                        if rfp_id in seen_rfps:
                            continue

                        seen_rfps.add(rfp_id)

                        print(f"\n🆕 New RFP detected: {rfp_id}")

                        # Decide whether to bid
                        if self.should_bid_on_rfp(rfp):
                            # Calculate bid price
                            bid_price = self.calculate_bid_price(rfp)

                            # Submit bid
                            self.submit_bid(rfp_id, bid_price)

            except Exception as e:
                print(f"⚠️  Polling error: {str(e)}")

            time.sleep(interval_seconds)

    async def register_to_registry(self):
        """Register this agent with the central registry"""

        registration_data = {
            "agent_id": self.agent_id,
            "name": self.agent_name,
            "service_type": "data_provider",
            "wallet_address": self.wallet_address,
            "endpoint_url": self.endpoint_url,
            "capabilities": [
                {
                    "name": "SOL/USDC Price",
                    "description": "Real-time SOL to USDC price data",
                    "price_usdc": self.base_price_usdc,
                }
            ],
            "metadata": {
                "version": "2.0.0",
                "bidding_enabled": True,
            },
        }

        try:
            response = self.http_client.post(
                f"{self.registry_url}/agents/register",
                json=registration_data,
            )

            if response.status_code == 200:
                print(f"✅ Agent {self.agent_id} registered successfully")

                # Subscribe to PRICE_DATA RFPs
                self.http_client.post(
                    f"{self.registry_url}/agents/{self.agent_id}/subscribe",
                    params={"agent_id": self.agent_id},
                    json=["price_data"],
                )
                print(f"✅ Subscribed to PRICE_DATA RFPs")

                return response.json()
            else:
                print(f"❌ Registration failed: {response.text}")

        except Exception as e:
            print(f"❌ Registration error: {str(e)}")

    def start(self):
        """Start the agent server"""

        print(f"\n{'='*60}")
        print(f"  BiddingDataProviderAgent Starting")
        print(f"{'='*60}")
        print(f"  Agent ID: {self.agent_id}")
        print(f"  Name: {self.agent_name}")
        print(f"  Wallet: {self.wallet_address}")
        print(f"  Port: {self.port}")
        print(f"  Base Price: {self.base_price_usdc} USDC")
        print(f"  Model: {self.model}")
        print(f"{'='*60}\n")

        # Register with registry on startup
        @self.app.on_event("startup")
        async def startup_event():
            await self.register_to_registry()

            # Start RFP polling in background thread
            polling_thread = threading.Thread(
                target=self.poll_for_rfps,
                args=(3,),
                daemon=True
            )
            polling_thread.start()

        uvicorn.run(
            self.app,
            host="0.0.0.0",
            port=self.port,
            log_level="info",
        )


if __name__ == "__main__":
    agent = BiddingDataProviderAgent(
        agent_id="bidding_data_provider_001",
        agent_name="AI-Powered Price Provider",
        wallet_address=os.getenv("PROVIDER_PUBKEY", "WALLET_ADDRESS_HERE"),
        registry_url=os.getenv("REGISTRY_URL", "http://localhost:8000"),
        endpoint_url=os.getenv("ENDPOINT_URL", "http://localhost:5001"),
        port=5001,
        base_price_usdc=0.00015,  # Price from AI bid
    )

    agent.start()
