# 🐳 Docker Deployment Guide

Complete guide for deploying the Multi-Agent Customer Service AI using Docker.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Docker Commands](#docker-commands)
- [Architecture](#architecture)
- [Troubleshooting](#troubleshooting)
- [Production Considerations](#production-considerations)

---

## Prerequisites

### Required Software

1. **Docker Desktop** (Windows/macOS) or **Docker Engine** (Linux)
   - Download: https://www.docker.com/products/docker-desktop
   - Minimum version: Docker 20.10+
   - Docker Compose: v2.0+

2. **API Keys**
   - OpenAI API key
   - AWS credentials (Access Key, Secret Key, Session Token)

### System Requirements

- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 5GB free space
- **CPU**: 2 cores minimum, 4 cores recommended

---

## Quick Start

### 1. Clone Repository

```bash
git clone <repository-url>
cd agent-proj2
```

### 2. Configure Environment

```bash
# Copy backend environment template
cp backend/env.example backend/.env

# Edit backend/.env with your API keys
# Required:
#   - OPENAI_API_KEY
#   - AWS_ACCESS_KEY_ID
#   - AWS_SECRET_ACCESS_KEY
#   - AWS_SESSION_TOKEN
#   - AWS_REGION (default: us-east-1)
```

### 3. Start the Application

```bash
# Build and start all services
docker-compose up --build

# Or run in background (detached mode)
docker-compose up -d --build
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health

### 5. Verify Everything Works

```bash
# Check service status
docker-compose ps

# Both services should show "healthy" status
# NAME                      STATUS
# multi-agent-backend       Up (healthy)
# multi-agent-frontend      Up (healthy)
```

### 6. View Logs

```bash
# Follow all logs
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

### 7. Stop the Application

```bash
# Stop services (preserves data)
docker-compose down

# Stop and remove data volumes
docker-compose down -v
```

---

## Detailed Setup

### Environment Configuration

#### Backend Environment (Required)

Create `backend/.env` with the following:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-...your-key-here...

# AWS Bedrock Configuration
AWS_ACCESS_KEY_ID=AKIA...your-key...
AWS_SECRET_ACCESS_KEY=...your-secret...
AWS_SESSION_TOKEN=...your-token...  # Required for AWS Academy/Learner Lab
AWS_REGION=us-east-1

# Optional Backend Configuration
# PORT=8000  # Default port
```

#### Frontend Environment (Optional)

Create `frontend/.env.local` (only if backend is on different host):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Note:** For local Docker deployment, this is automatically configured.

### First-Time Setup: Ingest Data

After starting the services, ingest the mock documents into ChromaDB:

```bash
# Run data ingestion inside the container
docker-compose exec backend python ingest_data.py
```

**Expected Output:**
```
✓ Created collection: billing_docs (25 documents)
✓ Created collection: technical_docs (30 documents)
✓ Created collection: policy_docs (20 documents)
✓ Data ingestion complete!
```

---

## Docker Commands

### Service Management

**Start services:**
```bash
docker-compose up              # Foreground (see logs)
docker-compose up -d           # Background (detached)
docker-compose up --build      # Rebuild and start
docker-compose up -d --build   # Rebuild and start in background
```

**Stop services:**
```bash
docker-compose stop            # Stop without removing
docker-compose down            # Stop and remove containers
docker-compose down -v         # Stop and remove containers + volumes
```

**Restart services:**
```bash
docker-compose restart         # Restart all services
docker-compose restart backend # Restart backend only
```

### Logs and Debugging

**View logs:**
```bash
docker-compose logs            # All logs
docker-compose logs -f         # Follow (tail) all logs
docker-compose logs -f backend # Follow backend logs only
docker-compose logs --tail=100 backend # Last 100 lines
```

**Check service status:**
```bash
docker-compose ps              # List running services
docker-compose top             # Show running processes
```

### Execute Commands in Containers

**Backend:**
```bash
# Ingest data
docker-compose exec backend python ingest_data.py

# Run agent tests
docker-compose exec backend python test_agents.py

# Run API tests
docker-compose exec backend python test_api.py

# Access backend shell
docker-compose exec backend /bin/bash

# Check ChromaDB collections
docker-compose exec backend python -c "from app.retrievers import get_retriever; print(get_retriever('billing').get_collection_count())"
```

**Frontend:**
```bash
# Access frontend shell
docker-compose exec frontend /bin/sh

# Check environment variables
docker-compose exec frontend env
```

### Image Management

**List images:**
```bash
docker images | grep multi-agent
```

**Remove images:**
```bash
docker rmi agent-proj2-backend
docker rmi agent-proj2-frontend
```

**Rebuild from scratch:**
```bash
docker-compose build --no-cache
```

### Volume Management

**List volumes:**
```bash
docker volume ls | grep multi-agent
```

**Inspect volume:**
```bash
docker volume inspect multi-agent-chroma-data
```

**Backup ChromaDB data:**
```bash
# Create backup
docker run --rm -v multi-agent-chroma-data:/data -v $(pwd):/backup alpine tar czf /backup/chroma-backup.tar.gz -C /data .

# Restore backup
docker run --rm -v multi-agent-chroma-data:/data -v $(pwd):/backup alpine tar xzf /backup/chroma-backup.tar.gz -C /data
```

---

## Architecture

### Services

#### Backend Service
- **Image**: Python 3.10 slim
- **Port**: 8000
- **Healthcheck**: `curl http://localhost:8000/health`
- **Volume**: `chroma_data` mounted at `/app/chroma_db`
- **Restart Policy**: `unless-stopped`

#### Frontend Service
- **Image**: Node 18 Alpine
- **Port**: 3000
- **Depends On**: Backend (waits for healthy status)
- **Healthcheck**: Node.js HTTP check
- **Restart Policy**: `unless-stopped`

### Volumes

- **chroma_data**: Persistent storage for ChromaDB vector database
  - Location: Docker managed volume
  - Survives container restarts
  - Deleted only with `docker-compose down -v`

### Network

- **app-network**: Bridge network for inter-service communication
  - Backend accessible as `backend:8000` from frontend
  - Frontend accessible as `frontend:3000` from backend

### Build Process

**Backend:**
1. Base: Python 3.10 slim
2. Install system dependencies (gcc, g++)
3. Install Python packages from `requirements.txt`
4. Copy application code
5. Create ChromaDB directory
6. Expose port 8000

**Frontend:**
1. Base: Node 18 Alpine
2. Install dependencies (`npm ci`)
3. Build Next.js application (standalone mode)
4. Create production image with minimal files
5. Run as non-root user (`nextjs:nodejs`)
6. Expose port 3000

---

## Troubleshooting

### Issue: Backend container exits immediately

**Symptoms:**
```bash
$ docker-compose ps
NAME                 STATUS
multi-agent-backend  Exited (1)
```

**Solution:**
```bash
# Check logs for error details
docker-compose logs backend

# Common causes:
# 1. Missing API keys in backend/.env
# 2. Invalid API key format
# 3. AWS credentials expired (Session Token)

# Fix: Update backend/.env and restart
docker-compose restart backend
```

### Issue: Frontend can't connect to backend

**Symptoms:**
- Frontend loads but shows connection errors
- "Failed to fetch" errors in browser console

**Solution:**
```bash
# 1. Check backend health
docker-compose ps
# Backend should show "healthy"

# 2. Check backend logs
docker-compose logs backend

# 3. Test backend from host
curl http://localhost:8000/health

# 4. Test backend from frontend container
docker-compose exec frontend wget -O- http://backend:8000/health

# 5. Restart frontend
docker-compose restart frontend
```

### Issue: ChromaDB data lost after restart

**Cause:** Used `docker-compose down -v` which deletes volumes

**Solution:**
```bash
# To preserve data, use:
docker-compose down          # ✓ Keeps volumes

# NOT:
docker-compose down -v       # ✗ Deletes volumes

# To restore from backup (see Volume Management section)
```

### Issue: Port already in use

**Symptoms:**
```
Error: bind: address already in use
```

**Solution:**
```bash
# Windows PowerShell
netstat -ano | findstr :3000
Stop-Process -Id <PID> -Force

netstat -ano | findstr :8000
Stop-Process -Id <PID> -Force

# macOS/Linux
lsof -ti:3000 | xargs kill -9
lsof -ti:8000 | xargs kill -9
```

### Issue: Build fails with "no space left on device"

**Solution:**
```bash
# Clean up Docker resources
docker system prune -a --volumes

# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune
```

### Issue: Slow performance inside container

**Solution:**
1. Allocate more resources to Docker Desktop:
   - Settings → Resources → Advanced
   - Increase CPUs: 4+
   - Increase Memory: 8GB+

2. Use BuildKit for faster builds:
   ```bash
   export DOCKER_BUILDKIT=1
   docker-compose build
   ```

### Issue: Health check failing

**Symptoms:**
```bash
$ docker-compose ps
NAME                 STATUS
multi-agent-backend  Up (unhealthy)
```

**Solution:**
```bash
# Check health check logs
docker inspect multi-agent-backend | grep -A 10 Health

# Check if service is actually running
docker-compose exec backend curl localhost:8000/health

# If curl fails, check service logs
docker-compose logs backend

# Common causes:
# 1. Application crashed (check logs)
# 2. Port not exposed correctly (check Dockerfile)
# 3. Health endpoint not responding (check app code)
```

---

## Production Considerations

### Security

1. **Environment Variables:**
   - Use Docker secrets or external secret management
   - Never commit `.env` files
   - Rotate AWS Session Tokens regularly

2. **User Permissions:**
   - Backend runs as root (needs fixing for production)
   - Frontend runs as non-root user `nextjs` ✓

3. **Network:**
   - Use reverse proxy (nginx) in front of services
   - Enable HTTPS/TLS
   - Restrict exposed ports

### Scaling

1. **Horizontal Scaling:**
   ```yaml
   # docker-compose.yml
   backend:
     deploy:
       replicas: 3
   ```

2. **Load Balancer:**
   - Use nginx or Traefik for load balancing
   - Session affinity for stateful sessions

### Monitoring

1. **Logs:**
   - Use centralized logging (ELK, Splunk)
   - Configure log rotation

2. **Metrics:**
   - Prometheus for metrics collection
   - Grafana for visualization
   - Monitor CPU, memory, request latency

3. **Health Checks:**
   - Already configured in docker-compose.yml ✓
   - Monitor health check endpoints

### Persistence

1. **ChromaDB Data:**
   - Backup volume regularly (see Volume Management)
   - Consider cloud-based vector DB for production (Pinecone, Weaviate)

2. **Session Data:**
   - Currently in-memory (lost on restart)
   - Use Redis for production session storage

### CI/CD

1. **GitHub Actions example:**
   ```yaml
   - name: Build Docker images
     run: docker-compose build
   
   - name: Run tests
     run: |
       docker-compose up -d
       docker-compose exec -T backend python test_agents.py
       docker-compose down
   ```

2. **Registry:**
   - Push images to Docker Hub or AWS ECR
   - Tag with version numbers

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/docker/)
- [Next.js Docker](https://nextjs.org/docs/deployment#docker-image)

---

## Support

For issues specific to this project, see:
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Manual testing without Docker
- [README.md](README.md) - Full project documentation
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - General troubleshooting (if exists)

