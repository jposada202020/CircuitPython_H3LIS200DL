# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import time
import board
import h3lis200dl

i2c = board.I2C()  # uses board.SCL and board.SDA
h3lis = h3lis200dl.H3LIS200DL(i2c)

while True:
    accx, accy, accz = h3lis.acceleration
    print(f"x:{accx:.2f}g, y:{accy:.2f}g, z{accz:.2f}g")
    print()
    time.sleep(0.5)
