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

import pygame
import pickle
from gamepad_bridge.joy_ps4 import JoyPS4
import gamepad_bridge.gamepad_socket as gpsock
import logging
import argparse
import argcomplete
import sys

pygame.init()

_logger = logging.getLogger(__name__)

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
      "-p",
      "--port",
      dest="port",
      help="port to send to, default: 1336",
      action="store",
      default=1336
    )

    parser.add_argument(
      "-d",
      "--deadzone",
      dest="deadzone",
      help="deadzone of the sticks, default: 0.01",
      action="store",
      default=0.1
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

def deadzone(value, deadzone):
    constrain = lambda x: min(1.0 , max(-1.0, x))
    value = constrain(value)

    if value < deadzone and value > -deadzone:
        return 0.0
    elif value > 0:
        value -= deadzone
    else:
        value += deadzone

    return value / (1.0 - deadzone)

def main(args):
    args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.debug("Starting crazy calculations...")

    #params
    p_rate = int(args.rate)
    p_port = int(args.port)
    p_host = args.host
    p_deadzone = float(args.deadzone)

    print("-- params --")
    print(f"delay: {p_rate}")
    print(f"port: {p_port}")
    print(f"host: {p_host}")
    print(f"deadzone: {p_deadzone}")
    print("------------")

    # Used to manage how fast the screen updates.
    clock = pygame.time.Clock()

    srv = gpsock.SocketSrv(p_host, p_port)
    srv.start()

    joyPS4Data = JoyPS4()

    done = False
    joystick = None
    while not done:
        # Event processing step.
        # Possible joystick events: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
        # JOYBUTTONUP, JOYHATMOTION, JOYDEVICEADDED, JOYDEVICEREMOVED
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True  # Flag that we are done so we exit this loop.

            # Handle hotplugging
            if event.type == pygame.JOYDEVICEADDED:
                # This event will be generated when the program starts for every
                # joystick, filling up the list without needing to create them manually.
                if joystick is None:
                    joystick = pygame.joystick.Joystick(event.device_index)
                    joystick.rumble(0, 0.7, 500)
                    print(f"Joystick {joystick.get_instance_id()} connencted")

            if event.type == pygame.JOYDEVICEREMOVED:
                if(event.instance_id == joystick.get_instance_id()):
                    joystick = None
                    print(f"Joystick {event.instance_id} disconnected")
        
        if joystick is not None:            
            joyPS4Data.stick_l_x = deadzone(joystick.get_axis(0), p_deadzone) 
            joyPS4Data.stick_l_y = deadzone(joystick.get_axis(1), p_deadzone)

            joyPS4Data.trigger_l = deadzone(joystick.get_axis(2), p_deadzone) 
            
            joyPS4Data.stick_r_x = deadzone(joystick.get_axis(3), p_deadzone) 
            joyPS4Data.stick_r_y = deadzone(joystick.get_axis(4), p_deadzone) 
            
            joyPS4Data.trigger_r = deadzone(joystick.get_axis(5), p_deadzone) 


            joyPS4Data.btn_a = joystick.get_button(0)
            joyPS4Data.btn_b = joystick.get_button(1)
            joyPS4Data.btn_x = joystick.get_button(2)
            joyPS4Data.btn_y = joystick.get_button(3)


            joyPS4Data.btn_l1 = joystick.get_button(4)
            joyPS4Data.btn_r1 = joystick.get_button(5)
            joyPS4Data.btn_l2 = joystick.get_button(6)
            joyPS4Data.btn_r2 = joystick.get_button(7)

            joyPS4Data.btn_share = joystick.get_button(8)
            joyPS4Data.btn_options = joystick.get_button(9)
            # = joystick.get_button(10)

            joyPS4Data.btn_stick_l = joystick.get_button(11)
            joyPS4Data.btn_stick_r = joystick.get_button(12)

            hat = joystick.get_hat(0)
            joyPS4Data.btn_left = hat[0] == -1
            joyPS4Data.btn_right = hat[0] == 1
            joyPS4Data.btn_down = hat[1] == -1
            joyPS4Data.btn_up = hat[1] == 1
            
            if _logger.level == logging.DEBUG:
              joyPS4Data.print_data()

            srv.send_to_all(pickle.dumps(joyPS4Data))

        # Limit to rate
        clock.tick(p_rate)

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
