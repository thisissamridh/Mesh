"""
Agent Registry API - FastAPI service for agent discovery and registration
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional
from datetime import datetime
import uvicorn

from .schemas import (
    AgentRegistration,
    AgentInfo,
    AgentListResponse,
    AgentDiscoveryQuery,
    RegistrationResponse,
    ServiceType,
    AgentStatus,
)

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
    ProviderRating,
)
from .rfp_manager import RFPManager
import uuid

# Initialize FastAPI app
app = FastAPI(
    title="x402 Agent Registry",
    description="Decentralized registry for autonomous agent discovery and settlement",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (replace with database for production)
agents_db: Dict[str, AgentInfo] = {}

# Ratings storage: agent_id -> List of ratings
ratings_db: Dict[str, List[ProviderRating]] = {}

# RFP Manager
rfp_manager = RFPManager()


@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "service": "x402 Agent Registry",
        "status": "active",
        "agents_registered": len(agents_db),
    }


@app.post("/agents/register", response_model=RegistrationResponse)
def register_agent(registration: AgentRegistration):
    """Register a new agent in the registry"""

    # Check if agent already exists
    if registration.agent_id in agents_db:
        # Update existing agent
        existing = agents_db[registration.agent_id]
        agent_info = AgentInfo(
            **registration.model_dump(),
            status=existing.status,
            registered_at=existing.registered_at,
            last_seen=datetime.utcnow(),
            total_transactions=existing.total_transactions,
            reputation_score=existing.reputation_score,
            total_ratings=existing.total_ratings,
            average_rating=existing.average_rating,
        )
    else:
        # Create new agent
        agent_info = AgentInfo(
            **registration.model_dump(),
            status=AgentStatus.ACTIVE,
            registered_at=datetime.utcnow(),
            last_seen=datetime.utcnow(),
            total_transactions=0,
        )

    agents_db[registration.agent_id] = agent_info

    return RegistrationResponse(
        success=True,
        message=f"Agent '{registration.name}' registered successfully",
        agent_id=registration.agent_id,
    )


@app.get("/agents", response_model=AgentListResponse)
def discover_agents(
    service_type: Optional[ServiceType] = Query(None, description="Filter by service type"),
    max_price_usdc: Optional[float] = Query(None, ge=0, description="Maximum price in USDC"),
    capability_name: Optional[str] = Query(None, description="Search by capability name"),
    status: Optional[AgentStatus] = Query(AgentStatus.ACTIVE, description="Filter by status"),
):
    """Discover agents based on filters"""

    filtered_agents = list(agents_db.values())

    # Apply filters
    if service_type:
        filtered_agents = [a for a in filtered_agents if a.service_type == service_type]

    if status:
        filtered_agents = [a for a in filtered_agents if a.status == status]

    if max_price_usdc is not None:
        filtered_agents = [
            a for a in filtered_agents
            if any(cap.price_usdc <= max_price_usdc for cap in a.capabilities)
        ]

    if capability_name:
        filtered_agents = [
            a for a in filtered_agents
            if any(capability_name.lower() in cap.name.lower() for cap in a.capabilities)
        ]

    return AgentListResponse(
        agents=filtered_agents,
        count=len(filtered_agents),
    )


@app.get("/agents/{agent_id}", response_model=AgentInfo)
def get_agent(agent_id: str):
    """Get detailed information about a specific agent"""

    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    return agents_db[agent_id]


@app.delete("/agents/{agent_id}")
def unregister_agent(agent_id: str):
    """Unregister an agent from the registry"""

    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    del agents_db[agent_id]

    return {
        "success": True,
        "message": f"Agent '{agent_id}' unregistered successfully",
    }


@app.patch("/agents/{agent_id}/status")
def update_agent_status(agent_id: str, status: AgentStatus):
    """Update agent status (active/inactive/maintenance)"""

    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    agents_db[agent_id].status = status
    agents_db[agent_id].last_seen = datetime.utcnow()

    return {
        "success": True,
        "agent_id": agent_id,
        "status": status,
    }


@app.post("/agents/{agent_id}/transaction")
def record_transaction(agent_id: str):
    """Record a completed transaction for an agent (increments counter)"""

    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    agents_db[agent_id].total_transactions += 1
    agents_db[agent_id].last_seen = datetime.utcnow()

    return {
        "success": True,
        "agent_id": agent_id,
        "total_transactions": agents_db[agent_id].total_transactions,
    }


# ========== RFP Endpoints ==========

@app.post("/rfp/create", response_model=RequestForProposal)
def create_rfp(
    requester_id: str,
    task_type: TaskType,
    task_description: str,
    requirements: Optional[Dict] = None,
    max_budget_usdc: Optional[float] = None,
    deadline_seconds: Optional[int] = None,
):
    """Create a new Request for Proposal"""

    rfp = rfp_manager.create_rfp(
        requester_id=requester_id,
        task_type=task_type,
        task_description=task_description,
        requirements=requirements,
        max_budget_usdc=max_budget_usdc,
        deadline_seconds=deadline_seconds,
    )

    return rfp


@app.get("/rfp/open")
def get_open_rfps(
    task_type: Optional[TaskType] = None,
    max_budget: Optional[float] = None,
):
    """Get all open RFPs"""

    rfps = rfp_manager.get_open_rfps(task_type=task_type, max_budget=max_budget)
    return {"rfps": rfps, "count": len(rfps)}


@app.get("/rfp/{rfp_id}", response_model=RequestForProposal)
def get_rfp(rfp_id: str):
    """Get RFP by ID"""

    rfp = rfp_manager.get_rfp(rfp_id)
    if not rfp:
        raise HTTPException(status_code=404, detail=f"RFP '{rfp_id}' not found")

    return rfp


@app.post("/rfp/{rfp_id}/bid", response_model=Bid)
def submit_bid(
    rfp_id: str,
    bidder_id: str,
    bidder_name: str,
    price_usdc: float,
    estimated_completion_time_ms: Optional[int] = None,
    capabilities_summary: str = "",
    reputation_score: Optional[float] = None,
    metadata: Optional[Dict] = None,
):
    """Submit a bid for an RFP"""

    try:
        bid = rfp_manager.submit_bid(
            rfp_id=rfp_id,
            bidder_id=bidder_id,
            bidder_name=bidder_name,
            price_usdc=price_usdc,
            estimated_completion_time_ms=estimated_completion_time_ms,
            capabilities_summary=capabilities_summary,
            reputation_score=reputation_score,
            metadata=metadata,
        )
        return bid
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/rfp/{rfp_id}/bids", response_model=List[Bid])
def get_bids(rfp_id: str):
    """Get all bids for an RFP"""

    return rfp_manager.get_bids(rfp_id)


@app.get("/rfp/{rfp_id}/evaluate", response_model=List[BidEvaluation])
def evaluate_bids(
    rfp_id: str,
    price_weight: float = 0.4,
    speed_weight: float = 0.3,
    reputation_weight: float = 0.3,
):
    """Evaluate all bids for an RFP"""

    return rfp_manager.evaluate_bids(
        rfp_id=rfp_id,
        price_weight=price_weight,
        speed_weight=speed_weight,
        reputation_weight=reputation_weight,
    )


@app.post("/rfp/{rfp_id}/select", response_model=TaskAssignment)
def select_winner(rfp_id: str, bid_id: str):
    """Select winning bid and create task assignment"""

    try:
        assignment = rfp_manager.select_winning_bid(rfp_id=rfp_id, bid_id=bid_id)
        return assignment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/rfp/{rfp_id}/negotiate", response_model=NegotiationMessage)
def send_negotiation(
    rfp_id: str,
    from_agent: str,
    to_agent: str,
    message_type: str,
    content: str,
    metadata: Optional[Dict] = None,
):
    """Send a negotiation message"""

    return rfp_manager.send_negotiation_message(
        from_agent=from_agent,
        to_agent=to_agent,
        rfp_id=rfp_id,
        message_type=message_type,
        content=content,
        metadata=metadata,
    )


@app.get("/rfp/{rfp_id}/negotiations", response_model=List[NegotiationMessage])
def get_negotiations(rfp_id: str):
    """Get all negotiation messages for an RFP"""

    return rfp_manager.get_negotiations(rfp_id)


@app.post("/agents/{agent_id}/subscribe")
def subscribe_to_rfps(agent_id: str, task_types: List[TaskType]):
    """Agent subscribes to receive RFPs for specific task types"""

    rfp_manager.subscribe_to_tasks(agent_id, task_types)

    return {
        "success": True,
        "agent_id": agent_id,
        "subscribed_to": [t.value for t in task_types],
    }


@app.get("/rfp/stats")
def get_rfp_stats():
    """Get RFP manager statistics"""

    return rfp_manager.get_stats()


# ==================== REPUTATION & RATING ENDPOINTS ====================

@app.post("/agents/{provider_id}/rate", response_model=ProviderRating)
def rate_provider(
    provider_id: str,
    assignment_id: str,
    consumer_id: str,
    rating: float = Query(..., ge=1.0, le=5.0),
    data_quality: float = Query(..., ge=1.0, le=5.0),
    response_time: float = Query(..., ge=1.0, le=5.0),
    value_for_price: float = Query(..., ge=1.0, le=5.0),
    review_text: Optional[str] = None,
):
    """
    Submit a rating for a provider after task completion
    """

    # Verify provider exists
    if provider_id not in agents_db:
        raise HTTPException(status_code=404, detail=f"Provider {provider_id} not found")

    # Create rating
    rating_obj = ProviderRating(
        rating_id=f"rating_{uuid.uuid4().hex[:8]}",
        assignment_id=assignment_id,
        consumer_id=consumer_id,
        provider_id=provider_id,
        rating=rating,
        data_quality=data_quality,
        response_time=response_time,
        value_for_price=value_for_price,
        review_text=review_text,
        timestamp=datetime.utcnow(),
    )

    # Store rating
    if provider_id not in ratings_db:
        ratings_db[provider_id] = []
    ratings_db[provider_id].append(rating_obj)

    # Update provider reputation
    provider = agents_db[provider_id]
    all_ratings = ratings_db[provider_id]

    # Calculate new average rating
    total_rating = sum(r.rating for r in all_ratings)
    provider.average_rating = total_rating / len(all_ratings)
    provider.total_ratings = len(all_ratings)

    # Calculate reputation score (weighted combination)
    # 60% average rating (normalized to 0-1), 40% based on number of ratings
    rating_component = provider.average_rating / 5.0  # Normalize to 0-1
    volume_component = min(provider.total_ratings / 100.0, 1.0)  # Cap at 100 ratings
    provider.reputation_score = (rating_component * 0.6) + (volume_component * 0.4)

    agents_db[provider_id] = provider

    return rating_obj


@app.get("/agents/{provider_id}/ratings")
def get_provider_ratings(provider_id: str, limit: int = 10):
    """
    Get recent ratings for a provider
    """

    if provider_id not in agents_db:
        raise HTTPException(status_code=404, detail=f"Provider {provider_id} not found")

    ratings = ratings_db.get(provider_id, [])

    # Sort by timestamp descending
    sorted_ratings = sorted(ratings, key=lambda r: r.timestamp, reverse=True)

    return {
        "provider_id": provider_id,
        "total_ratings": len(ratings),
        "average_rating": agents_db[provider_id].average_rating,
        "reputation_score": agents_db[provider_id].reputation_score,
        "recent_ratings": [r.model_dump() for r in sorted_ratings[:limit]],
    }


@app.get("/agents/{provider_id}/reputation")
def get_provider_reputation(provider_id: str):
    """
    Get reputation summary for a provider
    """

    if provider_id not in agents_db:
        raise HTTPException(status_code=404, detail=f"Provider {provider_id} not found")

    provider = agents_db[provider_id]
    ratings = ratings_db.get(provider_id, [])

    # Calculate breakdown
    if ratings:
        avg_data_quality = sum(r.data_quality for r in ratings) / len(ratings)
        avg_response_time = sum(r.response_time for r in ratings) / len(ratings)
        avg_value = sum(r.value_for_price for r in ratings) / len(ratings)
    else:
        avg_data_quality = avg_response_time = avg_value = 0.0

    return {
        "provider_id": provider_id,
        "provider_name": provider.name,
        "reputation_score": provider.reputation_score,
        "total_ratings": provider.total_ratings,
        "average_rating": provider.average_rating,
        "breakdown": {
            "data_quality": avg_data_quality,
            "response_time": avg_response_time,
            "value_for_price": avg_value,
        },
        "total_transactions": provider.total_transactions,
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
