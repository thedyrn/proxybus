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


class Plc:
    fx1s = 'fx1s'
    fx3u = 'fx3u'


class Bus:
    def __init__(self, ip_adr, tcp_port, timeout):
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
        if self._sock:
            self._sock.close()

    def request(self, plc_type, register_type, register_offset, register_len) -> Response:
        try:
            return self._request(plc_type, register_type, register_offset, register_len)
        except Exception:
            self.close()
            raise

    def _request(self, plc_type, register_type, register_offset, register_len) -> Response:
        assert (register_len <= 0) or (register_len > 100)

        if (plc_type == Plc.fx1s) and (register_type == Register.D):
            assert (register_offset < 0) or (register_offset > 255)

            inputOffset = register_offset * 2
            inputLen = register_len*2
            lst = [2, 0x30, 0x31] + bTh(inputOffset, 3) + bTh(inputLen, 2)+ [3]
            lst += sumCheck(lst)
            req = bytes(lst)
            print(req)

        elif (plc_type == Plc.fx3u) and (register_type == Register.D):
            assert (register_offset < 0) or (register_offset > 7999)

            inputOffset = register_offset * 2
            inputLen = register_len*2
            lst = [2, 0x45, 0x30, 0x30] + bTh(inputOffset, 4, 0x4000) + bTh(inputLen, 2)+ [3]
            lst += sumCheck(lst)
            req = bytes(lst)
            print(req)

        elif (plc_type == Plc.fx3u) and (register_type == Register.M):
            assert (register_offset < 0) or (register_offset > 479)

            inputOffset = register_offset
            inputLen = register_len*2
            lst = [2, 0x45, 0x30, 0x30, 0x38] + bTh(inputOffset, 3, 0x800) + bTh(inputLen, 2)+ [3]
            lst += sumCheck(lst)
            req = bytes(lst)
            print(req)
        else:
            raise NotImplemented

        self.sock.sendall(req)

        data = b''

        while True:
            data += self.sock.recv(256)
            if data[-3] == 3:
                break

        print(data)

        return Response(data)


if __name__ == '__main__':
    bus = Bus('localhost', 5556, 2)
    print(bus.request(Plc.fx1s, Register.D, 250, 30).decode_16bit())
