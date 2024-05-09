from .uuid import Uuid
from .labware_type import LabwareType
from tol_lab_share.constants.input_bioscan_pool_xp_to_traction_message import (
    REQUEST_COST_CODE,
    REQUEST_GENOME_SIZE,
    REQUEST_LIBRARY_TYPE,
    REQUEST_STUDY_UUID,
)
from tol_lab_share.messages.properties.simple import DictValue, StringValue
from tol_lab_share.messages.traction import TractionReceptionMessage

from tol_lab_share.messages.properties import MessageProperty
from functools import singledispatchmethod

import logging

logger = logging.getLogger(__name__)


class Request(MessageProperty):
    """MessageProperty that handles the parsing of a request section for TOL messages."""

    def __init__(self, input: MessageProperty):
        super().__init__(input)

        self.add_property("cost_code", LabwareType(DictValue(input, REQUEST_COST_CODE)))
        self.add_property("genome_size", StringValue(DictValue(input, REQUEST_GENOME_SIZE)))
        self.add_property("library_type", StringValue(DictValue(input, REQUEST_LIBRARY_TYPE)))
        self.add_property("study_uuid", Uuid(DictValue(input, REQUEST_STUDY_UUID)))

    @singledispatchmethod
    def add_to_message_property(self, message_property: MessageProperty) -> None:
        super().add_to_message_property(message_property)

    @add_to_message_property.register
    def _(self, message: TractionReceptionMessage) -> None:
        """Adds the request information to an OutputTractionMessage.

        Args:
            message (TractionReceptionMessage): The Traction reception message to add the data to.
        """
        super().add_to_message_property(message)
