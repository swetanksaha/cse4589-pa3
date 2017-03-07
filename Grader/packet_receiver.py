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
import socket
import signal

class Alarm(Exception):
    pass

def alarm_handler(signum, frame):
    raise Alarm

if __name__ == '__main__':
    UDP_PORT = int(sys.argv[1])
    TIMEOUT = int(sys.argv[2])
    DIR = sys.argv[3]

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sock.bind(('0.0.0.0', UDP_PORT))

    os.system('cd %s && rm -f num_updates' % (DIR))
    os.system('cd %s && rm -f update-packet-*' % (DIR))

    num_updates = 0
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(TIMEOUT)
    try:
        while True:
            data, addr = sock.recvfrom(1024)

            pkt_fname = os.path.join(DIR, 'update-packet-'+str(num_updates))
            pkt_file = open(pkt_fname, 'wb')
            pkt_file.write(data)
            pkt_file.close()

            num_updates += 1

            num_updates_fname = os.path.join(DIR, 'num_updates')
            num_updates_file = open(num_updates_fname, 'w')
            num_updates_file.write(str(num_updates))
            num_updates_file.close()
    except Alarm:
        pass
