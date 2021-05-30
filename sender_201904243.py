import socket
import os
import sys
import time
import struct

if (len(sys.argv) != 2):
    print("please pass port number")
    sys.exit()
    
print('It was successfully entered. Let\'s move on')
print(int(sys.argv[1]))

ip_addr = "127.0.0.1"
port = int(sys.argv[1])
buf_size = 984

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((ip_addr, port))
except socket.error:
	print("failed to create socket")
	sys.exit()
    
print('successfully created socket')

def ip2int(addr):
    return [int(x) for x in addr.split('.')]
    
def checksum(data):
    ret = 0
    data_len = len(data)
    
    # If the number of data is odd, add one more byte
    if (len(data) % 2):
        data_len += 1
        data += struct.pack('!B', 0)
    
    for i in range(0, len(data), 2):
        ret += int.from_bytes(data[i:i+2], "big")
        
    ret = (ret >> 16) + (ret & 0xFFFF)
    return ~ret & 0xFFFF

def sender_send(file_name):
    s.sendto('valid list command'.encode('utf-8'), client_addr)
    
    if(not os.path.isfile(file_name)):
        return
        
    s.sendto('file exists!'.encode('utf-8'), client_addr)
    
    file_size = os.stat(file_name).st_size
    print("file size: {0}bytes".format(file_size))
    
    count = file_size % buf_size == 0 and int(file_size / buf_size) or int(file_size / buf_size) + 1
    s.sendto(str(count).encode('utf-8'), client_addr)
    
    # calc checksum
    src_ip = ip_addr
    src_ip = struct.pack('!4B', *ip2int(src_ip))
 
    dst_ip = client_addr[0]
    dst_ip = struct.pack('!4B', *ip2int(dst_ip))
    
    zero = 0
    protocol = socket.IPPROTO_UDP
    src_port = port
    dst_port = client_addr[1]
    
    inital_cnt = count
    f = open(file_name, "rb")
    while(count != 0):
        data = f.read(buf_size)
        udp_len = 8 + len(data)
        pseudo_header = src_ip + dst_ip + struct.pack('!BBH', zero, protocol, udp_len)
        udp_header = struct.pack('!4H', src_port, dst_port, udp_len, 0)
        chksum = checksum(pseudo_header + udp_header + data)
        chksum_header = struct.pack('!4H', src_port, dst_port, udp_len, chksum)
        s.sendto(pseudo_header + chksum_header + data, client_addr)
        time.sleep(0.005) # give time to save
        
        # logging
        count -= 1
        print('packet number {0}'.format(inital_cnt - count))
        print('data sending now')
        print("### final checksum ###")
        print(hex(chksum))
        
    print("complete sending data task")

if __name__ == "__main__":
    while(True):
        print('waiting client command...')
        try:
            data, client_addr = s.recvfrom(4096)
        except ConnectionResetError:
            print("error. port number not matching.")
            sys.exit()

        text = data.decode('utf8')
        handler = text.split()

        if handler[0] == 'receive':
            sender_send(handler[1])
        elif handler[0] == 'exit':
            s.close()
            sys.exit()
