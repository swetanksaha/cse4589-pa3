import random
import os
import struct
import subprocess
from time import sleep
import filecmp
import sys
import socket

import utils
import remote_api
from dijkstra import Graph

def author(controller_path, cfg):
    ubitname = raw_input("UBIT Name: ")

    link_costs = [
    ('1', '2', 3),
    ('1', '3', 1),
    ('1', '4', 7),
    ('2', '4', 2),
    ('4', '5', 2),
    ('4', '3', 1),
    ('5', '2', 6),
    ]

    cntrl_port = utils.random_port()
    remote_api.init_remote_assignment(cfg, cntrl_port)
    ROUTERS, ROUTER_ID_MAPPING = utils.gen_topology(link_costs, cntrl_port)

    for router in ROUTERS:
        success = False
        utils.run_cmd([controller_path, '-t', 'topology', '-a', str(router.id), '-o', 'response.pkt'])
        try:
            with open('response.pkt', 'r') as f:
                header = struct.unpack('!4sBBH', f.read(8))
                controller_ip, cntrl_code, resp_code, payload_len = utils.parse_response_header(header)
                payload = f.read(payload_len)
                os.system('hexdump -C response.pkt')
                if payload == 'I, '+ubitname+', have read and understood the course academic integrity policy.':
                    success = True
        except:
            success = False

    remote_api.cleanup(cfg)
    utils.cleanup()
    print success

def parse_routing_table(payload):
    r_table = []
    num_entries = 1
    byte_index = 0
    while num_entries <= len(payload)/8:
        entry = struct.unpack('!H2sHH', payload[byte_index:byte_index+8])
        r_table.append( [entry[0], entry[2], entry[3]] )

        num_entries += 1
        byte_index += 8

    return r_table

def grade_init(controller_path, link_costs, cfg):
    cntrl_port = utils.random_port()
    remote_api.init_remote_assignment(cfg, cntrl_port)
    ROUTERS, ROUTER_ID_MAPPING = utils.gen_topology(link_costs, cntrl_port, scramble=True)

    utils.run_cmd([controller_path, '-t', 'topology', '-i', '10', '-o', 'response.pkt'])
    os.system('rm response.pkt*') #cleanup
    success = False
    for src in ROUTERS:
        success = False
        utils.run_cmd([controller_path, '-t', 'topology', '-r', str(src.id), '-o', 'response.pkt'])

        try:
            with open('response.pkt', 'r') as f:
                header = struct.unpack('!4sBBH', f.read(8))
                controller_ip, cntrl_code, resp_code, payload_len = utils.parse_response_header(header)
                payload = f.read(payload_len)
                os.system('hexdump -C response.pkt')

                if payload_len != len(ROUTERS)*8: break
                r_table = parse_routing_table(payload)

                #Build expected routing table
                expected_r_table = []
                for dst in ROUTERS:
                    expected_cost = utils.get_link_cost(ROUTER_ID_MAPPING[str(src.id)], ROUTER_ID_MAPPING[str(dst.id)], link_costs)
                    if expected_cost == 65535: nxt_hop = 65535
                    else: nxt_hop = dst.id
                    expected_r_table.append( [dst.id, nxt_hop, expected_cost] )

                if cmp(sorted(r_table), sorted(expected_r_table)) == 0: success = True
                else:
                    print '--------------'
                    print r_table
                    print expected_r_table
                    print '--------------'
                    success = False
                    break
        except:
            success = False
            break

        utils.delete_file('response.pkt')

    remote_api.cleanup(cfg)
    utils.cleanup()
    return success

