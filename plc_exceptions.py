class PlcError(Exception):
    ...


class CheckSumFail(PlcError):
    ...


class OutOfRange(PlcError):
    ...
