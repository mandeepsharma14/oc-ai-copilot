#!/usr/bin/env bash
# OC AI Copilot — Initial project setup script
set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
info()  { echo -e "${GREEN}[INFO]${NC}  $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

echo ""
echo "====================================="
echo "  OC AI Copilot — Project Setup"
echo "====================================="
echo ""

command -v python3 >/dev/null 2>&1 || error "Python 3.11+ required"
command -v node    >/dev/null 2>&1 || error "Node.js 20+ required"
command -v docker  >/dev/null 2>&1 || error "Docker required"
info "Prerequisites OK"

if [ ! -f .env ]; then
  cp .env.example .env
  # Auto-generate a secret key
  if command -v python3 >/dev/null 2>&1; then
    KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i.bak "s/replace-with-32-char-random-string/$KEY/" .env
    rm -f .env.bak
  fi
  info ".env created — edit it with your Azure credentials"
else
  info ".env already exists"
fi

info "Installing Python dependencies…"
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
deactivate
cd ..
info "Python ready"

info "Installing Node.js dependencies…"
cd frontend
npm install --silent
cd ..
info "Node ready"

echo ""
echo "====================================="
echo "  Setup complete!"
echo "====================================="
echo ""
echo "Next steps:"
echo "  1. Edit .env with your Azure credentials"
echo "  2. docker-compose up --build"
echo "  3. Open http://localhost:3000"
echo "  4. API docs: http://localhost:8000/docs"
echo ""
