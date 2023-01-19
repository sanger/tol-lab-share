from .message_property import MessageProperty
import logging
from functools import cached_property
from datetime import datetime

logger = logging.getLogger(__name__)


class DateUtc(MessageProperty):
    @property
    def validators(self):
        return [self.check_is_date_utc]
