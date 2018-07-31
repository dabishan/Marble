from enum import Enum
import inspect
from pprint import pprint


class State(Enum):
    NEW, MODIFIED, SAVED, DELETED = 0, 1, 2, 3


class Structure(dict):
    fields = None
    _state = State.MODIFIED
    structure = True

    def __init__(self, **kwargs):
        super(Structure, self).__init__()
        for key, value in kwargs.items():
            self.__setitem__(key, value)

    def _map(self, key, value):
        if key in self.fields and 'type' in self.fields[key].keys():
            if self.fields[key]['type'] is type(value):
                return value
            elif type(value) == dict:
                return self.fields[key]['type'](**value)
            elif type(value) == int and self.fields[key]['type'] is float:
                return float(value)

            raise ValueError("{} field should be of type {}, got {}".format(key, self.fields[key]['type'], type(value)))

        return value

    def __setitem__(self, key, value):
        if self._state == State.DELETED:
            raise ValueError("Tried to update deleted item")
        mapped_value = self._map(key, value)
        self.__validate_type(key, mapped_value)
        super(Structure, self).__setitem__(key, self._map(key, mapped_value))
        self._state = State.MODIFIED

    def __delitem__(self, key):
        if self._state == State.DELETED:
            raise ValueError("Tried to update deleted item")
        super(Structure, self).__delitem__(key)
        self._state = State.MODIFIED

    def validate(self):
        for key, value in self.items():
            if key in self and issubclass(type(self[key]), Structure):
                value.validate()

        if self.fields is not None:
            for key, value in self.fields.items():
                if 'required' in value and value['required'] is True and key not in self.keys():
                    raise ValueError("Required field {} is Empty".format(key))



    def __validate_type(self, key, value):
        if key in self.fields.keys():
            if 'type' in self.fields[key].keys() and type(value) is not self.fields[key]['type']:
                raise ValueError("{} field should be of type {}, got {}".format(key, self.fields[key]['type'], type(value)))
