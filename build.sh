#!/bin/bash
# build.sh
echo "🔧 Python sürümünü 3.12'ye düşürüyorum..."
apt-get update && apt-get install -y python3.12 python3.12-venv

echo "📦 Sanal ortam oluşturuyorum..."
python3.12 -m venv venv
source venv/bin/activate

echo "📦 Gereksinimleri yüklüyorum..."
pip install python-telegram-bot==20.7

echo "🚀 Bot başlatılıyor..."
python bot.py
