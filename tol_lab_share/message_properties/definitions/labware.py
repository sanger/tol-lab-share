import logging
from typing import Any, List

from tol_lab_share.constants import (
    OUTPUT_TRACTION_MESSAGE_CREATE_REQUEST_CONTAINER_TYPE_TUBES,
    OUTPUT_TRACTION_MESSAGE_CREATE_REQUEST_CONTAINER_TYPE_WELLS,
)
from tol_lab_share.constants.input_create_labware_message import BARCODE, LABWARE_TYPE, SAMPLES
from tol_lab_share.message_properties.definitions.barcode import Barcode
from tol_lab_share.message_properties.definitions.dict_input import DictInput
from tol_lab_share.message_properties.definitions.labware_type import LabwareType
from tol_lab_share.message_properties.definitions.sample import Sample
from tol_lab_share.message_properties.interfaces import MessagePropertyInterface
from tol_lab_share.messages.interfaces import OutputFeedbackMessageInterface
from tol_lab_share.messages.output_traction_message import OutputTractionMessageInterface
from tol_lab_share.messages.traction_qc_message import TractionQcMessageInterface

from .message_property import MessageProperty

logger = logging.getLogger(__name__)


class Labware(MessageProperty):
    """MessageProperty that handles the parsing of a labware section for the TOL message."""

    def __init__(self, input: MessageProperty):
        super().__init__(input)

        self.add_property("labware_type", LabwareType(DictInput(input, LABWARE_TYPE)))
        self.add_property("barcode", Barcode(DictInput(input, BARCODE)))
        self.add_property("samples", self._parse_samples(input))

    def _parse_samples(self, input: MessageProperty) -> List[MessagePropertyInterface]:
        """Parses the samples section and creates a sample for each position."""
        samples_dict = DictInput(input, SAMPLES)
        if samples_dict.validate():
            samples_list_dict: List[MessagePropertyInterface] = []
            for position in range(len(samples_dict.value)):
                sample = samples_dict.value[position]
                samples_list_dict.append(Sample(sample))
        else:
            samples_list_dict = [samples_dict]
        return samples_list_dict

    def labware_type(self) -> Any:
        """Returns the instance of LabwareType to is a property to this instance."""
        return self.properties("labware_type")

    def count_of_total_samples(self) -> int:
        """Returns the number of total samples inside this labware"""
        return len(self._properties["samples"])

    def count_of_valid_samples(self) -> int:
        """Returns the number of samples that are valid from this labware"""
        return [sample.validate() for sample in self._properties["samples"]].count(True)

    def add_to_feedback_message(self, feedback_message: OutputFeedbackMessageInterface) -> None:
        """Adds this labware information to the feedback message. It updates there the number
        of total samples and the number of valid samples.
        Parameters:
        feedback_message (OutputFeedbackInterface) Instance of the feedback message where we want
        to add the new data
        Returns:
        None"""
        logger.debug("Labware::add_to_feedback_message")
        super().add_to_feedback_message(feedback_message)
        feedback_message.count_of_total_samples = self.count_of_total_samples()
        feedback_message.count_of_valid_samples = self.count_of_valid_samples()

    def traction_container_type(self) -> str:
        """It converts the labware type to a valid container type value for
        Traction.
        Returns:
        str with a container type value for Traction
        """
        if self.labware_type().value == "Tube":
            return OUTPUT_TRACTION_MESSAGE_CREATE_REQUEST_CONTAINER_TYPE_TUBES
        else:
            return OUTPUT_TRACTION_MESSAGE_CREATE_REQUEST_CONTAINER_TYPE_WELLS

    def add_to_traction_message(self, traction_message: OutputTractionMessageInterface) -> None:
        """Given a traction message instance, it adds to the instance all the relevant information
        from the labware.
        Returns:
        None
        """
        super().add_to_traction_message(traction_message)
        for sample_pos in range(len(self.properties("samples"))):
            sample = self.properties("samples")[sample_pos]
            traction_message.requests(sample_pos).cost_code = sample.properties("cost_code").value
            traction_message.requests(sample_pos).study_uuid = sample.properties("study_uuid").value
            traction_message.requests(sample_pos).sample_name = sample.properties("public_name").value
            traction_message.requests(sample_pos).sample_uuid = sample.properties("uuid").value
            traction_message.requests(sample_pos).library_type = sample.properties("library_type").value
            traction_message.requests(sample_pos).species = sample.properties("scientific_name").value
            traction_message.requests(sample_pos).container_barcode = self.properties("barcode").value
            traction_message.requests(sample_pos).container_location = sample.properties("location").value
            traction_message.requests(sample_pos).container_type = self.traction_container_type()
            traction_message.requests(sample_pos).priority_level = sample.properties("priority_level").value
            traction_message.requests(sample_pos).sanger_sample_id = sample.properties("sanger_sample_id").value
            traction_message.requests(sample_pos).donor_id = sample.properties("donor_id").value
            traction_message.requests(sample_pos).country_of_origin = sample.properties("country_of_origin").value
            traction_message.requests(sample_pos).accession_number = sample.properties("accession_number").value
            traction_message.requests(sample_pos).supplier_name = sample.properties("supplier_sample_name").value

    def add_to_traction_qc_message(self, traction_qc_message: TractionQcMessageInterface) -> None:
        """Given a traction qc message instance, it adds the qc data.
        Returns:
        None
        """
        super().add_to_traction_qc_message(traction_qc_message)
        for sample_pos in range(len(self.properties("samples"))):
            sample = self.properties("samples")[sample_pos]
            traction_qc_message.requests(sample_pos).sheared_femto_fragment_size = sample.properties(
                "sheared_femto_fragment_size"
            ).value
            traction_qc_message.requests(sample_pos).post_spri_concentration = sample.properties(
                "post_spri_concentration"
            ).value
            traction_qc_message.requests(sample_pos).post_spri_volume = sample.properties("post_spri_volume").value
            traction_qc_message.requests(sample_pos).final_nano_drop_280 = sample.properties(
                "final_nano_drop_280"
            ).value
            traction_qc_message.requests(sample_pos).final_nano_drop_230 = sample.properties(
                "final_nano_drop_230"
            ).value
            traction_qc_message.requests(sample_pos).final_nano_drop = sample.properties("final_nano_drop").value
            traction_qc_message.requests(sample_pos).shearing_qc_comments = sample.properties(
                "shearing_qc_comments"
            ).value
            traction_qc_message.requests(sample_pos).date_submitted_utc = sample.properties("date_submitted_utc").value
            traction_qc_message.requests(sample_pos).container_barcode = self.properties("barcode").value
            traction_qc_message.requests(sample_pos).supplier_sample_name = sample.properties(
                "supplier_sample_name"
            ).value
