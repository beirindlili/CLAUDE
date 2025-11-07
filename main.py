#!/usr/bin/env python3
"""
Naver Keyword Opportunity Scraper
Main CLI entry point
"""
import os
import sys
import argparse
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv

from core.datalab import DataLabAPI
from core.shopping_api import ShoppingAPI
from core.blog_api import BlogAPI
from core.classify import KeywordClassifier
from core.scoring import OpportunityScorer
from core.utils import zscore, save_csv, get_date_ranges
from core.keyword_extractor import extract_category_keywords


# Category presets
CATEGORY_PRESETS = {
    '50000000': '패션의류',
    '50000001': '패션잡화',
    '50000002': '화장품/미용',
    '50000003': '디지털/가전',
    '50000004': '가구/인테리어',
    '50000005': '출산/육아',
    '50000006': '식품',
    '50000007': '스포츠/레저',
    '50000008': '생활/건강',
    '50000009': '여가/생활편의',
    '50000010': '면세점',
}

# Default seed keywords for testing
DEFAULT_KEYWORDS = [
    '나이키', '아디다스', '뉴발란스', '컨버스', '반스',
    '운동화', '스니커즈', '런닝화', '슬립온', '키높이',
    '티셔츠', '맨투맨', '후드', '청바지', '슬랙스',
    '백팩', '크로스백', '토트백', '에코백', '여행가방'
]


def select_category_interactive() -> str:
    """
    Interactive category selection menu

    Returns:
        Selected category code
    """
    print("\n" + "=" * 60)
    print("📂 네이버 쇼핑 카테고리 선택")
    print("=" * 60)

    categories = list(CATEGORY_PRESETS.items())

    for idx, (code, name) in enumerate(categories, 1):
        print(f"  {idx}. {name} ({code})")

    print(f"  0. 카테고리 없이 진행")
    print("=" * 60)

    while True:
        try:
            choice = input("\n선택 (번호 입력): ").strip()

            if choice == '0':
                return None

            choice_num = int(choice)
            if 1 <= choice_num <= len(categories):
                selected_code = categories[choice_num - 1][0]
                selected_name = categories[choice_num - 1][1]
                print(f"✓ 선택됨: {selected_name} ({selected_code})")
                return selected_code
            else:
                print(f"⚠️  1~{len(categories)} 사이의 숫자를 입력하세요")
        except ValueError:
            print("⚠️  숫자를 입력하세요")
        except KeyboardInterrupt:
            print("\n\n❌ 취소됨")
            sys.exit(0)


