# The MIT License (MIT)
#
# Copyright (c) 2016 Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import struct


# Minimal constants carried over from Arduino library:
LSM303_ADDRESS_ACCEL = (0x32 >> 1)  # 0011001x
LSM303_ADDRESS_MAG   = (0x3C >> 1)  # 0011110x
                                         # Default    Type
LSM303_REGISTER_ACCEL_CTRL_REG1_A = 0x20 # 00000111   rw
LSM303_REGISTER_ACCEL_CTRL_REG4_A = 0x23 # 00000000   rw
LSM303_REGISTER_ACCEL_OUT_X_L_A   = 0x28
LSM303_REGISTER_MAG_CRA_REG_M     = 0x00
LSM303_REGISTER_MAG_CRB_REG_M     = 0x01
LSM303_REGISTER_MAG_MR_REG_M      = 0x02
LSM303_REGISTER_MAG_OUT_X_H_M     = 0x03

# Gain settings for set_mag_gain()
LSM303_MAGGAIN_1_3 = 0x20 # +/- 1.3
LSM303_MAGGAIN_1_9 = 0x40 # +/- 1.9
LSM303_MAGGAIN_2_5 = 0x60 # +/- 2.5
LSM303_MAGGAIN_4_0 = 0x80 # +/- 4.0
LSM303_MAGGAIN_4_7 = 0xA0 # +/- 4.7
LSM303_MAGGAIN_5_6 = 0xC0 # +/- 5.6
LSM303_MAGGAIN_8_1 = 0xE0 # +/- 8.1
# Accelerometer resolution settings
LSM303_ACCEL_1_MG_PER_LSB = 0
LSM303_ACCEL_2_MG_PER_LSB = 1
LSM303_ACCEL_4_MG_PER_LSB = 2
LSM303_ACCEL_12_MG_PER_LSB = 3
# Accelerometer data rate settings
LSM303_ACCEL_RATE_POWER_DOWN = 0
LSM303_ACCEL_RATE_1_HZ = 1
LSM303_ACCEL_RATE_10_HZ = 2
LSM303_ACCEL_RATE_25_HZ = 3
LSM303_ACCEL_RATE_50_HZ = 4
LSM303_ACCEL_RATE_100_HZ = 5
LSM303_ACCEL_RATE_200_HZ = 6
LSM303_ACCEL_RATE_400_HZ = 7
LSM303_ACCEL_RATE_1_620_KHZ = 8 # low power mode
LSM303_ACCEL_RATE_5_376_KHZ = 9 # low power mode
LSM303_ACCEL_RATE_1_344_KHZ = 9 # normal mode
# Magnetometer data rate settings
LSM303_MAG_RATE_0_75_HZ = 0
LSM303_MAG_RATE_1_5_HZ = 1
LSM303_MAG_RATE_3_HZ = 2
LSM303_MAG_RATE_7_5_HZ = 3
LSM303_MAG_RATE_15_HZ = 4
LSM303_MAG_RATE_30_HZ = 5
LSM303_MAG_RATE_75_HZ = 6
LSM303_MAG_RATE_220_HZ = 7


