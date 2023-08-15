from .message_property import MessageProperty
from typing import List, Callable


class ShearedFemtoFragmentSize(MessageProperty):
    """MessageProperty subclass to manage parsing of a valid Sheared Femto Fragment Size string provided by another
    MessageProperty.
    The Sheared Femto Fragment Size has to be a string.
    Eg: '20'
    """

    @property
    def validators(self) -> List[Callable]:
        """Defines the list of validators"""
        return [self.check_is_string]