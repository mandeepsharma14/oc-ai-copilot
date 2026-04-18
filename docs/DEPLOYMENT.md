# Deployment Guide
## OC AI Copilot — Step-by-Step Azure Deployment

---

## Prerequisites Checklist

- [ ] Azure subscription with Owner or Contributor access
- [ ] Azure CLI: `az --version` (need 2.57+) — install: https://aka.ms/installazureclimacos
- [ ] Terraform: `terraform --version` (need 1.7+) — install: https://developer.hashicorp.com/terraform/install
- [ ] kubectl: `kubectl version --client`
- [ ] Docker Desktop running
- [ ] Node.js 20+ and Python 3.11+
- [ ] Git

---

## STEP 1 — Clone and Configure

```bash
# Clone
git clone https://github.com/mandeepsharma14/oc-ai-copilot.git
cd oc-ai-copilot

# Run setup script (creates .env, installs dependencies)
bash infrastructure/scripts/setup.sh

# Edit .env — fill in ALL Azure values
nano .env   # or open in VS Code: code .env
```

**Minimum required .env values:**
```
SECRET_KEY=<generate: python3 -c "import secrets; print(secrets.token_hex(32))">
AZURE_OPENAI_ENDPOINT=https://YOUR-INSTANCE.openai.azure.com/
AZURE_OPENAI_API_KEY=...
AZURE_SEARCH_ENDPOINT=https://YOUR-SEARCH.search.windows.net
AZURE_SEARCH_ADMIN_KEY=...
AZURE_TENANT_ID=...
AZURE_CLIENT_ID=...
AZURE_CLIENT_SECRET=...
COSMOS_ENDPOINT=...
COSMOS_KEY=...
```

---

## STEP 2 — Run Locally with Docker Compose

```bash
# Start all services
docker-compose up --build

# Verify running:
curl http://localhost:8000/api/v1/health
# → {"status":"healthy","version":"1.0.0",...}

# Open in browser:
open http://localhost:3000          # Internal portal
open http://localhost:8000/docs     # API documentation (Swagger)
```

---

## STEP 3 — Azure Prerequisites

```bash
# Login
az login
az account set --subscription "YOUR-SUBSCRIPTION-ID"

# Create Terraform state storage (one-time)
az group create --name rg-oc-copilot-tfstate --location "East US 2"
az storage account create \
  --name stoccopilottfstate \
  --resource-group rg-oc-copilot-tfstate \
  --sku Standard_LRS
az storage container create \
  --name tfstate \
  --account-name stoccopilottfstate

# Register providers
az provider register --namespace Microsoft.CognitiveServices
az provider register --namespace Microsoft.Search
az provider register --namespace Microsoft.ContainerService
az provider register --namespace Microsoft.DocumentDB
az provider register --namespace Microsoft.Cache
```

---

## STEP 4 — Provision Infrastructure (Terraform)

```bash
cd infrastructure/terraform

# Create variables file
cat > prod.tfvars << EOF
environment         = "production"
location            = "East US 2"
resource_group_name = "rg-oc-copilot-prod"
sql_admin_password  = "$(python3 -c 'import secrets; print(secrets.token_urlsafe(20))')"
EOF

# Init, plan, apply (~15 minutes)
terraform init
terraform plan -var-file="prod.tfvars"
terraform apply -var-file="prod.tfvars"

# Save outputs to .env
terraform output -raw openai_endpoint   # → AZURE_OPENAI_ENDPOINT
terraform output -raw search_endpoint   # → AZURE_SEARCH_ENDPOINT
terraform output -raw redis_hostname    # → REDIS_URL
terraform output -raw cosmos_endpoint   # → COSMOS_ENDPOINT

cd ../..
```

---

## STEP 5 — Configure Azure Entra ID (SSO)

```
In Azure Portal:
  Azure Active Directory → App registrations → New registration
  Name: OC AI Copilot
  Redirect URI: https://copilot.owenscorning.com/auth/callback

Copy:
  Application (client) ID → AZURE_CLIENT_ID in .env
  Directory (tenant) ID   → AZURE_TENANT_ID in .env

Create client secret:
  App registration → Certificates & secrets → New client secret
  Copy value immediately → AZURE_CLIENT_SECRET in .env

Add API permissions:
  → Microsoft Graph → Delegated → User.Read, profile, openid, email
```

