#!/bin/bash
echo "========================================="
echo " Starting Tokyo Dome Info Board... "
echo "========================================="

cd "$(dirname "$0")"

source .venv/bin/activate

python web_app/app.py