from devices.base import FxDevice, Register
from utils import sumCheck, bTh


class FX1S(FxDevice):
    def make_request(self, register_type, register_offset, register_len):
        if register_type == Register.D:
            inputOffset = register_offset * 2
            inputLen = register_len * 2
            lst = [2, 0x30, 0x31] + bTh(inputOffset, 3) + bTh(inputLen, 2) + [3]
            lst += sumCheck(lst)
        
        elif register_type == Register.CN:
            inputOffset = register_offset * 2
            inputLen = register_len * 2
            lst = [2, 0x30, 0x30] + bTh(inputOffset, 3, 0xA00) + bTh(inputLen, 2) + [3]
            lst += sumCheck(lst)
            
        
        elif register_type == Register.CN235:
            inputOffset = register_offset * 2
            inputLen = register_len * 2
            lst = [2, 0x30, 0x30] + bTh(inputOffset, 3, 0xC8C) + bTh(inputLen, 2) + [3]
            lst += sumCheck(lst)        
            
        else:
            raise NotImplementedError

        req = bytes(lst)
        print(req)
        return req


fx1s = FX1S(
        request_map={
            range(0, 256): lambda address: (Register.D, address),
            range(0xA340, 0xA360): lambda address: (Register.CN, address-0xA340),
            range(0xA44E, 0xA478): lambda address: (Register.CN235, address-0xA44E)
        }
    )
