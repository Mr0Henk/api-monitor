import asyncio
import json
import logging
import time
from confluent_kafka import Consumer, KafkaException
from aiohttp import web
import websockets

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('WebSocketServer')

# Глобальная переменная для хранения последних алертов
LATEST_ALERTS = []
MAX_ALERTS_HISTORY = 50


def create_kafka_consumer():
    """Создание потребителя Kafka с настройками"""
    return Consumer({
        'bootstrap.servers': 'kafka:9092',
        'group.id': 'websocket-group',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False,
        'session.timeout.ms': 10000
    })


def add_alert_to_history(alert):
    """Добавление алерта в историю"""
    global LATEST_ALERTS
    LATEST_ALERTS.append(alert)

    # Сохраняем только последние MAX_ALERTS_HISTORY алертов
    if len(LATEST_ALERTS) > MAX_ALERTS_HISTORY:
        LATEST_ALERTS = LATEST_ALERTS[-MAX_ALERTS_HISTORY:]


async def handle_websocket(websocket, path):
    """Обработка WebSocket соединения"""
    client_ip = websocket.remote_address[0]
    logger.info(f"New WebSocket connection from {client_ip}")

    consumer = None
    retry_count = 0
    max_retries = 5

    # Отправляем историю при подключении
    if LATEST_ALERTS:
        try:
            await websocket.send(json.dumps({
                "type": "history",
                "count": len(LATEST_ALERTS),
                "alerts": LATEST_ALERTS
            }))
        except Exception as e:
            logger.error(f"Failed to send history: {str(e)}")

    while True:
        try:
            # Создаем или пересоздаем потребителя Kafka
            if consumer is None:
                consumer = create_kafka_consumer()
                consumer.subscribe(['alerts'])
                logger.info("Kafka consumer created and subscribed")
                retry_count = 0

            # Обработка сообщений из Kafka
            msg = consumer.poll(1.0)

            if msg is None:
                await asyncio.sleep(0.1)
                continue

            if msg.error():
                if msg.error().code() == KafkaException._PARTITION_EOF:
                    # Конец раздела - нормальная ситуация
                    continue
                else:
                    logger.error(f"Kafka error: {msg.error()}")
                    raise KafkaException(msg.error())

            # Отправка сообщения через WebSocket
            try:
                message_data = msg.value().decode('utf-8')
                alert = json.loads(message_data)

                # Добавляем в историю
                add_alert_to_history(alert)

                await websocket.send(json.dumps({
                    "type": "new_alert",
                    "alert": alert
                }))

                logger.debug(f"Sent new alert to WebSocket")
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.error(f"WebSocket send error: {str(e)}")
                break

        except KafkaException as e:
            logger.error(f"Kafka exception: {str(e)}")
            consumer = None
            retry_count += 1

            if retry_count > max_retries:
                logger.error("Max Kafka retries reached. Closing connection.")
                break

            logger.info(f"Reconnecting to Kafka in 5 seconds... ({retry_count}/{max_retries})")
            await asyncio.sleep(5)

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            break

    # Очистка ресурсов при закрытии соединения
    try:
        if consumer:
            consumer.close()
            logger.info("Kafka consumer closed")
    except Exception as e:
        logger.error(f"Error closing consumer: {str(e)}")

    logger.info(f"WebSocket connection closed for {client_ip}")


async def get_latest_alerts(request):
    """HTTP endpoint для получения последних алертов"""
    count = int(request.query.get('count', 10))
    return web.json_response({
        "status": "success",
        "count": len(LATEST_ALERTS[:count]),
        "alerts": LATEST_ALERTS[:count]
    })


async def start_servers():
    """Запуск HTTP и WebSocket серверов"""
    # HTTP сервер
    app = web.Application()
    app.add_routes([
        web.get('/api/alerts', get_latest_alerts)
    ])
    runner = web.AppRunner(app)
    await runner.setup()
    http_site = web.TCPSite(runner, '0.0.0.0', 8766)
    await http_site.start()
    logger.info("HTTP server started on port 8766")

    # WebSocket сервер
    ws_server = await websockets.serve(
        handle_websocket,
        "0.0.0.0",
        8765,
        ping_interval=20,
        ping_timeout=30
    )
    logger.info("WebSocket server started on port 8765")

    return ws_server, runner


async def main():
    """Основная функция запуска серверов"""
    logger.info("Starting servers...")
    ws_server, http_runner = await start_servers()

    # Ожидание завершения
    try:
        await ws_server.wait_closed()
    except asyncio.CancelledError:
        logger.info("Servers shutting down")
        ws_server.close()
        await ws_server.wait_closed()
        await http_runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())