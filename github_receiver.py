import socket
import os
import sys
import hashlib

def check_md5_hash(path):
    f = open(path, 'rb')
    data = f.read()
    md5_hash = hashlib.md5(data).hexdigest()
    return md5_hash

file_name = input()

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setblocking(0)
    s.settimeout(15)
except socket.error:
    print("failed to create socket")
    sys.exit()

host = "localhost"
port = 8000

#
# send to sender
# "receive " + file_name
#
req_msg = "receive " + file_name
s.sendto(req_msg.encode('utf-8'), (host, port))

#
# receiver exist msg
#
valid_msg, sender_addr = s.recvfrom(4096)
exist_msg, _ = s.recvfrom(4096)


#
# if receiver exist msg:
#
if (exist_msg.decode('utf-8') == 'file exists!'):
    f = open('Received_script.txt', 'wb')
    
    size_msg, _ = s.recvfrom(4096)
    
    count = int(size_msg.decode('utf-8'))

#
# file receive ==> open("Received_script.txt", "wb") # Fixed file name
# Receives the standard count for dividing a file from the server
# ==> while recv_count != 0:
# Continuously receive and write file contents
#q
    while(count != 0):
        data, _ = s.recvfrom(4096)
        f.write(data)
        count -= 1

#
# file_name.close()
#
    f.close()

# Do not modify the code (below)
rec_md5_hash, addr = s.recvfrom(4096)
		
if rec_md5_hash.decode('utf8') == check_md5_hash('Received_script.txt'): # 
    print("True")
else:
    print("False")
