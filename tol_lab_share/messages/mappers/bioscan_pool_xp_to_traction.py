from tol_lab_share.messages.consumed import BioscanPoolXpToTractionMessage
from tol_lab_share.messages.traction.reception_message import TractionReceptionMessage


class BioscanPoolXpToTractionMapper:
    """A mapper for transferring values from a BioscanPoolXpToTractionMessage to a TractionReceptionMessage."""

    @staticmethod
    def map(source: BioscanPoolXpToTractionMessage, destination: TractionReceptionMessage) -> None:
        """Map the values from a BioscanPoolXpToTractionMessage to a TractionReceptionMessage.

        Args:
            source (BioscanPoolXpToTractionMessage): The source message to map from.
            destination (TractionReceptionMessage): The destination message to map to.
        """
        request = destination.create_request()

        request.container_type = "tubes"
        request.container_barcode = source.tube_barcode.value

        request.library_volume = source.library.volume.value
        request.library_concentration = source.library.concentration.value
        request.template_prep_kit_box_barcode = source.library.box_barcode.value
        request.library_insert_size = source.library.insert_size.value

        request.cost_code = source.request.cost_code.value
        request.genome_size = source.request.genome_size.value
        request.library_type = source.request.library_type.value
        request.study_uuid = source.request.study_uuid.value

        request.sample_name = source.sample.name.value
        request.sample_uuid = source.sample.uuid.value
        request.species = source.sample.species_name.value

        destination.source = source.source
