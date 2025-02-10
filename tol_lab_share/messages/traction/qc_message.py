from functools import singledispatchmethod
import logging
from json import dumps
from typing import Any, Callable

from requests import codes, post

from lab_share_lib.exceptions import TransientRabbitError
from tol_lab_share import error_codes
from tol_lab_share.constants import OUTPUT_TRACTION_MESSAGE_SOURCE
from tol_lab_share.error_codes import ErrorCode
from tol_lab_share.helpers import get_config
from tol_lab_share.messages.properties import MessageProperty
from tol_lab_share.messages.properties.simple import Value
from tol_lab_share.messages.rabbit.published import CreateLabwareFeedbackMessage

logger = logging.getLogger(__name__)


class TractionQcMessageRequest:
    """Class that holds the information for a Traction QC message request."""

    def __init__(self):
        """Constructor to initialize the info for the request."""
        self.container_barcode: str | None = None
        self.date_submitted_utc: float | None = None
        self.final_nano_drop: str | None = None
        self.final_nano_drop_230: str | None = None
        self.final_nano_drop_280: str | None = None
        self.post_spri_concentration: str | None = None
        self.post_spri_volume: str | None = None
        self.sanger_sample_id: str | None = None
        self.sheared_femto_fragment_size: str | None = None
        self.shearing_qc_comments: str | None = None

    def validate(self) -> bool:
        """Validate that the request has all the required information.

        Returns:
            bool: True if the request is valid; otherwise False.
        """
        return (
            (self.sanger_sample_id is not None)
            and (self.container_barcode is not None)
            and (self.sheared_femto_fragment_size is not None)
            and (self.post_spri_concentration is not None)
            and (self.post_spri_volume is not None)
            and (self.final_nano_drop_280 is not None)
            and (self.final_nano_drop_230 is not None)
            and (self.final_nano_drop is not None)
            and (self.shearing_qc_comments is not None)
            and (self.date_submitted_utc is not None)
        )


class QcRequestSerializer:
    """Class to manage the serialization to JSON of the request received as argument in the constructor."""

    def __init__(self, instance: TractionQcMessageRequest):
        """Constructor that sets initial state of the instance.

        Args:
            instance (TractionQcMessageRequest): The request to serialize.
        """
        self.instance = instance

    def payload(self) -> dict[str, Any]:
        """Prepare a payload for the TractionQcMessageRequest.

        Returns:
            dict[str, Any]: The payload for the request.  No entries for empty values will be included.
        """
        obj = {
            "sheared_femto_fragment_size": self.instance.sheared_femto_fragment_size,
            "post_spri_concentration": self.instance.post_spri_concentration,
            "post_spri_volume": self.instance.post_spri_volume,
            "final_nano_drop_280": self.instance.final_nano_drop_280,
            "final_nano_drop_230": self.instance.final_nano_drop_230,
            "final_nano_drop": self.instance.final_nano_drop,
            "shearing_qc_comments": self.instance.shearing_qc_comments,
            "sample_external_id": self.instance.sanger_sample_id,
            "labware_barcode": self.instance.container_barcode,
            "date_submitted": self.instance.date_submitted_utc,
        }
        return self.clear_empty_value_keys(obj)

    def clear_empty_value_keys(self, obj: dict[str, Any]) -> dict[str, Any]:
        return {k: v for k, v in obj.items() if v}


