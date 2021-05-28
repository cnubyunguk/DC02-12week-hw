import socket
import os
import sys
import hashlib

try:
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(("localhost", 8000))
except socket.error:
	print("failed to create socket")
	sys.exit()

def check_md5(path):
	f = open(path, 'rb')
	data = f.read()
	md5_hash = hashlib.md5(data).hexdigest()
	return md5_hash

def sender_send(file_name):
	#
	# Implement in the order mentioned in the silde and video.
	#
    s.sendto('valid list command'.encode('utf-8'), client_addr)
    
    if(not os.path.isfile(file_name)):
        return
        
    s.sendto('file exists!'.encode('utf-8'), client_addr)
    
    file_size = os.stat(file_name).st_size
    count = file_size % 4096 == 0 and int(file_size / 4096) or int(file_size / 4096) + 1
    s.sendto(str(count).encode('utf-8'), client_addr)
    
    f = open(file_name, "rb")
    while(count != 0):
        data = f.read(4096)
        s.sendto(data, client_addr)
        count -= 1

	# Do not modify the code (below)
    md5_hash = check_md5(file_name)
    s.sendto(md5_hash.encode('utf-8'), client_addr)

if __name__ == "__main__":
	try:
		data, client_addr = s.recvfrom(4096)
	except ConnectionResetError:
		print("error. port number not matching.")
		sys.exit()

	text = data.decode('utf8')
	handler = text.split()

	if handler[0] == 'receive':
		sender_send(handler[1])
