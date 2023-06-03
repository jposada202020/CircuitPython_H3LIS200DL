# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT
"""
`h3lis200dl`
================================================================================

CircuitPython Driver for the ST H3LIS200DL Accelerometer


* Author(s): Jose D. Montoya


"""

from micropython import const
from adafruit_bus_device import i2c_device
from adafruit_register.i2c_struct import ROUnaryStruct, UnaryStruct
from adafruit_register.i2c_bits import RWBits

try:
    from busio import I2C
    from typing import Tuple
except ImportError:
    pass


__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/jposada202020/CircuitPython_H3LIS200DL.git"

_REG_WHOAMI = const(0x0F)
_CTRL_REG1 = const(0x20)
_CTRL_REG4 = const(0x23)

_ACC_X = const(0x29)
_ACC_Y = const(0x2B)
_ACC_Z = const(0x2D)

_G_TO_ACCEL = 9.80665

POWER_DOWN = const(0b000)
NORMAL_MODE = const(0b001)
LOW_POWER_ODR0_5 = const(0b010)
LOW_POWER_ODR1 = const(0b011)
LOW_POWER_ODR2 = const(0b100)
LOW_POWER_ODR5 = const(0b101)
LOW_POWER_ODR10 = const(0b110)
operation_mode_values = (
    POWER_DOWN,
    NORMAL_MODE,
    LOW_POWER_ODR0_5,
    LOW_POWER_ODR1,
    LOW_POWER_ODR2,
    LOW_POWER_ODR5,
    LOW_POWER_ODR10,
)


SCALE_100G = const(0b0)
SCALE_200G = const(0b1)
full_scale_selection_values = (SCALE_100G, SCALE_200G)
full_scale = {SCALE_100G: 100, SCALE_200G: 200}


class H3LIS200DL:
    """Driver for the H3LIS200DL Sensor connected over I2C.

    :param ~busio.I2C i2c_bus: The I2C bus the H3LIS200DL is connected to.
    :param int address: The I2C device address. Defaults to :const:`0x19`

    :raises RuntimeError: if the sensor is not found

    **Quickstart: Importing and using the device**

    Here is an example of using the :class:`H3LIS200DL` class.
    First you will need to import the libraries to use the sensor

    .. code-block:: python

        import board
        import h3lis200dl

    Once this is done you can define your `board.I2C` object and define your sensor object

    .. code-block:: python

        i2c = board.I2C()  # uses board.SCL and board.SDA
        h3lis200dl = h3lis200dl.H3LIS200DL(i2c)

    Now you have access to the attributes

    .. code-block:: python

    """

    _device_id = ROUnaryStruct(_REG_WHOAMI, "B")
    _ctrl1 = UnaryStruct(_CTRL_REG1, "B")
    _operation_mode = RWBits(3, _CTRL_REG1, 5)
    _full_scale_selection = RWBits(1, _CTRL_REG4, 4)

    # Acceleration Data
    _acc_data_x = UnaryStruct(_ACC_X, "B")
    _acc_data_y = UnaryStruct(_ACC_Y, "B")
    _acc_data_z = UnaryStruct(_ACC_Z, "B")

    def __init__(self, i2c_bus: I2C, address: int = 0x19) -> None:
        self.i2c_device = i2c_device.I2CDevice(i2c_bus, address)

        if self._device_id != 0x32:
            raise RuntimeError("Failed to find H3LIS200DL")

        self._operation_mode = NORMAL_MODE

    @property
    def operation_mode(self) -> str:
        """
        Sensor operation_mode

        +-----------------------------------------+-------------------+
        | Mode                                    | Value             |
        +=========================================+===================+
        | :py:const:`h3lis200dl.POWER_DOWN`       | :py:const:`0b000` |
        +-----------------------------------------+-------------------+
        | :py:const:`h3lis200dl.NORMAL_MODE`      | :py:const:`0b001` |
        +-----------------------------------------+-------------------+
        | :py:const:`h3lis200dl.LOW_POWER_ODR0_5` | :py:const:`0b010` |
        +-----------------------------------------+-------------------+
        | :py:const:`h3lis200dl.LOW_POWER_ODR1`   | :py:const:`0b011` |
        +-----------------------------------------+-------------------+
        | :py:const:`h3lis200dl.LOW_POWER_ODR2`   | :py:const:`0b100` |
        +-----------------------------------------+-------------------+
        | :py:const:`h3lis200dl.LOW_POWER_ODR5`   | :py:const:`0b101` |
        +-----------------------------------------+-------------------+
        | :py:const:`h3lis200dl.LOW_POWER_ODR10`  | :py:const:`0b110` |
        +-----------------------------------------+-------------------+
        """
        values = (
            "POWER_DOWN",
            "NORMAL_MODE",
            "LOW_POWER_ODR0_5",
            "LOW_POWER_ODR1",
            "LOW_POWER_ODR2",
            "LOW_POWER_ODR5",
            "LOW_POWER_ODR10",
        )
        return values[self._operation_mode]

    @operation_mode.setter
    def operation_mode(self, value: int) -> None:
        if value not in operation_mode_values:
            raise ValueError("Value must be a valid operation_mode setting")
        self._operation_mode = value

    @property
    def acceleration(self) -> Tuple[int, int, int]:
        """
        Accelertion property
        :return: Acceleration data
        """

        x = (
            self._twos_comp(self._acc_data_x, 7)
            * full_scale[self._full_scale_selection]
            / 128
        )
        y = (
            self._twos_comp(self._acc_data_y, 7)
            * full_scale[self._full_scale_selection]
            / 128
        )
        z = (
            self._twos_comp(self._acc_data_z, 7)
            * full_scale[self._full_scale_selection]
            / 128
        )
        return x, y, z

    @property
    def full_scale_selection(self) -> str:
        """
        Sensor full_scale_selection

        +-----------------------------------+-----------------+
        | Mode                              | Value           |
        +===================================+=================+
        | :py:const:`h3lis200dl.SCALE_100G` | :py:const:`0b0` |
        +-----------------------------------+-----------------+
        | :py:const:`h3lis200dl.SCALE_200G` | :py:const:`0b1` |
        +-----------------------------------+-----------------+
        """
        values = (
            "SCALE_100G",
            "SCALE_200G",
        )
        return values[self._full_scale_selection]

    @full_scale_selection.setter
    def full_scale_selection(self, value: int) -> None:
        if value not in full_scale_selection_values:
            raise ValueError("Value must be a valid full_scale_selection setting")
        self._full_scale_selection = value

    @staticmethod
    def _twos_comp(val: int, bits: int) -> int:
        if val & (1 << (bits - 1)) != 0:
            return val - (1 << bits)
        return val
