from devices.fx3u import fx3u

MODBUS_ADDRESS = ('localhost', 5020)
TIMEOUT = 0.3

BRIDGES = [
    {'slave_id': 0x01, 'ip': 'localhost', 'port': 5226, 'device': fx3u},
]
