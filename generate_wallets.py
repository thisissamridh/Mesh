#!/usr/bin/env python3
"""
Generate Solana wallets for x402 demo
"""
from solders.keypair import Keypair
import base58

print("🔑 Generating Solana Wallets for x402 Demo\n")
print("="*60)

# Orchestrator wallet (pays for services)
orch_keypair = Keypair()
print("\n📋 ORCHESTRATOR WALLET (Pays for Data)")
print(f"Public Key:  {orch_keypair.pubkey()}")
print(f"Private Key: {base58.b58encode(bytes(orch_keypair)).decode()}")

# Data Provider wallet (receives payments)
provider_keypair = Keypair()
print("\n📊 DATA PROVIDER WALLET (Receives Payments)")
print(f"Public Key:  {provider_keypair.pubkey()}")
print(f"Private Key: {base58.b58encode(bytes(provider_keypair)).decode()}")

# Facilitator wallet (signs transactions, pays gas)
facilitator_keypair = Keypair()
print("\n⚡ FACILITATOR WALLET (Pays Gas Fees)")
print(f"Public Key:  {facilitator_keypair.pubkey()}")
print(f"Private Key: {base58.b58encode(bytes(facilitator_keypair)).decode()}")

print("\n" + "="*60)
print("\n📝 NEXT STEPS:")
print("1. Fund wallets at: https://faucet.solana.com/")
print("   - Send devnet SOL to all 3 wallets")
print("   \n2. Get devnet USDC from: https://faucet.circle.com/")
print("   - Select 'Solana Devnet'")
print("   - Send USDC to ORCHESTRATOR wallet")
print("\n3. Add these to .env file")
