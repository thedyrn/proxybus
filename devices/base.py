import typing as t
from abc import ABC, abstractmethod

from plc_exceptions import OutOfRange, CheckSumFail
from utils import sumCheckBytes


class Device(ABC):
    @abstractmethod
    def validate_request(self, address: int, count: int) -> bool:
        raise NotImplementedError

    def encode(self, address, count=1):
        if not self.validate_request(address, count):
            raise OutOfRange

        return self._encode_request(address, count)

    @abstractmethod
    def _encode_request(self, address, count):
        raise NotImplementedError

    @abstractmethod
    def decode(self, response):
        raise NotImplementedError


class Register:
    D = 'D'
    M = 'M_16b'


class FxDevice(Device):
    MAP = {}

    def __init__(self, request_map=None):
        self.request_map: t.Dict[range, t.Callable] = request_map or self.MAP

    def validate_request(self, address: int, count: int) -> bool:
        for _range in self.request_map.keys():
            if address in _range:
                return True
        return False

    def _encode_request(self, address, count=1):
        plc_address: t.Optional[tuple] = None
        for _range, _mapping in self.request_map.items():
            if address in _range:
                plc_address = _mapping(address)
                break

        if not plc_address:
            raise OutOfRange

        register_type, register_offset = plc_address

        assert 0 <= count < 100

        return self.request(register_type, register_offset, register_len=count)

    def decode(self, response):
        sc = bytes(sumCheckBytes(response))
        if response[-2:] != sc:
            raise CheckSumFail

        bb = bytes.fromhex(response[1:-3].decode('utf-8'))
        out = []
        i = 0
        while i < len(bb):
            out += [bb[i + 1] * 256 + bb[i]]
            i += 2
        return out

    @abstractmethod
    def request(self, register_type, register_offset, register_len):
        raise NotImplemented
