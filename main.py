import logging
from pymodbus.version import version
from pymodbus.server.asynchronous import StartTcpServer

from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext

import config
from plc_bus import Bus as PlcBus, FX1S, Register
from modbus import RemoteDataBlock

FORMAT = ('%(asctime)-15s %(threadName)-15s'
          ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)


def run_async_server(modbus_address, plc_address, timeout=2):
    device = FX1S(
        request_map={
            range(8000): lambda address: (Register.D, address)
        }
    )
    bus = PlcBus(device=device, ip_adr=plc_address[0], tcp_port=plc_address[1], timeout=timeout)
    slave_1 = ModbusSlaveContext(
        hr=RemoteDataBlock(bus),
        ir=RemoteDataBlock(bus),
        zero_mode=False  # начинаем адрес с 1
    )
    context = ModbusServerContext(slaves=slave_1, single=True)
    # slave_2 = ModbusSlaveContext(
    #     hr=RemoteDataBlock(bus),
    #     ir=RemoteDataBlock(bus),
    #     zero_mode=True
    # )
    #
    # context = ModbusServerContext(
    #     slaves={0x00: slave_1, 0x01: slave_2},  # slave_id и соответствующий slave context
    #     single=False  # несколько слейв айди
    # )

    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Proxybus'
    identity.ProductCode = 'PB'
    identity.VendorUrl = 'https://github.com/thedyrn/proxybus'
    identity.ProductName = 'Proxybus Server'
    identity.ModelName = 'Proxybus Server Alpha 1'
    identity.MajorMinorRevision = version.short()

    try:
        StartTcpServer(context, identity=identity, address=modbus_address)
    except BaseException as e:
        bus.close()
        raise e

    # TCP Server with deferred reactor run

    # from twisted.internet import reactor
    # StartTcpServer(context, identity=identity, address=("localhost", 5020),
    #                defer_reactor_run=True)
    # reactor.run()

    # Server with RTU framer
    # StartTcpServer(context, identity=identity, address=("localhost", 5020),
    #                framer=ModbusRtuFramer)

    # UDP Server
    # StartUdpServer(context, identity=identity, address=("127.0.0.1", 5020))

    # RTU Server
    # StartSerialServer(context, identity=identity,
    #                   port='/dev/ttyp0', framer=ModbusRtuFramer)

    # ASCII Server
    # StartSerialServer(context, identity=identity,
    #                   port='/dev/ttyp0', framer=ModbusAsciiFramer)

    # Binary Server
    # StartSerialServer(context, identity=identity,
    #                   port='/dev/ttyp0', framer=ModbusBinaryFramer)


if __name__ == "__main__":
    if not config.multi_device:
        modbus_address = config.BRIDGES[0]['modbus_address']
        plc_address = config.BRIDGES[0]['plc_address']
        timeout = config.BRIDGES[0]['timeout']
        run_async_server(modbus_address, plc_address, timeout)
    else:
        import threading as th
        threads = []
        for bridge in config.BRIDGES:
            thread = th.Thread(
                target=run_async_server,
                args=(bridge['modbus_address'], bridge['plc_address'], bridge['timeout'],)
            )
            threads.append(thread)
            thread.daemon = True
            thread.start()

        cmd = input()
