#!/usr/bin/python
#
# This file is part of CSE 489/589 PA3: Controller.
#
# CSE 489/589 PA3: Controller is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# CSE 489/589 PA3: Controller is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with CSE 489/589 PA3: Controller. If not, see <http://www.gnu.org/licenses/>.
#

__author__ = "Swetank Kumar Saha (swetankk@buffalo.edu)"
__copyright__ = "Copyright (C) 2016 Swetank Kumar Saha"
__license__ = "GNU GPL"
__version__ = "2.3"

import argparse
import sys
import struct

parser = argparse.ArgumentParser(description='CSE 489/589 PA3: Controller v'+__version__)

requiredArgs = parser.add_argument_group('required named arguments')
requiredArgs.add_argument('-t', '--topology', dest='topology', type=argparse.FileType('r'), nargs=1, help='topology file', required=True)

parser.add_argument('-o', '--response-dump-file', dest='file', type=str, nargs=1, help='control-response packet dump [default: response.pkt]', default=['response.pkt'])
parser.add_argument('-a', '--author', metavar='router-ID', dest='author', type=int, nargs=1, help='AUTHOR [Control Code:0x00]')
parser.add_argument('-i', '--init', metavar='routing-update-interval', dest='init', type=int, nargs=1, help='INIT [Control Code:0x01]')
parser.add_argument('-r', '--routing-table', metavar='router-ID', dest='rtable', type=int, nargs=1, help='ROUTING-TABLE [Control Code:0x02]')
parser.add_argument('-u', '--update', metavar=('router-ID1', 'router-ID2', 'new-cost'), dest='update', type=int, nargs=3, help='UPDATE [Control Code:0x03]')
parser.add_argument('-c', '--crash', metavar='router-ID', dest='crash', type=int, nargs=1, help='CRASH [Control Code:0x04]')
parser.add_argument('-f', '--sendfile', metavar=('src-router-ID' ,'dest-router-ID', 'init-ttl', 'transfer-ID', 'init-seq-num', 'filename'), dest='sendfile', nargs=6, help='SENDFILE [Control Code:0x05]')
parser.add_argument('-s', '--sendfile-stats', metavar=('router-ID', 'transfer-ID'), dest='stats', type=int, nargs=2, help='SENDFILE-STATS [Control Code:0x06]')
parser.add_argument('-l', '--last-data-packet', metavar='router-ID', dest='last', type=int, nargs=1, help='LAST-DATA-PACKET [Control Code:0x07]')
parser.add_argument('-p', '--penultimate-data-packet', metavar='router-ID', dest='penultimate', type=int, nargs=1, help='PENULTIMATE-DATA-PACKET [Control Code:0x08]')


class Router(object):
	"""Router"""
	# TO DO: Add checks for fields
	def __init__(self, id, ip_addr, control_port, router_port, data_port):
		super(Router, self).__init__()
		self.id = id
		self.ip_addr = ip_addr
		self.control_port = control_port
		self.router_port = router_port
		self.data_port = data_port


def print_regular(text):
	print '\033[33m'+text+'\033[0m',
	sys.stdout.flush()

def print_success(text):
	print '\033[92m'+text+'\033[0m',
	sys.stdout.flush()

def print_error(text):
	print '\033[91m'+text+'\033[0m',
	sys.stdout.flush()

def error_exit(e):
	print_error('Error!')
	print
	print_error(str(e))
	sys.exit()

def type_int(value):
	try:
		return int(value)
	except Exception, e: error_exit(e)

def type_str(value):
	try:
		return str(value)
	except Exception, e: error_exit(e)


num_routers = 0
routers = []
network = {}

dump_filename = ''

# Get the router with a given id
def get_router(r_id):
	return next((r for r in routers if r.id == r_id), None)

# Get init. link cost between two routers
def get_cost(router_a, router_b):
	r_a, r_b = router_a.id, router_b.id
	if r_a == r_b: cost = 0
	else:
		link = r_a, r_b
		key = tuple(sorted(link))
		if key in network: cost = network[key]
		else: cost = 65535

	return cost

# Returns the control in network-byte order
def control_packet(dest_ip_addr, cntrl_code, resp_time, payload):
	header = struct.pack('!4sBBH', dest_ip_addr, cntrl_code, resp_time, len(payload))
	return header+payload

# Parse control-response header
def parse_response_header(header):
	controller_ip = socket.inet_ntoa(header[0])
	cntrl_code, resp_code, payload_len = header[1:]
	print
	print ''.center(36, '-')
	print '|'+controller_ip.center(34, ' ')+'|'
	print ''.center(36, '-')
	print '|'+str(cntrl_code).center(8, ' ')+'|'+str(resp_code).center(8, ' ')+'|'+str(payload_len).center(16, ' ')+'|'
	print ''.center(36, '-')
	print

# Receive given number of bytes
def recvall(sock, num_bytes):
	response = ''
	while len(response) != num_bytes:
		data = sock.recv(num_bytes-len(response))
		if not data:
			error_exit('Connection closed unexpectedly by the router')

		response += data

	return response

# Receive packet and decode header
def recv_and_decode(sock):
	data = recvall(sock, 8)
	print_success('Done!')

	print
	print_regular('Parsing header ...\n')
	header = struct.unpack('!4sBBH', data)
	parse_response_header(header)

	payload_len = header[3]
	print_regular('Waiting for control-response payload ('+str(payload_len)+' bytes) from router ...')
	data += recvall(sock, payload_len)
	print_success('Done!')

	return data

