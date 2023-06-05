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
from adafruit_register.i2c_bit import RWBit

try:
    from busio import I2C
    from typing import Tuple
except ImportError:
    pass


__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/jposada202020/CircuitPython_H3LIS200DL.git"

_REG_WHOAMI = const(0x0F)
_CTRL_REG1 = const(0x20)
_CTRL_REG2 = const(0x21)
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

RATE_50HZ = const(0b00)
RATE_100HZ = const(0b01)
RATE_400HZ = const(0b10)
RATE_1000HZ = const(0b11)
data_rate_values = (RATE_50HZ, RATE_100HZ, RATE_400HZ, RATE_1000HZ)

# Axis Enabled Values
X_DISABLED = const(0b0)
X_ENABLED = const(0b1)
Y_DISABLED = const(0b0)
Y_ENABLED = const(0b1)
Z_DISABLED = const(0b0)
Z_ENABLED = const(0b1)
axis_enabled_values = (X_DISABLED, X_ENABLED)

SCALE_100G = const(0b0)
SCALE_200G = const(0b1)
full_scale_selection_values = (SCALE_100G, SCALE_200G)
full_scale = {SCALE_100G: 100, SCALE_200G: 200}

FILTER_NORMAL_MODE = const(0b00)
FILTER_SIGNAL_FILTERING = const(0b01)
high_pass_filter_mode_values = (FILTER_NORMAL_MODE, FILTER_SIGNAL_FILTERING)


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

    # Acceleration Data
    _acc_data_x = UnaryStruct(_ACC_X, "B")
    _acc_data_y = UnaryStruct(_ACC_Y, "B")
    _acc_data_z = UnaryStruct(_ACC_Z, "B")

    _full_scale_selection = RWBits(1, _CTRL_REG4, 4)

    # Register CTRL_REG1 (0x20)
    # |PM2|PM1|PM0|DR1|DR0|Zen|Yen|Xen|
    _operation_mode = RWBits(3, _CTRL_REG1, 5)
    _data_rate = RWBits(2, _CTRL_REG1, 3)
    _z_enabled = RWBit(_CTRL_REG1, 2)
    _y_enabled = RWBit(_CTRL_REG1, 1)
    _x_enabled = RWBit(_CTRL_REG1, 0)

    # Register CTRL_REG2 (0x21)
    # |BOOT|HPM1|HPM0|FDS|HPen2|HPen1|HPCF1|HPCF0|
    _high_pass_filter_mode = RWBits(2, _CTRL_REG2, 5)

    def __init__(self, i2c_bus: I2C, address: int = 0x19) -> None:
        self.i2c_device = i2c_device.I2CDevice(i2c_bus, address)

        if self._device_id != 0x32:
            raise RuntimeError("Failed to find H3LIS200DL")

        self._operation_mode = NORMAL_MODE
        self._memory_full_scale_selection = self._operation_mode

    @property
    def operation_mode(self) -> str:
        """
        Sensor operation_mode allow the user to select between power-down and two
        operating active modes. The device is in power-down mode when the PD bits
        are set to “000” (default value after boot). Table shows all the possible
        power mode configurations and respective output data rates. Output data
        in the low-power mode are computed with the low-pass filter cutoff frequency
        defined by the :attr:`data_rate`

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
    def acceleration(self) -> Tuple[float, float, float]:
        """
        Acceleration property
        :return: Acceleration data
        """

        x = (
            self._twos_comp(self._acc_data_x, 7)
            * full_scale[self._memory_full_scale_selection]
            / 128
        )
        y = (
            self._twos_comp(self._acc_data_y, 7)
            * full_scale[self._memory_full_scale_selection]
            / 128
        )
        z = (
            self._twos_comp(self._acc_data_z, 7)
            * full_scale[self._memory_full_scale_selection]
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
        self._memory_full_scale_selection = value

    @staticmethod
    def _twos_comp(val: int, bits: int) -> int:
        if val & (1 << (bits - 1)) != 0:
            return val - (1 << bits)
        return val

    @property
    def x_enabled(self) -> str:
        """
        Sensor x_enabled
        In order to optimize further power consumption of the h3lis200dl, data evaluation
        of individual axes can be deactivated. Per default, all three axes are active.

        +-----------------------------------+-----------------+
        | Mode                              | Value           |
        +===================================+=================+
        | :py:const:`h3lis200dl.X_DISABLED` | :py:const:`0b0` |
        +-----------------------------------+-----------------+
        | :py:const:`h3lis200dl.X_ENABLED`  | :py:const:`0b1` |
        +-----------------------------------+-----------------+
        """
        values = (
            "X_DISABLED",
            "X_ENABLED",
        )
        return values[self._x_enabled]

    @x_enabled.setter
    def x_enabled(self, value: int) -> None:
        if value not in axis_enabled_values:
            raise ValueError("Value must be a valid x_enabled setting")
        self._x_enabled = value

    @property
    def y_enabled(self) -> str:
        """
        Sensor y_enabled
        In order to optimize further power consumption of the h3lis200dl, data evaluation
        of individual axes can be deactivated. Per default, all three axes are active.

        +-----------------------------------+-----------------+
        | Mode                              | Value           |
        +===================================+=================+
        | :py:const:`h3lis200dl.Y_DISABLED` | :py:const:`0b0` |
        +-----------------------------------+-----------------+
        | :py:const:`h3lis200dl.Y_ENABLED`  | :py:const:`0b1` |
        +-----------------------------------+-----------------+
        """
        values = (
            "Y_DISABLED",
            "Y_ENABLED",
        )
        return values[self._y_enabled]

    @y_enabled.setter
    def y_enabled(self, value: int) -> None:
        if value not in axis_enabled_values:
            raise ValueError("Value must be a valid y_enabled setting")
        self._y_enabled = value

    @property
    def z_enabled(self) -> str:
        """
        Sensor z_enabled
        In order to optimize further power consumption of the h3lis200dl, data evaluation
        of individual axes can be deactivated. Per default, all three axes are active.

        +-----------------------------------+-----------------+
        | Mode                              | Value           |
        +===================================+=================+
        | :py:const:`h3lis200dl.Z_DISABLED` | :py:const:`0b0` |
        +-----------------------------------+-----------------+
        | :py:const:`h3lis200dl.Z_ENABLED`  | :py:const:`0b1` |
        +-----------------------------------+-----------------+
        """
        values = (
            "Z_DISABLED",
            "Z_ENABLED",
        )
        return values[self._z_enabled]

    @z_enabled.setter
    def z_enabled(self, value: int) -> None:
        if value not in axis_enabled_values:
            raise ValueError("Value must be a valid z_enabled setting")
        self._z_enabled = value

    @property
    def data_rate(self) -> str:
        """
        Sensor data_rate selects the data rate at which acceleration samples
        are produced. In low-power modes they define the output data resolution.
        Table shows all the possible configurations

        +------------------------------------+------------------+
        | Mode                               | Value            |
        +====================================+==================+
        | :py:const:`h3lis200dl.RATE_50HZ`   | :py:const:`0b00` |
        +------------------------------------+------------------+
        | :py:const:`h3lis200dl.RATE_100HZ`  | :py:const:`0b01` |
        +------------------------------------+------------------+
        | :py:const:`h3lis200dl.RATE_400HZ`  | :py:const:`0b10` |
        +------------------------------------+------------------+
        | :py:const:`h3lis200dl.RATE_1000HZ` | :py:const:`0b11` |
        +------------------------------------+------------------+
        """
        values = ("RATE_50HZ", "RATE_100HZ", "RATE_400HZ", "RATE_1000HZ")
        return values[self._data_rate]

    @data_rate.setter
    def data_rate(self, value: int) -> None:
        if value not in data_rate_values:
            raise ValueError("Value must be a valid data_rate setting")
        self._data_rate = value

    @property
    def high_pass_filter_mode(self) -> str:
        """
        Sensor high_pass_filter_mode used to configure the high-pass filter cutoff
        frequency ft which is given by:

        .. math::

            f_{t}= \\frac{f_{s}}{6*HP_{c}}


        +------------------------------------------------+------------------+
        | Mode                                           | Value            |
        +================================================+==================+
        | :py:const:`h3lis200dl.FILTER_NORMAL_MODE`      | :py:const:`0b00` |
        +------------------------------------------------+------------------+
        | :py:const:`h3lis200dl.FILTER_SIGNAL_FILTERING` | :py:const:`0b01` |
        +------------------------------------------------+------------------+
        """
        values = ("FILTER_NORMAL_MODE", "FILTER_SIGNAL_FILTERING")
        return values[self._high_pass_filter_mode]

    @high_pass_filter_mode.setter
    def high_pass_filter_mode(self, value: int) -> None:
        if value not in high_pass_filter_mode_values:
            raise ValueError("Value must be a valid high_pass_filter_mode setting")
        self._high_pass_filter_mode = value
