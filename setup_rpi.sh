#!/bin/bash
# ============================================================
# EasySunSystem - Script d'installation Raspberry Pi
# A lancer une seule fois sur un RPi fraichement installe.
#
# Usage : sudo bash setup_rpi.sh
# ============================================================

set -e

# --- Couleurs ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()  { echo -e "${GREEN}[OK]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!!]${NC} $1"; }
error() { echo -e "${RED}[ERR]${NC} $1"; exit 1; }

# --- Verification ---
if [ "$EUID" -ne 0 ]; then
    error "Ce script doit etre lance avec sudo : sudo bash setup_rpi.sh"
fi

INSTALL_DIR="$(cd "$(dirname "$0")" && pwd)"
echo ""
echo "========================================"
echo "  EasySunSystem - Installation"
echo "  Dossier : $INSTALL_DIR"
echo "========================================"
echo ""

# --- 1. Mise a jour systeme ---
info "Mise a jour du systeme..."
apt-get update -qq
apt-get upgrade -y -qq

# --- 2. Installation des paquets systeme ---
info "Installation de hostapd et dnsmasq..."
apt-get install -y -qq hostapd dnsmasq python3-pip

# Arreter les services le temps de la configuration
systemctl stop hostapd 2>/dev/null || true
systemctl stop dnsmasq 2>/dev/null || true

# --- 3. Installation des dependances Python ---
info "Installation des dependances Python..."
pip3 install -r "$INSTALL_DIR/requirements.txt" --break-system-packages 2>/dev/null \
    || pip3 install -r "$INSTALL_DIR/requirements.txt"

# --- 4. Configuration du hotspot WiFi ---
info "Configuration du hotspot WiFi..."

# dhcpcd.conf - IP statique pour wlan0
cp "$INSTALL_DIR/config/dhcpcd.conf" /etc/dhcpcd.conf

# hostapd.conf - Point d'acces WiFi
cp "$INSTALL_DIR/config/hostapd.conf" /etc/hostapd/hostapd.conf

# Activer hostapd avec le bon fichier de config
sed -i 's|^#DAEMON_CONF=.*|DAEMON_CONF="/etc/hostapd/hostapd.conf"|' /etc/default/hostapd 2>/dev/null || true

# dnsmasq.conf - DHCP + portail captif
cp "$INSTALL_DIR/config/dnsmasq.conf" /etc/dnsmasq.conf

# --- 5. Configuration des services systemd ---
info "Configuration des services systemd..."

# Service principal EasySunSystem
cat > /etc/systemd/system/easy_sun.service << EOF
[Unit]
Description=EasySunSystem Monitoring
After=multi-user.target network.target

[Service]
Type=idle
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/app.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Service hotspot WiFi
cp "$INSTALL_DIR/config/wifi-hotspot.service" /etc/systemd/system/wifi-hotspot.service

# Activer les services au demarrage
systemctl daemon-reload
systemctl unmask hostapd
systemctl enable hostapd
systemctl enable dnsmasq
systemctl enable wifi-hotspot.service
systemctl enable easy_sun.service

# --- 6. Nettoyage rc.local (eviter le double lancement de hostapd) ---
if grep -q "hostapd" /etc/rc.local 2>/dev/null; then
    warn "Nettoyage de rc.local (suppression du lancement hostapd en double)..."
    sed -i '/hostapd/d' /etc/rc.local
fi

# --- 7. Initialisation de la base de donnees ---
info "Initialisation de la base de donnees..."
cd "$INSTALL_DIR"
python3 -c "from easysun import create_app; create_app({'SIMULATION_MODE': True, 'SAVE_INTERVAL': 999999, 'CLEAR_INTERVAL': 999999})" 2>/dev/null
info "Base de donnees initialisee."

# --- Termine ---
echo ""
echo "========================================"
echo "  Installation terminee !"
echo "========================================"
echo ""
echo "  Hotspot WiFi :"
echo "    SSID     : EasySunSystem"
echo "    Mot de passe : easysunsystem"
echo ""
echo "  Interface web :"
echo "    Connectez-vous au WiFi ci-dessus"
echo "    puis ouvrez n'importe quel site"
echo "    dans votre navigateur."
echo ""
echo "  Redemarrage dans 5 secondes..."
echo ""

sleep 5
reboot