def init(controller_path, cfg):
    score = 0.0

    link_costs = [
    ('1', '2', 3),
    ('1', '3', 1),
    ('1', '4', 7),
    ('2', '4', 2),
    ('4', '5', 2),
    ('4', '3', 1),
    ('5', '2', 6)
    ]
    if grade_init(controller_path, link_costs, cfg): score += 5.0

    link_costs = [
    ('1', '2', 1),
    ('2', '3', 2),
    ('3', '4', 3),
    ('4', '5', 4)
    ]
    if grade_init(controller_path, link_costs, cfg): score += 5.0

    link_costs = [
    ('1', '2', 1),
    ('2', '3', 1),
    ('3', '1', 1),
    ('2', '4', 1)
    ]
    if grade_init(controller_path, link_costs, cfg): score += 5.0

    print score

def rupdates(controller_path, cfg):
    score = 0.0

    link_costs = [
    ('1', '2', 3)
    ]

    cntrl_port = utils.random_port()
    remote_api.init_remote_assignment(cfg, cntrl_port)
    ROUTERS, ROUTER_ID_MAPPING = utils.gen_topology(link_costs, cntrl_port)

    utils.run_cmd([controller_path, '-t', 'topology', '-i', '2', '-o' 'response.pkt'])
    os.system('rm response.pkt*') #cleanup

    if hasattr(sys, '_MEIPASS'): base_path = sys._MEIPASS
    else: base_path = os.path.abspath('.')
    packet_receiver_path = os.path.join(base_path, 'packet_receiver.py')

    # Neighbor
    remote_api.kill_process(cfg, utils.get_router_ip(int(ROUTER_ID_MAPPING['2']), ROUTERS), ROUTERS[1].control_port)
    remote_api.run_script(cfg, utils.get_router_ip(int(ROUTER_ID_MAPPING['2']), ROUTERS), str(ROUTERS[1].router_port)+' 4 '+remote_api.ASSIGNMENT_PATH, packet_receiver_path)

    # Non-Neighbor
    remote_api.kill_process(cfg, utils.get_router_ip(int(ROUTER_ID_MAPPING['3']), ROUTERS), ROUTERS[2].control_port)
    remote_api.run_script(cfg, utils.get_router_ip(int(ROUTER_ID_MAPPING['3']), ROUTERS), str(ROUTERS[2].router_port)+' 4 '+remote_api.ASSIGNMENT_PATH, packet_receiver_path)

    sleep(4)

    os.system('rm -f num_updates*')
    os.system('rm -f update-packet-*')

    # Check neighbor
    check = False
    remote_api.copy_file_from(cfg, ROUTERS[1].ip_addr, 'num_updates', 'num_updates_neighbor')
    if os.path.isfile('num_updates_neighbor'):
        check = True
        score += 2.5

    # Check non-neighbor
    if check:
        os.system('rm -f num_updates_non-neighbor')
        remote_api.copy_file_from(cfg, ROUTERS[2].ip_addr, 'num_updates', 'num_updates_non-neighbor')
        if not os.path.isfile('num_updates_non-neighbor'): score += 2.5

        with open('num_updates_neighbor', 'r') as f:
            num_updates = int(f.read())
        if num_updates == 2 or num_updates == 3: score += 5.0
        else: print 'Boo:', num_updates

        remote_api.copy_file_from(cfg, ROUTERS[1].ip_addr, os.path.join(remote_api.ASSIGNMENT_PATH, 'update-packet-'+str(num_updates-1)), './')
        with open('update-packet-'+str(num_updates-1), 'rb') as f:
            pkt = f.read()

        num_updates, src_router_port, src_router_ip = struct.unpack('!HH4s', pkt[:8])
        updates = []
        pkt = pkt[8:]
        #print "checking ...", len(pkt), num_updates
        if len(pkt) == num_updates*12:
            for index in range(num_updates):
                updates.append(struct.unpack('!4sHHHH', pkt[index*12:(index*12)+12]))

            # Build expected updates
            expected_updates = []
            for router in ROUTERS:
                cost = 65535
                if router.id == 1: cost = 0
                if router.id == 2: cost = 3
                update = (socket.inet_aton(router.ip_addr), router.router_port, 0, router.id, cost)
                expected_updates.append(update)

            if (num_updates == 5) and (src_router_port == ROUTERS[0].router_port) and (src_router_ip == socket.inet_aton(ROUTERS[0].ip_addr)) and (cmp(sorted(updates), sorted(expected_updates)) == 0):
                score += 5.0

    os.system('rm -f num_updates*')
    os.system('rm -f update-packet-*')
    remote_api.cleanup(cfg)
    utils.cleanup()
    print score

