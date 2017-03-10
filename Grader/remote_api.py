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

import utils

ASSIGNMENT_PATH = ''
SSH_PROC_LIST = []

def init_remote_assignment(cfg, cntrl_port):
    global SSH_PROC_LIST

    utils.print_regular('Starting assignment servers ...')
    GRADING_SERVERS_HOSTNAME = [server[1] for server in cfg.items('GradingServerList')]
    for server in GRADING_SERVERS_HOSTNAME:
        remote_cmd = './%s %s;/bin/tcsh' % (cfg.get('Grader', 'binary'), cntrl_port)
        SSH_PROC_LIST.append((run_cmd(cfg, server, remote_cmd, async=True, verbose=False), server, cntrl_port))

    # Wait for all servers to init.
    time.sleep(3)
    utils.print_success('OK')

def cleanup(cfg):
    global SSH_PROC_LIST

    while len(SSH_PROC_LIST) != 0:
        proc, server, port = SSH_PROC_LIST.pop()
        #remote
        kill_process(cfg, server, port)
        #local
        proc.kill()

def kill_process(cfg, server, port, verbose=False):
    kill_cmd = "kill -9 `netstat -tupln | grep :%d | awk '{print $NF}' | cut -d/ -f1`" % (port)
    ssh_cmd = ['ssh', '-i', cfg.get('SSH', 'id'), cfg.get('SSH', 'user')+'@'+server, kill_cmd]

    args = {'stdout': open(os.devnull, 'w'), 'stderr': subprocess.STDOUT}
    if verbose:
        print ' '.join(ssh_cmd)
        args = {}

    env = dict(os.environ)
    env['LD_LIBRARY_PATH'] = env.get('LD_LIBRARY_PATH_ORIG', '')
    subprocess.call(ssh_cmd, env=env, **args)

def copy_file_from(cfg, server, remote_file, local_file, verbose=False):
    rfile = os.path.join(ASSIGNMENT_PATH, remote_file)
    scp_cmd = ['scp', '-i', cfg.get('SSH', 'id'), cfg.get('SSH', 'user')+'@'+server+':'+rfile, local_file]

    args = {'stdout': open(os.devnull, 'w'), 'stderr': subprocess.STDOUT}
    if verbose:
        print ' '.join(scp_cmd)
        args = {}

    env = dict(os.environ)
    env['LD_LIBRARY_PATH'] = env.get('LD_LIBRARY_PATH_ORIG', '')
    subprocess.call(scp_cmd, env=env, **args)

def copy_file_to(cfg, server, local_file, remote_file, verbose=False):
    rfile = os.path.join(ASSIGNMENT_PATH, remote_file)
    scp_cmd = ['scp', '-i', cfg.get('SSH', 'id'), local_file, cfg.get('SSH', 'user')+'@'+server+':'+rfile]

    args = {'stdout': open(os.devnull, 'w'), 'stderr': subprocess.STDOUT}
    if verbose:
        print ' '.join(scp_cmd)
        args = {}

    env = dict(os.environ)
    env['LD_LIBRARY_PATH'] = env.get('LD_LIBRARY_PATH_ORIG', '')
    subprocess.check_call(scp_cmd, env=env, **args)

def delete_file_from(cfg, server, remote_file, verbose=False):
    rfile = os.path.join(ASSIGNMENT_PATH, remote_file)
    del_cmd = 'rm -f %s' % (rfile)
    ssh_cmd = ['ssh', '-i', cfg.get('SSH', 'id'), cfg.get('SSH', 'user')+'@'+server, del_cmd]

    args = {'stdout': open(os.devnull, 'w'), 'stderr': subprocess.STDOUT}
    if verbose:
        print ' '.join(ssh_cmd)
        args = {}

    env = dict(os.environ)
    env['LD_LIBRARY_PATH'] = env.get('LD_LIBRARY_PATH_ORIG', '')
    subprocess.call(ssh_cmd, env=env, **args)

def run_cmd(cfg, server, remote_cmd, async=True, verbose=False):
    r_cmd = 'cd %s; %s' % (ASSIGNMENT_PATH, remote_cmd)
    ssh_cmd = ['ssh', '-i', cfg.get('SSH', 'id'), cfg.get('SSH', 'user')+'@'+server, r_cmd]

    args = {'stdout': open(os.devnull, 'w'), 'stderr': subprocess.STDOUT}
    if verbose:
        print ' '.join(ssh_cmd)
        args = {}

    env = dict(os.environ)
    env['LD_LIBRARY_PATH'] = env.get('LD_LIBRARY_PATH_ORIG', '')
    if async: return subprocess.Popen(ssh_cmd, env=env, **args)
    else: return subprocess.call(ssh_cmd, env=env, **args)

def run_script(cfg, server, args, script, verbose=False):
    remote_cmd = 'python -u - %s < %s' % (args, script)
    ssh_cmd = ['ssh', '-i', cfg.get('SSH', 'id'), cfg.get('SSH', 'user')+'@'+server, remote_cmd]

    args = {'stdout': open(os.devnull, 'w'), 'stderr': subprocess.STDOUT}
    if verbose:
        print ' '.join(ssh_cmd)
        args = {}

    env = dict(os.environ)
    env['LD_LIBRARY_PATH'] = env.get('LD_LIBRARY_PATH_ORIG', '')
    subprocess.Popen(' '.join(ssh_cmd), shell=True, env=env, **args)
