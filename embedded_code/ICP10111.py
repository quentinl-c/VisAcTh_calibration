from time import sleep

class ICP10111():
    """
        Class to read the ICP10111 sensor
        Adapted from: https://github.com/pimoroni/icp10125-python/blob/main/library/icp10125/__init__.py (from datasheets of ICP-10111 abd personnal modifications)
    """

    DEFAULT_I2C_ADDRESS = 0x63
    READ_OTP = bytes([0xC7, 0xF7])
    OTP_ADDRESS = bytes([0xC5, 0x95, 0x00, 0x66, 0x9C])
    SOFT_RESET = bytes([0x80, 0x5D])
    NORMAL_T_FIRST = bytes([0x68, 0x25])
    READ_ID = bytes([0xEF, 0xC8])

    NORMAL = 0x6825
    LOW_POWER = 0x609C
    LOW_NOISE = 0x70DF
    ULTRA_LOW_NOISE = 0x7866

    NORMAL_P_FIRST = 0x48A3
    LOW_POWER_T_FIRST = 0x609C
    LOW_POWER_P_FIRST = 0x401A
    LOW_NOISE_T_FIRST = 0x70DF
    LOW_NOISE_P_FIRST = 0x5059
    ULN_T_FIRST = 0x7866
    ULN_P_FIRST = 0x58E0

    MOVE_ADDRESS_PTR = 0xC595

    CHIP_ID = 0x08

    I2C_WAIT_TIME = 0.025

    MEASUREMENT_DELAYS = {
        NORMAL: 7,  # 5.6 to 6.3ms
        LOW_POWER: 2,  # 1.6 to 1.8ms
        LOW_NOISE: 24,  # 20.8 to 23.8ms
        ULTRA_LOW_NOISE: 95  # 83.2 to 94.5ms
    }

    #sensor_constants = [0, 0, 0, 0]

    def __init__(self, i2c, address=DEFAULT_I2C_ADDRESS):
        self.i2c = i2c
        self.address = address
        #self.reset()

    def get_temperature_pressure(self):
        """ Convert an output from a calibrated sensor to a pressure in Pa.
        Arguments:
        p_LSB -- Raw pressure data from sensor
        T_LSB -- Raw temperature data from sensor
        """
        LUT_lower = 3.5 * (1 << 20)
        LUT_upper = 11.5 * (1 << 20)
        quadr_factor = 1.0 / 16777216.0
        offst_factor = 2048.0
        calib_constants = self.read_otp_from_i2c()
        T_LSB, p_LSB = self.get_data_from_ICP10111()

        t = T_LSB - 32768.0
        s1 = LUT_lower + float(calib_constants[0] * t * t) * quadr_factor
        s2 = offst_factor * calib_constants[3] + float(calib_constants[1] * t * t) * quadr_factor
        s3 = LUT_upper + float(calib_constants[2] * t * t) * quadr_factor
        A, B, C = self.calculate_conversion_constants([s1, s2, s3])
        pressure = A + B / (C + p_LSB)
        temperature = -45.0 + 175.0 / 65536.0 * T_LSB
        return temperature, pressure

    def reset(self):
        self.i2c.writeto(self.address, self.SOFT_RESET)
        sleep(self.I2C_WAIT_TIME)

    def read_ICP1011_ID(self):
        self.i2c.writeto(self.address, self.READ_ID)
        sleep(self.I2C_WAIT_TIME)
        id = self.i2c.readfrom(self.address, 16)
        id = self._convert_to_integer(id[-5:])
        return id

    def read_otp_from_i2c(self):
        calib_const = [0, 0, 0, 0]
        self.i2c.writeto(self.address, self.OTP_ADDRESS)
        sleep(0.025)
        for x in range(4):
            self.i2c.writeto(self.address, self.READ_OTP)
            data = self.i2c.readfrom(self.address, 3)
            calib_const[x]= self._convert_to_integer(data[:2])
            verified = self._verify_checksum(data)
            if not verified:
                raise CRCError('Data read off i2c bus failed CRC check.',
                               data[:2],
                               data[-1])
        return calib_const

    def get_data_from_ICP10111(self):
        self.i2c.writeto(self.address, self.NORMAL_T_FIRST)
        sleep(self.I2C_WAIT_TIME)
        data = self.i2c.readfrom(self.address, 9)
        t_dout = self._convert_to_integer(data[:2])
        p_dout = data[3] << 16 | data[4] << 8 | data[6] #to group MMSB, MLSB, LMSB
        #CRC check temperature
        verified = self._verify_checksum(data[:3])
        if not verified:
            raise CRCError('Temperature read off i2c bus failed CRC check.',
                           data[:2],
                           data[-1])
        return t_dout, p_dout

        # CRC check Pressure MMSB,MLSB
        verified = self._verify_checksum([data[3], data[4], data[5]])
        if not verified:
            raise CRCError('Pressure MMSB/MLSB read off i2c bus failed CRC check.',
                           data[:2],
                           data[-1])

        verified = self._verify_checksum([data[6], data[7], data[8]])
        if not verified:
            raise CRCError('Pressure LMSB/LLSB read off i2c bus failed CRC check.',
                           data[:2],
                           data[-1])

        return t_dout, p_dout

    def calculate_conversion_constants(self, p_LUT):

        """ calculate temperature dependent constants
        Arguments:
        p_Pa -- List of 3 values corresponding to applied pressure in Pa
        p_LUT -- List of 3 values corresponding to the measured p_LUT values at the applied pressures.
        """

        p_Pa = [45000.0, 80000.0, 105000.0]

        C = (p_LUT[0] * p_LUT[1] * (p_Pa[0] - p_Pa[1]) +   # noqa: W504
        p_LUT[1] * p_LUT[2] * (p_Pa[1] - p_Pa[2]) +        # noqa: W504
        p_LUT[2] * p_LUT[0] * (p_Pa[2] - p_Pa[0])) / (p_LUT[2] * (p_Pa[0] - p_Pa[1]) +   # noqa: W504
        p_LUT[0] * (p_Pa[1] - p_Pa[2]) +                   # noqa: W504
        p_LUT[1] * (p_Pa[2] - p_Pa[0]))
        A = (p_Pa[0] * p_LUT[0] - p_Pa[1] * p_LUT[1] - (p_Pa[1] - p_Pa[0]) * C) / (p_LUT[0] - p_LUT[1])
        B = (p_Pa[0] - A) * (p_LUT[0] + C)

        return A, B, C

    def _convert_to_integer(self, bytes_to_convert):
        'Use bitwise operators to convert the bytes into integers.'
        integer = None
        for chunk in bytes_to_convert:
            if not integer:
                integer = chunk
            else:
                integer = integer << 8
                integer = integer | chunk
        return integer

    def _verify_checksum(self, data):
        ''''Verify the checksum using the polynomial from page 19 of the
        datasheet.
        x8 + x5 + x4 + 1 = 0x131 = 0b100110001
        '''
        crc = 0xff
        values = data[:2]
        checksum = int(data[-1])
        for value in values:
            crc = crc ^ value
            for bit in range(8, 0, -1):
                if crc & 0x80: #10000000
                    crc <<= 1
                    crc ^= 0x131 #100110001
                else:
                    crc <<= 1
        if crc != checksum:
            return False
        else:
            return True