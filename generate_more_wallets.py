#!/usr/bin/env python3
"""
Generate additional Solana wallets for agent marketplace
"""

from solders.keypair import Keypair
import base58

def generate_wallet(name):
    keypair = Keypair()
    pubkey = str(keypair.pubkey())
    private_key = base58.b58encode(bytes(keypair)).decode('utf-8')

    print(f"\n{name}:")
    print(f"Public Key:  {pubkey}")
    print(f"Private Key: {private_key}")

    return pubkey, private_key

if __name__ == "__main__":
    print("=" * 60)
    print("  Generating Additional Agent Wallets")
    print("=" * 60)

    wallets = {}

    # Generate wallets
    wallets['PORTFOLIO_MANAGER'] = generate_wallet("Portfolio Manager (Consumer)")
    wallets['PROVIDER_002'] = generate_wallet("Data Provider 002 (Competing Provider)")

    print("\n" + "=" * 60)
    print("  Add these to your .env file:")
    print("=" * 60)

    print("\n# Portfolio Manager Wallet (Independent Consumer)")
    print(f"PORTFOLIO_MANAGER_PUBKEY={wallets['PORTFOLIO_MANAGER'][0]}")
    print(f"PORTFOLIO_MANAGER_PRIVATE_KEY={wallets['PORTFOLIO_MANAGER'][1]}")

    print("\n# Data Provider 002 Wallet (Competing Provider)")
    print(f"PROVIDER_002_PUBKEY={wallets['PROVIDER_002'][0]}")
    print(f"PROVIDER_002_PRIVATE_KEY={wallets['PROVIDER_002'][1]}")

    print("\n" + "=" * 60)
    print("  Fund these wallets on Solana Devnet:")
    print("=" * 60)

    print("\n# Airdrop SOL for gas fees:")
    print(f"solana airdrop 1 {wallets['PORTFOLIO_MANAGER'][0]} --url devnet")
    print(f"solana airdrop 1 {wallets['PROVIDER_002'][0]} --url devnet")

    print("\n# Get USDC from Circle faucet:")
    print(f"Visit: https://faucet.circle.com/")
    print(f"Send to Portfolio Manager: {wallets['PORTFOLIO_MANAGER'][0]}")
    print(f"Send to Provider 002: {wallets['PROVIDER_002'][0]}")
