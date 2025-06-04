"""Arduino communication utilities.

This package provides the :class:`ArduinoComm` class and the
``send_rotation_command`` helper for sending rotation commands to the
Arduino controller. Importing them here allows consumers to simply do::

    from arduino_comm import ArduinoComm, send_rotation_command
"""

from .arduino_comm import ArduinoComm, send_rotation_command

__all__ = ["ArduinoComm", "send_rotation_command"]
