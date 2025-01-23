import json
import logging
from typing import Any, Callable

from lab_share_lib.rabbit.basic_publisher import BasicPublisher

from tol_lab_share.constants import RABBITMQ_ROUTING_KEY_CREATE_ALIQUOT
from tol_lab_share.error_codes import ErrorCode
from tol_lab_share.helpers import get_config
from tol_lab_share.messages.properties import MessageProperty
from tol_lab_share.messages.properties.simple import Value

logger = logging.getLogger(__name__)


class Aliquot:
    """Class that serialises into an aliquot"""

    def __init__(self):
        """Constructor that initializes an aliquot message"""
        self.id_lims: str | None = None
        self.aliquot_uuid: str | None = None
        self.aliquot_type: str | None = None
        self.source_type: str | None = None
        self.source_barcode: str | None = None
        self.sample_name: str | None = None
        self.used_by_type: str | None = None
        self.used_by_barcode: str | None = None
        self.volume: float | None = None
        self.concentration: float | None = None
        self.insert_size: int | None = None
        self.last_updated: str | None = None
        self.recorded_at: str | None = None
        self.created_at: str | None = None

    def to_dict(self) -> dict:
        """Convert the aliquot message to a JSON string"""
        return {
            "id_lims": self.id_lims,
            "aliquot_uuid": str(self.aliquot_uuid),
            "aliquot_type": self.aliquot_type,
            "source_type": self.source_type,
            "source_barcode": self.source_barcode,
            "sample_name": self.sample_name,
            "used_by_type": self.used_by_type,
            "used_by_barcode": self.used_by_barcode,
            "volume": self.volume,
            "concentration": self.concentration,
            "insert_size": self.insert_size,
            "last_updated": self.last_updated,
            "recorded_at": self.recorded_at,
            "created_at": self.created_at,
        }


class CreateAliquotInWarehouseMessage(MessageProperty):
    """Class that handles publishing of a volume tracking message to the warehouse"""

    def __init__(self):
        """Reset initial data"""
        super().__init__(Value(self))
        self.lims: str | None = None
        self.aliquot: Aliquot = Aliquot()
        self._sent = False
        self._validate_certificates = get_config().CERTIFICATES_VALIDATION_ENABLED

    @property
    def origin(self) -> Any:
        """The origin identifier for this message type.
        This will be appended to any errors generated via the `trigger_error` method.

        Returns:
            str: The origin identifier.
        """
        return "WarehouseReceptionMessage"

    @property
    def validators(self) -> "list[Callable]":
        return []

    @property
    def errors(self) -> "list[ErrorCode]":
        """A list of errors defined for this message."""
        return self._errors

    @staticmethod
    def create_aliquot_message():
        """Creates an empty warehouse message that should be populated by the mapper"""
        message = CreateAliquotInWarehouseMessage()
        message.aliquot = Aliquot()
        return message

    def check_no_errors(self) -> bool:
        """Check that the message has no errors.

        Returns:
            bool: True if there are no errors registered; otherwise False.
        """
        return not self.errors

    def to_string(self) -> str:
        """Returns a dict with the JSON-like representation of the message."""

        return json.dumps({"lims": self.lims, "aliquot": self.aliquot.to_dict()})

    def publish(self, publisher: BasicPublisher, exchange: str) -> None:
        """Publish a new message in the queue with the current contents of the feedback message
        Parameters:
        publisher (BasicPublisher) instance of basic publisher that we will use to connect to rabbitmq
        schema_registry (SchemaRegistry) instance of schema registry that we will use to retrieve data from redpanda
        exchange (str) name of the exchange where we will publish the message in Rabbitmq
        """
        message = self.to_string()
        routing_key = self._prepare_routing_key()
        logger.info(f"Sending json to the warehouse queue: {message}")
        publisher.publish_message(
            exchange,
            routing_key,
            message,
            None,
            None,
            None,
        )

    def check_errors_correct(self) -> bool:
        """Returns the aggregation result of the validation of all errors content"""
        return all([error.validate() for error in self.errors])

    @staticmethod
    def _prepare_routing_key() -> str:
        """Prepares the routing key for create aliquot message to be sent to warehouse RabbitMQ"""
        environment = get_config("").MLWH_ENVIRONMENT_NAME

        return RABBITMQ_ROUTING_KEY_CREATE_ALIQUOT.format(environment=environment)
