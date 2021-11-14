"""Defines core consumer functionality"""
import logging

import confluent_kafka
from confluent_kafka import Consumer, OFFSET_BEGINNING
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError
from tornado import gen


logger = logging.getLogger(__name__)


class KafkaConsumer:
    """Defines the base kafka consumer class"""

    def __init__(
        self,
        topic_name_pattern,
        message_handler,
        is_avro=True,
        offset_earliest=False,
        sleep_secs=1.0,
        consume_timeout=0.1,
    ):
        """Creates a consumer object for asynchronous use"""
        self.topic_name_pattern = topic_name_pattern
        self.message_handler = message_handler
        self.sleep_secs = sleep_secs
        self.consume_timeout = consume_timeout
        self.offset_earliest = offset_earliest


        self.broker_properties = {
            "bootstrap.servers": "PLAINTEXT://localhost:9092",
            "group.id":f"{self.topic_name_pattern}",
            'default.topic.config': {
                'auto.offset.reset': 'earliest' if offset_earliest else 'latest'
            }
        }

        if is_avro is True:
            self.broker_properties["schema.registry.url"]= "http://localhost:8081"
            self.consumer = AvroConsumer(self.broker_properties)
        else:
            self.consumer = Consumer(self.broker_properties)
            pass


        self.consumer.subscribe(topics=[self.topic_name_pattern], on_assign= self.on_assign )

    def on_assign(self, consumer, partitions):
        """Callback for when topic assignment takes place"""
        for partition in partitions:
           if self.offset_earliest:
               partition.offset = OFFSET_BEGINNING

        logger.info("partitions assigned for %s", self.topic_name_pattern)
        consumer.assign(partitions)

    async def consume(self):
        """Asynchronously consumes data from kafka topic"""
        while True:
            num_results = 1
            while num_results > 0:
                num_results = self._consume()
            await gen.sleep(self.sleep_secs)

    def _consume(self):
        while True:
            message = self.consumer.poll(1.0)
            if message is None:
                return 0
            elif message.error() is not None:
                print(f"error from consumer {message.error()}")
                return 0
            else:
                #print(f"consumed message {message.key()}: {message.value()}")
                self.message_handler(message)
                return 1


    def close(self):
        self.consumer.close()
