import socket
from time import sleep
import struct

HOST = "prog.pwnme.fr"
PORT = 7001

def recv_until(s,p):
	rep =b''
	while p not in rep:
		rep += s.recv(1024)
		# stop condition
		if b'PWNME' in rep:
			return rep
	return rep

def dist(c,f):
	lines = f.split(b'\n')
	lines = lines[1:-1]
	size = len(lines[0])

	for i in range(size):
		for j in range(size):
			if chr(lines[i][j]) == c:
				return (j,i)
	return (0,0)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	
	s.connect((HOST, PORT))


	while(1):
		chall = recv_until(s,b'>> ')
		print(chall.decode())

		
		floors = chall.split(b'-')

		for i,f in enumerate(floors):
			if b'E' in f:
				ze=i
				(xe,ye)=dist('E',f)
			if b'S' in f:
				zs=i
				(xs,ys)=dist('S',f)


		steps = ""

		if zs < ze:
			steps += "z-;" * (ze-zs)
		if zs > ze:
			steps += "z+;" * (zs-ze)

		if ys < ye:
			steps += "y+;" * (ye-ys)
		if ys > ye:
			steps += "y-;" * (ys-ye)

		if xs < xe:
			steps += "x-;" * (xe-xs)
		if xs > xe:
			steps += "x+;" * (xs-xe)



		steps=steps[:-1]
		print(steps)

		steps=steps.encode()
		s.send(steps + b'\n')

		sleep(0.1)
