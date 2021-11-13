"""Contains functionality related to Weather"""
import logging
import json


logger = logging.getLogger(__name__)


class Weather:
    """Defines the Weather model"""

    def __init__(self):
        """Creates the weather model"""
        self.temperature = 70.0
        self.status = "sunny"

    def process_message(self, message):
        """Handles incoming weather data"""
        try:
            logger.info("processing weather data")
            value = message.value()
            value = json.loads(value)
            self.temperature = value["temperature"]
            self.status = value["status"]
        except Exception as e:
            print(e)