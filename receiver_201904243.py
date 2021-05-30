import socket
import os
import sys
import struct

def check_md5_hash(path):
    f = open(path, 'rb')
    data = f.read()
    md5_hash = hashlib.md5(data).hexdigest()
    return md5_hash

if (len(sys.argv) != 3):
    sys.exit()
    
host = sys.argv[1]
port = int(sys.argv[2])

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setblocking(0)
    s.settimeout(15)
except socket.error:
    print("failed to create socket")
    sys.exit()
    
def checksum(data):
    ret = 0
    data_len = len(data)
    
    # If the number of data is odd, add one more byte
    if (len(data) % 2):
        data_len += 1
        data += struct.pack('!B', 0)
    
    for i in range(0, data_len, 2):
        ret += int.from_bytes(data[i:i+2], "big")
        if(i >= 2):
            print("checksum hex addition: {0} + {1}".format('0x' + data[i-2:i].hex(), '0x' + data[i:i+2].hex()))
        
    ret = (ret >> 16) + (ret & 0xFFFF)
    
    print('checksum value before flip: {0}'.format(ret & 0xFFFF))
    print('checksum value after flip: {0}'.format(~ret & 0xFFFF))
    
    return ~ret & 0xFFFF

    
while(True):
    req_msg = input("enter command: ");
    s.sendto(req_msg.encode('utf-8'), (host, port))
    
    cmd = req_msg.split()[0]
    if(cmd == 'exit'):
        sys.exit()

    # is command valid?
    valid_msg, sender_addr = s.recvfrom(4096)
    if (valid_msg.decode('utf-8') != 'valid list command'):
        continue
    
    # is file exist?
    exist_msg, _ = s.recvfrom(4096)
    if (exist_msg.decode('utf-8') != 'file exists!'):
        continue
    
    file_name = "Received_" + req_msg.split()[1]
    f = open(file_name, 'wb')
    
    # receive file transfer count
    size_msg, _ = s.recvfrom(4096)
    
    my_chksum = checksum(size_msg[:18] + struct.pack('!H', 0) + size_msg[20:])
    received_chksum = int.from_bytes(size_msg[18:20], 'big')
    if (my_chksum != received_chksum):
        print('[Checksum Error] my checksum: {0} received checksum: {1}'.format(my_chksum, received_chksum))
        sys.exit()
    
    count = int(size_msg[20:].decode('utf-8'))
    print("number of receive: {0}".format(count))
    
    # receive file
    init_cnt = count
    while(count != 0):
        data, _ = s.recvfrom(4096)
        my_chksum = checksum(data[:18] + struct.pack('!H', 0) + data[20:])
        received_chksum = int.from_bytes(data[18:20], 'big')
        
        if (my_chksum == received_chksum):
            f.write(data[20:])
            print("received packet number {0}".format(init_cnt - (count - 1)))
            print('Received checksum: {0}'.format(hex(received_chksum)))
            print('New calculated checksum: {0}'.format(hex(my_chksum)))
        else:
            print('[Checksum Error] my checksum: {0} received checksum: {1}'.format(my_chksum, received_chksum))
            sys.exit()
        
        print(my_chksum == received_chksum)
        count -= 1
        
    f.close()
    print("file download complete")
