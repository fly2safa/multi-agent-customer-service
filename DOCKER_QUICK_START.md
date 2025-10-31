# 🚀 Docker Quick Start - Email This to yourself or someone you like to have this Docker guide
#            for installing and running this Multi Agent Customer Service application!

**Project:** Multi-Agent Customer Service AI  
**Docker Version:** v2.0.0  
**Updated:** October 31, 2025

---

## ⚡ What is Docker?

Docker lets you run this entire application (backend + frontend) with **ONE command**, without installing Python, Node.js, or any dependencies manually. Everything runs in isolated "containers" that work on any computer (Windows, Mac, Linux).

**Benefits:**
- ✅ No Python/Node installation needed
- ✅ Works exactly the same on any computer
- ✅ One command to start everything
- ✅ Easy to stop, restart, and clean up

---

## 📋 Step 1: Install Docker Desktop

### Windows / macOS

1. **Download Docker Desktop:**
   - Go to: https://www.docker.com/products/docker-desktop
   - Click "Download for Windows" or "Download for Mac"

2. **Install:**
   - Run the installer
   - Follow the prompts (accept defaults)
   - **Important:** You may need to restart your computer

3. **Verify Installation:**
   - Open PowerShell (Windows) or Terminal (Mac)
   - Type: `docker --version`
   - Should show: `Docker version 24.x.x` or similar

4. **Start Docker Desktop:**
   - Windows: Search for "Docker Desktop" and launch it
   - Mac: Open Docker from Applications
   - Wait for the Docker icon in system tray to show "Docker Desktop is running"

### Linux

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group (avoid using sudo)
sudo usermod -aG docker $USER
# Log out and log back in for this to take effect
```

---

## 📂 Step 2: Get Your Project Files

You already have the project on your computer at:
```
C:\Users\fly2s\Documents\ASU\MyAIcourse\MyProjects\MyRepoSandbox\agent-proj2
```

Or clone from GitHub:
```bash
git clone https://github.com/fly2safa/multi-agent-customer-service.git
cd multi-agent-customer-service
```

---

## 🔑 Step 3: Configure API Keys (CRITICAL!)

**You need 3 things:**
1. OpenAI API Key
2. AWS Access Key ID
3. AWS Secret Access Key + Session Token

### Create Environment File

**Windows PowerShell:**
```powershell
cd C:\Users\fly2s\Documents\ASU\MyAIcourse\MyProjects\MyRepoSandbox\agent-proj2\backend
Copy-Item env.example .env
notepad .env
```

**Mac/Linux:**
```bash
cd backend
cp env.example .env
nano .env
```

### Edit `.env` File

Replace the placeholder values with your actual credentials:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-actual-openai-key-here

# AWS Bedrock Configuration
AWS_ACCESS_KEY_ID=AKIA...your-actual-key...
AWS_SECRET_ACCESS_KEY=...your-actual-secret-key...
AWS_SESSION_TOKEN=...your-actual-session-token...
AWS_REGION=us-east-1
```

**⚠️ IMPORTANT:**
- Don't use quotes around the values
- No spaces around the `=` sign
- For AWS Academy, you MUST include `AWS_SESSION_TOKEN` (it expires every 4 hours)

**Save and close the file.**

---

## 🐳 Step 4: Start the Application with Docker

### Navigate to Project Root

**Windows PowerShell:**
```powershell
cd C:\Users\fly2s\Documents\ASU\MyAIcourse\MyProjects\MyRepoSandbox\agent-proj2
```

**Mac/Linux:**
```bash
cd /path/to/agent-proj2
```

### Build and Start Everything

```bash
docker-compose up --build
```

**What this does:**
1. Builds Docker images for backend and frontend
2. Creates containers and network
3. Starts both services
4. Shows you the logs in real-time

**Expected Output:**
```
[+] Building 120.5s (35/35) FINISHED
[+] Running 3/3
 ✔ Network multi-agent-network        Created
 ✔ Container multi-agent-backend      Started
 ✔ Container multi-agent-frontend     Started

multi-agent-backend  | INFO:     Application startup complete.
multi-agent-backend  | INFO:     Uvicorn running on http://0.0.0.0:8000
multi-agent-frontend | ▲ Next.js 14.0.0
multi-agent-frontend | - Local:        http://localhost:3000
multi-agent-frontend | ✓ Ready in 3.2s
```

**⏱️ First time takes 3-5 minutes to build. Subsequent starts are much faster!**

---

## 🎯 Step 5: Load Data into ChromaDB

**Keep the first terminal running** (showing logs).

Open a **new terminal window** and run:

**Windows PowerShell:**
```powershell
cd C:\Users\fly2s\Documents\ASU\MyAIcourse\MyProjects\MyRepoSandbox\agent-proj2
docker-compose exec backend python ingest_data.py
```

