#!/usr/bin/env python3
"""
Setup script to create and fund USDC token accounts for all wallets
"""

import os
import base58
import time
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import create_account, CreateAccountParams
from solders.transaction import Transaction
from solders.message import Message
from spl.token.instructions import (
    get_associated_token_address,
    create_associated_token_account,
    mint_to,
    MintToParams,
    TOKEN_PROGRAM_ID,
    ASSOCIATED_TOKEN_PROGRAM_ID,
)
from spl.token.constants import TOKEN_PROGRAM_ID as TOKEN_PROGRAM
from dotenv import load_dotenv
import httpx

load_dotenv()


class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'


def get_rpc_client():
    """Get Solana RPC client"""
    rpc_url = os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com")
    return httpx.Client(base_url=rpc_url, timeout=30.0)


def get_recent_blockhash(client):
    """Get recent blockhash from Solana"""
    response = client.post(
        "",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getLatestBlockhash",
            "params": [{"commitment": "finalized"}],
        },
    )
    result = response.json()
    from solders.hash import Hash
    return Hash.from_string(result["result"]["value"]["blockhash"])


def send_transaction(client, tx_bytes):
    """Send transaction to Solana"""
    tx_b58 = base58.b58encode(tx_bytes).decode('utf-8')

    response = client.post(
        "",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "sendTransaction",
            "params": [
                tx_b58,
                {"encoding": "base58", "skipPreflight": False, "preflightCommitment": "confirmed"}
            ],
        },
    )

    result = response.json()
    if "error" in result:
        raise Exception(f"Transaction failed: {result['error']}")

    return result["result"]


def request_airdrop(client, pubkey: Pubkey, lamports: int = 2_000_000_000):
    """Request SOL airdrop for transaction fees"""
    response = client.post(
        "",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "requestAirdrop",
            "params": [str(pubkey), lamports],
        },
    )

    result = response.json()
    if "error" in result:
        print(f"   {Colors.YELLOW}Airdrop failed (wallet may already have SOL): {result['error']['message']}{Colors.ENDC}")
        return None

    return result["result"]


def create_ata_if_needed(client, wallet_keypair: Keypair, mint_pubkey: Pubkey, wallet_name: str):
    """Create Associated Token Account if it doesn't exist"""

    ata = get_associated_token_address(wallet_keypair.pubkey(), mint_pubkey)

    print(f"\n{Colors.CYAN}Setting up: {wallet_name}{Colors.ENDC}")
    print(f"  Wallet: {wallet_keypair.pubkey()}")
    print(f"  ATA: {ata}")

    # Create ATA instruction
    create_ata_ix = create_associated_token_account(
        payer=wallet_keypair.pubkey(),
        owner=wallet_keypair.pubkey(),
        mint=mint_pubkey,
    )

    # Get blockhash
    recent_blockhash = get_recent_blockhash(client)

    # Create transaction
    message = Message.new_with_blockhash(
        [create_ata_ix],
        wallet_keypair.pubkey(),
        recent_blockhash,
    )

    transaction = Transaction.new_unsigned(message)
    transaction.sign([wallet_keypair], recent_blockhash)

    # Send transaction
    try:
        sig = send_transaction(client, bytes(transaction))
        print(f"  {Colors.GREEN}✅ ATA created/verified: {sig[:20]}...{Colors.ENDC}")
        return ata
    except Exception as e:
        error_msg = str(e)
        if "already in use" in error_msg or "AccountInUse" in error_msg:
            print(f"  {Colors.GREEN}✅ ATA already exists{Colors.ENDC}")
            return ata
        else:
            print(f"  {Colors.RED}❌ Failed: {e}{Colors.ENDC}")
            raise


def main():
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}  Solana Token Account Setup{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}\n")

    # Load config
    mint_address = os.getenv("USDC_MINT_ADDRESS")
    mint_pubkey = Pubkey.from_string(mint_address)

    print(f"{Colors.BOLD}USDC Mint:{Colors.ENDC} {mint_address}")
    print(f"{Colors.BOLD}Network:{Colors.ENDC} {os.getenv('SOLANA_NETWORK', 'devnet')}\n")

    # Create RPC client
    client = get_rpc_client()

    # List of all wallets
    wallets = [
        ("Portfolio Manager", os.getenv("PORTFOLIO_MANAGER_PRIVATE_KEY")),
        ("Provider 001", os.getenv("PROVIDER_PRIVATE_KEY")),
        ("Provider 002", os.getenv("PROVIDER_002_PRIVATE_KEY")),
        ("Facilitator", os.getenv("FACILITATOR_PRIVATE_KEY")),
    ]

    print(f"{Colors.YELLOW}Step 1: Requesting SOL airdrops for transaction fees...{Colors.ENDC}")

    for name, private_key in wallets:
        if not private_key:
            print(f"{Colors.RED}⚠️  Skipping {name}: No private key found{Colors.ENDC}")
            continue

        keypair = Keypair.from_bytes(base58.b58decode(private_key))
        print(f"\n{Colors.CYAN}{name}:{Colors.ENDC} {keypair.pubkey()}")

        try:
            sig = request_airdrop(client, keypair.pubkey(), 2_000_000_000)
            if sig:
                print(f"  {Colors.GREEN}✅ Airdrop requested: {sig[:20]}...{Colors.ENDC}")
                time.sleep(2)  # Wait for airdrop to confirm
        except Exception as e:
            print(f"  {Colors.YELLOW}⚠️  Airdrop error (continuing anyway): {e}{Colors.ENDC}")

    print(f"\n{Colors.YELLOW}Step 2: Creating Associated Token Accounts...{Colors.ENDC}")

    for name, private_key in wallets:
        if not private_key:
            continue

        keypair = Keypair.from_bytes(base58.b58decode(private_key))

        try:
            create_ata_if_needed(client, keypair, mint_pubkey, name)
            time.sleep(1)  # Brief pause between transactions
        except Exception as e:
            print(f"{Colors.RED}Failed to create ATA for {name}: {e}{Colors.ENDC}")

    print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.GREEN}  Setup Complete!{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.GREEN}{'='*70}{Colors.ENDC}\n")

    print(f"{Colors.YELLOW}Note: Token accounts are created but have 0 USDC balance.{Colors.ENDC}")
    print(f"{Colors.YELLOW}For testing, you can use devnet USDC faucets or mock the balance check.{Colors.ENDC}\n")


if __name__ == "__main__":
    main()
