import requests
import json
from datetime import datetime

class NaverRealEstateData:
    def __init__(self):
        self.cookies = {
            'NNB': 'MCKEQFZCFXVWO',
            'SRT30': '1743639791',
            'SRT5': '1743640125',
            'page_uid': 'i+3Tesqo15wssd32sDVssssstU4-032738',
            '_naver_usersession_': 'sa1Bk06co+dIVngtenkeJw==',
            'nhn.realestate.article.rlet_type_cd': 'A01',
            'nhn.realestate.article.trade_type_cd': '""',
            'nhn.realestate.article.ipaddress_city': '4800000000',
            '_fwb': '89GoRpkhzDdC2lzT3FZnir.1743640139513',
            'landHomeFlashUseYn': 'Y',
            'realestate.beta.lastclick.cortar': '4812300000',
            'REALESTATE': 'Thu%20Apr%2003%202025%2009%3A29%3A07%20GMT%2B0900%20(Korean%20Standard%20Time)',
            '_fwb': '89GoRpkhzDdC2lzT3FZnir.1743640139513',
            'BUC': '8ZBDcMJKZIDTBbalZzi0mhzxc-FJEsCphA6H50Kf6iU=',
        }

        self.headers = {
            'accept': '*/*',
            'accept-language': 'ko,en;q=0.9,en-US;q=0.8,ko-KR;q=0.7',
            'authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IlJFQUxFU1RBVEUiLCJpYXQiOjE3NDM2NDAxNDcsImV4cCI6MTc0MzY1MDk0N30.spWTR9rB8tscdTUKxH_Znz1YTk2r5Yh9n4XrrUblAZk',
            'priority': 'u=1, i',
            'referer': 'https://new.land.naver.com/complexes/22896?ms=35.2405155,128.6573506,15&a=PRE:OPST&e=RETAIL',
            'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        }

    def fetch_data(self, complex_no='22896', page=1, filters=None):
        url = f'https://new.land.naver.com/api/articles/complex/{complex_no}'
        params = {
            'realEstateType': 'PRE:OPST',
            'tradeType': '',
            'tag': '::::::::',
            'rentPriceMin': '0',
            'rentPriceMax': '900000000',
            'priceMin': '0',
            'priceMax': '900000000',
            'areaMin': '0',
            'areaMax': '900000000',
            'oldBuildYears': '',
            'recentlyBuildYears': '',
            'minHouseHoldCount': '',
            'maxHouseHoldCount': '',
            'showArticle': 'false',
            'sameAddressGroup': 'false',
            'minMaintenanceCost': '',
            'maxMaintenanceCost': '',
            'priceType': 'RETAIL',
            'directions': '',
            'page': str(page),
            'complexNo': complex_no,
            'buildingNos': '',
            'areaNos': '',
            'type': 'list',
            'order': 'rank'
        }

        # 필터 적용
        if filters:
            if 'min_price' in filters and filters['min_price']:
                params['priceMin'] = str(filters['min_price'])
            if 'max_price' in filters and filters['max_price']:
                params['priceMax'] = str(filters['max_price'])
            if 'min_area' in filters and filters['min_area']:
                params['areaMin'] = str(filters['min_area'])
            if 'max_area' in filters and filters['max_area']:
                params['areaMax'] = str(filters['max_area'])
            if 'trade_types' in filters and filters['trade_types']:
                trade_type_map = {
                    '매매': 'A1',
                    '전세': 'B1',
                    '월세': 'B2'
                }
                selected_types = [trade_type_map[t] for t in filters['trade_types'] if t in trade_type_map]
                if selected_types:
                    params['tradeType'] = ','.join(selected_types)

        try:
            response = requests.get(url, cookies=self.cookies, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

    def save_to_json(self, data, filename='naver_real_estate.json'):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False

    def load_from_json(self, filename='naver_real_estate.json'):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading data: {e}")
            return None 