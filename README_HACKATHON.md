# Self-Negotiating Agent Mesh 🤖🤝

**Solana x402 Hackathon Project - AI Agents that Discover, Bid & Negotiate**

## What It Does

Agents use **OpenAI GPT-4** to:
- 📢 Broadcast RFPs for tasks they need
- 💰 Autonomously bid on tasks they can do
- 🧠 Evaluate bids intelligently
- 🤝 Negotiate prices
- 💳 Pay via x402 on Solana

## Architecture

```
OrchestratorAgent (needs price data)
    ↓ broadcasts RFP
Registry (collects bids)
    ↓ notifies
BiddingAgents (AI decides to bid)
    ↓ submit bids
OrchestratorAgent (AI evaluates)
    ↓ selects winner
TaskAssignment + x402 Payment
```

## Quick Start

### 1. Install
```bash
pip install fastapi uvicorn httpx openai pydantic solders
```

### 2. Configure .env
```bash
OPENAI_API_KEY=sk-proj-YOUR_KEY
OPENAI_MODEL=gpt-4o-2024-08-06
```

### 3. Run (3 terminals)
```bash
# Terminal 1: Registry
cd registry/src && python main.py

# Terminal 2: Bidding Agent
cd agents/src && python bidding_data_provider.py

# Terminal 3: Demo
python demo_negotiation.py
```

## Key Files

| File | Purpose |
|------|---------|
| `shared/schemas/negotiation.py` | RFP/Bid/Assignment schemas |
| `shared/schemas/prompts.py` | AI system prompts |
| `registry/src/rfp_manager.py` | RFP coordination |
| `agents/src/orchestrator_agent.py` | AI task coordinator |
| `agents/src/bidding_data_provider.py` | AI bidding agent |

## AI Decision Flow

**Agent sees RFP** → AI analyzes task → AI decides bid price → Submits bid

**Orchestrator gets bids** → AI evaluates all bids → Selects winner → Assigns task

## Example AI Decisions

```json
// Agent decides to bid
{"should_bid": true, "reasoning": "Task matches capability, budget 10x cost"}

// Agent prices bid
{"bid_price_usdc": 0.00008, "reasoning": "Undercut competitors, maintain 80% margin"}

// Orchestrator selects
{"selected_bid_id": "bid_123", "reasoning": "Best price + reputation"}
```

## x402 Integration

Agents serve paid APIs with HTTP 402:
```python
if not payment:
    return 402 {"recipient": wallet, "amount": "0.0001 USDC"}
return price_data
```

## Hackathon Track

**Best Trustless Agent** ✅
- Autonomous discovery
- Reputation system
- AI-powered validation
- Decentralized coordination

## Innovation

First agent mesh using **AI for negotiations** - not hardcoded rules!

---

Built for Solana x402 Hackathon | Nov 2025
