from lab_share_lib.rabbit.avro_encoder import AvroEncoderJson, AvroEncoderBinary
from lab_share_lib.constants import RABBITMQ_HEADER_VALUE_ENCODER_TYPE_BINARY, RABBITMQ_HEADER_VALUE_ENCODER_TYPE_JSON
from tol_lab_share.constants import (
    RABBITMQ_SUBJECT_CREATE_LABWARE_FEEDBACK,
    RABBITMQ_ROUTING_KEY_CREATE_LABWARE_FEEDBACK,
)
from tol_lab_share import error_codes
from tol_lab_share.messages.properties import MessageProperty
import logging
from tol_lab_share.helpers import get_config
from tol_lab_share.messages.properties.simple import Value
from typing import Any

from lab_share_lib.rabbit.basic_publisher import BasicPublisher
from lab_share_lib.rabbit.schema_registry import SchemaRegistry

logger = logging.getLogger(__name__)


class CreateLabwareFeedbackMessage(MessageProperty):
    """Class that handles the feedback message parsing for TOL lab share"""

    def __init__(self):
        """Constructor that resets the state of a feedback message"""
        super().__init__(Value(self))

        self.source_message_uuid: bytes | None = None
        self.count_of_total_samples: int | None = None
        self.count_of_valid_samples: int | None = None
        self.operation_was_error_free: bool = True

    @property
    def validators(self):
        """list of validators to apply to the message"""
        return [self.check_defined_keys, self.check_errors_correct]

    @property
    def origin(self):
        """ "Name of the origin for this property, set as a constant value."""
        return "CreateLabwareFeedbackMessage"

    def to_json(self) -> dict[str, Any]:
        """Returns a dict with the JSON-like representation of the message."""
        return {
            "sourceMessageUuid": str(self.source_message_uuid),
            "countOfTotalSamples": self.count_of_total_samples,
            "countOfValidSamples": self.count_of_valid_samples,
            "operationWasErrorFree": self.operation_was_error_free,
            "errors": [error.json() for error in self.errors],
        }

    def encoder_config_for(self, encoder_type_selection: str) -> dict[str, Any]:
        """Returns a config object with the encoder class and encoder type depending of the encoder selected."""
        if encoder_type_selection == "json":
            return {"encoder_class": AvroEncoderJson, "encoder_type": RABBITMQ_HEADER_VALUE_ENCODER_TYPE_JSON}
        else:
            return {"encoder_class": AvroEncoderBinary, "encoder_type": RABBITMQ_HEADER_VALUE_ENCODER_TYPE_BINARY}

    def publish(self, publisher: BasicPublisher, schema_registry: SchemaRegistry, exchange: str) -> None:
        """Publish a new message in the queue with the current contents of the feedback message
        Parameters:
        publisher (BasicPublisher) instance of basic publisher that we will use to connect to rabbitmq
        schema_registry (SchemaRegistry) instance of schema registry that we will use to retrieve data from redpanda
        exchange (str) name of the exchange where we will publish the message in Rabbitmq
        """
        encoder_selected = get_config("").SELECTED_ENCODER_FOR_FEEDBACK_MESSAGE
        encoder_class = self.encoder_config_for(encoder_selected)["encoder_class"]
        encoder_type = self.encoder_config_for(encoder_selected)["encoder_type"]

        encoder = encoder_class(schema_registry, RABBITMQ_SUBJECT_CREATE_LABWARE_FEEDBACK)

        message = self.to_json()
        encoded_message = None
        try:
            encoded_message = encoder.encode([message])
        except Exception as e:
            self.trigger_error(error_codes.ERROR_22_CANNOT_ENCODE_FEEDBACK_MESSAGE, text=str(e))
            return

        logger.info(f"Sending json: {message}")

        publisher.publish_message(
            exchange,
            RABBITMQ_ROUTING_KEY_CREATE_LABWARE_FEEDBACK,
            encoded_message.body,
            RABBITMQ_SUBJECT_CREATE_LABWARE_FEEDBACK,
            encoded_message.version,
            encoder_type,
        )

    def check_defined_keys(self) -> bool:
        """Checks that the message has defined all required keys, or trigger an error if not"""
        json = self.to_json()
        for key in ["sourceMessageUuid", "countOfTotalSamples", "countOfValidSamples", "operationWasErrorFree"]:
            if json[key] is None:
                self.trigger_error(
                    error_codes.ERROR_15_FEEDBACK_UNDEFINED_KEY,
                    text=f"Key {key} is undefined in feedback message",
                )

                return False
        return True

    def check_errors_correct(self) -> bool:
        """Returns the aggregation result of the validation of all errors content"""
        return all([error.validate() for error in self.errors])
