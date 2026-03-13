from typing import Callable
from unittest.mock import patch

import pytest
from tests.data.example_bioscan_pool_xp_to_traction_messages import (
    VALID_BIOSCAN_POOL_XP_TO_TRACTION_PAYLOAD as VALID_PAYLOAD,
)
from tol_lab_share.constants.input_bioscan_pool_xp_to_traction_message import (
    MESSAGE_UUID,
    CREATED_DATE_UTC,
    TUBE_BARCODE,
    LIBRARY,
    REQUEST,
    SAMPLE,
)
from tol_lab_share.messages.consumed.bioscan_pool_xp_to_traction.root import Root
from tol_lab_share.constants import (
    OUTPUT_BIOSCAN_TRACTION_MESSAGE_SOURCE
)

@pytest.fixture
def subject():
    return Root(VALID_PAYLOAD.copy())


class TestRoot:
    def test_init_passes_arguments_to_record(self):
        with patch("tol_lab_share.messages.consumed.bioscan_pool_xp_to_traction.root.Record.__init__") as super_init:
            Root(VALID_PAYLOAD)

        super_init.assert_called_once_with(VALID_PAYLOAD)

    def test_message_uuid_returns_correct_message_field(self, subject, any):
        with patch("tol_lab_share.messages.consumed.bioscan_pool_xp_to_traction.root.Root._make_field") as make_field:
            field = subject.message_uuid

        make_field.assert_called_once_with(MESSAGE_UUID, any(Callable))
        assert field == make_field.return_value

    def test_message_uuid_value_correct(self, subject):
        assert subject.message_uuid.value == VALID_PAYLOAD[MESSAGE_UUID].decode()

    def test_create_date_utc_returns_correct_message_field(self, subject):
        with patch("tol_lab_share.messages.consumed.bioscan_pool_xp_to_traction.root.Root._make_field") as make_field:
            field = subject.create_date_utc

        make_field.assert_called_once_with(CREATED_DATE_UTC)
        assert field == make_field.return_value

    def test_create_date_utc_value_correct(self, subject):
        assert subject.create_date_utc.value == VALID_PAYLOAD[CREATED_DATE_UTC]

    def test_tube_barcode_returns_correct_message_field(self, subject):
        with patch("tol_lab_share.messages.consumed.bioscan_pool_xp_to_traction.root.Root._make_field") as make_field:
            field = subject.tube_barcode

        make_field.assert_called_once_with(TUBE_BARCODE)
        assert field == make_field.return_value

    def test_tube_barcode_value_correct(self, subject):
        assert subject.tube_barcode.value == VALID_PAYLOAD[TUBE_BARCODE]

    def test_library_returns_correct_message_field(self, subject):
        with patch("tol_lab_share.messages.consumed.bioscan_pool_xp_to_traction.root.Library") as library:
            field = subject.library

        library.assert_called_once_with(VALID_PAYLOAD[LIBRARY], LIBRARY, "")
        assert field == library.return_value

    def test_request_returns_correct_message_field(self, subject):
        with patch("tol_lab_share.messages.consumed.bioscan_pool_xp_to_traction.root.Request") as request:
            field = subject.request

        request.assert_called_once_with(VALID_PAYLOAD[REQUEST], REQUEST, "")
        assert field == request.return_value

    def test_sample_returns_correct_message_field(self, subject):
        with patch("tol_lab_share.messages.consumed.bioscan_pool_xp_to_traction.root.Sample") as sample:
            field = subject.sample

        sample.assert_called_once_with(VALID_PAYLOAD[SAMPLE], SAMPLE, "")
        assert field == sample.return_value

    def test_source_returns_bioscan_source(self, subject):
        assert subject.source == OUTPUT_BIOSCAN_TRACTION_MESSAGE_SOURCE