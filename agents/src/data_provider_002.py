"""
Second Data Provider - Competes with first provider
Different pricing strategy to show marketplace competition
"""

import os
from dotenv import load_dotenv

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from bidding_data_provider import BiddingDataProviderAgent

load_dotenv(dotenv_path="../../.env")


if __name__ == "__main__":
    # Second data provider with different strategy
    # - Lower price to compete
    # - Emphasizes speed over quality

    agent = BiddingDataProviderAgent(
        agent_id="data_provider_002",
        agent_name="Fast Price Provider",
        wallet_address=os.getenv("PROVIDER_002_PUBKEY", "WALLET_ADDRESS_HERE"),
        port=5002,
        base_price_usdc=0.00012,  # Slightly cheaper than provider_001
    )

    print("\n🏪 Strategy: Compete on price and speed")
    print("   Price: 0.00012 USDC (vs 0.00015 from competitor)")
    print("   Focus: Fast delivery\n")

    agent.start()
