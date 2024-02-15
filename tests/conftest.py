import logging
import logging.config
from datetime import datetime
from unittest.mock import MagicMock

import pytest
from data.examples_create_labware_messages import TEST_CREATE_LABWARE_MSG_OBJECT, TEST_INVALID_CREATE_LABWARE_MSG_OBJECT
from lab_share_lib.constants import RABBITMQ_HEADER_KEY_SUBJECT, RABBITMQ_HEADER_KEY_VERSION
from lab_share_lib.processing.rabbit_message import RabbitMessage

from tol_lab_share.helpers import get_config
from tol_lab_share.messages.output_feedback_message import OutputFeedbackMessage

CONFIG = get_config("tol_lab_share.config.test")
logging.config.dictConfig(CONFIG.LOGGING)


@pytest.fixture
def config():
    return CONFIG


HEADERS = {
    RABBITMQ_HEADER_KEY_SUBJECT: "a-subject",
    RABBITMQ_HEADER_KEY_VERSION: "3",
}

ENCODED_BODY = "Encoded body"
VALID_DECODED_LIST = [TEST_CREATE_LABWARE_MSG_OBJECT]
INVALID_DECODED_LIST = [TEST_INVALID_CREATE_LABWARE_MSG_OBJECT]


@pytest.fixture
def unchecked_create_labware_message():
    return RabbitMessage(HEADERS, ENCODED_BODY)


@pytest.fixture
def valid_decoder():
    decoder = MagicMock()
    decoder.decode.return_value = VALID_DECODED_LIST

    return decoder


@pytest.fixture
def invalid_decoder():
    decoder = MagicMock()
    decoder.decode.return_value = INVALID_DECODED_LIST

    return decoder


@pytest.fixture
def valid_create_labware_message(unchecked_create_labware_message, valid_decoder):
    unchecked_create_labware_message.decode(valid_decoder)

    return unchecked_create_labware_message


@pytest.fixture
def invalid_create_labware_message(unchecked_create_labware_message, invalid_decoder):
    unchecked_create_labware_message.decode(invalid_decoder)

    return unchecked_create_labware_message


@pytest.fixture
def traction_success_creation_response():
    return {
        "data": {
            "id": "52",
            "type": "receptions",
            "links": {"self": "http://localhost:3000/v1/receptions/52"},
            "attributes": {"source": "traction-ui.sequencescape"},
        }
    }


@pytest.fixture()
def traction_qc_success_response():
    return {
        "data": {
            "id": "10",
            "type": "qc_receptions",
            "links": {"self": "http://localhost:3000/v1/qc_receptions/10"},
            "attributes": {"source": "tol-lab-share.tol"},
        }
    }


@pytest.fixture()
def valid_feedback_message():
    instance = OutputFeedbackMessage()
    instance.count_of_total_samples = 0
    instance.count_of_valid_samples = 0
    instance.source_message_uuid = b"b01aa0ad-7b19-4f94-87e9-70d74fb8783c"
    instance.operation_was_error_free = True
    return instance


@pytest.fixture
def taxonomy_record():
    return {
        "taxId": "9600",
        "scientificName": "Pongo pygmaeus",
        "commonName": "Bornean orangutan",
        "formalName": "true",
        "rank": "species",
        "division": "MAM",
        "lineage": (
            "Eukaryota; Metazoa; Chordata; Craniata; Vertebrata; Euteleostomi; "
            "Mammalia; Eutheria; Euarchontoglires; Primates; Haplorrhini; "
            "Catarrhini; Hominidae; Pongo; "
        ),
        "geneticCode": "1",
        "mitochondrialGeneticCode": "2",
        "submittable": "true",
        "binomial": "true",
    }


@pytest.fixture
def valid_sample():
    return {
        "sampleUuid": "dd490ee5-fd1d-456d-99fd-eb9d3861e0f6".encode(),
        "studyUuid": "dd490ee5-fd1d-456d-99fd-eb9d3861e014".encode(),
        "sangerSampleId": "cichlid_pacbio8196429",
        "location": "A01",
        "supplierSampleName": "SampleSupplied1",
        "volume": "5",
        "concentration": "5",
        "publicName": "SamplePublicName1",
        "taxonId": "10090",
        "commonName": "Mus Musculus",
        "donorId": "cichlid_pacbio8196429",
        "libraryType": "Library1",
        "countryOfOrigin": "United Kingdom",
        "genomeSize": "14",
        "accessionNumber": "EE1234",
        "sampleCollectionDateUtc": datetime.utcnow(),
        "costCode": "S1234",
        "shearedFemtoFragmentSize": "8",
        "postSPRIConcentration": "9",
        "postSPRIVolume": "10",
        "finalNanoDrop280": "200",
        "finalNanoDrop230": "200",
        "finalNanoDrop": "150",
        "shearingAndQCComments": "",
        "dateSubmittedUTC": datetime.utcnow(),
        "priorityLevel": "Medium",
    }


@pytest.fixture
def invalid_sample():
    return {
        "sampleUuid": b"dd490ee5-fd1d-456d-99fd-eb9d3861e0f6",
        "studyUuid": "dd490ee5-fd1d-456d-99fd-eb9d3861e014",
        "sangerSampleId": 1234,
        "location": "A001",
        "supplierSampleName": "1234",
        "volume": "ee5",
        "concentration": "ee5",
        "publicName": "1234",
        "taxonId": "ee10090",
        "commonName": 1234,
        "donorId": 1234,
        "libraryType": 1234,
        "countryOfOrigin": 1234,
        "genomeSize": "14",
        "accessionNumber": "EE1234",
        "costCode": 1234,
        "sampleCollectionDateUtc": datetime.utcnow(),
        "shearedFemtoFragmentSize": "8",
        "postSPRIConcentration": "9",
        "postSPRIVolume": "10",
        "finalNanoDrop280": 200,
        "finalNanoDrop230": 200,
        "finalNanoDrop": "150",
        "shearingAndQCComments": "",
        "dateSubmittedUTC": datetime.utcnow(),
        "priorityLevel": "Medium",
    }


def read_file(filename):
    with open(filename, "r") as file:
        return file.read()


@pytest.fixture
def feedback_schema_json():
    return read_file("./schemas/create-labware-feedback/1-create-labware-feedback.avsc")
