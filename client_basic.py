import asyncio
import argparse
import time
import json
from messages import IAMAT, WHATSAT
from evaluate import evaluate_json, evaluate_info
import pandas as pd
import os
import sys


'''
communicate (['Hill', 'Jaquez', 'Smith', 'Campbell', 'Singleton'])
0 1 1 0 0
0 1 0 0 1
0 0 0 1 1
0 0 1 0 1
0 1 1 1 0
'''

TIMEOUT_MSG = "TIMEOUT"
PYTHON_VER = "3.8" # "3.7"

class SuperClient:
    def __init__(self, host='127.0.0.1', message_max_length=1e6, timeout=None):
        '''
        127.0.0.1 is the localhost
        port could be any port
        '''
        self.host = host
        self.message_max_length = int(message_max_length)
        self.timeout = timeout # no timeout if None

    def set_server_info(self, port_dict, server_dir):
        self.port_dict = port_dict
        self.port2server = dict(zip(port_dict.values(), port_dict.keys()))
        self.Hill = port_dict['Hill']
        self.Jaquez = port_dict['Jaquez']
        self.Smith = port_dict['Smith']
        self.Campbell = port_dict['Campbell']
        self.Singleton = port_dict['Singleton']
        self.server = os.path.join(server_dir, "server.py")

    async def start_server(self, server_name):
        command = 'nohup python{} {} {} &\n'.format(PYTHON_VER, self.server, server_name)
        os.system(command)
        # wait for a while so that the server has its time of setting up
        await asyncio.sleep(0.5)

    async def end_server(self, server_name):
        port = self.port_dict[server_name]
        os.system('lsof -ti:{} | xargs kill'.format(port))
        await asyncio.sleep(0.3)

    def end_all_servers(self):
        for server_name in self.port_dict.keys():
            port = self.port_dict[server_name]
            os.system('lsof -ti:{} | xargs kill'.format(port))

    async def crazy(self, port, message):
        reader, writer = await asyncio.open_connection(self.host, port, loop=self.loop)
        # write
        writer.write(str(message).encode())
        await writer.drain()
        writer.write_eof()
        # read
        if self.timeout is None:
            data =  await reader.read(self.message_max_length)
        else:
            read_func = reader.read(self.message_max_length)
            try:
                data = await asyncio.wait_for(read_func, timeout=self.timeout)
            except asyncio.TimeoutError:
                writer.close()
                print("TIME OUT")
                return TIMEOUT_MSG
        writer.close()
        return data.decode().strip()

    async def iamat(self, port, clientName, longitude, latitude):
        message = IAMAT(clientName, longitude, latitude, time.time())
        reader, writer = await asyncio.open_connection(self.host, port, loop=self.loop)
        # write
        writer.write(str(message).encode())
        await writer.drain()
        writer.write_eof()
        # read
        if self.timeout is None:
            data =  await reader.read(self.message_max_length)
        else:
            read_func = reader.read(self.message_max_length)
            try:
                data = await asyncio.wait_for(read_func, timeout=self.timeout)
            except asyncio.TimeoutError:
                writer.close()
                print("TIME OUT")
                return TIMEOUT_MSG
        writer.close()
        return data.decode().strip()

    async def whatsat(self, port, clientName, radius, maxItems):
        message = WHATSAT(clientName, radius, maxItems)
        reader, writer = await asyncio.open_connection(self.host, port, loop=self.loop)
        # write
        writer.write(str(message).encode())
        await writer.drain()
        writer.write_eof()
        # read
        if self.timeout is None:
            data =  await reader.read(self.message_max_length)
        else:
            read_func = reader.read(self.message_max_length)
            try:
                data = await asyncio.wait_for(read_func, timeout=self.timeout)
            except asyncio.TimeoutError:
                writer.close()
                print("TIME OUT")
                return TIMEOUT_MSG
        writer.close()
        return data.decode()

    def run_iamat(self, port, clientName, longitude, latitude):
        # start the loop
        data = self.loop.run_until_complete(self.iamat(port, clientName, longitude, latitude))
        return data
    def safe_run_iamat(self, *args):
        try:
            return self.run_iamat(*args)
        except:
            return "CRUSH"

    def run_whatsat(self, port, clientName, radius, maxItems):
        # start the loop
        data = self.loop.run_until_complete(self.whatsat(port, clientName, radius, maxItems))
        first_line = data.split('\n')[0]
        json_part = json.loads(data[len(first_line):]) if first_line.strip()[0] != "?" else dict()
        first_line = first_line.strip()
        return first_line, json_part

    def safe_run_whatsat(self, *args):
        try:
            return self.run_whatsat(*args)
        except:
            return "CRUSH", dict()

    def run_crazy(self, port, crazy_info):
        data = self.loop.run_until_complete(self.crazy(port, crazy_info))
        return True if (len(data) and data[0] == '?') else False

    def run_startserver(self, server_name):
        self.loop.run_until_complete(self.start_server(server_name))
    def run_endserver(self, server_name):
        self.loop.run_until_complete(self.end_server(server_name))

    def start_all_servers(self):
        for server_name in self.port_dict.keys():
            self.run_startserver(server_name)

    def test(self):
        self.loop = asyncio.get_event_loop()
        # dropping the connections
        all_servers = list(self.port_dict.keys())
        for server_name in all_servers:
            self.run_endserver(server_name)
            # similarly, self.run_startserver(server_name) could be used to start a single server
        # start the servers
        self.start_all_servers()
        # basic test
        data = self.run_iamat(self.Hill, "client", 34.068930, -118.445127)
        print(evaluate_info(data, self.port2server[self.Hill], "client", 34.068930, -118.445127))
        first_line, json_part = self.run_whatsat(self.Hill, "client", 10, 5)
        print(evaluate_info(first_line, self.port2server[self.Hill], "client", 34.068930, -118.445127))
        print(evaluate_json(json_part, 5))
        first_line, json_part = self.run_whatsat(self.Jaquez, "client", 10, 5)
        print(evaluate_info(first_line, self.port2server[self.Hill], "client", 34.068930, -118.445127))
        print(evaluate_json(json_part, 5))
        self.loop.close()
        # terminate the servers
        self.end_all_servers()

if __name__ == '__main__':
    TIMEOUT = 20
    # an example of the ports
    port_dict = {
        'Hill': 8000,
        'Jaquez': 8001,
        'Smith': 8002,
        'Campbell': 8003,
        'Singleton': 8004
    }
    server_dir = "./sample_submission" # the place where we can find server.py

    sys.path.append(server_dir) # this is in case we have other files to import from there

    client = SuperClient(timeout=TIMEOUT) # using the default settings
    client.set_server_info(port_dict, server_dir)
    client.test()
    
    
    
    


