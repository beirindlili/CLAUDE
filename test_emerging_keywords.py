#!/usr/bin/env python3
"""
새롭게 떠오르는 키워드 추출 테스트
"""
import os
from dotenv import load_dotenv
from core.keyword_extractor import extract_category_keywords
from core.shopping_api import ShoppingAPI

load_dotenv()

# ShoppingAPI 초기화
shopping = ShoppingAPI()

# 패션의류 카테고리에서 새로운 트렌드 키워드 추출
category = '50000000'
print(f"=" * 70)
print(f"🔍 새롭게 떠오르는 키워드 자동 추출 테스트")
print(f"   카테고리: {category} (패션의류)")
print(f"=" * 70)

keywords = extract_category_keywords(category, shopping, max_keywords=30)

print(f"\n" + "=" * 70)
print(f"📊 추출된 새로운 트렌드 키워드 (총 {len(keywords)}개)")
print(f"=" * 70)
for i, kw in enumerate(keywords, 1):
    print(f"{i:3d}. {kw}")

print(f"\n✅ 테스트 완료!")
print(f"   → 이 키워드들은 최신 상품에 많이 나타나지만")
print(f"   → 인기 상품(기준선)에는 적게 나타나는 '새로운 트렌드'입니다")
