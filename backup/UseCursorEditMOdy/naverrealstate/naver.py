import requests

cookies = {
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

headers = {
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
    # 'cookie': 'NNB=MCKEQFZCFXVWO; SRT30=1743639791; SRT5=1743640125; page_uid=i+3Tesqo15wssd32sDVssssstU4-032738; _naver_usersession_=sa1Bk06co+dIVngtenkeJw==; nhn.realestate.article.rlet_type_cd=A01; nhn.realestate.article.trade_type_cd=""; nhn.realestate.article.ipaddress_city=4800000000; _fwb=89GoRpkhzDdC2lzT3FZnir.1743640139513; landHomeFlashUseYn=Y; realestate.beta.lastclick.cortar=4812300000; REALESTATE=Thu%20Apr%2003%202025%2009%3A29%3A07%20GMT%2B0900%20(Korean%20Standard%20Time); _fwb=89GoRpkhzDdC2lzT3FZnir.1743640139513; BUC=8ZBDcMJKZIDTBbalZzi0mhzxc-FJEsCphA6H50Kf6iU=',
}

response = requests.get(
    'https://new.land.naver.com/api/articles/complex/22896?realEstateType=PRE%3AOPST&tradeType=&tag=%3A%3A%3A%3A%3A%3A%3A%3A&rentPriceMin=0&rentPriceMax=900000000&priceMin=0&priceMax=900000000&areaMin=0&areaMax=900000000&oldBuildYears&recentlyBuildYears&minHouseHoldCount&maxHouseHoldCount&showArticle=false&sameAddressGroup=false&minMaintenanceCost&maxMaintenanceCost&priceType=RETAIL&directions=&page=2&complexNo=22896&buildingNos=&areaNos=&type=list&order=rank',
    cookies=cookies,
    headers=headers,
)

import json

# 응답 데이터를 JSON 형식으로 저장
with open('naver_real_estate.json', 'w', encoding='utf-8') as f:
    json.dump(response.json(), f, ensure_ascii=False, indent=4)