#Uses original IDs: 1,2,3,4,5  as input but return nxt_hop as mapped ID
def get_shortest_path(src, dst, link_costs, ROUTER_ID_MAPPING):
    if src == dst: return 0, int(ROUTER_ID_MAPPING[src])

    # Make link_costs symmetrical
    symm_link_costs = []
    for link in link_costs:
        symm_link_costs.append(link)
        symm_link_costs.append((link[1], link[0], link[2]))

    network = Graph(symm_link_costs)
    try:
        shortest_path = network.dijkstra(src, dst)
    except: return 65535, 65535
    path_cost = 0
    for hop in range(len(shortest_path)-1):
        path_cost += utils.get_link_cost(shortest_path[hop], shortest_path[hop+1], symm_link_costs)
    return path_cost, int(ROUTER_ID_MAPPING[shortest_path[1]])

def grade_rtable(controller_path, link_costs, cfg):
    cntrl_port = utils.random_port()
    remote_api.init_remote_assignment(cfg, cntrl_port)
    ROUTERS, ROUTER_ID_MAPPING = utils.gen_topology(link_costs, cntrl_port)

    utils.run_cmd([controller_path, '-t', 'topology', '-i', '1', '-o', 'response.pkt'])
    os.system('rm response.pkt*') #cleanup
    sleep(5)

    success = False
    for src in ROUTERS:
        success = False
        utils.run_cmd([controller_path, '-t', 'topology', '-r', str(src.id), '-o', 'response.pkt'])

        try:
            with open('response.pkt', 'r') as f:
                header = struct.unpack('!4sBBH', f.read(8))
                controller_ip, cntrl_code, resp_code, payload_len = utils.parse_response_header(header)
                payload = f.read(payload_len)
                os.system('hexdump -C response.pkt')

                if payload_len != len(ROUTERS)*8: break
                r_table = parse_routing_table(payload)

                #Build expected routing table
                expected_r_table = []
                for dst in ROUTERS:
                    expected_cost, nxt_hop = get_shortest_path(ROUTER_ID_MAPPING[str(src.id)], ROUTER_ID_MAPPING[str(dst.id)], link_costs, ROUTER_ID_MAPPING)
                    if expected_cost == 65535: nxt_hop = 65535
                    expected_r_table.append( [dst.id, nxt_hop, expected_cost] )

                if cmp(sorted(r_table), sorted(expected_r_table)) == 0: success = True
                else:
                    success = False
                    break
        except:
            success = False
            break

        utils.delete_file('response.pkt')

    remote_api.cleanup(cfg)
    utils.cleanup()
    return success

def rtable(controller_path, cfg):
    score = 0.0

    link_costs = [
    ('1', '2', 3),
    ('1', '3', 1),
    ('1', '4', 7),
    ('2', '4', 2),
    ('4', '5', 2),
    ('4', '3', 1),
    ('5', '2', 6)
    ]
    if grade_rtable(controller_path, link_costs, cfg): score += 5.0

    link_costs = [
    ('1', '2', 1),
    ('2', '3', 2),
    ('3', '4', 3),
    ('4', '5', 4)
    ]
    if grade_rtable(controller_path, link_costs, cfg): score += 5.0

    link_costs = [
    ('1', '2', 1),
    ('2', '3', 1),
    ('3', '1', 1),
    ('2', '4', 1)
    ]
    if grade_rtable(controller_path, link_costs, cfg): score += 5.0

    link_costs = [
    ('1', '2', 22),
    ('1', '4', 2),
    ('3', '4', 1),
    ('4', '5', 3),
    ('2', '3', 11),
    ('5', '2', 3)
    ]
    if grade_rtable(controller_path, link_costs, cfg): score += 5.0

    print score

