import json
import logging
import requests


logger = logging.getLogger(__name__)
KAFKA_CONNECT_URL = "http://localhost:8083/connectors"
CONNECTOR_NAME = "stations"

def configure_connector():
    """Starts and configures the Kafka Connect connector"""
    logging.debug("creating or updating kafka connect connector...")

    resp = requests.get(f"{KAFKA_CONNECT_URL}/{CONNECTOR_NAME}")
    if resp.status_code == 200:
        logging.debug("connector already created skipping recreation")
        return

    logger.info("Reading from Kafka connector")
    resp = requests.post(
        KAFKA_CONNECT_URL,
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "name": CONNECTOR_NAME,
            "config": {
                "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",
                "key.converter": "org.apache.kafka.connect.json.JsonConverter",
                "key.converter.schemas.enable": "false",
                "value.converter": "org.apache.kafka.connect.json.JsonConverter",
                "value.converter.schemas.enable": "false",
                "batch.max.rows": "500",
                "connection.url": "jdbc:postgresql://192.168.86.116:5432/cta",
                "connection.user": "cta_admin",
                "connection.password": "chicago",
                "table.whitelist": "stations",
                "mode": "incrementing",
                "incrementing.column.name": "stop_id",
                "topic.prefix": "topic_kafka_connector_",
                "poll.interval.ms": "86400000", # polls every day once
            }
        }),
    )
    try:
        ## Ensure a healthy response was given
        resp.raise_for_status()
        logging.debug("connector created successfully")
    except Exception as err:
        logging.error("Execption occured in kafka jdbc connector while trying to read stations data ", err)


if __name__ == "__main__":
    configure_connector()