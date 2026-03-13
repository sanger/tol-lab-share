from typing import Literal


RABBITMQ_SUBJECT_BIOSCAN_POOL_XP_TO_TRACTION = "bioscan-pool-xp-tube-to-traction"
RABBITMQ_SUBJECT_CREATE_ALIQUOT_IN_MLWH = "create-aliquot-in-mlwh"
RABBITMQ_SUBJECT_CREATE_LABWARE = "create-labware"
RABBITMQ_SUBJECT_UPDATE_LABWARE = "update-labware"
RABBITMQ_FEEDBACK_EXCHANGE = "psd.tol"
RABBITMQ_ROUTING_KEY_CREATE_LABWARE_FEEDBACK = "feedback.created.labware"
RABBITMQ_ROUTING_KEY_UPDATE_LABWARE_FEEDBACK = "feedback.updated.labware"
RABBITMQ_ROUTING_KEY_CREATE_ALIQUOT = "{environment}.saved.aliquot"
RABBITMQ_SUBJECT_CREATE_LABWARE_FEEDBACK = "create-labware-feedback"
RABBITMQ_SUBJECT_UPDATE_LABWARE_FEEDBACK = "update-labware-feedback"


OUTPUT_TRACTION_MESSAGE_SOURCE = "tol-lab-share.tol"

OUTPUT_BIOSCAN_TRACTION_MESSAGE_SOURCE = "tol-lab-share-bioscan.tol"

OUTPUT_TRACTION_MESSAGE_CONTAINER_TYPES = Literal["tubes", "wells"]
