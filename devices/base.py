import typing as t
from abc import ABC, abstractmethod

from plc_exceptions import OutOfRange, CheckSumFail
from utils import sumCheckBytes


class Request:
    def __init__(self, register_type, register_offset, register_len, request_data):
        self.register_type = register_type
        self.register_offset = register_offset
        self.register_len = register_len

        self.request_data = request_data


class Device(ABC):
    @abstractmethod
    def validate_request(self, address: int, count: int) -> bool:
        raise NotImplementedError

    def encode(self, address: int, count: int = 1) -> Request:
        if not self.validate_request(address, count):
            raise OutOfRange

        return self._encode_request(address, count)

    @abstractmethod
    def _encode_request(self, address: int, count: int) -> Request:
        raise NotImplementedError

    def decode(self, request: Request, response_data: bytes) -> list:
        return self._decode_response(request, response_data)

    @abstractmethod
    def _decode_response(self, request: Request, response_data: bytes) -> list:
        raise NotImplementedError


class Register:
    D = 'D'
    D8000 = 'D8000'
    R = 'R'
    TN = 'TN'
    CN = 'CN'
    CN200 = 'CN200'
    CN235 = 'CN235'
    M_16b = 'M_16b'
    M8000_16b = 'M8000_16b'
    S = 'S'
    TS = 'TS'
    CS = 'CS'
    Y = 'Y'
    X = 'X'


class FxDevice(Device):
    MAP = {}

    def __init__(self, request_map=None):
        self.request_map: t.Dict[range, t.Callable] = request_map or self.MAP

    def validate_request(self, address: int, count: int) -> bool:
        for _range in self.request_map.keys():
            if address in _range:
                return True
        return False

    def _encode_request(self, address, count=1) -> Request:
        plc_address: t.Optional[tuple] = None
        for _range, _mapping in self.request_map.items():
            if address in _range:
                plc_address = _mapping(address)
                break

        if not plc_address:
            raise OutOfRange

        register_type, register_offset = plc_address

        assert 0 <= count < 100
        req_data = self.make_request(register_type, register_offset, register_len=count)
        return Request(
            request_data=req_data,
            register_type=register_type,
            register_offset=register_offset,
            register_len=count
        )

    def _decode_response(self, request: Request, response_data: bytes) -> list:
        req = response_data
        sc = bytes(sumCheckBytes(req))
        if req[-2:] != sc:
            raise CheckSumFail

        bb = bytes.fromhex(req[1:-3].decode('utf-8'))
        out = []
        i = 0
        while i < len(bb):
            out += [bb[i + 1] * 256 + bb[i]]
            i += 2
        return out

    @abstractmethod
    def make_request(self, register_type, register_offset, register_len) -> Request:
        raise NotImplemented
