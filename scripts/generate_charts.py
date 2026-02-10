#!/usr/bin/env python3
"""
Business Analysis - Wolt Markets Baku
Generates business-focused charts and insights from scraped data
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# Set style for professional business charts
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9

# Output directory
CHARTS_DIR = Path("charts")
CHARTS_DIR.mkdir(exist_ok=True)

def load_data():
    """Load the scraped data"""
    print("Loading data...")
    markets = pd.read_csv("data/markets_baku.csv")
    items = pd.read_csv("data/items_baku.csv")

    print(f"Loaded {len(markets)} markets and {len(items)} items")
    return markets, items

def analyze_market_categories(markets):
    """Analyze market types and categories"""
    print("\n1. Analyzing market categories...")

    # Extract tag patterns to categorize markets
    def categorize_market(tags):
        if pd.isna(tags):
            return "Other"
        tags = str(tags).lower()

        if "grocery" in tags or "supermarket" in tags:
            return "Supermarket"
        elif "alcohol" in tags or "beer" in tags or "piv" in tags:
            return "Alcohol & Beverages"
        elif "zoo" in tags or "pet" in tags:
            return "Pet Supplies"
        elif "aptek" in tags or "pharm" in tags:
            return "Pharmacy"
        elif "flower" in tags or "gul" in tags or "cicek" in tags:
            return "Flowers"
        elif "cake" in tags or "bakery" in tags or "dessert" in tags:
            return "Bakery & Desserts"
        elif "vape" in tags or "smoke" in tags or "tobacco" in tags:
            return "Tobacco & Vape"
        elif "baby" in tags or "toy" in tags:
            return "Baby & Kids"
        elif "phone" in tags or "mobile" in tags or "telekom" in tags or "aksesuar" in tags:
            return "Electronics & Accessories"
        else:
            return "Other"

    markets['category'] = markets['tags'].apply(categorize_market)
    category_counts = markets['category'].value_counts()

    # Chart 1: Market Distribution by Category
    fig, ax = plt.subplots(figsize=(12, 7))
    colors = sns.color_palette("husl", len(category_counts))
    bars = ax.barh(category_counts.index, category_counts.values, color=colors)
    ax.set_xlabel('Number of Markets', fontweight='bold')
    ax.set_title('Market Distribution by Category in Baku', fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3)

    # Add value labels
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2, f' {int(width)}',
                ha='left', va='center', fontweight='bold')

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "01_market_categories.png", dpi=300, bbox_inches='tight')
    plt.close()

    return category_counts

def analyze_pricing_strategy(items):
    """Analyze pricing and discount strategies"""
    print("\n2. Analyzing pricing strategies...")

    # Filter valid prices
    items_with_price = items[items['price'] > 0].copy()

    # Chart 2: Price Distribution
    fig, ax = plt.subplots(figsize=(12, 6))

    # Focus on reasonable price range for better visualization
    price_range = items_with_price[items_with_price['price'] <= 50]['price']

    ax.hist(price_range, bins=50, color='#2E86AB', alpha=0.7, edgecolor='black')
    ax.set_xlabel('Price (AZN)', fontweight='bold')
    ax.set_ylabel('Number of Products', fontweight='bold')
    ax.set_title('Product Price Distribution (0-50 AZN)', fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3)

    # Add median line
    median_price = price_range.median()
    ax.axvline(median_price, color='red', linestyle='--', linewidth=2, label=f'Median: {median_price:.2f} AZN')
    ax.legend()

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "02_price_distribution.png", dpi=300, bbox_inches='tight')
    plt.close()

    # Chart 3: Discount Analysis
    items_with_discount = items[items['discount_percentage'] > 0].copy()

    if len(items_with_discount) > 0:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Discount distribution
        ax1.hist(items_with_discount['discount_percentage'], bins=30, color='#E63946', alpha=0.7, edgecolor='black')
        ax1.set_xlabel('Discount Percentage (%)', fontweight='bold')
        ax1.set_ylabel('Number of Products', fontweight='bold')
        ax1.set_title('Discount Percentage Distribution', fontsize=13, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)

        # Average discount amount
        ax2.hist(items_with_discount['discount_amount'], bins=30, color='#F4A261', alpha=0.7, edgecolor='black')
        ax2.set_xlabel('Discount Amount (AZN)', fontweight='bold')
        ax2.set_ylabel('Number of Products', fontweight='bold')
        ax2.set_title('Discount Amount Distribution', fontsize=13, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(CHARTS_DIR / "03_discount_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()

        print(f"   - {len(items_with_discount)} products on discount ({len(items_with_discount)/len(items)*100:.1f}%)")
        print(f"   - Average discount: {items_with_discount['discount_percentage'].mean():.1f}%")

def analyze_ratings_performance(markets):
    """Analyze market ratings and performance"""
    print("\n3. Analyzing market ratings and performance...")

    markets_with_ratings = markets[(markets['rating_score'].notna()) & (markets['rating_volume'] > 0)].copy()

    if len(markets_with_ratings) > 0:
        # Chart 4: Rating Distribution
        fig, ax = plt.subplots(figsize=(12, 6))

        rating_counts = markets_with_ratings['rating_score'].value_counts().sort_index()
        bars = ax.bar(rating_counts.index, rating_counts.values, color='#06A77D', alpha=0.8, edgecolor='black')
        ax.set_xlabel('Rating Score', fontweight='bold')
        ax.set_ylabel('Number of Markets', fontweight='bold')
        ax.set_title('Market Rating Score Distribution', fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3)

        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontweight='bold')

        plt.tight_layout()
        plt.savefig(CHARTS_DIR / "04_rating_distribution.png", dpi=300, bbox_inches='tight')
        plt.close()

        # Chart 5: Rating vs Review Volume (Market Maturity)
        fig, ax = plt.subplots(figsize=(12, 7))

        # Filter for better visualization
        plot_data = markets_with_ratings[markets_with_ratings['rating_volume'] <= 5000].copy()

        scatter = ax.scatter(plot_data['rating_volume'], plot_data['rating_score'],
                           alpha=0.5, s=50, c=plot_data['rating_score'],
                           cmap='RdYlGn', edgecolors='black', linewidth=0.5)

        ax.set_xlabel('Number of Reviews', fontweight='bold')
        ax.set_ylabel('Rating Score', fontweight='bold')
        ax.set_title('Market Maturity: Rating vs Review Volume', fontsize=14, fontweight='bold', pad=20)
        ax.grid(alpha=0.3)

        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Rating Score', fontweight='bold')

        plt.tight_layout()
        plt.savefig(CHARTS_DIR / "05_rating_vs_reviews.png", dpi=300, bbox_inches='tight')
        plt.close()

def analyze_delivery_coverage(markets):
    """Analyze delivery fees and coverage"""
    print("\n4. Analyzing delivery coverage...")

    delivering_markets = markets[markets['delivers'] == True].copy()

    # Chart 6: Delivery Fee Distribution
    fig, ax = plt.subplots(figsize=(12, 6))

    delivery_fee_counts = delivering_markets['delivery_price'].value_counts().sort_index()
    bars = ax.bar(delivery_fee_counts.index, delivery_fee_counts.values,
                   color='#4361EE', alpha=0.8, edgecolor='black')
    ax.set_xlabel('Delivery Fee (AZN)', fontweight='bold')
    ax.set_ylabel('Number of Markets', fontweight='bold')
    ax.set_title('Delivery Fee Distribution Across Markets', fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3)

    # Add value labels
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "06_delivery_fees.png", dpi=300, bbox_inches='tight')
    plt.close()

    # Chart 7: Delivery Time Estimates
    fig, ax = plt.subplots(figsize=(12, 6))

    estimate_counts = delivering_markets['estimate_minutes'].value_counts().sort_index()
    bars = ax.bar(estimate_counts.index, estimate_counts.values,
                   color='#F72585', alpha=0.8, edgecolor='black')
    ax.set_xlabel('Estimated Delivery Time (Minutes)', fontweight='bold')
    ax.set_ylabel('Number of Markets', fontweight='bold')
    ax.set_title('Delivery Time Distribution', fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "07_delivery_time.png", dpi=300, bbox_inches='tight')
    plt.close()

def analyze_product_categories(items):
    """Analyze product categories and sections"""
    print("\n5. Analyzing product categories...")

    # Top sections by product count
    section_counts = items['section_name'].value_counts().head(15)

    # Chart 8: Top Product Sections
    fig, ax = plt.subplots(figsize=(12, 8))
    colors = sns.color_palette("viridis", len(section_counts))
    bars = ax.barh(section_counts.index, section_counts.values, color=colors)
    ax.set_xlabel('Number of Products', fontweight='bold')
    ax.set_title('Top 15 Product Sections by Volume', fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3)

    # Add value labels
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2, f' {int(width)}',
                ha='left', va='center', fontweight='bold')

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "08_top_product_sections.png", dpi=300, bbox_inches='tight')
    plt.close()

def analyze_market_concentration(items, markets):
    """Analyze market share and concentration"""
    print("\n6. Analyzing market concentration...")

    # Products per venue
    products_per_venue = items.groupby('venue_name').size().sort_values(ascending=False).head(20)

    # Chart 9: Top Markets by Product Volume
    fig, ax = plt.subplots(figsize=(12, 8))
    colors = sns.color_palette("coolwarm", len(products_per_venue))
    bars = ax.barh(range(len(products_per_venue)), products_per_venue.values, color=colors)
    ax.set_yticks(range(len(products_per_venue)))
    ax.set_yticklabels(products_per_venue.index, fontsize=9)
    ax.set_xlabel('Number of Products', fontweight='bold')
    ax.set_title('Top 20 Markets by Product Catalog Size', fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3)

    # Add value labels
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2, f' {int(width)}',
                ha='left', va='center', fontsize=8, fontweight='bold')

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "09_top_markets_by_products.png", dpi=300, bbox_inches='tight')
    plt.close()

def analyze_availability_stock(items):
    """Analyze product availability and stock patterns"""
    print("\n7. Analyzing product availability...")

    # Availability statistics
    available_count = items['is_available'].sum()
    unavailable_count = len(items) - available_count

    # Chart 10: Product Availability Status
    fig, ax = plt.subplots(figsize=(10, 6))

    availability_data = pd.Series({
        'Available': available_count,
        'Unavailable': unavailable_count
    })

    bars = ax.bar(availability_data.index, availability_data.values,
                   color=['#06A77D', '#E63946'], alpha=0.8, edgecolor='black', linewidth=2)
    ax.set_ylabel('Number of Products', fontweight='bold')
    ax.set_title('Product Availability Status', fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3)

    # Add value labels and percentages
    total = availability_data.sum()
    for bar in bars:
        height = bar.get_height()
        percentage = (height / total) * 100
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}\n({percentage:.1f}%)',
                ha='center', va='bottom', fontweight='bold', fontsize=11)

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "10_product_availability.png", dpi=300, bbox_inches='tight')
    plt.close()

def analyze_price_by_category(items, markets):
    """Analyze pricing patterns across different market categories"""
    print("\n8. Analyzing price patterns by market category...")

    # Merge items with market categories
    def categorize_market(tags):
        if pd.isna(tags):
            return "Other"
        tags = str(tags).lower()

        if "grocery" in tags or "supermarket" in tags:
            return "Supermarket"
        elif "alcohol" in tags or "beer" in tags:
            return "Alcohol & Beverages"
        elif "zoo" in tags or "pet" in tags:
            return "Pet Supplies"
        elif "aptek" in tags or "pharm" in tags:
            return "Pharmacy"
        elif "flower" in tags or "gul" in tags:
            return "Flowers"
        elif "cake" in tags or "bakery" in tags or "dessert" in tags:
            return "Bakery & Desserts"
        else:
            return "Other"

    markets['category'] = markets['tags'].apply(categorize_market)
    items_with_category = items.merge(markets[['venue_id', 'category']], on='venue_id', how='left')

    # Calculate average price by category
    items_valid = items_with_category[(items_with_category['price'] > 0) & (items_with_category['price'] <= 100)].copy()
    avg_price_by_category = items_valid.groupby('category')['price'].agg(['mean', 'median', 'count']).sort_values('mean', ascending=False)

    # Filter categories with sufficient data
    avg_price_by_category = avg_price_by_category[avg_price_by_category['count'] >= 50]

    # Chart 11: Average Price by Category
    fig, ax = plt.subplots(figsize=(12, 7))

    x = range(len(avg_price_by_category))
    width = 0.35

    bars1 = ax.bar([i - width/2 for i in x], avg_price_by_category['mean'], width,
                    label='Mean Price', color='#4361EE', alpha=0.8, edgecolor='black')
    bars2 = ax.bar([i + width/2 for i in x], avg_price_by_category['median'], width,
                    label='Median Price', color='#F72585', alpha=0.8, edgecolor='black')

    ax.set_xlabel('Market Category', fontweight='bold')
    ax.set_ylabel('Price (AZN)', fontweight='bold')
    ax.set_title('Average Product Pricing by Market Category', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(avg_price_by_category.index, rotation=45, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "11_price_by_category.png", dpi=300, bbox_inches='tight')
    plt.close()

def generate_summary_statistics(markets, items):
    """Generate key business metrics"""
    print("\n9. Generating summary statistics...")

    stats = {
        'total_markets': len(markets),
        'total_products': len(items),
        'avg_products_per_market': len(items) / len(markets),
        'markets_with_delivery': markets['delivers'].sum(),
        'delivery_penetration': (markets['delivers'].sum() / len(markets)) * 100,
        'avg_delivery_fee': markets[markets['delivery_price'] > 0]['delivery_price'].mean(),
        'markets_with_ratings': markets[markets['rating_score'].notna()].shape[0],
        'avg_rating': markets[markets['rating_score'].notna()]['rating_score'].mean(),
        'products_on_discount': items[items['discount_percentage'] > 0].shape[0],
        'discount_penetration': (items[items['discount_percentage'] > 0].shape[0] / len(items)) * 100,
        'avg_discount_percentage': items[items['discount_percentage'] > 0]['discount_percentage'].mean(),
        'median_price': items[items['price'] > 0]['price'].median(),
        'avg_price': items[items['price'] > 0]['price'].mean(),
        'product_availability_rate': (items['is_available'].sum() / len(items)) * 100,
    }

    # Chart 12: Key Business Metrics Dashboard
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Key Business Metrics Overview', fontsize=16, fontweight='bold', y=0.995)

    # Metric 1: Market Coverage
    ax1.text(0.5, 0.7, f"{stats['total_markets']:,}", ha='center', fontsize=48, fontweight='bold', color='#2E86AB')
    ax1.text(0.5, 0.4, 'Total Markets', ha='center', fontsize=16, fontweight='bold')
    ax1.text(0.5, 0.25, f"{stats['delivery_penetration']:.1f}% offer delivery", ha='center', fontsize=12, color='#666')
    ax1.axis('off')
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)

    # Metric 2: Product Catalog
    ax2.text(0.5, 0.7, f"{stats['total_products']:,}", ha='center', fontsize=48, fontweight='bold', color='#06A77D')
    ax2.text(0.5, 0.4, 'Total Products', ha='center', fontsize=16, fontweight='bold')
    ax2.text(0.5, 0.25, f"{stats['avg_products_per_market']:.0f} avg per market", ha='center', fontsize=12, color='#666')
    ax2.axis('off')
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)

    # Metric 3: Customer Satisfaction
    ax3.text(0.5, 0.7, f"{stats['avg_rating']:.1f}/10", ha='center', fontsize=48, fontweight='bold', color='#F4A261')
    ax3.text(0.5, 0.4, 'Average Rating', ha='center', fontsize=16, fontweight='bold')
    ax3.text(0.5, 0.25, f"{stats['markets_with_ratings']} markets rated", ha='center', fontsize=12, color='#666')
    ax3.axis('off')
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)

    # Metric 4: Promotions
    ax4.text(0.5, 0.7, f"{stats['discount_penetration']:.1f}%", ha='center', fontsize=48, fontweight='bold', color='#E63946')
    ax4.text(0.5, 0.4, 'Products on Discount', ha='center', fontsize=16, fontweight='bold')
    ax4.text(0.5, 0.25, f"Avg discount: {stats['avg_discount_percentage']:.1f}%", ha='center', fontsize=12, color='#666')
    ax4.axis('off')
    ax4.set_xlim(0, 1)
    ax4.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "12_key_metrics_dashboard.png", dpi=300, bbox_inches='tight')
    plt.close()

    return stats

def main():
    """Main analysis function"""
    print("="*60)
    print("WOLT MARKETS BAKU - BUSINESS ANALYSIS")
    print("="*60)

    # Load data
    markets, items = load_data()

    # Run all analyses
    analyze_market_categories(markets)
    analyze_pricing_strategy(items)
    analyze_ratings_performance(markets)
    analyze_delivery_coverage(markets)
    analyze_product_categories(items)
    analyze_market_concentration(items, markets)
    analyze_availability_stock(items)
    analyze_price_by_category(items, markets)
    stats = generate_summary_statistics(markets, items)

    print("\n" + "="*60)
    print("ANALYSIS COMPLETE!")
    print("="*60)
    print(f"\nGenerated 12 business charts in '{CHARTS_DIR}/' directory")
    print("\nKey Findings:")
    print(f"  • {stats['total_markets']:,} markets analyzed")
    print(f"  • {stats['total_products']:,} products cataloged")
    print(f"  • {stats['delivery_penetration']:.1f}% delivery coverage")
    print(f"  • {stats['avg_rating']:.1f}/10 average rating")
    print(f"  • {stats['discount_penetration']:.1f}% products on promotion")
    print(f"  • {stats['product_availability_rate']:.1f}% product availability")
    print("\n")

if __name__ == "__main__":
    main()
