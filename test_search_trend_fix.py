import os, json, requests
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()

ID = os.getenv("NAVER_CLIENT_ID")
SC = os.getenv("NAVER_CLIENT_SECRET")

print(f"Client ID: {ID}")
print(f"Client Secret: {SC[:4]}***\n")

url = "https://openapi.naver.com/v1/datalab/search"
headers = {
    "X-Naver-Client-Id": ID,
    "X-Naver-Client-Secret": SC,
    "Content-Type": "application/json; charset=UTF-8",
}

end = date.today() - timedelta(days=1)
start = end - timedelta(days=7)

body = {
  "startDate": start.strftime("%Y-%m-%d"),
  "endDate": end.strftime("%Y-%m-%d"),
  "timeUnit": "date",
  "keywordGroups": [
    {
      "groupName": "나이키",
      "keywords": ["나이키"]
    }
  ]
}

print(f"요청 URL: {url}")
print(f"요청 Body: {json.dumps(body, ensure_ascii=False)}\n")

r = requests.post(url, headers=headers, data=json.dumps(body), timeout=20)
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:500]}")

if r.status_code == 200:
    print("\n✅ 검색어 트렌드 API 정상 작동!")
    data = json.loads(r.text)
    if 'results' in data and len(data['results']) > 0:
        print(f"결과 개수: {len(data['results'][0]['data'])}")
elif r.status_code == 401:
    print("\n❌ 401: ID/Secret 확인 필요")
elif r.status_code == 403:
    print("\n❌ 403: API 활성화 확인")
elif r.status_code == 400:
    print("\n❌ 400: Body 스키마 오류")
