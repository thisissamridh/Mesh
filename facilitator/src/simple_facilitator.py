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
KORA_RPC_URL = os.getenv("KORA_RPC_URL", "http://localhost:8080")
http_client = httpx.Client()

print(f"\n{'='*60}")
print(f"  x402 Facilitator Starting (with Kora)")
print(f"{'='*60}")
print(f"  Facilitator Pubkey: {facilitator_keypair.pubkey()}")
print(f"  RPC URL: {RPC_URL}")
print(f"  Kora RPC URL: {KORA_RPC_URL}")
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
    Verifies transaction using Kora's signTransaction (gasless validation)
    """
    try:
        print(f"\n🔍 Verifying transaction via Kora...")

        # Call Kora's signTransaction endpoint
        kora_response = http_client.post(
            f"{KORA_RPC_URL}/signTransaction",
            json={
                "transaction": request.payment,
                "commitment": "confirmed",
            },
        )

        if kora_response.status_code == 200:
            result = kora_response.json()
            is_valid = "signature" in result or "transaction" in result

            print(f"   ✅ Kora validated transaction")
            return {
                "isValid": is_valid,
                "message": "Transaction verified by Kora",
            }
        else:
            print(f"   ❌ Kora validation failed: {kora_response.text}")
            return {
                "isValid": False,
                "message": f"Kora validation failed: {kora_response.text}",
            }

    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        return {"isValid": False, "message": str(e)}


@app.post("/settle")
async def settle_payment(request: SettleRequest):
    """
    x402 /settle endpoint
    Uses Kora to sign as fee payer and broadcast (GASLESS for user!)
    """
    try:
        print(f"\n💳 Settling payment via Kora (gasless)...")
        print(f"   Transaction: {request.payment[:20]}...")

        # Call Kora's signAndSendTransaction endpoint
        # Kora will sign as fee payer and broadcast to Solana
        kora_response = http_client.post(
            f"{KORA_RPC_URL}/signAndSendTransaction",
            json={
                "transaction": request.payment,
                "commitment": "confirmed",
            },
        )

        if kora_response.status_code == 200:
            result = kora_response.json()
            signature = result.get("signature") or result.get("transaction")

            if signature:
                print(f"✅ Payment settled via Kora!")
                print(f"   Signature: {signature}")
                print(f"   🎉 Gasless: Kora paid the fees!")

                return {
                    "success": True,
                    "transaction": signature,
                    "network": "solana-devnet",
                    "gasless": True,
                }
            else:
                raise Exception(f"No signature in Kora response: {result}")
        else:
            error_text = kora_response.text
            print(f"❌ Kora settlement failed: {error_text}")
            raise Exception(f"Kora settlement failed: {error_text}")

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
