from tol_lab_share.constants.input_bioscan_pool_xp_to_traction_message import (
    MESSAGE_UUID,
    CREATED_DATE_UTC,
    TUBE_BARCODE,
    LIBRARY,
    REQUEST,
    SAMPLE,
)

from tol_lab_share.constants import (
    OUTPUT_BIOSCAN_TRACTION_MESSAGE_SOURCE
)
from tol_lab_share.messages.consumed.record import Record
from .library import Library
from .request import Request
from .sample import Sample

from tol_lab_share.messages.consumed.message_field import MessageField


class Root(Record):
    """The root record of a BioscanPoolXpToTraction message."""

    def __init__(self, payload: dict):
        """Initialises the root record.

        Args:
            payload (dict): The root message payload as a dictionary.
        """
        super().__init__(payload)

    @property
    def message_uuid(self) -> MessageField:
        """Gets the decoded message UUID as a string."""
        return self._make_field(MESSAGE_UUID, lambda v: v.decode())

    @property
    def create_date_utc(self) -> MessageField:
        """Gets the UTC creation date of the message as a datetime object."""
        return self._make_field(CREATED_DATE_UTC)

    @property
    def tube_barcode(self) -> MessageField:
        """Gets the tube barcode as a string."""
        return self._make_field(TUBE_BARCODE)

    @property
    def library(self) -> Library:
        """Gets the library record."""
        return Library(self._payload[LIBRARY], LIBRARY, self._path)

    @property
    def request(self) -> Request:
        """Gets the request record."""
        return Request(self._payload[REQUEST], REQUEST, self._path)

    @property
    def sample(self) -> Sample:
        """Gets the sample record."""
        return Sample(self._payload[SAMPLE], SAMPLE, self._path)


    @property
    def source(self) -> str:
        """Indicates this is a BioScan sample."""
        return OUTPUT_BIOSCAN_TRACTION_MESSAGE_SOURCE

