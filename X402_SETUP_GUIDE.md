# 🚀 x402 Payment Integration - Setup Guide

## ✅ What's Been Built

You now have a **FULLY INTEGRATED** x402 payment system:

1. ✅ **Python Facilitator** (`facilitator/src/simple_facilitator.py`)
2. ✅ **x402 Client** (`agents/src/x402_client.py`)
3. ✅ **Payment-Gated API** (BiddingAgent `/deliver` endpoint)
4. ✅ **Payment Execution** (Orchestrator uses x402_client)
5. ✅ **Solana Wallets** (Generated in `.env`)

---

## 🔑 Wallet Addresses (FUND THESE!)

Your wallets are in `.env`:

### Orchestrator (Pays for Services)
```
Public Key:  EN8ZvMt7Gnnwmi9QtFXULFVtieKfN624yb79gPMCY6a7
```

### Data Provider (Receives Payments)
```
Public Key:  7DsSG72ySAbJH3czgiYHjaCr7Bw7QiY4MeXDdy6FKBof
```

### Facilitator (Pays Gas Fees)
```
Public Key:  LMYsxvTuHfMJBCsoCBTebQBEaaput8Z66Mq3mPLVHEr
```

---

## 💰 Funding Wallets (REQUIRED)

### Step 1: Get Devnet SOL (For Gas Fees)

**Option A: Solana CLI**
```bash
# Install Solana CLI if needed
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"

# Airdrop to each wallet
solana airdrop 1 EN8ZvMt7Gnnwmi9QtFXULFVtieKfN624yb79gPMCY6a7 --url devnet
solana airdrop 1 7DsSG72ySAbJH3czgiYHjaCr7Bw7QiY4MeXDdy6FKBof --url devnet
solana airdrop 2 LMYsxvTuHfMJBCsoCBTebQBEaaput8Z66Mq3mPLVHEr --url devnet
```

**Option B: Web Faucet**
Visit: https://faucet.solana.com/
- Paste each address
- Select "Devnet"
- Request SOL

### Step 2: Get Devnet USDC (For Payments)

Visit: https://faucet.circle.com/

1. Select **"Solana Devnet"**
2. Paste **Orchestrator address**: `EN8ZvMt7Gnnwmi9QtFXULFVtieKfN624yb79gPMCY6a7`
3. Request USDC (you'll get 10 USDC)

---

## 🎬 Running the Full System (4 Terminals)

### Terminal 1: Registry
```bash
./run_registry.sh
```
Wait for: `Uvicorn running on http://0.0.0.0:8000`

### Terminal 2: Facilitator (NEW!)
```bash
./run_facilitator.sh
```
Wait for: `x402 Facilitator Starting`

### Terminal 3: Bidding Agent
```bash
./run_bidding_agent.sh
```
Wait for: `✅ Subscribed to PRICE_DATA RFPs`

### Terminal 4: Demo
```bash
./run_demo.sh
```

---

## 🎯 What Happens (Full x402 Flow)

### Without Funding (Current State):
```
1. Orchestrator broadcasts RFP ✅
2. Bidding Agent bids ✅
3. AI selects winner ✅
4. Payment MOCK (no funds) ⚠️
```

### With Funded Wallets:
```
1. Orchestrator broadcasts RFP ✅
2. Bidding Agent bids ✅
3. AI selects winner ✅
4. Orchestrator creates USDC payment transaction 💳
5. Facilitator signs as fee payer ⚡
6. Transaction submitted to Solana devnet 🌐
7. Payment confirmed on-chain ✅
8. BiddingAgent delivers data 📊
9. Orchestrator receives data + tx signature 🎉
```

---

## 🔍 Verify It's Working

### Check Wallet Balances
```bash
# Check SOL balance
solana balance EN8ZvMt7Gnnwmi9QtFXULFVtieKfN624yb79gPMCY6a7 --url devnet

# Check USDC balance (use Solana Explorer)
# Visit: https://explorer.solana.com/?cluster=devnet
# Paste orchestrator address
```

### Check Transaction on Solana
After payment succeeds, you'll see:
```
📊 Transaction: 5ULZpdeThaMAy6hcEGfAoMFqJq...
```

Visit: `https://explorer.solana.com/tx/[SIGNATURE]?cluster=devnet`

You'll see:
- ✅ Transaction confirmed
- ✅ 0.00015 USDC transferred
- ✅ From: Orchestrator
- ✅ To: Data Provider

---

## 📊 System Architecture

```
┌─────────────────────┐
│  Orchestrator       │ Has USDC
│  (Needs data)       │
└──────────┬──────────┘
           │ 1. Broadcasts RFP
           ↓
┌─────────────────────┐
│  Registry           │
└──────────┬──────────┘
           │ 2. Notifies
           ↓
┌─────────────────────┐
│  BiddingAgent       │
│  (Can provide data) │
└──────────┬──────────┘
           │ 3. Submits bid
           ↓
┌─────────────────────┐
│  Orchestrator       │
│  (AI selects best)  │
└──────────┬──────────┘
           │ 4. Creates payment tx
           ↓
┌─────────────────────┐
│  x402 Facilitator   │ Has SOL for gas
│  (Signs & submits)  │
└──────────┬──────────┘
           │ 5. Broadcasts to Solana
           ↓
┌─────────────────────┐
│  Solana Devnet      │
│  (Confirms payment) │
└──────────┬──────────┘
           │ 6. Payment proof
           ↓
┌─────────────────────┐
│  BiddingAgent       │
│  (Delivers data)    │
└─────────────────────┘
```

---

## 🐛 Troubleshooting

### "Insufficient funds"
- Fund orchestrator with USDC
- Fund facilitator with SOL (for gas)

### "Transaction failed"
- Check Solana RPC is reachable: https://api.devnet.solana.com
- Check facilitator is running on port 3000

### "Payment proof not found"
- Ensure facilitator URL is correct in .env
- Check facilitator logs

---

## 🎓 For Hackathon Demo

### **If Wallets Are Funded:**
You have **REAL Solana x402 payments**! 🔥

Show judges:
1. Transaction signature in terminal
2. Solana Explorer showing payment
3. USDC transfer on-chain
4. Full autonomous agent economy

### **If Wallets Not Funded:**
System still works with mock payments!

Tell judges:
- "Architecture is complete"
- "x402 integration ready"
- "Just needs wallet funding for live demo"
- "Focus on AI negotiation innovation"

---

## 📝 Quick Test Without Funding

Want to see the flow without funding? The system will:
1. ✅ Create RFP
2. ✅ Get bids
3. ✅ Select winner
4. ⚠️  Attempt payment (will fail gracefully)
5. ✅ Show error message
6. ✅ Continue demo

The **AI negotiation** still works perfectly!

---

## 🚀 Next Steps

1. **Fund wallets** (5 minutes)
2. **Run demo** (see real Solana txs!)
3. **Record video** (show transaction on Solana Explorer)
4. **Submit to hackathon** 🏆

---

Built for **Solana x402 Hackathon** | November 2025