def grade_update(controller_path, link_costs, link_update, updated_link_costs, cfg):
    cntrl_port = utils.random_port()
    remote_api.init_remote_assignment(cfg, cntrl_port)
    ROUTERS, ROUTER_ID_MAPPING = utils.gen_topology(link_costs, cntrl_port)

    utils.run_cmd([controller_path, '-t', 'topology', '-i', '1', '-o', 'response.pkt'])
    os.system('rm response.pkt*') #cleanup
    sleep(3)
    utils.run_cmd([controller_path, '-t', 'topology', '-u', ROUTER_ID_MAPPING[link_update[0]], ROUTER_ID_MAPPING[link_update[1]], str(link_update[2]), '-o', 'response.pkt'])
    os.system('rm response.pkt*') #cleanup
    sleep(3)
    success = False
    for src in ROUTERS:
        success = False
        utils.run_cmd([controller_path, '-t', 'topology', '-r', str(src.id), '-o', 'response.pkt'])

        try:
            with open('response.pkt', 'r') as f:
                header = struct.unpack('!4sBBH', f.read(8))
                controller_ip, cntrl_code, resp_code, payload_len = utils.parse_response_header(header)
                payload = f.read(payload_len)
                os.system('hexdump -C response.pkt')

                if payload_len != len(ROUTERS)*8: break
                r_table = parse_routing_table(payload)

                #Build expected routing table
                expected_r_table = []
                for dst in ROUTERS:
                    expected_cost, nxt_hop = get_shortest_path(ROUTER_ID_MAPPING[str(src.id)], ROUTER_ID_MAPPING[str(dst.id)], updated_link_costs, ROUTER_ID_MAPPING)
                    if expected_cost == 65535: nxt_hop = 65535
                    expected_r_table.append( [dst.id, nxt_hop, expected_cost] )

                if cmp(sorted(r_table), sorted(expected_r_table)) == 0: success = True
                else:
                    print '--------------'
                    print r_table
                    print expected_r_table
                    print '--------------'
                    success = False
                    break
        except:
            success = False
            break

        utils.delete_file('response.pkt') #cleanup

    remote_api.cleanup(cfg)
    utils.cleanup()
    return success

def update(controller_path, cfg):
    score = 0.0

    link_costs = [
    ('1', '2', 1),
    ('1', '3', 1),
    ('2', '3', 1),
    ('4', '2', 1),
    ('3', '5', 1)
    ]
    updated_link_costs = [
    ('1', '2', 1),
    ('1', '3', 3),
    ('2', '3', 1),
    ('4', '2', 1),
    ('3', '5', 1)
    ]
    if grade_update(controller_path, link_costs, ('1', '3', 3), updated_link_costs, cfg): score += 5.0

    link_costs = [
    ('1', '2', 4),
    ('1', '3', 3),
    ('2', '3', 2),
    ('4', '2', 3),
    ('3', '5', 1)
    ]
    updated_link_costs = [
    ('1', '2', 4),
    ('1', '3', 1),
    ('2', '3', 2),
    ('4', '2', 3),
    ('3', '5', 1)
    ]
    if grade_update(controller_path, link_costs, ('1', '3', 1), updated_link_costs, cfg): score += 5.0

    print score

