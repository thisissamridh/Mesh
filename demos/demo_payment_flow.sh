#!/bin/bash

# X402 Payment Flow Demonstration
# Shows: Payment Requirements -> Verification -> Settlement

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}X402 Payment Flow Demonstration${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Configuration
PROVIDER_URL="http://localhost:5001"
FACILITATOR_URL="http://localhost:3000"
ENDPOINT="/deliver"

# Check if services are running
echo -e "${YELLOW}Checking services...${NC}"
if ! curl -s "${PROVIDER_URL}/health" > /dev/null 2>&1; then
    echo -e "${RED}✗ Provider not running at ${PROVIDER_URL}${NC}"
    echo -e "${YELLOW}Start services first:${NC}"
    echo -e "  docker compose -f docker/docker-compose.yml up -d"
    echo -e "  or"
    echo -e "  ./run_demo_local.sh"
    exit 1
fi

if ! curl -s "${FACILITATOR_URL}/supported" > /dev/null 2>&1; then
    echo -e "${RED}✗ Facilitator not running at ${FACILITATOR_URL}${NC}"
    echo -e "${YELLOW}Start services first:${NC}"
    echo -e "  docker compose -f docker/docker-compose.yml up -d"
    exit 1
fi

echo -e "${GREEN}✓ Services are running${NC}"
echo ""

echo -e "${YELLOW}Step 1: Request without payment (expect 402)${NC}"
echo -e "POST ${PROVIDER_URL}${ENDPOINT}"
echo ""

RESPONSE=$(curl -s -X POST -w "\nHTTP_CODE:%{http_code}" "${PROVIDER_URL}${ENDPOINT}" || true)
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE/d')

if [ "$HTTP_CODE" == "402" ]; then
    echo -e "${GREEN}✓ Received 402 Payment Required${NC}"
    echo -e "${GREEN}Payment Requirements:${NC}"
    echo "$BODY" | jq '.'

    # Extract payment details
    RECIPIENT=$(echo "$BODY" | jq -r '.recipient // "unknown"')
    AMOUNT=$(echo "$BODY" | jq -r '.amount // 0')
    TOKEN_MINT=$(echo "$BODY" | jq -r '.token_mint // "unknown"')
    FACILITATOR=$(echo "$BODY" | jq -r '.facilitator_url // "unknown"')

    echo ""
    echo -e "${BLUE}→ Recipient: ${NC}${RECIPIENT}"
    echo -e "${BLUE}→ Amount: ${NC}${AMOUNT} USDC"
    echo -e "${BLUE}→ Token: ${NC}${TOKEN_MINT}"
    echo -e "${BLUE}→ Facilitator: ${NC}${FACILITATOR}"
else
    echo -e "${RED}✗ Expected 402, got ${HTTP_CODE}${NC}"
    echo "$BODY"
    echo ""
    echo -e "${YELLOW}Make sure a data provider agent is running and serving at ${PROVIDER_URL}${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 2: Verify payment transaction structure${NC}"
echo -e "POST ${FACILITATOR_URL}/verify"
echo ""

# Create mock transaction data for verification
VERIFY_PAYLOAD=$(cat <<EOF
{
    "payment": "mock_signed_transaction_base58"
}
EOF
)

echo -e "${BLUE}Verification Request:${NC}"
echo "$VERIFY_PAYLOAD" | jq '.'
echo ""

VERIFY_RESPONSE=$(curl -s -X POST "${FACILITATOR_URL}/verify" \
    -H "Content-Type: application/json" \
    -d "$VERIFY_PAYLOAD" || echo '{"isValid": false, "error": "Facilitator not running"}')

echo -e "${GREEN}Verification Response:${NC}"
echo "$VERIFY_RESPONSE" | jq '.'

IS_VALID=$(echo "$VERIFY_RESPONSE" | jq -r '.isValid // false')
if [ "$IS_VALID" == "true" ]; then
    echo -e "${GREEN}✓ Transaction structure valid${NC}"
else
    echo -e "${YELLOW}⚠ Verification failed (expected - mock transaction is not valid base58)${NC}"
    echo -e "${BLUE}   In real flow, x402_client.py creates a valid USDC SPL token transfer${NC}"
fi

echo ""
echo -e "${YELLOW}Step 3: Settle payment via facilitator${NC}"
echo -e "POST ${FACILITATOR_URL}/settle"
echo ""

# Create mock settlement payload
SETTLE_PAYLOAD=$(cat <<EOF
{
    "payment": "mock_signed_transaction_base58"
}
EOF
)

echo -e "${BLUE}Settlement Request:${NC}"
echo "$SETTLE_PAYLOAD" | jq '.'
echo ""

SETTLE_RESPONSE=$(curl -s -X POST "${FACILITATOR_URL}/settle" \
    -H "Content-Type: application/json" \
    -d "$SETTLE_PAYLOAD" || echo '{"signature": null, "error": "Facilitator not running"}')

echo -e "${GREEN}Settlement Response:${NC}"
echo "$SETTLE_RESPONSE" | jq '.'

SIGNATURE=$(echo "$SETTLE_RESPONSE" | jq -r '.transaction // .signature // null')
if [ "$SIGNATURE" != "null" ] && [ "$SIGNATURE" != "" ]; then
    echo -e "${GREEN}✓ Payment settled on Solana${NC}"
    echo -e "${BLUE}→ Transaction: ${NC}${SIGNATURE}"
    echo -e "${BLUE}→ Explorer: ${NC}https://explorer.solana.com/tx/${SIGNATURE}?cluster=devnet"
else
    echo -e "${YELLOW}⚠ Settlement failed (expected - mock transaction rejected by Kora)${NC}"
    echo -e "${BLUE}   In real flow, Kora signs as fee payer and broadcasts to Solana (gasless!)${NC}"
fi

echo ""
echo -e "${YELLOW}Step 4: Retry request with payment proof${NC}"
echo -e "POST ${PROVIDER_URL}${ENDPOINT}"
echo -e "Header: X-Payment-Response: ${SIGNATURE}"
echo ""

if [ "$SIGNATURE" != "null" ] && [ "$SIGNATURE" != "" ]; then
    PAID_RESPONSE=$(curl -s -X POST -w "\nHTTP_CODE:%{http_code}" \
        -H "X-Payment-Response: {\"signature\":\"${SIGNATURE}\",\"network\":\"solana-devnet\"}" \
        "${PROVIDER_URL}${ENDPOINT}" || true)

    PAID_HTTP_CODE=$(echo "$PAID_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
    PAID_BODY=$(echo "$PAID_RESPONSE" | sed '/HTTP_CODE/d')

    if [ "$PAID_HTTP_CODE" == "200" ]; then
        echo -e "${GREEN}✓ Received 200 OK - Data delivered${NC}"
        echo -e "${GREEN}Response:${NC}"
        echo "$PAID_BODY" | jq '.'
    else
        echo -e "${YELLOW}⚠ Got HTTP ${PAID_HTTP_CODE}${NC}"
        echo "$PAID_BODY"
    fi
else
    echo -e "${YELLOW}⚠ Skipping (no valid payment signature)${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Complete X402 Payment Flow:${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "1. ${GREEN}✓${NC} Payment Required (402) - Provider returns payment details"
echo -e "2. ${GREEN}✓${NC} Verification - Facilitator validates transaction structure"
echo -e "3. ${GREEN}✓${NC} Settlement - Kora signs and broadcasts to Solana"
echo -e "4. ${GREEN}✓${NC} Data Delivery - Provider verifies payment and returns data"
echo ""
echo -e "${YELLOW}Note: For real transactions, run with actual agents:${NC}"
echo -e "  ./run_demo_local.sh    # Local demo with real USDC payments"
echo -e "  ./run_demo_docker.sh   # Docker demo with full setup"
echo ""
