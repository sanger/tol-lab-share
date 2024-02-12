from functools import singledispatchmethod
from typing import Callable, Any
from json import dumps
from datetime import datetime
from requests import post, codes
from tol_lab_share.message_properties.definitions.message_property import MessageProperty
from tol_lab_share.message_properties.definitions.input import Input
from tol_lab_share.constants import (
    OUTPUT_TRACTION_MESSAGE_CONTAINER_TYPES,
    OUTPUT_TRACTION_MESSAGE_SOURCE,
)
from tol_lab_share import error_codes
from tol_lab_share.error_codes import ErrorCode
from tol_lab_share.helpers import get_config
from tol_lab_share.messages.output_feedback_message import OutputFeedbackMessage


class OutputTractionMessageRequest:
    """Class that manages the information of a single Traction request instance
    as part of the Traction message
    """

    def __init__(self):
        """Constructor that initializes all info for a single request."""
        self.accession_number: str | None = None
        self.container_barcode: str | None = None
        self.container_location: str | None = None
        self.container_type: OUTPUT_TRACTION_MESSAGE_CONTAINER_TYPES | None = None
        self.cost_code: str | None = None
        self.country_of_origin: str | None = None
        self.date_of_sample_collection: datetime | None = None
        self.donor_id: str | None = None
        self.library_type: str | None = None
        self.priority_level: str | None = None
        self.public_name: str | None = None
        self.sample_name: str | None = None
        self.sample_uuid: str | None = None
        self.sanger_sample_id: str | None = None
        self.species: str | None = None
        self.study_uuid: str | None = None
        self.supplier_name: str | None = None
        self.taxon_id: str | None = None

    def validate(self) -> bool:
        """Checks that we have all required information and that it is valid before marking this request as valid."""
        return (
            (self.library_type is not None)
            and (self.study_uuid is not None)
            and (self.sample_name is not None)
            and (self.container_barcode is not None)
            and (self.species is not None)
            and (self.container_type is not None)
            and (self.species is not None)
        )

    def serializer(self):
        """Returns a serializer instance to handle the generation of the message for this request.
        Returns:
        RequestSerializer instance for this request
        """
        return RequestSerializer(self)


class RequestSerializer:
    """Class to manage the serialization to JSON of the request received as argument in the constructor."""

    def __init__(self, instance: OutputTractionMessageRequest):
        """Constructor that sets the initial state of the instance.

        Args:
            instance (OutputTractionMessageRequest): The request that we want to serialize.
        """
        self.instance = instance

    def is_ont_library_type(self) -> bool:
        """Flag boolean method that identifies if the library type is ONT.

        Returns:
            bool: True if the library type is ONT; otherwise false.
        """
        return bool(self.instance.library_type and ("ONT" in self.instance.library_type))

    def request_payload(self) -> dict[str, Any]:
        """Generates the correct payload depending on the library type for the current request.
        Returns:
        Dic[str,str] with the required information to send for this request to Traction
        """
        if self.is_ont_library_type():
            return {
                "data_type": "basecalls",
                "library_type": self.instance.library_type,
                "external_study_id": self.instance.study_uuid,
                "cost_code": self.instance.cost_code,
            }
        else:
            return {
                "library_type": self.instance.library_type,
                "external_study_id": self.instance.study_uuid,
                "cost_code": self.instance.cost_code,
            }

    def sample_payload(self) -> dict[str, Any]:
        """Generates the correct payload for the sample defined in this request
        Returns:
        Dic[str,str] with the required sample information to send for this request to Traction
        """
        collection_date = None
        if self.instance.date_of_sample_collection is not None:
            collection_date = self.instance.date_of_sample_collection.strftime("%Y-%m-%d")
        return {
            "name": self.instance.sample_name,
            "external_id": self.instance.sample_uuid,
            "species": self.instance.species,
            "priority_level": self.instance.priority_level,
            "sanger_sample_id": self.instance.sanger_sample_id,
            "supplier_name": self.instance.supplier_name,
            "public_name": self.instance.public_name,
            "taxon_id": self.instance.taxon_id,
            "donor_id": self.instance.donor_id,
            "country_of_origin": self.instance.country_of_origin,
            "accession_number": self.instance.accession_number,
            "date_of_sample_collection": collection_date,
        }

    def container_payload(self) -> dict[str, Any]:
        """Generates the correct payload for the container defined in this request depending on
        the container type (tubes or wells)
        Returns:
        Dic[str,str] with the required container information to send for this request to Traction
        """
        if self.instance.container_type == "tubes":
            return {"type": self.instance.container_type, "barcode": self.instance.container_barcode}
        else:
            return {
                "type": self.instance.container_type,
                "barcode": self.instance.container_barcode,
                "position": self.instance.container_location,
            }

    def payload(self) -> dict[str, Any]:
        """Main builder of the payload required to describe all information required for Traction:
        sample, request and container.
        Returns:
        Dic[str,str] with all the required payload information for Traction
        """
        return {
            "request": self.request_payload(),
            "sample": self.sample_payload(),
            "container": self.container_payload(),
        }


