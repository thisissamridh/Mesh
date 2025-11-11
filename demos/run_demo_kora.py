#!/usr/bin/env python3
"""
Demo script for x402 USDC + Kora Providers
Tests proper SPL token payments via Kora gasless transactions
"""

import requests
import json
import time
from datetime import datetime

# ANSI Color codes
CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
DIM = '\033[2m'
NC = '\033[0m'

REGISTRY_URL = "http://localhost:8000"
FACILITATOR_URL = "http://localhost:3000"
KORA_PROVIDER_URLS = [
    "http://localhost:6001",
    "http://localhost:6002",
]

def print_header(title):
    print(f"\n{CYAN}{BOLD}{'='*70}{NC}")
    print(f"{CYAN}{BOLD}  {title}{NC}")
    print(f"{CYAN}{BOLD}{'='*70}{NC}\n")

def print_step(step_num, description):
    print(f"{GREEN}{step_num}.{NC} {description}")

def print_success(message):
    print(f"{GREEN}✅ {message}{NC}")

def print_error(message):
    print(f"{RED}❌ {message}{NC}")

def print_info(message):
    print(f"{YELLOW}ℹ️  {message}{NC}")

def main():
    print(f"\n{CYAN}{BOLD}╔════════════════════════════════════════════════════════════════════╗{NC}")
    print(f"{CYAN}{BOLD}║          x402 USDC + Kora Gasless Payment Demo                     ║{NC}")
    print(f"{CYAN}{BOLD}║       Proper SPL Token Payments • x402 Protocol • Kora RPC         ║{NC}")
    print(f"{CYAN}{BOLD}╚════════════════════════════════════════════════════════════════════╝{NC}\n")

    session = requests.Session()
    session.timeout = 30.0

    # Step 1: Check provider endpoints
    print_header("Step 1: Verify Kora Providers")
    providers = []
    for url in KORA_PROVIDER_URLS:
        try:
            response = session.get(url, timeout=30)
            data = response.json()
            providers.append({"url": url, "data": data})
            print_success(f"Provider {data['provider_id']} online")
            print(f"  Wallet: {data['wallet']}")
            print(f"  Payment: {data['payment_method']}")
            print(f"  Gasless: {data['gasless']}")
        except Exception as e:
            print_error(f"Failed to connect to {url}: {e}")
            return

    # Step 2: Create and broadcast RFP
    print_header("Step 2: Broadcast RFP for SOL/USDC Price Data")
    rfp = {
        "rfp_id": f"rfp_{int(time.time())}",
        "requester_id": "demo_consumer",
        "task_type": "price_data",
        "task_description": "Get current SOL/USDC price",
        "max_budget_usdc": 0.001,
        "requirements": {
            "min_reputation_score": 50,
            "response_time_ms": 5000,
        },
    }

    print_info(f"RFP ID: {rfp['rfp_id']}")
    print_info(f"Task: {rfp['task_description']}")
    print_info(f"Budget: {rfp['max_budget_usdc']} USDC")

    # Step 3: Collect bids
    print_header("Step 3: Collect Bids from Providers")
    bids = []
    for provider in providers:
        try:
            response = session.post(f"{provider['url']}/rfp", json=rfp, timeout=30)
            bid = response.json()
            bids.append({"provider": provider, "bid": bid})
            print_success(f"Bid received from {bid['bidder_id']}")
            print(f"  Price: {bid['price_usdc']} USDC")
            print(f"  Completion time: {bid.get('estimated_completion_time_ms', 0)/1000}s")
            print(f"  Reputation: {bid.get('reputation_score', 0)}")
        except Exception as e:
            print_error(f"Failed to get bid from {provider['url']}: {e}")

    if not bids:
        print_error("No bids received!")
        return

    # Step 4: Select winner (cheapest bid)
    print_header("Step 4: Select Winning Bid")
    winner = min(bids, key=lambda x: x['bid']['price_usdc'])
    print_success(f"Winner: {winner['bid']['bidder_id']}")
    print(f"  Price: {winner['bid']['price_usdc']} USDC")
    print(f"  Summary: {winner['bid']['capabilities_summary']}")

    # Step 5: Assign task
    print_header("Step 5: Assign Task & Request Payment")
    assignment = {
        "assignment_id": f"assign_{int(time.time())}",
        "rfp_id": rfp['rfp_id'],
        "winning_bid_id": winner['bid']['bid_id'],
        "requester_id": "demo_consumer",
        "provider_id": winner['bid']['bidder_id'],
        "agreed_price_usdc": winner['bid']['price_usdc'],
        "task_description": rfp['task_description'],
    }

    print_info(f"Assignment ID: {assignment['assignment_id']}")
    print_info(f"Payment: {assignment['agreed_price_usdc']} USDC")

    try:
        response = session.post(f"{winner['provider']['url']}/assign", json=assignment, timeout=30)

        if response.status_code == 200:
            result = response.json()

            print_header("✅ SUCCESS - x402 USDC Payment Completed!")

            print(f"\n{BOLD}📊 Data Received:{NC}")
            print(f"  Symbol: {result['data']['symbol']}")
            print(f"  Price: ${result['data']['price']}")
            print(f"  Source: {result['data']['source']}")
            print(f"  Timestamp: {result['data']['timestamp']}")

            print(f"\n{BOLD}💳 Payment Details:{NC}")
            print(f"  Method: {result['payment_method']}")
            print(f"  Status: {GREEN}{'Confirmed' if result['payment_confirmed'] else 'Failed'}{NC}")
            print(f"  Transaction: {CYAN}{result['transaction']}{NC}")

            print(f"\n{BOLD}🔍 Verify on Solana Explorer:{NC}")
            print(f"  {CYAN}https://explorer.solana.com/tx/{result['transaction']}?cluster=devnet{NC}")

            print(f"\n{BOLD}✨ Expected Transaction Details:{NC}")
            print(f"  {GREEN}✓{NC} Program: Token Program (NOT System Program)")
            print(f"  {GREEN}✓{NC} Type: transferChecked (NOT simple transfer)")
            print(f"  {GREEN}✓{NC} Token: USDC (4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU)")
            print(f"  {GREEN}✓{NC} Fee Payer: Kora Signer (gasless for provider)")

            print(f"\n{CYAN}{BOLD}{'='*70}{NC}")
            print(f"{GREEN}{BOLD}  🎉 Demo completed successfully!{NC}")
            print(f"{CYAN}{BOLD}{'='*70}{NC}\n")

        else:
            print_error(f"Assignment failed with status {response.status_code}")
            print(response.text)

    except Exception as e:
        print_error(f"Failed to assign task: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
