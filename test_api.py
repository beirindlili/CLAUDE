#!/usr/bin/env python3
"""
API 연결 테스트 스크립트
"""
import os
import requests
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

client_id = os.getenv('NAVER_CLIENT_ID')
client_secret = os.getenv('NAVER_CLIENT_SECRET')

print("=" * 60)
print("네이버 API 연결 테스트")
print("=" * 60)
print(f"Client ID: {client_id}")
print(f"Client Secret: {client_secret[:4]}***" if client_secret else "None")
print("=" * 60)

if not client_id or not client_secret:
    print("❌ .env 파일에 API 키가 없습니다!")
    print("\n.env 파일을 확인하세요:")
    print("NAVER_CLIENT_ID=여기에_클라이언트ID")
    print("NAVER_CLIENT_SECRET=여기에_시크릿")
    exit(1)

# 1. 쇼핑 검색 API 테스트
print("\n[1/3] 쇼핑 검색 API 테스트...")
headers = {
    'X-Naver-Client-Id': client_id,
    'X-Naver-Client-Secret': client_secret
}

try:
    response = requests.get(
        'https://openapi.naver.com/v1/search/shop.json',
        params={'query': '나이키', 'display': 1},
        headers=headers,
        timeout=10
    )

    if response.status_code == 200:
        print("   ✅ 쇼핑 검색 API - 정상 작동")
    elif response.status_code == 401:
        print("   ❌ 인증 실패 (401) - Client ID/Secret 확인 필요")
        print(f"   응답: {response.text}")
    elif response.status_code == 403:
        print("   ❌ 권한 없음 (403) - API 사용 신청 필요")
        print(f"   응답: {response.text}")
    else:
        print(f"   ⚠️  오류 ({response.status_code}): {response.text}")
except Exception as e:
    print(f"   ❌ 연결 실패: {e}")

# 2. 블로그 검색 API 테스트
print("\n[2/3] 블로그 검색 API 테스트...")
try:
    response = requests.get(
        'https://openapi.naver.com/v1/search/blog.json',
        params={'query': '나이키', 'display': 1},
        headers=headers,
        timeout=10
    )

    if response.status_code == 200:
        print("   ✅ 블로그 검색 API - 정상 작동")
    elif response.status_code == 401:
        print("   ❌ 인증 실패 (401)")
    elif response.status_code == 403:
        print("   ❌ 권한 없음 (403)")
    else:
        print(f"   ⚠️  오류 ({response.status_code}): {response.text}")
except Exception as e:
    print(f"   ❌ 연결 실패: {e}")

# 3. DataLab API 테스트
print("\n[3/3] DataLab (검색어 트렌드) API 테스트...")
headers['Content-Type'] = 'application/json'

from datetime import datetime, timedelta
today = datetime.now()
end_date = (today - timedelta(days=1)).strftime('%Y-%m-%d')
start_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')

body = {
    "startDate": start_date,
    "endDate": end_date,
    "timeUnit": "date",
    "keywordGroups": [
        {
            "groupName": "나이키",
            "keywords": ["나이키"]
        }
    ]
}

try:
    response = requests.post(
        'https://openapi.naver.com/v1/datalab/search',
        json=body,
        headers=headers,
        timeout=10
    )

    if response.status_code == 200:
        print("   ✅ DataLab API - 정상 작동")
    elif response.status_code == 401:
        print("   ❌ 인증 실패 (401)")
        print(f"   응답: {response.text}")
    elif response.status_code == 403:
        print("   ❌ 권한 없음 (403) - DataLab API 사용 신청 필요")
        print(f"   응답: {response.text}")
    elif response.status_code == 400:
        print("   ⚠️  요청 오류 (400) - DataLab API가 활성화되지 않았을 수 있음")
        print(f"   응답: {response.text}")
    else:
        print(f"   ⚠️  오류 ({response.status_code}): {response.text}")
except Exception as e:
    print(f"   ❌ 연결 실패: {e}")

print("\n" + "=" * 60)
print("테스트 완료")
print("=" * 60)
print("\n💡 문제 해결 방법:")
print("1. 네이버 개발자센터 접속: https://developers.naver.com/")
print("2. 내 애플리케이션 → 해당 앱 선택")
print("3. API 설정에서 다음 API 활성화:")
print("   - 검색 (필수)")
print("   - 데이터랩 (검색어 트렌드) (필수)")
print("4. Client ID/Secret 재확인")
print("=" * 60)
