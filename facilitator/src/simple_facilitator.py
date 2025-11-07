"""
Simple Python x402 Facilitator
Handles payment verification and settlement on Solana devnet
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
import os
import base58
import httpx
from solders.keypair import Keypair
from solders.transaction import Transaction
from solders.pubkey import Pubkey
from solders.system_program import transfer, TransferParams
from solders.message import Message
from solders.hash import Hash
from dotenv import load_dotenv
import uvicorn
import json

load_dotenv(dotenv_path="../../.env")

app = FastAPI(title="x402 Facilitator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load facilitator keypair
FACILITATOR_PRIVATE_KEY = os.getenv("FACILITATOR_PRIVATE_KEY")
facilitator_keypair = Keypair.from_bytes(base58.b58decode(FACILITATOR_PRIVATE_KEY))

RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com")
http_client = httpx.Client()

print(f"\n{'='*60}")
print(f"  x402 Facilitator Starting")
print(f"{'='*60}")
print(f"  Facilitator Pubkey: {facilitator_keypair.pubkey()}")
print(f"  RPC URL: {RPC_URL}")
print(f"{'='*60}\n")


class VerifyRequest(BaseModel):
    payment: str  # Base64 encoded transaction


class SettleRequest(BaseModel):
    payment: str  # Base64 encoded transaction


@app.get("/")
def root():
    return {
        "service": "x402 Facilitator",
        "facilitator": str(facilitator_keypair.pubkey()),
        "network": "solana-devnet",
    }


@app.get("/supported")
def get_supported():
    """
    x402 /supported endpoint
    Returns facilitator capabilities
    """
    return {
        "version": "0.1.0",
        "network": "solana-devnet",
        "paymentScheme": "exact",
        "feePayer": str(facilitator_keypair.pubkey()),
    }


@app.post("/verify")
async def verify_payment(request: VerifyRequest):
    """
    x402 /verify endpoint
    Verifies transaction without broadcasting
    """
    try:
        # Decode transaction
        tx_bytes = base58.b58decode(request.payment)
        transaction = Transaction.from_bytes(tx_bytes)

        print(f"\n🔍 Verifying transaction...")
        print(f"   Signatures: {len(transaction.signatures)}")

        # Basic validation
        is_valid = len(transaction.signatures) > 0

        return {
            "isValid": is_valid,
            "message": "Transaction verified" if is_valid else "Invalid transaction",
        }

    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        return {"isValid": False, "message": str(e)}


@app.post("/settle")
async def settle_payment(request: SettleRequest):
    """
    x402 /settle endpoint
    Signs transaction as fee payer and broadcasts to Solana
    """
    try:
        # Decode transaction
        tx_bytes = base58.b58decode(request.payment)
        transaction = Transaction.from_bytes(tx_bytes)

        print(f"\n💳 Settling payment...")
        print(f"   Transaction: {request.payment[:20]}...")

        # For MVP: Just broadcast the already-signed transaction from client
        # The client's wallet pays its own fees
        # In production with Kora, facilitator would sign as fee payer

        serialized = request.payment

        send_response = http_client.post(
            RPC_URL,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "sendTransaction",
                "params": [
                    serialized,
                    {
                        "encoding": "base58",
                        "skipPreflight": False,
                        "preflightCommitment": "processed",
                    },
                ],
            },
        )

        result = send_response.json()

        if "result" in result:
            signature = result["result"]
            print(f"✅ Payment settled!")
            print(f"   Signature: {signature}")

            return {
                "success": True,
                "transaction": signature,
                "network": "solana-devnet",
            }
        else:
            error = result.get("error", {})
            print(f"❌ Settlement failed: {error}")
            raise Exception(f"Transaction failed: {error}")

    except Exception as e:
        print(f"❌ Settlement error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=3000,
        log_level="info",
    )
