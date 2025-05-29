# API Monitoring System

![Architecture](architecture.png)
проверка на ру буквы

Real-time API monitoring system with Kafka and WebSocket notifications.

## Features
- Monitors API availability
- Detects 4XX and 5XX errors
- Real-time alerts via WebSocket
- Historical alerts via HTTP API
- Docker containerization

## Quick Start

```bash
# Clone repository
git clone https://github.com/your-username/api-monitor.git
cd api-monitor

# Start services
docker-compose up -d

# Access web interface
open http://localhost:8081
```

## Configuration
Edit `config/api_config.json` to add your API endpoints:

```json
[
  {
    "url": "https://your-api.com/health",
    "type": "GET"
  }
]
```

## Project Structure
```
api-monitor/
├── docker-compose.yml
├── .gitignore
├── README.md
├── config/
│   └── api_config.json
├── api_checker/
│   ├── Dockerfile
│   ├── api_checker.py
│   ├── kafka_utils.py
│   └── requirements.txt
├── websocket_server/
│   ├── Dockerfile
│   ├── server.py
│   └── requirements.txt
└── client/
    ├── Dockerfile
    └── index.html
```