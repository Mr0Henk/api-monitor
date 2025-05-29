# RU: Система мониторинга API




Система мониторинга API в реальном времени с оповещением Kafka и WebSocket.

## Возможности
- Отслеживает доступность API
- Обнаруживает ошибки 4XX и 5XX
- Оповещения в реальном времени через WebSocket
- История оповещений через HTTP API
- Контейнеризация Docker
- 
## Быстрый старт

```bash
# Скопируйте репозиторий
git clone https://github.com/your-username/api-monitor.git
cd api-monitor

# Запустите проект
docker-compose up -d

# Доступ к веб-интерфейсу по ссылке:
open http://localhost:8081
```

## Конфигурация
Измените `config/api_config.json` чтобы добавить свои endpoints для API:

```json
[
  {
    "url": "https://your-api.com/health",
    "type": "GET"
  }
]
```

## Структура проекта
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


# ENG: API Monitoring System



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