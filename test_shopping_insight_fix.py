import os, json, requests
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()

ID = os.getenv("NAVER_CLIENT_ID")
SC = os.getenv("NAVER_CLIENT_SECRET")

print(f"Client ID: {ID}")
print(f"Client Secret: {SC[:4]}***\n")

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
  "category": "50000000",              # 예: 패션의류 대분류
  "keyword": ["하이볼 잔","코듀로이 팬츠"],   # 키워드 배열(필수)
  "device": "", "gender": "", "ages": []
}

print(f"요청 URL: {url}")
print(f"요청 Body: {json.dumps(body, ensure_ascii=False)}\n")

r = requests.post(url, headers=headers, data=json.dumps(body), timeout=20)
print(f"Status: {r.status_code}")
print(f"Response: {r.text}")

if r.status_code == 200:
    print("\n✅ 쇼핑인사이트 API 정상 작동!")
elif r.status_code == 401:
    print("\n❌ 401: ID/Secret 확인 필요")
elif r.status_code == 403:
    print("\n❌ 403: API 활성화 또는 HTTPS/POST 확인")
elif r.status_code == 400:
    print("\n❌ 400: Body 스키마 오류")
