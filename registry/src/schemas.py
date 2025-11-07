"""
Agent Registry Schemas - Pydantic models for agent registration and discovery
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ServiceType(str, Enum):
    """Types of services agents can offer"""
    DATA_PROVIDER = "data_provider"
    PRICE_ORACLE = "price_oracle"
    SWAP_EXECUTOR = "swap_executor"
    ANALYTICS = "analytics"
    SIMULATOR = "simulator"
    CUSTOM = "custom"


class AgentStatus(str, Enum):
    """Agent availability status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


class AgentCapability(BaseModel):
    """Specific capability an agent offers"""
    name: str = Field(..., description="Capability name (e.g., 'SOL/USDC price')")
    description: str = Field(..., description="What this capability does")
    price_usdc: float = Field(..., description="Price in USDC", ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "SOL/USDC Price",
                "description": "Real-time SOL to USDC price from Pyth/Jupiter",
                "price_usdc": 0.0001
            }
        }


class AgentRegistration(BaseModel):
    """Agent registration request"""
    agent_id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Human-readable agent name")
    service_type: ServiceType
    wallet_address: str = Field(..., description="Solana wallet address for payments")
    endpoint_url: HttpUrl = Field(..., description="Agent's API endpoint")
    capabilities: List[AgentCapability] = Field(..., description="List of services offered")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional info")

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "data_provider_001",
                "name": "Pyth Price Provider",
                "service_type": "data_provider",
                "wallet_address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
                "endpoint_url": "http://localhost:5000",
                "capabilities": [
                    {
                        "name": "SOL/USDC Price",
                        "description": "Real-time price",
                        "price_usdc": 0.0001
                    }
                ],
                "metadata": {
                    "version": "1.0.0",
                    "update_frequency": "1s"
                }
            }
        }


class AgentInfo(AgentRegistration):
    """Agent information with registration metadata"""
    status: AgentStatus = Field(default=AgentStatus.ACTIVE)
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    total_transactions: int = Field(default=0)
    reputation_score: float = Field(default=0.95, ge=0.0, le=1.0, description="Reputation score 0-1")
    total_ratings: int = Field(default=0, description="Total number of ratings received")
    average_rating: float = Field(default=0.0, ge=0.0, le=5.0, description="Average rating 0-5 stars")

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "data_provider_001",
                "name": "Pyth Price Provider",
                "service_type": "data_provider",
                "wallet_address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
                "endpoint_url": "http://localhost:5000",
                "capabilities": [
                    {
                        "name": "SOL/USDC Price",
                        "description": "Real-time price",
                        "price_usdc": 0.0001
                    }
                ],
                "status": "active",
                "registered_at": "2025-11-07T10:00:00",
                "last_seen": "2025-11-07T10:30:00",
                "total_transactions": 42
            }
        }


class AgentDiscoveryQuery(BaseModel):
    """Query for discovering agents"""
    service_type: Optional[ServiceType] = None
    max_price_usdc: Optional[float] = Field(None, ge=0)
    capability_name: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "service_type": "data_provider",
                "max_price_usdc": 0.001,
                "capability_name": "price"
            }
        }


class AgentListResponse(BaseModel):
    """Response containing list of agents"""
    agents: List[AgentInfo]
    count: int

    class Config:
        json_schema_extra = {
            "example": {
                "count": 1,
                "agents": [
                    {
                        "agent_id": "data_provider_001",
                        "name": "Pyth Price Provider",
                        "service_type": "data_provider",
                        "wallet_address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
                        "endpoint_url": "http://localhost:5000",
                        "capabilities": [
                            {
                                "name": "SOL/USDC Price",
                                "description": "Real-time price",
                                "price_usdc": 0.0001
                            }
                        ],
                        "status": "active",
                        "registered_at": "2025-11-07T10:00:00",
                        "last_seen": "2025-11-07T10:30:00",
                        "total_transactions": 42
                    }
                ]
            }
        }


class RegistrationResponse(BaseModel):
    """Response after successful registration"""
    success: bool
    message: str
    agent_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Agent registered successfully",
                "agent_id": "data_provider_001"
            }
        }
