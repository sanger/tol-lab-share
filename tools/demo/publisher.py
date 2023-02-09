import os
import argparse
from lab_share_lib.rabbit.schema_registry import SchemaRegistry
from lab_share_lib.rabbit.basic_publisher import BasicPublisher
from lab_share_lib.rabbit.avro_encoder import AvroEncoderJson, AvroEncoderBinary
from lab_share_lib.types import RabbitServerDetails
from lab_share_lib.constants import RABBITMQ_HEADER_VALUE_ENCODER_TYPE_JSON, RABBITMQ_HEADER_VALUE_ENCODER_TYPE_BINARY
from uuid import uuid4
from testing_data import build_create_labware_96_msg, build_update_labware_msg, build_create_tube_msg

REDPANDA_URL = os.getenv("REDPANDA_URL", "http://localhost")
REDPANDA_API_KEY = os.getenv("REDPANDA_API_KEY", "test")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "5671")
RABBITMQ_USERNAME = os.getenv("RABBITMQ_USERNAME", "psd")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "psd")
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "tol")
RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "tol-team.tol")
RABBITMQ_ROUTING_KEY = os.getenv("RABBITMQ_ROUTING_KEY", "crud.1")
INPUT_ENCODER = os.getenv("INPUT_ENCODER", "json")
UNIQUE_ID = os.getenv("UNIQUE_ID")


def encoder_config_for(encoder_type_selection):
    if encoder_type_selection == "json":
        return {"encoder_class": AvroEncoderJson, "encoder_type": RABBITMQ_HEADER_VALUE_ENCODER_TYPE_JSON}
    else:
        return {"encoder_class": AvroEncoderBinary, "encoder_type": RABBITMQ_HEADER_VALUE_ENCODER_TYPE_BINARY}


def send_message(msg, subject, registry, publisher, version="latest"):
    print(f"Want to send { subject } message { msg }\n")

    encoder_selected = INPUT_ENCODER
    encoder_class = encoder_config_for(encoder_selected)["encoder_class"]
    encoder_type = encoder_config_for(encoder_selected)["encoder_type"]

    encoder = encoder_class(registry, subject)
    if encoder_type == RABBITMQ_HEADER_VALUE_ENCODER_TYPE_BINARY:
        encoder.set_compression_codec("snappy")

    #encoded_message = encoder.encode([msg], version="latest")
    encoded_message = encoder.encode([msg], version)

    print(f"Publishing message { encoded_message }\n")

    publisher.publish_message(
        RABBITMQ_EXCHANGE,
        RABBITMQ_ROUTING_KEY,
        encoded_message.body,
        subject,
        encoded_message.version,
        encoder_type,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TOL LabShare message publisher demo script.")
    parser.add_argument("unique_id")

    args = parser.parse_args()

    registry = SchemaRegistry(REDPANDA_URL, REDPANDA_API_KEY, verify=False)

    rabbitmq_details = RabbitServerDetails(
        uses_ssl=False,
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        username=RABBITMQ_USERNAME,
        password=RABBITMQ_PASSWORD,
        vhost=RABBITMQ_VHOST,
    )
    publisher = BasicPublisher(rabbitmq_details, publish_retry_delay=5, publish_max_retries=36, verify_cert=False)

    labware_uuid = str(uuid4()).encode()

    for pos in range(0, 5):
        sample_msg = build_create_labware_96_msg(args.unique_id, pos)
        update_msg = build_update_labware_msg(sample_msg)
        tube_msg = build_create_tube_msg(args.unique_id, pos)
        send_message(sample_msg, "create-labware", registry, publisher, "2")
        send_message(update_msg, "update-labware", registry, publisher)
        send_message(tube_msg, "create-labware", registry, publisher)
