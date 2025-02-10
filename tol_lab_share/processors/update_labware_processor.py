from typing import Any
from lab_share_lib.processing.base_processor import BaseProcessor
from lab_share_lib.processing.rabbit_message import RabbitMessage
from lab_share_lib.rabbit.avro_encoder import AvroEncoderBinary
from lab_share_lib.rabbit.basic_publisher import BasicPublisher
from lab_share_lib.rabbit.schema_registry import SchemaRegistry

import logging

from tol_lab_share.constants import (
    RABBITMQ_SUBJECT_UPDATE_LABWARE_FEEDBACK,
    RABBITMQ_ROUTING_KEY_UPDATE_LABWARE_FEEDBACK,
)
from lab_share_lib.constants import RABBITMQ_HEADER_VALUE_ENCODER_TYPE_BINARY

logger = logging.getLogger(__name__)


class UpdateLabwareProcessor(BaseProcessor):
    """Class to handle consuming update-labware messages from TOL"""

    def __init__(self, schema_registry: SchemaRegistry, basic_publisher: BasicPublisher, config: Any):
        """Resets data for the processor
        Parameters:
        schema_registry (SchemaRegistry) the redpanda schema registry we will us to validate messages
        basic_publisher (BasicPublisher) instance that will provide the communication with the queues system
        config (Any) mainconfiguration from the app
        """
        logger.debug("UpdateLabwareProcessor::__init__")
        self._encoder = AvroEncoderBinary(schema_registry, RABBITMQ_SUBJECT_UPDATE_LABWARE_FEEDBACK)
        self._basic_publisher = basic_publisher
        self._config = config

    @staticmethod
    def instantiate(
        schema_registry: SchemaRegistry, basic_publisher: BasicPublisher, config: Any
    ) -> "UpdateLabwareProcessor":
        """Instantiate a UpdateLabwareProcessor"""
        return UpdateLabwareProcessor(schema_registry, basic_publisher, config)

    def process(self, message: RabbitMessage) -> bool:
        """Consumes a message for updating labware information. At now no relevant action is attached to
        this.
        Returns:
        bool indicating if the message was correctly consumed
        """
        logger.debug("UpdateLabwareProcessor::process")

        message = {
            "sourceMessageUuid": str(message.message["messageUuid"].decode()),
            "operationWasErrorFree": str(True),
            "errors": [],
        }

        encoded_message = self._encoder.encode([message])

        logger.debug(f"Sending: {encoded_message}")

        self._basic_publisher.publish_message(
            "psd.tol",
            RABBITMQ_ROUTING_KEY_UPDATE_LABWARE_FEEDBACK,
            encoded_message.body,
            RABBITMQ_SUBJECT_UPDATE_LABWARE_FEEDBACK,
            encoded_message.version,
            RABBITMQ_HEADER_VALUE_ENCODER_TYPE_BINARY,
        )

        return True
