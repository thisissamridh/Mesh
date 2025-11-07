"""
Demo Script - Demonstrates agent-to-agent settlement with x402
"""

import os
import sys
import time
import asyncio
from dotenv import load_dotenv
from solders.keypair import Keypair
import base58

from consumer_agent import ConsumerAgent

load_dotenv(dotenv_path="../../.env")


def print_banner(text: str):
    """Print formatted banner"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")


def check_environment():
    """Check if all required environment variables are set"""
    required_vars = [
        "CONSUMER_PRIVATE_KEY",
        "DATA_PROVIDER_ADDRESS",
        "REGISTRY_URL",
        "FACILITATOR_URL",
    ]

    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)

    if missing:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\nPlease configure .env file with required variables")
        return False

    return True


async def main():
    """
    Main demo workflow:
    1. Start registry (manual)
    2. Start DataProviderAgent (manual)
    3. ConsumerAgent discovers provider
    4. ConsumerAgent makes x402 payment
    5. Receives data with transaction proof
    """

    print_banner("x402 Agent-to-Agent Settlement Demo")

    # Check environment
    if not check_environment():
        sys.exit(1)

    print("📋 Pre-flight Checklist:")
    print("   ✓ Environment variables loaded")
    print("   ⏳ Checking services...\n")

    registry_url = os.getenv("REGISTRY_URL", "http://localhost:8000")
    facilitator_url = os.getenv("FACILITATOR_URL", "http://localhost:3000")

    print("Required Services:")
    print(f"   1. Registry API:     {registry_url}")
    print(f"   2. Facilitator:      {facilitator_url}")
    print(f"   3. Kora RPC:         http://localhost:8080")
    print(f"   4. DataProvider:     http://localhost:5000")

    print("\n⚠️  Make sure all services are running:")
    print("   Terminal 1: pnpm run start:registry")
    print("   Terminal 2: pnpm run start:kora")
    print("   Terminal 3: pnpm run start:facilitator")
    print("   Terminal 4: python agents/src/data_provider_agent.py")

    input("\n   Press Enter when all services are ready...")

    # Load consumer keypair
    print("\n🔑 Loading consumer wallet...")
    payer_private_key = os.getenv("CONSUMER_PRIVATE_KEY", "")

    try:
        payer_keypair = Keypair.from_bytes(base58.b58decode(payer_private_key))
        print(f"   Wallet: {payer_keypair.pubkey()}")
    except Exception as e:
        print(f"❌ Failed to load keypair: {str(e)}")
        sys.exit(1)

    # Initialize consumer agent
    print("\n🤖 Initializing ConsumerAgent...")
    consumer = ConsumerAgent(
        agent_id="consumer_001",
        payer_keypair=payer_keypair,
        registry_url=registry_url,
        facilitator_url=facilitator_url,
    )

    try:
        print_banner("Starting Agent Discovery & Payment Flow")

        # Run the workflow
        result = consumer.discover_and_call_provider()

        if result:
            print_banner("✅ Demo Completed Successfully!")
            print("Results:")
            print(f"   • Agent discovery: ✅")
            print(f"   • x402 payment: ✅")
            print(f"   • Data received: ✅")
            print(f"\n   Price Data: {result}")
        else:
            print_banner("❌ Demo Failed")
            print("Check logs above for errors")

    except Exception as e:
        print(f"\n❌ Demo error: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        consumer.close()
        print("\n👋 Demo completed\n")


if __name__ == "__main__":
    asyncio.run(main())
