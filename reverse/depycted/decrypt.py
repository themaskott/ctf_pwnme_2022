from Crypto.Util.number import *


cipher = 2195160159893668717327286059367551976012130689570892075754234400430874403925069147738764347075321
cipher = str(cipher)

for i in range(1,len(cipher)):
    first = cipher[:i]
    second = cipher[i:]

    first = first[::-1]
    second = second[::-1]

    first = int(first)^13
    second = int(second)^37

    d = long_to_bytes(first) + long_to_bytes(second)
    if d.startswith(b'PWN'):
        print(d)
