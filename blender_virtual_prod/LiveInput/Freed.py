"""
Copyright Miraxyz 2024

Defines how to decode the FreeD protocol
"""

import socket
from threading import Thread
import struct

def unpack(packet):
    if(packet[0] == 0xD1 and len(packet) == 29 ): # freed
        p = int.from_bytes(packet[2:5], 'big', signed=True)
        t = int.from_bytes(packet[5:8], 'big', signed=True)
        r = int.from_bytes(packet[8:11], 'big', signed=True)
        x = int.from_bytes(packet[11:14], 'big', signed=True)
        y = int.from_bytes(packet[14:17], 'big', signed=True)
        z = int.from_bytes(packet[17:20], 'big', signed=True)
        zo = int.from_bytes(packet[20:23], 'big')
        fo = int.from_bytes(packet[23:26], 'big')

        fields = [x,y,z,p,t,r,zo,fo]

        #shift data
        fields[3]/=32768
        fields[4]/=32768
        fields[5]/=32768
        fields[0]/=64
        fields[1]/=64
        fields[2]/=64 
        
        return fields
    return None

        
class FreedReceiver:

    def __init__(self, ip = "0.0.0.0", port = 5000, callback = None):
        self.data = [0,0,0,0,0,0,0,0]
        self.port = port
        self.ip = ip
        self.sock = None
        self.thread = None
        self.isRunning = False
        self.callback = callback

    def start(self):
        self.stop() # try stopping 
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        try:
            self.sock.bind((self.ip, self.port))
        except:
            print("invalid ip adress or port number")
            return
        self.sock.settimeout(1)
        self.isRunning = True
        self.thread = Thread(target=self.run)
        self.thread.start()
       
    #FreeD Receiver
    def run(self):
        while(self.isRunning):
            try:
                msg, _ = self.sock.recvfrom(1024) # buffer size is 1024 bytes
            except:
                continue
             
            if(msg):
                data = unpack(msg)
                if data is not None:
                    self.data = data
                
                if self.callback is not None:
                    self.callback(self.data)

    def stop(self):
        self.isRunning = False
        try:
            self.thread.join()
        except:
            pass
        self.thread = None
        try:
            self.sock.close()
        except:
            pass
        self.sock = None
        self.frequency = 0.0
           