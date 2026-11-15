#!/usr/bin/env bash
# EduAlert 1-Click Server Setup Script for Ubuntu / Debian
set -e

echo "=========================================================="
echo "🚀 EduAlert Server Deployment Script"
echo "=========================================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "❌ Please run as root (use: sudo bash deploy.sh)"
  exit 1
fi

APP_DIR="/var/www/edualert"

echo "[1/5] Updating packages and installing Python3, pip, venv..."
apt-get update -y
apt-get install -y python3 python3-pip python3-venv git curl

echo "[2/5] Creating application directory at $APP_DIR..."
mkdir -p "$APP_DIR"
cp -r . "$APP_DIR/"
cd "$APP_DIR"

echo "[3/5] Setting up virtual environment..."
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

echo "[4/5] Configuring systemd auto-start service..."
cp edualert.service /etc/systemd/system/edualert.service
systemctl daemon-reload
systemctl enable edualert
systemctl restart edualert

echo "[5/5] Checking service status..."
sleep 2
if systemctl is-active --quiet edualert; then
    SERVER_IP=$(curl -s ifconfig.me || hostname -I | awk '{print $1}')
    echo ""
    echo "=========================================================="
    echo "✅ EduAlert successfully deployed and running 24/7!"
    echo "🌐 Web Dashboard: http://${SERVER_IP}:5000"
    echo "⚙️ Service commands:"
    echo "   - View logs:    sudo journalctl -u edualert -f"
    echo "   - Restart:      sudo systemctl restart edualert"
    echo "   - Stop:         sudo systemctl stop edualert"
    echo "=========================================================="
else
    echo "❌ Service failed to start. Run 'journalctl -u edualert -e' to view errors."
fi
