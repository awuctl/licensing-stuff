#!/usr/bin/env python

from keycutter import ProductKeyEncoder
from pkeyconfig import PKeyConfig

if __name__ == '__main__':

    import argparse
    import json

    main_parser = argparse.ArgumentParser(
        'Keymaker',
        description='Create 2009 product keys for all ranges defined in a pkeyconfig'
    )

    main_parser.add_argument('pkeyconfig', type=argparse.FileType('r'))
    main_parser.add_argument('format', help='Output format', choices=['text', 'json'])

    args = main_parser.parse_args()

    alg2009 = 'msft:rm/algorithm/pkey/2009'

    import xml.etree.ElementTree as ET
    pkc = PKeyConfig(ET.fromstring(args.pkeyconfig.read()))

    configs = filter(lambda x: pkc.pubkey_for_group(x.group_id).algorithm == alg2009 and x.group_id != 999999, pkc.configs)

    match args.format:
        case 'text':
            for c in configs:
                print(f'C: {c.desc}\n   (edition: {c.edition_id}, group: {c.group_id}, type: {c.key_type}, act_id: {c.config_id})')
                for range in pkc.ranges_for_config(c):
                    print(f'R: {range.start:>10}-{range.end:>10} [{range.part_number}]: {str(ProductKeyEncoder(c.group_id, range.start, 0, 0))}')
                print()

        case 'json':
            print(json.dumps([{
                'actid': config.config_id,
                'desc': config.desc,
                'group': config.group_id,
                'ranges': [{
                    'start': range.start,
                    'end': range.end,
                    'part_number': range.part_number,
                    'key': str(ProductKeyEncoder(config.group_id, range.start, 0, 0))
                    } for range in pkc.ranges_for_config(config)
                ]
            } for config in configs]))
