# Naver Keyword Opportunity Scraper

네이버에서 **수요는 높은데 공급(스마트스토어)은 적은** "기회 키워드"를 자동으로 찾아주는 스크립트입니다.

## 주요 기능

- 네이버 DataLab으로 검색 트렌드 분석 (최근 vs 이전 기간 비교)
- 네이버 쇼핑 검색으로 스마트스토어 공급량 추정
- 블로그 언급량 분석 (선택)
- 브랜드/상품 키워드 자동 분류
- Opportunity Score 기반 정렬 및 CSV 출력

## 설치

```bash
# Python 3.10+ 필요
pip install -r requirements.txt
```

## 설정

`.env` 파일에 네이버 API 인증 정보를 설정하세요:

```
NAVER_CLIENT_ID=your_client_id
NAVER_CLIENT_SECRET=your_client_secret
TZ=Asia/Seoul
```

## 사용법

### 기본 실행 (기본 키워드로 7일 분석)

```bash
python main.py
```

### 카테고리 지정

```bash
python main.py --category 50000000 --period 7 --top-n 50
```

**카테고리 코드:**
- 50000000: 패션의류
- 50000001: 패션잡화
- 50000002: 화장품/미용
- 50000003: 디지털/가전
- 50000004: 가구/인테리어
- 50000005: 출산/육아
- 50000006: 식품
- 50000007: 스포츠/레저
- 50000008: 생활/건강
- 50000009: 여가/생활편의

### 시드 파일 사용

```bash
python main.py --seed-file keywords.txt --period 30
```

`keywords.txt` 예시:
```
나이키
아디다스
운동화
스니커즈
```

### 브랜드만 분석

```bash
python main.py --mode brand --top-n 100
```

### 블로그 지표 포함

```bash
python main.py --with-blog --period 14
```

## CLI 옵션

- `--category`: 쇼핑 카테고리 코드 (예: 50000000)
- `--period`: 분석 기간(일) (기본: 7)
- `--top-n`: 출력 상위 개수 (기본: 50)
- `--mode`: both|brand|product (기본: both)
- `--seed-file`: 초기 키워드 파일 (.txt/.csv)
- `--with-blog`: 블로그 지표 포함
- `--outdir`: 결과 저장 경로 (기본: ./out)

## 출력

`out/` 디렉토리에 다음 파일이 생성됩니다:

- `brand_trends_{category}.csv`: 브랜드 키워드 분석 결과
- `product_trends_{category}.csv`: 상품 키워드 분석 결과

### CSV 컬럼

| 컬럼 | 설명 |
|------|------|
| keyword | 키워드 |
| type | 브랜드/상품 분류 |
| search_recent_avg | 최근 기간 검색량 평균 |
| search_prev_avg | 이전 기간 검색량 평균 |
| search_wow | 검색량 증감률 |
| blog_recent | 최근 기간 블로그 언급 (옵션) |
| blog_prev | 이전 기간 블로그 언급 (옵션) |
| blog_wow | 블로그 언급 증감률 (옵션) |
| shopping_total | 쇼핑 검색 총 상품 수 |
| smartstore_est | 스마트스토어 추정 개수 |
| demand_z | 수요 Z-score |
| momentum | 모멘텀 점수 |
| opportunity_score | 기회 점수 (정렬 기준) |

## 스코어 계산 로직

```
momentum = 0.6 * search_wow + 0.4 * blog_wow

opportunity_score = demand_z * (1 / log1p(smartstore_est)) * (1 + momentum)
```

- **demand_z**: 검색량의 Z-score (다른 키워드 대비 상대적 수요)
- **momentum**: 검색량/블로그 증감률 기반 모멘텀
- **smartstore_est**: 스마트스토어 공급량 (낮을수록 기회)

## 프로젝트 구조

```
project/
  main.py                # CLI 엔트리
  core/
    datalab.py           # DataLab API
    shopping_api.py      # Shopping API
    blog_api.py          # Blog API
    classify.py          # 브랜드/상품 분류
    scoring.py           # 점수 계산
    utils.py             # 유틸리티
  data/
    brand_dictionary.txt # 브랜드 사전 (선택)
  out/                   # 결과 CSV
  .env                   # 환경변수
  requirements.txt
  README.md
```

## 에러 처리

- API 호출 간 0.2~0.3초 대기 (레이트 리밋 방지)
- HTTP 429/5xx 시 지수 백오프 재시도 (최대 3회)
- 인증 오류(401/403) 시 환경변수 확인 안내
- 빈 결과 시 0으로 처리

## 라이선스

MIT License

## 참고

- [네이버 개발자센터](https://developers.naver.com/)
- [네이버 DataLab API](https://developers.naver.com/docs/datalab/search/)
- [네이버 검색 API](https://developers.naver.com/docs/search/shopping/)