def crash(controller_path, cfg):
    score = 0.0

    link_costs = [
    ('1', '2', 1),
    ('2', '3', 1),
    ('3', '4', 1),
    ('4', '5', 1)
    ]

    cntrl_port = utils.random_port()
    remote_api.init_remote_assignment(cfg, cntrl_port)
    ROUTERS, ROUTER_ID_MAPPING = utils.gen_topology(link_costs, cntrl_port, scramble=True)

    utils.run_cmd([controller_path, '-t', 'topology', '-i', '1', '-o', 'response.pkt'])
    os.system('rm response.pkt*') #cleanup
    sleep(3)

    nonce = random.randint(100,1000)
    utils.run_cmd([controller_path, '-t', 'topology', '-a', ROUTER_ID_MAPPING['1'], '-o', 'response-author-'+str(nonce)+'.pkt'])
    before_author = False
    if os.path.isfile('response-author-'+str(nonce)+'.pkt'):
        before_author = True

    # Crash router
    utils.run_cmd([controller_path, '-t', 'topology', '-c', ROUTER_ID_MAPPING['1'], '-o', 'response.pkt'])
    os.system('rm response.pkt*') #cleanup

    nonce = random.randint(100,1000)
    utils.run_cmd([controller_path, '-t', 'topology', '-a', ROUTER_ID_MAPPING['1'], '-o', 'response-author-'+str(nonce)+'.pkt'])
    after_author = False
    if os.path.isfile('response-author-'+str(nonce)+'.pkt'):
        after_author = True

    if before_author and (not after_author): score += 5.0

    sleep(4)
    utils.run_cmd([controller_path, '-t', 'topology', '-r', ROUTER_ID_MAPPING['3'], '-o', 'response.pkt'])
    before_cost = None
    try:
        with open('response.pkt', 'r') as f:
            header = struct.unpack('!4sBBH', f.read(8))
            controller_ip, cntrl_code, resp_code, payload_len = utils.parse_response_header(header)
            payload = f.read(payload_len)
            os.system('hexdump -C response.pkt')

            if payload_len == len(ROUTERS)*8:
                r_table = parse_routing_table(payload)
                for entry in r_table:
                    if entry[0] == int(ROUTER_ID_MAPPING['1']): before_cost = entry[2]
    except: pass

    sleep(2)
    utils.run_cmd([controller_path, '-t', 'topology', '-r', ROUTER_ID_MAPPING['3'], '-o', 'response.pkt'])
    after_cost = None
    try:
        with open('response.pkt', 'r') as f:
            header = struct.unpack('!4sBBH', f.read(8))
            controller_ip, cntrl_code, resp_code, payload_len = utils.parse_response_header(header)
            payload = f.read(payload_len)
            os.system('hexdump -C response.pkt')

            if payload_len == len(ROUTERS)*8:
                r_table = parse_routing_table(payload)
                for entry in r_table:
                    if entry[0] == int(ROUTER_ID_MAPPING['1']): after_cost = entry[2]
    except: pass

    #print before_cost, after_cost
    if before_cost and after_cost and (after_cost > before_cost): score += 5.0

    os.system('rm response-author*') #cleanup
    remote_api.cleanup(cfg)
    utils.cleanup()
    print score

def read_file_bytes(filename, start_byte, num_bytes):
    with open(filename, 'rb') as file:
        file.seek(start_byte, os.SEEK_END)
        return file.read(num_bytes)

