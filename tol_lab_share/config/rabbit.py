import os
from lab_share_lib.config.rabbit_config import RabbitConfig, ProcessorSchemaConfig
from lab_share_lib.config.rabbit_server_details import RabbitServerDetails

from tol_lab_share.constants import (
    RABBITMQ_SUBJECT_BIOSCAN_POOL_XP_TO_TRACTION,
    RABBITMQ_SUBJECT_CREATE_ALIQUOT_IN_MLWH,
    RABBITMQ_SUBJECT_CREATE_LABWARE,
    RABBITMQ_SUBJECT_UPDATE_LABWARE,
)
from tol_lab_share.processors.bioscan_pool_xp_to_traction_processor import BioscanPoolXpToTractionProcessor
from tol_lab_share.processors.create_labware_processor import CreateLabwareProcessor
from tol_lab_share.processors.update_labware_processor import UpdateLabwareProcessor
from tol_lab_share.processors.create_aliquot_processor import CreateAliquotProcessor

RABBIT_SERVER_DETAILS = RabbitServerDetails(
    uses_ssl=False,
    host=os.environ.get("LOCALHOST", "127.0.0.1"),
    port=5672,
    username=os.environ.get("RABBITMQ_USER", "admin"),
    password=os.environ.get("RABBITMQ_PASSWORD", "development"),
    vhost="tol",
)

# In our servers, this will be picked up using deployment project's
# roles/deploy_tol_stack/templates/tol-lab-share/app_config.py.j2 and
# environments/uat/group_vars/tol_swarm_managers.yml
MLWH_ENVIRONMENT_NAME = os.environ.get("MLWH_ENVIRONMENT_NAME", "development")

WAREHOUSE_RABBIT_SERVER_DETAILS = RabbitServerDetails(
    uses_ssl=False,
    host=os.environ.get("WAREHOUSE_RMQ_HOST", "127.0.0.1"),
    port=5672,
    username=os.environ.get("WAREHOUSE_RMQ_USER", "admin"),
    password=os.environ.get("WAREHOUSE_RMQ_PASSWORD", "development"),
    vhost="test",
)

RABBITMQ_SERVERS = [
    RabbitConfig(
        consumer_details=RABBIT_SERVER_DETAILS,
        consumed_queue="tls.poolxp-export-to-traction",
        processors={
            RABBITMQ_SUBJECT_BIOSCAN_POOL_XP_TO_TRACTION: BioscanPoolXpToTractionProcessor,
        },
        message_subjects={
            RABBITMQ_SUBJECT_BIOSCAN_POOL_XP_TO_TRACTION: ProcessorSchemaConfig(
                processor=BioscanPoolXpToTractionProcessor, reader_schema_version="1"
            )
        },
        publisher_details=RABBIT_SERVER_DETAILS,
    ),
    RabbitConfig(
        consumer_details=RABBIT_SERVER_DETAILS,
        consumed_queue="tol.crud-operations",
        processors={
            RABBITMQ_SUBJECT_CREATE_LABWARE: CreateLabwareProcessor,
            RABBITMQ_SUBJECT_UPDATE_LABWARE: UpdateLabwareProcessor,
        },
        message_subjects={
            RABBITMQ_SUBJECT_CREATE_LABWARE: ProcessorSchemaConfig(
                processor=CreateLabwareProcessor, reader_schema_version="1"
            ),
            RABBITMQ_SUBJECT_UPDATE_LABWARE: ProcessorSchemaConfig(
                processor=UpdateLabwareProcessor, reader_schema_version="1"
            ),
        },
        publisher_details=RABBIT_SERVER_DETAILS,
    ),
    RabbitConfig(
        consumer_details=RABBIT_SERVER_DETAILS,
        consumed_queue="tls.volume-tracking",
        processors={RABBITMQ_SUBJECT_CREATE_ALIQUOT_IN_MLWH: CreateAliquotProcessor},
        message_subjects={
            RABBITMQ_SUBJECT_CREATE_ALIQUOT_IN_MLWH: ProcessorSchemaConfig(
                processor=CreateAliquotProcessor, reader_schema_version="1"
            )
        },
        publisher_details=WAREHOUSE_RABBIT_SERVER_DETAILS,
    ),
]

RABBITMQ_PUBLISH_RETRY_DELAY = 5
RABBITMQ_PUBLISH_RETRIES = 36  # 3 minutes of retries