**Mac/Linux:**
```bash
cd /path/to/agent-proj2
docker-compose exec backend python ingest_data.py
```

**Expected Output:**
```
📦 Ingesting documents into ChromaDB...
✓ Created collection: billing_docs (25 documents)
✓ Created collection: technical_docs (30 documents)  
✓ Created collection: policy_docs (20 documents)
✓ Data ingestion complete!
```

**⚠️ You only need to do this ONCE!** The data persists even when you stop Docker.

---

## 🌐 Step 6: Access the Application

**Open your web browser and go to:**

- **Frontend (Chat Interface):** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Health Check:** http://localhost:8000/health

**Test it:**
1. Go to http://localhost:3000
2. Type: "What are your pricing plans?"
3. You should see the Billing Agent respond!

---

## 🎛️ Common Docker Commands

### Stop the Application

**In the terminal showing logs, press:**
```
Ctrl + C
```

Then run:
```bash
docker-compose down
```

**This stops the containers but KEEPS your data** (ChromaDB will remember documents).

### Start Again (After Stopping)

```bash
docker-compose up
```

**Note:** No `--build` needed unless you changed the code!

### Run in Background (Detached Mode)

```bash
docker-compose up -d
```

**Containers run in background. To see logs:**
```bash
docker-compose logs -f
```

**To stop:**
```bash
docker-compose down
```

### Check if Services are Running

```bash
docker-compose ps
```

**Expected Output:**
```
NAME                      STATUS
multi-agent-backend       Up (healthy)
multi-agent-frontend      Up (healthy)
```

### View Logs

```bash
# All logs
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend

# Last 50 lines
docker-compose logs --tail=50
```

### Restart Services

```bash
# Restart everything
docker-compose restart

# Restart backend only
docker-compose restart backend
```

### Rebuild After Code Changes

```bash
docker-compose up --build
```

---

## 🔧 Troubleshooting

### Problem: "Cannot connect to Docker daemon"

**Solution:**
- Make sure Docker Desktop is running
- Check system tray (Windows) or menu bar (Mac) for Docker icon
- Wait for "Docker Desktop is running" message

### Problem: "Port 3000/8000 already in use"

**Solution - Kill the process:**

**Windows PowerShell:**
```powershell
# Find process on port 3000
netstat -ano | findstr :3000
# Note the PID (last column), then:
Stop-Process -Id <PID> -Force

# Same for port 8000
netstat -ano | findstr :8000
Stop-Process -Id <PID> -Force
```

**Mac/Linux:**
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Problem: Backend shows "Unhealthy" status

**Solution:**
```bash
# Check backend logs
docker-compose logs backend

# Common issues:
# 1. Missing API keys in backend/.env
# 2. Expired AWS Session Token (AWS Academy expires every 4 hours)
# 3. Invalid API key format

# Fix: Update backend/.env and restart
docker-compose restart backend
```

### Problem: Frontend can't connect to backend

**Solution:**
```bash
# Check if backend is healthy
docker-compose ps

# Test backend directly
curl http://localhost:8000/health

# Restart frontend
docker-compose restart frontend
```

### Problem: "AWS Session Token expired"

**AWS Academy tokens expire every 4 hours!**

**Solution:**
1. Go to AWS Academy → AWS Details
2. Click "AWS CLI: Show"
3. Copy the new credentials
4. Update `backend/.env` with new `AWS_SESSION_TOKEN`
5. Restart: `docker-compose restart backend`

### Problem: Lost all data after restart

**Cause:** You used `docker-compose down -v` which deletes volumes.

**Solution:**
```bash
# To KEEP data (ChromaDB):
docker-compose down

# To DELETE data:
docker-compose down -v

# Restore: Re-run data ingestion
docker-compose exec backend python ingest_data.py
```

### Problem: Slow build or "no space left"

**Solution:**
```bash
# Clean up unused Docker resources
docker system prune -a

# This removes:
# - Stopped containers
# - Unused images
# - Build cache
# - Unused networks
```

---

## 🧹 Complete Cleanup

**To remove EVERYTHING (containers, images, volumes):**

```bash
# Stop and remove containers + volumes
docker-compose down -v

# Remove images
docker rmi agent-proj2-backend agent-proj2-frontend

# Clean up system
docker system prune -a
```

**⚠️ After this, you'll need to rebuild and re-ingest data!**

---

## 📝 Quick Reference Card

| Task | Command |
|------|---------|
| **First time setup** | `docker-compose up --build` |
| **Load data** | `docker-compose exec backend python ingest_data.py` |
| **Start (already built)** | `docker-compose up` |
| **Start in background** | `docker-compose up -d` |
| **Stop (keep data)** | `docker-compose down` |
| **Stop (delete data)** | `docker-compose down -v` |
| **View logs** | `docker-compose logs -f` |
| **Check status** | `docker-compose ps` |
| **Restart** | `docker-compose restart` |
| **Rebuild** | `docker-compose up --build` |
| **Clean up** | `docker system prune -a` |

