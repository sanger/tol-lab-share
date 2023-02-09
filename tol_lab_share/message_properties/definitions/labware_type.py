from .message_property import MessageProperty
from tol_lab_share import error_codes
import logging
from typing import List, Callable

logger = logging.getLogger(__name__)

VALID_LABWARE_TYPES = ["Plate12x8", "Tube"]


class LabwareType(MessageProperty):
    """MessageProperty subclass to manage parsing of a valid labware type string provided by another
    MessageProperty. The labware type string has to any of these: ["Plate12x8", "Tube"]
    Eg: 'Plate12x8' for a plate
    """

    @property
    def validators(self) -> List[Callable]:
        """Defines the list of validators"""
        return [self.check_labware_type]

    def check_labware_type(self):
        """Checks that the received input contains a valid labware type. Triggers an error
        if that is not the case.
        Returns:
        bool with the result of the check
        """
        logger.debug("LabwareType::check_labware_type")
        if not self.check_is_string():
            return False
        result = self._input.value in VALID_LABWARE_TYPES
        if not result:
            self.trigger_error(error_codes.ERROR_6_LABWARE_TYPE, text=f"input: {self._input.value}")
        return result

    def pad_number(self, number: int) -> str:
        """Given a number, it generates a string of size 2 padded with zeros at the left representing
        the same value. Eg: 3 would be converted to '03', while 12 would be converted to '12'.
        Parameters:
        number (int) value we want to convert
        Returns:
        str with the padded value
        """
        padded_number = str(number)
        if len(padded_number) == 1:
            padded_number = f"0{padded_number}"
        return padded_number

    def _locations_for_plate12x8_column_order(self) -> List[str]:
        """It generates the list of all valid locations for a labware type following column
        order. Eg: ['A01', 'B01', 'C01', .... 'H12']
        Returns:
        List[str] with al the valid locations
        """
        locations = []
        for number in range(12):
            for letter_ord in range(ord("A"), ord("H") + 1):
                locations.append(f"{chr(letter_ord)}{self.pad_number(number+1)}")
        return locations

    def valid_locations(self) -> List[str]:
        """It returns the list of valid locations for the labware type. If the labware type is
        a tube, it returns ane empty list. If it is a plate 12x8 it returns all locations in
        column order.
        Returns:
        List[str] with all the valid locations
        """
        if self.value == "Plate12x8":
            return self._locations_for_plate12x8_column_order()
        else:
            return []