---

## STEP 6 — Build and Push Docker Images

```bash
# Login to GitHub Container Registry
echo $GITHUB_PAT | docker login ghcr.io -u mandeepsharma14 --password-stdin

# Build and push
docker build -t ghcr.io/mandeepsharma14/oc-ai-copilot/backend:latest  ./backend
docker build -t ghcr.io/mandeepsharma14/oc-ai-copilot/frontend:latest ./frontend
docker push ghcr.io/mandeepsharma14/oc-ai-copilot/backend:latest
docker push ghcr.io/mandeepsharma14/oc-ai-copilot/frontend:latest
```

---

## STEP 7 — Deploy to AKS

```bash
# Get AKS credentials
az aks get-credentials \
  --resource-group rg-oc-copilot-prod \
  --name aks-oc-copilot-production
kubectl get nodes   # should show 3+ Ready nodes

# Create namespace and secrets
kubectl create namespace production
kubectl create secret generic oc-copilot-secrets \
  --from-env-file=.env \
  --namespace production

# Install NGINX ingress controller
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace

# Install cert-manager (SSL)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.5/cert-manager.yaml

# Deploy application
VERSION=$(git rev-parse --short HEAD)
sed -i '' "s|IMAGE_TAG|$VERSION|g" infrastructure/kubernetes/backend-deployment.yaml
sed -i '' "s|IMAGE_TAG|$VERSION|g" infrastructure/kubernetes/frontend-deployment.yaml
kubectl apply -f infrastructure/kubernetes/ --namespace production

# Watch deployment
kubectl rollout status deployment/oc-copilot-backend  --namespace production
kubectl rollout status deployment/oc-copilot-frontend --namespace production
```

---

## STEP 8 — Configure DNS

```bash
# Get external IP
kubectl get ingress oc-copilot-ingress --namespace production
# Note the ADDRESS

# In your DNS provider, create two A records:
# copilot.owenscorning.com  → <EXTERNAL_IP>
# advisor.owenscorning.com  → <EXTERNAL_IP>
# TTL: 300
```

---

## STEP 9 — Set Up GitHub Actions CI/CD

```bash
# Create Azure service principal for GitHub Actions
az ad sp create-for-rbac \
  --name "oc-copilot-github-actions" \
  --role contributor \
  --scopes /subscriptions/<subscription-id>/resourceGroups/rg-oc-copilot-prod \
  --sdk-auth
# Copy JSON output

# In GitHub repo: Settings → Secrets → Actions → New secret
# Name: AZURE_CREDENTIALS
# Value: <paste JSON output>

# Push to trigger first automated deploy:
git add . && git commit -m "feat: initial deploy" && git push origin main
```

---

## STEP 10 — Smoke Test

```bash
# Health check
curl https://copilot.owenscorning.com/api/v1/health

# Test internal query
curl -X POST https://copilot.owenscorning.com/api/v1/chat/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the LOTO standard?", "stream_type": "internal"}'

# Open browser
open https://copilot.owenscorning.com   # Internal portal
open https://advisor.owenscorning.com   # External customer portal
```

---

## Troubleshooting

**Pods not starting:**
```bash
kubectl describe pod -l app=oc-copilot-backend --namespace production
kubectl logs -l app=oc-copilot-backend --namespace production
```

**Azure OpenAI 429 quota errors:**
- Azure Portal → Azure OpenAI → Deployments → View quota → Request increase

**Redis connection error:**
```bash
kubectl exec -it deploy/oc-copilot-backend --namespace production -- \
  python -c "import redis; r=redis.from_url('redis://...'); print(r.ping())"
```

**Roll back a bad deployment:**
```bash
kubectl rollout undo deployment/oc-copilot-backend --namespace production
```

---

## Expected Monthly Costs (Phase 1 — 500 users)

| Service | Monthly Cost |
|---------|-------------|
| Azure OpenAI (GPT-4o) | ~$2,500 |
| AKS (3 Standard_D8s_v3) | ~$800 |
| Azure AI Search (S2) | ~$300 |
| Redis, Cosmos DB, SQL | ~$400 |
| **Total** | **~$4,000/month** |
