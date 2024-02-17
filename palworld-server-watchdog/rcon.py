import socket
import struct
import os
import env
import random

SIGNED_INT_32_BIT_MAX = 2147483647

class RCONClient:
    def __init__(self, host = '127.0.0.1', port = 25575, password = ''):
        self.host = host
        self.port = port
        self.password = os.getenv('PALWORLD_ADMIN_PASSWORD', password)
    
    def command(self, command, args):
        packet = self.build_packet(command, args)
        return self.send_request(packet)
    
    def send_request(self,packet):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            
    def build_packet(self,command,args):
        raise NotImplementedError
    
    def encode(self, type, body):
        id = self.generate_id()
        return struct.pack('<iii', 10 + len(body), id, type) + body.encode('utf-8') + b'\x00\x00'

    def decode(self, packet):
        raise NotImplementedError
    
    def generate_id(self):
        return random.randint(0,SIGNED_INT_32_BIT_MAX)