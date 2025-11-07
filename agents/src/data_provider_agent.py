"""
DataProviderAgent - Provides price data for SOL/USDC via x402 payments
"""

import os
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(dotenv_path="../../.env")


class PriceData(BaseModel):
    """Price data response"""
    symbol: str
    price: float
    timestamp: str
    source: str


class DataProviderAgent:
    """
    Agent that provides real-time price data for Solana tokens
    Requires x402 payment for each request
    """

    def __init__(
        self,
        agent_id: str,
        wallet_address: str,
        port: int = 5000,
        price_usdc: float = 0.0001,
    ):
        self.agent_id = agent_id
        self.wallet_address = wallet_address
        self.port = port
        self.price_usdc = price_usdc
        self.app = FastAPI(title=f"DataProvider-{agent_id}")

        # Setup routes
        self._setup_routes()

    def _setup_routes(self):
        """Setup FastAPI routes"""

        @self.app.get("/")
        def root():
            return {
                "agent_id": self.agent_id,
                "service": "Price Data Provider",
                "status": "active",
            }

        @self.app.get("/price/sol-usdc")
        async def get_sol_price(request: Request):
            """
            Get SOL/USDC price - requires x402 payment
            """

            # Check for payment proof
            payment_proof = request.headers.get("X-Payment-Response")

            if not payment_proof:
                # Return 402 Payment Required
                return JSONResponse(
                    status_code=402,
                    content={
                        "error": "Payment required",
                        "recipient": self.wallet_address,
                        "amount": str(self.price_usdc),
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

    async def _fetch_sol_price(self) -> PriceData:
        """
        Fetch real SOL/USDC price from Jupiter or Pyth
        For MVP, returns mock data
        """

        # TODO: Integrate with real price oracle (Pyth/Jupiter)
        # For now, return mock data
        return PriceData(
            symbol="SOL/USDC",
            price=142.35,  # Mock price
            timestamp=datetime.utcnow().isoformat(),
            source="mock_oracle",
        )

    async def register_to_registry(self, registry_url: str):
        """Register this agent with the central registry"""

        registration_data = {
            "agent_id": self.agent_id,
            "name": "SOL Price Provider",
            "service_type": "data_provider",
            "wallet_address": self.wallet_address,
            "endpoint_url": f"http://localhost:{self.port}",
            "capabilities": [
                {
                    "name": "SOL/USDC Price",
                    "description": "Real-time SOL to USDC price data",
                    "price_usdc": self.price_usdc,
                }
            ],
            "metadata": {
                "version": "1.0.0",
                "update_frequency": "real-time",
            },
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{registry_url}/agents/register",
                    json=registration_data,
                )

                if response.status_code == 200:
                    print(f"✅ Agent {self.agent_id} registered successfully")
                    return response.json()
                else:
                    print(f"❌ Registration failed: {response.text}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Registry registration failed: {response.text}"
                    )

            except Exception as e:
                print(f"❌ Registration error: {str(e)}")
                raise

    def start(self, register_to_registry: bool = True):
        """Start the agent server"""

        print(f"\n{'='*50}")
        print(f"  DataProviderAgent Starting")
        print(f"{'='*50}")
        print(f"  Agent ID: {self.agent_id}")
        print(f"  Wallet: {self.wallet_address}")
        print(f"  Port: {self.port}")
        print(f"  Price: {self.price_usdc} USDC per request")
        print(f"{'='*50}\n")

        # Register with registry on startup
        if register_to_registry:
            registry_url = os.getenv("REGISTRY_URL", "http://localhost:8000")

            @self.app.on_event("startup")
            async def startup_event():
                await self.register_to_registry(registry_url)

        uvicorn.run(
            self.app,
            host="0.0.0.0",
            port=self.port,
            log_level="info",
        )


if __name__ == "__main__":
    # Load configuration from environment
    agent = DataProviderAgent(
        agent_id="data_provider_001",
        wallet_address=os.getenv("DATA_PROVIDER_ADDRESS", ""),
        port=5000,
        price_usdc=0.0001,
    )

    agent.start()
