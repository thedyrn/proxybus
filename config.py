from devices.fx1s import FX1S, Register

MODBUS_ADDRESS = ('localhost', 5020)
TIMEOUT = 2

fx1s = FX1S(
        request_map={
            range(8000): lambda address: (Register.D, address)
        }
    )

BRIDGES = [
    {'slave_id': 0x00, 'ip': 'localhost', 'port': 5226, 'device': fx1s},
]
