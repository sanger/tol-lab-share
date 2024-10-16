from lab_share_lib.config.rabbit_config import RabbitConfig, MessageSubjectConfig

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

from .rabbit_servers import TOL_RABBIT_SERVER, ISG_RABBIT_SERVER, MLWH_RABBIT_SERVER

RABBITMQ_SERVERS = [
    RabbitConfig(
        consumer_details=TOL_RABBIT_SERVER,
        consumed_queue="tol.crud-operations",
        message_subjects={
            RABBITMQ_SUBJECT_CREATE_LABWARE: MessageSubjectConfig(
                processor=CreateLabwareProcessor, reader_schema_version="2"
            ),
            RABBITMQ_SUBJECT_UPDATE_LABWARE: MessageSubjectConfig(
                processor=UpdateLabwareProcessor, reader_schema_version="1"
            ),
        },
        publisher_details=TOL_RABBIT_SERVER,
    ),
    RabbitConfig(
        consumer_details=ISG_RABBIT_SERVER,
        consumed_queue="tls.poolxp-export-to-traction",
        message_subjects={
            RABBITMQ_SUBJECT_BIOSCAN_POOL_XP_TO_TRACTION: MessageSubjectConfig(
                processor=BioscanPoolXpToTractionProcessor, reader_schema_version="1"
            ),
        },
        publisher_details=ISG_RABBIT_SERVER,
    ),
    RabbitConfig(
        consumer_details=ISG_RABBIT_SERVER,
        consumed_queue="tls.volume-tracking",
        message_subjects={
            RABBITMQ_SUBJECT_CREATE_ALIQUOT_IN_MLWH: MessageSubjectConfig(
                processor=CreateAliquotProcessor, reader_schema_version="2"
            ),
        },
        publisher_details=MLWH_RABBIT_SERVER,
    ),
]
