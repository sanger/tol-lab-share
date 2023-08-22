from tol_lab_share.message_properties.definitions.country_of_origin import CountryOfOrigin
from tol_lab_share.message_properties.definitions.input import Input


def test_CountryOfOrigin_check_CountryOfOrigin_is_valid():
    instance = CountryOfOrigin(Input(None))
    assert instance.validate() is False
    assert len(instance.errors) > 0

    instance = CountryOfOrigin(Input("1234"))
    assert instance.validate() is False
    assert len(instance.errors) > 0

    instance = CountryOfOrigin(Input([]))
    assert instance.validate() is False
    assert len(instance.errors) > 0

    instance = CountryOfOrigin(Input(1234))
    assert instance.validate() is False
    assert len(instance.errors) > 0

    instance = CountryOfOrigin(Input("Testing"))
    assert instance.validate() is False
    assert len(instance.errors) > 0

    instance = CountryOfOrigin(Input("UNITED KINGDOM"))
    assert instance.validate() is True
    assert len(instance.errors) == 0
