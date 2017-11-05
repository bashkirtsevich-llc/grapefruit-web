# Grapefruit-web
Grapefruit web interface to access torrents database.

Table of content:

[TOC]

## Requirements
* Python 3.6.3 or higher
* MongoDB 3.2.17 or higher

## Execution
### Direct execution
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
3. Start MongoDB
4. Start web-server (by default server start at `0.0.0.0:8080`)
```bash
python app.py
```

### Docker
1. Install Docker
2. Start Docker daemon (optional step)
```bash
sudo usermod -aG docker $(whoami)
sudo service docker start
```
3. Build container
```bash
sudo docker build -t grapefruit-web .
```
4. Start container
```bash
sudo docker run grapefruit-web
```
Port forwarding:
```bash
sudo docker run -p 80:8080 grapefruit-web
```
Interactive mode:
```bash
sudo docker run -it -p 80:8080 grapefruit-web
```