def check_file_transfer(controller_path, init_ttl, transfer_id, init_seq_num, filename, expected_path, ROUTER_ID_MAPPING, multi=False):
    success = True
    for router in expected_path:
        # Check Stats
        os.system('rm response.pkt*') #cleanup
        utils.run_cmd([controller_path, '-t', 'topology', '-s', ROUTER_ID_MAPPING[router], str(transfer_id), '-o', 'response.pkt'])

        try:
            with open('response.pkt', 'r') as f:
                header = struct.unpack('!4sBBH', f.read(8))
                controller_ip, cntrl_code, resp_code, payload_len = utils.parse_response_header(header)
                payload = f.read(payload_len)
                #os.system('hexdump -C response.pkt')

                t_id, ttl, padding = struct.unpack('!BB2s', payload[:4])
                seq_nums = []
                index = 4
                while index < payload_len:
                    seq_num = struct.unpack('!H', payload[index:index+2])
                    seq_nums.append(seq_num[0])
                    index += 2
                expected_seq_nums = range(init_seq_num, init_seq_num+10240)
                if (t_id != transfer_id) or (ttl != init_ttl) or (cmp(expected_seq_nums, seq_nums)!=0) :
                    success = False
                    break
        except:
            success = False
            break

        # Check Last packet
        if not multi:
            os.system('rm response.pkt*') #cleanup
            utils.run_cmd([controller_path, '-t', 'topology', '-l', ROUTER_ID_MAPPING[router], '-o', 'response.pkt'])

            try:
                with open('response.pkt', 'r') as f:
                    header = struct.unpack('!4sBBH', f.read(8))
                    controller_ip, cntrl_code, resp_code, payload_len = utils.parse_response_header(header)
                    payload = f.read(payload_len)
                    #os.system('hexdump -C response.pkt')

                    if payload_len != 1036:
                        success = False
                        break

                    data_pkt = payload
                    t_id, ttl, seq_num, fin = struct.unpack('!BBHB', data_pkt[4:9])
                    expected_data = read_file_bytes(filename, -1024, 1024)
                    if (t_id != transfer_id) or (ttl != init_ttl) or (seq_num!=expected_seq_nums[-1]) or (fin!=128) or (expected_data!=data_pkt[12:]):
                        success = False
                        break
            except:
                success = False
                break

        # Check Penultimate packet
        if not multi:
            os.system('rm response.pkt*') #cleanup
            utils.run_cmd([controller_path, '-t', 'topology', '-p', ROUTER_ID_MAPPING[router], '-o', 'response.pkt'])

            try:
                with open('response.pkt', 'r') as f:
                    header = struct.unpack('!4sBBH', f.read(8))
                    controller_ip, cntrl_code, resp_code, payload_len = utils.parse_response_header(header)
                    payload = f.read(payload_len)
                    #os.system('hexdump -C response.pkt')

                    if payload_len != 1036:
                        success = False
                        break

                    data_pkt = payload
                    t_id, ttl, seq_num, fin = struct.unpack('!BBHB', data_pkt[4:9])
                    expected_data = read_file_bytes(filename, -(1024+1024), 1024)
                    if (t_id != transfer_id) or (ttl != init_ttl) or (seq_num!=expected_seq_nums[-2]) or (fin!=0) or (expected_data!=data_pkt[12:]):
                        success = False
                        break
            except:
                success = False
                break

        init_ttl -= 1

    return success

def compare_files(cfg, local_filename, server, remote_filename):
    result = False
    try:
        utils.delete_file(remote_filename)
        remote_api.run_cmd(cfg, server, 'chmod 777 '+remote_filename)
        remote_api.copy_file_from(cfg, server, remote_filename, remote_filename)
        result = filecmp.cmp(local_filename, remote_filename)
    except: pass
    finally: utils.delete_file(remote_filename)

    return result

