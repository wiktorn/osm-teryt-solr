#!/usr/bin/env sh

set -e

cd push-teryt-to-solr
python3 -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/python fetch.py
