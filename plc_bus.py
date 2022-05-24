import socket
import typing as t

from devices.base import Device, Register, Request
from devices.fx1s import FX1S


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

    def request(self, address, count=1) -> list:
        try:
            return self._request(address, count)
        except Exception:
            self.close()
            raise

    def _request(self, address, count) -> list:
        req: Request = self.device.encode(address, count)

        self.sock.sendall(req.request_data)

        data = b''

        while True:
            data += self.sock.recv(256)
            if len(data) > 3 and data[-3] == 3:
                break

        print(data)

        return self.device.decode(request=req, response_data=data)


if __name__ == '__main__':
    # Register.D, 250, 30
    # register, offset, len
    _device = FX1S(
        request_map={
            range(8000): lambda address: (Register.D, address)
        }
    )
    bus = Bus(_device, 'localhost', 5556, 2)
    print(bus.request(255))
    bus.close()
