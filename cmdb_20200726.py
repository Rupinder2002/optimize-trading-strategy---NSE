import ipaddress
import os
import subprocess
import json
import pandas as pd
import concurrent.futures
from netmiko import Netmiko
from netmiko import ConnectHandler
from netmiko.ssh_exception import AuthenticationException
from netmiko.ssh_exception import NetMikoTimeoutException
from netmiko.ssh_autodetect import SSHDetect
import time
import threading
from netmiko.snmp_autodetect import SNMPDetect


start = time.perf_counter()

alive = []
device_dict = []
config_threads_list = []

cmdb =  {'device_ip':[],
        'software_version':[],
        'hostname':[],
        'vendor' :[],
        'model' :[],
        'serial_number':[],
        'part_number':[],
        'description':[]
        }
show_juniper = []
show_juniper_mx = []

def ping_host(i):
    i = str(i)
    retval = subprocess.Popen(["sudo", "/usr/local/sbin/fping", "-g", "-r", "1", i],stdout=subprocess.PIPE )
    output = retval.stdout.read()
    output = output.decode('utf-8')
    lis = output.splitlines()
    live = [line.split()[0] for line in lis if line.split()[2] == 'alive']
    alive.extend(live)

def run_ping():
    sub_list = ['10.12.20.3/32','10.12.20.5/32','10.12.20.6/32','10.12.20.1/32','10.12.20.8/32']
    for sub in sub_list:
        ping_host(sub)

def device_dictionary(alive):
    for ip in alive:
        device = {
            'device_type': 'autodetect',
            'host': ip,
            'username': 'ln-sbalakrishnan',
            'password': 'Sandy````2222',
        }
        device_dict.append(device)


def juniper_mx(output,output1,host_ip,model):
    output = output.replace('{master}','')
    output_dict = json.loads(output)
    
    output1 = output1.replace('{master}','')
    output1_dict = json.loads(output1)
   
    temp_var = output1_dict['chassis-inventory'][0]['chassis']
    temp_var1 = output1_dict['chassis-inventory'][0]['chassis'][0]['chassis-module']
    
    chassis ={}
    chassis['serial'] = output1_dict['chassis-inventory'][0]['chassis'][0]['serial-number'][0]['data']
    chassis['name'] = output1_dict['chassis-inventory'][0]['chassis'][0]['name'][0]['data']
    chassis['part_number'] = 'NA'
    chassis['host_ip'] = host_ip
    chassis['description'] = output1_dict['chassis-inventory'][0]['chassis'][0]['description'][0]['data']
    chassis['hostname'] = output_dict['software-information'][0]['host-name'][0]['data']
    chassis['software_version'] = output_dict['software-information'][0]['junos-version'][0]['data']
    show_juniper_mx.append(chassis)

    for item in temp_var1:
        temp_dict = {}
        temp_dict['serial'] = item['serial-number'][0]['data']
        temp_dict['name'] = item['name'][0]['data']
        temp_dict['part_number'] = item['part-number'][0]['data']
        temp_dict['host_ip'] = host_ip
        temp_dict['description'] = item['description'][0]['data']
        temp_dict['hostname'] = output_dict['software-information'][0]['host-name'][0]['data']
        temp_dict['software_version'] = 'NA'
        show_juniper_mx.append(temp_dict)
    

def ssh_device(device):
    try:
        guesser = SSHDetect(**device)
        best_match = guesser.autodetect()
        print(best_match)
        print(guesser.potential_matches)
        device['device_type'] = best_match
        net_connect = ConnectHandler(**device)
        host_ip = device['host']
        # If the device matched is JUNIPER
        if best_match == 'juniper_junos':
            #Check if the device is MX or EX
            output = net_connect.send_command('show version |match model')
            model = output.split()[1]
            if model.__contains__("ex"):
                output = net_connect.send_command('show version | display json | no-more')
                output1 = net_connect.send_command('show virtual-chassis | display json | no-more')
                juniper_ex(output,output1,host_ip,model)
            if model.__contains__("mx"):
                output = net_connect.send_command('show version | display json | no-more')
                output1 = net_connect.send_command('show chassis hardware | display json | no-more')
                juniper_mx(output,output1,host_ip,model)

    except(AuthenticationException):
        print("Error connecting to device:", device['host'])
    except(NetMikoTimeoutException):
        print("SSH detect timeout for device:", device['host'])
        return


def cmdb_publish_mx(show_juniper_mx):
    for item in show_juniper_mx:
        cmdb['serial_number'].append(item['serial'])
        cmdb['device_ip'].append(item['host_ip'])
        cmdb['hostname'].append(item['hostname'])
        cmdb['model'].append(item['name'])
        cmdb['vendor'] = ' Juniper' 
        cmdb['part_number'].append(item['part_number'])
        cmdb['description'].append(item['description'])
        cmdb['software_version'].append(item['software_version'])

def ssh_thread(device_dict):
    for device in device_dict:
        print(device)
        config_threads_list.append(threading.Thread(target=ssh_device, args=(device,)))

    for config_thread in config_threads_list:
        config_thread.start()
        print(config_thread)

    for config_thread in config_threads_list:
        config_thread.join()
    cmdb_publish_mx(show_juniper_mx)

def data_frame(value):
    pd.set_option('display.max_rows', 100)
    df = pd.DataFrame(value)
    #df = pd.DataFrame.from_dict(cmdb, orient='index', columns=[]) 
    print("\n\n",df)

def run_main():
    run_ping()
    device_dictionary(alive)
    ssh_thread(device_dict)
    data_frame(cmdb)


if __name__ == '__main__':
    run_main()

finish = time.perf_counter()
print("\n", f'Finished in {round(finish - start, 3)} second(s)')

