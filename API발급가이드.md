# 네이버 API 발급 완벽 가이드

## 🎯 전체 과정 (5분)

### 1단계: 네이버 개발자센터 접속
- 링크: https://developers.naver.com/
- 네이버 계정으로 로그인

### 2단계: Application 메뉴
- 우측 상단 **Application** 클릭
- 또는 직접 접속: https://developers.naver.com/apps/#/list

### 3단계: 애플리케이션 등록

**[애플리케이션 등록] 버튼 클릭**

#### 입력 정보:

**애플리케이션 이름**
```
키워드분석기
```
(원하는 이름 아무거나)

**사용 API 선택** (중요!)
```
✅ 검색
   - 블로그
   - 뉴스
   - 쇼핑 ⭐ 반드시 체크!

✅ 데이터랩 (검색어 트렌드) ⭐ 반드시 체크!

✅ 데이터랩 (쇼핑인사이트) (선택사항)
```

**비로그인 오픈 API 서비스 환경**
```
Web 서비스 URL: http://localhost
```

### 4단계: 등록 완료

등록하면 다음이 표시됩니다:
```
Client ID: sXtXIAuuv1cKBQYXmGVO
Client Secret: 7a0kMTO57Q
```

### 5단계: .env 파일에 입력

프로젝트 폴더에서:

**Windows:**
```cmd
notepad .env
```

**Mac/Linux:**
```bash
nano .env
```

**내용:**
```
NAVER_CLIENT_ID=위에서_복사한_Client_ID
NAVER_CLIENT_SECRET=위에서_복사한_Client_Secret
TZ=Asia/Seoul
```

**저장!** (Ctrl+S 또는 저장 후 닫기)

### 6단계: 테스트

```bash
python test_api.py
```

다음과 같이 나와야 성공:
```
[1/3] 쇼핑 검색 API 테스트...
   ✅ 쇼핑 검색 API - 정상 작동

[2/3] 블로그 검색 API 테스트...
   ✅ 블로그 검색 API - 정상 작동

[3/3] DataLab (검색어 트렌드) API 테스트...
   ✅ DataLab API - 정상 작동
```

---

## ⚠️ 자주 하는 실수

### 실수 1: API 선택 안 함
→ **검색**, **데이터랩(검색어 트렌드)** 반드시 체크!

### 실수 2: Client ID/Secret 복사 오류
→ 공백이나 개행문자 포함 안 되게 조심!

### 실수 3: .env 파일 위치
→ main.py와 같은 폴더에 있어야 함!

### 실수 4: 따옴표 사용
→ .env 파일에서 따옴표 사용 안 함:
```
# 잘못된 예:
NAVER_CLIENT_ID="abc123"

# 올바른 예:
NAVER_CLIENT_ID=abc123
```

---

## 🔍 문제 해결

### 여전히 403 에러?

1. **애플리케이션 목록에서 확인**
   - https://developers.naver.com/apps/#/list
   - 만든 앱 클릭
   - "API 설정" 탭 확인
   - 검색, 데이터랩이 체크되어 있는지 확인

2. **다시 등록**
   - 기존 앱 삭제하고 새로 등록
   - API 선택 확실히 체크

3. **Client ID/Secret 재확인**
   - 복사할 때 전체가 다 복사되었는지 확인
   - 공백 없는지 확인

### 401 에러?

→ Client ID/Secret이 틀림
- 다시 복사해서 .env 파일에 입력

### 400 에러?

→ 요청 형식 오류 (스크립트 문제)
- test_api.py 재실행

---

## 📞 추가 도움

**네이버 개발자 고객센터**
- https://developers.naver.com/support/

**API 문서**
- 검색 API: https://developers.naver.com/docs/search/
- 데이터랩 API: https://developers.naver.com/docs/datalab/
