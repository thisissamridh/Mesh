"""
OrchestratorAgent - Coordinates complex multi-agent workflows using OpenAI
Broadcasts RFPs, evaluates bids, negotiates, and selects winners
"""

import os
import httpx
from typing import List, Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv
import json
import base58
from solders.keypair import Keypair

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from shared.schemas.negotiation import TaskType, Bid, BidEvaluation
from shared.schemas.prompts import ORCHESTRATOR_AGENT_PROMPT
from x402_client import X402Client

# Load .env from project root
dotenv_path = os.path.join(os.path.dirname(__file__), "../../.env")
load_dotenv(dotenv_path=dotenv_path)


class OrchestratorAgent:
    """
    Orchestrator agent that uses OpenAI to coordinate complex tasks
    by broadcasting RFPs and selecting the best agents
    """

    def __init__(
        self,
        agent_id: str,
        registry_url: str = "http://localhost:8000",
        openai_api_key: Optional[str] = None,
        model: str = "gpt-4o-2024-08-06",
    ):
        self.agent_id = agent_id
        self.registry_url = registry_url
        self.http_client = httpx.Client(timeout=60.0)

        # Initialize OpenAI
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", model)
        self.client = OpenAI(api_key=api_key)

        # System prompt
        self.system_prompt = ORCHESTRATOR_AGENT_PROMPT

        # Initialize x402 client for payments
        orchestrator_private_key = os.getenv("ORCHESTRATOR_PRIVATE_KEY")
        if orchestrator_private_key:
            payer_keypair = Keypair.from_bytes(base58.b58decode(orchestrator_private_key))
            self.x402_client = X402Client(
                payer_keypair=payer_keypair,
                facilitator_url=os.getenv("FACILITATOR_URL", "http://localhost:3000"),
                network="solana-devnet",
            )
            self.has_x402 = True
            print(f"   💳 x402 Payment Enabled: {payer_keypair.pubkey()}")
        else:
            self.x402_client = None
            self.has_x402 = False
            print(f"   ⚠️  x402 disabled (no wallet key)")


        print(f"\n{'='*60}")
        print(f"  OrchestratorAgent Initialized")
        print(f"{'='*60}")
        print(f"  Agent ID: {self.agent_id}")
        print(f"  Registry: {self.registry_url}")
        print(f"  Model: {self.model}")
        print(f"{'='*60}\n")

    def ask_llm(self, user_message: str, context: Optional[Dict] = None) -> str:
        """
        Ask OpenAI for guidance on orchestration decisions
        """

        messages = [
            {"role": "system", "content": self.system_prompt},
        ]

        if context:
            messages.append({
                "role": "user",
                "content": f"Context:\n{json.dumps(context, indent=2)}"
            })

        messages.append({"role": "user", "content": user_message})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
        )

        return response.choices[0].message.content

    def broadcast_rfp(
        self,
        task_type: TaskType,
        task_description: str,
        requirements: Optional[Dict] = None,
        max_budget_usdc: Optional[float] = None,
        deadline_seconds: int = 60,
    ) -> str:
        """
        Broadcast an RFP to the registry
        Returns RFP ID
        """

        print(f"\n📢 Broadcasting RFP...")
        print(f"   Task: {task_type.value}")
        print(f"   Description: {task_description}")
        print(f"   Budget: {max_budget_usdc} USDC")

        response = self.http_client.post(
            f"{self.registry_url}/rfp/create",
            params={
                "requester_id": self.agent_id,
                "task_type": task_type.value,
                "task_description": task_description,
                "max_budget_usdc": max_budget_usdc,
                "deadline_seconds": deadline_seconds,
            },
            json=requirements or {},
        )

        if response.status_code == 200:
            rfp_data = response.json()
            rfp_id = rfp_data["rfp_id"]
            print(f"✅ RFP Created: {rfp_id}")
            return rfp_id
        else:
            print(f"❌ RFP creation failed: {response.text}")
            raise Exception(f"Failed to create RFP: {response.text}")

    def get_bids(self, rfp_id: str) -> List[Dict]:
        """Get all bids for an RFP"""

        response = self.http_client.get(f"{self.registry_url}/rfp/{rfp_id}/bids")

        if response.status_code == 200:
            return response.json()
        else:
            return []

    def evaluate_bids_with_llm(
        self,
        rfp_id: str,
        task_description: str,
        bids: List[Dict],
    ) -> str:
        """
        Use OpenAI to evaluate bids and select the best one
        Returns the selected bid_id
        """

        if not bids:
            raise ValueError("No bids to evaluate")

        print(f"\n🤖 Asking AI to evaluate {len(bids)} bids...")

        # Get automated evaluations from RFP manager
        response = self.http_client.get(
            f"{self.registry_url}/rfp/{rfp_id}/evaluate",
            params={
                "price_weight": 0.4,
                "speed_weight": 0.3,
                "reputation_weight": 0.3,
            }
        )

        evaluations = response.json() if response.status_code == 200 else []

        context = {
            "task_description": task_description,
            "num_bids": len(bids),
            "bids": bids,
            "automated_evaluations": evaluations,
        }

        prompt = f"""
You received {len(bids)} bids for this task: "{task_description}"

Bids:
{json.dumps(bids, indent=2)}

Automated Evaluations (sorted by score):
{json.dumps(evaluations, indent=2)}

Based on the task requirements, bid details, and automated evaluations:
1. Which bid should we accept and why?
2. Should we negotiate with any bidders for better terms?
3. Are there any red flags?

Return your response in JSON format:
{{
    "selected_bid_id": "bid_xxx",
    "reasoning": "why this bid was selected",
    "should_negotiate": false,
    "negotiation_strategy": "if should_negotiate is true, explain what to negotiate"
}}
"""

        llm_response = self.ask_llm(prompt, context=None)

        print(f"\n🧠 AI Evaluation:")
        print(llm_response)

        # Parse JSON response
        try:
            # Extract JSON from markdown code blocks if present
            if "```json" in llm_response:
                json_str = llm_response.split("```json")[1].split("```")[0].strip()
            elif "```" in llm_response:
                json_str = llm_response.split("```")[1].split("```")[0].strip()
            else:
                json_str = llm_response.strip()

            decision = json.loads(json_str)
            return decision["selected_bid_id"]

        except Exception as e:
            print(f"⚠️  Failed to parse LLM response, using automated evaluation")
            # Fallback: use automated evaluation
            if evaluations:
                return evaluations[0]["bid_id"]
            else:
                return bids[0]["bid_id"]

    def select_winner(self, rfp_id: str, bid_id: str) -> Dict:
        """
        Select a winning bid
        Returns task assignment
        """

        print(f"\n✅ Selecting winner: {bid_id}")

        response = self.http_client.post(
            f"{self.registry_url}/rfp/{rfp_id}/select",
            params={
                "rfp_id": rfp_id,
                "bid_id": bid_id,
            }
        )

        if response.status_code == 200:
            assignment = response.json()
            print(f"✅ Task assigned: {assignment['assignment_id']}")
            print(f"   Provider: {assignment['provider_id']}")
            print(f"   Price: {assignment['agreed_price_usdc']} USDC")

            # Execute x402 payment and get data
            if self.has_x402:
                print(f"\n💳 Executing x402 Payment...")

                # Get provider endpoint from registry
                provider_response = self.http_client.get(
                    f"{self.registry_url}/agents/{assignment['provider_id']}"
                )

                if provider_response.status_code == 200:
                    provider_data = provider_response.json()
                    provider_url = provider_data['endpoint_url'].rstrip('/')  # Remove trailing slash

                    print(f"   Provider: {provider_url}")
                    print(f"   Amount: {assignment['agreed_price_usdc']} USDC")

                    # Make payment and get data via x402
                    payment_result = self.x402_client.fetch_with_payment(
                        url=f"{provider_url}/deliver",
                        method="POST",
                    )

                    if payment_result.success:
                        print(f"   ✅ Payment successful!")
                        print(f"   📊 Transaction: {payment_result.transaction_signature}")
                        print(f"\n📦 DATA RECEIVED:")
                        print(f"   {json.dumps(payment_result.data, indent=6)}")
                        assignment['payment_tx'] = payment_result.transaction_signature
                        assignment['data_received'] = payment_result.data
                    else:
                        print(f"   ❌ Payment failed: {payment_result.error}")
                        assignment['payment_error'] = payment_result.error
                else:
                    print(f"   ⚠️  Could not get provider endpoint")
            else:
                # Mock payment
                print(f"\n💳 Payment Processing (MOCK - no wallet)...")
                print(f"   Amount: {assignment['agreed_price_usdc']} USDC")
                print(f"   Recipient: {assignment['provider_id']}")
                print(f"   ✅ Payment confirmed (mock)")

            return assignment
        else:
            raise Exception(f"Failed to select winner: {response.text}")

    def coordinate_task(
        self,
        task_type: TaskType,
        task_description: str,
        max_budget_usdc: float = 0.01,
        wait_for_bids_seconds: int = 5,
    ) -> Dict:
        """
        Complete workflow: Broadcast RFP → Wait for bids → Evaluate → Select winner
        """

        print(f"\n{'='*60}")
        print(f"  Coordinating Task")
        print(f"{'='*60}")
        print(f"  Type: {task_type.value}")
        print(f"  Description: {task_description}")
        print(f"  Budget: {max_budget_usdc} USDC")
        print(f"{'='*60}\n")

        # Step 1: Broadcast RFP
        rfp_id = self.broadcast_rfp(
            task_type=task_type,
            task_description=task_description,
            max_budget_usdc=max_budget_usdc,
            deadline_seconds=wait_for_bids_seconds,
        )

        # Step 2: Wait for bids
        import time
        print(f"\n⏳ Waiting {wait_for_bids_seconds}s for bids...")
        time.sleep(wait_for_bids_seconds)

        # Step 3: Get bids
        bids = self.get_bids(rfp_id)

        if not bids:
            print("❌ No bids received")
            return {
                "success": False,
                "error": "No bids received",
                "rfp_id": rfp_id,
            }

        print(f"\n📊 Received {len(bids)} bids")

        # Step 4: Evaluate with LLM
        try:
            selected_bid_id = self.evaluate_bids_with_llm(
                rfp_id=rfp_id,
                task_description=task_description,
                bids=bids,
            )
        except Exception as e:
            print(f"❌ Evaluation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "rfp_id": rfp_id,
            }

        # Step 5: Select winner
        try:
            assignment = self.select_winner(rfp_id, selected_bid_id)

            print(f"\n{'='*60}")
            print(f"  ✅ Task Coordinated Successfully")
            print(f"{'='*60}")
            print(f"  RFP: {rfp_id}")
            print(f"  Assignment: {assignment['assignment_id']}")
            print(f"  Winner: {assignment['provider_id']}")
            print(f"  Price: {assignment['agreed_price_usdc']} USDC")
            print(f"{'='*60}\n")

            return {
                "success": True,
                "rfp_id": rfp_id,
                "assignment": assignment,
                "total_bids": len(bids),
            }

        except Exception as e:
            print(f"❌ Winner selection failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "rfp_id": rfp_id,
            }

    def close(self):
        """Cleanup resources"""
        self.http_client.close()


if __name__ == "__main__":
    # Example: Coordinate a price data request
    orchestrator = OrchestratorAgent(
        agent_id="orchestrator_001",
    )

    try:
        result = orchestrator.coordinate_task(
            task_type=TaskType.PRICE_DATA,
            task_description="Get real-time SOL/USDC price data",
            max_budget_usdc=0.001,
            wait_for_bids_seconds=10,
        )

        print(f"\n📋 Final Result:")
        print(json.dumps(result, indent=2))

    finally:
        orchestrator.close()
