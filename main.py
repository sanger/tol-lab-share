import time
import logging
import logging.config
from tol_lab_share.helpers import get_config
from lab_share_lib.rabbit.rabbit_stack import RabbitStack
import os

config = get_config("")
logging.config.dictConfig(config.LOGGING)

logger = logging.getLogger(__name__)

settings = os.getenv("SETTINGS_MODULE", "tol_lab_share.config.defaults")

if __name__ == "__main__":
    print("Starting TOL consumer")
    rabbit_stack = RabbitStack(settings)

    rabbit_stack.bring_stack_up()

    try:
        while True:
            if rabbit_stack.is_healthy:
                logger.debug("RabbitStack thread is running healthy")
            time.sleep(5)
    except KeyboardInterrupt:
        print("Stopping TOL consumer...")