def grade_data(controller_path, link_costs, pass_stats, pass_file, pass_fail, expected_path_success, expected_path_fail, init_ttl_success, init_ttl_fail, src, dst, cfg):
    score = 0.0
    cntrl_port = utils.random_port()
    remote_api.init_remote_assignment(cfg, cntrl_port)
    ROUTERS, ROUTER_ID_MAPPING = utils.gen_topology(link_costs, cntrl_port, scramble=True)

    init_ttl = init_ttl_success
    transfer_id = random.randint(1,100)
    init_seq_num = random.randint(1,100)
    filename = 'testfile1'

    # Move file on src router
    remote_api.copy_file_to(cfg, utils.get_router_ip(int(ROUTER_ID_MAPPING[src]), ROUTERS), filename, filename)

    # Remove file on dst router (if it exists)
    remote_api.delete_file_from(cfg, utils.get_router_ip(int(ROUTER_ID_MAPPING[dst]), ROUTERS), 'file-*')

    # INIT
    utils.run_cmd([controller_path, '-t', 'topology', '-i', '1', '-o', 'response.pkt'])
    os.system('rm response.pkt*') #cleanup
    sleep(2)

    # Do File Transfer
    remote_api.run_cmd(cfg, utils.get_router_ip(int(ROUTER_ID_MAPPING[src]), ROUTERS), 'chmod 777 '+filename)
    utils.run_cmd([controller_path, '-t', 'topology', '-f', ROUTER_ID_MAPPING[src], ROUTER_ID_MAPPING[dst], str(init_ttl), str(transfer_id), str(init_seq_num), filename, '-o', 'response.pkt'])
    sleep(8)

    # Checks File stats/meta
    expected_path = expected_path_success
    if check_file_transfer(controller_path, init_ttl, transfer_id, init_seq_num, filename, expected_path, ROUTER_ID_MAPPING): score += pass_stats
    # Check File itself
    if compare_files(cfg, filename, utils.get_router_ip(int(ROUTER_ID_MAPPING[dst]), ROUTERS), 'file-'+str(transfer_id)): score += pass_file

    init_ttl = init_ttl_fail
    transfer_id = random.randint(1,100)
    init_seq_num = random.randint(1,100)
    filename = 'testfile2'

    # Move file on src router
    remote_api.copy_file_to(cfg, utils.get_router_ip(int(ROUTER_ID_MAPPING[src]), ROUTERS), filename, filename)

    # Remove file on dst router (if it exists)
    remote_api.delete_file_from(cfg, utils.get_router_ip(int(ROUTER_ID_MAPPING[dst]), ROUTERS), 'file-*')

    # Do File Transfer
    remote_api.run_cmd(cfg, utils.get_router_ip(int(ROUTER_ID_MAPPING[src]), ROUTERS), 'chmod 777 '+filename)
    utils.run_cmd([controller_path, '-t', 'topology', '-f', ROUTER_ID_MAPPING[src], ROUTER_ID_MAPPING[dst], str(init_ttl), str(transfer_id), str(init_seq_num), filename, '-o', 'response.pkt'])
    sleep(8)

    # Checks File stats/meta and File Transfer failure
    expected_path = expected_path_fail
    if check_file_transfer(controller_path, init_ttl, transfer_id, init_seq_num, filename, expected_path, ROUTER_ID_MAPPING) and not (compare_files(cfg, filename, utils.get_router_ip(int(ROUTER_ID_MAPPING[dst]), ROUTERS), 'file-'+str(transfer_id))):
        score += pass_fail

    remote_api.cleanup(cfg)
    utils.cleanup()
    return score

def data(controller_path, cfg):
    score = 0.0

    link_costs = [
    ('1', '2', 1),
    ('2', '3', 1),
    ('3', '4', 1),
    ('4', '1', 100),
    ('4', '5', 1),
    ('5', '2', 100)
    ]
    score += grade_data(controller_path, link_costs, 5.0, 10.0, 5.0, ['5', '4', '3', '2', '1'], ['5', '4'], 7, 2, '5', '1', cfg)

    link_costs = [
    ('1', '2', 100),
    ('2', '3', 100),
    ('3', '4', 100),
    ('4', '1', 100),
    ('4', '5', 1),
    ('5', '2', 100)
    ]
    score += grade_data(controller_path, link_costs, 3.0, 4.0, 3.0, ['5', '4'], ['5'], 2, 1, '5', '4', cfg)

    print score

def init_multi_file_transfer(controller_path, src, dst, init_ttls, transfer_ids, init_seq_nums, file_list, ROUTER_ID_MAPPING):
    command = '#!/bin/bash\n'
    for index in range(len(file_list)):
        command += controller_path+' -t topology -f '+ROUTER_ID_MAPPING[src[index]]+' '+ROUTER_ID_MAPPING[dst[index]]+' '+str(init_ttls[index])+' '
        command += str(transfer_ids[index])+' '+str(init_seq_nums[index])+' '+str(file_list[index])+' -o response-'+str(index)+'.pkt'
        command += ' &\n'

    run_file = open('multi_run_script', 'w')
    run_file.write(command)
    run_file.close()

    os.system('chmod +x multi_run_script')

    os.system('./multi_run_script')
    sleep(3)
    os.system('rm response-*.pkt') #cleanup

