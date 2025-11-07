"""
Keyword extraction from Naver Shopping
카테고리 기반 키워드 자동 추출
"""
import os
import re
from collections import Counter
from typing import List, Set
from dotenv import load_dotenv
from core.shopping_api import ShoppingAPI

load_dotenv()


# 카테고리별 시드 키워드
CATEGORY_SEEDS = {
    '50000000': ['여성의류', '남성의류', '아우터', '상의', '하의', '원피스', '패딩', '코트', '티셔츠', '바지'],
    '50000001': ['가방', '지갑', '벨트', '모자', '액세서리', '신발', '운동화', '구두', '시계', '선글라스'],
    '50000002': ['화장품', '스킨케어', '메이크업', '립스틱', '쿠션', '선크림', '마스크팩', '에센스', '크림'],
    '50000003': ['노트북', '스마트폰', '태블릿', '이어폰', '키보드', '마우스', '모니터', '충전기'],
    '50000007': ['운동화', '운동복', '헬스', '요가', '등산', '캠핑', '자전거', '골프', '수영'],
}

# 제외할 키워드 (브랜드, 일반 단어)
EXCLUDE_WORDS = {
    '상품', '제품', '구매', '가격', '할인', '무료배송', '당일배송', '빠른배송',
    '정품', '신상', '인기', '추천', '베스트', '특가', '세트', '묶음',
    'NEW', 'SALE', 'HOT', 'EVENT', '이벤트', '증정', '사은품',
}


def extract_keywords_from_title(title: str) -> List[str]:
    """
    상품명에서 키워드 추출

    Args:
        title: 상품명

    Returns:
        추출된 키워드 리스트
    """
    # HTML 태그 제거
    title = re.sub(r'<[^>]+>', '', title)

    # 특수문자 제거 (한글, 영문, 숫자만)
    title = re.sub(r'[^\w\s가-힣]', ' ', title)

    # 공백 기준 분리
    words = title.split()

    # 2~10글자 단어만 (너무 짧거나 긴 것 제외)
    keywords = [w for w in words if 2 <= len(w) <= 10]

    return keywords


def extract_category_keywords(category: str, max_keywords: int = 100) -> List[str]:
    """
    카테고리에서 인기 키워드 추출

    Args:
        category: 카테고리 코드
        max_keywords: 추출할 최대 키워드 수

    Returns:
        추출된 키워드 리스트
    """
    shopping = ShoppingAPI()

    # 시드 키워드 가져오기
    seeds = CATEGORY_SEEDS.get(category, ['상품'])

    print(f"\n🔍 키워드 추출 시작 (카테고리: {category})")
    print(f"   시드 키워드: {', '.join(seeds)}")

    all_keywords = []

    # 각 시드로 검색
    for seed in seeds:
        print(f"   검색 중: {seed}...", end=' ')
        try:
            items = shopping.search_products(seed, display=100)

            # 상품명에서 키워드 추출
            for item in items:
                title = item.get('title', '')
                keywords = extract_keywords_from_title(title)
                all_keywords.extend(keywords)

            print(f"✓ ({len(items)}개 상품)")
        except Exception as e:
            print(f"✗ ({e})")

    # 빈도수 계산
    counter = Counter(all_keywords)

    # 제외 단어 필터링
    filtered = [(kw, cnt) for kw, cnt in counter.most_common()
                if kw not in EXCLUDE_WORDS and len(kw) >= 2]

    # 상위 키워드 선택
    top_keywords = [kw for kw, cnt in filtered[:max_keywords]]

    print(f"\n✓ 총 {len(top_keywords)}개 키워드 추출 완료")

    return top_keywords


if __name__ == '__main__':
    # 테스트
    category = '50000000'  # 패션의류
    keywords = extract_category_keywords(category, max_keywords=50)

    print(f"\n추출된 키워드 (상위 50개):")
    for i, kw in enumerate(keywords, 1):
        print(f"{i:3d}. {kw}")
