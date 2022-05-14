from base import FxDevice, Register
from utils import sumCheck, bTh


class FX3U(FxDevice):
    def request(self, register_type, register_offset, register_len):
        if register_type == Register.D:
            assert 0 < register_offset <= 7999

            inputOffset = register_offset * 2
            inputLen = register_len * 2
            lst = [2, 0x45, 0x30, 0x30] + bTh(inputOffset, 4, 0x4000) + bTh(inputLen, 2) + [3]
            lst += sumCheck(lst)

        elif register_type == Register.M:
            assert 0 < register_offset <= 479

            inputOffset = register_offset
            inputLen = register_len * 2
            lst = [2, 0x45, 0x30, 0x30, 0x38] + bTh(inputOffset, 3, 0x800) + bTh(inputLen, 2) + [3]
            lst += sumCheck(lst)
        else:
            raise NotImplemented

        req = bytes(lst)
        print(req)
        return req
