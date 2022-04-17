#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket

inputOfset = 3*2
inputLen = 7*2


def hTa(_hex):
    if _hex > 9:
        _hex += 7
    return _hex + 48


def bTh(n, length=2, add=0):
    n += add
    n1 = n % 16
    n = n // 16
    n2 = n % 16
    n = n // 16
    n3 = n % 16
    n = n // 16
    return [hTa(n), hTa(n3), hTa(n2), hTa(n1)][4 - length:]


def sumCheck(_list):
    out = 0
    for i in _list[1:]:
        out += i 
    return bTh(out)


def sumCheckBytes(_bytes):
    out = 0
    for i in _bytes[1:-2]:
        out += i 
    return bTh(out)


def responseDecode16bit(resp):
    sc = bytes(sumCheckBytes(resp))
    if resp[-2:] == sc:
        print('sumCheckOk')
    else:
        print('sumCheckFail')
        return
    bb = bytes.fromhex(resp[1:-3].decode('utf-8'))
    bbLen = len(bb)
    out = []
    i = 0
    while i < bbLen:
        out += [bb[i+1]*256+bb[i]]
        i += 2
    return out


def request(ip_adr, tcp_port, plc_type, register_type, register_ofset, register_len):
    if (register_len <= 0) or (register_len > 100):
        return

    if (plc_type == 'fx1s') and (register_type == 'D'):
        if (register_ofset < 0) or (register_ofset > 255):
            return

        inputOfset = register_ofset*2
        inputLen = register_len*2
        lst = [2, 0x30, 0x31] + bTh(inputOfset, 3) + bTh(inputLen, 2)+ [3]
        lst += sumCheck(lst)
        req = bytes(lst)
        print(req)
        
    elif (plc_type == 'fx3u') and (register_type == 'D'):
        if (register_ofset < 0) or (register_ofset > 7999):
            return
        inputOfset = register_ofset*2
        inputLen = register_len*2
        lst = [2, 0x45, 0x30, 0x30] + bTh(inputOfset, 4, 0x4000) + bTh(inputLen, 2)+ [3]
        lst += sumCheck(lst)
        req = bytes(lst)
        print(req)
        
    elif (plc_type == 'fx3u') and (register_type == 'M_16b'):
        if (register_ofset < 0) or (register_ofset > 479):
            return
        inputOfset = register_ofset
        inputLen = register_len*2
        lst = [2, 0x45, 0x30, 0x30, 0x38] + bTh(inputOfset, 3, 0x800) + bTh(inputLen, 2)+ [3]
        lst += sumCheck(lst)
        req = bytes(lst)
        print(req)
    else:
        return

    sock = socket.socket()
    sock.settimeout(2)
    sock.connect((ip_adr, tcp_port))
    sock.sendall(req)

    data = b''
    try:
        while True:
            data += sock.recv(256)
            if data[-3] == 3:
                break
    except Exception as e:
        sock.close()
        raise

    sock.close()

    print(data)
    
    return responseDecode16bit(data)


#print (request('localhost', 5556, 'fx3u', 'D', 250, 10))
#print (request('localhost', 5556, 'fx3u', 'M_16b', 0, 10))


#print (request('192.168.0.2', 8020, 'fx3u', 'D', 7900, 10))

print(request('localhost', 5556, 'fx1s', 'D', 250, 30))


