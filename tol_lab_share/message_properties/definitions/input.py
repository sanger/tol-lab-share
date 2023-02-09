from .message_property import MessageProperty
from functools import cached_property
import logging
from typing import List, Callable

logger = logging.getLogger(__name__)


class Input(MessageProperty):
    """MessageProperty subclass to manage access to any value, acting as an access interface
    to provide a MessageProperty-like instance to access the value.
    """

    @cached_property
    def value(self):
        self.setup()
        return self._input

    @property
    def validators(self) -> List[Callable]:
        """Defines the list of validators"""
        return []
