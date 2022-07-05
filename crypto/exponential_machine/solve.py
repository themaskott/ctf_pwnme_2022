import socket
import time
import struct
from Crypto.Util.number import *


def send_bytes(s, b):
    s.send(b.encode() + b'\n')
    rep = s.recv(1024)
    return rep


HOST = 'pwn.pwnme.fr'
PORT = 7003

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))


    rep = s.recv(2048).decode()

    a = rep.split('\n')[3]
    n = rep.split('\n')[5]
    c = rep.split('\n')[6]

    a = int(a.split(' = ')[1])
    n = int(n.split(' = ')[1])
    c = int(c.split(' = ')[1])


    print(f"{a = }")
    print(f"{n = }")
    print(f"{c = }")

    flag = 0
    i = 93
    exp = 10**i

    while(exp!=1):

        exp = 10**i
        if exp < 10:
            exp = 1

        rep = send_bytes(s, '/')

        rep = send_bytes(s, str(exp))

        result = rep.decode().split('\n\n')[0]
        result = int(result.split(' : ')[1])



        for j in range(100):
            tmp = flag * 100 + j
            if pow(a,tmp,n) == result:
                flag = tmp
                print(flag)
                i=i-2
                break

    flag = flag * 10


    # find the last digit
    for j in range(10):

        tmp = flag + j
        if pow(a,tmp,n) == result:
            flag = tmp
            break

    print(long_to_bytes(flag))
