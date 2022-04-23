import socket

from utils import sumCheckBytes, sumCheck, bTh


class CheckSumFail(Exception):
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
    @staticmethod
    def request(register_type, register_offset, register_len):
        raise NotImplemented


class FX1S(Device):
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
    def __init__(self, device, ip_adr, tcp_port, timeout):
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

    def request(self, register_type, register_offset, register_len) -> Response:
        try:
            return self._request(register_type, register_offset, register_len)
        except Exception:
            self.close()
            raise

    def _request(self, register_type, register_offset, register_len) -> Response:
        assert 0 <= register_len < 100
        req = self.device.request(register_type, register_offset, register_len)

        self.sock.sendall(req)

        data = b''

        while True:
            data += self.sock.recv(256)
            if data[-3] == 3:
                break

        print(data)

        return Response(data)


if __name__ == '__main__':
    bus = Bus(FX1S, 'localhost', 5556, 2)
    print(bus.request(Register.D, 250, 30).decode_16bit())
    bus.close()
