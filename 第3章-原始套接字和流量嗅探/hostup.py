import socket
import os
import struct
import threading
import time
from ctypes import *
from netaddr import IPNetwork,IPAddress


# 监听的主机
host = "172.16.0.100"

# 扫描的子网
subnet = "172.16.0.0/20"
# 自定义字符串，将在ICMP中进行核对
magic_message = "PYTHONRULES!"
# IP头定义
class IP(Structure):
	_fields_ = [
		("ihl",c_ubyte,4),
		("version",c_ubyte,4),
		("tos",c_ubyte),
		("len",c_ushort),
		("id",c_ushort),
		("offset",c_ushort),
		("ttl",c_ubyte),
		("protocol_num",c_ubyte),
		("sum",c_ushort),
		("src",c_ulong),
		("dst",c_ulong)
	]

	def __new__(self,socket_buffer=None):
		return self.from_buffer_copy(socket_buffer)

	def __init__(self,socket_buffer=None):
		self.protocol_map = {1:"ICMP",6:"TCP",17:"UDP"}
		self.src_address = socket.inet_ntoa(struct.pack("<L",self.src))
		self.dst_address = socket.inet_ntoa(struct.pack("<L",self.dst))
		try:
			self.protocol = self.protocol_map[self.protocol_num]
		except:
			self.protocol = str(self.protocol_num)

class ICMP(Structure):
	_fields_ = [
		("type",c_ubyte),
		("code",c_ubyte),
		("checksum",c_ushort),
		("unused",c_ushort),
		("next_hop_mtu",c_ushort)
	]

	def __new__(self,socket_buffer):
		return self.from_buffer_copy(socket_buffer)

	def __init__(self,socket_buffer):
		pass

def udp_sender(subnet,magic_message):
	time.sleep(5)
	sender = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	for ip in IPNetwork(subnet):
		try:
			sender.sendto(magic_message,("%s" %ip,65212))
		except:
			pass

t = threading.Thread(target=udp_sender,args=(subnet,magic_message))
t.start()

# 创建原始套接字，绑定在公开接口上
if os.name == "nt":
	socket_protocol = socket.IPPROTO_IP
else:
	socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET,socket.SOCK_RAW,socket_protocol)
sniffer.bind((host,0))
# 设置在捕获的数据包中包含IP头
sniffer.setsockopt(socket.IPPROTO_IP,socket.IP_HDRINCL,1)
# 在windows平台上，需要设置IOCTL以启用混杂模式
if os.name == "nt":
	sniffer.ioctl(socket.SIO_RCVALL,socket.RCVALL_ON)

try:
	while True:
		# recvfrom从套接字接收数据。返回值是一对(string, address)，其中string是表示接收数据的字符串
		raw_buffer = sniffer.recvfrom(65535)[0]
		ip_header = IP(raw_buffer[0:20])
		# print("Protocol:%s %s -> %s" %(ip_header.protocol,ip_header.src_address,
				# ip_header.dst_address))
		if ip_header.protocol == "ICMP":
			offset = ip_header.ihl * 4
			buf = raw_buffer[offset:offset + sizeof(ICMP)]
			icmp_header = ICMP(buf)
			# print("ICMP -> Type:%d Code:%d" %(icmp_header.type,icmp_header.code))
			# 检查返回类型和代码是否为3
			if icmp_header.code == 3 and icmp_header.type == 3:
				# 确认响应的主机在我们的目标子网内
				if IPAddress(ip_header.src_address) in IPNetwork(subnet):
					# 确认ICMP包数据中包含我们发送的自定义字符串
					if raw_buffer[len(raw_buffer) - len(magic_message):] == magic_message:
						print("Host Up: %s" % ip_header.src_address)

#处理 CTRL-C
except KeyboardInterrupt:
	# 在windows平台上关闭混杂模式
	if os.name == "nt":
		sniffer.ioctl(socket.SIO_RCVALL,socket.RCVALL_OFF)
