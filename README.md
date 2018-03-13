# Grapefruit-web
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/1b638c81ede44715872e0ae699c5de2a)](https://www.codacy.com/app/bashkirtsevich/grapefruit-web?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=bashkirtsevich-llc/grapefruit-web&amp;utm_campaign=Badge_Grade)
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
