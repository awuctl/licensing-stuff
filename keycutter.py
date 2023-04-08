#!/usr/bin/env python

from dataclasses import dataclass
from functools import reduce
from typing import Tuple, Union

# CRC32/MPEG-2
def crc_table():
    tab = []
    for i in range(256):
        k = i << 24
        for _bit in range(8):
            k = (k << 1) ^ (0x4c11db7) if k & 0x80000000 else k << 1
        tab.append(k & 0xffffffff)
    return tab

CRC32_TABLE = crc_table()

class ProductKeyDecoder:
    ALPHABET = 'BCDFGHJKMPQRTVWXY2346789'

    @staticmethod
    def decode_5x5(key: str, alphabet: str) -> int:
        """Decodes a 5x5 key into a number"""
        key = key.replace('-', '')

        dec = [key.index('N')]
        dec.extend([
            alphabet.index(l) for l in key.replace('N', '')
        ])

        return reduce(lambda a, x: (a * 24) + x, dec)

    def __str__(self):
        return self.key_5x5

    def __int__(self):
        return self.key

    def __init__(self, key: str):
        self.key_5x5 = key
        self.key     = self.decode_5x5(key, self.ALPHABET)

        self.group    = ( int(self) & 0x000000000000000000000000000fffff )
        self.serial   = ( int(self) & 0x00000000000000000003fffffff00000 ) >> 20
        self.security = ( int(self) & 0x0000007ffffffffffffc000000000000 ) >> 50
        self.checksum = ( int(self) & 0x0001ff80000000000000000000000000 ) >> 103
        self.upgrade  = ( int(self) & 0x00020000000000000000000000000000 ) >> 113
        self.extra    = ( int(self) & 0x00040000000000000000000000000000 ) >> 114

class ProductKeyEncoder():
    ALPHABET = 'BCDFGHJKMPQRTVWXY2346789' # N omitted

    # group, serial, security, checksum, upgrade, extra
    BOUNDS = [0xfffff, 0x3fffffff, 0x1fffffffffffff, 0x3ff, 0x1, 0x1]

    @staticmethod
    def to_5x5(key: int) -> str:

        def encode(key: int) -> bytes:
            """Encodes the key into a byte-base25 form"""
            # the bytes are calculated in reverse,
            # hence they're bytes()d to little endian
            num = 0
            for _i in range(25):
                num = num << 8
                num = num | (key % 24)
                key = key // 24

            return num.to_bytes(25, 'little')

        key = encode(key)

        key_5x5 = [ProductKeyDecoder.ALPHABET[i] for i in key[1:]]
        key_5x5.insert(key[0], 'N')

        key_5x5.insert(5,  '-')
        key_5x5.insert(11, '-')
        key_5x5.insert(17, '-')
        key_5x5.insert(23, '-')

        return reduce(lambda a, x: a + x, key_5x5, '')

    @staticmethod
    def checksum_key(key: bytes):
        
        crc = 0xffffffff
        for byte in key:
            crc = (crc << 8) ^ CRC32_TABLE[((crc >> 24) ^ byte) & 0xff]
        return ~crc & 0x3ff

    def __str__(self) -> str:
        return self.key_5x5

    def __int__(self) -> int:
        return self.key

    def __init__(self, group: int, serial: int, security: int, upgrade: int, checksum: int = 0x400, extra: int = 0):

        # Bound checking
        if False in ([x <= b for b,x in zip(
                [0xfffff, 0x3fffffff, 0x1fffffffffffff, 0x3ff, 0x1, 0x1],
                [group, serial, security, checksum - 1, upgrade, extra]
            )]):
            raise Exception('Key parameter(s) not within bounds')

        self.group, self.serial, self.security = (group, serial, security)

        key  = 0
        key |= extra    << 114
        key |= upgrade  << 113
        key |= security << 50
        key |= serial   << 20
        key |= group

        if checksum == 0x400:
            checksum = self.checksum_key(key.to_bytes(16, 'little'))

        self.checksum = checksum
        key |= checksum << 103

        # for the extra bit to work and the key to still
        # be encodable, its value has to be below (24^25)
        if extra != 0:
            if key > (0x62A32B15518 << 72):
                raise Exception('Extra parameter unencodable')

        self.key = key
        self.key_5x5 = self.to_5x5(self.key)

