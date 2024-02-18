import socket
import struct
import os
import env
import random
from enum import Enum

class RCONPacketType(Enum):
    INVALID = -1
    SERVER_RESPONSE = 0
    SERVER_COMMAND_REQUEST = 2
    SERVER_AUTH_RESPONSE = 2
    SERVER_AUTH_REQUEST = 3

class RCONCommands(Enum):
    #ENUM = ('Command', Parameter Count)
    SAVE = ('Save', 0)
    SHOWPLAYERS = ('ShowPlayers', 0)
    INFO = ('Info', 0)
    DOEXIT = ('DoExit', 0)
    BANPLAYER = ('BanPlayer', 1)
    KICKPLAYER = ('KickPlayer', 1)
    BROADCAST = ('Broadcast', 1)
    SHUTDOWN = ('ShutDown', 2)

class RCONPacket:
    SIGNED_INT_32_BIT_MAX = 2147483647
    NULL_TERMINATOR = b'\x00'
    
    #ID FIELD = 4
    #TYPE FIELD = 4
    #PACKET TERMINATOR = 1
    HEADER_SIZE = 9 

    def __init__(self, *args):
        if len(args) == 2:
            self.id = RCONPacket.generate_id()
            self.type = args[0]
            self.body = args[1]
        elif len(args) == 3:
            self.id = args[0]
            self.type = args[1]
            self.body = args[2]
        else:
            raise Exception('Invalid arguments')

        self.body_size = len(self.body) + 1 if self.body is not None else 1
    
    def getTotalSize(self):
        return RCONPacket.HEADER_SIZE + self.body_size

    def generate_id():
        return random.randint(0,RCONPacket.SIGNED_INT_32_BIT_MAX)
    
    def isAuthenticated(self):
        return self.id != -1
    
    def pack(self):
        return struct.pack('<iii', self.getTotalSize(), self.id, self.type.value) + self.body.encode('utf-8') + RCONPacket.NULL_TERMINATOR + RCONPacket.NULL_TERMINATOR
    
    def unpack(packet:bytes):
        if len(packet) >= 10:
            (id, type_value) = struct.unpack('<ii', packet[4:12])
            body = packet[12:len(packet)-2].decode('utf-8')
            
            return RCONPacket(id, RCONPacketType(type_value), body)
        else:
            return RCONPacket(None, None, None)


class RCONClient:
    MAX_PACKET_SIZE = 4096

    RETRY_CONNECT = 3
    TIMEOUT_INTERVAL = 5
    WAIT_INTERVAL = 15

    def __init__(self, password = os.getenv('PALWORLD_ADMIN_PASSWORD', ''), host = '127.0.0.1', port = 25575):
        self.host = host
        self.port = port
        self.password = password

    def command(self, input:str):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(RCONClient.TIMEOUT_INTERVAL)

            #Attempt Connection
            retries = 0
            while retries < RCONClient.RETRY_CONNECT:
                try:
                    s.connect((self.host, self.port))
                except socket.error as error:
                    print('Socket Exception on Connection:{}').format(error)
                    print('Retrying...')
                    retries += 1
            
            if retries > RCONClient.RETRY_CONNECT:
                raise Exception('Could not connect to Palworld Server')
            
            #Attempt RCON Authentication
            auth_request_packet = RCONPacket(RCONPacketType.SERVER_AUTH_REQUEST, self.password)
            auth_empty_packet = RCONPacket(getattr(auth_request_packet,'id')+1, RCONPacketType.SERVER_RESPONSE, '')
            s.send(auth_request_packet.pack())
            s.send(auth_empty_packet.pack())

            auth_response = b''
            while True:
                response = s.recv(RCONClient.MAX_PACKET_SIZE)
                id = struct.unpack('<i', response[4:8])

                if id == getattr(auth_empty_packet,'id'):
                    break
                else:
                    auth_response += response
            auth_response_packet = RCONPacket.unpack(auth_response)

            if not auth_response_packet.isAuthenticated():
                raise Exception('Failed to authenticate with Palworld Server. Please validate password.')

            #Send command
            command_body = RCONClient.get_command_body(input)
            command_request_packet = RCONPacket(RCONPacketType.SERVER_COMMAND_REQUEST, command_body)
            command_empty_packet = RCONPacket(getattr(command_request_packet, 'id')+1,RCONPacketType.SERVER_RESPONSE, '')
            s.send(command_request_packet)
            s.send(command_empty_packet)

            command_response = b''
            while True:
                response = s.recv(RCONClient.MAX_PACKET_SIZE)
                id = struct.unpack('<i', response[4:8])

                if id == getattr(command_empty_packet, 'id'):
                    break
                else:
                    command_response += response
            command_response_packet = RCONPacket.unpack(command_response)
            print(getattr(command_response_packet, 'body'))

    def save(self):
        return self.command(RCONCommands.SAVE.name)
    
    def showPlayers(self):
        return self.command(RCONCommands.SHOWPLAYERS.name)
    
    def info(self):
        return self.command(RCONCommands.INFO.name)
    
    def doExit(self):
        return self.command(RCONCommands.DOEXIT.name)
    
    def banPlayer(self, playerId:str):
        return self.command(RCONCommands.BANPLAYER.name + ' ' + playerId)
    
    def kickPlayer(self, playerId:str):
        return self.command(RCONCommands.KICKPLAYER.name + ' ' + playerId)
    
    def broadcast(self, message:str):
        return self.command(RCONCommands.BROADCAST.name + ' ' + message)
    
    def shutdown(self, time:int, message:str):
        return self.command(RCONCommands.SHUTDOWN.name + ' ' + time + ' ' + message)

    def get_command_body(input:str):
        input = input.lstrip()
        
        if input[0] == '/':
            input = input[1:]

        input_split = input.split(None, 1)
        command = input_split[0].upper()
        
        command = RCONCommands[command]
        args = input_split[1].split(None, command.value[1]-1) if command.value[1] > 0 else None

        body = command.value[0]
        if args is not None:
            for i in range(len(args)):
                args[i] = RCONClient.fix_whitespace(args[i])
                body += ' ' + args[i]

        return body

    def fix_whitespace(input:str):
        return input.replace(' ', u'\u00A0')