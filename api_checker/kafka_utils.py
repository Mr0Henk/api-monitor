from confluent_kafka import Producer
import json
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('KafkaUtils')

def create_kafka_producer(bootstrap_servers='kafka:9092'):
    """Создание продюсера Kafka"""
    return Producer({
        'bootstrap.servers': bootstrap_servers,
        'message.timeout.ms': 5000,  # Таймаут отправки сообщения
        'retries': 5,                # Количество попыток повторной отправки
        'retry.backoff.ms': 1000,     # Задержка между попытками
        'acks': 'all'                # Гарантированная доставка
    })

def send_alert(producer, topic, data):
    """Отправка алерта в Kafka"""
    try:
        producer.produce(
            topic=topic,
            value=json.dumps(data).encode('utf-8'),
            callback=lambda err, msg: delivery_report(err, msg, data)
        )
        producer.poll(0)  # Обработка событий
    except Exception as e:
        logger.error(f"Failed to produce message: {str(e)}")

def delivery_report(err, msg, data):
    """Обратный вызов для подтверждения доставки"""
    if err is not None:
        logger.error(f"Message delivery failed: {str(err)} for data: {data}")
    else:
        logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")