import logging
from pymodbus.version import version
from pymodbus.server.asynchronous import StartTcpServer

from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext

import config
from plc_bus import Bus as PlcBus
from modbus import RemoteDataBlock

FORMAT = ('%(asctime)-15s %(threadName)-15s'
          ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)


def run_async_server():
    slaves: dict = {}
    buses: list = []
    for bridge in config.BRIDGES:
        bus = PlcBus(
            device=bridge['device'], ip_adr=bridge['ip'], tcp_port=bridge['port'], timeout=config.TIMEOUT
        )
        buses.append(bus)

        slaves[bridge['slave_id']] = ModbusSlaveContext(
            hr=RemoteDataBlock(bus),
            ir=RemoteDataBlock(bus),
            zero_mode=False  # начинаем адрес с 1
        )

    context = ModbusServerContext(slaves=slaves, single=False)

    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Proxybus'
    identity.ProductCode = 'PB'
    identity.VendorUrl = 'https://github.com/thedyrn/proxybus'
    identity.ProductName = 'Proxybus Server'
    identity.ModelName = 'Proxybus Server Alpha 1'
    identity.MajorMinorRevision = version.short()

    try:
        StartTcpServer(context, identity=identity, address=config.MODBUS_ADDRESS)
    except BaseException as e:
        for bus in buses:
            bus.close()
        raise e


if __name__ == "__main__":
    run_async_server()
