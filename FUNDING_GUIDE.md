# 💰 Wallet Funding Guide - 5 Wallets

## Overview

You now have **5 separate wallets** for a proper marketplace demo:

| Wallet | Role | Needs SOL? | Needs USDC? |
|--------|------|------------|-------------|
| Orchestrator | Consumer (buys services) | ✅ Yes | ✅ Yes |
| Portfolio Manager | Independent Consumer | ✅ Yes | ✅ Yes |
| Data Provider 1 | Service Provider | ✅ Yes | ❌ No (receives) |
| Data Provider 2 | Competing Provider | ✅ Yes | ❌ No (receives) |
| Facilitator | Gas fee payer | ✅ Yes | ❌ No |

---

## Step 1: Fund with SOL (for gas fees)

### Option A: Solana CLI (Fastest)
```bash
# Orchestrator (already funded ✅)
solana airdrop 1 EN8ZvMt7Gnnwmi9QtFXULFVtieKfN624yb79gPMCY6a7 --url devnet

# Portfolio Manager (NEW - needs funding)
solana airdrop 1 A98Cyn1J7BM8Tug5MUXrMvBoH6tmFoiAxEYpkirB6RBP --url devnet

# Data Provider 1 (already funded ✅)
solana airdrop 1 7DsSG72ySAbJH3czgiYHjaCr7Bw7QiY4MeXDdy6FKBof --url devnet

# Data Provider 2 (NEW - needs funding)
solana airdrop 1 5kXPxgJE15pKqUpkKU2TmYwSeG72fPcsBCYwKT28zq8B --url devnet

# Facilitator (already funded ✅)
solana airdrop 2 LMYsxvTuHfMJBCsoCBTebQBEaaput8Z66Mq3mPLVHEr --url devnet
```

### Option B: Web Faucet
Visit: https://faucet.solana.com/
- Paste each address
- Select "Devnet"
- Request SOL

---

## Step 2: Fund with USDC (for payments)

Visit: https://faucet.circle.com/

### Fund Consumer Wallets (they pay for services):

**Orchestrator (already funded ✅):**
```
EN8ZvMt7Gnnwmi9QtFXULFVtieKfN624yb79gPMCY6a7
```

**Portfolio Manager (NEW - needs funding):**
```
A98Cyn1J7BM8Tug5MUXrMvBoH6tmFoiAxEYpkirB6RBP
```

### Provider Wallets:
**Providers DON'T need USDC** - they receive payments from consumers!

---

## Summary of NEW Wallets to Fund:

### Portfolio Manager (Independent Consumer)
```bash
# SOL for gas:
solana airdrop 1 A98Cyn1J7BM8Tug5MUXrMvBoH6tmFoiAxEYpkirB6RBP --url devnet

# USDC from Circle faucet:
# Visit: https://faucet.circle.com/
# Paste: A98Cyn1J7BM8Tug5MUXrMvBoH6tmFoiAxEYpkirB6RBP
```

### Data Provider 2 (Competing Provider)
```bash
# SOL for gas:
solana airdrop 1 5kXPxgJE15pKqUpkKU2TmYwSeG72fPcsBCYwKT28zq8B --url devnet

# USDC: NOT NEEDED (receives payments)
```

---

## Verify Funding

```bash
# Check SOL balance
solana balance A98Cyn1J7BM8Tug5MUXrMvBoH6tmFoiAxEYpkirB6RBP --url devnet
solana balance 5kXPxgJE15pKqUpkKU2TmYwSeG72fPcsBCYwKT28zq8B --url devnet

# Check USDC on Solana Explorer
# Visit: https://explorer.solana.com/?cluster=devnet
# Paste Portfolio Manager address: A98Cyn1J7BM8Tug5MUXrMvBoH6tmFoiAxEYpkirB6RBP
```

---

## Why 5 Wallets?

### Old Setup (3 wallets):
- ❌ Both providers shared wallet → can't see competition
- ❌ Portfolio Manager = Orchestrator → not independent

### New Setup (5 wallets):
- ✅ Each provider has own wallet → see who wins bids
- ✅ Portfolio Manager independent → true consumer AI decisions
- ✅ Clear payment flows → transparency in marketplace

---

## Demo Benefits

With separate wallets you can see:
1. **Portfolio Manager's AI** chooses Provider 1
2. **Payment goes specifically** to Provider 1's wallet
3. **Provider 2's wallet** shows no payment (they lost the bid)
4. **Reputation updates** correctly for Provider 1
5. **True marketplace competition** visible on-chain
