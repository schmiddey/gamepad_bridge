"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following lines in the
``[options.entry_points]`` section in ``setup.cfg``::

    console_scripts =
         fibonacci = gamepad_bridge.skeleton:run

Then run ``pip install .`` (or ``pip install -e .`` for editable mode)
which will install the command ``fibonacci`` inside your current environment.

Besides console scripts, the header (i.e. until ``_logger``...) of this file can
also be used as template for Python modules.

Note:
    This file can be renamed depending on your needs or safely removed if not needed.

References:
    - https://setuptools.pypa.io/en/latest/userguide/entry_point.html
    - https://pip.pypa.io/en/stable/reference/pip_install
"""

import argparse
import argcomplete
import logging
import sys
import time

import gamepad_bridge.gamepad_socket as gpsock
from gamepad_bridge.joy_ps4 import JoyPS4
from gamepad_bridge.gamepad_rcv import GamepadReceiver
import hid
import pickle 
import signal

from gamepad_bridge import __version__

__author__ = "schmiddey"
__copyright__ = "schmiddey"
__license__ = "BSD 3-Clause"

_logger = logging.getLogger(__name__)



# ---- CLI ----
# The functions defined in this section are wrappers around the main Python
# API allowing them to be called directly from the terminal as a CLI
# executable/script.


def parse_args(args):
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(description="gamepad socket bridge")


    parser.add_argument(
        "--version",
        action="version",
        version=f"gamepad_bridge {__version__}",
    )

    parser.add_argument(
      "-l",
      "--list",
      dest="list",
      help="list devices",
      action="store_true",
    )

    parser.add_argument(
      "-ds",
      "--device-string",
      dest="device_str",
      help="part of a device string, should be unique -> otherwise first match will be used",
      action="store",
      default="DUALSHOCK"
    )

    parser.add_argument(
      "-p",
      "--port",
      dest="port",
      help="port to send to, default: 1336",
      action="store",
      default=1336
    )

    parser.add_argument(
      "-ho",
      "--host",
      dest="host",
      help="host of this machine, default: localhost",
      action="store",
      default="localhost"
    )

    #add rate
    parser.add_argument(
      "-r",
      "--rate",
      dest="rate",
      help="rate of sending data, default: 30",
      action="store",
      default=50
    )

    #add -cl for client
    parser.add_argument(
      "-cl",
      "--client",
      dest="client",
      help="run as client",
      action="store_true",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )

    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )
    
    argcomplete.autocomplete(parser)

    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def main(args):

  args = parse_args(args)
  setup_logging(args.loglevel)
  _logger.debug("Starting crazy calculations...")



  if args.list:
    print("Listing devices with valid product_string:")
    for device in hid.enumerate():
      if device['product_string'] == '':
        continue
      print(f"{device['vendor_id']:04}:{device['product_id']:04} {device['product_string']}")
    exit(0)
  
  # print(f"used device_string: {args.device_str}")
  # exit(0)

  #params
  p_delay = 1.0/int(args.rate)
  p_port = int(args.port)
  p_host = args.host
  p_device_str = args.device_str

  print("-- params --")
  print(f"delay: {p_delay}")
  print(f"port: {p_port}")
  print(f"host: {p_host}")
  print(f"device_str: {p_device_str}")
  print("------------")

  if args.client:
    print("Starting client and dumping data to stdout")

    def joy_callback(joy: JoyPS4):
      joy.print_data()


    rcv = GamepadReceiver(p_host, p_port, joy_callback)
    rcv.connect()

    signal.signal(signal.SIGINT, lambda x, y: rcv.close())

    while rcv.is_running():
      rcv.tick()
      time.sleep(0.01)
    

    exit(0)

  #find device
  def find_device(device_str: str) -> hid.device:
    devices = hid.enumerate()
    controller_id = None
    controller_vendor = None
    for e in devices:
      # print(f"{e['product_string']}")
      if p_device_str in e['product_string']:
        controller_id = e['product_id']
        controller_vendor = e['vendor_id']
        break
    if controller_id is None:
      return None
    #valid device
    device = hid.device()
    device.open(controller_vendor, controller_id)
    device.set_nonblocking(True)
    return device
  

  srv = gpsock.SocketSrv(p_host, p_port)
  srv.start()

  signal.signal(signal.SIGINT, lambda x, y: srv.close())

  gamepad = None
  while srv.run:
    if gamepad is None:
      gamepad = find_device(p_device_str)
      if gamepad is None:
        print("No device found, retrying in 1s")
        time.sleep(1)
        continue
      print("Device found")
    try:
      rdy = False 
      #read untill no data is available
      while not rdy:
        if report:=gamepad.read(64):
          joy = JoyPS4()
          joy.from_list(report)
          # joy.print_data()
          srv.send_to_all(pickle.dumps(joy))
        else:
          rdy = True
    except OSError:
      print("Device disconnected")
      gamepad = None
      continue
    time.sleep(p_delay) 

  

  _logger.info("Script ends here")


def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    # ^  This is a guard statement that will prevent the following code from
    #    being executed in the case someone imports this file instead of
    #    executing it as a script.
    #    https://docs.python.org/3/library/__main__.html

    # After installing your project with pip, users can also run your Python
    # modules as scripts via the ``-m`` flag, as defined in PEP 338::
    #
    #     python -m gamepad_bridge.skeleton 42
    #
    run()
