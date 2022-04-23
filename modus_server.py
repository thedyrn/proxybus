import logging
from pymodbus.version import version
from pymodbus.server.asynchronous import StartTcpServer
from pymodbus.server.asynchronous import StartUdpServer
from pymodbus.server.asynchronous import StartSerialServer

from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore.store import BaseModbusDataBlock
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import (ModbusRtuFramer,
                                  ModbusAsciiFramer,
                                  ModbusBinaryFramer)

from main import Bus as PlcBus, FX1S, Register


FORMAT = ('%(asctime)-15s %(threadName)-15s'
          ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)


class RemoteDataBlock(BaseModbusDataBlock):
    def __init__(self, plc_bus: PlcBus):
        self.plc_bus = plc_bus

        # default values
        self.default_value = False
        self.values: list = []
        self.address = None

    def default(self, count, value=False):
        """ Used to initialize a store to one value

        :param count: The number of fields to set
        :param value: The default value to set to the fields
        """
        self.default_value = value
        self.values = [self.default_value] * count
        self.address = 0x00

    def reset(self):
        """ Resets the datastore to the initialized default value """
        self.values = [self.default_value] * len(self.values)

    def validate(self, address, count=1):
        """ Checks to see if the request is in range

        :param address: The starting address
        :param count: The number of values to test for
        :returns: True if the request in within range, False otherwise
        """

        return address in self.plc_bus.device.request_map  # TODO правильная проверка

    def getValues(self, address, count=1):
        """ Returns the requested values from the datastore

        :param address: The starting address
        :param count: The number of values to retrieve
        :returns: The requested values from a:a+c
        """

        return self.plc_bus.request(address, count)

    def setValues(self, address, values):
        """ Sets the requested values from the datastore

        :param address: The starting address
        :param values: The values to store
        """
        raise NotImplemented("Datastore Value Retrieve")


def run_async_server():
    device = FX1S(
        request_map={
            255: (Register.D, 250, 30)
        }
    )
    bus = PlcBus(device, 'localhost', 5556, 2)
    store = ModbusSlaveContext(
        hr=RemoteDataBlock(bus),
        ir=RemoteDataBlock(bus))

    # store.register(CustomModbusRequest.function_code, 'cm',
    #                ModbusSequentialDataBlock(0, [17] * 100))

    context = ModbusServerContext(slaves=store, single=True)

    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Proxybus'
    identity.ProductCode = 'PB'
    identity.VendorUrl = 'https://github.com/thedyrn/proxybus'
    identity.ProductName = 'Proxybus Server'
    identity.ModelName = 'Proxybus Server Alpha 1'
    identity.MajorMinorRevision = version.short()

    try:
        StartTcpServer(context, identity=identity, address=("localhost", 5020))
    except BaseException:
        bus.close()

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
    run_async_server()
