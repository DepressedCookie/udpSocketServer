# server.py

import random
import socket
import time
from _thread import *
import threading
from datetime import datetime
import json

clients_lock = threading.Lock()
connected = 0

clients = {}

def connectionLoop(sock):
   while True:
      data, addr = sock.recvfrom(1024)
      allPlayers = {"cmd": 3, "players": []}
      if addr in clients:
         if 'heartbeat' in str(data):
            clients[addr]['lastBeat'] = datetime.now()
         else:
            clients[addr]['location'] = json.loads(data)
            print(clients[addr]['location'])
      else:
         if 'connect' in str(data):
            clients[addr] = {}
            clients[addr]['lastBeat'] = datetime.now()
            clients[addr]['location'] = {'x':0,'y':0,'z':0}
            
            message = {"cmd": 0,"player":{"id":str(addr)}}
            m = json.dumps(message)
            for c in clients:
               player = {}
               player['id'] = str(c)
               allPlayers['players'].append(player)
               sock.sendto(bytes(m,'utf8'), (c[0],c[1]))


            AP = json.dumps(allPlayers)
            sock.sendto(bytes(AP,'utf8'), (addr[0],addr[1]))


def cleanClients(sock):
   while True:
      for c in list(clients.keys()):
         if (datetime.now() - clients[c]['lastBeat']).total_seconds() > 5:
            #print('Dropped Client: ', c)
            clients_lock.acquire()
            del clients[c]
            clients_lock.release()

            message = {"cmd": 2,"player":{"id":str(c)}}
            m = json.dumps(message)
            for p in clients:
               sock.sendto(bytes(m,'utf8'), (p[0],p[1]))

      time.sleep(1)

def gameLoop(sock):
   while True:
      GameState = {"cmd": 1, "players": []}
      clients_lock.acquire()
      #print (clients)
      for c in clients:
         player = {}
         player['id'] = str(c)
         
         player['location'] = clients[c]['location']
         GameState['players'].append(player)
      s=json.dumps(GameState)
      #print(s)
      for c in clients:
         sock.sendto(bytes(s,'utf8'), (c[0],c[1]))
      clients_lock.release()
      time.sleep(1.0/30.0)

def main():
   port = 12345
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   s.bind(('', port))
   start_new_thread(gameLoop, (s,))
   start_new_thread(connectionLoop, (s,))
   start_new_thread(cleanClients,(s,))
   while True:
      time.sleep(1)

if __name__ == '__main__':
   main()
