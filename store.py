#!/usr/bin/env python

from typing import Tuple
import requests
from hashlib import sha256
from uuid import UUID
import xml.etree.ElementTree as ET
import json

from pkeyconfig import PKeyConfig

def content_id(product: str, publisher: str, platform: str) -> UUID:
    content_str = (product + ':' + publisher + ':' + platform).lower()

    # utf-16[2:] meant to fake UCS-2
    return UUID(bytes_le=sha256(content_str.encode('utf-16')[2:]).digest()[:16])

class StoreQuery:

    @staticmethod
    def query_store(content_id: str, market: str = 'US', locale: str = 'en-US', catalog_locale: str = 'en-US', session: requests.Session = requests.session()) -> Tuple[object, bool]:
        store_r = session.get(
            'https://storeedgefd.dsx.mp.microsoft.com/v9.0/pages/pdp',
            params = {
                'productId': content_id,
                'itemType': 'Apps',
                'idType': 'ContentId',
                'appversion': '22206.1401.0',
                'market': market,
                'locale': locale,
                'deviceFamily': 'Windows.Desktop',
                'catalogLocales': catalog_locale,
                'architecture': 'x64',
                'displayMode': 3
            }
        ).text
        obj_response = json.loads(store_r)

        return (obj_response, StoreQuery.get_error(obj_response))

    @staticmethod
    def get_error(response: object) -> Tuple[int, str]:

        if not isinstance(response, list):
            response = [response]

        for r in response:
            if 'Path' in r:
                if r['Path'].startswith('/errorinfo'):
                    return (int(r['Payload']['ErrorCode'], base=16), r['Payload']['ErrorDescription'])
            else:
                if 'innererror' in r:
                    return (-1, r['message'])
        return (0, 'Success')

if __name__ == '__main__':

    import argparse

    p = argparse.ArgumentParser(
        'store',
        description='Collection of utility functions for Microsoft Store stuff'
    )

    sp = p.add_subparsers(title='Utils', dest='util', required=True)

    sp_ci = sp.add_parser('content-id')
    sp_ci.add_argument('product',  help='Product name')
    sp_ci.add_argument('publisher', help='Publisher string (eg. 8wekyb3d8bbwe)')
    sp_ci.add_argument('platform',  help='Platform name (eg. win32, uwp)')

    sp_qc = sp.add_parser('query-content')
    sp_qc.add_argument('content_id')
    sp_qc.add_argument('-market', help='Market code (US/IR/PL/RU/...)', nargs='?')
    sp_qc.add_argument('-locale', help='Language for the query (en-US, fa-IR, pl-PL, ru-RU, ...)', nargs='?')

    sp_qp = sp.add_parser('query-pkeyconfig')
    sp_qp.add_argument('pkeyconfig', type=argparse.FileType(mode='r'))
    sp_qp.add_argument('-market', help='Market code (US/IR/PL/RU/...)', nargs='?')
    sp_qp.add_argument('-locale', help='Language for the query (en-US, fa-IR, pl-PL, ru-RU, ...)', nargs='?')

    args = p.parse_args()

    match args.util:
        case 'content-id':
            print(content_id(args.product, args.publisher, args.platform))

        case 'query-content':
            # build arguments
            kwords = {'content_id': args.content_id}
            if args.market is not None:
                kwords['market'] = args.market
            if args.locale is not None:
                kwords['locale'] = args.locale

            print(StoreQuery.query_store(**kwords)[0])

        case 'query-pkeyconfig':
            from skuidmap import sku_id_map
            # invert to map from name to id:
            sku_id_map = { k : v for v, k in sku_id_map.items() }

            alg2009 = 'msft:rm/algorithm/pkey/2009'
            pkc = PKeyConfig(ET.fromstring(args.pkeyconfig.read()))

            confs = filter(
                lambda c: c.group_id != 999999 # placeholders
                        and c.edition_id in sku_id_map.keys() # unknown SKUs, multiple SKU groups
                        and 'Server' not in c.edition_id, # filter out Server SKUs (filters out ServerRdsh too, but it's not in the Store anyway)
                        #and 'EnterpriseS' in c.edition_id,
                pkc.configs
            )

            sess = requests.session()
            for c in confs:
                for r in pkc.ranges_for_config(c):
                    part_num = r.part_number.split(':')[0][-9:]
                    ident = content_id(f'Microsoft.Windows.{sku_id_map[c.edition_id]}.{part_num}', '8wekyb3d8bbwe', 'win32')

                    # build arguments
                    kwords = {'content_id': ident, 'session': sess}
                    if args.market is not None:
                        kwords['market'] = args.market
                    if args.locale is not None:
                        kwords['locale'] = args.locale
                        kwords['catalog_locale'] = args.locale

                    (res, (code, errstr)) = StoreQuery.query_store(**kwords)
                    if code != 0:
                        print(f"[ ] {c.edition_id:>24} ({c.key_type:>14}, {part_num:<9}) -> {errstr}")
                    else:
                        prod_info = next((x for x in res if 'V3.ProductDetails' in x['Payload']['$type']))['Payload']
                        print(f"[x] {c.edition_id:>24} ({c.key_type:>14}, {part_num:<9}) -> {prod_info['Title']}")