def load_seed_keywords(seed_file: str = None) -> List[str]:
    """
    Load seed keywords from file or use defaults

    Args:
        seed_file: Path to seed file (.txt or .csv)

    Returns:
        List of keywords
    """
    if not seed_file:
        print("ℹ️  No seed file provided, using default keywords")
        return DEFAULT_KEYWORDS

    if not os.path.exists(seed_file):
        print(f"⚠️  Seed file not found: {seed_file}, using defaults")
        return DEFAULT_KEYWORDS

    keywords = []
    with open(seed_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Handle CSV (take first column)
                if ',' in line:
                    line = line.split(',')[0].strip()
                keywords.append(line)

    print(f"✓ Loaded {len(keywords)} keywords from {seed_file}")
    return keywords


def analyze_keyword(keyword: str, datalab: DataLabAPI, shopping: ShoppingAPI,
                    blog: BlogAPI, recent_start: str, recent_end: str,
                    prev_start: str, prev_end: str, with_blog: bool = False) -> Dict:
    """
    Analyze a single keyword

    Args:
        keyword: Keyword to analyze
        datalab: DataLab API instance
        shopping: Shopping API instance
        blog: Blog API instance
        recent_start: Recent period start date
        recent_end: Recent period end date
        prev_start: Previous period start date
        prev_end: Previous period end date
        with_blog: Include blog metrics

    Returns:
        Dictionary with keyword metrics
    """
    print(f"  Analyzing: {keyword}")

    # Get search trends
    try:
        search_recent, search_prev, search_wow = datalab.compare_recent_prev(
            keyword, recent_start, recent_end, prev_start, prev_end
        )
    except Exception as e:
        print(f"    ⚠️  Search trend error: {e}")
        search_recent, search_prev, search_wow = 0.0, 0.0, 0.0

    # Get shopping supply
    try:
        shopping_total, smartstore_est = shopping.get_shopping_supply(keyword)
    except Exception as e:
        print(f"    ⚠️  Shopping supply error: {e}")
        shopping_total, smartstore_est = 0, 0

    # Initialize result
    result = {
        'keyword': keyword,
        'search_recent_avg': round(search_recent, 2),
        'search_prev_avg': round(search_prev, 2),
        'search_wow': round(search_wow, 4),
        'shopping_total': shopping_total,
        'smartstore_est': smartstore_est,
    }

    # Get blog metrics if requested
    if with_blog:
        try:
            blog_recent, blog_prev, blog_wow = blog.compare_blog_mentions(
                keyword, recent_start, recent_end, prev_start, prev_end
            )
            result['blog_recent'] = blog_recent
            result['blog_prev'] = blog_prev
            result['blog_wow'] = round(blog_wow, 4)
        except Exception as e:
            print(f"    ⚠️  Blog metrics error: {e}")
            result['blog_recent'] = 0
            result['blog_prev'] = 0
            result['blog_wow'] = 0.0

    return result


def main():
    """Main CLI entry point"""
    # Load environment variables
    load_dotenv()

    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Naver Keyword Opportunity Scraper',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--category', type=str, default=None,
                       help='Shopping category code (e.g., 50000000)')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Interactive mode (select category from menu)')
    parser.add_argument('--period', type=int, default=7,
                       help='Analysis period in days (default: 7)')
    parser.add_argument('--top-n', type=int, default=50,
                       help='Number of top results to output (default: 50)')
    parser.add_argument('--mode', type=str, choices=['both', 'brand', 'product'],
                       default='both', help='Output mode (default: both)')
    parser.add_argument('--seed-file', type=str, default=None,
                       help='Path to seed keywords file (.txt or .csv)')
    parser.add_argument('--with-blog', action='store_true',
                       help='Include blog metrics')
    parser.add_argument('--rising-threshold', type=float, default=0.05,
                       help='Minimum search growth rate to be considered "rising" (default: 0.05 = 5%%)')
    parser.add_argument('--outdir', type=str, default='./out',
                       help='Output directory (default: ./out)')

    args = parser.parse_args()

    # Interactive category selection
    if args.interactive or args.category is None:
        args.category = select_category_interactive()

    # Ensure output directory exists
    os.makedirs(args.outdir, exist_ok=True)

    # Display configuration
    print("=" * 60)
    print("Naver Keyword Opportunity Scraper")
    print("🎯 Finding rising keywords with low competition")
    print("=" * 60)
    print(f"Category: {args.category or 'N/A'}")
    print(f"Period: {args.period} days")
    print(f"Top N: {args.top_n}")
    print(f"Mode: {args.mode}")
    print(f"Rising Threshold: {args.rising_threshold:.1%} (search growth)")
    print(f"With Blog: {args.with_blog}")
    print(f"Output: {args.outdir}")
    print("=" * 60)

    # Get date ranges
    recent_start, recent_end, prev_start, prev_end = get_date_ranges(args.period)
    print(f"Recent period: {recent_start} ~ {recent_end}")
    print(f"Previous period: {prev_start} ~ {prev_end}")
    print("=" * 60)

    # Initialize APIs
    try:
        datalab = DataLabAPI()
        shopping = ShoppingAPI()
        blog = BlogAPI() if args.with_blog else None
        classifier = KeywordClassifier(brand_dict_path='./data/brand_dictionary.txt')
        scorer = OpportunityScorer()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("Please set NAVER_CLIENT_ID and NAVER_CLIENT_SECRET in .env file")
        sys.exit(1)

    # Load keywords
    # Priority: 1) seed_file, 2) auto-extract from category
    if args.seed_file:
        print(f"📂 Loading keywords from file: {args.seed_file}")
        keywords = load_seed_keywords(args.seed_file)
    elif args.category:
        print(f"🤖 Auto-extracting keywords from category {args.category}...")
        keywords = extract_category_keywords(args.category, shopping, max_keywords=100)
    else:
        print("❌ No category or seed file specified")
        print("   Use --interactive to select category or --seed-file to load keywords")
        sys.exit(1)

    if not keywords:
        print("❌ No keywords found")
        sys.exit(1)

    print(f"\n📊 Analyzing {len(keywords)} keywords...")
    print("-" * 60)

    # Analyze all keywords
    all_results = []
    for i, keyword in enumerate(keywords, 1):
        print(f"[{i}/{len(keywords)}]", end=" ")
        result = analyze_keyword(
            keyword, datalab, shopping, blog,
            recent_start, recent_end, prev_start, prev_end,
            with_blog=args.with_blog
        )
        all_results.append(result)

    print("-" * 60)
    print(f"✓ Analysis complete: {len(all_results)} keywords")

    # Calculate demand Z-scores
    search_recent_values = [r['search_recent_avg'] for r in all_results]
    for result in all_results:
        result['demand_z'] = round(
            zscore(search_recent_values, result['search_recent_avg']), 4
        )

    # Calculate scores
    all_results = scorer.calculate_all_scores(all_results, with_blog=args.with_blog)

    # Filter rising keywords
    threshold = args.rising_threshold
    print(f"\n📈 Filtering rising keywords (search_wow > {threshold:.1%})...")
    rising_keywords = [r for r in all_results if r.get('search_wow', 0) > threshold]
    print(f"  Total keywords: {len(all_results)}")
    print(f"  Rising keywords: {len(rising_keywords)} ({len(rising_keywords)/len(all_results)*100:.1f}%)")

    # Use rising keywords only
    if rising_keywords:
        all_results = rising_keywords
        print(f"  ✓ Using {len(rising_keywords)} rising keywords")
    else:
        print(f"  ⚠️  No keywords meet threshold, using all keywords")

    # Classify keywords
    print("\n🏷️  Classifying keywords...")
    for result in all_results:
        result['type'] = classifier.classify(result['keyword'])

    # Split by type
    brand_results = [r for r in all_results if r['type'] == 'brand']
    product_results = [r for r in all_results if r['type'] == 'product']

    print(f"  Brands: {len(brand_results)}")
    print(f"  Products: {len(product_results)}")

    # Rank and save
    category_name = args.category or 'default'

    if args.mode in ['both', 'brand'] and brand_results:
        brand_results = scorer.rank_keywords(brand_results)
        brand_results = brand_results[:args.top_n]
        brand_path = os.path.join(args.outdir, f'brand_trends_{category_name}.csv')
        save_csv(brand_results, brand_path)

    if args.mode in ['both', 'product'] and product_results:
        product_results = scorer.rank_keywords(product_results)
        product_results = product_results[:args.top_n]
        product_path = os.path.join(args.outdir, f'product_trends_{category_name}.csv')
        save_csv(product_results, product_path)

    print("\n" + "=" * 60)
    print("✨ Done!")
    print("=" * 60)


if __name__ == '__main__':
    main()
