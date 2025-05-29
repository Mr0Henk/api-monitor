import requests
import json
import time
import logging
from datetime import datetime, timezone
from confluent_kafka import KafkaException
from kafka_utils import create_kafka_producer, send_alert

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ApiChecker')


class ApiChecker:
    def __init__(self, config_path, kafka_topic='alerts'):
        self.config = self._load_config(config_path)
        self.kafka_topic = kafka_topic
        self.producer = self._init_kafka_producer()

    def _init_kafka_producer(self, retries=5, delay=5):
        """Инициализация продюсера Kafka с повторными попытками"""
        for i in range(retries):
            try:
                producer = create_kafka_producer()
                # Проверка подключения путем получения списка топиков
                producer.list_topics(timeout=10)
                logger.info("Successfully connected to Kafka")
                return producer
            except KafkaException as e:
                logger.warning(f"Kafka connection failed (attempt {i + 1}/{retries}): {str(e)}")
                time.sleep(delay)
        raise RuntimeError("Failed to connect to Kafka after multiple attempts")

    def _load_config(self, path):
        """Загрузка конфигурации API"""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            raise

    def _send_request(self, entry):
        """Отправка HTTP запроса"""
        method = entry['type'].lower()
        url = entry['url']
        options = entry.get('options', {})

        try:
            response = requests.request(
                method=method,
                url=url,
                **options,
                timeout=5
            )
            return response
        except Exception as e:
            logger.warning(f"Request failed: {url} - {str(e)}")
            return None

    def _process_response(self, entry, response):
        """Обработка HTTP ответа"""
        if response is None:
            return {
                "error": "Network error",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "url": entry['url'],
                "method": entry['type']
            }

        if 200 <= response.status_code < 400:
            return None

        return {
            "status_code": response.status_code,
            "response": response.text[:200],  # Ограничиваем размер ответа
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "url": entry['url'],
            "method": entry['type'],
            "options": entry.get('options', {})
        }

    def run(self):
        """Основной цикл проверки API"""
        logger.info("Starting API monitoring")
        while True:
            try:
                for entry in self.config:
                    response = self._send_request(entry)
                    alert_data = self._process_response(entry, response)

                    if alert_data:
                        try:
                            send_alert(
                                self.producer,
                                self.kafka_topic,
                                alert_data
                            )
                            logger.info(f"Alert sent for {entry['url']}")
                        except Exception as e:
                            logger.error(f"Failed to send alert: {str(e)}")

                time.sleep(10)
            except Exception as e:
                logger.error(f"Critical error in main loop: {str(e)}")
                time.sleep(30)  # Даем время на восстановление


if __name__ == "__main__":
    checker = ApiChecker('config/api_config.json')
    checker.run()