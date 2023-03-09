import gamepad_bridge.gamepad_socket as gpsock
import pickle
from gamepad_bridge.joy import Joy


class GamepadReceiver:
  def __init__(self, host: str, port: int, callback: callable):
    self.host = host
    self.port = port
    self.callback = callback
    self.socket = gpsock.SocketCl(self.host, self.port, self.rcv_callback)

  def rcv_callback(self, data):
    try:
      joy:Joy = pickle.loads(data)
    except pickle.UnpicklingError:
      print("Unpickling error")
      return
    # ensure type of joy
    if not isinstance(joy, Joy):
      print("Not Joy")
      return
    #todo convert to joy
    self.callback(joy)

  def connect(self):
    self.socket.connect()

  def close(self):
    self.socket.close()
  
  def is_running(self) -> bool:
    return self.socket.run

  def tick(self):
    self.socket.tick()

