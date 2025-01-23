from functools import singledispatchmethod
import itertools
import logging
from typing import Callable, Any
from json import dumps
from datetime import datetime
from requests import post, codes
from lab_share_lib.exceptions import TransientRabbitError
from tol_lab_share.messages.properties import MessageProperty
from tol_lab_share.messages.properties.simple import Value
from tol_lab_share.constants import (
    OUTPUT_TRACTION_MESSAGE_CONTAINER_TYPES,
    OUTPUT_TRACTION_MESSAGE_SOURCE,
)
from tol_lab_share import error_codes
from tol_lab_share.error_codes import ErrorCode
from tol_lab_share.helpers import get_config
from tol_lab_share.messages.rabbit.published import CreateLabwareFeedbackMessage

logger = logging.getLogger(__name__)


class TractionReceptionMessageRequest:
    """Class that manages the information of a single Traction request instance as part of the Traction message."""

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
        self.genome_size: str | None = None
        self.library_concentration: float | None = None
        self.library_insert_size: int | None = None
        self.library_type: str | None = None
        self.library_volume: float | None = None
        self.priority_level: str | None = None
        self.public_name: str | None = None
        self.sample_name: str | None = None
        self.sample_uuid: str | None = None
        self.sanger_sample_id: str | None = None
        self.species: str | None = None
        self.study_uuid: str | None = None
        self.supplier_name: str | None = None
        self.taxon_id: str | None = None
        self.template_prep_kit_box_barcode: str | None = None
        self.retention_instruction: str | None = None

    def validate(self) -> bool:
        """Validate the information in this request.

        Returns:
            bool: True if the request is valid; otherwise False.
        """
        return (
            (self.library_type is not None)
            and (self.study_uuid is not None)
            and (self.sample_name is not None)
            and (self.container_barcode is not None)
            and (self.species is not None)
            and (self.container_type is not None)
            and (self.species is not None)
        )


class Serializer:
    """Class to manage the serialization of requests."""

    @staticmethod
    def library_payload(request: TractionReceptionMessageRequest) -> dict[str, Any]:
        """Generate the library payload for the given request.

        Args:
            request (TractionReceptionMessageRequest): The request to generate the payload for.

        Returns:
            dict[str, Any]: A dictionary containing the Traction "request" payload for the request.
        """
        library_payload = {
            "volume": request.library_volume,
            "template_prep_kit_box_barcode": request.template_prep_kit_box_barcode,
            "concentration": request.library_concentration,
            "insert_size": request.library_insert_size,
        }

        return library_payload

    @staticmethod
    def request_payload(request: TractionReceptionMessageRequest) -> dict[str, Any]:
        """Generate the request payload for the given request.
        The payload varies depending on whether the library type is ONT or not.

        Args:
            request (TractionReceptionMessageRequest): The request to generate the payload for.

        Returns:
            dict[str, Any]: A dictionary containing the Traction "request" payload for the request.
        """
        request_payload = {
            "cost_code": request.cost_code,
            "estimate_of_gb_required": request.genome_size,
            "external_study_id": request.study_uuid,
            "library_type": request.library_type,
        }

        if request.library_type and ("ONT" in request.library_type):
            request_payload["data_type"] = "basecalls"

        return request_payload

    @staticmethod
    def sample_payload(request: TractionReceptionMessageRequest) -> dict[str, Any]:
        """Generate the sample payload for the given request.

        Args:
            request (TractionReceptionMessageRequest): The request to generate the payload for.

        Returns:
            dict[str, Any]: A dictionary containing the Traction "sample" payload for the request.
        """
        collection_date = None
        if request.date_of_sample_collection is not None:
            collection_date = request.date_of_sample_collection.strftime("%Y-%m-%d")

        return {
            "accession_number": request.accession_number,
            "country_of_origin": request.country_of_origin,
            "date_of_sample_collection": collection_date,
            "donor_id": request.donor_id,
            "external_id": request.sample_uuid,
            "name": request.sample_name,
            "priority_level": request.priority_level,
            "public_name": request.public_name,
            "sanger_sample_id": request.sanger_sample_id,
            "species": request.species,
            "supplier_name": request.supplier_name,
            "taxon_id": request.taxon_id,
            "retention_instruction": request.retention_instruction,
        }


class PlateSerializer(Serializer):
    """Class to manage the serialization of plate requests."""

    def __init__(self, plate_requests: list[TractionReceptionMessageRequest]):
        """Constructor.

        Args:
            plate_requests (list[TractionReceptionMessageRequest]): The list of requests to serialize for a single
                plate.
        """
        self._requests = plate_requests

    def well_attributes_payload(self) -> list[dict[str, Any]]:
        """Generate the well attributes payload for each of the plate's requests.

        Returns:
            list[dict[str, Any]]: A list containing the well attributes for all the request.
        """
        return [
            {
                "position": request.container_location,
                "request": self.request_payload(request),
                "sample": self.sample_payload(request),
            }
            for request in self._requests
        ]

    def payload(self) -> dict[str, Any]:
        """Generate a payload with the information required by Traction.

        Returns:
            dict[str, Any]: A dictionary containing the overall payload.
        """
        return {
            "barcode": self._requests[0].container_barcode,
            "type": "plates",
            "wells_attributes": self.well_attributes_payload(),
        }


