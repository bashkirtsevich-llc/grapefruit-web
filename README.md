# Grapefruit-web
[![Build Status](https://travis-ci.org/bashkirtsevich-llc/grapefruit-web.svg?branch=master)](https://travis-ci.org/bashkirtsevich-llc/grapefruit-web)

Grapefruit web interface to access torrents database.

## Requirements
* Python 3.6.3 or higher
* MongoDB 3.2.17 or higher

## Execution
1. Install requirements
```bash
pip install -r requirements.txt
```
2. Set environment variables
```
MONGODB_URL=mongodb://mongodb:27017/grapefruit
```
Optional (default = `grapefruit`):
```
MONGODB_BASE_NAME=grapefruit
```
3. Start web-server (by default server start at `0.0.0.0:8080`)
```bash
python app.py
```
