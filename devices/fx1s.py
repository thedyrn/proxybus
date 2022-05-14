from devices.base import FxDevice, Register
from utils import sumCheck, bTh


class FX1S(FxDevice):
    def request(self, register_type, register_offset, register_len):
        if register_type == Register.D:
            assert 0 < register_offset <= 255

            inputOffset = register_offset * 2
            inputLen = register_len * 2
            lst = [2, 0x30, 0x31] + bTh(inputOffset, 3) + bTh(inputLen, 2) + [3]
            lst += sumCheck(lst)
        else:
            raise NotImplementedError

        req = bytes(lst)
        print(req)
        return req
