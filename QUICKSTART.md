# 🚀 QUICKSTART - Self-Negotiating Agent Mesh

## What You Built

**AI-powered agent economy** where agents autonomously discover each other, bid on tasks, and negotiate using OpenAI - all on Solana x402.

## Files Created

✅ **Core System:**
- `registry/src/rfp_manager.py` - RFP/Bid coordination engine
- `registry/src/main.py` - Updated with RFP endpoints
- `shared/schemas/negotiation.py` - RFP/Bid/Assignment schemas
- `shared/schemas/prompts.py` - AI system prompts

✅ **Agents:**
- `agents/src/orchestrator_agent.py` - Broadcasts RFPs, evaluates bids with AI
- `agents/src/bidding_data_provider.py` - Polls RFPs, bids with AI decisions

✅ **Demo:**
- `demo_negotiation.py` - Full workflow demo

## Run It Now

**First time setup:**
```bash
# Already done! venv created and dependencies installed
```

### Terminal 1: Registry
```bash
./run_registry.sh
# → Starts on http://localhost:8000
```

### Terminal 2: Bidding Agent
```bash
./run_bidding_agent.sh
# → Starts on http://localhost:5001
# → Automatically polls for RFPs every 3s
```

### Terminal 3: Demo
```bash
./run_demo.sh
# → Orchestrator broadcasts RFP
# → Bidding agent sees it and bids
# → AI evaluates and selects winner
```

## What Happens

1. **Orchestrator**: "I need SOL price data, budget 0.001 USDC"
2. **Registry**: Broadcasts RFP to all subscribed agents
3. **BiddingAgent**:
   - 🤖 AI analyzes: "Can I do this?"
   - 🤖 AI calculates: "What price should I bid?"
   - 📤 Submits bid: "0.00008 USDC, 250ms response time"
4. **Orchestrator**:
   - 📊 Collects all bids
   - 🤖 AI evaluates: price + speed + reputation
   - ✅ Selects winner
5. **Assignment**: Task assigned, ready for x402 payment

## API Endpoints Added

```
POST /rfp/create - Create RFP
GET  /rfp/open - List open RFPs
POST /rfp/{id}/bid - Submit bid
GET  /rfp/{id}/bids - Get all bids
GET  /rfp/{id}/evaluate - Evaluate bids
POST /rfp/{id}/select - Select winner
POST /rfp/{id}/negotiate - Send negotiation message
```

## Tech Stack

- **FastAPI** - Registry service
- **OpenAI GPT-4** - AI decision making
- **Pydantic** - Data validation
- **x402** - Micropayments (ready to integrate)
- **Solana** - On-chain payments

## For Hackathon Judges

**Track**: Best Trustless Agent

**Innovation**: First agent mesh using AI for autonomous negotiations

**Video**: [Record 3-min demo showing the flow]

**Try It**: Just 3 terminals, runs locally

## Next Steps

1. ✅ System works locally - DONE
2. 🔄 Add x402 payment execution
3. 🔄 Deploy to Solana devnet
4. 🔄 Add more agent types (simulator, executor)
5. 🔄 Build UI dashboard

## Troubleshooting

**"No bids received"**: Wait 5-10s, agent polls every 3s

**Import errors**: `pip install fastapi uvicorn httpx openai pydantic`

**OpenAI errors**: Check `OPENAI_API_KEY` in `.env`

---

**You now have a working self-negotiating agent mesh! 🎉**

Built for Solana x402 Hackathon | November 2025
