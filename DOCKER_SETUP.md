# 🐳 Docker Setup - One Command to Rule Them All

## Quick Start

### 1. Start All Services
```bash
docker-compose up -d
```

This starts **4 services**:
- ✅ Registry (port 8000)
- ✅ Facilitator (port 3000)
- ✅ Data Provider 1 (port 5001)
- ✅ Data Provider 2 (port 5002)

### 2. Run Demo
```bash
./run_demo_docker.sh
```

This triggers the Portfolio Manager (Consumer with AI) which:
1. Broadcasts RFP
2. Receives 2 competing bids
3. AI evaluates and chooses winner
4. Executes x402 payment
5. Rates provider

### 3. Check Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f provider_001
docker-compose logs -f provider_002
docker-compose logs -f registry
docker-compose logs -f facilitator
```

### 4. Stop All Services
```bash
docker-compose down
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│                                                          │
│  ┌──────────────┐     ┌──────────────┐                 │
│  │   Registry   │     │ Facilitator  │                 │
│  │   :8000      │     │   :3000      │                 │
│  └──────┬───────┘     └──────┬───────┘                 │
│         │                    │                          │
│         │                    │                          │
│  ┌──────▼──────────────┬─────▼──────────────┐         │
│  │                     │                     │         │
│  │  Data Provider 1    │  Data Provider 2    │         │
│  │     :5001          │      :5002          │         │
│  │  (Premium 0.00015)  │  (Budget 0.00012)   │         │
│  └─────────────────────┴─────────────────────┘         │
│                                                          │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │
                    ┌─────┴──────┐
                    │ Portfolio  │
                    │  Manager   │
                    │ (Demo Run) │
                    └────────────┘
```

---

## Service Details

### Registry (Marketplace Intelligence)
- **Port:** 8000
- **Role:** Agent discovery, RFP routing, reputation tracking
- **Endpoints:** `/rfp/*`, `/agents/*`

### Facilitator (x402 Payments)
- **Port:** 3000
- **Role:** Signs transactions, broadcasts to Solana
- **Endpoints:** `/supported`, `/verify`, `/settle`

### Data Provider 1 (Premium)
- **Port:** 5001
- **Price:** 0.00015 USDC
- **Strategy:** Quality-focused, high reputation

### Data Provider 2 (Budget)
- **Port:** 5002
- **Price:** 0.00012 USDC
- **Strategy:** Speed-focused, competitive pricing

---

## Environment Variables

All services read from `.env` file:
```env
OPENAI_API_KEY=...
SOLANA_RPC_URL=...
ORCHESTRATOR_PRIVATE_KEY=...
PROVIDER_PUBKEY=...
PROVIDER_002_PUBKEY=...
FACILITATOR_PRIVATE_KEY=...
PORTFOLIO_MANAGER_PRIVATE_KEY=...
```

---

## Health Checks

Docker Compose includes health checks for:
- Registry: `http://localhost:8000/`
- Facilitator: `http://localhost:3000/`

Services wait for dependencies to be healthy before starting.

---

## Useful Commands

### Check Service Status
```bash
docker-compose ps
```

### Restart Specific Service
```bash
docker-compose restart provider_001
```

### View Real-Time Logs (Multiple Services)
```bash
docker-compose logs -f provider_001 provider_002
```

### Rebuild After Code Changes
```bash
docker-compose up -d --build
```

### Clean Everything
```bash
docker-compose down -v
docker system prune -f
```

---

## Demo Flow

1. **Start Services:**
   ```bash
   docker-compose up -d
   ```
   Wait 10-15 seconds for all services to be ready.

2. **Check Services Are Up:**
   ```bash
   curl http://localhost:8000/
   curl http://localhost:3000/
   ```

3. **Run Demo:**
   ```bash
   ./run_demo_docker.sh
   ```

4. **Watch AI Decision:**
   - AI evaluates 2 bids
   - Chooses Provider 1 (better reputation)
   - Executes Solana payment
   - Rates provider 4.8★

5. **Verify On-Chain:**
   - Copy transaction signature from output
   - Visit: `https://explorer.solana.com/tx/[SIGNATURE]?cluster=devnet`

---

## Troubleshooting

### "Port already in use"
```bash
# Find and kill process using port
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
lsof -ti:5001 | xargs kill -9
lsof -ti:5002 | xargs kill -9
```

### "Cannot connect to Docker daemon"
```bash
# Start Docker Desktop (macOS)
open -a Docker

# Or check Docker service (Linux)
sudo systemctl start docker
```

### Services not starting
```bash
# Check logs for errors
docker-compose logs

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Demo fails to connect
```bash
# Ensure services are ready
docker-compose ps

# Check network
docker network ls | grep x402

# Restart services
docker-compose restart
```

---

## For Hackathon Demo

**Preparation:**
```bash
# 1. Start services (do this before judges arrive)
docker-compose up -d

# 2. Verify all running
docker-compose ps

# 3. Check logs are clean
docker-compose logs --tail=50
```

**During Demo:**
```bash
# Run demo in front of judges
./run_demo_docker.sh
```

**What to Show:**
1. "Four services running in Docker"
2. "AI evaluating two competing bids" (terminal output)
3. "AI chooses Provider 1 based on reputation"
4. "Real Solana transaction" (copy signature to explorer)
5. "Only Provider 1's wallet received payment"
6. "AI automatically rated provider 4.8 stars"

**Cleanup After:**
```bash
docker-compose down
```

---

## Benefits of Docker Setup

✅ **One Command Setup:** `docker-compose up -d`
✅ **Isolated Network:** Services communicate internally
✅ **Reproducible:** Works same on any machine
✅ **Easy Reset:** `docker-compose restart`
✅ **Professional:** Shows deployment readiness
✅ **Hackathon Ready:** Quick setup for judges

---

## Production Notes

For production deployment:
- Use environment-specific compose files
- Add volume mounts for persistence
- Implement proper logging (ELK stack)
- Add monitoring (Prometheus/Grafana)
- Use secrets management (not .env)
- Deploy to Kubernetes for scaling
