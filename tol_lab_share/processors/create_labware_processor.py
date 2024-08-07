import logging
from typing import Any

from lab_share_lib.processing.base_processor import BaseProcessor
from lab_share_lib.processing.rabbit_message import RabbitMessage
from lab_share_lib.rabbit.basic_publisher import BasicPublisher
from lab_share_lib.rabbit.schema_registry import SchemaRegistry

from tol_lab_share import error_codes
from tol_lab_share.messages.rabbit.consumed import CreateLabwareMessage
from tol_lab_share.messages.rabbit.published import CreateLabwareFeedbackMessage
from tol_lab_share.messages.traction import TractionReceptionMessage, TractionQcMessage

logger = logging.getLogger(__name__)


class CreateLabwareProcessor(BaseProcessor):
    """Class to handle consuming create-labware messages from TOL"""

    def __init__(self, schema_registry: SchemaRegistry, basic_publisher: BasicPublisher, config: Any):
        """Resets data for the processor
        Parameters:
        schema_registry (SchemaRegistry) the redpanda schema registry we will us to validate messages
        basic_publisher (BasicPublisher) instance that will provide the communication with the queues system
        config (Any) mainconfiguration from the app
        """
        logger.debug("CreateLabwareProcessor::__init__")

        self._basic_publisher = basic_publisher
        self._schema_registry = schema_registry
        self._config = config

    @staticmethod
    def instantiate(
        schema_registry: SchemaRegistry, basic_publisher: BasicPublisher, config: Any
    ) -> "CreateLabwareProcessor":
        """Instantiate a CreateLabwareProcessor"""
        return CreateLabwareProcessor(schema_registry, basic_publisher, config)

    def process(self, message: RabbitMessage) -> bool:
        """Receives a message from rabbitmq. Parses the message with CreateLabwareMessage and validates
        that it is correct. If is correct, it will generate a new OutputTractionMessage and send it to Traction.
        The result of this operation will be aggregated to a feedback message and this message will be published
        back into the feedback queue.
        If there is any error on the input message received, it will add all the errors from the parsing into
        a feedback message and send message back to the feedback queue.
        If a feedback message could be generated and sent correctly, this method will return True.
        If there was any major issue and this feedback message could not be generated and sent, the method will
        return False. This will also trigger publishing the input message into the dead letters queue so a
        user can have a look at the message to debug what was the problem.
        Parameters:
        message (RabbitMessage) message received in the create-labware queue
        Returns:
        boolean indicating that the message could be correctly processed (parsed correctly and sent to traction).
        If not, it will return False, which will trigger sending this message to the dead letters queue.
        """
        logger.debug("CreateLabwareProcessor::process")

        output_feedback_message = CreateLabwareFeedbackMessage()
        input = CreateLabwareMessage(message)
        validation = input.validate()

        input.add_to_message_property(output_feedback_message)

        if validation:
            traction_reception_message = TractionReceptionMessage()
            input.add_to_message_property(traction_reception_message)
            logger.info("Attempting to send to traction")
            traction_reception_message.send(url=self._config.TRACTION_URL)
            traction_reception_message.add_to_message_property(output_feedback_message)

            if len(traction_reception_message.errors) > 0:
                error_codes.ERROR_16_PROBLEM_TALKING_WITH_TRACTION.trigger(
                    text=f":{traction_reception_message.errors}", instance=self
                )
            else:
                self.send_qc_data_to_traction(input, output_feedback_message)
        else:
            error_codes.ERROR_17_INPUT_MESSAGE_INVALID.trigger(text=f":{input.errors}", instance=self)

        if output_feedback_message.validate():
            output_feedback_message.publish(
                publisher=self._basic_publisher,
                schema_registry=self._schema_registry,
                exchange="psd.tol",
            )
            logger.info("Message process completed")
        else:
            error_codes.ERROR_18_FEEDBACK_MESSAGE_INVALID.trigger(instance=self)
            return False

        return True

    def send_qc_data_to_traction(
        self, input: CreateLabwareMessage, feedback_message: CreateLabwareFeedbackMessage
    ) -> bool:
        """Send qc data to traction, if there is any error, add to feedback message"""
        traction_qc_message = TractionQcMessage()
        input.add_to_message_property(traction_qc_message)
        logger.info("Attempting to send qc message to traction")
        traction_qc_message.send(url=self._config.TRACTION_QC_URL)
        traction_qc_message.add_to_message_property(feedback_message)

        if len(traction_qc_message.errors) > 0:
            error_codes.ERROR_28_PROBLEM_TALKING_TO_TRACTION.trigger(
                text=f":{traction_qc_message.errors}", instance=self
            )
            return False
        return True