class LSM303(object):
    """LSM303 accelerometer & magnetometer."""

    def __init__(self, hires=True, accel_address=LSM303_ADDRESS_ACCEL,
                 mag_address=LSM303_ADDRESS_MAG, i2c=None, **kwargs):
        """Initialize the LSM303 accelerometer & magnetometer.  The hires
        boolean indicates if high resolution (12-bit) mode vs. low resolution
        (10-bit, faster and lower power) mode should be used.
        """
        # Setup I2C interface for accelerometer and magnetometer.
        if i2c is None:
            import Adafruit.Adafruit_GPIO.I2C as I2C
            i2c = I2C
        self._accel = i2c.get_i2c_device(accel_address, **kwargs)
        self._mag = i2c.get_i2c_device(mag_address, **kwargs)
        # Enable the accelerometer
        self._accel.write8(LSM303_REGISTER_ACCEL_CTRL_REG1_A, 0x27)
        # Select hi-res (12-bit) or low-res (10-bit) output mode.
        # Low-res mode uses less power and sustains a higher update rate,
        # output is padded to compatible 12-bit units.
        if hires:
            self._accel.write8(LSM303_REGISTER_ACCEL_CTRL_REG4_A, 0b00001000)
        else:
            self._accel.write8(LSM303_REGISTER_ACCEL_CTRL_REG4_A, 0)
        # Enable the magnetometer
        self._mag.write8(LSM303_REGISTER_MAG_MR_REG_M, 0x00)

    def read(self):
        """Read the accelerometer and magnetometer value.  A tuple of tuples will
        be returned with:
          ((accel X, accel Y, accel Z), (mag X, mag Y, mag Z))
        """
        # Read the accelerometer as signed 16-bit little endian values.
        accel_raw = self._accel.readList(LSM303_REGISTER_ACCEL_OUT_X_L_A | 0x80, 6)
        accel = struct.unpack('<hhh', accel_raw)
        # Convert to 12-bit values by shifting unused bits.
        accel = (accel[0] >> 4, accel[1] >> 4, accel[2] >> 4)
        # Read the magnetometer.
        # Note that for some reason the LSM303 returns data in (X,Z,Y) order
        mag_raw = self._mag.readList(LSM303_REGISTER_MAG_OUT_X_H_M, 6)
        magX, magZ, magY = struct.unpack('>hhh', mag_raw)
        reordered_mag = magX, magY, magZ
        return (accel, reordered_mag)

    def read_accelerometer(self):
        """
        Read the accelerometer value. A tuple will be returned with:
          (accel_x, accel_y, accel_z)
        """
        accel_raw = self._accel.readList(LSM303_REGISTER_ACCEL_OUT_X_L_A | 0x80, 6)
        accel = struct.unpack('<hhh', accel_raw)
        accel = (accel[0] >> 4, accel[1] >> 4, accel[2] >> 4)
        return accel

    def set_accelerometer_resolution(self, resolution):
        """
        Set the full scale resolution of the accelerometer.
        """
        reg4_a = self._accel.readU8(LSM303_REGISTER_ACCEL_CTRL_REG4_A)
        reg4_a = (reg4_a & 0xC0) + ((resolution & 0x03) << 4) + (reg4_a & 0x0F)
        self._accel.write8(LSM303_REGISTER_ACCEL_CTRL_REG4_A, reg4_a)

    def set_accelerometer_datarate(self, datarate):
        """
        Set the linear acceleratio data rate.
        """
        reg1_a = self._accel.readU8(LSM303_REGISTER_ACCEL_CTRL_REG1_A)
        reg1_a = ((datarate & 0x0F) << 4) + reg1_a
        self._accel.write8(LSM303_REGISTER_ACCEL_CTRL_REG1_A, reg1_a)

    def read_magnetometer(self):
        """
        Read the magnetometer value. A tuple will be returned with:
          (mag_x, mag_y, mag_z)
        """
        mag_raw = self._mag.readList(LSM303_REGISTER_MAG_OUT_X_H_M, 6)
        magX, magZ, magY = struct.unpack('>hhh', mag_raw)
        return (magX, magY, magZ)

    def set_magnetometer_datarate(self, datarate):
        """
        Set the magnetometer's rate of measurement.
        """
        reg_value = self._mag.readU8(LSM303_REGISTER_MAG_CRA_REG_M)
        reg_value = (reg_value & 0x80) + ((datarate & 0x07) << 2)
        self._mag.write8(LSM303_REGISTER_MAG_CRA_REG_M, reg_value)

    def set_mag_gain(self, gain=LSM303_MAGGAIN_1_3):
        """Set the magnetometer gain.  Gain should be one of the following
        constants:
         - LSM303_MAGGAIN_1_3 = +/- 1.3 (default)
         - LSM303_MAGGAIN_1_9 = +/- 1.9
         - LSM303_MAGGAIN_2_5 = +/- 2.5
         - LSM303_MAGGAIN_4_0 = +/- 4.0
         - LSM303_MAGGAIN_4_7 = +/- 4.7
         - LSM303_MAGGAIN_5_6 = +/- 5.6
         - LSM303_MAGGAIN_8_1 = +/- 8.1
        """
        self._mag.write8(LSM303_REGISTER_MAG_CRB_REG_M, gain)
