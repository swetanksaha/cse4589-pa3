# This file is part of CSE 489/589 Grader.
#
# CSE 489/589 Grader is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# CSE 489/589 Grader is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with CSE 489/589 Grader. If not, see <http://www.gnu.org/licenses/>.
#

import sys
import os
import ConfigParser
import socket
import random
import subprocess

GRADING_SERVERS_HOSTNAME = []
GRADING_SERVERS_IP = []
CFG = None

def readConfiguration(config_file):
    global GRADING_SERVERS_HOSTNAME, GRADING_SERVERS_IP, CFG

    config = ConfigParser.SafeConfigParser()
    config.read(config_file.name)

    print_regular('Reading configuration file: '+'\033[0m'+config_file.name+'\033[0m'+' ...')

    GRADING_SERVERS_HOSTNAME = [server[1] for server in config.items('GradingServerList')]
    GRADING_SERVERS_IP = [resolveIP(server[1]) for server in config.items('GradingServerList')]

    config_file.close()
    CFG = config
    return config

class Router(object):
    """Router"""
    # TO DO: Add checks for fields
    def __init__(self, id, ip_addr, cntrl_port):
        super(Router, self).__init__()
        self.id = id
        self.ip_addr = ip_addr
        self.control_port = cntrl_port
        self.router_port = random_port()
        self.data_port = random_port()

def gen_topology(link_costs, cntrl_port, scramble=False):
    ROUTERS = []
    ROUTER_ID_MAPPING = {}

    for server_ip in GRADING_SERVERS_IP:
        if scramble: r_id = random.randint(10, 1000)
        else: r_id = GRADING_SERVERS_IP.index(server_ip)+1
        router = Router(r_id, server_ip, cntrl_port)
        ROUTERS.append(router)
        ROUTER_ID_MAPPING[str(GRADING_SERVERS_IP.index(server_ip)+1)] = str(r_id)
        ROUTER_ID_MAPPING[str(r_id)] = str(GRADING_SERVERS_IP.index(server_ip)+1)

    topology = str(len(ROUTERS))+'\n'
    for router in ROUTERS:
        topology += str(router.id)+' '+str(router.ip_addr)+' '+str(router.control_port)+' '+str(router.router_port)+' '+str(router.data_port)+'\n'

    for link in link_costs:
        topology += ROUTER_ID_MAPPING[link[0]]+' '+ROUTER_ID_MAPPING[link[1]]+' '+str(link[2])+'\n'

    topology.rstrip('\n')
    print topology

    top_file = open('topology', 'w')
    top_file.write(topology)
    top_file.close()

    return ROUTERS, ROUTER_ID_MAPPING

#Uses original IDs: 1,2,3,4,5
def get_link_cost(src, dst, link_costs):
    if src == dst: return 0

    for link in link_costs:
        if (src == link[0] and dst == link[1]) or (src == link[1] and dst == link[0]):
            return link[2]

    return 65535

#Uses mapped IDs
def get_router_ip(router_id, ROUTERS):
    for router in ROUTERS:
        if router.id == router_id: return router.ip_addr

    return None

def parse_response_header(header):
    controller_ip = socket.inet_ntoa(header[0])
    cntrl_code, resp_code, payload_len = header[1:]

    return controller_ip, cntrl_code, resp_code, payload_len

def run_cmd(cmd):
    subprocess.call(cmd)

def delete_file(filepath):
    subprocess.call(['rm', '-f', filepath], stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)

def cleanup():
    delete_file('topology')
    delete_file('response.pkt')

def print_generic(print_str, newline):
    if newline: print print_str
    else: print print_str,
    sys.stdout.flush()

def print_regular(text, newline=True):
    print_str = '\033[33m%s\033[0m' % (text)
    print_generic(print_str, newline)

def print_error(text, newline=True):
    print_str = '\033[91m%s\033[0m' % (text)
    print_generic(print_str, newline)

def get_grading_server_paths(config, student_type):
    grading_servers = [server[1] for server in config.items('GradingServerList')]
    grading_dir = os.path.join(config.get('GradingServer', 'dir-local'), student_type)
    return [server+':'+grading_dir for server in grading_servers]

def resolveIP(fqdn):
    return socket.gethostbyname(fqdn)

def random_port():
    return random.randint(1000, 60000)
