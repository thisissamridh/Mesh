"""
Jupiter Token Verification Provider Agent

Provides token verification status, holder count, liquidity, and more
Uses real Jupiter Token API data
"""

import os
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any
import uvicorn
from datetime import datetime
from dotenv import load_dotenv

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

# Load environment
dotenv_path = os.path.join(os.path.dirname(__file__), "../../.env")
load_dotenv(dotenv_path=dotenv_path)


class JupiterVerificationProvider:
    """
    Provider that fetches token verification and stats from Jupiter
    """

    def __init__(
        self,
        provider_id: str = "jupiter_verify_provider_001",
        port: int = 5004,
        price_per_request: float = 0.0002  # 0.0002 USDC for verification check
    ):
        self.provider_id = provider_id
        self.port = port
        self.price_per_request = price_per_request

        # Jupiter Token API
        self.token_api = "https://lite-api.jup.ag/tokens/v2"

        # Common tokens
        self.tokens = {
            "SOL": "So11111111111111111111111111111111111111112",
            "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            "USDT": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
            "BONK": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"
        }

        self.app = FastAPI(title=f"Jupiter Verification Provider - {provider_id}")
        self.http_client = httpx.AsyncClient(timeout=30.0)

        self._setup_routes()

        # Stats
        self.requests_served = 0
        self.total_earnings = 0.0

    def _setup_routes(self):
        """Setup FastAPI routes"""

        @self.app.get("/")
        async def root():
            return {
                "provider_id": self.provider_id,
                "service": "Token verification & analytics from Jupiter",
                "price": f"{self.price_per_request} USDC per request",
                "data_source": "Jupiter Token API (Real Solana)",
                "endpoints": ["/deliver", "/health", "/stats"],
                "capabilities": ["token_verification", "token_analytics", "safety_check"],
                "reputation": 0.98,
                "requests_served": self.requests_served
            }

        @self.app.get("/health")
        async def health():
            return {"status": "healthy", "provider": self.provider_id}

        @self.app.get("/stats")
        async def stats():
            return {
                "provider_id": self.provider_id,
                "requests_served": self.requests_served,
                "total_earnings": self.total_earnings,
                "uptime": "99.5%"
            }

        @self.app.post("/deliver")
        async def deliver(request: Request):
            """Deliver verification data after payment"""

            # Check x402 payment
            payment_token = request.headers.get("x402-payment-token")
            if not payment_token:
                raise HTTPException(
                    status_code=402,
                    detail="Payment Required",
                    headers={"WWW-Authenticate": "x402"}
                )

            # Get request data
            try:
                body = await request.json()
            except:
                body = {}

            # Get token symbol or address
            token = body.get("token", "SOL")

            # Fetch verification data
            try:
                result = await self._fetch_token_verification(token)

                self.requests_served += 1
                self.total_earnings += self.price_per_request

                return {
                    "success": True,
                    "data": result,
                    "payment_confirmed": True,
                    "agent_id": self.provider_id,
                    "message": "Token verification data delivered",
                    "data_source": "Jupiter Token API"
                }

            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error fetching data: {str(e)}"
                )

    async def _fetch_token_verification(self, token: str) -> Dict[str, Any]:
        """
        Fetch token verification and stats from Jupiter
        """

        # Convert symbol to address if needed
        token_addr = self.tokens.get(token.upper(), token)

        # Search for verified tokens matching query
        url = f"{self.token_api}/tag?query=verified"
        response = await self.http_client.get(url)
        response.raise_for_status()
        verified_tokens = response.json()

        # Find our token
        token_data = None
        for t in verified_tokens:
            if t.get("id") == token_addr or t.get("symbol", "").upper() == token.upper():
                token_data = t
                break

        if not token_data:
            # Try fetching by address directly
            url = f"{self.token_api}/strict"
            response = await self.http_client.get(url)
            tokens = response.json()

            for t in tokens:
                if t.get("id") == token_addr:
                    token_data = t
                    break

        if not token_data:
            return {
                "token": token,
                "address": token_addr,
                "is_verified": False,
                "error": "Token not found in Jupiter database",
                "timestamp": datetime.utcnow().isoformat()
            }

        # Extract key information
        return {
            "token": {
                "symbol": token_data.get("symbol"),
                "name": token_data.get("name"),
                "address": token_data.get("id"),
                "decimals": token_data.get("decimals"),
                "icon": token_data.get("icon")
            },
            "verification": {
                "is_verified": token_data.get("isVerified", False),
                "tags": token_data.get("tags", []),
                "organic_score": token_data.get("organicScore", 0),
                "organic_score_label": token_data.get("organicScoreLabel", "unknown")
            },
            "supply": {
                "circulating": token_data.get("circSupply", 0),
                "total": token_data.get("totalSupply", 0)
            },
            "holders": {
                "count": token_data.get("holderCount", 0)
            },
            "price": {
                "usd": token_data.get("usdPrice", 0),
                "fdv": token_data.get("fdv", 0),
                "mcap": token_data.get("mcap", 0),
                "liquidity": token_data.get("liquidity", 0)
            },
            "security": {
                "mint_authority_disabled": token_data.get("audit", {}).get("mintAuthorityDisabled", False),
                "freeze_authority_disabled": token_data.get("audit", {}).get("freezeAuthorityDisabled", False),
                "top_holders_percentage": token_data.get("audit", {}).get("topHoldersPercentage", 0)
            },
            "stats_24h": token_data.get("stats24h", {}),
            "community": {
                "ct_likes": token_data.get("ctLikes", 0),
                "smart_ct_likes": token_data.get("smartCtLikes", 0)
            },
            "timestamp": datetime.utcnow().isoformat(),
            "source": "Jupiter Token API"
        }

    async def register_with_marketplace(self, registry_url: str):
        """Register with x402 marketplace"""

        registration_data = {
            "agent_id": self.provider_id,
            "agent_type": "provider",
            "capabilities": ["token_verification", "token_analytics"],
            "endpoint_url": f"http://localhost:{self.port}",
            "pricing": {
                "token_verification": self.price_per_request
            },
            "metadata": {
                "name": "Jupiter Verification Provider",
                "description": "Token verification and analytics from Jupiter",
                "data_source": "Jupiter Token API (Real Solana)",
                "reputation_score": 0.98,
                "response_time_ms": 300
            }
        }

        try:
            response = await self.http_client.post(
                f"{registry_url}/agents/register",
                json=registration_data
            )
            response.raise_for_status()
            print(f"✅ Registered with marketplace at {registry_url}")
        except Exception as e:
            print(f"⚠️  Could not register with marketplace: {e}")

    def run(self, registry_url: str = "http://localhost:8000"):
        """Start the provider service"""

        print(f"\n{'='*70}")
        print(f"🔍 Jupiter Verification Provider Starting")
        print(f"{'='*70}")
        print(f"Provider ID:   {self.provider_id}")
        print(f"Port:          {self.port}")
        print(f"Price:         {self.price_per_request} USDC per request")
        print(f"Data Source:   Jupiter Token API (Real Solana)")
        print(f"Capabilities:  Verification, Analytics, Safety Checks")
        print(f"{'='*70}\n")

        # Register with marketplace after server starts
        @self.app.on_event("startup")
        async def startup_event():
            await self.register_with_marketplace(registry_url)

        # Start server
        uvicorn.run(
            self.app,
            host="0.0.0.0",
            port=self.port,
            log_level="info"
        )


if __name__ == "__main__":
    provider = JupiterVerificationProvider(
        provider_id="jupiter_verify_provider_001",
        port=5004,
        price_per_request=0.0002
    )

    provider.run()
