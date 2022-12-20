from tol_lab_share.messages.output_feedback_message import OutputFeedbackMessage
from typing import List
from tol_lab_share.error_codes import ErrorCode
from functools import cached_property
from tol_lab_share.data_resolvers.data_resolver_interface import DataResolverInterface
from itertools import chain


class MessageProperty(DataResolverInterface):
    def __init__(self, input):
        self._input = input
        self._errors = []
        self._properties = {}
        self.set_validators()

    def validate(self):
        return all(list([self._validate_properties(), self._validate_instance()]))

    @cached_property
    def value(self):
        return self._input

    def resolve(self):
        for property in self._properties_instances:
            property.resolve()

    def add_to_feedback_message(self, feedback_message: OutputFeedbackMessage) -> None:
        for property in self._properties_instances:
            property.add_to_feedback_message(feedback_message)
        self.add_errors_to_feedback_message(feedback_message)

    @property
    def errors(self) -> List[ErrorCode]:
        return list(chain.from_iterable([self._errors, self._errors_properties]))

    def add_error(self, error: ErrorCode) -> None:
        self._errors.append(error)

    def add_errors_to_feedback_message(self, feedback_message: OutputFeedbackMessage) -> None:
        for error in self.errors:
            feedback_message.add_error_code(error)

    def set_validators(self):
        self._validators = []

    def check_is_string(self):
        return isinstance(self._input, str)

    def _validate_properties(self):
        return all(list([property.validate() for property in self._properties_instances]))

    def _validate_instance(self):
        return all(list([validator() for validator in self._validators]))

    @property
    def _errors_properties(self) -> List[ErrorCode]:
        error_list = []
        for property in self._properties_instances:
            if len(property.errors) > 0:
                error_list.append(property.errors)
        return error_list

    @cached_property
    def _properties_instances(self) -> List[DataResolverInterface]:
        prop_list = []
        for property in list(self._properties.values()):

            if isinstance(property, list):
                for elem in list(property):
                    prop_list.append(elem)
            else:
                prop_list.append(property)
        return prop_list