class TractionQcMessage(MessageProperty):
    """Class that handle the generation and publishing of a QC message to Traction"""

    def __init__(self):
        """Resets initial data"""
        super().__init__(Value(self))
        self._requests: list[TractionQcMessageRequest] = []
        self._sent = False
        self._validate_certificates = get_config().CERTIFICATES_VALIDATION_ENABLED

    @property
    def origin(self) -> str:
        """Default origin identifier. This will be appended to any errors generated to know
        where it was originated when we received
        """
        return "TractionQcMessage"

    @property
    def validators(self) -> list[Callable]:
        """A list of validators to check the message is correct before sending."""
        return [self.check_has_requests, self.check_requests_have_all_content, self.check_no_errors]

    def create_request(self) -> TractionQcMessageRequest:
        """Creates a new request and returns it. It will be appended to the list of requests.

        Returns:
            TractionQcMessageRequest: The newly created request.
        """
        self._requests.append(TractionQcMessageRequest())
        return self._requests[-1]

    def request_attributes(self) -> list[dict[str, Any]]:
        """Prepare a payload for all the QC data of every request.

        Returns:
            list[dict[str,Any]]: The payload for all the requests.
        """
        return [QcRequestSerializer(request).payload() for request in self._requests]

    @property
    def errors(self) -> list[ErrorCode]:
        """The list of errors defined for this message"""
        return self._errors

    def check_has_requests(self) -> bool:
        """Check whether the message has requests. If not an error will be triggered.

        Returns
            bool: True if the message has requests; otherwise False.
        """
        if self._requests:
            return True

        self.trigger_error(error_codes.ERROR_25_TRACTION_QC_MESSAGE_HAS_NO_REQUESTS)
        return False

    def check_no_errors(self) -> bool:
        """Checks that a message has no errors.

        Returns:
            bool: True if there are no errors; otherwise False.
        """
        return not self.errors

    def check_requests_have_all_content(self) -> bool:
        """Checks that all requests provided are valid. Triggers an error if any is not.

        Returns:
            bool: True if all requests validate; otherwise False.
        """
        if all([request.validate() for request in self._requests]):
            return True

        self.trigger_error(error_codes.ERROR_26_TRACTION_QC_MESSAGE_REQUESTS_HAVE_MISSING_DATA)
        return False

    def payload(self) -> dict[str, Any]:
        """Prepare a valid payload to send to traction.

        Returns:
            dict[str, Any]: The payload.
        """
        return {
            "data": {
                "type": "qc_receptions",
                "attributes": {
                    "source": OUTPUT_TRACTION_MESSAGE_SOURCE,
                    "qc_results_list": self.request_attributes(),
                },
            }
        }

    def error_code_traction_problem(self, status_code: int, error_str: str) -> None:
        """Triggers an error indicating that traction failed.

        Args:
            status_code (int): HTTP status code when sending to traction (422, 500, etc)
            error_str (str): contents received by Traction endpoint on the request
        """
        self.trigger_error(
            error_codes.ERROR_27_TRACTION_QC_REQUEST_FAILED, text=f"HTTP CODE: {status_code}, MSG: {error_str}"
        )

    def raise_submission_error(self, cause: Exception | None = None) -> None:
        """Raises an error when submitting the message to Traction with an optional cause exception.

        Args:
            cause (Exception): The exception that caused the need to raise.

        Raises:
            TransientRabbitError: Always raised to cause a 30 second delay before trying to process the message again.
        """
        logger.critical(f"Error submitting {self.__class__.__name__} to the Traction API.")
        if cause:
            logger.exception(cause)

        raise TransientRabbitError(f"There was an error POSTing the {self.__class__.__name__} to the Traction API.")

    def send(self, url: str) -> bool:
        """Sends a request to Traction. If is correct returns true, if not it will trigger an error and
        return False

        Args:
            url (str): url where it will send the Traction qc request

        Returns:
            bool indicating if the request was successful
        """
        headers = {"Content-type": "application/vnd.api+json", "Accept": "application/vnd.api+json"}

        try:
            r = post(url, headers=headers, data=dumps(self.payload(), default=str), verify=self._validate_certificates)
        except Exception as ex:
            self.raise_submission_error(ex)

        if r.status_code == codes.bad_gateway:
            self.raise_submission_error()

        self._sent = r.status_code == codes.created
        if not self._sent:
            problem = r.text
            self.error_code_traction_problem(r.status_code, problem)

        return self._sent

    @singledispatchmethod
    def add_to_message_property(self, message_property: MessageProperty) -> None:
        super().add_to_message_property(message_property)

    @add_to_message_property.register
    def _(self, feedback_message: CreateLabwareFeedbackMessage) -> None:
        """Adds errors about this TractionQcMessage to an CreateLabwareFeedbackMessage.
        Also sets the operation_was_error_free to False if the message was not sent.

        Args:
            feedback_message (CreateLabwareFeedbackMessage): The CreateLabwareFeedbackMessage to add the errors to.
        """
        if not self._sent:
            feedback_message.operation_was_error_free = False
        if len(self._errors) > 0:
            for error_code in self._errors:
                feedback_message.add_error(error_code)
