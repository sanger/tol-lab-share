from tol_lab_share import error_codes
from tol_lab_share.message_properties.definitions.input import Input
from tol_lab_share.message_properties.definitions.labware import Labware
from tol_lab_share.message_properties.definitions.labware_type import LabwareType
from tol_lab_share.message_properties.definitions.sample import Sample


def build_sample(sample_data):
    labware = Labware(Input(None))
    sample = Sample(sample_data)
    lt = LabwareType(Input("Plate12x8"))

    labware.add_property("labware_type", lt)
    labware.add_property("barcode", Input("1234"))
    labware.add_property("samples", [sample])

    return sample


def check_presence_error(error_list, error_code, field):
    assert any([((x.type_id == error_code.type_id) and (x.field == field)) for x in error_list])
    # return error_list.any(lambda x: x.type_id==error_code.type_id and x.field == field)


def test_sample_is_valid(valid_sample):
    instance = build_sample(valid_sample)
    assert instance.validate() is True
    assert len(instance.errors) == 0


def test_sample_is_invalid(invalid_sample):
    lt = LabwareType(Input("Plate12x8"))
    labware = Labware(Input("Bubidibu"))
    labware._properties["labware_type"] = lt

    instance = build_sample({"publicName": 1234})
    assert instance.validate() is False
    assert len(instance.errors) > 0

    instance = build_sample(invalid_sample)
    assert instance.validate() is False

    check_presence_error(instance.errors, error_codes.ERROR_1_UUID_NOT_BINARY, "study_uuid")
    check_presence_error(instance.errors, error_codes.ERROR_2_NOT_STRING, "study_uuid")
    check_presence_error(instance.errors, error_codes.ERROR_2_NOT_STRING, "common_name")
    check_presence_error(instance.errors, error_codes.ERROR_20_INPUT_IS_NOT_VALID_FLOAT_STRING, "concentration")
    check_presence_error(instance.errors, error_codes.ERROR_20_INPUT_IS_NOT_VALID_FLOAT_STRING, "volume")
    check_presence_error(instance.errors, error_codes.ERROR_2_NOT_STRING, "country_of_origin")
    check_presence_error(instance.errors, error_codes.ERROR_4_NOT_VALID_COUNTRY_INSDC, "country_of_origin")
    check_presence_error(instance.errors, error_codes.ERROR_2_NOT_STRING, "donor_id")
    check_presence_error(instance.errors, error_codes.ERROR_2_NOT_STRING, "library_type")
    check_presence_error(instance.errors, error_codes.ERROR_7_INVALID_LOCATION, "location")
    check_presence_error(instance.errors, error_codes.ERROR_2_NOT_STRING, "sanger_sample_id")

    check_presence_error(instance.errors, error_codes.ERROR_2_NOT_STRING, "cost_code")
    check_presence_error(instance.errors, error_codes.ERROR_2_NOT_STRING, "final_nano_drop_280")
    check_presence_error(instance.errors, error_codes.ERROR_2_NOT_STRING, "final_nano_drop_230")
    assert len(instance.errors) == 15
