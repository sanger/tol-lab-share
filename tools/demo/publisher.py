import argparse
import os

from lab_share_lib.config.rabbit_server_details import RabbitServerDetails
from lab_share_lib.constants import RABBITMQ_HEADER_VALUE_ENCODER_TYPE_BINARY, RABBITMQ_HEADER_VALUE_ENCODER_TYPE_JSON
from lab_share_lib.rabbit.avro_encoder import AvroEncoderBinaryMessage, AvroEncoderJson
from lab_share_lib.rabbit.basic_publisher import BasicPublisher
from lab_share_lib.rabbit.schema_registry import SchemaRegistry

from bioscan_pool_xp_messages import build_bioscan_pool_xp_msg
from create_labware_messages import (
    build_create_labware_96_msg,
    build_update_labware_msg,
    build_create_tube_msg,
    build_create_tube_msg_without_retention_instruction,
)

REDPANDA_URL = os.getenv("REDPANDA_URL", "http://localhost:8081")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "5672")
RABBITMQ_USERNAME = os.getenv("RABBITMQ_USERNAME", "admin")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "development")
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "tol")
RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "tol-team.tol")
RABBITMQ_ROUTING_KEY = os.getenv("RABBITMQ_ROUTING_KEY", "crud.1")


def encoder_config_for(encoder_type_selection):
    if encoder_type_selection == "json":
        return {"encoder_class": AvroEncoderJson, "encoder_type": RABBITMQ_HEADER_VALUE_ENCODER_TYPE_JSON}
    else:
        return {"encoder_class": AvroEncoderBinaryMessage, "encoder_type": RABBITMQ_HEADER_VALUE_ENCODER_TYPE_BINARY}


def send_message(msg, subject, encoder, registry, publisher):
    print(f"Want to send {subject} message {msg}\n")

    encoder_class = encoder_config_for(encoder)["encoder_class"]
    encoder_type = encoder_config_for(encoder)["encoder_type"]

    encoder = encoder_class(registry, subject)

    encoded_message = encoder.encode([msg], version="1")

    print(f"Publishing message {encoded_message}\n")

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
    parser.add_argument(
        "--encoder", default="json", help="The encoder to use for the messages.", choices=["json", "binary"]
    )
    parser.add_argument("--unique_id", required=True, help="Unique ID for the messages.")
    parser.add_argument(
        "--message_types",
        required=True,
        help="The type of messages being sent.",
        choices=["create-update-labware", "bioscan-pool-xp-to-traction", "create-labware"],
    )
    parser.add_argument("--loop", required=False, default=False, help="Send request iteratively", choices=[True, False])

    args = parser.parse_args()

    registry = SchemaRegistry(REDPANDA_URL, verify=False)

    rabbitmq_details = RabbitServerDetails(
        uses_ssl=False,
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        username=RABBITMQ_USERNAME,
        password=RABBITMQ_PASSWORD,
        vhost=RABBITMQ_VHOST,
    )
    publisher = BasicPublisher(rabbitmq_details, publish_retry_delay=5, publish_max_retries=36, verify_cert=False)
    encoder = args.encoder

    loop = bool(args.loop)

    if loop:
        for pos in range(0, 5):
            if args.message_types == "create-update-labware":
                sample_msg = build_create_labware_96_msg(args.unique_id, pos)
                update_msg = build_update_labware_msg(sample_msg)
                tube_msg = build_create_tube_msg(args.unique_id, pos)
                send_message(sample_msg, "create-labware", encoder, registry, publisher)
                send_message(update_msg, "update-labware", encoder, registry, publisher)
                send_message(tube_msg, "create-labware", encoder, registry, publisher)
            elif args.message_types == "bioscan-pool-xp-to-traction":
                pool_xp_msg = build_bioscan_pool_xp_msg(args.unique_id, pos)
                send_message(pool_xp_msg, "bioscan-pool-xp-tube-to-traction", encoder, registry, publisher)
    else:
        if args.message_types == "create-update-labware":
            sample_msg = build_create_labware_96_msg(args.unique_id, 1)
            update_msg = build_update_labware_msg(sample_msg)
            tube_msg = build_create_tube_msg(args.unique_id, 3)
            send_message(update_msg, "update-labware", encoder, registry, publisher)
            send_message(tube_msg, "create-labware", encoder, registry, publisher)
            send_message(sample_msg, "create-labware", encoder, registry, publisher)
        elif args.message_types == "create-labware":
            # tube_msg = build_create_tube_msg(args.unique_id, 3)
            tube_msg_without_retention_instruction = build_create_tube_msg_without_retention_instruction(
                args.unique_id, 4
            )
            # send_message(tube_msg, "create-labware", encoder, registry, publisher)
            send_message(tube_msg_without_retention_instruction, "create-labware", encoder, registry, publisher)
        else:
            print("Error in argument inputs.")
