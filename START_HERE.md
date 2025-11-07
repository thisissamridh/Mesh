# 🚀 START HERE - x402 AI Agent Marketplace

## Quickest Way to Run (Docker)

### 1. Start All Services
```bash
docker-compose up -d
```
**Wait 10-15 seconds** for services to initialize.

### 2. Run Demo
```bash
./run_demo_docker.sh
```

### 3. Watch Magic Happen
You'll see:
- 🤖 AI evaluating 2 competing provider bids
- ✅ AI choosing Provider 1 (better reputation)
- 💳 Real Solana payment executed
- ⭐ AI rating provider 4.8 stars

### 4. Stop Services
```bash
docker-compose down
```

---

## Alternative: Manual Setup (5 Terminals)

### Terminal 1: Registry
```bash
./run_registry.sh
```

### Terminal 2: Facilitator
```bash
./run_facilitator.sh
```

### Terminal 3: Provider 1
```bash
./run_bidding_agent.sh
```

### Terminal 4: Provider 2
```bash
./run_provider_002.sh
```

### Terminal 5: Demo
```bash
./run_portfolio_manager.sh
```

---

## What's Running?

| Service | Port | Role |
|---------|------|------|
| Registry | 8000 | Marketplace intelligence |
| Facilitator | 3000 | x402 payment handler |
| Provider 1 | 5001 | Premium data (0.00015 USDC) |
| Provider 2 | 5002 | Budget data (0.00012 USDC) |
| Portfolio Manager | - | Consumer with AI (demo trigger) |

---

## Key Features

✅ **AI Decision-Making:** GPT-4 evaluates bids autonomously
✅ **Real Blockchain:** Solana devnet payments
✅ **Reputation System:** Providers build track records
✅ **Market Competition:** Multiple providers compete
✅ **Autonomous Agents:** No human intervention needed

---

## Troubleshooting

**Docker not working?**
```bash
# Check Docker is running
docker ps

# Rebuild if needed
docker-compose build --no-cache
```

**Need to check logs?**
```bash
docker-compose logs -f provider_001
```

**Want to restart?**
```bash
docker-compose restart
```

---

## For Judges/Demo

1. Start: `docker-compose up -d`
2. Demo: `./run_demo_docker.sh`
3. Show: Terminal output + Solana Explorer transaction
4. Highlight: "AI chose quality over price - Provider 1 won!"

---

## Documentation

- **DOCKER_SETUP.md** - Complete Docker guide
- **CONSUMER_AI_DEMO.md** - AI decision flow explained
- **FUNDING_GUIDE.md** - Wallet funding instructions
- **QUICKSTART.md** - Manual setup guide

---

## Architecture

```
Consumer Agent (Portfolio Manager)
    ↓ Broadcasts RFP
Registry (Smart routing)
    ↓ Routes to providers
Provider 1 & Provider 2 (AI bidding)
    ↓ Submit competing bids
Consumer's AI (Evaluation)
    ↓ Chooses winner
Facilitator + Solana (Payment)
    ↓ x402 settlement
Provider 1 (Data delivery)
    ↓ After payment proof
Consumer's AI (Rating)
    ✅ 4.8★ submitted
```

---

**Built for Solana x402 Hackathon | November 2025**
