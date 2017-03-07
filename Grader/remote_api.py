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

import subprocess
import time
import os

ASSIGNMENT_PATH = ''
SSH_PROC_LIST = []

def init_remote_assignment(cfg, cntrl_port):
    global SSH_PROC_LIST

    GRADING_SERVERS_HOSTNAME = [server[1] for server in cfg.items('GradingServerList')]
    for server in GRADING_SERVERS_HOSTNAME:
        remote_cmd = 'cd %s;./%s %s;/bin/tcsh' % (ASSIGNMENT_PATH, cfg.get('Grader', 'binary'), cntrl_port)
        ssh_cmd = ['ssh', '-i', cfg.get('SSH', 'id'), cfg.get('SSH', 'user')+'@'+server, remote_cmd]
        print ' '.join(ssh_cmd)

        SSH_PROC_LIST.append((subprocess.Popen(ssh_cmd, stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT), server, cntrl_port))

    # Wait for all servers to init.
    time.sleep(3)

def cleanup(cfg):
    global SSH_PROC_LIST

    while len(SSH_PROC_LIST) != 0:
        proc, server, port = SSH_PROC_LIST.pop()
        #remote
        kill_process(cfg, server, port)
        #local
        proc.kill()

def kill_process(cfg, server, port):
    kill_cmd = "kill -9 `netstat -tupln | grep :%d | awk '{print $NF}' | cut -d/ -f1`" % (port)
    ssh_cmd = ['ssh', '-i', cfg.get('SSH', 'id'), cfg.get('SSH', 'user')+'@'+server, kill_cmd]
    print ' '.join(ssh_cmd)

    subprocess.call(ssh_cmd, stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)

def copy_file_from(cfg, server, remote_file, local_file):
    rfile = os.path.join(ASSIGNMENT_PATH, remote_file)
    scp_cmd = ['scp', '-i', cfg.get('SSH', 'id'), cfg.get('SSH', 'user')+'@'+server+':'+rfile, local_file]
    print ' '.join(scp_cmd)

    subprocess.call(scp_cmd, stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)

def copy_file_to(cfg, server, local_file, remote_file):
    rfile = os.path.join(ASSIGNMENT_PATH, remote_file)
    scp_cmd = ['scp', '-i', cfg.get('SSH', 'id'), local_file, cfg.get('SSH', 'user')+'@'+server+':'+rfile]
    print ' '.join(scp_cmd)

    subprocess.call(scp_cmd, stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)

def delete_file_from(cfg, server, remote_file):
    rfile = os.path.join(ASSIGNMENT_PATH, remote_file)
    del_cmd = 'rm -f %s' % (rfile)
    ssh_cmd = ['ssh', '-i', cfg.get('SSH', 'id'), cfg.get('SSH', 'user')+'@'+server, del_cmd]
    print ' '.join(ssh_cmd)

    subprocess.call(ssh_cmd, stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)

def run_cmd(cfg, server, remote_cmd):
    r_cmd = 'cd %s; %s' % (ASSIGNMENT_PATH, remote_cmd)
    ssh_cmd = ['ssh', '-i', cfg.get('SSH', 'id'), cfg.get('SSH', 'user')+'@'+server, r_cmd]
    print ' '.join(ssh_cmd)

    subprocess.Popen(ssh_cmd)

def run_script(cfg, server, args, script):
    remote_cmd = 'python -u - %s < %s' % (args, script)
    ssh_cmd = ['ssh', '-i', cfg.get('SSH', 'id'), cfg.get('SSH', 'user')+'@'+server, remote_cmd]
    print ' '.join(ssh_cmd)

    subprocess.Popen(' '.join(ssh_cmd), shell=True)
