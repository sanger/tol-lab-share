from lab_share_lib.processing.rabbit_message import RabbitMessage
from tol_lab_share.constants import (
    INPUT_CREATE_LABWARE_MESSAGE_MESSAGE_UUID,
    INPUT_CREATE_LABWARE_MESSAGE_CREATED_DATE_UTC,
    INPUT_CREATE_LABWARE_MESSAGE_LABWARE,
)
from tol_lab_share.message_properties.definitions.message_uuid import MessageUuid
from tol_lab_share.message_properties.definitions.labware import Labware
from tol_lab_share.message_properties.definitions.date_utc import DateUtc
from tol_lab_share.message_properties.definitions.message_property import MessageProperty
from tol_lab_share.message_properties.definitions.dict_input import DictInput
from tol_lab_share.messages.interfaces import OutputFeedbackMessageInterface
from tol_lab_share.schema_versioning import SchemaVersioning
from functools import cached_property
import logging

logger = logging.getLogger(__name__)


class InputCreateLabwareMessage(MessageProperty):
    """Class that handles parsing a TOL lab share message received"""

    def __init__(self, m: RabbitMessage):
        """Constructor that receives a RabbitMessage and parses it using the properties defined
        Parameters:
        m (RabbitMessage) message we want to parse
        """
        super().__init__(m)
        self._message = m.message
        self.schema_versioning = SchemaVersioning(m.subject, m.schema_version)
        self.setup_properties()
    
    @cached_property
    def property_definitions(self):
        return [
            {
                "name": "message_uuid",
                "property": MessageUuid(DictInput(self._message, INPUT_CREATE_LABWARE_MESSAGE_MESSAGE_UUID)),
            },
            {
                "name": "labware",
                "property": Labware(DictInput(self._message, INPUT_CREATE_LABWARE_MESSAGE_LABWARE)),
            },
            {
                "name": "create_date_utc",
                "property": DateUtc(DictInput(self._message, INPUT_CREATE_LABWARE_MESSAGE_CREATED_DATE_UTC)),
            }
        ]

    def add_to_feedback_message(self, feedback_message: OutputFeedbackMessageInterface) -> None:
        """Given a feedback message, it adds all errors from this message into it. If there are
        any errors it changes the flag setting to indicate it.
        Parameters:
        feedback_message (OutputFeedbackMessageInterface) feedback message
        """
        logger.debug("InputCreateLabware::add_to_feedback_message")
        super().add_to_feedback_message(feedback_message)
        if len(self.errors) > 0:
            for error in self.errors:
                feedback_message.add_error(error)
            feedback_message.operation_was_error_free = False
