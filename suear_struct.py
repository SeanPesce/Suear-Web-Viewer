#!/usr/bin/env python3
# Author: Sean Pesce

from ctypes import c_char, c_uint8, c_uint16, c_uint32, c_uint64

from ctypes_util import StructLE



class SuearUdpMsg_0xffeeffee(StructLE):
    MAGIC = 0xffeeffee
    
    MESSAGE_TYPE = {
        0x0001: 'GetDeviceInfo',
        0x0002: 'GetLicense',
        0x0003: 'SetLicense',
        0x0004: 'OpenVideo',
        0x0006: 'UpdateFirmware',
        0x000a: 'SetLed',
        0x000c: 'CameraCommand',
        0x000d: 'GetCameraConfig',
        0x000e: 'SetCameraConfig',
    }
    
    _fields_ = [
        ('magic', c_uint32),  # 0xffeeffee
        ('id', c_uint16),   # Message ID (increments after every request/response pair)
        ('type', c_uint16),   # Message type
        ('unk', c_uint8),  # Always set to 1 in requests (?)
        ('err_code', c_uint8),  # 0 == SUCCESS
        ('length', c_uint16),  # Length of data that follows this header
    ]

    
    def validate(self):
        # Initialize
        self.data = b''
        
        # Validate
        if self.magic != self.__class__.MAGIC:
            raise ValueError(f'Invalid magic bytes for {self.__class__.__name__}: {self.magic:#x}')
        return
    
    
    @property
    def type_name(self):
        return self.__class__.MESSAGE_TYPE[self.type]
    
    
    def get_bytes(self):
        return super().get_bytes() + self.data
    
    
    def __bytes__(self):
        return bytes(self.get_bytes())



class SuearDeviceInfo(StructLE):
    ENCODING = 'ascii'

    _fields_ = [
        ('unk0', c_uint8),
        ('_vendor', c_char * 32),
        ('_product_id', c_char * 32),
        ('_fw_version', c_char * 16),
        ('_ssid', c_char * 32),
        ('unk113', c_uint32),
        ('unk117', c_uint16),
        ('power_info', c_uint16),
        ('capacity', c_uint8),
        ('workmode1', c_uint8),
        ('workmode2', c_uint8),
        ('unk124', c_uint32),
    ]

    @property
    def battery(self):
        return self.power_info >> 9

    @property
    def is_charging(self):
        return bool(((self.power_info << 0x17) & 0xffffffff) >> 0x1f)

    @property
    def is_low_power_off(self):
        return ((self.power_info << 0x18) & 0xffffffff) >> 0x19

    @property
    def vendor(self):
        return self._vendor.decode(self.__class__.ENCODING)
    
    @property
    def product_id(self):
        return self._product_id.decode(self.__class__.ENCODING)
    
    @property
    def fw_version(self):
        return self._fw_version.decode(self.__class__.ENCODING)
    
    @property
    def ssid(self):
        return self._ssid.decode(self.__class__.ENCODING)



class SuearUdpMsg_StreamChunk(StructLE):
    _fields_ = [
        ('unk1', c_uint8),  # Always 0x01?
        ('n_chunk', c_uint8),
        ('n_frame', c_uint8),
        ('last_chunk', c_uint8),  # If 0x01, next message is a new frame
        ('total_chunks', c_uint8),  # Zero until last chunk
        ('unk5', c_uint8),
        ('position', c_uint16 * 3),  # Possibly position data (i.e., coordinates/rotation)
        ('res_width', c_uint16),   # Video resolution (width)
        ('res_height', c_uint16),  # Video resolution (height)
    ]



class SuearLicenseInfo(StructLE):
    _fields_ = [
        ('_serial_num', c_char * 32),
        ('license', c_char * 144),
    ]

    @property
    def serial_num(self):
        return self._serial_num.decode('ascii')
