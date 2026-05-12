from datetime import UTC, datetime

from unittest.mock import patch
import pytest
import requests
import requests_mock

from tol_lab_share.messages.traction.qc_message import TractionQcMessage, QcRequestSerializer, TractionQcMessageRequest
from lab_share_lib.exceptions import TransientRabbitError


@pytest.fixture(autouse=True)
def mock_logger():
    with patch("tol_lab_share.messages.traction.qc_message.logger") as logger:
        yield logger


class TestTractionQcMessage:
    @pytest.fixture()
    def valid_traction_qc_message(self, freezer):
        traction_qc_message = TractionQcMessage()

        request = traction_qc_message.create_request()
        request.sanger_sample_id = "sanger_sample_id_DDD"
        request.container_barcode = "FD20706500"
        request.sheared_femto_fragment_size = "5"
        request.post_spri_concentration = "10"
        request.post_spri_volume = "20"
        request.final_nano_drop_280 = "280"
        request.final_nano_drop_230 = "230"
        request.final_nano_drop = "200"
        request.shearing_qc_comments = "Comments"
        request.date_submitted_utc = datetime.now(UTC).timestamp() * 1000

        request = traction_qc_message.create_request()
        request.sanger_sample_id = "sanger_sample_id_DDD2"
        request.container_barcode = "FD20706501"
        request.sheared_femto_fragment_size = "9"
        request.post_spri_concentration = "10"
        request.post_spri_volume = "30"
        request.final_nano_drop_280 = "180"
        request.final_nano_drop_230 = "130"
        request.final_nano_drop = "100"
        request.shearing_qc_comments = ""
        request.date_submitted_utc = datetime.now(UTC).timestamp() * 1000

        return traction_qc_message

    @pytest.fixture()
    def invalid_traction_qc_message(self):
        traction_qc_message = TractionQcMessage()
        request = traction_qc_message.create_request()
        request.sheared_femto_fragment_size = "5"

        return traction_qc_message

    def test_can_initialize_traction_qc_message(self):
        assert TractionQcMessage() is not None

    def test_validate_traction_qc_message(self, valid_traction_qc_message, invalid_traction_qc_message):
        traction_qc_message = TractionQcMessage()
        assert not traction_qc_message.validate()
        assert not invalid_traction_qc_message.validate()
        assert valid_traction_qc_message.validate()

    def test_can_generate_correct_payload(self, valid_traction_qc_message, freezer):
        payload = valid_traction_qc_message.payload()

        expected_payload = {
            "data": {
                "attributes": {
                    "qc_results_list": [
                        {
                            "final_nano_drop": "200",
                            "final_nano_drop_230": "230",
                            "final_nano_drop_280": "280",
                            "post_spri_concentration": "10",
                            "post_spri_volume": "20",
                            "sheared_femto_fragment_size": "5",
                            "shearing_qc_comments": "Comments",
                            "date_submitted": datetime.now(UTC).timestamp() * 1000,
                            "labware_barcode": "FD20706500",
                            "sample_external_id": "sanger_sample_id_DDD",
                        },
                        {
                            "final_nano_drop": "100",
                            "final_nano_drop_230": "130",
                            "final_nano_drop_280": "180",
                            "post_spri_concentration": "10",
                            "post_spri_volume": "30",
                            "sheared_femto_fragment_size": "9",
                            "date_submitted": datetime.now(UTC).timestamp() * 1000,
                            "labware_barcode": "FD20706501",
                            "sample_external_id": "sanger_sample_id_DDD2",
                        },
                    ],
                    "source": "tol-lab-share.tol",
                },
                "type": "qc_receptions",
            }
        }

        assert payload == expected_payload

    def test_can_add_to_message_property_on_success(
        self, config, valid_traction_qc_message, valid_feedback_message, traction_qc_success_response
    ):
        feedback = valid_feedback_message
        with requests_mock.Mocker() as m:
            m.post(config.TRACTION_QC_URL, json=traction_qc_success_response, status_code=201)
            valid_traction_qc_message.send(config.TRACTION_QC_URL)
        valid_traction_qc_message.add_to_message_property(feedback)
        assert len(feedback.errors) == 0
        assert feedback.operation_was_error_free

    def test_can_add_to_message_property_when_errors(self, invalid_traction_qc_message, valid_feedback_message):
        assert not invalid_traction_qc_message.validate()
        feedback = valid_feedback_message
        invalid_traction_qc_message.add_to_message_property(feedback)
        assert len(feedback.errors) > 0
        assert not feedback.operation_was_error_free

    def test_qc_request_serializer_request_with_empty_strings(self):
        request = TractionQcMessageRequest()
        serial = QcRequestSerializer(request)
        request.final_nano_drop_280 = "1234"
        request.container_barcode = ""
        assert serial.payload() == {"final_nano_drop_280": "1234"}

    def test_qc_request_serializer_clear_empty_value_keys(self):
        request = TractionQcMessageRequest()
        serial = QcRequestSerializer(request)
        assert serial.clear_empty_value_keys({"asdf": "1234", "bcde": ""}) == {"asdf": "1234"}

    def test_raises_transient_error_when_traction_api_responds_502(self, valid_traction_qc_message, config):
        # This happens when the Traction API is down but nginx is still up.
        with requests_mock.Mocker() as m:
            m.post(config.TRACTION_URL, text="Error", status_code=502)
            with pytest.raises(TransientRabbitError):
                valid_traction_qc_message.send(config.TRACTION_URL)

    def test_raises_transient_error_when_post_raises(self, valid_traction_qc_message, config, mock_logger):
        # This happens when nginx serving Traction API is down.
        cause = requests.exceptions.RequestException()

        with requests_mock.Mocker() as m:
            m.post(config.TRACTION_URL, exc=cause)
            with pytest.raises(TransientRabbitError) as raised:
                valid_traction_qc_message.send(config.TRACTION_URL)

            assert "QcMessage" in raised.value.message
            mock_logger.exception.assert_called_once_with(cause)

    def test_can_detect_other_errors_on_sent(self, valid_traction_qc_message, config):
        with requests_mock.Mocker() as m:
            m.post(config.TRACTION_URL, text="Error", status_code=422)
            valid_traction_qc_message.send(config.TRACTION_URL)

        assert not valid_traction_qc_message.validate()
        assert len(valid_traction_qc_message.errors) > 0

    def test_sends_api_key_header(
        self, config, valid_traction_qc_message, traction_qc_success_response
    ):

        with requests_mock.Mocker() as m:
            m.post(config.TRACTION_QC_URL, json=traction_qc_success_response, status_code=201)
            valid_traction_qc_message.send(config.TRACTION_QC_URL)

            assert m.last_request.headers.get("X-Traction-Client-Id") == "traction-development"
