#!/usr/bin/env python

from dataclasses import dataclass
from typing import List, Tuple
from xml.etree import ElementTree as ET

from base64 import b64decode

class PKeyConfig:

    PKEYCONFIGDATA_XPATH = './{*}license/{*}otherInfo/{*}infoTables/{*}infoList/{*}infoBin[@name="pkeyConfigData"]'

    @dataclass
    class Configuration:
        config_id:   str
        group_id:    int
        edition_id:  str
        desc:        str
        key_type:    str
        randomized:  bool

    @dataclass
    class KeyRange:
        config_id:   str
        part_number: str
        eula_type:   str
        is_valid:    bool
        start:       int
        end:         int

    @dataclass
    class PublicKey:
        group_id:    int
        algorithm:   str
        pub_key:     str

    # Initialized via **License** XrML
    def __init__(self, xml: ET):
        if type(xml) == str:
            xml = ET.fromstring(xml)

        def parse_config(x: ET.Element):
            return self.Configuration(
                x.find('./{*}ActConfigId').text,
                int(x.find('./{*}RefGroupId').text),
                x.find('./{*}EditionId').text,
                x.find('./{*}ProductDescription').text,
                x.find('./{*}ProductKeyType').text,
                True if x.find('./{*}IsRandomized').text == 'true' else False
            )

        def parse_range(x: ET.Element):
            return self.KeyRange(
                x.find('./{*}RefActConfigId').text,
                x.find('./{*}PartNumber').text,
                x.find('./{*}EulaType').text,
                True if x.find('./{*}IsValid').text == 'true' else False,
                int(x.find('./{*}Start').text),
                int(x.find('./{*}End').text)
            )

        def parse_pubkey(x: ET.Element):
            return self.PublicKey(
                int(x.find('./{*}GroupId').text),
                x.find('./{*}AlgorithmId').text,
                x.find('./{*}PublicKeyValue').text
            )

        self.pkeyconfigdata = ET.fromstring(b64decode(xml.find(self.PKEYCONFIGDATA_XPATH).text))

        configs = self.pkeyconfigdata.findall('./{*}Configurations/{*}Configuration')
        ranges  = self.pkeyconfigdata.findall('./{*}KeyRanges/{*}KeyRange')
        pubkeys = self.pkeyconfigdata.findall('./{*}PublicKeys/{*}PublicKey')

        self.configs = [parse_config(x) for x in configs]
        self.ranges =  [parse_range(x)  for x in ranges]
        self.pubkeys = [parse_pubkey(x) for x in pubkeys]

    def config_for_group(self, group: int) -> Configuration:
        """Find Configuration for a Group ID"""
        return next((x for x in self.configs if x.group_id == group))

    def ranges_for_group(self, group: int) -> List[KeyRange]:
        """Find KeyRanges for a Group ID"""
        conf = self.config_for_group(group)
        return list((x for x in self.ranges if x.config_id == conf.config_id))

    def ranges_for_config(self, config: Configuration) -> List[KeyRange]:
        """Find KeyRanges for a Configuration"""
        return list((x for x in self.ranges if x.config_id == config.config_id))

    def pubkey_for_group(self, group: int) -> PublicKey:
        """Find the PublicKey info for a Group ID"""
        return next((x for x in self.pubkeys if x.group_id == group))

    def all_for_group(self, group: int) -> Tuple[Configuration, List[KeyRange], PublicKey]:
        """Find the Configuration, all KeyRanges and PublicKey for a Group ID"""
        return (
            self.config_for_group(group),
            self.ranges_for_group(group),
            self.pubkey_for_group(group)
        )

if __name__ == '__main__':
    import argparse
    import xml.etree.ElementTree as ET

    ALG2009 = 'msft:rm/algorithm/pkey/2009'

    p = argparse.ArgumentParser()
    p.add_argument('pkeyconfig', type=argparse.FileType('r', encoding='utf-8'))
    p.add_argument('substring', type=str, nargs='?', default='', help='Substring to look for in the edition name')

    args = p.parse_args()

    pkc = PKeyConfig(ET.fromstring(args.pkeyconfig.read()))
    c2k9 = filter(lambda x: pkc.pubkey_for_group(x.group_id).algorithm == ALG2009 and x.group_id != 999999, pkc.configs)

    for c in c2k9:
        if args.substring.lower() in c.desc.lower():
            print(f'[{c.group_id}]: "{c.desc}" - {c.edition_id}')
    