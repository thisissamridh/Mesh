"""
Python x402 Client - Payment wrapper for agent-to-agent transactions
"""

import httpx
import base64
import base58
import json
from typing import Optional, Dict, Any
from dataclasses import dataclass
from solders.keypair import Keypair
from solders.transaction import Transaction
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solders.instruction import Instruction
from solders.message import Message
from solders.hash import Hash


@dataclass
class X402PaymentResponse:
    """Response from x402 payment"""
    success: bool
    transaction_signature: Optional[str] = None
    data: Optional[Any] = None
    error: Optional[str] = None


class X402Client:
    """
    Python client for making x402-protected API calls
    Automatically handles payment flow for 402 responses
    """

    def __init__(
        self,
        payer_keypair: Keypair,
        facilitator_url: str = "http://localhost:3000",
        network: str = "solana-devnet",
    ):
        self.payer = payer_keypair
        self.facilitator_url = facilitator_url
        self.network = network
        self.http_client = httpx.Client(timeout=30.0)

    def _get_recent_blockhash(self) -> Hash:
        """Get recent blockhash from Solana RPC"""
        try:
            response = self.http_client.post(
                "https://api.devnet.solana.com",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getLatestBlockhash",
                    "params": [{"commitment": "finalized"}],
                },
            )
            result = response.json()
            blockhash_str = result["result"]["value"]["blockhash"]
            return Hash.from_string(blockhash_str)
        except Exception as e:
            # Fallback to a default hash
            return Hash.from_string("11111111111111111111111111111111")

    def _create_payment_transaction(
        self,
        recipient: str,
        amount_usdc: float,
        usdc_mint: str,
    ) -> bytes:
        """
        Create a Solana transaction for USDC payment
        Note: Simplified version - production should use SPL token transfer
        """
        recipient_pubkey = Pubkey.from_string(recipient)

        # For MVP, using SOL transfer as placeholder
        # TODO: Replace with SPL token transfer instruction
        transfer_ix = transfer(
            TransferParams(
                from_pubkey=self.payer.pubkey(),
                to_pubkey=recipient_pubkey,
                lamports=int(amount_usdc * 1_000_000_000),  # Convert to lamports
            )
        )

        # Get real blockhash
        recent_blockhash = self._get_recent_blockhash()

        # Create transaction
        message = Message.new_with_blockhash(
            [transfer_ix],
            self.payer.pubkey(),
            recent_blockhash,
        )

        transaction = Transaction.new_unsigned(message)
        transaction.sign([self.payer], recent_blockhash)

        # Serialize transaction (solders uses bytes() not .serialize())
        return bytes(transaction)

    def _settle_payment(self, payment_b58: str) -> X402PaymentResponse:
        """Send payment to facilitator for settlement"""
        try:
            response = self.http_client.post(
                f"{self.facilitator_url}/settle",
                json={"payment": payment_b58},
            )

            if response.status_code == 200:
                result = response.json()
                return X402PaymentResponse(
                    success=True,
                    transaction_signature=result.get("transaction"),  # Changed from transactionSignature
                )
            else:
                return X402PaymentResponse(
                    success=False,
                    error=f"Settlement failed: {response.text}",
                )

        except Exception as e:
            return X402PaymentResponse(
                success=False,
                error=f"Settlement error: {str(e)}",
            )

    def fetch_with_payment(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> X402PaymentResponse:
        """
        Make HTTP request with automatic x402 payment handling

        Workflow:
        1. Try request without payment
        2. If 402 response, extract payment requirements
        3. Create and settle payment transaction
        4. Retry request with payment proof
        """

        headers = headers or {}

        # Step 1: Try request without payment
        try:
            response = self.http_client.request(method, url, headers=headers, **kwargs)

            # Success - no payment required
            if response.status_code == 200:
                return X402PaymentResponse(
                    success=True,
                    data=response.json() if response.content else None,
                )

            # Payment required
            if response.status_code == 402:
                payment_info = response.json()

                # Extract payment requirements
                recipient = payment_info.get("recipient")
                amount = payment_info.get("amount")
                usdc_mint = payment_info.get("token_mint")

                if not all([recipient, amount, usdc_mint]):
                    return X402PaymentResponse(
                        success=False,
                        error="Invalid payment requirements in 402 response",
                    )

                # Step 2: Create payment transaction
                tx_bytes = self._create_payment_transaction(
                    recipient=recipient,
                    amount_usdc=float(amount),
                    usdc_mint=usdc_mint,
                )

                # Encode as base58 for facilitator
                payment_b58 = base58.b58encode(tx_bytes).decode("utf-8")

                # Step 3: Settle payment
                settlement = self._settle_payment(payment_b58)

                if not settlement.success:
                    return settlement

                # Step 4: Retry with payment proof
                headers["X-Payment-Response"] = json.dumps({
                    "transactionSignature": settlement.transaction_signature,
                    "network": self.network,
                })

                paid_response = self.http_client.request(
                    method, url, headers=headers, **kwargs
                )

                if paid_response.status_code == 200:
                    return X402PaymentResponse(
                        success=True,
                        transaction_signature=settlement.transaction_signature,
                        data=paid_response.json() if paid_response.content else None,
                    )
                else:
                    return X402PaymentResponse(
                        success=False,
                        error=f"Request failed after payment: {paid_response.text}",
                    )

            # Other error
            return X402PaymentResponse(
                success=False,
                error=f"HTTP {response.status_code}: {response.text}",
            )

        except Exception as e:
            return X402PaymentResponse(
                success=False,
                error=f"Request error: {str(e)}",
            )

    def close(self):
        """Close HTTP client"""
        self.http_client.close()
