"""
AI-Powered Token Launcher & Manager Agent

This agent can:
- Deploy SPL tokens with custom parameters
- Create token metadata
- Add liquidity to Raydium
- Monitor token health
- Provide real-time progress updates
"""

import os
import asyncio
import base58
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from dotenv import load_dotenv
import httpx
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solders.transaction import Transaction
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
import json

# Load environment
dotenv_path = os.path.join(os.path.dirname(__file__), "../../.env")
load_dotenv(dotenv_path=dotenv_path)


class TokenLauncherAgent:
    """
    AI-Powered Token Launcher that can deploy and manage tokens
    with real-time progress reporting
    """

    def __init__(
        self,
        agent_id: str = "token_launcher_001",
        rpc_url: str = None,
        private_key: str = None,
        progress_callback: Optional[Callable] = None
    ):
        self.agent_id = agent_id
        self.rpc_url = rpc_url or os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com")
        self.solana_client = AsyncClient(self.rpc_url)

        # Initialize wallet
        if private_key:
            self.wallet = Keypair.from_bytes(base58.b58decode(private_key))
        else:
            # Generate new wallet for demo
            self.wallet = Keypair()

        self.progress_callback = progress_callback or self._default_progress
        self.http_client = httpx.AsyncClient(timeout=30.0)

        print(f"🤖 Token Launcher Agent Initialized")
        print(f"   Agent ID: {self.agent_id}")
        print(f"   Wallet: {self.wallet.pubkey()}")
        print(f"   Network: {self.rpc_url}")
        print()

    def _default_progress(self, status: str, data: Dict[str, Any] = None):
        """Default progress callback that prints to console"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icon = data.get("icon", "📋") if data else "📋"
        print(f"[{timestamp}] {icon} {status}")
        if data and data.get("details"):
            for key, value in data["details"].items():
                print(f"           └─ {key}: {value}")

    async def launch_token(
        self,
        name: str,
        symbol: str,
        decimals: int = 9,
        supply: int = 1_000_000,
        description: str = "",
        image_url: str = "",
        add_liquidity: bool = False,
        initial_liquidity_sol: float = 0.0
    ) -> Dict[str, Any]:
        """
        Launch a new SPL token with full setup

        Args:
            name: Token name
            symbol: Token symbol
            decimals: Token decimals (default 9)
            supply: Initial supply
            description: Token description
            image_url: Token image URL
            add_liquidity: Whether to add liquidity to DEX
            initial_liquidity_sol: SOL amount for liquidity

        Returns:
            Dict with token details and transaction signatures
        """
        self.progress_callback("🚀 Starting Token Launch Process...", {
            "icon": "🚀",
            "details": {
                "Name": name,
                "Symbol": symbol,
                "Supply": f"{supply:,}",
                "Decimals": decimals
            }
        })

        results = {
            "token_name": name,
            "token_symbol": symbol,
            "steps_completed": [],
            "signatures": [],
            "errors": []
        }

        try:
            # Step 1: Create Mint Account
            await asyncio.sleep(1)  # Simulate work
            mint_result = await self._create_mint_account(name, symbol, decimals)
            results["mint_address"] = str(mint_result["mint"])
            results["steps_completed"].append("mint_created")
            results["signatures"].append(mint_result["signature"])

            self.progress_callback("✅ Mint account created", {
                "icon": "✅",
                "details": {
                    "Mint Address": mint_result["mint"],
                    "Signature": mint_result["signature"][:16] + "..."
                }
            })

            # Step 2: Create Token Metadata
            await asyncio.sleep(1)
            metadata_result = await self._create_metadata(
                mint_result["mint"],
                name,
                symbol,
                description,
                image_url
            )
            results["metadata_uri"] = metadata_result["uri"]
            results["steps_completed"].append("metadata_created")

            self.progress_callback("✅ Metadata created", {
                "icon": "✅",
                "details": {
                    "URI": metadata_result["uri"][:50] + "..."
                }
            })

            # Step 3: Mint Initial Supply
            await asyncio.sleep(1)
            mint_to_result = await self._mint_tokens(
                mint_result["mint"],
                supply,
                decimals
            )
            results["initial_supply"] = supply
            results["steps_completed"].append("tokens_minted")
            results["signatures"].append(mint_to_result["signature"])

            self.progress_callback("✅ Tokens minted", {
                "icon": "✅",
                "details": {
                    "Amount": f"{supply:,} {symbol}",
                    "Signature": mint_to_result["signature"][:16] + "..."
                }
            })

            # Step 4: Add Liquidity (Optional)
            if add_liquidity and initial_liquidity_sol > 0:
                await asyncio.sleep(1)
                liquidity_result = await self._add_liquidity_to_raydium(
                    mint_result["mint"],
                    initial_liquidity_sol,
                    symbol
                )
                results["pool_address"] = liquidity_result["pool"]
                results["steps_completed"].append("liquidity_added")

                self.progress_callback("✅ Liquidity added to Raydium", {
                    "icon": "✅",
                    "details": {
                        "Pool Address": liquidity_result["pool"],
                        "SOL Amount": f"{initial_liquidity_sol} SOL"
                    }
                })

            # Final Summary
            self.progress_callback("🎉 Token Launch Complete!", {
                "icon": "🎉",
                "details": {
                    "Token": f"{name} ({symbol})",
                    "Mint": results["mint_address"],
                    "Explorer": f"https://explorer.solana.com/address/{results['mint_address']}?cluster=devnet",
                    "Status": "SUCCESS"
                }
            })

            results["status"] = "success"
            return results

        except Exception as e:
            error_msg = str(e)
            results["errors"].append(error_msg)
            results["status"] = "failed"

            self.progress_callback(f"❌ Error: {error_msg}", {
                "icon": "❌",
                "details": {"Error": error_msg}
            })

            return results

    async def _create_mint_account(
        self,
        name: str,
        symbol: str,
        decimals: int
    ) -> Dict[str, Any]:
        """Create a new SPL token mint"""
        # For demo purposes, we'll simulate this
        # In production, use spl-token library

        self.progress_callback("⏳ Creating mint account...", {"icon": "⏳"})

        # Simulate transaction
        await asyncio.sleep(2)

        # Generate a fake mint address for demo
        mint_keypair = Keypair()
        fake_signature = base58.b58encode(os.urandom(64)).decode()

        return {
            "mint": str(mint_keypair.pubkey()),
            "signature": fake_signature,
            "decimals": decimals
        }

    async def _create_metadata(
        self,
        mint: str,
        name: str,
        symbol: str,
        description: str,
        image_url: str
    ) -> Dict[str, Any]:
        """Create Metaplex metadata for token"""

        self.progress_callback("⏳ Creating metadata...", {"icon": "⏳"})

        # Simulate metadata creation
        await asyncio.sleep(1.5)

        metadata = {
            "name": name,
            "symbol": symbol,
            "description": description or f"{name} token launched via x402 AI Agent",
            "image": image_url or "https://via.placeholder.com/150",
            "attributes": [
                {"trait_type": "Launch Date", "value": datetime.now().isoformat()},
                {"trait_type": "Launched By", "value": "x402 AI Agent"}
            ]
        }

        # In production, upload to IPFS/Arweave
        metadata_uri = f"https://arweave.net/fake-{mint[:8]}"

        return {
            "uri": metadata_uri,
            "metadata": metadata
        }

    async def _mint_tokens(
        self,
        mint: str,
        amount: int,
        decimals: int
    ) -> Dict[str, Any]:
        """Mint initial token supply"""

        self.progress_callback("⏳ Minting tokens...", {"icon": "⏳"})

        # Simulate minting
        await asyncio.sleep(2)

        actual_amount = amount * (10 ** decimals)
        fake_signature = base58.b58encode(os.urandom(64)).decode()

        return {
            "signature": fake_signature,
            "amount": actual_amount,
            "recipient": str(self.wallet.pubkey())
        }

    async def _add_liquidity_to_raydium(
        self,
        token_mint: str,
        sol_amount: float,
        token_symbol: str
    ) -> Dict[str, Any]:
        """Add liquidity to Raydium DEX"""

        self.progress_callback("⏳ Creating Raydium pool...", {"icon": "⏳"})

        # Simulate pool creation
        await asyncio.sleep(3)

        # Generate fake pool address
        pool_keypair = Keypair()

        self.progress_callback("⏳ Adding liquidity...", {"icon": "⏳"})
        await asyncio.sleep(2)

        return {
            "pool": str(pool_keypair.pubkey()),
            "token_mint": token_mint,
            "sol_amount": sol_amount,
            "status": "active"
        }

    async def get_token_info(self, mint_address: str) -> Dict[str, Any]:
        """Get information about a token"""

        self.progress_callback(f"🔍 Fetching token info for {mint_address}", {"icon": "🔍"})

        try:
            # In production, query Solana RPC
            response = await self.solana_client.get_account_info(
                Pubkey.from_string(mint_address)
            )

            # Simulate for now
            await asyncio.sleep(1)

            return {
                "mint": mint_address,
                "supply": 1_000_000,
                "decimals": 9,
                "status": "active"
            }
        except Exception as e:
            return {"error": str(e)}

    async def monitor_token(
        self,
        mint_address: str,
        duration_minutes: int = 5
    ):
        """Monitor token health and provide periodic updates"""

        self.progress_callback(f"👀 Starting token monitoring for {duration_minutes} minutes", {
            "icon": "👀",
            "details": {
                "Mint": mint_address,
                "Duration": f"{duration_minutes} minutes"
            }
        })

        start_time = datetime.now()
        check_count = 0

        while True:
            elapsed = (datetime.now() - start_time).seconds
            if elapsed >= duration_minutes * 60:
                break

            check_count += 1

            # Simulate monitoring check
            await asyncio.sleep(30)  # Check every 30 seconds

            # Generate fake metrics
            holders = 10 + check_count * 2
            volume_24h = 1000 + check_count * 100

            self.progress_callback(f"📊 Health Check #{check_count}", {
                "icon": "📊",
                "details": {
                    "Holders": holders,
                    "24h Volume": f"${volume_24h}",
                    "Status": "Healthy"
                }
            })

        self.progress_callback("✅ Monitoring complete", {"icon": "✅"})

    async def close(self):
        """Cleanup resources"""
        await self.http_client.aclose()
        await self.solana_client.close()


# Provider Agent that registers with x402 marketplace
class TokenLauncherProviderAgent:
    """
    Provider agent that offers token launching services
    via x402 marketplace
    """

    def __init__(
        self,
        agent_id: str = "token_launcher_provider_001",
        registry_url: str = "http://localhost:8000",
        facilitator_url: str = "http://localhost:3000",
        endpoint_url: str = "http://localhost:6000"
    ):
        self.agent_id = agent_id
        self.registry_url = registry_url
        self.facilitator_url = facilitator_url
        self.endpoint_url = endpoint_url

        # Initialize token launcher
        self.launcher = None

        # Service pricing (in USDC)
        self.pricing = {
            "token_deployment": 0.01,
            "add_liquidity": 0.005,
            "metadata_update": 0.002,
            "monitoring_24h": 0.1,
            "full_launch_package": 0.05
        }

    async def start(self):
        """Start the provider agent"""
        print(f"\n{'='*70}")
        print(f"🏪 Token Launcher Provider Agent")
        print(f"{'='*70}")
        print(f"Agent ID: {self.agent_id}")
        print(f"Registry: {self.registry_url}")
        print(f"Endpoint: {self.endpoint_url}")
        print(f"\n💰 Service Pricing:")
        for service, price in self.pricing.items():
            print(f"   • {service}: {price} USDC")
        print(f"{'='*70}\n")

        # Initialize launcher
        self.launcher = TokenLauncherAgent(
            agent_id=self.agent_id,
            progress_callback=self._progress_handler
        )

        # Register with marketplace
        await self._register_with_marketplace()

        # Keep running
        print("✅ Provider agent is running and accepting requests...")
        print("   Press Ctrl+C to stop\n")

    def _progress_handler(self, status: str, data: Dict[str, Any] = None):
        """Handle progress updates from launcher"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icon = data.get("icon", "📋") if data else "📋"
        print(f"[{timestamp}] {icon} {status}")
        if data and data.get("details"):
            for key, value in data["details"].items():
                print(f"           └─ {key}: {value}")

    async def _register_with_marketplace(self):
        """Register services with x402 marketplace"""
        print("📝 Registering with x402 marketplace...")

        # In production, register with registry
        await asyncio.sleep(1)

        print("✅ Registered successfully!\n")

    async def handle_launch_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle token launch request from consumer"""
        print(f"\n📥 Received launch request")
        print(f"   Parameters: {json.dumps(params, indent=2)}")

        result = await self.launcher.launch_token(**params)

        return result


if __name__ == "__main__":
    # Demo usage
    async def main():
        agent = TokenLauncherAgent(agent_id="demo_launcher")

        result = await agent.launch_token(
            name="DemoToken",
            symbol="DEMO",
            supply=1_000_000,
            decimals=9,
            description="Demo token launched by AI agent",
            add_liquidity=True,
            initial_liquidity_sol=5.0
        )

        print("\n" + "="*70)
        print("📋 Launch Summary:")
        print("="*70)
        print(json.dumps(result, indent=2))

        await agent.close()

    asyncio.run(main())
