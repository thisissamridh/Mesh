"""
ConsumerMixin - AI-powered bid evaluation, payment, and rating capabilities
Any agent can inherit this mixin to become a consumer
"""

import httpx
import json
from typing import List, Dict, Optional
from openai import OpenAI
from dataclasses import dataclass

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from x402_client import X402Client, X402PaymentResponse


@dataclass
class BidDecision:
    """AI decision about a bid"""
    bid_id: str
    action: str  # "accept" or "reject"
    reasoning: str
    confidence: float  # 0-1


class ConsumerMixin:
    """
    Mixin that provides consumer capabilities to any agent:
    - AI-powered bid evaluation
    - Payment execution via x402
    - Provider rating

    Usage:
        class MyAgent(ConsumerMixin):
            def __init__(self, ...):
                super().__init__(...)
                self.setup_consumer(
                    openai_client=openai_client,
                    x402_client=x402_client,
                    registry_url=registry_url
                )
    """

    def setup_consumer(
        self,
        openai_client: OpenAI,
        x402_client: Optional[X402Client],
        registry_url: str,
        agent_id: str,
        model: str = "gpt-4o-2024-08-06",
    ):
        """Setup consumer capabilities"""
        self.openai_client = openai_client
        self.x402_client = x402_client
        self.registry_url = registry_url
        self.consumer_id = agent_id
        self.model = model
        self.http_client = httpx.Client(timeout=60.0)

    def evaluate_bids_with_ai(
        self,
        bids: List[Dict],
        task_description: str,
        evaluation_criteria: Optional[Dict] = None,
    ) -> List[BidDecision]:
        """
        Use AI to evaluate all bids and decide which to accept/reject

        Returns list of decisions sorted by preference
        """

        if not bids:
            return []

        print(f"\n🤖 AI Evaluating {len(bids)} bids...")

        # Default criteria
        criteria = evaluation_criteria or {
            "price_weight": 0.3,
            "quality_weight": 0.4,
            "speed_weight": 0.2,
            "reputation_weight": 0.1,
        }

        prompt = f"""
You are evaluating service provider bids for this task: "{task_description}"

Evaluation Criteria:
{json.dumps(criteria, indent=2)}

Bids received:
{json.dumps(bids, indent=2)}

For each bid, decide whether to ACCEPT or REJECT it, and explain your reasoning.
Consider:
1. Price vs quality tradeoff
2. Provider reputation and past performance
3. Speed/response time promises
4. Capability match with requirements

Return your decisions in JSON format:
{{
    "decisions": [
        {{
            "bid_id": "bid_xxx",
            "action": "accept" or "reject",
            "reasoning": "explanation",
            "confidence": 0.0-1.0
        }},
        ...
    ],
    "recommended_winner": "bid_xxx",
    "overall_analysis": "summary of your decision process"
}}

Be selective - only accept bids that truly meet the requirements at a fair price.
"""

        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert at evaluating service provider bids."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )

        llm_response = response.choices[0].message.content

        try:
            # Extract JSON
            if "```json" in llm_response:
                json_str = llm_response.split("```json")[1].split("```")[0].strip()
            elif "```" in llm_response:
                json_str = llm_response.split("```")[1].split("```")[0].strip()
            else:
                json_str = llm_response.strip()

            result = json.loads(json_str)

            print(f"\n📊 AI Decision:")
            print(f"   Recommended Winner: {result.get('recommended_winner', 'None')}")
            print(f"   Analysis: {result.get('overall_analysis', '')}")

            # Convert to BidDecision objects
            decisions = []
            for d in result.get("decisions", []):
                decision = BidDecision(
                    bid_id=d["bid_id"],
                    action=d["action"],
                    reasoning=d["reasoning"],
                    confidence=d.get("confidence", 0.5),
                )
                decisions.append(decision)

                # Print decision
                emoji = "✅" if decision.action == "accept" else "❌"
                print(f"   {emoji} {decision.bid_id}: {decision.action.upper()}")
                print(f"      Reasoning: {decision.reasoning}")

            return decisions

        except Exception as e:
            print(f"⚠️  Failed to parse AI response: {str(e)}")
            print(f"Raw response: {llm_response}")
            # Fallback: accept the first bid
            if bids:
                return [BidDecision(
                    bid_id=bids[0]["bid_id"],
                    action="accept",
                    reasoning="Fallback: AI parsing failed, accepting first bid",
                    confidence=0.3,
                )]
            return []

    def execute_payment_to_winner(
        self,
        provider_id: str,
        provider_url: str,
        amount_usdc: float,
    ) -> X402PaymentResponse:
        """
        Execute x402 payment to the winning provider
        """

        if not self.x402_client:
            print("⚠️  x402 client not available, cannot execute payment")
            return X402PaymentResponse(
                success=False,
                error="x402 client not configured",
            )

        print(f"\n💳 Executing Payment...")
        print(f"   Provider: {provider_id}")
        print(f"   Amount: {amount_usdc} USDC")
        print(f"   URL: {provider_url}")

        # Make payment and get data via x402
        payment_result = self.x402_client.fetch_with_payment(
            url=f"{provider_url.rstrip('/')}/deliver",
            method="POST",
        )

        if payment_result.success:
            print(f"   ✅ Payment successful!")
            print(f"   📊 Transaction: {payment_result.transaction_signature}")

            if payment_result.data:
                print(f"\n📦 DATA RECEIVED:")
                print(f"   {json.dumps(payment_result.data, indent=6)}")
        else:
            print(f"   ❌ Payment failed: {payment_result.error}")

        return payment_result

    def rate_provider_with_ai(
        self,
        provider_id: str,
        assignment_id: str,
        data_received: Dict,
        expected_quality: str = "high",
    ) -> bool:
        """
        Use AI to evaluate received data and submit rating
        """

        print(f"\n⭐ AI Evaluating Provider Performance...")

        prompt = f"""
You just received data/service from a provider. Evaluate their performance:

Data/Service Received:
{json.dumps(data_received, indent=2)}

Expected Quality: {expected_quality}

Rate the provider on these dimensions (1-5 stars each):
1. **Data Quality**: Accuracy, completeness, relevance
2. **Response Time**: How fast was delivery
3. **Value for Price**: Was it worth the cost

Also provide:
- Overall rating (1-5 stars)
- Review text (1-2 sentences)

Return JSON:
{{
    "rating": 4.5,
    "data_quality": 5.0,
    "response_time": 4.0,
    "value_for_price": 4.5,
    "review_text": "Excellent service, fast and accurate data"
}}
"""

        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert at evaluating service quality."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )

        llm_response = response.choices[0].message.content

        try:
            # Extract JSON
            if "```json" in llm_response:
                json_str = llm_response.split("```json")[1].split("```")[0].strip()
            elif "```" in llm_response:
                json_str = llm_response.split("```")[1].split("```")[0].strip()
            else:
                json_str = llm_response.strip()

            rating_data = json.loads(json_str)

            print(f"   Rating: {rating_data['rating']}★")
            print(f"   Review: {rating_data['review_text']}")

            # Submit rating to registry
            response = self.http_client.post(
                f"{self.registry_url}/agents/{provider_id}/rate",
                params={
                    "provider_id": provider_id,
                    "assignment_id": assignment_id,
                    "consumer_id": self.consumer_id,
                    "rating": rating_data["rating"],
                    "data_quality": rating_data["data_quality"],
                    "response_time": rating_data["response_time"],
                    "value_for_price": rating_data["value_for_price"],
                    "review_text": rating_data["review_text"],
                },
            )

            if response.status_code == 200:
                print(f"   ✅ Rating submitted successfully")
                return True
            else:
                print(f"   ❌ Rating submission failed: {response.text}")
                return False

        except Exception as e:
            print(f"⚠️  Failed to rate provider: {str(e)}")
            return False

    def request_service_from_marketplace(
        self,
        task_type: str,
        task_description: str,
        max_budget_usdc: float = 0.01,
        wait_for_bids_seconds: int = 10,
    ) -> Dict:
        """
        Complete consumer flow:
        1. Broadcast RFP to marketplace
        2. Wait for bids
        3. AI evaluates bids
        4. Pay winner
        5. Rate provider

        Returns result with data and transaction info
        """

        print(f"\n{'='*60}")
        print(f"  🛒 Requesting Service from Marketplace")
        print(f"{'='*60}")
        print(f"  Task: {task_type}")
        print(f"  Description: {task_description}")
        print(f"  Budget: {max_budget_usdc} USDC")
        print(f"{'='*60}\n")

        # Step 1: Broadcast RFP
        print(f"📢 Broadcasting RFP...")
        response = self.http_client.post(
            f"{self.registry_url}/rfp/create",
            params={
                "requester_id": self.consumer_id,
                "task_type": task_type,
                "task_description": task_description,
                "max_budget_usdc": max_budget_usdc,
                "deadline_seconds": wait_for_bids_seconds,
            },
            json={},
        )

        if response.status_code != 200:
            return {
                "success": False,
                "error": f"Failed to create RFP: {response.text}",
            }

        rfp_data = response.json()
        rfp_id = rfp_data["rfp_id"]
        print(f"✅ RFP Created: {rfp_id}")

        # Step 2: Wait for bids
        import time
        print(f"\n⏳ Waiting {wait_for_bids_seconds}s for bids...")
        time.sleep(wait_for_bids_seconds)

        # Step 3: Get bids
        response = self.http_client.get(f"{self.registry_url}/rfp/{rfp_id}/bids")
        if response.status_code != 200:
            return {
                "success": False,
                "error": "Failed to get bids",
                "rfp_id": rfp_id,
            }

        bids = response.json()

        if not bids:
            return {
                "success": False,
                "error": "No bids received",
                "rfp_id": rfp_id,
            }

        print(f"\n📊 Received {len(bids)} bids")

        # Step 4: AI evaluates bids
        decisions = self.evaluate_bids_with_ai(
            bids=bids,
            task_description=task_description,
        )

        # Find accepted bid
        accepted = [d for d in decisions if d.action == "accept"]
        if not accepted:
            return {
                "success": False,
                "error": "AI rejected all bids",
                "rfp_id": rfp_id,
                "bids": bids,
                "decisions": [d.__dict__ for d in decisions],
            }

        winner_decision = accepted[0]
        winner_bid = next(b for b in bids if b["bid_id"] == winner_decision.bid_id)

        print(f"\n✅ AI Selected Winner: {winner_bid['bidder_id']}")
        print(f"   Price: {winner_bid['price_usdc']} USDC")
        print(f"   Confidence: {winner_decision.confidence}")

        # Step 5: Select winner in registry
        response = self.http_client.post(
            f"{self.registry_url}/rfp/{rfp_id}/select",
            params={
                "rfp_id": rfp_id,
                "bid_id": winner_decision.bid_id,
            },
        )

        if response.status_code != 200:
            return {
                "success": False,
                "error": f"Failed to select winner: {response.text}",
            }

        assignment = response.json()

        # Step 6: Get provider endpoint
        provider_response = self.http_client.get(
            f"{self.registry_url}/agents/{assignment['provider_id']}"
        )

        if provider_response.status_code != 200:
            return {
                "success": False,
                "error": "Could not get provider endpoint",
            }

        provider_data = provider_response.json()
        provider_url = provider_data["endpoint_url"]

        # Step 7: Execute payment
        payment_result = self.execute_payment_to_winner(
            provider_id=assignment["provider_id"],
            provider_url=provider_url,
            amount_usdc=assignment["agreed_price_usdc"],
        )

        if not payment_result.success:
            return {
                "success": False,
                "error": payment_result.error,
                "assignment": assignment,
            }

        # Step 8: Rate provider
        if payment_result.data:
            self.rate_provider_with_ai(
                provider_id=assignment["provider_id"],
                assignment_id=assignment["assignment_id"],
                data_received=payment_result.data,
            )

        print(f"\n{'='*60}")
        print(f"  ✅ Service Request Completed")
        print(f"{'='*60}")
        print(f"  Provider: {assignment['provider_id']}")
        print(f"  Price: {assignment['agreed_price_usdc']} USDC")
        print(f"  Transaction: {payment_result.transaction_signature}")
        print(f"{'='*60}\n")

        return {
            "success": True,
            "rfp_id": rfp_id,
            "assignment": assignment,
            "payment_tx": payment_result.transaction_signature,
            "data": payment_result.data,
            "total_bids": len(bids),
            "ai_decisions": [d.__dict__ for d in decisions],
        }