---

## 🎓 Testing Your Setup

### Test 1: Basic Connectivity

```bash
# Test backend health
curl http://localhost:8000/health

# Or visit in browser:
# http://localhost:8000/health
```

**Expected:** JSON response with `"status": "healthy"`

### Test 2: Frontend Loading

Visit: http://localhost:3000

**Expected:** Chat interface loads with "Multi-Agent Customer Service" header

### Test 3: End-to-End Chat

1. Go to http://localhost:3000
2. Type: "What are your pricing plans?"
3. **Expected:** Billing Agent responds with pricing information
4. Type: "How do I reset my password?"
5. **Expected:** Technical Support Agent responds with reset steps

### Test 4: Agent Routing

Try these queries to test each agent:

**Billing Agent:**
- "What payment methods do you accept?"
- "Tell me about enterprise contracts"

**Technical Support Agent:**
- "How do I set up API authentication?"
- "What are common errors?"

**Policy Agent:**
- "What is your privacy policy?"
- "Tell me about GDPR compliance"

---

## 📱 Accessing from Other Devices (Optional)

**Want to access from your phone/tablet on same WiFi?**

1. Find your computer's IP address:

**Windows:**
```powershell
ipconfig
# Look for "IPv4 Address" under your WiFi adapter
# Example: 192.168.1.100
```

**Mac/Linux:**
```bash
ifconfig | grep "inet "
# Or: ip addr show
```

2. On your phone/tablet, go to:
```
http://YOUR-IP:3000
# Example: http://192.168.1.100:3000
```

**⚠️ Note:** Your computer's firewall may block this. You might need to allow port 3000 through the firewall.

---

## 🔗 Useful Links

- **Full Documentation:** See `README.md` in project folder
- **Detailed Docker Guide:** See `DOCKER_GUIDE.md` (562 lines!)
- **Manual Setup (No Docker):** See `TESTING_GUIDE.md`
- **Docker Documentation:** https://docs.docker.com/
- **Docker Compose Docs:** https://docs.docker.com/compose/

---

## 💡 Tips & Best Practices

### Daily Workflow

```bash
# Morning: Start the app
cd C:\Users\fly2s\Documents\ASU\MyAIcourse\MyProjects\MyRepoSandbox\agent-proj2
docker-compose up -d

# Work: Use the app at http://localhost:3000

# Evening: Stop the app
docker-compose down
```

### AWS Academy Users (Session Tokens Expire!)

**Every 4 hours, you need to refresh AWS credentials:**

1. Open AWS Academy → AWS Details
2. Click "AWS CLI: Show"
3. Copy new credentials
4. Update `backend/.env`
5. Run: `docker-compose restart backend`

**Tip:** Set a 3-hour reminder on your phone!

### Backup Your ChromaDB Data

```bash
# Create backup
docker run --rm -v multi-agent-chroma-data:/data -v C:\Users\fly2s\Documents\backups:/backup alpine tar czf /backup/chroma-backup.tar.gz -C /data .

# Restore backup
docker run --rm -v multi-agent-chroma-data:/data -v C:\Users\fly2s\Documents\backups:/backup alpine tar xzf /backup/chroma-backup.tar.gz -C /data
```

### Monitor Resource Usage

**Docker Desktop → Settings → Resources:**
- **CPUs:** Allocate 4+ for best performance
- **Memory:** Allocate 4GB minimum, 8GB recommended
- **Disk:** 20GB should be plenty

---

## 📧 Email This Document to Yourself!

**Subject:** Docker Quick Start - Multi-Agent AI

**Save this file as:** `DOCKER_QUICK_START.md`

**Or print as PDF:**
1. Open this file in your editor or browser
2. File → Print → Save as PDF

---

## ✅ Success Checklist

Before you close this guide, make sure:

- [ ] Docker Desktop installed and running
- [ ] Project files on your computer
- [ ] `backend/.env` configured with API keys
- [ ] Ran `docker-compose up --build` successfully
- [ ] Ran `docker-compose exec backend python ingest_data.py`
- [ ] Accessed http://localhost:3000 in browser
- [ ] Tested a chat query and got a response
- [ ] Bookmarked this guide for future reference!

---

## 🆘 Need More Help?

- **Detailed Troubleshooting:** See `DOCKER_GUIDE.md`
- **API Configuration Issues:** See `backend/env.example`
- **Frontend Issues:** See `frontend/README.md` (if exists)
- **General Testing:** See `TESTING_GUIDE.md`

---

**🎉 You're all set! Enjoy your Docker-powered AI assistant!**

**Version:** 2.0.0 | **Last Updated:** October 31, 2025

