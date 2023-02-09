from tol_lab_share.message_properties.definitions.labware_type import LabwareType
from tol_lab_share.message_properties.definitions.input import Input


def test_LabwareType_check_LabwareType_is_string():
    instance = LabwareType(Input(None))
    assert instance.validate() is False
    assert len(instance.errors) > 0

    instance = LabwareType(Input(1234))
    assert instance.validate() is False
    assert len(instance.errors) > 0

    instance = LabwareType(Input([]))
    assert instance.validate() is False
    assert len(instance.errors) > 0

    instance = LabwareType(Input("1234"))
    assert instance.validate() is False
    assert len(instance.errors) > 0

    instance = LabwareType(Input("plate"))
    assert instance.validate() is False
    assert len(instance.errors) > 0

    instance = LabwareType(Input("Plate12x8"))
    assert instance.validate() is True
    assert len(instance.errors) == 0

    instance = LabwareType(Input("Tube"))
    assert instance.validate() is True
    assert len(instance.errors) == 0


def test_valid_locations():
    instance = LabwareType(Input("Tube"))
    assert instance.valid_locations() == []

    instance = LabwareType(Input("Plate12x8"))
    assert len(instance.valid_locations()) == 96
    assert instance.valid_locations()[95] == "H12"
    assert instance.valid_locations()[1] == "B01"


def test_value():
    instance = LabwareType(Input("Tube"))
    assert instance.value == 'Tube'
    assert instance.validate()
    instance = LabwareType(Input(None))
    assert instance.value is None  
    assert not instance.validate()
