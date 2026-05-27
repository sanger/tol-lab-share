from unittest.mock import patch
import pytest
import requests
from tol_lab_share.messages.traction.reception_message import TractionReceptionMessage
from lab_share_lib.exceptions import TransientRabbitError
from datetime import UTC, datetime
import requests_mock


@pytest.fixture(autouse=True)
def mock_logger():
    with patch("tol_lab_share.messages.traction.reception_message.logger") as logger:
        yield logger


def valid_traction_message():
    instance = TractionReceptionMessage()
    request = instance.create_request()
    request.container_barcode = "1"
    request.container_type = "wells"
    request.library_type = "library"
    request.sample_name = "test1"
    request.study_uuid = "dd490ee5-fd1d-456d-99fd-eb9d3861e014"
    request.sample_uuid = "8860a6b4-82e2-451c-aba2-a3129c38c0fc"
    request.species = "test species"
    request.cost_code = "S1234"

    return instance


class TestTractionReceptionMessage:
    def test_can_validate(self):
        instance = TractionReceptionMessage()
        assert not instance.validate()

        instance = TractionReceptionMessage()
        request = instance.create_request()
        request.container_barcode = "1"
        request.container_type = "wells"
        request.library_type = "library"
        assert not instance.validate()

        assert valid_traction_message().validate()

    def test_can_generate_payload_for_plates(self):
        my_date = datetime.now(UTC)
        instance = TractionReceptionMessage()

        request = instance.create_request()
        request.accession_number = "AN1234"
        request.container_barcode = "1"
        request.container_location = "A1"
        request.container_type = "wells"
        request.cost_code = "S1234"
        request.country_of_origin = "United Kingdom"
        request.date_of_sample_collection = my_date
        request.donor_id = "donor1"
        request.genome_size = "123,456,789"
        request.library_type = "library"
        request.priority_level = None
        request.public_name = "Public1"
        request.sample_name = "test1"
        request.sample_uuid = "8860a6b4-82e2-451c-aba2-a3129c38c0fc"
        request.sanger_sample_id = "sample1"
        request.species = "test species"
        request.study_uuid = "dd490ee5-fd1d-456d-99fd-eb9d3861e014"
        request.supplier_name = "supplier1"
        request.taxon_id = "9606"
        request.retention_instruction = "return_to_customer_after_2_years"

        request = instance.create_request()
        request.accession_number = "AN1235"
        request.container_barcode = "1"
        request.container_location = "B1"
        request.container_type = "wells"
        request.cost_code = "S4567"
        request.country_of_origin = "United Kingdom"
        request.date_of_sample_collection = my_date
        request.donor_id = "donor2"
        request.genome_size = None
        request.library_type = "library"
        request.priority_level = None
        request.public_name = "Public2"
        request.sample_name = "test1"
        request.sample_uuid = "8860a6b4-82e2-451c-aba2-a3129c38c0fc"
        request.sanger_sample_id = "sample2"
        request.species = "test species"
        request.study_uuid = "dd490ee5-fd1d-456d-99fd-eb9d3861e014"
        request.supplier_name = "supplier2"
        request.taxon_id = "9606"
        request.retention_instruction = "return_to_customer_after_2_years"

        assert instance.payload() == {
            "data": {
                "type": "receptions",
                "attributes": {
                    "source": "tol-lab-share.tol",
                    "plates_attributes": [
                        {
                            "barcode": "1",
                            "type": "plates",
                            "wells_attributes": [
                                {
                                    "position": "A1",
                                    "request": {
                                        "cost_code": "S1234",
                                        "estimate_of_gb_required": "123,456,789",
                                        "external_study_id": "dd490ee5-fd1d-456d-99fd-eb9d3861e014",
                                        "library_type": "library",
                                    },
                                    "sample": {
                                        "accession_number": "AN1234",
                                        "country_of_origin": "United Kingdom",
                                        "date_of_sample_collection": my_date.strftime("%Y-%m-%d"),
                                        "donor_id": "donor1",
                                        "external_id": "8860a6b4-82e2-451c-aba2-a3129c38c0fc",
                                        "name": "test1",
                                        "priority_level": None,
                                        "public_name": "Public1",
                                        "sanger_sample_id": "sample1",
                                        "species": "test species",
                                        "supplier_name": "supplier1",
                                        "taxon_id": "9606",
                                        "retention_instruction": "return_to_customer_after_2_years",
                                    },
                                },
                                {
                                    "position": "B1",
                                    "request": {
                                        "cost_code": "S4567",
                                        "estimate_of_gb_required": None,
                                        "external_study_id": "dd490ee5-fd1d-456d-99fd-eb9d3861e014",
                                        "library_type": "library",
                                    },
                                    "sample": {
                                        "accession_number": "AN1235",
                                        "country_of_origin": "United Kingdom",
                                        "date_of_sample_collection": my_date.strftime("%Y-%m-%d"),
                                        "donor_id": "donor2",
                                        "external_id": "8860a6b4-82e2-451c-aba2-a3129c38c0fc",
                                        "name": "test1",
                                        "priority_level": None,
                                        "public_name": "Public2",
                                        "sanger_sample_id": "sample2",
                                        "species": "test species",
                                        "supplier_name": "supplier2",
                                        "taxon_id": "9606",
                                        "retention_instruction": "return_to_customer_after_2_years",
                                    },
                                },
                            ],
                        },
                    ],
                    "tubes_attributes": [],
                },
            }
        }

    def test_can_generate_payload_for_multiple_plates(self):
        my_date = datetime.now(UTC)
        instance = TractionReceptionMessage()

        # Mix the order of the requests to ensure the grouping for plates works.
        # Well order is still maintained since the payload keeps the order of the requests.

        # First plate, first well (A1).
        request = instance.create_request()
        request.accession_number = "AN1234"
        request.container_barcode = "123"
        request.container_location = "A1"
        request.container_type = "wells"
        request.cost_code = "S1234"
        request.country_of_origin = "United Kingdom"
        request.date_of_sample_collection = my_date
        request.donor_id = "donor1"
        request.genome_size = "123,456,789"
        request.library_type = "library"
        request.priority_level = None
        request.public_name = "Public1"
        request.sample_name = "test1"
        request.sample_uuid = "8860a6b4-1234-451c-aba2-a3129c38c0fc"
        request.sanger_sample_id = "sample1"
        request.species = "test species"
        request.study_uuid = "dd490ee5-fd1d-456d-99fd-eb9d3861e014"
        request.supplier_name = "supplier1"
        request.taxon_id = "9606"
        request.retention_instruction = "return_to_customer_after_2_years"

        # Second plate, first well (B1).
        request = instance.create_request()
        request.accession_number = "AN1236"
        request.container_barcode = "456"
        request.container_location = "B1"
        request.container_type = "wells"
        request.cost_code = "S1234"
        request.country_of_origin = "United Kingdom"
        request.date_of_sample_collection = my_date
        request.donor_id = "donor3"
        request.genome_size = None
        request.library_type = "library"
        request.priority_level = None
        request.public_name = "Public3"
        request.sample_name = "test3"
        request.sample_uuid = "8860a6b4-1236-451c-aba2-a3129c38c0fc"
        request.sanger_sample_id = "sample3"
        request.species = "test species"
        request.study_uuid = "dd490ee5-fd1d-456d-99fd-eb9d3861e014"
        request.supplier_name = "supplier1"
        request.taxon_id = "9606"
        request.retention_instruction = "return_to_customer_after_2_years"

        # First plate, second well (B1).
        request = instance.create_request()
        request.accession_number = "AN1235"
        request.container_barcode = "123"
        request.container_location = "B1"
        request.container_type = "wells"
        request.cost_code = "S4567"
        request.country_of_origin = "United Kingdom"
        request.date_of_sample_collection = my_date
        request.donor_id = "donor2"
        request.genome_size = None
        request.library_type = "library"
        request.priority_level = None
        request.public_name = "Public2"
        request.sample_name = "test2"
        request.sample_uuid = "8860a6b4-1235-451c-aba2-a3129c38c0fc"
        request.sanger_sample_id = "sample2"
        request.species = "test species"
        request.study_uuid = "dd490ee5-fd1d-456d-99fd-eb9d3861e014"
        request.supplier_name = "supplier2"
        request.taxon_id = "9606"
        request.retention_instruction = "return_to_customer_after_2_years"

        # Second plate, second well (C1).
        request = instance.create_request()
        request.accession_number = "AN1237"
        request.container_barcode = "456"
        request.container_location = "C1"
        request.container_type = "wells"
        request.cost_code = "S4567"
        request.country_of_origin = "United Kingdom"
        request.date_of_sample_collection = my_date
        request.donor_id = "donor4"
        request.genome_size = "987,654,321"
        request.library_type = "library"
        request.priority_level = None
        request.public_name = "Public4"
        request.sample_name = "test4"
        request.sample_uuid = "8860a6b4-1237-451c-aba2-a3129c38c0fc"
        request.sanger_sample_id = "sample4"
        request.species = "test species"
        request.study_uuid = "dd490ee5-fd1d-456d-99fd-eb9d3861e014"
        request.supplier_name = "supplier2"
        request.taxon_id = "9606"
        request.retention_instruction = "return_to_customer_after_2_years"

        assert instance.payload() == {
            "data": {
                "type": "receptions",
                "attributes": {
                    "source": "tol-lab-share.tol",
                    "plates_attributes": [
                        {
                            "barcode": "123",
                            "type": "plates",
                            "wells_attributes": [
                                {
                                    "position": "A1",
                                    "request": {
                                        "cost_code": "S1234",
                                        "estimate_of_gb_required": "123,456,789",
                                        "external_study_id": "dd490ee5-fd1d-456d-99fd-eb9d3861e014",
                                        "library_type": "library",
                                    },
                                    "sample": {
                                        "accession_number": "AN1234",
                                        "country_of_origin": "United Kingdom",
                                        "date_of_sample_collection": my_date.strftime("%Y-%m-%d"),
                                        "donor_id": "donor1",
                                        "external_id": "8860a6b4-1234-451c-aba2-a3129c38c0fc",
                                        "name": "test1",
                                        "priority_level": None,
                                        "public_name": "Public1",
                                        "sanger_sample_id": "sample1",
                                        "species": "test species",
                                        "supplier_name": "supplier1",
                                        "taxon_id": "9606",
                                        "retention_instruction": "return_to_customer_after_2_years",
                                    },
                                },
                                {
                                    "position": "B1",
                                    "request": {
                                        "cost_code": "S4567",
                                        "estimate_of_gb_required": None,
                                        "external_study_id": "dd490ee5-fd1d-456d-99fd-eb9d3861e014",
                                        "library_type": "library",
                                    },
                                    "sample": {
                                        "accession_number": "AN1235",
                                        "country_of_origin": "United Kingdom",
                                        "date_of_sample_collection": my_date.strftime("%Y-%m-%d"),
                                        "donor_id": "donor2",
                                        "external_id": "8860a6b4-1235-451c-aba2-a3129c38c0fc",
                                        "name": "test2",
                                        "priority_level": None,
                                        "public_name": "Public2",
                                        "sanger_sample_id": "sample2",
                                        "species": "test species",
                                        "supplier_name": "supplier2",
                                        "taxon_id": "9606",
                                        "retention_instruction": "return_to_customer_after_2_years",
                                    },
                                },
                            ],
                        },
                        {
                            "barcode": "456",
                            "type": "plates",
                            "wells_attributes": [
                                {
                                    "position": "B1",
                                    "request": {
                                        "cost_code": "S1234",
                                        "estimate_of_gb_required": None,
                                        "external_study_id": "dd490ee5-fd1d-456d-99fd-eb9d3861e014",
                                        "library_type": "library",
                                    },
                                    "sample": {
                                        "accession_number": "AN1236",
                                        "country_of_origin": "United Kingdom",
                                        "date_of_sample_collection": my_date.strftime("%Y-%m-%d"),
                                        "donor_id": "donor3",
                                        "external_id": "8860a6b4-1236-451c-aba2-a3129c38c0fc",
                                        "name": "test3",
                                        "priority_level": None,
                                        "public_name": "Public3",
                                        "sanger_sample_id": "sample3",
                                        "species": "test species",
                                        "supplier_name": "supplier1",
                                        "taxon_id": "9606",
                                        "retention_instruction": "return_to_customer_after_2_years",
                                    },
                                },
                                {
                                    "position": "C1",
                                    "request": {
                                        "cost_code": "S4567",
                                        "estimate_of_gb_required": "987,654,321",
                                        "external_study_id": "dd490ee5-fd1d-456d-99fd-eb9d3861e014",
                                        "library_type": "library",
                                    },
                                    "sample": {
                                        "accession_number": "AN1237",
                                        "country_of_origin": "United Kingdom",
                                        "date_of_sample_collection": my_date.strftime("%Y-%m-%d"),
                                        "donor_id": "donor4",
                                        "external_id": "8860a6b4-1237-451c-aba2-a3129c38c0fc",
                                        "name": "test4",
                                        "priority_level": None,
                                        "public_name": "Public4",
                                        "sanger_sample_id": "sample4",
                                        "species": "test species",
                                        "supplier_name": "supplier2",
                                        "taxon_id": "9606",
                                        "retention_instruction": "return_to_customer_after_2_years",
                                    },
                                },
                            ],
                        },
                    ],
                    "tubes_attributes": [],
                },
            }
        }

    def test_can_generate_payload_for_ont_library_types(self):
        my_date = datetime.now(UTC)
        instance = TractionReceptionMessage()

        request = instance.create_request()
        request.accession_number = "AN1234"
        request.container_barcode = "1"
        request.container_location = "A1"
        request.container_type = "wells"
        request.cost_code = "S1234"
        request.country_of_origin = "United Kingdom"
        request.date_of_sample_collection = my_date
        request.donor_id = "donor1"
        request.genome_size = None
        request.library_type = "ONT_mylib"
        request.priority_level = "Medium"
        request.public_name = "Public1"
        request.sample_name = "test1"
        request.sample_uuid = "8860a6b4-82e2-451c-aba2-a3129c38c0fc"
        request.sanger_sample_id = "sample1"
        request.species = "test species"
        request.study_uuid = "dd490ee5-fd1d-456d-99fd-eb9d3861e014"
        request.supplier_name = "supplier1"
        request.taxon_id = "9606"
        request.retention_instruction = "return_to_customer_after_2_years"

        request = instance.create_request()
        request.accession_number = "AN1235"
        request.container_barcode = "1"
        request.container_location = "B1"
        request.container_type = "wells"
        request.cost_code = "S4567"
        request.country_of_origin = "United Kingdom"
        request.date_of_sample_collection = my_date
        request.donor_id = "donor2"
        request.genome_size = None
        request.library_type = "ONT_mylib"
        request.priority_level = None
        request.public_name = "Public2"
        request.sample_name = "test1"
        request.sample_uuid = "8860a6b4-82e2-451c-aba2-a3129c38c0fc"
        request.sanger_sample_id = "sample2"
        request.species = "test species"
        request.study_uuid = "dd490ee5-fd1d-456d-99fd-eb9d3861e014"
        request.supplier_name = "supplier2"
        request.taxon_id = "9606"
        request.retention_instruction = "return_to_customer_after_2_years"

        assert instance.payload() == {
            "data": {
                "type": "receptions",
                "attributes": {
                    "source": "tol-lab-share.tol",
                    "plates_attributes": [
                        {
                            "barcode": "1",
                            "type": "plates",
                            "wells_attributes": [
                                {
                                    "position": "A1",
                                    "request": {
                                        "cost_code": "S1234",
                                        "data_type": "basecalls",
                                        "estimate_of_gb_required": None,
                                        "external_study_id": "dd490ee5-fd1d-456d-99fd-eb9d3861e014",
                                        "library_type": "ONT_mylib",
                                    },
                                    "sample": {
                                        "accession_number": "AN1234",
                                        "country_of_origin": "United Kingdom",
                                        "date_of_sample_collection": my_date.strftime("%Y-%m-%d"),
                                        "donor_id": "donor1",
                                        "external_id": "8860a6b4-82e2-451c-aba2-a3129c38c0fc",
                                        "name": "test1",
                                        "priority_level": "Medium",
                                        "public_name": "Public1",
                                        "sanger_sample_id": "sample1",
                                        "species": "test species",
                                        "supplier_name": "supplier1",
                                        "taxon_id": "9606",
                                        "retention_instruction": "return_to_customer_after_2_years",
                                    },
                                },
                                {
                                    "position": "B1",
                                    "request": {
                                        "cost_code": "S4567",
                                        "data_type": "basecalls",
                                        "estimate_of_gb_required": None,
                                        "external_study_id": "dd490ee5-fd1d-456d-99fd-eb9d3861e014",
                                        "library_type": "ONT_mylib",
                                    },
                                    "sample": {
                                        "accession_number": "AN1235",
                                        "country_of_origin": "United Kingdom",
                                        "date_of_sample_collection": my_date.strftime("%Y-%m-%d"),
                                        "donor_id": "donor2",
                                        "external_id": "8860a6b4-82e2-451c-aba2-a3129c38c0fc",
                                        "name": "test1",
                                        "priority_level": None,
                                        "public_name": "Public2",
                                        "sanger_sample_id": "sample2",
                                        "species": "test species",
                                        "supplier_name": "supplier2",
                                        "taxon_id": "9606",
                                        "retention_instruction": "return_to_customer_after_2_years",
                                    },
                                },
                            ],
                        },
                    ],
                    "tubes_attributes": [],
                },
            }
        }

    def test_can_generate_payload_for_tubes(self):
        my_date = datetime.now(UTC)
        instance = TractionReceptionMessage()

        request = instance.create_request()
        request.accession_number = "AN1234"
        request.container_barcode = "1"
        request.container_type = "tubes"
        request.cost_code = "S1234"
        request.country_of_origin = "United Kingdom"
        request.date_of_sample_collection = my_date
        request.donor_id = "donor1"
        request.genome_size = "123,456,789"
        request.library_type = "library"
        request.priority_level = "High"
        request.public_name = "Public1"
        request.sample_name = "test1"
        request.sample_uuid = "8860a6b4-82e2-451c-aba2-a3129c38c0fc"
        request.sanger_sample_id = "sample1"
        request.species = "test species"
        request.study_uuid = "dd490ee5-fd1d-456d-99fd-eb9d3861e014"
        request.supplier_name = "supplier1"
        request.taxon_id = "9606"
        request.retention_instruction = "return_to_customer_after_2_years"

        request = instance.create_request()
        request.accession_number = "AN1235"
        request.container_barcode = "1"
        request.container_type = "tubes"
        request.cost_code = "S4567"
        request.country_of_origin = "United Kingdom"
        request.date_of_sample_collection = my_date
        request.donor_id = "donor2"
        request.genome_size = "987,654,321"
        request.library_type = "library"
        request.priority_level = "Low"
        request.public_name = "Public2"
        request.sample_name = "test1"
        request.sample_uuid = "8860a6b4-82e2-451c-aba2-a3129c38c0fc"
        request.sanger_sample_id = "sample2"
        request.species = "test species"
        request.study_uuid = "dd490ee5-fd1d-456d-99fd-eb9d3861e014"
        request.supplier_name = "supplier2"
        request.taxon_id = "9606"
        request.retention_instruction = "return_to_customer_after_2_years"

        assert instance.payload() == {
            "data": {
                "type": "receptions",
                "attributes": {
                    "source": "tol-lab-share.tol",
                    "plates_attributes": [],
                    "tubes_attributes": [
                        {
                            "barcode": "1",
                            "type": "tubes",
                            "request": {
                                "cost_code": "S1234",
                                "estimate_of_gb_required": "123,456,789",
                                "external_study_id": "dd490ee5-fd1d-456d-99fd-eb9d3861e014",
                                "library_type": "library",
                            },
                            "sample": {
                                "accession_number": "AN1234",
                                "country_of_origin": "United Kingdom",
                                "date_of_sample_collection": my_date.strftime("%Y-%m-%d"),
                                "donor_id": "donor1",
                                "external_id": "8860a6b4-82e2-451c-aba2-a3129c38c0fc",
                                "name": "test1",
                                "priority_level": "High",
                                "public_name": "Public1",
                                "sanger_sample_id": "sample1",
                                "species": "test species",
                                "supplier_name": "supplier1",
                                "taxon_id": "9606",
                                "retention_instruction": "return_to_customer_after_2_years",
                            },
                        },
                        {
                            "barcode": "1",
                            "type": "tubes",
                            "request": {
                                "cost_code": "S4567",
                                "estimate_of_gb_required": "987,654,321",
                                "external_study_id": "dd490ee5-fd1d-456d-99fd-eb9d3861e014",
                                "library_type": "library",
                            },
                            "sample": {
                                "accession_number": "AN1235",
                                "country_of_origin": "United Kingdom",
                                "date_of_sample_collection": my_date.strftime("%Y-%m-%d"),
                                "donor_id": "donor2",
                                "external_id": "8860a6b4-82e2-451c-aba2-a3129c38c0fc",
                                "name": "test1",
                                "priority_level": "Low",
                                "public_name": "Public2",
                                "sanger_sample_id": "sample2",
                                "species": "test species",
                                "supplier_name": "supplier2",
                                "taxon_id": "9606",
                                "retention_instruction": "return_to_customer_after_2_years",
                            },
                        },
                    ],
                },
            }
        }

    def test_can_generate_payload_for_mix_of_plate_and_tubes(self):
        my_date = datetime.now(UTC)
        instance = TractionReceptionMessage()

        request = instance.create_request()
        request.accession_number = "AN1234"
        request.container_barcode = "123"
        request.container_location = "A1"
        request.container_type = "wells"
        request.cost_code = "S1234"
        request.country_of_origin = "United Kingdom"
        request.date_of_sample_collection = my_date
        request.donor_id = "donor1"
        request.genome_size = "123,456,789"
        request.library_type = "library"
        request.priority_level = None
        request.public_name = "Public1"
        request.sample_name = "test1"
        request.sample_uuid = "8860a6b4-1234-451c-aba2-a3129c38c0fc"
        request.sanger_sample_id = "sample1"
        request.species = "test species"
        request.study_uuid = "dd490ee5-fd1d-456d-99fd-eb9d3861e014"
        request.supplier_name = "supplier1"
        request.taxon_id = "9606"
        request.retention_instruction = "return_to_customer_after_2_years"

        request = instance.create_request()
        request.accession_number = "AN1235"
        request.container_barcode = "123"
        request.container_location = "B1"
        request.container_type = "wells"
        request.cost_code = "S4567"
        request.country_of_origin = "United Kingdom"
        request.date_of_sample_collection = my_date
        request.donor_id = "donor2"
        request.genome_size = None
        request.library_type = "library"
        request.priority_level = None
        request.public_name = "Public2"
        request.sample_name = "test2"
        request.sample_uuid = "8860a6b4-1235-451c-aba2-a3129c38c0fc"
        request.sanger_sample_id = "sample2"
        request.species = "test species"
        request.study_uuid = "dd490ee5-fd1d-456d-99fd-eb9d3861e014"
        request.supplier_name = "supplier2"
        request.taxon_id = "9606"
        request.retention_instruction = "return_to_customer_after_2_years"

        request = instance.create_request()
        request.accession_number = "AN1236"
        request.container_barcode = "987"
        request.container_type = "tubes"
        request.cost_code = "S1234"
        request.country_of_origin = "United Kingdom"
        request.date_of_sample_collection = my_date
        request.donor_id = "donor3"
        request.genome_size = None
        request.library_type = "library"
        request.priority_level = "High"
        request.public_name = "Public3"
        request.sample_name = "test3"
        request.sample_uuid = "8860a6b4-1236-451c-aba2-a3129c38c0fc"
        request.sanger_sample_id = "sample3"
        request.species = "test species"
        request.study_uuid = "dd490ee5-fd1d-456d-99fd-eb9d3861e014"
        request.supplier_name = "supplier3"
        request.taxon_id = "9606"
        request.retention_instruction = "return_to_customer_after_2_years"

        request = instance.create_request()
        request.accession_number = "AN1237"
        request.container_barcode = "876"
        request.container_type = "tubes"
        request.cost_code = "S4567"
        request.country_of_origin = "United Kingdom"
        request.date_of_sample_collection = my_date
        request.donor_id = "donor4"
        request.genome_size = "987,654,321"
        request.library_type = "library"
        request.priority_level = "Low"
        request.public_name = "Public4"
        request.sample_name = "test4"
        request.sample_uuid = "8860a6b4-1237-451c-aba2-a3129c38c0fc"
        request.sanger_sample_id = "sample4"
        request.species = "test species"
        request.study_uuid = "dd490ee5-fd1d-456d-99fd-eb9d3861e014"
        request.supplier_name = "supplier4"
        request.taxon_id = "9606"
        request.retention_instruction = "return_to_customer_after_2_years"

        assert instance.payload() == {
            "data": {
                "type": "receptions",
                "attributes": {
                    "source": "tol-lab-share.tol",
                    "plates_attributes": [
                        {
                            "barcode": "123",
                            "type": "plates",
                            "wells_attributes": [
                                {
                                    "position": "A1",
                                    "request": {
                                        "cost_code": "S1234",
                                        "estimate_of_gb_required": "123,456,789",
                                        "external_study_id": "dd490ee5-fd1d-456d-99fd-eb9d3861e014",
                                        "library_type": "library",
                                    },
                                    "sample": {
                                        "accession_number": "AN1234",
                                        "country_of_origin": "United Kingdom",
                                        "date_of_sample_collection": my_date.strftime("%Y-%m-%d"),
                                        "donor_id": "donor1",
                                        "external_id": "8860a6b4-1234-451c-aba2-a3129c38c0fc",
                                        "name": "test1",
                                        "priority_level": None,
                                        "public_name": "Public1",
                                        "sanger_sample_id": "sample1",
                                        "species": "test species",
                                        "supplier_name": "supplier1",
                                        "taxon_id": "9606",
                                        "retention_instruction": "return_to_customer_after_2_years",
                                    },
                                },
                                {
                                    "position": "B1",
                                    "request": {
                                        "cost_code": "S4567",
                                        "estimate_of_gb_required": None,
                                        "external_study_id": "dd490ee5-fd1d-456d-99fd-eb9d3861e014",
                                        "library_type": "library",
                                    },
                                    "sample": {
                                        "accession_number": "AN1235",
                                        "country_of_origin": "United Kingdom",
                                        "date_of_sample_collection": my_date.strftime("%Y-%m-%d"),
                                        "donor_id": "donor2",
                                        "external_id": "8860a6b4-1235-451c-aba2-a3129c38c0fc",
                                        "name": "test2",
                                        "priority_level": None,
                                        "public_name": "Public2",
                                        "sanger_sample_id": "sample2",
                                        "species": "test species",
                                        "supplier_name": "supplier2",
                                        "taxon_id": "9606",
                                        "retention_instruction": "return_to_customer_after_2_years",
                                    },
                                },
                            ],
                        },
                    ],
                    "tubes_attributes": [
                        {
                            "barcode": "987",
                            "type": "tubes",
                            "request": {
                                "cost_code": "S1234",
                                "estimate_of_gb_required": None,
                                "external_study_id": "dd490ee5-fd1d-456d-99fd-eb9d3861e014",
                                "library_type": "library",
                            },
                            "sample": {
                                "accession_number": "AN1236",
                                "country_of_origin": "United Kingdom",
                                "date_of_sample_collection": my_date.strftime("%Y-%m-%d"),
                                "donor_id": "donor3",
                                "external_id": "8860a6b4-1236-451c-aba2-a3129c38c0fc",
                                "name": "test3",
                                "priority_level": "High",
                                "public_name": "Public3",
                                "sanger_sample_id": "sample3",
                                "species": "test species",
                                "supplier_name": "supplier3",
                                "taxon_id": "9606",
                                "retention_instruction": "return_to_customer_after_2_years",
                            },
                        },
                        {
                            "barcode": "876",
                            "type": "tubes",
                            "request": {
                                "cost_code": "S4567",
                                "estimate_of_gb_required": "987,654,321",
                                "external_study_id": "dd490ee5-fd1d-456d-99fd-eb9d3861e014",
                                "library_type": "library",
                            },
                            "sample": {
                                "accession_number": "AN1237",
                                "country_of_origin": "United Kingdom",
                                "date_of_sample_collection": my_date.strftime("%Y-%m-%d"),
                                "donor_id": "donor4",
                                "external_id": "8860a6b4-1237-451c-aba2-a3129c38c0fc",
                                "name": "test4",
                                "priority_level": "Low",
                                "public_name": "Public4",
                                "sanger_sample_id": "sample4",
                                "species": "test species",
                                "supplier_name": "supplier4",
                                "taxon_id": "9606",
                                "retention_instruction": "return_to_customer_after_2_years",
                            },
                        },
                    ],
                },
            }
        }

    def test_can_generate_payload_for_tube_with_library(self):
        instance = TractionReceptionMessage()

        request = instance.create_request()
        request.container_barcode = "1"
        request.container_type = "tubes"
        request.cost_code = "S1234"
        request.genome_size = "123,456,789"
        request.library_concentration = 55.95
        request.library_insert_size = 120381
        request.library_type = "library"
        request.library_volume = 69.69
        request.sample_name = "test1"
        request.sample_uuid = "8860a6b4-82e2-451c-aba2-a3129c38c0fc"
        request.species = "test species"
        request.study_uuid = "dd490ee5-fd1d-456d-99fd-eb9d3861e014"
        request.template_prep_kit_box_barcode = "box_barcode_001"
        request.retention_instruction = "return_to_customer_after_2_years"

        assert instance.payload() == {
            "data": {
                "type": "receptions",
                "attributes": {
                    "source": "tol-lab-share.tol",
                    "plates_attributes": [],
                    "tubes_attributes": [
                        {
                            "barcode": "1",
                            "type": "tubes",
                            "library": {
                                "concentration": 55.95,
                                "insert_size": 120381,
                                "template_prep_kit_box_barcode": "box_barcode_001",
                                "volume": 69.69,
                            },
                            "request": {
                                "cost_code": "S1234",
                                "estimate_of_gb_required": "123,456,789",
                                "external_study_id": "dd490ee5-fd1d-456d-99fd-eb9d3861e014",
                                "library_type": "library",
                            },
                            "sample": {
                                "accession_number": None,
                                "country_of_origin": None,
                                "date_of_sample_collection": None,
                                "donor_id": None,
                                "external_id": "8860a6b4-82e2-451c-aba2-a3129c38c0fc",
                                "name": "test1",
                                "priority_level": None,
                                "public_name": None,
                                "sanger_sample_id": None,
                                "species": "test species",
                                "supplier_name": None,
                                "taxon_id": None,
                                "retention_instruction": "return_to_customer_after_2_years",
                            },
                        },
                    ],
                },
            }
        }

    def test_raises_transient_error_when_traction_api_responds_502(self, config):
        # This happens when the Traction API is down but nginx is still up.
        vt = valid_traction_message()

        with requests_mock.Mocker() as m:
            m.post(config.TRACTION_URL, text="Error", status_code=502)
            with pytest.raises(TransientRabbitError):
                vt.send(config.TRACTION_URL)

    def test_raises_transient_error_when_post_raises(self, config, mock_logger):
        # This happens when nginx serving Traction API is down.
        vt = valid_traction_message()
        cause = requests.exceptions.RequestException()

        with requests_mock.Mocker() as m:
            m.post(config.TRACTION_URL, exc=cause)
            with pytest.raises(TransientRabbitError) as raised:
                vt.send(config.TRACTION_URL)

            assert "ReceptionMessage" in raised.value.message
            mock_logger.exception.assert_called_once_with(cause)

    def test_can_detect_other_errors_on_sent(self, config):
        vt = valid_traction_message()

        with requests_mock.Mocker() as m:
            m.post(config.TRACTION_URL, text="Error", status_code=422)
            vt.send(config.TRACTION_URL)

        assert not vt.validate()
        assert len(vt.errors) > 0

    def test_can_add_to_message_property_when_not_sent(self, valid_feedback_message):
        vt = valid_traction_message()

        assert vt.validate()

        feedback = valid_feedback_message
        vt.add_to_message_property(feedback)

        assert len(feedback.errors) == 0
        assert not feedback.operation_was_error_free

    def test_can_add_to_message_property_when_sent(
        self, config, traction_success_creation_response, valid_feedback_message
    ):
        vt = valid_traction_message()
        feedback = valid_feedback_message

        with requests_mock.Mocker() as m:
            m.post(config.TRACTION_URL, json=traction_success_creation_response, status_code=201)
            vt.send(config.TRACTION_URL)

        vt.add_to_message_property(feedback)

        assert len(feedback.errors) == 0
        assert feedback.operation_was_error_free

    def test_sends_api_key_header(self, config, traction_success_creation_response):
        vt = valid_traction_message()

        with requests_mock.Mocker() as m:
            m.post(config.TRACTION_URL, json=traction_success_creation_response, status_code=201)
            vt.send(config.TRACTION_URL)

            assert m.last_request.headers.get("X-Traction-Client-Id") == "traction-development"

    def test_can_add_to_message_property_when_errors(self, valid_feedback_message):
        instance = TractionReceptionMessage()

        request = instance.create_request()
        request.container_barcode = "1"
        request.container_type = "tubes"

        assert not instance.validate()

        feedback = valid_feedback_message
        instance.add_to_message_property(feedback)

        assert len(feedback.errors) > 0
        assert not feedback.operation_was_error_free
