import socket
import threading as thrd
import contextlib
import time


class SocketSrv:
  """_summary_
  example:
  def main():

  srv = SocketSrv("localhost", 1337)
  srv.start()
  
  signal.signal(signal.SIGINT, lambda x, y: srv.close())

  while srv.run:
    srv.send_to_all(b"Hello World")
    time.sleep(0.25)

  """
  def __init__(self, host: str, port: int) -> None:
    self.host = host
    self.port = port
    self.clients = {}
    self.run = True
    self.lock = thrd.Lock() #mutex for clients

    self.read_callback = None

  #start accepting threads
  def start(self) -> None:
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.bind((self.host, self.port))
    self.socket.listen()
    print("start thread")
    self.accept_thread = thrd.Thread(target=self.thrd_accept)
    self.accept_thread.start()

  def thrd_accept(self) -> None:
    print("entering accept thread")
    while(self.run):
      try:
        conn, addr = self.socket.accept()
      except socket.error:
        print("Connection lost")
        break
      self.lock.acquire()
      self.clients[addr] = conn
      self.lock.release()
      print(f"Connected by {addr}")

    #stop 
    print("Stopping")
    self.lock.acquire()
    for addr, conn in self.clients.items():
      print(f"Closing connection to {addr}")
      conn.shutdown(socket.SHUT_RDWR)
      conn.close()
    self.lock.release()


  def close(self) -> None:
    self.run = False
    # self.socket.shutdown(socket.SHUT_RDWR)
    self.socket.close()


  def send_to_all(self, data: bytes) -> None:
    self.lock.acquire()
    addr_to_remove = []
    for addr, conn in self.clients.items():
      co: socket.socket = conn
      try:
        co.sendall(data)
      except socket.error:
        print("Connection lost")
        co.close()
        addr_to_remove.append(addr)

    #remove dead connections
    for addr in addr_to_remove:
      self.clients.pop(addr)

    self.lock.release()


  def send_to(self) -> None: #todo
    pass

  def client_count(self) -> int:
    return len(self.clients)

  def get_clients(self) -> dict:
    return self.clients

  
  # call read callback and stuff
  def tick(self) -> None:
    pass




#####################################################
# client #
##########




class SocketCl:
  """
  
  example: 

  def main():
  def callback(data: bytes):
    print(data)

  cl = SocketCl("localhost", 1337, callback)

  cl.connect()

  signal.signal(signal.SIGINT, lambda x, y: cl.close())

  while cl.run:
    cl.tick()
    time.sleep(0.01)
  
  """
  def __init__(self, host: str, port: int, callback: callable):
    self.host = host
    self.port = port
    self.socket: socket.socket = None
    self.run = False
    self.do_reconnect = True

    self.read_callback: callable = callback

    self.last_data = None

  def connect(self) -> None:


    connected = False
    while not connected:
      try:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        connected = True
      except ConnectionRefusedError:
        if self.do_reconnect is False:
          return
        print("Connection refused will retry in 1s")
        time.sleep(1)
    print("Connected")
    if self.run is False:
      self.run = True
      self.read_thread = thrd.Thread(target=self.thrd_read)
      self.read_thread.start()

  def thrd_read(self) -> None:
    print("entering read thread")
    while self.run:
      # print("reading")
      try:
        self.last_data = self.socket.recv(1024)
      except socket.error:
        print("Connection lost in recv")
        self.last_data = None

      #check if ok
      if self.last_data is None or len(self.last_data) == 0:
        print("Connection lost")
        self.last_data = None
        if self.run is True:
          with contextlib.suppress(Exception):
            self.socket.shutdown(socket.SHUT_RDWR)
          self.socket.close()
           #reconnect
          self.connect()
      

      # print("--")
      # print(type(self.last_data))
      # # print(len(self.last_data))
      # print(self.last_data)
      # print("++")

  def close(self) -> None:
    print("closing")
    self.run = False
    self.do_reconnect = False
    with contextlib.suppress(Exception):
      self.socket.shutdown(socket.SHUT_RDWR)
    self.socket.close() # todo check if blocking recv is interrupted


  def send(self, data: bytes) -> None:
    # self.socket.sendall(data)
    print("not implemented")

  def tick(self) -> None:
    if self.last_data is not None:
      self.read_callback(self.last_data)
      self.last_data = None
