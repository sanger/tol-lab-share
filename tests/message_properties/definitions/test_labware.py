from tol_lab_share.message_properties.definitions.labware import Labware
from tol_lab_share.message_properties.definitions.location import Location
from tol_lab_share.message_properties.definitions.input import Input
from tol_lab_share.messages.output_traction_message import OutputTractionMessage


def test_labware_is_valid():
    labware = {
        "labwareType": "Plate12x8",
        "labwareUuid": "dd490ee5-fd1d-456d-99fd-eb9d3861e0f9".encode(),
        "barcode": "BARCODE001",
        "samples": [],
    }

    instance = Labware(Input(labware))
    assert instance.validate() is True
    assert instance.errors == []


def test_sample_is_invalid():
    labware = {
        "labwareType": "Plate12x9",
        "labwareUuid": "dd490ee5-fd1d-456d-99fd-eb9d3861e0f9",
        "barcode": 1234,
        "samples": [],
    }

    instance = Labware(Input(labware))
    assert instance.validate() is False
    assert len(instance.errors) > 0

    labware = {
        "labwareType": "Plate12x8",
        "labwareUuid": "dd490ee5-fd1d-456d-99fd-eb9d3861e0f9".encode(),
        "samples": [],
    }
    instance = Labware(Input(labware))
    assert instance.validate() is False
    assert len(instance.errors) > 0


def test_count_of_total_samples(valid_sample):
    labware = {
        "labwareType": "Plate12x8",
        "labwareUuid": "dd490ee5-fd1d-456d-99fd-eb9d3861e0f9".encode(),
        "barcode": "1234",
        "samples": [],
    }

    instance = Labware(Input(labware))
    assert instance.validate()
    assert instance.count_of_total_samples() == 0

    labware2 = {
        "labwareType": "Plate12x8",
        "labwareUuid": "dd490ee5-fd1d-456d-99fd-eb9d3861e0f9".encode(),
        "barcode": "1234",
        "samples": [valid_sample, valid_sample],
    }

    instance = Labware(Input(labware2))
    assert instance.validate()
    assert instance.count_of_total_samples() == 2
    assert instance.errors == []


def test_count_of_valid_samples(valid_sample, invalid_sample):
    labware = {
        "labwareType": "Plate12x8",
        "labwareUuid": b"dd490ee5-fd1d-456d-99fd-eb9d3861e0f9",
        "barcode": "1234",
        "samples": [],
    }

    instance = Labware(Input(labware))
    instance.validate()
    assert instance.count_of_valid_samples() == 0

    labware2 = {
        "labwareType": "Plate12x8",
        "labwareUuid": b"dd490ee5-fd1d-456d-99fd-eb9d3861e0f9",
        "barcode": "1234",
        "samples": [valid_sample, valid_sample],
    }

    instance = Labware(Input(labware2))
    instance.validate()
    assert instance.errors == []
    assert instance.count_of_valid_samples() == 2

    labware2 = {
        "labwareType": "Plate12x8",
        "labwareUuid": b"dd490ee5-fd1d-456d-99fd-eb9d3861e0f9",
        "barcode": "1234",
        "samples": [invalid_sample, valid_sample],
    }

    instance = Labware(Input(labware2))
    instance.validate()
    assert instance.count_of_valid_samples() == 1


def test_labware_add_to_traction_message_wells(valid_sample):
    data = {
        "labwareType": "Plate12x8",
        "labwareUuid": "dd490ee5-fd1d-456d-99fd-eb9d3861e0f9".encode(),
        "barcode": "BARCODE001",
        "samples": [valid_sample],
    }
    instance = Labware(Input(data))
    assert instance.validate()

    traction_message = OutputTractionMessage()
    instance.add_to_traction_message(traction_message)

    assert traction_message.requests(0).study_uuid == "dd490ee5-fd1d-456d-99fd-eb9d3861e014"
    assert traction_message.requests(0).sample_name == "SamplePublicName1"
    assert traction_message.requests(0).sample_uuid == "dd490ee5-fd1d-456d-99fd-eb9d3861e0f6"
    assert traction_message.requests(0).library_type == "Library1"
    assert traction_message.requests(0).species == "Mus musculus"
    assert traction_message.requests(0).container_barcode == "BARCODE001"
    assert traction_message.requests(0).container_location == "A1"
    assert traction_message.requests(0).container_type == "wells"


def test_labware_add_to_traction_message_tubes(valid_sample):
    data = {
        "labwareType": "Tube",
        "labwareUuid": "dd490ee5-fd1d-456d-99fd-eb9d3861e0f9".encode(),
        "barcode": "BARCODE001",
        "samples": [valid_sample],
    }
    instance = Labware(Input(data))

    traction_message = OutputTractionMessage()
    instance.add_to_traction_message(traction_message)

    assert traction_message.requests(0).study_uuid == "dd490ee5-fd1d-456d-99fd-eb9d3861e014"
    assert traction_message.requests(0).sample_name == "SamplePublicName1"
    assert traction_message.requests(0).sample_uuid == "dd490ee5-fd1d-456d-99fd-eb9d3861e0f6"
    assert traction_message.requests(0).library_type == "Library1"
    assert traction_message.requests(0).species == "Mus musculus"
    assert traction_message.requests(0).container_barcode == "BARCODE001"
    assert traction_message.requests(0).container_location == "A1"
    assert traction_message.requests(0).container_type == "tubes"


def test_labware_add_to_traction_message_uses_unpadded_location(valid_sample):
    data = {
        "labwareType": "Plate12x8",
        "labwareUuid": "dd490ee5-fd1d-456d-99fd-eb9d3861e0f9".encode(),
        "barcode": "BARCODE001",
        "samples": [valid_sample],
    }
    instance = Labware(Input(data))
    instance.properties("samples")[0].add_property("location", Location(Input("B01")))
    traction_message = OutputTractionMessage()
    instance.add_to_traction_message(traction_message)
    assert traction_message.requests(0).container_location == "B1"