class TubeSerializer(Serializer):
    """Class to manage the serialization of tube requests."""

    def __init__(self, tube_request: TractionReceptionMessageRequest):
        """Constructor.

        Args:
            tube_request (TractionReceptionMessageRequest): The request to serialize for a single tube.
        """
        self._request = tube_request

    def payload(self) -> dict[str, Any]:
        """Generate a payload with the information required by Traction.

        Returns:
            dict[str, Any]: A dictionary containing the overall payload.
        """
        payload = {
            "barcode": self._request.container_barcode,
            "type": "tubes",
            "request": self.request_payload(self._request),
            "sample": self.sample_payload(self._request),
        }

        library_payload = self.library_payload(self._request)
        if any([val is not None for val in library_payload.values()]):
            payload["library"] = library_payload

        return payload


class TractionReceptionMessage(MessageProperty):
    """Class that handles the generation and publishing of a reception message to Traction."""

    def __init__(self):
        """Reset initial data."""
        super().__init__(Value(self))
        self._requests: list[TractionReceptionMessageRequest] = []
        self._sent = False
        self._validate_certificates = get_config().CERTIFICATES_VALIDATION_ENABLED

    @property
    def origin(self) -> str:
        """The origin identifier for this message type.
        This will be appended to any errors generated via the `trigger_error` method.

        Returns:
            str: The origin identifier.
        """
        return "CreateLabwareFeedbackMessage"

    @property
    def validators(self) -> list[Callable]:
        """A list of validators to check the message is correct.

        Returns:
            list[Callable]: The list of methods to call for complete validation of this message.
        """
        return [self.check_has_requests, self.check_requests_have_all_content, self.check_no_errors]

    def create_request(self) -> TractionReceptionMessageRequest:
        """Creates a new request and returns it. It will be appended to the list of requests.

        Returns:
            TractionReceptionMessageRequest: The newly created request.
        """
        self._requests.append(TractionReceptionMessageRequest())
        return self._requests[-1]

    def plates_attributes(self) -> list[dict[str, Any]]:
        """Prepare a payload for all the request related to plates.

        Returns:
            list[dict[str, Any]]: A list containing the payload for all the plates.
        """
        # Group well requests by plate barcode
        well_requests = [request for request in self._requests if request.container_type == "wells"]
        well_requests.sort(key=lambda request: request.container_barcode or "")
        plate_requests = itertools.groupby(well_requests, lambda request: request.container_barcode)

        return [PlateSerializer(list(requests)).payload() for _, requests in plate_requests]

    def tubes_attributes(self) -> list[dict[str, Any]]:
        """Prepare a payload for all the requests related to tubes.

        Returns:
            list[dict[str, Any]]: A list containing the payload for all the tubes.
        """
        return [TubeSerializer(request).payload() for request in self._requests if request.container_type == "tubes"]

    @property
    def errors(self) -> list[ErrorCode]:
        """A list of errors defined for this message."""
        return self._errors

    def check_has_requests(self) -> bool:
        """Check that this message has associated requests.
        Even if there are no requests, this will not trigger an error.

        Returns:
            bool: True if there are registered requests; otherwise False.
        """
        if self._requests:
            return True

        self.trigger_error(error_codes.ERROR_23_TRACTION_MESSAGE_HAS_NO_REQUESTS)
        return False

    def check_no_errors(self) -> bool:
        """Check that the message has no errors.

        Returns:
            bool: True if there are no errors registered; otherwise False.
        """
        return not self.errors

    def check_requests_have_all_content(self) -> bool:
        """Checks that all requests provided have valid content.
        Triggers an error if any is not.

        Returns:
            bool: True if all requests validate successfully; otherwise False.
        """
        if all([request.validate() for request in self._requests]):
            return True

        self.trigger_error(error_codes.ERROR_24_TRACTION_MESSAGE_REQUESTS_HAVE_MISSING_DATA)
        return False

    def payload(self) -> dict[str, Any]:
        """Generates the payload to send to Traction.

        Returns:
            dict[str, Any]: The payload dictionary.
        """
        return {
            "data": {
                "type": "receptions",
                "attributes": {
                    "source": OUTPUT_TRACTION_MESSAGE_SOURCE,
                    "plates_attributes": self.plates_attributes(),
                    "tubes_attributes": self.tubes_attributes(),
                },
            }
        }

    def error_code_traction_problem(self, status_code: int, error_str: str) -> None:
        """Triggers an error indicating that Traction failed.

        Args:
            status_code (int): HTTP status code when sending to Traction (422, 500, etc)
            error_str (str): Error message received from the Traction endpoint.
        """
        self.trigger_error(
            error_codes.ERROR_13_TRACTION_REQUEST_FAILED, text=f"HTTP CODE: {status_code}, MSG: {error_str}"
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
        """Sends a Traction API request to the provided URL.
        If the send fails, an error code will be recorded.

        Args:
            url (str): The URL to submit the Traction request to.

        Returns:
            bool: True if the request was sent successfully; otherwise False.
        """
        headers = {"Content-type": "application/vnd.api+json", "Accept": "application/vnd.api+json"}

        try:
            r = post(url, headers=headers, data=dumps(self.payload()), verify=self._validate_certificates)
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
        """Adds error information to the an CreateLabwareFeedbackMessage.
        Also sets the operation_was_error_free to False if the message has not been sent.

        Args:
            feedback_message (CreateLabwareFeedbackMessage): The CreateLabwareFeedbackMessage to add errors to.
        """
        if not self._sent:
            feedback_message.operation_was_error_free = False
        if len(self._errors) > 0:
            for error_code in self._errors:
                feedback_message.add_error(error_code)
