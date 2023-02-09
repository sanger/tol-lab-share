from .message_property import MessageProperty
from tol_lab_share.message_properties.definitions.public_name import PublicName
from tol_lab_share.message_properties.definitions.common_name import CommonName
from tol_lab_share.message_properties.definitions.concentration import Concentration
from tol_lab_share.message_properties.definitions.volume import Volume
from tol_lab_share.message_properties.definitions.country_of_origin import CountryOfOrigin
from tol_lab_share.message_properties.definitions.donor_id import DonorId
from tol_lab_share.message_properties.definitions.library_type import LibraryType
from tol_lab_share.message_properties.definitions.location import Location
from tol_lab_share.message_properties.definitions.sanger_sample_id import SangerSampleId
from tol_lab_share.message_properties.definitions.taxon_id import TaxonId
from tol_lab_share.message_properties.definitions.scientific_name_from_taxon_id import ScientificNameFromTaxonId
from tol_lab_share.message_properties.definitions.uuid import Uuid
from tol_lab_share.message_properties.definitions.dict_input import DictInput
from tol_lab_share.message_properties.definitions.date_utc import DateUtc
from tol_lab_share.message_properties.definitions.genome_size import GenomeSize
from tol_lab_share.message_properties.definitions.accession_number import AccessionNumber

from functools import cached_property

from tol_lab_share.constants import (
    INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_PUBLIC_NAME,
    INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_COMMON_NAME,
    INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_CONCENTRATION,
    INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_COUNTRY_OF_ORIGIN,
    INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_DONOR_ID,
    INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_LIBRARY_TYPE,
    INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_LOCATION,
    INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_SANGER_SAMPLE_ID,
    INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_SANGER_TAXON_ID,
    INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_SANGER_UUID,
    INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_STUDY_UUID,
    INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_COLLECTION_DATE,
    INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_VOLUME,
    INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_ACCESSION_NUMBER,
    INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_GENOME_SIZE,
)
from typing import Any

from tol_lab_share import schema_versioning

import logging

logger = logging.getLogger(__name__)


class Sample(MessageProperty):
    """MessageProperty that handles the parsing of a labware section for the TOL message."""

    @cached_property
    def property_definitions(self):
        return {
            "study_uuid": {
                "property": Uuid(DictInput(self._input, INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_STUDY_UUID)),
            },
            "common_name": {
                "property": CommonName(DictInput(self._input, INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_COMMON_NAME)),
            },
            "concentration": {
                "property": Concentration(DictInput(self._input, INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_CONCENTRATION)),
            },
            "volume": {
                "property": Volume(DictInput(self._input, INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_VOLUME)),
            },
            "country_of_origin": {
                "property": CountryOfOrigin(DictInput(self._input, INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_COUNTRY_OF_ORIGIN)),
            },
            "donor_id": {
                "property": DonorId(DictInput(self._input, INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_DONOR_ID)),
            },
            "library_type": {
                "property": LibraryType(DictInput(self._input, INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_LIBRARY_TYPE)),
            },
            "location": {
                "property": Location(DictInput(self._input, INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_LOCATION)),
            },
            "public_name": {
                "property": PublicName(DictInput(self._input, INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_PUBLIC_NAME))
            },
            "sanger_sample_id": {
                "property": SangerSampleId(DictInput(self._input, INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_SANGER_SAMPLE_ID))
            },
            "scientific_name": {
                "property": ScientificNameFromTaxonId(TaxonId(DictInput(self._input, INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_SANGER_TAXON_ID)))
            },
            "uuid": {
                "property": Uuid(DictInput(self._input, INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_SANGER_UUID)),
            },
            "accession_number": {
                "property": AccessionNumber(DictInput(self._input, INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_ACCESSION_NUMBER)),
                "versioning": schema_versioning.CREATE_LABWARE_SUPPORTING_ACCESSIONING_AND_GENOME,
            },
            "genome_size": {
                "property": GenomeSize(DictInput(self._input, INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_GENOME_SIZE)),
                "versioning": schema_versioning.CREATE_LABWARE_SUPPORTING_ACCESSIONING_AND_GENOME,
            },
            "collection_date": {
                "property": DateUtc(DictInput(self._input, INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_COLLECTION_DATE)),                
            },
        }