# Send control packet to router and wait for response
def send_and_recv(cntrl_packet, router, resp_time):
	IP = socket.inet_ntoa(router.ip_addr)
	PORT = router.control_port

	print_regular('Sending control message to: '+'\033[0m'+IP+':'+str(PORT)+'\033[0m'+' ...')

	# Connect to router
	sock = socket.create_connection((IP, PORT), timeout=resp_time)
	# Send Packet
	sock.sendall(cntrl_packet)
	print_success('Done!')
	# Wait for response
	print
	print_regular('Waiting for control-response header from router ...')
	response = recv_and_decode(sock)
	# Close the connection
	sock.close()

	return response

# Prepare control packet and do send_and_recv
def send_to_router(router, cntrl_code, resp_time, payload):
	cntrl_packet = control_packet(router.ip_addr, cntrl_code, resp_time, payload)
	try:
		resp = send_and_recv(cntrl_packet, router, resp_time)
		response_dump(resp)
	except Exception, e:
		error_exit(e)

# Write control-response to dump-file
def response_dump(response):
	try:
		dump_file = open(dump_filename, 'wb')
		print
		print_regular('Writing response-packet to file: '+'\033[0m'+dump_filename+'\033[0m'+' ...')
		dump_file.write(response)
		print_success('Done!')
		print
	except Exception, e:
		error_exit(e)
	finally:
		dump_file.close()

if __name__ == "__main__":

	args = parser.parse_args()

	import socket
	import pprint

	topology_file = args.topology[0]
	print_regular('Reading Topology file: '+'\033[0m'+topology_file.name+'\033[0m'+' ...')

	try:
		topology = topology_file.readlines()
		topology = [line.rstrip() for line in topology] #Clean out the \n's

		# Number of routers
		num_routers = int(topology.pop(0))

		# Router Info.
		for index in range(num_routers):
			r_info = topology.pop(0).split(' ')
			router = Router(int(r_info[0]),
							socket.inet_aton(r_info[1]),
							int(r_info[2]),
							int(r_info[3]),
							int(r_info[4])
							)
			routers.append(router)

		# Links
		for link in topology:
			l_info = link.split(' ')
			key = int(l_info[0]), int(l_info[1])
			network[tuple(sorted(key))] = int(l_info[2])

		print_success('Done!')

	except Exception, e:
		error_exit(e)
	finally:
		topology_file.close()

	dump_filename = args.file[0]

	# AUTHOR
	if args.author:
		print
		print '\nAUTHOR:'

		cntrl_code = 0
		resp_time = 1

		r_id = args.author[0]
		router = get_router(r_id)

		send_to_router(router, cntrl_code, resp_time, '')

	# INIT
	if args.init:
		print
		print '\nINIT:'

		cntrl_code = 1
		resp_time = 3

		for dst_router in routers:
			payload = struct.pack('!HH', num_routers, args.init[0])
			for router in routers:
				payload += struct.pack('!HHHH4s', router.id,
										router.router_port, router.data_port,
										get_cost(dst_router, router), router.ip_addr
										)

			dump_filename = args.file[0]+'-'+str(dst_router.id)
			send_to_router(dst_router, cntrl_code, resp_time, payload)
			print

	# ROUTING-TABLE
	if args.rtable:
		print
		print '\nROUTING-TABLE:'

		cntrl_code = 2
		resp_time = 3

		r_id = args.rtable[0]
		router = get_router(r_id)

		send_to_router(router, cntrl_code, resp_time, '')

	# UPDATE
	if args.update:
		print
		print '\nUPDATE:'

		cntrl_code = 3
		resp_time = 1

		r_id1 = args.update[0]
		r_id2 = args.update[1]
		cost = args.update[2]

		router_1 = get_router(r_id1)
		router_2 = get_router(r_id2)

		# Send to router_1
		payload = struct.pack('!HH', router_2.id, cost)
		send_to_router(router_1, cntrl_code, resp_time, payload)
		# Send to router_2
		payload = struct.pack('!HH', router_1.id, cost)
		send_to_router(router_2, cntrl_code, resp_time, payload)

	# CRASH
	if args.crash:
		print
		print '\nCRASH:'

		cntrl_code = 4
		resp_time = 1

		r_id = args.crash[0]
		router = get_router(r_id)

		send_to_router(router, cntrl_code, resp_time, '')

	# SENDFILE
	if args.sendfile:
		print
		print '\nSENDFILE:'

		cntrl_code = 5
		resp_time = 6

		for index in range(0,5):
			args.sendfile[index] = type_int(args.sendfile[index])
		filename = type_str(args.sendfile[index+1])

		src_r_id = args.sendfile[0]
		src_router = get_router(src_r_id)
		dst_r_id = args.sendfile[1]
		dst_router = get_router(dst_r_id)

		payload = struct.pack('!4sBBH'+str(len(filename))+'s', dst_router.ip_addr, args.sendfile[2], args.sendfile[3], args.sendfile[4], args.sendfile[5])
		send_to_router(src_router, cntrl_code, resp_time, payload)

	# SENDFILE-STATS
	if args.stats:
		print
		print '\nSENDFILE-STATS:'

		cntrl_code = 6
		resp_time = 4

		r_id = args.stats[0]
		router = get_router(r_id)

		payload = struct.pack('!B', args.stats[1])
		send_to_router(router, cntrl_code, resp_time, payload)

	# LAST-DATA-PACKET
	if args.last:
		print
		print '\nLAST-DATA-PACKET:'

		cntrl_code = 7
		resp_time = 3

		r_id = args.last[0]
		router = get_router(r_id)

		send_to_router(router, cntrl_code, resp_time, '')

	# PENULTIMATE-DATA-PACKET
	if args.penultimate:
		print
		print '\nPENULTIMATE-DATA-PACKET:'

		cntrl_code = 8
		resp_time = 3

		r_id = args.penultimate[0]
		router = get_router(r_id)

		send_to_router(router, cntrl_code, resp_time, '')
