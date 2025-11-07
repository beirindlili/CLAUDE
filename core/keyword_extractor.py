"""
Automatic keyword extraction from Naver Shopping
카테고리 기반 새롭게 떠오르는 키워드 자동 추출
"""
import re
from collections import Counter
from typing import List, Set, Tuple, Dict
from datetime import datetime, timedelta
from core.shopping_api import ShoppingAPI


# 제외할 단어 (일반 단어, 불용어)
STOPWORDS = {
    '상품', '제품', '구매', '가격', '할인', '무료배송', '당일배송', '빠른배송',
    '정품', '신상', '인기', '추천', '베스트', '특가', '세트', '묶음',
    'NEW', 'SALE', 'HOT', 'EVENT', '이벤트', '증정', '사은품',
    '배송', '무료', '쿠폰', '포인트', '적립', '할인가', 'BEST',
    '오늘', '오늘만', '한정', '특별', '최저가', '파격', '대박',
    '만원', '천원', '원', '개', '종', '세트',
}


def extract_keywords_from_title(title: str) -> List[str]:
    """
    상품명에서 키워드 추출
    """
    # HTML 태그 제거
    title = re.sub(r'<[^>]+>', '', title)

    # 특수문자를 공백으로 변경
    title = re.sub(r'[^\w\s가-힣]', ' ', title)

    # 공백 기준 분리
    words = title.split()

    # 2~10글자 단어만 (너무 짧거나 긴 것 제외)
    # 숫자만 있는 단어 제외
    keywords = []
    for word in words:
        if 2 <= len(word) <= 10 and not word.isdigit():
            keywords.append(word)

    return keywords


def extract_keywords_by_period_with_sort(category_code: str, shopping_api: ShoppingAPI,
                                         seeds: List[str], sort: str = 'date') -> Counter:
    """
    특정 정렬 방식으로 상품에서 키워드 추출

    Args:
        category_code: 카테고리 코드
        shopping_api: ShoppingAPI 인스턴스
        seeds: 시드 키워드 리스트
        sort: 정렬 방식 ('date'=최신순, 'sim'=정확도순, 'asc'=가격낮은순, 'dsc'=가격높은순)

    Returns:
        키워드 빈도수 Counter
    """
    all_keywords = []

    for seed in seeds:
        try:
            # 지정된 정렬 방식으로 검색
            items = shopping_api.search_products(seed, display=100, sort=sort)

            for item in items:
                title = item.get('title', '')
                keywords = extract_keywords_from_title(title)
                all_keywords.extend(keywords)
        except Exception as e:
            pass

    # 빈도수 계산
    counter = Counter(all_keywords)

    # 불용어 제거
    for stopword in STOPWORDS:
        if stopword in counter:
            del counter[stopword]

    return counter


def find_emerging_keywords(recent_counter: Counter, prev_counter: Counter,
                          min_recent_count: int = 3) -> List[Tuple[str, float]]:
    """
    새롭게 떠오르는 키워드 찾기

    Args:
        recent_counter: 최근 기간 키워드 빈도
        prev_counter: 이전 기간 키워드 빈도
        min_recent_count: 최소 빈도수

    Returns:
        (키워드, 증가율) 튜플 리스트
    """
    emerging = []

    for keyword, recent_count in recent_counter.items():
        # 최소 빈도수 체크
        if recent_count < min_recent_count:
            continue

        # 너무 짧은 키워드 제외
        if len(keyword) < 2:
            continue

        prev_count = prev_counter.get(keyword, 0)

        # 증가율 계산
        if prev_count == 0:
            # 완전히 새로운 키워드
            growth = float('inf')
            score = recent_count * 1000  # 높은 점수
        else:
            # 증가율 계산
            growth = (recent_count - prev_count) / prev_count
            score = recent_count * (1 + growth)

        # 증가한 키워드만
        if growth > 0:
            emerging.append((keyword, score))

    # 점수순 정렬
    emerging.sort(key=lambda x: x[1], reverse=True)

    return emerging


def extract_category_keywords(category_code: str, shopping_api: ShoppingAPI,
                              max_keywords: int = 100) -> List[str]:
    """
    카테고리에서 새롭게 떠오르는 키워드 자동 추출

    전략:
    1. 최신 상품에서 키워드 추출 (sort='date')
    2. 인기 상품에서 키워드 추출 (sort='sim', 기준선)
    3. 최신에만 나타나거나 급증한 키워드 찾기

    Args:
        category_code: 카테고리 코드 (예: 50000000)
        shopping_api: ShoppingAPI 인스턴스
        max_keywords: 추출할 최대 키워드 수

    Returns:
        새롭게 떠오르는 키워드 리스트
    """
    # 카테고리별 시드 키워드 (다양하게)
    CATEGORY_SEEDS = {
        '50000000': ['여성', '남성', '의류', '패션', '데일리', '캐주얼', '스트릿', '베이직'],
        '50000001': ['가방', '신발', '액세서리', '모자', '벨트', '지갑'],
        '50000002': ['화장품', '스킨케어', '메이크업', '선케어', '토너', '세럼'],
        '50000003': ['노트북', '스마트폰', '가전', '디지털', '이어폰', '충전기'],
        '50000004': ['가구', '인테리어', '수납', '침대', '소파', '조명'],
        '50000005': ['육아', '유아', '아기', '출산', '유모차', '분유'],
        '50000006': ['식품', '건강식품', '간식', '과자', '음료', '차'],
        '50000007': ['운동', '스포츠', '헬스', '요가', '러닝', '등산'],
        '50000008': ['생활', '건강', '욕실', '주방', '청소', '수납'],
        '50000009': ['여가', '취미', '게임', '완구', '도서', '문구'],
    }

    seeds = CATEGORY_SEEDS.get(category_code, ['상품', '인기', '추천'])

    print(f"\n🔍 새롭게 떠오르는 키워드 자동 추출 (카테고리: {category_code})")
    print(f"   전략: 최신 vs 인기 비교 → 새로운 트렌드 발견")
    print(f"   시드: {', '.join(seeds[:4])}...")

    # 1. 최신 상품에서 키워드 추출 (최근 트렌드)
    print(f"\n   📈 최신 상품 분석 중 (sort=date)...")
    recent_counter = extract_keywords_by_period_with_sort(
        category_code, shopping_api, seeds, sort='date'
    )
    print(f"      추출: {len(recent_counter)}개 고유 키워드")

    # 2. 인기 상품에서 키워드 추출 (기준선)
    print(f"\n   📊 인기 상품 분석 중 (sort=sim, 기준선)...")
    baseline_counter = extract_keywords_by_period_with_sort(
        category_code, shopping_api, seeds, sort='sim'
    )
    print(f"      추출: {len(baseline_counter)}개 고유 키워드")

    # 3. 새롭게 떠오르는 키워드 찾기
    print(f"\n   🔥 급상승 키워드 분석 중...")
    emerging = find_emerging_keywords(recent_counter, baseline_counter, min_recent_count=3)

    # 상위 키워드만 선택
    top_keywords = [keyword for keyword, score in emerging[:max_keywords]]

    print(f"\n✓ {len(top_keywords)}개 새로운 트렌드 키워드 발견!")
    print(f"   (최신 상품에 많지만 인기 상품에는 적은 키워드)")

    return top_keywords
