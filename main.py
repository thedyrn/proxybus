import socket

from utils import sumCheckBytes, sumCheck, bTh


class CheckSumFail(Exception):
    ...


class OutOfRange(Exception):
    ...


class Response:
    def __init__(self, data):
        self.data = data

    def decode_16bit(self):
        sc = bytes(sumCheckBytes(self.data))
        if self.data[-2:] != sc:
            raise CheckSumFail

        bb = bytes.fromhex(self.data[1:-3].decode('utf-8'))
        out = []
        i = 0
        while i < len(bb):
            out += [bb[i + 1] * 256 + bb[i]]
            i += 2
        return out


class Register:
    D = 'D'
    M = 'M_16b'


class Device:
    MAP = {}

    def __init__(self, request_map=None):
        self.request_map = request_map or self.MAP

    def modbus_request(self, address, count=1):
        if address not in self.request_map:
            raise OutOfRange

        request_data = self.request_map[address]

        assert 0 <= request_data[1] < 100

        return self.request(*request_data)

    @staticmethod
    def request(register_type, register_offset, register_len):
        raise NotImplemented


class FX1S(Device):
    MAP = {}

    @staticmethod
    def request(register_type, register_offset, register_len):
        if register_type == Register.D:
            assert 0 < register_offset < 255

            inputOffset = register_offset * 2
            inputLen = register_len * 2
            lst = [2, 0x30, 0x31] + bTh(inputOffset, 3) + bTh(inputLen, 2) + [3]
            lst += sumCheck(lst)
        else:
            raise NotImplemented

        req = bytes(lst)
        print(req)
        return req


class FX3U(Device):
    MAP = {}

    @staticmethod
    def request(register_type, register_offset, register_len):
        if register_type == Register.D:
            assert 0 < register_offset < 7999

            inputOffset = register_offset * 2
            inputLen = register_len * 2
            lst = [2, 0x45, 0x30, 0x30] + bTh(inputOffset, 4, 0x4000) + bTh(inputLen, 2) + [3]
            lst += sumCheck(lst)

        elif register_type == Register.M:
            assert 0 < register_offset < 479

            inputOffset = register_offset
            inputLen = register_len * 2
            lst = [2, 0x45, 0x30, 0x30, 0x38] + bTh(inputOffset, 3, 0x800) + bTh(inputLen, 2) + [3]
            lst += sumCheck(lst)
        else:
            raise NotImplemented

        req = bytes(lst)
        print(req)
        return req


class Bus:
    def __init__(self, device: Device, ip_adr, tcp_port, timeout):
        self.device = device
        self.address = (ip_adr, tcp_port)
        self.timeout = timeout
        self._sock = None

    @property
    def sock(self):
        if self._sock is None:
            self._sock = socket.socket()
            self._sock.settimeout(self.timeout)
            self._sock.connect(self.address)

        return self._sock

    def close(self):
        if self._sock is not None:
            self._sock.close()
            self._sock = None

    def request(self, address, count=1) -> Response:
        try:
            return self._request(address, count)
        except Exception:
            self.close()
            raise

    def _request(self, address, count) -> Response:
        req = self.device.modbus_request(address, count)

        self.sock.sendall(req)

        data = b''

        while True:
            data += self.sock.recv(256)
            if data[-3] == 3:
                break

        print(data)

        return Response(data)


if __name__ == '__main__':
    # Register.D, 250, 30
    # register, offset, len
    device = FX1S(
        request_map={
            255: (Register.D, 250, 30)
        }
    )
    bus = Bus(device, 'localhost', 5556, 2)
    print(bus.request(255).decode_16bit())
    bus.close()
