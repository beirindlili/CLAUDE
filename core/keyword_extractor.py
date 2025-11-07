"""
Automatic keyword extraction from Naver Shopping
카테고리 기반 새로운 키워드 자동 추출
"""
import re
from collections import Counter
from typing import List, Set, Tuple
from core.shopping_api import ShoppingAPI


# 제외할 단어 (일반 단어, 불용어)
STOPWORDS = {
    '상품', '제품', '구매', '가격', '할인', '무료배송', '당일배송', '빠른배송',
    '정품', '신상', '인기', '추천', '베스트', '특가', '세트', '묶음',
    'NEW', 'SALE', 'HOT', 'EVENT', '이벤트', '증정', '사은품',
    '배송', '무료', '쿠폰', '포인트', '적립', '할인가', 'BEST',
    '오늘', '오늘만', '한정', '특별', '최저가', '파격', '대박',
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


def extract_category_keywords(category_code: str, shopping_api: ShoppingAPI,
                              max_keywords: int = 100) -> List[str]:
    """
    카테고리에서 새로운 키워드 자동 추출

    전략:
    1. 카테고리별 대표 시드 키워드로 검색
    2. 상품명에서 빈도수 높은 키워드 추출
    3. 불용어 제거 후 상위 키워드 반환

    Args:
        category_code: 카테고리 코드 (예: 50000000)
        shopping_api: ShoppingAPI 인스턴스
        max_keywords: 추출할 최대 키워드 수

    Returns:
        추출된 키워드 리스트
    """
    # 카테고리별 시드 키워드 (최소한의 시작점)
    CATEGORY_SEEDS = {
        '50000000': ['여성', '남성', '의류', '패션'],  # 패션의류
        '50000001': ['가방', '신발', '액세서리'],  # 패션잡화
        '50000002': ['화장품', '스킨케어', '메이크업'],  # 화장품/미용
        '50000003': ['노트북', '스마트폰', '가전'],  # 디지털/가전
        '50000004': ['가구', '인테리어', '수납'],  # 가구/인테리어
        '50000005': ['육아', '유아', '아기'],  # 출산/육아
        '50000006': ['식품', '건강식품', '간식'],  # 식품
        '50000007': ['운동', '스포츠', '헬스'],  # 스포츠/레저
        '50000008': ['생활', '건강', '욕실'],  # 생활/건강
        '50000009': ['여가', '취미', '게임'],  # 여가/생활편의
    }

    seeds = CATEGORY_SEEDS.get(category_code, ['상품'])

    print(f"\n🔍 자동 키워드 추출 (카테고리: {category_code})")
    print(f"   시드: {', '.join(seeds)}")

    all_keywords = []

    # 각 시드로 검색
    for seed in seeds:
        print(f"   검색 중: {seed}...", end=' ')
        try:
            # 상품 100개 검색
            items = shopping_api.search_products(seed, display=100, sort='sim')

            # 상품명에서 키워드 추출
            for item in items:
                title = item.get('title', '')
                keywords = extract_keywords_from_title(title)
                all_keywords.extend(keywords)

            print(f"✓ ({len(items)}개)")
        except Exception as e:
            print(f"✗ ({e})")

    # 빈도수 계산
    counter = Counter(all_keywords)

    # 불용어 제거 및 필터링
    filtered = []
    for word, count in counter.most_common():
        # 불용어 제외
        if word in STOPWORDS:
            continue
        # 너무 짧은 단어 제외
        if len(word) < 2:
            continue
        # 빈도수 2 이상만
        if count < 2:
            break
        filtered.append(word)

    # 상위 키워드 선택
    result = filtered[:max_keywords]

    print(f"\n✓ {len(result)}개 키워드 추출 완료")

    return result