class OutputTractionMessage(MessageProperty):
    """Class that handles the generation and publishing of a message to Traction."""

    def __init__(self):
        """Reset initial data."""
        super().__init__(Input(self))
        self._requests: list[OutputTractionMessageRequest] = []
        self._sent = False
        self._validate_certificates = get_config().CERTIFICATES_VALIDATION_ENABLED

    @property
    def origin(self) -> str:
        """Default origin identifier. This will be appended to any errors generated to know where it was originated
        when we received it.
        """
        return "OutputFeedbackMessage"

    @property
    def validators(self) -> list[Callable]:
        """list of validators to check the message is correct before sending"""
        return [self.check_has_requests, self.check_requests_have_all_content, self.check_no_errors]

    def create_request(self) -> OutputTractionMessageRequest:
        """Creates a new request and returns it. It will be appended to the list of requests.

        Returns:
            OutputTractionMessageRequest: The newly created request.
        """
        self._requests.append(OutputTractionMessageRequest())
        return self._requests[-1]

    def request_attributes(self) -> list[dict[str, Any]]:
        """Returns a list with all the payloads for every request

        Returns:
            list[dict[str,Any]] with all payloads for all the requests
        """
        return [request.serializer().payload() for request in self._requests]

    @property
    def errors(self) -> list[ErrorCode]:
        """list of errors defined for this message"""
        return self._errors

    def check_has_requests(self) -> bool:
        """Returns a bool identifying if the message has requests. If not it will trigger an error and
        return false.

        Returns
            bool saying if the message has requests
        """
        if self._requests:
            return True

        self.trigger_error(error_codes.ERROR_23_TRACTION_MESSAGE_HAS_NO_REQUESTS)
        return False

    def check_no_errors(self) -> bool:
        """Checks that a message has no errors

        Returns:
            bool indicating if there is no errors
        """
        return not self.errors

    def check_requests_have_all_content(self) -> bool:
        """Checks that all requests provided are valid. Triggers an error if any is not.

        Returns:
            bool indicating that all requests have valid content inside.
        """
        if all([request.validate() for request in self._requests]):
            return True

        self.trigger_error(error_codes.ERROR_24_TRACTION_MESSAGE_REQUESTS_HAVE_MISSING_DATA)
        return False

    def payload(self) -> dict[str, Any]:
        """Returns the valid payload to send to traction"""
        return {
            "data": {
                "type": "receptions",
                "attributes": {
                    "source": OUTPUT_TRACTION_MESSAGE_SOURCE,
                    "request_attributes": self.request_attributes(),
                },
            }
        }

    def error_code_traction_problem(self, status_code: int, error_str: str) -> None:
        """Triggers an error indicating that traction failed.

        Args:
            status_code (int) HTTP status code when sending to traction (422, 500, etc)
            error_str (str) contents received by Traction endpoint on the request
        """
        self.trigger_error(
            error_codes.ERROR_13_TRACTION_REQUEST_FAILED, text=f"HTTP CODE: { status_code }, MSG: {error_str}"
        )

    def send(self, url: str) -> bool:
        """Sends a request to Traction. If is correct returns true, if not it will trigger an error and
        return False

        Args:
            url (str) url where it will send the Traction request

        Returns:
            bool indicating if the request was successful
        """
        headers = {"Content-type": "application/vnd.api+json", "Accept": "application/vnd.api+json"}

        r = post(url, headers=headers, data=dumps(self.payload()), verify=self._validate_certificates)

        self._sent = r.status_code == codes.created
        if not self._sent:
            problem = r.text
            self.error_code_traction_problem(r.status_code, problem)

        return self._sent

    @singledispatchmethod
    def add_to_message_property(self, message_property: MessageProperty) -> None:
        super().add_to_message_property(message_property)

    @add_to_message_property.register
    def _(self, feedback_message: OutputFeedbackMessage) -> None:
        """Adds error information to the an OutputFeedbackMessage.
        Also sets the operation_was_error_free to False if the message has not been sent.

        Args:
            feedback_message (OutputFeedbackMessage): The OutputFeedbackMessage to add errors to.
        """
        if not self._sent:
            feedback_message.operation_was_error_free = False
        if len(self._errors) > 0:
            for error_code in self._errors:
                feedback_message.add_error(error_code)
