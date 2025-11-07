"""
Negotiation Protocol Schemas - RFP, Bidding, and Agent-to-Agent Communication
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class TaskType(str, Enum):
    """Types of tasks agents can perform"""
    PRICE_DATA = "price_data"
    SWAP_SIMULATION = "swap_simulation"
    SWAP_EXECUTION = "swap_execution"
    ANALYTICS = "analytics"
    ORACLE_DATA = "oracle_data"
    CUSTOM = "custom"


class RFPStatus(str, Enum):
    """RFP lifecycle status"""
    OPEN = "open"
    CLOSED = "closed"
    ACCEPTED = "accepted"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RequestForProposal(BaseModel):
    """
    RFP sent by an agent looking for services
    Example: "Who can simulate this swap path?"
    """
    rfp_id: str = Field(..., description="Unique RFP identifier")
    requester_id: str = Field(..., description="Agent requesting service")
    task_type: TaskType = Field(..., description="Type of task needed")
    task_description: str = Field(..., description="Detailed task description")
    requirements: Dict[str, Any] = Field(
        default_factory=dict,
        description="Specific requirements (e.g., response time, accuracy)"
    )
    max_budget_usdc: Optional[float] = Field(None, description="Maximum willing to pay")
    deadline: Optional[datetime] = Field(None, description="When response is needed")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: RFPStatus = Field(default=RFPStatus.OPEN)

    class Config:
        json_schema_extra = {
            "example": {
                "rfp_id": "rfp_001",
                "requester_id": "finder_agent_001",
                "task_type": "swap_simulation",
                "task_description": "Simulate SOL->USDC swap for 10 SOL, need slippage estimate",
                "requirements": {
                    "response_time_ms": 1000,
                    "accuracy": "high"
                },
                "max_budget_usdc": 0.001,
                "deadline": "2025-11-07T12:00:00Z"
            }
        }


class Bid(BaseModel):
    """
    Bid submitted by an agent in response to RFP
    """
    bid_id: str = Field(..., description="Unique bid identifier")
    rfp_id: str = Field(..., description="RFP this bid responds to")
    bidder_id: str = Field(..., description="Agent submitting bid")
    bidder_name: str = Field(..., description="Agent's display name")
    price_usdc: float = Field(..., description="Price in USDC", ge=0)
    estimated_completion_time_ms: Optional[int] = Field(
        None,
        description="Estimated time to complete in milliseconds"
    )
    capabilities_summary: str = Field(..., description="Why this agent is qualified")
    reputation_score: Optional[float] = Field(None, description="Agent's reputation (0-1)")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional bid details"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "bid_id": "bid_001",
                "rfp_id": "rfp_001",
                "bidder_id": "simulator_agent_001",
                "bidder_name": "Jupiter Swap Simulator",
                "price_usdc": 0.0005,
                "estimated_completion_time_ms": 500,
                "capabilities_summary": "Uses Jupiter API with 99.9% accuracy, 1000+ simulations completed",
                "reputation_score": 0.98,
                "metadata": {
                    "total_transactions": 1523,
                    "success_rate": 0.99
                }
            }
        }


class BidEvaluation(BaseModel):
    """
    Evaluation criteria for selecting winning bid
    """
    bid_id: str
    score: float = Field(..., description="Overall score (0-1)")
    price_score: float = Field(..., description="Price competitiveness (0-1)")
    speed_score: float = Field(..., description="Speed score (0-1)")
    reputation_score: float = Field(..., description="Reputation score (0-1)")
    selected: bool = Field(default=False)


class NegotiationMessage(BaseModel):
    """
    Message exchanged during negotiation
    """
    message_id: str
    from_agent: str
    to_agent: str
    rfp_id: str
    message_type: str = Field(..., description="question, counter_offer, acceptance, rejection")
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "message_id": "msg_001",
                "from_agent": "finder_agent_001",
                "to_agent": "simulator_agent_001",
                "rfp_id": "rfp_001",
                "message_type": "counter_offer",
                "content": "Can you do it for 0.0003 USDC if I provide liquidity data?",
                "metadata": {"urgency": "high"}
            }
        }


class TaskAssignment(BaseModel):
    """
    Final assignment after bid acceptance
    """
    assignment_id: str
    rfp_id: str
    winning_bid_id: str
    requester_id: str
    provider_id: str
    agreed_price_usdc: float
    task_description: str
    payment_escrow: Optional[str] = Field(None, description="Escrow transaction if used")
    status: str = Field(default="assigned", description="assigned, in_progress, completed, failed")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "assignment_id": "assign_001",
                "rfp_id": "rfp_001",
                "winning_bid_id": "bid_001",
                "requester_id": "finder_agent_001",
                "provider_id": "simulator_agent_001",
                "agreed_price_usdc": 0.0005,
                "task_description": "Simulate SOL->USDC swap",
                "status": "assigned"
            }
        }


class ProviderRating(BaseModel):
    """
    Rating/review given by consumer to provider after task completion
    """
    rating_id: str
    assignment_id: str
    consumer_id: str
    provider_id: str
    rating: float = Field(..., ge=1.0, le=5.0, description="Rating 1-5 stars")
    review_text: Optional[str] = Field(None, description="Optional review text")
    data_quality: float = Field(..., ge=1.0, le=5.0, description="Quality of data/service")
    response_time: float = Field(..., ge=1.0, le=5.0, description="Speed of delivery")
    value_for_price: float = Field(..., ge=1.0, le=5.0, description="Value vs price paid")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "rating_id": "rating_001",
                "assignment_id": "assign_001",
                "consumer_id": "orchestrator_001",
                "provider_id": "data_provider_001",
                "rating": 4.5,
                "review_text": "Fast and accurate price data",
                "data_quality": 5.0,
                "response_time": 5.0,
                "value_for_price": 4.0,
            }
        }


class AgentCapabilitySchema(BaseModel):
    """
    Detailed capability schema that agents advertise
    """
    capability_id: str
    name: str
    description: str
    task_type: TaskType
    input_schema: Dict[str, Any] = Field(..., description="JSON schema for inputs")
    output_schema: Dict[str, Any] = Field(..., description="JSON schema for outputs")
    pricing: Dict[str, Any] = Field(
        ...,
        description="Pricing structure (base_price, per_unit, etc.)"
    )
    performance_metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="avg_response_time_ms, success_rate, etc."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "capability_id": "cap_sol_usdc_price",
                "name": "SOL/USDC Real-time Price",
                "description": "Provides real-time SOL to USDC price with sub-second latency",
                "task_type": "price_data",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "enum": ["SOL/USDC"]}
                    }
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "price": {"type": "number"},
                        "timestamp": {"type": "string"},
                        "confidence": {"type": "number"}
                    }
                },
                "pricing": {
                    "base_price_usdc": 0.0001,
                    "bulk_discount": {"over_100": 0.00008}
                },
                "performance_metrics": {
                    "avg_response_time_ms": 250,
                    "success_rate": 0.999,
                    "uptime": 0.9995
                }
            }
        }
