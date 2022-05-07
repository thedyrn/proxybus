from pymodbus.datastore.store import BaseModbusDataBlock

from plc_bus import Bus as PlcBus, PlcError


class ModbusError(Exception):
    code = 0x04  # Невосстанавливаемая ошибка имела место,
    # пока ведомое устройство пыталось выполнить затребованное действие.


class CheckSumFail(ModbusError):
    ...


class OutOfRange(ModbusError):
    code = 0x02  # Адрес данных, указанный в запросе, недоступен.


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

        return any([address in _range for _range in self.plc_bus.device.request_map.keys()])

    def getValues(self, address, count=1):
        """ Returns the requested values from the datastore

        :param address: The starting address
        :param count: The number of values to retrieve
        :returns: The requested values from a:a+c
        """

        try:
            return self.plc_bus.request(address, count).decode_16bit()
        except PlcBus as e:
            return

    def setValues(self, address, values):
        """ Sets the requested values from the datastore

        :param address: The starting address
        :param values: The values to store
        """
        raise NotImplemented("Datastore Value Retrieve")