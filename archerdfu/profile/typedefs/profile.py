"""
//******************************************************************************
// FileName   : profile.py
// Created    : 11.05.2023
// Author     : Yaroshenko D. (https://github.com/o-murphy)
//******************************************************************************/
 *  PYTHON CLASS FOR BUILDING / PARSING BCProfile DATA
//******************************************************************************/
"""
from archerdfu.construct import Str1251
from construct import Struct, Int16ul, Float32l, Int8ul, Byte, Int16sl, Int32ul, \
    Bytes, Default, Hex, Enum, Computed

SPI_FI_FLASH_PAGE = 4096

Clicks = Struct(
    'pClickX' / Default(Int16ul, 2),
    'pClickY' / Default(Int16ul, 2),
)

Sight = Struct(
    'sight_name' / Default(Str1251(64), 'TEMPLATE'),
    'clicks' / Clicks
)

DragCoeff = Struct(
    'mach' / Float32l,
    'cd' / Float32l
)

_DragModelType = Enum(
    Int8ul,
    UNKNOWN=0,
    G1=1,
    G7=7,
    CUSTOM=9,
)

Bullet = Struct(
    'bullet_name' / Str1251(64),
    'bc_type' / _DragModelType,

    'drf_start' / Default(Int16ul, 0),
    'drf_count' / Default(Int8ul, 0),
    'drf_end' / Computed(lambda ctx: ctx.drf_start + ctx.drf_count),

    'bal_coeff' / Float32l,
    'b_diameter' / Float32l,
    'b_length' / Float32l,
    'b_weight' / Float32l,

)

Cartridge = Struct(
    'cartridge_name' / Str1251(64),
    'cartridge_desc' / Str1251(20),
    'c_muzzle_velocity' / Int16ul,
    'c_zero_temperature' / Byte,
    'c_t_coeff' / Float32l,
)

Environment = Struct(
    'c_zero_air_temperature' / Default(Byte, 15),
    'c_zero_p_temperature' / Default(Byte, 15),
    'c_zero_air_humidity' / Default(Int8ul, 50),
    'c_zero_air_pressure' / Default(Int16ul, 760),
    'zero_wind_speed' / Default(Float32l, 0),
    'zero_wind_angle' / Default(Int16sl, 0),
    'zero_altitude' / Default(Int16sl, 0),
    'c_zero_w_pitch' / Default(Byte, 0),
    'zero_azimuth' / Default(Int16sl, 270),
    'zero_latitude' / Default(Byte, 75),
    'zero_slope' / Default(Byte, 0),
)

Weapon = Struct(
    'rifle_name' / Str1251(64),
    'rifle_desc' / Str1251(20),
    'caliber_name' / Str1251(32),
    'sc_height' / Int16sl,
    'zero_dist' / Int16ul,
    'twist' / Float32l,

    'r_twist' / Computed(lambda ctx: ctx.twist if ctx.twist >= 0 else -ctx.twist),
    'twist_dir' / Computed(lambda ctx: 'RIGHT' if ctx.twist >= 0 else 'LEFT'),
)

CalcDataHeader = Struct(
    'c_data_crc' / Default(Bytes(2), 0),
    'c_struct_ver' / Hex(Default(Int16ul, 1)),
    'c_struct_size' / Hex(Default(Int32ul, 0x192C)),
    'c_drag_func_start' / Default(Int32ul, SPI_FI_FLASH_PAGE * 2),
    'c_drag_func_size' / Default(Int32ul, 0),
    'c_sight_data' / Sight,
    'c_envir' / Environment,
    'profiles_count' / Default(Int16ul, 0)
)

Profile = Struct(
    *Weapon.subcons,
    *Cartridge.subcons,
    *Bullet.subcons,
    *Environment.subcons
)

PROFILES_COUNT = 20
CALC_DATA_SIZE = CalcDataHeader.sizeof() + Profile.sizeof() * PROFILES_COUNT
G1_DFL = 79
G7_DFL = 84
