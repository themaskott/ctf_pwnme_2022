import socket
from time import sleep
import struct

HOST = "prog.pwnme.fr"
PORT = 7000

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
				return (i,j)
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


		steps = abs(ze-zs)+abs(xe-xs)+abs(ye-ys)

		print("dist :", steps)

		steps=str(steps)
		steps=steps.encode()


		s.send(steps + b'\n')

		sleep(0.1)
