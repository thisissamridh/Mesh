"""
DEMO: Self-Negotiating Agent Mesh - Quick Start
"""
import sys
import os
from dotenv import load_dotenv

# Load .env first
load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), "agents/src"))

from orchestrator_agent import OrchestratorAgent
from shared.schemas.negotiation import TaskType
import time

print("""
╔══════════════════════════════════════════════════════════════╗
║   SELF-NEGOTIATING AGENT MESH - Solana x402 Hackathon       ║
╚══════════════════════════════════════════════════════════════╝

AI agents that discover, bid, and negotiate autonomously!

TERMINALS NEEDED:
1. python registry/src/main.py
2. python agents/src/bidding_data_provider.py
3. python demo_negotiation.py (this)
""")

input("Press ENTER when ready...")

orchestrator = OrchestratorAgent(agent_id="demo_orch")

try:
    print("\n🎯 Orchestrator needs SOL price data...")

    result = orchestrator.coordinate_task(
        task_type=TaskType.PRICE_DATA,
        task_description="Get SOL/USDC price with high accuracy",
        max_budget_usdc=0.001,
        wait_for_bids_seconds=10,  # Increased to 10s for AI processing time
    )

    if result["success"]:
        print(f"\n✅ SUCCESS!")
        print(f"Provider: {result['assignment']['provider_id']}")
        print(f"Price: {result['assignment']['agreed_price_usdc']} USDC")
        print(f"Bids: {result['total_bids']}")
    else:
        print(f"\n❌ FAILED: {result.get('error')}")

finally:
    orchestrator.close()
