# 🤖 Consumer AI Decision-Making Demo

## Overview

This demo shows **AI agents making autonomous marketplace decisions**:
- AI evaluates competing provider bids
- AI decides which provider to pay
- AI rates providers after receiving service

## New Architecture

### Old Way (Orchestrator decides):
```
User → Orchestrator → Evaluates bids → Pays → Rates
```

### New Way (Each agent decides):
```
Portfolio Agent needs data
  ↓
Broadcasts RFP to registry
  ↓
2 Data Providers compete with bids
  ↓
Portfolio Agent's AI evaluates both bids
  ↓
AI chooses best provider
  ↓
Portfolio Agent pays winner via x402
  ↓
AI rates provider's service
```

## Running the Demo

### Terminal 1: Registry
```bash
./run_registry.sh
```

### Terminal 2: Facilitator
```bash
./run_facilitator.sh
```

### Terminal 3: Data Provider 1 (Premium)
```bash
./run_bidding_agent.sh
```
- Price: 0.00015 USDC
- Strategy: Quality over price

### Terminal 4: Data Provider 2 (Budget)
```bash
./run_provider_002.sh
```
- Price: 0.00012 USDC
- Strategy: Speed and low price

### Terminal 5: Portfolio Manager (Consumer with AI)
```bash
./run_portfolio_manager.sh
```

## What Happens

### Step 1: RFP Broadcast
```
Portfolio Manager: "I need SOL/USDC price data"
Registry: Routes to 2 data providers
```

### Step 2: Competing Bids
```
Provider 1: "0.00015 USDC, high quality, 4.8★ rated"
Provider 2: "0.00012 USDC, fast delivery, new provider"
```

### Step 3: AI Evaluation
```
Portfolio Manager's AI analyzes:
- Price difference: 20% cheaper for Provider 2
- Reputation: Provider 1 has better rating
- Speed: Provider 2 promises faster
- Quality: Provider 1 emphasizes accuracy

AI Decision: "Accept Provider 1 - better reputation
worth the extra cost for portfolio decisions"
```

### Step 4: Payment
```
Portfolio Manager → x402 payment → Provider 1
Transaction confirmed on Solana devnet
```

### Step 5: AI Rating
```
Portfolio Manager's AI evaluates received data:
- Data quality: 5★
- Response time: 4★
- Value for price: 4.5★

Submits rating to registry
Provider 1's reputation increases
```

## Key Features

### ConsumerMixin
- Any agent can inherit consumer capabilities
- AI-powered bid evaluation
- Autonomous payment decisions
- Intelligent rating system

### Example: Create Your Own Consumer Agent
```python
from consumer_mixin import ConsumerMixin

class MyAgent(ConsumerMixin):
    def __init__(self, ...):
        # Setup consumer capabilities
        self.setup_consumer(
            openai_client=openai_client,
            x402_client=x402_client,
            registry_url=registry_url,
            agent_id=agent_id
        )

    def request_service(self):
        # AI evaluates bids and pays winner
        result = self.request_service_from_marketplace(
            task_type="price_data",
            task_description="Get SOL price",
            max_budget_usdc=0.001
        )
```

## Registry as Marketplace Intelligence

The orchestrator/registry now focuses on:
- Agent discovery
- Smart RFP routing
- Usage analytics
- Reputation aggregation
- NOT making payment decisions (agents do that)

## Expected Output

```
🛒 Requesting Service from Marketplace
Task: price_data
Description: Get real-time SOL/USDC price data
Budget: 0.001 USDC

📢 Broadcasting RFP...
✅ RFP Created: rfp_abc123

⏳ Waiting 10s for bids...

📊 Received 2 bids

🤖 AI Evaluating 2 bids...

📊 AI Decision:
   Recommended Winner: bid_provider_001
   Analysis: Provider 1 offers better reputation and proven
   track record. The 20% price premium is justified for
   portfolio decision-making where data accuracy is critical.

   ✅ bid_provider_001: ACCEPT
      Reasoning: Excellent reputation (4.8★), proven accuracy,
      worth premium for critical portfolio data

   ❌ bid_provider_002: REJECT
      Reasoning: Lower price but unproven, risky for portfolio
      decisions

✅ AI Selected Winner: data_provider_001
   Price: 0.00015 USDC
   Confidence: 0.85

💳 Executing Payment...
   Provider: data_provider_001
   Amount: 0.00015 USDC
   ✅ Payment successful!
   📊 Transaction: NixVLHGq6Xzk9K8rNSAREYvADPQPy9...

📦 DATA RECEIVED:
   {
      "success": true,
      "data": {
         "symbol": "SOL/USDC",
         "price": 142.35,
         "timestamp": "2025-11-07T12:00:00",
         "source": "mock_oracle"
      }
   }

⭐ AI Evaluating Provider Performance...
   Rating: 4.8★
   Review: Excellent data quality and fast delivery
   ✅ Rating submitted successfully

✅ Service Request Completed
   Provider: data_provider_001
   Price: 0.00015 USDC
   Transaction: NixVLHGq6Xzk9K8rNSAREYvADPQPy9...
```

## Benefits

1. **Decentralized Decision-Making**: Each agent decides independently
2. **AI-Powered**: Intelligent evaluation, not just lowest price
3. **Reputation System**: Providers build track records
4. **Market Competition**: Multiple providers compete on price/quality
5. **Autonomous Economy**: No human intervention needed

## Next Steps

- Add more agent types (Analytics, Swap Executors)
- Implement on-chain reputation (Solana accounts)
- Add more sophisticated AI evaluation criteria
- Create agent specialization (price-focused vs quality-focused consumers)