def grade_bonus(controller_path, link_costs, src, dst, init_ttls, file_list, expected_path, cfg):
    score = 0.0
    cntrl_port = utils.random_port()
    remote_api.init_remote_assignment(cfg, cntrl_port)
    ROUTERS, ROUTER_ID_MAPPING = utils.gen_topology(link_costs, cntrl_port, scramble=True)

    transfer_ids = []
    init_seq_nums = []

    for index in range(len(file_list)):
        transfer_ids.append(random.randint(1,100))
        init_seq_nums.append(random.randint(1,100))

        # Move file on src router
        remote_api.copy_file_to(cfg, utils.get_router_ip(int(ROUTER_ID_MAPPING[src[index]]), ROUTERS), file_list[index], file_list[index])
        remote_api.run_cmd(cfg, utils.get_router_ip(int(ROUTER_ID_MAPPING[src[index]]), ROUTERS), 'chmod 777 '+file_list[index])

        # Remove file on dst router (if it exists)
        remote_api.delete_file_from(cfg, utils.get_router_ip(int(ROUTER_ID_MAPPING[dst[index]]), ROUTERS), 'file-*')

    # INIT
    utils.run_cmd([controller_path, '-t', 'topology', '-i', '1', '-o', 'response.pkt'])
    os.system('rm response.pkt*') #cleanup
    sleep(2)

    # Do File Transfer
    init_multi_file_transfer(controller_path, src, dst, init_ttls, transfer_ids, init_seq_nums, file_list, ROUTER_ID_MAPPING)
    sleep(8)
    os.system('rm multi_run_script')

    for index in range(len(file_list)):
        # Checks File stats/meta
        if check_file_transfer(controller_path, init_ttls[index], transfer_ids[index], init_seq_nums[index], file_list[index], expected_path[index], ROUTER_ID_MAPPING, multi=True):
            score += 10.0
        # Check File itself
        if compare_files(cfg, file_list[index], utils.get_router_ip(int(ROUTER_ID_MAPPING[dst[index]]), ROUTERS), 'file-'+str(transfer_ids[index])):
            score += 10.0

    remote_api.cleanup(cfg)
    utils.cleanup()

    if score == len(file_list)*20: return True
    else: return False

def bonus(controller_path, cfg):
    score = 0.0

    link_costs = [
    ('1', '3', 1),
    ('3', '4', 1),
    ('1', '4', 5),
    ('2', '3', 1),
    ('2', '5', 5),
    ('5', '3', 1)
    ]
    if grade_bonus(controller_path, link_costs, ['1', '5'], ['4', '2'], [4, 4], ['testfile1', 'testfile2'], [['1', '3', '4'], ['5', '3', '2']], cfg):
        score += 7.0

    link_costs = [
    ('1', '4', 1),
    ('2', '4', 1),
    ('3', '4', 1),
    ('4', '5', 1)
    ]
    if grade_bonus(controller_path, link_costs, ['1', '2', '3'], ['5', '5', '5'], [4, 4, 4], ['testfile1', 'testfile2', 'testfile3'], [['1', '4', '5'], ['2', '4', '5'], ['3', '4', '5']], cfg):
        score += 7.0

    link_costs = [
    ('1', '3', 1),
    ('3', '4', 1),
    ('1', '4', 10),
    ('2', '3', 10),
    ('2', '5', 1),
    ('5', '3', 1)
    ]
    if grade_bonus(controller_path, link_costs, ['4', '2'], ['1', '1'], [4, 4], ['testfile1', 'testfile2'], [['4', '3', '1'], ['2', '5', '3', '1']], cfg):
        score += 6.0

    print score
