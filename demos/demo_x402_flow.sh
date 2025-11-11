#!/bin/bash

# ANSI Color codes
CYAN='\033[96m'
GREEN='\033[92m'
YELLOW='\033[93m'
RED='\033[91m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m' # No Color

clear

echo ""
echo -e "${CYAN}${BOLD}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}${BOLD}║           HTTP 402 Payment Required - x402 Protocol Demo          ║${NC}"
echo -e "${CYAN}${BOLD}║          Step-by-Step Demonstration of Payment Flow               ║${NC}"
echo -e "${CYAN}${BOLD}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Provider endpoint
PROVIDER_URL="http://localhost:5002/deliver"

echo -e "${CYAN}${BOLD}════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}  Step 1: Attempt to Access Data WITHOUT Payment${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${DIM}Making request to: ${PROVIDER_URL}${NC}"
echo ""

# Try to access without payment
response=$(curl -s -w "\n%{http_code}" -X POST "$PROVIDER_URL" -H "Content-Type: application/json")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" = "402" ]; then
    echo -e "${RED}${BOLD}❌ HTTP 402 - Payment Required!${NC}"
    echo ""
    echo -e "${YELLOW}Payment Requirements:${NC}"
    echo "$body" | jq -C '.'

    # Extract payment details
    recipient=$(echo "$body" | jq -r '.recipient')
    amount=$(echo "$body" | jq -r '.amount')
    token_mint=$(echo "$body" | jq -r '.token_mint')

    echo ""
    echo -e "${CYAN}${BOLD}════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}  Step 2: Payment Details Extracted${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${BOLD}Recipient:${NC}    ${GREEN}$recipient${NC}"
    echo -e "${BOLD}Amount:${NC}       ${GREEN}$amount USDC${NC}"
    echo -e "${BOLD}Token Mint:${NC}   ${GREEN}$token_mint${NC}"

    echo ""
    echo -e "${CYAN}${BOLD}════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}  Step 3: Creating USDC Payment Transaction${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}⏳ Building SPL token transfer transaction...${NC}"
    echo -e "${DIM}   Using x402 client to create signed transaction${NC}"
    echo -e "${DIM}   Transaction will transfer $amount USDC to provider${NC}"

    sleep 2

    echo ""
    echo -e "${CYAN}${BOLD}════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}  Step 4: Settling Payment via Facilitator${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}⏳ Sending payment to facilitator for settlement...${NC}"
    echo -e "${DIM}   Facilitator will submit transaction to Solana${NC}"

    # Note: In real demo, this would call the Python client to create and sign the transaction
    # For this shell demo, we'll show the concept

    echo ""
    echo -e "${YELLOW}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${DIM}To see the full payment flow in action, run:${NC}"
    echo ""
    echo -e "  ${CYAN}./run_demo_local.sh${NC}    ${DIM}# Full demo with automatic payment${NC}"
    echo ""
    echo -e "${DIM}The Python x402 client will:${NC}"
    echo -e "  ${GREEN}1.${NC} Detect 402 response"
    echo -e "  ${GREEN}2.${NC} Create USDC SPL token transfer transaction"
    echo -e "  ${GREEN}3.${NC} Sign transaction with consumer wallet"
    echo -e "  ${GREEN}4.${NC} Send to facilitator (/settle endpoint)"
    echo -e "  ${GREEN}5.${NC} Receive transaction signature"
    echo -e "  ${GREEN}6.${NC} Retry request with X-Payment-Response header"
    echo -e "  ${GREEN}7.${NC} Receive data from provider"
    echo ""
    echo -e "${YELLOW}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

else
    echo -e "${RED}${BOLD}Unexpected response code: $http_code${NC}"
    echo "$body"
fi

echo ""
echo -e "${CYAN}${BOLD}════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}  What is HTTP 402 Payment Required?${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${DIM}HTTP 402 is a reserved status code that means 'Payment Required'.${NC}"
echo -e "${DIM}It's part of the HTTP specification but rarely used.${NC}"
echo ""
echo -e "${BOLD}x402 Protocol Uses:${NC}"
echo -e "  • ${GREEN}Micropayments${NC} for API access"
echo -e "  • ${GREEN}Pay-per-use${NC} data services"
echo -e "  • ${GREEN}Agent-to-agent${NC} transactions"
echo -e "  • ${GREEN}Blockchain payments${NC} (USDC on Solana)"
echo ""
echo -e "${BOLD}Benefits:${NC}"
echo -e "  • ${GREEN}No subscription${NC} needed"
echo -e "  • ${GREEN}Pay only for what you use${NC}"
echo -e "  • ${GREEN}Cryptographic proof${NC} of payment"
echo -e "  • ${GREEN}Instant settlement${NC} on blockchain"
echo ""

echo -e "${CYAN}${BOLD}════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}  Current System Architecture${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BOLD}Services Running:${NC}"
echo -e "  • ${CYAN}Registry${NC}        (Port 8000) - Marketplace discovery"
echo -e "  • ${CYAN}Facilitator${NC}     (Port 3000) - Payment settlement"
echo -e "  • ${CYAN}Provider 001${NC}    (Port 5001) - Premium data (0.00015 USDC)"
echo -e "  • ${CYAN}Provider 002${NC}    (Port 5002) - Fast data (0.00012 USDC)"
echo ""
echo -e "${BOLD}Payment Flow:${NC}"
echo -e "  ${GREEN}Consumer${NC} ──[RFP]──> ${YELLOW}Registry${NC} ──[Broadcast]──> ${CYAN}Providers${NC}"
echo -e "            <─[Bids]──                  <──[Bids]──"
echo -e "            ──[402]───> ${CYAN}Provider${NC}"
echo -e "            ──[USDC]──> ${YELLOW}Facilitator${NC} ──[Submit]──> ${GREEN}Solana${NC}"
echo -e "            <─[TxSig]──"
echo -e "            ──[Retry with proof]──> ${CYAN}Provider${NC}"
echo -e "            <─[Data]────────────────"
echo ""

echo -e "${CYAN}${BOLD}════════════════════════════════════════════════════════════════════${NC}"
echo ""
