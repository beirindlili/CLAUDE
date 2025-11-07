"""
Keyword classification module (Brand vs Product)
"""
import re
from typing import List, Tuple, Set, Optional


class KeywordClassifier:
    """Classify keywords as Brand or Product type"""

    # Common brand name patterns
    BRAND_PATTERNS = [
        r'^[A-Z][a-z]+$',  # Single capitalized word (e.g., Nike, Adidas)
        r'^[A-Z]{2,}$',  # All caps (e.g., IBM, HP)
        r'^[A-Z][a-z]+[A-Z][a-z]+',  # CamelCase (e.g., PlayStation, YouTube)
        r'^\d+[A-Z]',  # Number + letter (e.g., 3M)
    ]

    # Product descriptor keywords (Korean)
    PRODUCT_KEYWORDS = {
        # Clothing
        '티셔츠', '셔츠', '바지', '청바지', '원피스', '치마', '자켓', '코트', '패딩',
        '후드', '맨투맨', '가디건', '니트', '블라우스', '조끼', '점퍼',

        # Accessories
        '가방', '지갑', '벨트', '모자', '신발', '스니커즈', '구두', '샌들', '슬리퍼',
        '장갑', '목도리', '스카프', '양말', '시계', '선글라스', '안경',

        # Electronics
        '노트북', '컴퓨터', '모니터', '키보드', '마우스', '이어폰', '헤드폰', '스피커',
        '충전기', '케이블', '휴대폰', '태블릿', '카메라', 'TV', '냉장고', '세탁기',

        # Beauty & Health
        '화장품', '스킨', '로션', '크림', '에센스', '마스크팩', '선크림', '립스틱',
        '파운데이션', '샴푸', '린스', '바디워시', '치약', '영양제', '비타민',

        # Food & Beverage
        '과자', '초콜릿', '사탕', '음료', '커피', '차', '물', '우유', '라면', '쌀',

        # Home & Living
        '침대', '책상', '의자', '소파', '테이블', '수납장', '조명', '커튼', '이불',
        '베개', '쿠션', '러그', '시계', '액자', '화분', '청소기', '공기청정기',

        # Sports & Leisure
        '운동화', '운동복', '요가매트', '덤벨', '자전거', '텐트', '침낭', '등산화',

        # Common product attributes
        '세트', '키트', '팩', '묶음', '모음', '용', '형', '타입', '사이즈', '색상',
        '여성', '남성', '유아', '아동', '성인', '프리미엄', '고급', '저렴'
    }

    # Common brand names (Korean & International)
    BRAND_DICTIONARY = {
        # Fashion
        '나이키', '아디다스', '퓨마', '뉴발란스', '컨버스', '반스', '리복', '아식스',
        '언더아머', '노스페이스', '파타고니아', '콜럼비아', '유니클로', '자라', '에잇세컨즈',
        '탑텐', '스파오', 'MLB', 'NBA', '디스커버리', '빈폴', '폴로', '라코스테',
        '타미힐피거', '캘빈클라인', '리바이스', '디젤', '게스',

        # Electronics
        '삼성', '애플', 'LG', '소니', '샤오미', '화웨이', '레노버', 'HP', '델',
        '에이수스', 'MSI', '로지텍', '레이저', '젠하이저', 'JBL', '보스', 'AKG',

        # Beauty
        '설화수', '후', '아모레퍼시픽', '이니스프리', '에뛰드', '미샤', '토니모리',
        '더페이스샵', '네이처리퍼블릭', '랑콤', '에스티로더', '시세이도', '크리니크',
        '맥', '바비브라운', '샤넬', '디올', 'SK2', '라네즈', '헤라',

        # Food & Beverage
        '오리온', '롯데', '해태', '농심', '삼양', '빙그레', '매일', '남양', '서울우유',
        '코카콜라', '펩시', '네슬레', '켈로그', '동서식품',

        # Etc
        '다이소', '이케아', '무인양품', '한샘', '현대리바트', '에넥스', '일룸'
    }

    def __init__(self, brand_dict_path: Optional[str] = None):
        """
        Initialize classifier

        Args:
            brand_dict_path: Path to additional brand dictionary file (one brand per line)
        """
        self.brand_dict = set(self.BRAND_DICTIONARY)

        # Load additional brand dictionary if provided
        if brand_dict_path:
            try:
                with open(brand_dict_path, 'r', encoding='utf-8') as f:
                    additional_brands = {line.strip() for line in f if line.strip()}
                    self.brand_dict.update(additional_brands)
            except FileNotFoundError:
                print(f"⚠️  Brand dictionary not found: {brand_dict_path}")

    def is_brand(self, keyword: str) -> bool:
        """
        Check if keyword is likely a brand name

        Args:
            keyword: Keyword to classify

        Returns:
            True if likely brand, False otherwise
        """
        # Check brand dictionary
        if keyword in self.brand_dict:
            return True

        # Check for English brand patterns
        if re.match(r'^[A-Za-z0-9]+$', keyword):
            for pattern in self.BRAND_PATTERNS:
                if re.match(pattern, keyword):
                    return True

        # Check for Korean brand patterns (proper nouns, capitalized)
        # If it doesn't contain product keywords, might be brand
        has_product_keyword = any(pk in keyword for pk in self.PRODUCT_KEYWORDS)
        if not has_product_keyword and len(keyword) >= 2:
            # If it's short and doesn't have product keywords, more likely brand
            return True

        return False

    def is_product(self, keyword: str) -> bool:
        """
        Check if keyword is likely a product name

        Args:
            keyword: Keyword to classify

        Returns:
            True if likely product, False otherwise
        """
        # Check for product keywords
        for product_keyword in self.PRODUCT_KEYWORDS:
            if product_keyword in keyword:
                return True

        return False

    def classify(self, keyword: str) -> str:
        """
        Classify keyword as 'brand' or 'product'

        Args:
            keyword: Keyword to classify

        Returns:
            'brand' or 'product'
        """
        is_brand = self.is_brand(keyword)
        is_product = self.is_product(keyword)

        # If both or neither, use heuristics
        if is_brand and is_product:
            # Mixed case: if brand name appears first, classify as brand
            for brand in self.brand_dict:
                if keyword.startswith(brand):
                    return 'brand'
            return 'product'  # Default to product for mixed

        if is_brand:
            return 'brand'

        if is_product:
            return 'product'

        # Default: short keywords -> brand, long keywords -> product
        return 'brand' if len(keyword) <= 4 else 'product'

    def split_brand_product(self, keywords: List[str]) -> Tuple[List[str], List[str]]:
        """
        Split keywords into brand and product lists

        Args:
            keywords: List of keywords to classify

        Returns:
            Tuple of (brand_keywords, product_keywords)
        """
        brands = []
        products = []

        for keyword in keywords:
            if self.classify(keyword) == 'brand':
                brands.append(keyword)
            else:
                products.append(keyword)

        return brands, products
