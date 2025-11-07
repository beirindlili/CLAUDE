#!/usr/bin/env python3
"""
쇼핑인사이트 API 실제 테스트
"""
import os
import json
import requests
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()

ID = os.getenv("NAVER_CLIENT_ID")
SC = os.getenv("NAVER_CLIENT_SECRET")

url = "https://openapi.naver.com/v1/datalab/shopping/category/keywords"
headers = {
    "X-Naver-Client-Id": ID,
    "X-Naver-Client-Secret": SC,
    "Content-Type": "application/json; charset=UTF-8",
}

end = date.today()
start = end - timedelta(days=30)

body = {
  "startDate": start.strftime("%Y-%m-%d"),
  "endDate": end.strftime("%Y-%m-%d"),
  "timeUnit": "date",
  "category": "50000000",  # 패션의류
  "keyword": ["패딩", "코트"],  # 샘플 키워드
  "device": "",
  "gender": "",
  "ages": []
}

print("=" * 60)
print("쇼핑인사이트 API 테스트 (키워드별 트렌드)")
print("=" * 60)
print(f"요청 Body:\n{json.dumps(body, ensure_ascii=False, indent=2)}\n")

r = requests.post(url, headers=headers, data=json.dumps(body), timeout=20)
print(f"Status: {r.status_code}")

if r.status_code == 200:
    print("✅ 성공!\n")
    data = r.json()
    print(f"응답 구조:\n{json.dumps(data, ensure_ascii=False, indent=2)}")
else:
    print(f"❌ 실패: {r.text}")

print("=" * 60)
