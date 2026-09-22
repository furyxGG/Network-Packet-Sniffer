import socket
import struct

s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3)) # we want to take packet from network adapter with headers

class Packet:
	def __init__(self):
		self.protocol = None
		
	def	get_ethernet_frame(self, data):
		# we should know, ethernet frame is just 14 byte. its dest mac(6 byte), source mac(6 byte), type(2 byte)
		ether_frame = data[:14]
		unpacked_eth = struct.unpack('!6s6sH', ether_frame) # we have to use (!) because our systems are Little-Endian but Network systems are Big-Endian. We will reverse our integer data with (!).
		self.dst_mac = unpacked_eth[0]
		self.src_mac = unpacked_eth[1]
		self.type = unpacked_eth[2]

	def get_ipv4_header(self, data): # min 20, max 60 byte
		if self.type == 0x0800: # only ipv4
			ipv4_frame = data[14:34]
			all_bytes = struct.unpack('!BBHHHBBHII', ipv4_frame) # u can check readme.md
			self.version = all_bytes[0] >> 4
			self.ihl = all_bytes[0] & 0x0F
			self.dscp = all_bytes[1] >> 2
			self.ecn = all_bytes[1] & 0x03
			self.total_len = all_bytes[2]
			self.identification = all_bytes[3]
			self.flags = all_bytes[4] >> 13
			self.fragment_offset = all_bytes[4] & 0x1FFF
			self.ttl = all_bytes[5]
			self.protocol = all_bytes[6]
			self.header_checksum = all_bytes[7]
			source_ip = all_bytes[8]
			byte1 = (source_ip >> 24) & 0xFF
			byte2 = (source_ip >> 16) & 0xFF
			byte3 = (source_ip >> 8) & 0xFF
			byte4 = source_ip & 0xFF
			self.source_ip_address = f"{byte1}.{byte2}.{byte3}.{byte4}"

			dst_ip = all_bytes[9]
			byte1 = (dst_ip >> 24) & 0xFF
			byte2 = (dst_ip >> 16) & 0xFF
			byte3 = (dst_ip >> 8) & 0xFF
			byte4 = dst_ip & 0xFF
			self.dst_ip_address = f"{byte1}.{byte2}.{byte3}.{byte4}"
		else:
			pass

	def	get_tcpudp_header(self, data):
		if self.protocol == 6:
			start = 14 + (self.ihl * 4)
			tcp_header = data[start:start + 20]
			all_bytes = struct.unpack("!HHIIHHHH", tcp_header)
			self.src_port = all_bytes[0]
			self.dst_port = all_bytes[1]
			self.seq_nbr = all_bytes[2]
			self.ack_nbr = all_bytes[3]
			self.header_len = all_bytes[4] >> 12
			self.reserved_bits = (all_bytes[4] >> 6) & 0x003F
			self.urg = (all_bytes[4] >> 5) & 0x0001
			self.ack = (all_bytes[4] >> 4) & 0x0001
			self.psh = (all_bytes[4] >> 3) & 0x0001
			self.rst = (all_bytes[4] >> 2) & 0x0001
			self.syn = (all_bytes[4] >> 1) & 0x0001
			self.fin = all_bytes[4] & 0x0001
			self.w_size = all_bytes[5]
			self.tcp_checksum = all_bytes[6]
			self.urg_pointer = all_bytes[7]
		elif self.protocol == 17:
			start = 14 + (self.ihl * 4)
			udp_header = data[start:start + 8]
			all_bytes = struct.unpack("!HHHH", udp_header)
			self.src_port = all_bytes[0]
			self.dst_port = all_bytes[1]
			self.udp_len = all_bytes[2]
			self.udp_checksum = all_bytes[3]
		else:
			pass


while True:
	packet = Packet()
	data, addr = s.recvfrom(65535) # our max packet size
	packet.get_ethernet_frame(data)
	packet.get_ipv4_header(data)
	packet.get_tcpudp_header(data)
	del packet