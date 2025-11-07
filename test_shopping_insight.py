#!/usr/bin/env python3
"""
쇼핑인사이트 API 테스트
"""
import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

client_id = os.getenv('NAVER_CLIENT_ID')
client_secret = os.getenv('NAVER_CLIENT_SECRET')

print("=" * 60)
print("네이버 쇼핑인사이트 API 테스트")
print("=" * 60)

headers = {
    'X-Naver-Client-Id': client_id,
    'X-Naver-Client-Secret': client_secret,
    'Content-Type': 'application/json'
}

# 날짜 설정 (최근 1개월)
today = datetime.now()
end_date = (today - timedelta(days=1)).strftime('%Y-%m-%d')
start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')

# 패션의류 카테고리
body = {
    "startDate": start_date.replace('-', ''),
    "endDate": end_date.replace('-', ''),
    "timeUnit": "month",
    "category": ["50000000"],  # 패션의류
    "device": "",
    "ages": [],
    "gender": ""
}

print(f"요청: {body}\n")

try:
    response = requests.post(
        'https://openapi.naver.com/v1/datalab/shopping/categories',
        json=body,
        headers=headers,
        timeout=10
    )

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        print("✅ 쇼핑인사이트 API 정상 작동!")
        data = response.json()
        print(f"\n결과: {data}")
    elif response.status_code == 403:
        print("❌ 권한 없음 - 쇼핑인사이트 API 활성화 필요")
        print(f"응답: {response.text}")
    elif response.status_code == 400:
        print("⚠️ 요청 오류")
        print(f"응답: {response.text}")
    else:
        print(f"❌ 오류 ({response.status_code})")
        print(f"응답: {response.text}")

except Exception as e:
    print(f"❌ 연결 실패: {e}")

print("=" * 60)