if __name__ == '__main__':

    import argparse
    import re

    p = argparse.ArgumentParser(
        'keycutter',
        description='generate Windows product keys (2009 algorithm).',
        allow_abbrev=True
    )

    sp = p.add_subparsers(title='Commands', dest='mode')
    enc_p = sp.add_parser('encode')
    enc_p.add_argument('group',    type=lambda i: int(i,0), help='Group reference ID')
    enc_p.add_argument('serial',   type=lambda i: int(i,0), help='Serial number')
    enc_p.add_argument('security', type=lambda i: int(i,0), help='Security value')
    enc_p.add_argument('-u',       type=lambda i: int(i,0), help='Upgrade bit', dest='upgrade', default=0)
    enc_p.add_argument('-c',       type=lambda i: int(i,0), help='truncated 10-bit CRC, 0x400 for automatic', dest='checksum', default='0x400')
    enc_p.add_argument('-e',       type=lambda i: int(i,0), help='Extra bit', dest='extra', default=0)

    dec_p = sp.add_parser('decode')
    dec_p.add_argument('key', type=str)
    dec_p.add_argument('-output', choices=['parametric', 'raw', 'rawhex'], default='parametric')

    tmpl_p = sp.add_parser('template')
    tmpl_p.add_argument('group',    type=lambda i: int(i,0), help='Group reference ID')
    tmpl_p.add_argument('template', type=str,                help='Key template')
    tmpl_p.add_argument('-u',       type=lambda i: int(i,0), help='Upgrade bit', dest='upgrade')
    tmpl_p.add_argument('-e',       type=lambda i: int(i,0), help='Extra bit',   dest='extra')

    arg = p.parse_args()

    match arg.mode:
        case 'decode':
            # Verify if 5x5
            alpha = ProductKeyDecoder.ALPHABET
            if not re.match(f'(?:[{alpha+"N"}]{{5}}-){{4}}[{alpha+"N"}]{{4}}[{alpha}]', arg.key):
                print('Invalid product key')
                exit(1)

            keyi = ProductKeyDecoder(arg.key)

            match arg.output:
                case 'parametric':
                    print('\nPKey     : [%s]\n        -> [%032x]\n' % (str(keyi), int(keyi)))
                    print('            0xfffff')
                    print('Group    : [0x%05x]\n' % keyi.group)
                    print('            0x3fffffff')
                    print('Serial   : [0x%08x]\n' % keyi.serial)
                    print('            0x1FFFFFFFFFFFFF')
                    print('Security : [0x%014x]\n' % keyi.security)
                    print('            0x3FF')
                    print('Checksum : [0x%03x]\n' % keyi.checksum)
                    print('            0x1')
                    print('Upgrade  : [0x%01x]\n' % keyi.upgrade)
                    print('            0x1')
                    print('Extra    : [0x%01x]\n' % keyi.extra)
                case 'raw':
                    print(*[str(keyi),
                        int(keyi),
                        keyi.group,
                        keyi.serial,
                        keyi.security,
                        keyi.upgrade,
                        keyi.checksum,
                        keyi.extra],
                        sep='\n'
                    )
                case 'rawhex':
                    print(*[str(keyi),
                        hex(int(keyi)),
                        hex(keyi.group),
                        hex(keyi.serial),
                        hex(keyi.security),
                        hex(keyi.upgrade),
                        hex(keyi.checksum),
                        hex(keyi.extra)],
                        sep='\n'
                    )
                
        case 'encode':
            keyi = ProductKeyEncoder(arg.group, arg.serial, arg.security, arg.upgrade, arg.checksum, arg.extra)
            print(str(keyi))
        case 'template':
            NULL = 'NBBBB-BBBBB-BBBBB-BBBBB-BBBBB'

            def list_keys(gid: int, template: str):

                if len(template) > 21: # 18 meaningful digits
                    raise Exception('Template too long')

                template_key = ProductKeyDecoder(template + NULL[len(template):])
                serial_iter = template_key.serial

                # Find serial that will give a key that matches the template
                while True:

                    key = ProductKeyEncoder(
                        gid,
                        serial_iter,
                        template_key.security,
                        template_key.upgrade,
                        extra=template_key.extra
                    )

                    serial_iter += 1
                    if key.checksum != template_key.checksum:
                        continue

                    # Usable serial numbers exhausted
                    if str(key)[:len(template)] != template:
                        break

                    print(str(key))

            if 'N' in arg.template:
                list_keys(arg.group, arg.template)
