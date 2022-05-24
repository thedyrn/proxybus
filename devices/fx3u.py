from devices.base import FxDevice, Register
from utils import sumCheck, bTh


class FX3U(FxDevice):
    def make_request(self, register_type, register_offset, register_len):
        if register_type == Register.D:
            inputOffset = register_offset * 2
            inputLen = register_len * 2
            lst = [2, 0x45, 0x30, 0x30] + bTh(inputOffset, 4, 0x4000) + bTh(inputLen, 2) + [3]
            lst += sumCheck(lst)
            
        elif register_type == Register.D8000:
            inputOffset = register_offset * 2
            inputLen = register_len * 2
            lst = [2, 0x45, 0x30, 0x30] + bTh(inputOffset, 4, 0x8000) + bTh(inputLen, 2) + [3]
            lst += sumCheck(lst)

        elif register_type == Register.R:
            inputOffset = register_offset * 2
            inputLen = register_len * 2
            lst = [2, 0x45, 0x30, 0x36] + bTh(inputOffset, 4, 0x0) + bTh(inputLen, 2) + [3]
            lst += sumCheck(lst)
            
        elif register_type == Register.TN:
            inputOffset = register_offset * 2
            inputLen = register_len * 2
            lst = [2, 0x45, 0x30, 0x30] + bTh(inputOffset, 4, 0x1000) + bTh(inputLen, 2) + [3]
            lst += sumCheck(lst)
            
        elif register_type == Register.CN:
            inputOffset = register_offset * 2
            inputLen = register_len * 2
            lst = [2, 0x45, 0x30, 0x30, 0x30] + bTh(inputOffset, 3, 0xA00) + bTh(inputLen, 2) + [3]
            lst += sumCheck(lst)		

        elif register_type == Register.CN200:
            inputOffset = register_offset * 2
            inputLen = register_len * 2
            lst = [2, 0x45, 0x30, 0x30, 0x30] + bTh(inputOffset, 3, 0xC00) + bTh(inputLen, 2) + [3]
            lst += sumCheck(lst)		

        elif register_type == Register.M_16b:
            inputOffset = register_offset
            inputLen = register_len * 2
            lst = [2, 0x45, 0x30, 0x30, 0x38] + bTh(inputOffset, 3, 0x800) + bTh(inputLen, 2) + [3]
            lst += sumCheck(lst)
            
        elif register_type == Register.M8000_16b:
            inputOffset = register_offset
            inputLen = register_len * 2
            lst = [2, 0x45, 0x30, 0x30, 0x38] + bTh(inputOffset, 3, 0xC00) + bTh(inputLen, 2) + [3]
            lst += sumCheck(lst)
            
        elif register_type == Register.S:
            inputOffset = register_offset
            inputLen = register_len * 2
            lst = [2, 0x45, 0x30, 0x30, 0x38] + bTh(inputOffset, 3, 0xC60) + bTh(inputLen, 2) + [3]
            lst += sumCheck(lst)
         
        elif register_type == Register.TS:
            inputOffset = register_offset
            inputLen = register_len * 2
            lst = [2, 0x45, 0x30, 0x30, 0x38] + bTh(inputOffset, 3, 0xCE0) + bTh(inputLen, 2) + [3]
            lst += sumCheck(lst)
         
        elif register_type == Register.CS:
            inputOffset = register_offset
            inputLen = register_len * 2
            lst = [2, 0x45, 0x30, 0x30, 0x38] + bTh(inputOffset, 3, 0xC40) + bTh(inputLen, 2) + [3]
            lst += sumCheck(lst)
            
        elif register_type == Register.Y:
            inputOffset = register_offset
            inputLen = register_len * 2
            lst = [2, 0x45, 0x30, 0x30, 0x38] + bTh(inputOffset, 3, 0xBC0) + bTh(inputLen, 2) + [3]
            lst += sumCheck(lst)
            
        elif register_type == Register.X:
            inputOffset = register_offset
            inputLen = register_len * 2
            lst = [2, 0x45, 0x30, 0x30, 0x38] + bTh(inputOffset, 3, 0xCA0) + bTh(inputLen, 2) + [3]
            lst += sumCheck(lst)
         
        else:
            raise NotImplemented

        req = bytes(lst)
        print(req)
        return req


fx3u = FX3U(
        request_map={
            range(0x0, 0x1F40): lambda address: (Register.D, address),
            range(0x1F40, 0x2140): lambda address: (Register.D8000, address-0x1F40),
            range(0x2140, 0xA140): lambda address: (Register.R, address-0x2140),
            range(0xA140, 0xA340): lambda address: (Register.TN, address-0xA140),
            range(0xA340, 0xA408): lambda address: (Register.CN, address-0xA340),
            range(0xA408, 0xA478): lambda address: (Register.CN200, address-0xA408),
            range(0xA478, 0xA658): lambda address: (Register.M_16b, address-0xA478),
            range(0xA658, 0xA678): lambda address: (Register.M8000_16b, address-0xA658),
            range(0xA678, 0xA778): lambda address: (Register.S, address-0xA678),
            range(0xA778, 0xA798): lambda address: (Register.TS, address-0xA778),

            range(0xA798, 0xA7A8): lambda address: (Register.CS, address-0xA798),
            range(0xA7A8, 0xA7B8): lambda address: (Register.Y, address-0xA7A8),
            range(0xA7B8, 0xA7C8): lambda address: (Register.X, address-0xA7B8)
        }
    )

