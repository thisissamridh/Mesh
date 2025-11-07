"""
RFP Manager - Handles Request for Proposals, Bidding, and Negotiation
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import uuid
from collections import defaultdict

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from shared.schemas.negotiation import (
    RequestForProposal,
    Bid,
    BidEvaluation,
    NegotiationMessage,
    TaskAssignment,
    TaskType,
    RFPStatus,
)


class RFPManager:
    """
    Manages the RFP lifecycle:
    1. Agents broadcast RFPs
    2. Other agents submit bids
    3. Requester evaluates and selects winner
    4. Negotiation if needed
    5. Task assignment
    """

    def __init__(self):
        # Storage
        self.rfps: Dict[str, RequestForProposal] = {}
        self.bids: Dict[str, List[Bid]] = defaultdict(list)  # rfp_id -> [bids]
        self.negotiations: Dict[str, List[NegotiationMessage]] = defaultdict(list)
        self.assignments: Dict[str, TaskAssignment] = {}

        # Subscriptions: which agents want to receive which types of RFPs
        self.agent_subscriptions: Dict[str, List[TaskType]] = defaultdict(list)

    # ========== RFP Management ==========

    def create_rfp(
        self,
        requester_id: str,
        task_type: TaskType,
        task_description: str,
        requirements: Dict = None,
        max_budget_usdc: Optional[float] = None,
        deadline_seconds: Optional[int] = None,
    ) -> RequestForProposal:
        """Create and broadcast a new RFP"""

        rfp_id = f"rfp_{uuid.uuid4().hex[:8]}"

        deadline = None
        if deadline_seconds:
            deadline = datetime.utcnow() + timedelta(seconds=deadline_seconds)

        rfp = RequestForProposal(
            rfp_id=rfp_id,
            requester_id=requester_id,
            task_type=task_type,
            task_description=task_description,
            requirements=requirements or {},
            max_budget_usdc=max_budget_usdc,
            deadline=deadline,
            created_at=datetime.utcnow(),
            status=RFPStatus.OPEN,
        )

        self.rfps[rfp_id] = rfp

        print(f"📢 RFP Broadcast: {rfp_id}")
        print(f"   Task: {task_type.value}")
        print(f"   Requester: {requester_id}")
        print(f"   Budget: {max_budget_usdc} USDC")

        return rfp

    def get_rfp(self, rfp_id: str) -> Optional[RequestForProposal]:
        """Get RFP by ID"""
        return self.rfps.get(rfp_id)

    def get_open_rfps(
        self,
        task_type: Optional[TaskType] = None,
        max_budget: Optional[float] = None,
    ) -> List[RequestForProposal]:
        """Get all open RFPs, optionally filtered"""

        rfps = [rfp for rfp in self.rfps.values() if rfp.status == RFPStatus.OPEN]

        if task_type:
            rfps = [rfp for rfp in rfps if rfp.task_type == task_type]

        if max_budget:
            rfps = [
                rfp for rfp in rfps
                if rfp.max_budget_usdc and rfp.max_budget_usdc <= max_budget
            ]

        return rfps

    # ========== Bidding ==========

    def submit_bid(
        self,
        rfp_id: str,
        bidder_id: str,
        bidder_name: str,
        price_usdc: float,
        estimated_completion_time_ms: Optional[int],
        capabilities_summary: str,
        reputation_score: Optional[float] = None,
        metadata: Dict = None,
    ) -> Bid:
        """Agent submits a bid for an RFP"""

        rfp = self.get_rfp(rfp_id)
        if not rfp:
            raise ValueError(f"RFP {rfp_id} not found")

        if rfp.status != RFPStatus.OPEN:
            raise ValueError(f"RFP {rfp_id} is not open for bids")

        bid_id = f"bid_{uuid.uuid4().hex[:8]}"

        bid = Bid(
            bid_id=bid_id,
            rfp_id=rfp_id,
            bidder_id=bidder_id,
            bidder_name=bidder_name,
            price_usdc=price_usdc,
            estimated_completion_time_ms=estimated_completion_time_ms,
            capabilities_summary=capabilities_summary,
            reputation_score=reputation_score,
            metadata=metadata or {},
            created_at=datetime.utcnow(),
        )

        self.bids[rfp_id].append(bid)

        print(f"💰 Bid Submitted: {bid_id}")
        print(f"   RFP: {rfp_id}")
        print(f"   Bidder: {bidder_name}")
        print(f"   Price: {price_usdc} USDC")

        return bid

    def get_bids(self, rfp_id: str) -> List[Bid]:
        """Get all bids for an RFP"""
        return self.bids.get(rfp_id, [])

    # ========== Bid Evaluation ==========

    def evaluate_bids(
        self,
        rfp_id: str,
        price_weight: float = 0.4,
        speed_weight: float = 0.3,
        reputation_weight: float = 0.3,
    ) -> List[BidEvaluation]:
        """
        Evaluate bids based on price, speed, and reputation
        Returns sorted evaluations (best first)
        """

        bids = self.get_bids(rfp_id)
        if not bids:
            return []

        evaluations = []

        # Normalize scores
        prices = [b.price_usdc for b in bids]
        speeds = [b.estimated_completion_time_ms or 1000 for b in bids]
        reputations = [b.reputation_score or 0.5 for b in bids]

        min_price = min(prices)
        max_speed = max(speeds)

        for bid in bids:
            # Price score: lower is better (inverse)
            price_score = min_price / bid.price_usdc if bid.price_usdc > 0 else 0

            # Speed score: faster is better (inverse)
            speed_ms = bid.estimated_completion_time_ms or 1000
            speed_score = max_speed / speed_ms if speed_ms > 0 else 0

            # Reputation score: as-is
            reputation_score = bid.reputation_score or 0.5

            # Overall score
            overall_score = (
                price_score * price_weight +
                speed_score * speed_weight +
                reputation_score * reputation_weight
            )

            evaluation = BidEvaluation(
                bid_id=bid.bid_id,
                score=overall_score,
                price_score=price_score,
                speed_score=speed_score,
                reputation_score=reputation_score,
                selected=False,
            )

            evaluations.append(evaluation)

        # Sort by overall score (descending)
        evaluations.sort(key=lambda e: e.score, reverse=True)

        return evaluations

    def select_winning_bid(
        self,
        rfp_id: str,
        bid_id: str,
    ) -> TaskAssignment:
        """
        Select a winning bid and create task assignment
        """

        rfp = self.get_rfp(rfp_id)
        if not rfp:
            raise ValueError(f"RFP {rfp_id} not found")

        # Find the bid
        bid = None
        for b in self.bids[rfp_id]:
            if b.bid_id == bid_id:
                bid = b
                break

        if not bid:
            raise ValueError(f"Bid {bid_id} not found")

        # Update RFP status
        rfp.status = RFPStatus.ACCEPTED

        # Create assignment
        assignment_id = f"assign_{uuid.uuid4().hex[:8]}"

        assignment = TaskAssignment(
            assignment_id=assignment_id,
            rfp_id=rfp_id,
            winning_bid_id=bid_id,
            requester_id=rfp.requester_id,
            provider_id=bid.bidder_id,
            agreed_price_usdc=bid.price_usdc,
            task_description=rfp.task_description,
            status="assigned",
            created_at=datetime.utcnow(),
        )

        self.assignments[assignment_id] = assignment

        print(f"✅ Task Assigned: {assignment_id}")
        print(f"   Winner: {bid.bidder_name}")
        print(f"   Price: {bid.price_usdc} USDC")

        return assignment

    # ========== Negotiation ==========

    def send_negotiation_message(
        self,
        from_agent: str,
        to_agent: str,
        rfp_id: str,
        message_type: str,
        content: str,
        metadata: Dict = None,
    ) -> NegotiationMessage:
        """Send a negotiation message between agents"""

        message_id = f"msg_{uuid.uuid4().hex[:8]}"

        message = NegotiationMessage(
            message_id=message_id,
            from_agent=from_agent,
            to_agent=to_agent,
            rfp_id=rfp_id,
            message_type=message_type,
            content=content,
            metadata=metadata or {},
            created_at=datetime.utcnow(),
        )

        self.negotiations[rfp_id].append(message)

        print(f"💬 Negotiation: {from_agent} → {to_agent}")
        print(f"   Type: {message_type}")
        print(f"   Content: {content}")

        return message

    def get_negotiations(self, rfp_id: str) -> List[NegotiationMessage]:
        """Get all negotiation messages for an RFP"""
        return self.negotiations.get(rfp_id, [])

    # ========== Agent Subscriptions ==========

    def subscribe_to_tasks(self, agent_id: str, task_types: List[TaskType]):
        """Agent subscribes to receive RFPs for specific task types"""
        self.agent_subscriptions[agent_id] = task_types
        print(f"📮 {agent_id} subscribed to: {[t.value for t in task_types]}")

    def get_subscribers(self, task_type: TaskType) -> List[str]:
        """Get agents subscribed to a task type"""
        return [
            agent_id
            for agent_id, types in self.agent_subscriptions.items()
            if task_type in types
        ]

    # ========== Statistics ==========

    def get_stats(self) -> Dict:
        """Get RFP manager statistics"""
        return {
            "total_rfps": len(self.rfps),
            "open_rfps": len([r for r in self.rfps.values() if r.status == RFPStatus.OPEN]),
            "total_bids": sum(len(bids) for bids in self.bids.values()),
            "total_assignments": len(self.assignments),
            "active_agents": len(self.agent_subscriptions),
        }
