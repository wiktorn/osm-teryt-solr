#!/usr/bin/env sh

set -e

cd push-teryt-to-solr
apt update
apt install -y python3 python3-venv
python3 -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/python fetch.py
