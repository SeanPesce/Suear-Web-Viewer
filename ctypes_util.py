#!/usr/bin/env python3

import logging
from ctypes import Array, BigEndianStructure, LittleEndianStructure, sizeof

# Author: Jonathon Reinhart
# Source: https://gist.github.com/JonathonReinhart/b6f355f13021cd8ec5d0101e0e6675b2
class StructHelper(object):
    def __get_value_str(self, name, fmt='{}'):
        val = getattr(self, name)
        if isinstance(val, Array):
            val = list(val)
        elif isinstance(val, int):
            return f'{val:#x}'.ljust(18) + '  (' + fmt.format(val) + ')'
        return fmt.format(val)

    def __str__(self):
        result = '{}:\n'.format(self.__class__.__name__)
        maxname = max(len(name) for name, type_, *sz_ in self._fields_)
        for name, type_, *sz_ in self._fields_:
            value = getattr(self, name)
            result += '  {name:<{width}}: {value}'.format(
                    name = name,
                    width = maxname,
                    value = self.__get_value_str(name),
                    )
            result += '\n'
        return result

    def __repr__(self):
        return '{name}({fields})'.format(
                name = self.__class__.__name__,
                fields = ', '.join(
                    '{}={}'.format(name, self.__get_value_str(name, '{!r}')) for name, _, *sz_ in self._fields_)
                )

    @classmethod
    def _typeof(cls, field):
        """Get the type of a field
        Example: A._typeof(A.fld)
        Inspired by stackoverflow.com/a/6061483
        """
        for name, type_, *sz_ in cls._fields_:
            if getattr(cls, name) is field:
                return type_
        raise KeyError

    @classmethod
    def read_from(cls, f):
        result = cls()
        if f.readinto(result) != sizeof(cls):
            raise EOFError
        return result

    def get_bytes(self):
        """Get raw byte string of this structure
        ctypes.Structure implements the buffer interface, so it can be used
        directly anywhere the buffer interface is implemented.
        https://stackoverflow.com/q/1825715
        """
        # Works for either Python 2 or Python 3
        return bytearray(self)
    
    def validate(self):
        """Derived types can override this function to automatically throw errors if bad data is
        encountered after instantiating with from_bytes
        """
        return
    
    @classmethod
    def from_bytes(cls, buf):
        inst = cls.from_buffer_copy(buf)
        inst.validate()
        logging.debug(inst)
        return inst
    
    @classmethod
    def sizeof(cls):
        return sizeof(cls)


class StructLE(LittleEndianStructure, StructHelper):
    """Little endian structure class pre-configured for the majority of use-cases
    """
    _pack_ = 1


class StructBE(BigEndianStructure, StructHelper):
    """Big endian structure class pre-configured for the majority of use-cases
    """
    _pack_ = 1
