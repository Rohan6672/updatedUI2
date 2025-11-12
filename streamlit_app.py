from __future__ import annotations

import random
import uuid
import os
import re
import time
from datetime import datetime, timezone, timedelta
from textwrap import dedent
from typing import Any, Dict, List

import streamlit as st
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration ---
deployment_mode = os.getenv('deployment_mode', 'local')
if deployment_mode == 'docker':
    API_BASE_URL = os.getenv('DOCKER_FASTAPI_BASE_URL', 'http://backend:8000')
elif deployment_mode == 'local':
    API_BASE_URL = os.getenv('LOCAL_FASTAPI_BASE_URL', 'http://localhost:8000')
else:
    API_BASE_URL = 'http://localhost:8000'  # Fallback

API_TIMEOUT = int(os.getenv('API_TIMEOUT', '300'))  # 5 minutes for AI trend discovery

Trend = Dict[str, Any]

# Mock trends data for fallback when API is unavailable
MOCK_TRENDS_DATA = {
    "reportSummary": "The 2025 beauty landscape is defined by a captivating blend of contrasting aesthetics, scientific innovation, and a profound emphasis on personalization and self-expression.",
    "trends": {
        "makeupTrends": [
            {
                "id": "c1a2b3c4-d5e6-4f7g-8h9i-j0k1l2m3n4o5",
                "trend_name": "\"No-Mascara\" Full Face",
                "trend_description": "The \"No-Mascara\" Full Face trend is a deliberate move away from lash-centric looks, placing the focus on the skin and facial structure.",
                "trend_summary": "A makeup look involving a full face of foundation, concealer, blush, and defined brows, but with the intentional omission of mascara.",
                "category_associations": ["Makeup"],
                "keywords": ["No Mascara", "Minimalist Glamour", "Flawless Base"],
                "hashtags": ["#NoMascara", "#MinimalistMakeup", "#SkinFocus"]
            },
            {
                "id": "p6q7r8s9-t0u1-4v2w-3x4y-z5a6b7c8d9e0",
                "trend_name": "Black Cherry Lips",
                "trend_description": "A dramatic departure from nude tones, Black Cherry Lips embrace deep, vampy shades with a high-shine, vinyl-like finish.",
                "trend_summary": "A bold lip trend featuring deep, vampy shades of red and burgundy with a high-shine, vinyl-like finish.",
                "category_associations": ["Makeup"],
                "keywords": ["Black Cherry Lips", "Vampy Lips", "90s Makeup", "High Shine Lips"],
                "hashtags": ["#BlackCherryLips", "#VampyLip", "#GlossyLips"]
            }
        ],
        "skincareTrends": [
            {
                "id": "f1g2h3i4-j5k6-4l7m-8n9o-p0q1r2s3t4u5",
                "trend_name": "Barrier Repair 2.0",
                "trend_description": "An advanced approach to protecting and restoring the skin's natural defenses using ceramides, peptides, and postbiotics.",
                "trend_summary": "Advanced skincare focused on protecting and restoring the skin barrier with ceramides, peptides, and postbiotics.",
                "category_associations": ["Skincare"],
                "ingredients": ["Ceramides", "Peptides", "Postbiotics"],
                "keywords": ["Skin Barrier", "Barrier Repair", "Gentle Skincare"],
                "hashtags": ["#BarrierRepair", "#SkinBarrierHealth"]
            },
            {
                "id": "v6w7x8y9-z0a1-4b2c-3d4e-f5g6h7i8j9k0",
                "trend_name": "Regenerative Beauty",
                "trend_description": "Focuses on stimulating the skin's own renewal processes using ingredients like polynucleotides and growth factors.",
                "trend_summary": "A skincare trend focused on cellular health and collagen production using polynucleotides and peptides.",
                "category_associations": ["Skincare"],
                "ingredients": ["Polynucleotides", "Growth Factors", "Advanced Peptides"],
                "keywords": ["Regenerative Beauty", "Polynucleotides", "Cellular Health"],
                "hashtags": ["#RegenerativeBeauty", "#Polynucleotides"]
            }
        ],
        "hairTrends": [
            {
                "id": "l1m2n3o4-p5q6-4r7s-8t9u-v0w1x2y3z4a5",
                "trend_name": "The Baroque Bob",
                "trend_description": "A romantic, voluminous bob inspired by the Baroque era with soft waves and texture.",
                "trend_summary": "A romantic, voluminous bob featuring soft waves, texture, and an undone finish.",
                "category_associations": ["Hair"],
                "keywords": ["Baroque Bob", "Voluminous Bob", "Romantic Hair", "Wavy Bob"],
                "hashtags": ["#BaroqueBob", "#TexturedBob"]
            }
        ]
    },
    "discoveryDate": "2025-11-06",
    "totalTrendsFound": 18
}

BASE_TRENDS: List[Trend] = [
    {
        "id": "1",
        "name": "Glass Skin",
        "summary": "A dewy, luminous, and ultra-hydrated skincare aesthetic originating from Korean beauty, emphasizing translucent, poreless skin.",
        "viralityScore": 91,
        "world": "Skincare",
        "categories": ["Serums", "Primers", "Moisturizers"],
        "sentiment": "Positive",
        "sources": ["TikTok", "Vogue Beauty", "Allure"],
        "views": "57M",
        "engagement": "4.2M",
        "insights": "Glass skin continues to dominate K-beauty trends with 300% growth in searches. Consumers are seeking products with hyaluronic acid, niacinamide, and glycerin.",
        "socialMedia": {
            "tiktok": "26M posts",
            "instagram": "18M posts",
            "youtube": "13M views",
            "trending_hashtags": ["#GlassSkin", "#KBeauty", "#DewySkin"]
        },
        "imageBank": [
            "https://example.com/glass-skin-1.jpg",
            "https://example.com/glass-skin-2.jpg",
            "https://example.com/glass-skin-routine.jpg"
        ],
        "expertNotes": "Dermatologists recommend layering lightweight hydrating products and emphasizing sun protection to maintain the glass skin effect. Key ingredients: hyaluronic acid, ceramides, and snail mucin.",
        "performance": {
            "revenue_impact": "+45% in serums category",
            "conversion_rate": "8.2%",
            "top_products": ["Glow Recipe Plum Plump Serum", "COSRX Snail Mucin", "Laneige Water Bank"],
            "demographic": "Women 18-34, urban markets"
        }
    },
    {
        "id": "2",
        "name": "Barrier Repair",
        "summary": "Focus on strengthening skin's natural protective barrier using ceramides, niacinamide, and gentle formulations.",
        "viralityScore": 87,
        "world": "Skincare",
        "categories": ["Moisturizers", "Serums", "Cleansers"],
        "sentiment": "Positive",
        "sources": ["Dermstore", "TikTok", "Into The Gloss"],
        "views": "42M",
        "engagement": "3.1M",
        "insights": "Rising awareness of barrier damage from over-exfoliation and harsh products. Searches for ceramides up 250%, with consumers prioritizing gentle, repairing formulations.",
        "socialMedia": {
            "tiktok": "19M posts",
            "instagram": "14M posts",
            "youtube": "9M views",
            "trending_hashtags": ["#BarrierRepair", "#SkinBarrier", "#GentleSkincare"]
        },
        "imageBank": [
            "https://example.com/barrier-repair-1.jpg",
            "https://example.com/barrier-repair-products.jpg"
        ],
        "expertNotes": "Barrier repair focuses on restoring the skin's lipid layer. Essential ingredients include ceramides, cholesterol, and fatty acids in a 3:1:1 ratio for optimal repair.",
        "performance": {
            "revenue_impact": "+38% in moisturizers",
            "conversion_rate": "7.5%",
            "top_products": ["CeraVe Moisturizing Cream", "La Roche-Posay Cicaplast", "Dr. Jart+ Ceramidin"],
            "demographic": "Women 25-45, sensitive skin concerns"
        }
    },
    {
        "id": "3",
        "name": "Latte Makeup",
        "summary": "Warm, creamy neutral tones inspired by coffee drinks, creating a soft and natural monochromatic look.",
        "viralityScore": 84,
        "world": "Makeup",
        "categories": ["Eyeshadow", "Lipstick", "Blush"],
        "sentiment": "Positive",
        "sources": ["TikTok", "Elle Beauty", "Instagram"],
        "views": "38M",
        "engagement": "2.8M",
        "insights": "Latte makeup represents the shift towards soft, wearable neutrals. Brown-toned makeup products saw 180% increase, appealing to minimalist aesthetic and everyday wearability.",
        "socialMedia": {
            "tiktok": "22M posts",
            "instagram": "11M posts",
            "youtube": "5M views",
            "trending_hashtags": ["#LatteMakeup", "#BrownMakeup", "#NeutralMakeup"]
        },
        "imageBank": [
            "https://example.com/latte-makeup-1.jpg",
            "https://example.com/latte-look.jpg",
            "https://example.com/neutral-tones.jpg"
        ],
        "expertNotes": "Makeup artists recommend cream formulas for a cohesive latte look. Focus on warm browns, taupes, and caramels across eyes, cheeks, and lips for monochromatic harmony.",
        "performance": {
            "revenue_impact": "+42% in neutral palettes",
            "conversion_rate": "9.1%",
            "top_products": ["Charlotte Tilbury Pillow Talk", "Huda Beauty Nude Palette", "MAC Taupe"],
            "demographic": "Women 22-40, all skin tones"
        }
    },
    {
        "id": "4",
        "name": "Blush Hacking",
        "summary": "Strategic placement of blush extending to temples and nose bridge for a lifted, youthful appearance.",
        "viralityScore": 79,
        "world": "Makeup",
        "categories": ["Blush", "Bronzer"],
        "sentiment": "Positive",
        "sources": ["TikTok", "YouTube", "Refinery29"],
        "views": "31M",
        "engagement": "2.3M",
        "insights": "Blush hacking techniques gained traction as users seek non-surgical ways to achieve lifted, sculpted looks. Cream blush sales up 165%.",
        "socialMedia": {
            "tiktok": "17M posts",
            "instagram": "9M posts",
            "youtube": "5M views",
            "trending_hashtags": ["#BlushHacking", "#BlushPlacement", "#MakeupHacks"]
        },
        "imageBank": [
            "https://example.com/blush-hacking-1.jpg",
            "https://example.com/blush-placement-guide.jpg"
        ],
        "expertNotes": "Strategic blush placement creates an instant lifting effect. Apply from apples of cheeks up to temples in a C-shape. Cream formulas blend best for natural finish.",
        "performance": {
            "revenue_impact": "+35% in blush category",
            "conversion_rate": "8.8%",
            "top_products": ["Rare Beauty Soft Pinch Blush", "NARS Orgasm", "Glossier Cloud Paint"],
            "demographic": "Women 18-35, makeup enthusiasts"
        }
    },
    {
        "id": "5",
        "name": "Scalp Care",
        "summary": "Treating the scalp as skincare, using exfoliants, serums, and treatments for optimal hair health.",
        "viralityScore": 76,
        "world": "Hair",
        "categories": ["Scalp Treatments", "Shampoos", "Serums"],
        "sentiment": "Positive",
        "sources": ["TikTok", "Byrdie", "Who What Wear"],
        "views": "28M",
        "engagement": "2.1M",
        "insights": "Scalp care emerges as the 'skinification of hair'. Scalp treatment products grew 220%, driven by awareness of scalp health's impact on hair quality and growth.",
        "socialMedia": {
            "tiktok": "15M posts",
            "instagram": "8M posts",
            "youtube": "5M views",
            "trending_hashtags": ["#ScalpCare", "#HealthyScalp", "#HairCareRoutine"]
        },
        "imageBank": [
            "https://example.com/scalp-care-1.jpg",
            "https://example.com/scalp-treatment.jpg",
            "https://example.com/scalp-massage.jpg"
        ],
        "expertNotes": "Trichologists emphasize that healthy hair starts with a healthy scalp. Regular exfoliation, hydration, and targeted treatments address issues like dandruff, oiliness, and hair thinning.",
        "performance": {
            "revenue_impact": "+52% in scalp care category",
            "conversion_rate": "7.9%",
            "top_products": ["Briogeo Scalp Revival", "The Ordinary Multi-Peptide Serum", "Olaplex No.0"],
            "demographic": "Women & Men 25-45, hair health conscious"
        }
    },
    {
        "id": "6",
        "name": "Sunset Eyes",
        "summary": "Gradient eye makeup mimicking sunset colors—warm oranges, pinks, and purples blended seamlessly.",
        "viralityScore": 73,
        "world": "Makeup",
        "categories": ["Eyeshadow", "Eyeliner"],
        "sentiment": "Positive",
        "sources": ["Instagram", "Pinterest", "TikTok"],
        "views": "25M",
        "engagement": "1.9M",
        "insights": "Sunset eyes trend driven by bold, artistic makeup looks on social media. Warm-toned eyeshadow palettes sales increased 95%, particularly sunset and warm spectrum shades.",
        "socialMedia": {
            "tiktok": "13M posts",
            "instagram": "8M posts",
            "youtube": "4M views",
            "trending_hashtags": ["#SunsetEyes", "#ColorfulMakeup", "#EyeshadowLooks"]
        },
        "imageBank": [
            "https://example.com/sunset-eyes-1.jpg",
            "https://example.com/gradient-eyeshadow.jpg",
            "https://example.com/warm-eye-look.jpg"
        ],
        "expertNotes": "Achieve sunset eyes by blending warm oranges in the crease, pinks on the lid, and purple in the outer corner. Use a fluffy brush for seamless gradients and primer for vibrancy.",
        "performance": {
            "revenue_impact": "+28% in colorful palettes",
            "conversion_rate": "6.5%",
            "top_products": ["Urban Decay Naked Heat", "Huda Beauty Obsessions Warm", "Natasha Denona Sunset"],
            "demographic": "Women 18-30, creative makeup users"
        }
    },
    {
        "id": "7",
        "name": "Clean Fragrance",
        "summary": "Transparent ingredient lists, sustainable sourcing, and allergen-free formulas in perfumes and body care.",
        "viralityScore": 71,
        "world": "Fragrance",
        "categories": ["Perfume", "Body Mist"],
        "sentiment": "Positive",
        "sources": ["The Zoe Report", "Goop", "TikTok"],
        "views": "22M",
        "engagement": "1.6M",
        "insights": "Clean fragrance movement aligns with consumer demand for transparency and sustainability. Clean perfume sales grew 140%, with younger demographics prioritizing ethical sourcing.",
        "socialMedia": {
            "tiktok": "11M posts",
            "instagram": "7M posts",
            "youtube": "4M views",
            "trending_hashtags": ["#CleanFragrance", "#NonToxicBeauty", "#SustainablePerfume"]
        },
        "imageBank": [
            "https://example.com/clean-fragrance-1.jpg",
            "https://example.com/sustainable-perfume.jpg"
        ],
        "expertNotes": "Clean fragrances avoid synthetic chemicals and prioritize natural, sustainably-sourced ingredients. Look for certifications and transparent ingredient disclosure.",
        "performance": {
            "revenue_impact": "+40% in clean fragrance",
            "conversion_rate": "8.0%",
            "top_products": ["Clean Reserve", "Phlur", "Skylar"],
            "demographic": "Women 25-40, eco-conscious consumers"
        }
    },
    {
        "id": "8",
        "name": "Skin Cycling",
        "summary": "Rotating active ingredients (retinoids, acids, recovery nights) to maximize efficacy while minimizing irritation.",
        "viralityScore": 88,
        "world": "Skincare",
        "categories": ["Serums", "Night Creams", "Exfoliants"],
        "sentiment": "Positive",
        "sources": ["TikTok", "Dermstore", "Harper's Bazaar"],
        "views": "45M",
        "engagement": "3.4M",
        "insights": "Skin cycling became viral through dermatologist Dr. Whitney Bowe. Method reduces irritation while maximizing results. Retinoid and exfoliant product bundles increased 190%.",
        "socialMedia": {
            "tiktok": "24M posts",
            "instagram": "13M posts",
            "youtube": "8M views",
            "trending_hashtags": ["#SkinCycling", "#SkincareRoutine", "#RetinolRoutine"]
        },
        "imageBank": [
            "https://example.com/skin-cycling-1.jpg",
            "https://example.com/cycling-schedule.jpg",
            "https://example.com/nighttime-routine.jpg"
        ],
        "expertNotes": "Dr. Bowe's 4-night cycle: Night 1 - Exfoliation, Night 2 - Retinoid, Nights 3 & 4 - Recovery with hydration. This method prevents over-exfoliation while building tolerance.",
        "performance": {
            "revenue_impact": "+48% in night treatments",
            "conversion_rate": "8.7%",
            "top_products": ["Paula's Choice BHA", "The Ordinary Retinol", "CeraVe Skin Renewing"],
            "demographic": "Women 25-50, active skincare users"
        }
    },
    {
        "id": "9",
        "name": "Soap Brows",
        "summary": "Using brow soap or gel to create feathery, laminated eyebrows with strong hold and natural texture.",
        "viralityScore": 68,
        "world": "Makeup",
        "categories": ["Brow Gel", "Brow Soap"],
        "sentiment": "Positive",
        "sources": ["YouTube", "TikTok", "Cosmopolitan"],
        "views": "19M",
        "engagement": "1.4M",
        "insights": "Soap brows offer DIY alternative to professional brow lamination. Brow gel sales increased 125% as consumers seek fuller, feathered brow aesthetics at home.",
        "socialMedia": {
            "tiktok": "10M posts",
            "instagram": "6M posts",
            "youtube": "3M views",
            "trending_hashtags": ["#SoapBrows", "#BrowLamination", "#FluffyBrows"]
        },
        "imageBank": [
            "https://example.com/soap-brows-1.jpg",
            "https://example.com/brow-technique.jpg"
        ],
        "expertNotes": "Use a spoolie dampened with setting spray or water, swipe across brow soap, then brush upward and outward for lifted, feathered effect. Set with clear gel for all-day hold.",
        "performance": {
            "revenue_impact": "+32% in brow products",
            "conversion_rate": "7.2%",
            "top_products": ["Anastasia Brow Freeze", "Soap Brows Kit", "NYX Lift & Snatch"],
            "demographic": "Women 18-32, beauty DIY enthusiasts"
        }
    },
    {
        "id": "10",
        "name": "Hair Slugging",
        "summary": "Applying rich oils or masks to hair overnight, inspired by skincare 'slugging', for deep hydration and shine.",
        "viralityScore": 65,
        "world": "Hair",
        "categories": ["Hair Masks", "Hair Oils"],
        "sentiment": "Positive",
        "sources": ["TikTok", "Allure", "Byrdie"],
        "views": "17M",
        "engagement": "1.2M",
        "insights": "Hair slugging adapts viral skincare trend to haircare. Rich oil and mask sales grew 110% as consumers combat dryness and damage with intensive overnight treatments.",
        "socialMedia": {
            "tiktok": "9M posts",
            "instagram": "5M posts",
            "youtube": "3M views",
            "trending_hashtags": ["#HairSlugging", "#HairMask", "#HairOil"]
        },
        "imageBank": [
            "https://example.com/hair-slugging-1.jpg",
            "https://example.com/overnight-treatment.jpg"
        ],
        "expertNotes": "Apply rich oil or mask to damp hair, focusing on mid-lengths to ends. Cover with silk cap or towel overnight. Shampoo thoroughly in morning. Best for dry, damaged, or coarse hair types.",
        "performance": {
            "revenue_impact": "+38% in hair oils/masks",
            "conversion_rate": "6.8%",
            "top_products": ["Olaplex No.3", "Moroccanoil Treatment", "K18 Mask"],
            "demographic": "Women 22-45, dry/damaged hair concerns"
        }
    },
    {
        "id": "11",
        "name": "Shower Steamers",
        "summary": "Aromatherapy tablets that dissolve in the shower, offering spa-like experiences with essential oils.",
        "viralityScore": 62,
        "world": "Bath & Body",
        "categories": ["Aromatherapy", "Shower Products"],
        "sentiment": "Positive",
        "sources": ["Amazon", "TikTok", "Target"],
        "views": "15M",
        "engagement": "1.1M",
        "insights": "Shower steamers emerged as shower-friendly alternative to bath bombs. Sales increased 175% driven by self-care trend and aromatherapy benefits without requiring bathtub.",
        "socialMedia": {
            "tiktok": "8M posts",
            "instagram": "4M posts",
            "youtube": "3M views",
            "trending_hashtags": ["#ShowerSteamers", "#SelfCare", "#Aromatherapy"]
        },
        "imageBank": [
            "https://example.com/shower-steamers-1.jpg",
            "https://example.com/spa-shower.jpg"
        ],
        "expertNotes": "Place steamer on shower floor away from direct water stream. Steam activates essential oils for aromatherapy benefits. Popular scents: eucalyptus for energy, lavender for relaxation.",
        "performance": {
            "revenue_impact": "+55% in bath accessories",
            "conversion_rate": "9.3%",
            "top_products": ["BodyRestore Shower Steamers", "Cleverfy Aromatherapy", "Pure Daily Care"],
            "demographic": "Women & Men 25-55, wellness-focused"
        }
    },
    {
        "id": "12",
        "name": "Retinol Alternatives",
        "summary": "Gentler options like bakuchiol and peptides providing anti-aging benefits without retinol sensitivity.",
        "viralityScore": 82,
        "world": "Skincare",
        "categories": ["Serums", "Night Creams"],
        "sentiment": "Positive",
        "sources": ["Sephora", "Dermstore", "Vogue Beauty"],
        "views": "35M",
        "engagement": "2.6M",
        "insights": "Retinol alternatives gained traction among sensitive skin types and those seeking gentler anti-aging options. Bakuchiol product sales increased 280% year-over-year.",
        "socialMedia": {
            "tiktok": "18M posts",
            "instagram": "11M posts",
            "youtube": "6M views",
            "trending_hashtags": ["#Bakuchiol", "#RetinolAlternative", "#GentleSkincare"]
        },
        "imageBank": [
            "https://example.com/retinol-alternatives-1.jpg",
            "https://example.com/bakuchiol-serum.jpg"
        ],
        "expertNotes": "Bakuchiol offers retinol-like benefits (anti-aging, skin renewal) without irritation, suitable for sensitive skin and pregnancy. Can be used morning and night, unlike traditional retinol.",
        "performance": {
            "revenue_impact": "+62% in gentle anti-aging",
            "conversion_rate": "8.9%",
            "top_products": ["Biossance Bakuchiol Serum", "Herbivore Bakuchiol", "The Inkey List Retinol Alternative"],
            "demographic": "Women 30-55, sensitive skin types"
        }
    },
]

WORLDS = [
    "All",
    "Skincare",
    "Makeup",
    "Hair",
    "Fragrance",
    "Bath & Body",
    "Tools & Brushes",
    "Men",
    "Gifts",
    "Mini Size",
]


def check_backend_health() -> bool:
    """Check if backend is accessible"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def init_state() -> None:
    if "all_trends" not in st.session_state:
        st.session_state["all_trends"] = list(BASE_TRENDS)
    if "selected_trend" not in st.session_state:
        st.session_state["selected_trend"] = None
    if "pending_query" not in st.session_state:
        st.session_state["pending_query"] = ""
    if "web_search_loading" not in st.session_state:
        st.session_state["web_search_loading"] = False
    if "search_result" not in st.session_state:
        st.session_state["search_result"] = None
    if "backend_connected" not in st.session_state:
        st.session_state["backend_connected"] = check_backend_health()
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = str(uuid.uuid4())
    if "detail_view_trend" not in st.session_state:
        st.session_state["detail_view_trend"] = None
    if "rate_limit_until" not in st.session_state:
        st.session_state["rate_limit_until"] = None


def render_header(active_view: str) -> None:
    # Determine title based on active view
    if active_view == "Sephora Trends Dashboard":
        title = "Sephora Trends Dashboard"
    elif active_view == "Trend Discovery":
        title = "Trend Discovery"
    else:
        title = active_view  # Fallback to the view name itself

    st.markdown(
        dedent(
            f"""
            <div style="display:flex; flex-wrap:wrap; margin-bottom:1.5rem;">
                <div style="font-size:2rem; font-weight:700; margin-right:1rem;">{title}</div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    st.caption(
        f"Last updated: {datetime.now(timezone.utc).astimezone().strftime('%b %d, %Y %I:%M %p %Z')}"
    )


def render_trend_card_compact(trend: Trend) -> None:
    """Render a compact card matching the screenshot design"""
    # Card container with custom styling
    card_html = f"""
    <div style="
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        height: 280px;
        position: relative;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        transition: box-shadow 0.3s;
    ">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
            <h3 style="margin: 0; font-size: 18px; font-weight: 600; color: #1a1a1a; flex: 1;">{trend['name']}</h3>
            <div style="display: flex; align-items: center; gap: 4px; margin-left: 12px;">
                <span style="color: #ff69b4; font-size: 14px;">📈</span>
                <span style="color: #ff69b4; font-size: 24px; font-weight: 700;">{trend['viralityScore']}</span>
            </div>
        </div>
        <p style="color: #666; font-size: 13px; line-height: 1.5; margin: 0 0 12px 0; height: 60px; overflow: hidden;">
            {trend['summary'][:120]}...
        </p>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

    # Category tags
    if trend.get("categories"):
        tags_html = '<div style="margin: 8px 0; display: flex; flex-wrap: wrap; gap: 6px;">'
        for cat in trend["categories"][:4]:
            tags_html += f'<span style="background: #f0f0f0; padding: 4px 10px; border-radius: 12px; font-size: 11px; color: #555;">{cat}</span>'
        tags_html += '</div>'
        st.markdown(tags_html, unsafe_allow_html=True)

    # Bottom section: views, engagement, sources
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(f"<small style='color: #888;'>👁 {trend.get('views', 'N/A')} &nbsp;&nbsp; ❤️ {trend.get('engagement', 'N/A')}</small>", unsafe_allow_html=True)
    with col2:
        sources = trend.get("sources") or []
        if sources:
            sources_text = " ".join(sources[:2])
            st.markdown(f"<small style='color: #888; text-align: right; display: block;'>{sources_text}</small>", unsafe_allow_html=True)

    # View Full Details Button
    if st.button("View Full Details", key=f"detail_{trend['id']}", use_container_width=True):
        st.session_state["detail_view_trend"] = trend
        st.rerun()


def render_full_detail_view(trend: Trend) -> None:
    """Render full-screen detail view for a trend"""
    # Header with close button
    col1, col2 = st.columns([10, 1])
    with col1:
        st.markdown(f"# {trend['name']}")
    with col2:
        if st.button("✕", key="close_detail"):
            st.session_state["detail_view_trend"] = None
            st.rerun()

    st.markdown("")

    # Trend Summary Section
    st.markdown("**TREND SUMMARY**")
    st.write(trend.get("summary", "No summary available"))

    st.markdown("")

    # Virality and World boxes
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                <div style="color: #888; font-size: 12px;">📈 Virality</div>
                <div style="color: #ff69b4; font-size: 32px; font-weight: 700;">{trend['viralityScore']}</div>
                <div style="color: #666; font-size: 12px; margin-top: 5px;">Update ⚙️</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                <div style="color: #888; font-size: 12px;">🌍 World</div>
                <div style="font-size: 24px; font-weight: 600; margin-top: 10px; color: #000;">{trend.get('world', 'N/A')}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("")

    # Sources, Keywords, Hashtags in 3 columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**SOURCES**")
        sources = trend.get("sources", [])
        sources_html = '<div style="display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px;">'
        for source in sources:
            sources_html += f'<span style="background: white; border: 1px solid #ddd; padding: 6px 12px; border-radius: 16px; font-size: 13px; color: #000;">{source}</span>'
        sources_html += '</div>'
        st.markdown(sources_html, unsafe_allow_html=True)

    with col2:
        st.markdown("**KEYWORDS**")
        # Extract keywords from categories or create default ones
        keywords = trend.get("categories", ["beauty", "trending"])[:2]
        keywords_html = '<div style="display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px;">'
        for keyword in keywords:
            keywords_html += f'<span style="background: white; border: 1px solid #ddd; padding: 6px 12px; border-radius: 16px; font-size: 13px; color: #000;">{keyword}</span>'
        keywords_html += '</div>'
        st.markdown(keywords_html, unsafe_allow_html=True)

    with col3:
        st.markdown("**HASHTAGS**")
        social = trend.get("socialMedia", {})
        hashtags = social.get("trending_hashtags", [])
        if not hashtags and trend.get("categories"):
            # Generate hashtags from categories if none exist
            hashtags = [f"#{cat.replace(' ', '').lower()}" for cat in trend.get("categories", [])[:2]]
        hashtags_html = '<div style="display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px;">'
        for tag in hashtags:
            hashtags_html += f'<span style="background: white; border: 1px solid #ddd; padding: 6px 12px; border-radius: 16px; font-size: 13px; color: #000;">{tag}</span>'
        hashtags_html += '</div>'
        st.markdown(hashtags_html, unsafe_allow_html=True)

    st.markdown("")

    # Sentiment Section
    st.markdown("**SENTIMENT**")
    sentiment = trend.get("sentiment", "Positive")
    sentiment_color = "#d4edda" if sentiment == "Positive" else "#fff3cd"
    st.markdown(
        f"""
        <div style="background: {sentiment_color}; padding: 15px; border-radius: 8px; display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 24px;">👍</span>
            <div>
                <div style="font-weight: 600; font-size: 16px; color: #000;">{sentiment}</div>
                <div style="color: #555; font-size: 13px;">Based on social media analysis</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("")

    # External Beauty Expert Comments
    st.markdown("**EXTERNAL BEAUTY EXPERT COMMENTS** ℹ️")
    expert_notes = trend.get("expertNotes", "No expert comments available")
    st.markdown(
        f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; font-style: italic; color: #000;">
            "{expert_notes}"
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("")
    st.markdown("---")

    # Tab Navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Insights", "Social Media", "Image Bank", "Expert Notes", "Performance"])

    with tab1:
        st.markdown("### 📊 Insights")

        # Top Categories Section
        st.markdown("#### Top Categories")
        st.markdown("")
        categories_list = ["Skincare", "Makeup", "Hair Care", "Fragrance", "Body Care"]
        categories_html = '<div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; margin-bottom: 20px;">'
        for cat in categories_list:
            categories_html += f'<span style="background: white; border: 1px solid #ddd; padding: 8px 16px; border-radius: 16px; font-size: 14px; color: #000;">{cat}</span>'
        categories_html += '</div>'
        st.markdown(categories_html, unsafe_allow_html=True)

        st.markdown("---")

        # Top Sub-Categories Section
        st.markdown("#### Top Sub-Categories")
        st.markdown("")
        subcategories_list = ["Moisturizers", "Lipstick", "Serums", "Shampoo", "Foundation"]
        subcategories_html = '<div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; margin-bottom: 20px;">'
        for subcat in subcategories_list:
            subcategories_html += f'<span style="background: white; border: 1px solid #ddd; padding: 8px 16px; border-radius: 16px; font-size: 14px; color: #000;">{subcat}</span>'
        subcategories_html += '</div>'
        st.markdown(subcategories_html, unsafe_allow_html=True)

        st.markdown("---")

        # Associated Sephora Products
        st.markdown("### Associated Sephora Products")
        st.markdown("")

        # Product list
        products = [
            ("Lilly Lashes", "Lilly Lashes for Sephora Collection"),
            ("Hourglass", "Curator™ Eyeshadow Singles Air"),
            ("Lancôme", "Teint Idole Ultra Wear Care & Glow Foundation"),
            ("Bobbi Brown", "Weightless Skin Oil-Controlling Foundation")
        ]

        for brand, product in products:
            st.markdown(f"**{brand}**")
            st.caption(product)
            st.markdown("")

        st.markdown("---")

        # Top Sephora Brands
        st.markdown("### Top Sephora Brands")
        st.markdown("")

        brands = ["The Original MakeUp Eraser", "Givenchy", "Danessa Myricks Beauty", "Laura Mercier"]
        brands_html = '<div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px;">'
        for brand in brands:
            brands_html += f'<span style="background: white; border: 1px solid #ddd; padding: 8px 16px; border-radius: 16px; font-size: 14px; color: #000;">{brand}</span>'
        brands_html += '</div>'
        st.markdown(brands_html, unsafe_allow_html=True)

        st.markdown("")
        st.markdown("---")

        # Product Features (Taxonomy)
        st.markdown("### Product Features (Taxonomy)")
        st.markdown("")

        # Create 2 columns for the taxonomy
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Finish Type**")
            finish_types = ["Matte", "Satin", "Natural", "Dewy", "Radiant"]
            finish_html = '<div style="display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; margin-bottom: 20px;">'
            for finish in finish_types:
                finish_html += f'<span style="background: white; border: 1px solid #ddd; padding: 6px 12px; border-radius: 16px; font-size: 13px; color: #000;">{finish}</span>'
            finish_html += '</div>'
            st.markdown(finish_html, unsafe_allow_html=True)

            st.markdown("**Coverage**")
            coverage_types = ["Sheer", "Light", "Medium", "Full", "Buildable"]
            coverage_html = '<div style="display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; margin-bottom: 20px;">'
            for coverage in coverage_types:
                coverage_html += f'<span style="background: white; border: 1px solid #ddd; padding: 6px 12px; border-radius: 16px; font-size: 13px; color: #000;">{coverage}</span>'
            coverage_html += '</div>'
            st.markdown(coverage_html, unsafe_allow_html=True)

        with col2:
            st.markdown("**Skin Type**")
            skin_types = ["All Skin Types", "Dry", "Oily", "Combination", "Sensitive"]
            skin_html = '<div style="display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; margin-bottom: 20px;">'
            for skin in skin_types:
                skin_html += f'<span style="background: white; border: 1px solid #ddd; padding: 6px 12px; border-radius: 16px; font-size: 13px; color: #000;">{skin}</span>'
            skin_html += '</div>'
            st.markdown(skin_html, unsafe_allow_html=True)

            st.markdown("**Key Ingredients**")
            ingredients = ["Hyaluronic Acid", "Niacinamide", "SPF", "Vitamin E", "Peptides"]
            ingredients_html = '<div style="display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; margin-bottom: 20px;">'
            for ingredient in ingredients:
                ingredients_html += f'<span style="background: white; border: 1px solid #ddd; padding: 6px 12px; border-radius: 16px; font-size: 13px; color: #000;">{ingredient}</span>'
            ingredients_html += '</div>'
            st.markdown(ingredients_html, unsafe_allow_html=True)

        st.markdown("---")

        # Key Insights Section
        st.markdown("#### Key Insights")
        st.markdown("")

        # Sample insights - these would come from the trend data in production
        insights = [
            "This trend shows strong growth in the 18-34 demographic",
            "High engagement rates on TikTok and Instagram",
            "Associated products see 35% increase in searches",
            "Peak interest during Q4 holiday shopping season"
        ]

        for insight in insights:
            st.markdown(f"• {insight}")

        st.markdown("")

    with tab2:
        st.markdown("### 📱 Social Media")
        if trend.get("socialMedia"):
            social = trend["socialMedia"]

            # Create 3 columns for TikTok, Instagram, YouTube
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("#### TikTok")
                # Parse the numbers or use defaults
                tiktok_views = social.get("tiktok", "N/A")
                st.metric("Views", tiktok_views)
                st.metric("Likes", "4.2M")
                st.metric("Shares", "892K")

            with col2:
                st.markdown("#### Instagram")
                instagram_views = social.get("instagram", "N/A")
                st.metric("Views", instagram_views)
                st.metric("Likes", "3.1M")
                st.metric("Shares", "654K")

            with col3:
                st.markdown("#### YouTube")
                youtube_views = social.get("youtube", "N/A")
                st.metric("Views", youtube_views)
                st.metric("Likes", "1.2M")
                st.metric("Shares", "287K")

            st.markdown("")
            st.markdown("---")

            # Relevant Influencers Section
            st.markdown("#### Relevant Influencers")
            st.markdown("")

            # Influencer 1
            col1, col2 = st.columns([1, 5])
            with col1:
                st.markdown("**@hyramyarbro**")
            with col2:
                st.markdown("**TikTok** • 15.2M followers")
                st.caption("Posted about #glassskin with skincare routine tips")

            st.markdown("")

            # Influencer 2
            col1, col2 = st.columns([1, 5])
            with col1:
                st.markdown("**@jamescharles**")
            with col2:
                st.markdown("**YouTube** • 23.8M subscribers")
                st.caption("Created tutorial featuring Glass Skin in recent makeup video")

            st.markdown("")

            # Influencer 3
            col1, col2 = st.columns([1, 5])
            with col1:
                st.markdown("**@mikayla**")
            with col2:
                st.markdown("**TikTok** • 14.5M followers")
                st.caption("Shared first impressions and comparison with #glassskin")

            st.markdown("")

            # Influencer 4
            col1, col2 = st.columns([1, 5])
            with col1:
                st.markdown("**@hudabeauty**")
            with col2:
                st.markdown("**Instagram** • 52.1M followers")
                st.caption("Featured Glass Skin in beauty trends roundup and product recommendations")
        else:
            st.write("No social media data available")

    with tab3:
        st.markdown("### 🖼️ Image Bank")
        images = trend.get("imageBank", [])
        if images:
            for img_url in images:
                st.write(f"• {img_url}")
        else:
            st.write("No images available")

    with tab4:
        st.markdown("### 👨‍⚕️ Expert Notes")
        st.markdown("")

        # Display existing expert notes if available
        if expert_notes and expert_notes != "No expert notes available yet.":
            st.markdown("#### Existing Notes")
            st.markdown(expert_notes)
            st.markdown("---")

        # Add new expert note form
        st.markdown("#### Add New Note")
        st.markdown("")

        # Name input field
        st.markdown("**Name** *")
        expert_name = st.text_input(
            "Enter your name",
            key=f"expert_name_{trend['id']}",
            placeholder="Enter your name...",
            label_visibility="collapsed"
        )

        st.markdown("")

        # Expert note textarea
        st.markdown("**Add Expert Note** *")
        expert_note = st.text_area(
            "Share your insights about this trend",
            key=f"expert_note_{trend['id']}",
            placeholder="Share your insights about this trend...",
            height=120,
            label_visibility="collapsed"
        )

        st.markdown("")

        # Save button
        if st.button("Save Note", key=f"save_note_{trend['id']}", use_container_width=False):
            if not expert_name or not expert_note:
                st.warning("Please fill in both Name and Expert Note fields.")
            else:
                st.success(f"Note saved successfully from {expert_name}!")
                # In production, this would save to a database
                st.info("Note: In production, this note would be saved to the database.")

    with tab5:
        st.markdown("### 📈 Performance")
        st.markdown("")

        # Category Selection Dropdowns
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Select Category**")
            categories = ["Skincare", "Makeup", "Hair", "Fragrance", "Bath & Body", "Tools & Brushes", "Men", "Gifts", "Mini Size"]
            selected_category = st.selectbox(
                "Choose a category",
                categories,
                key=f"perf_category_{trend['id']}",
                label_visibility="collapsed"
            )

        with col2:
            st.markdown("**Select Sub-Category**")
            if selected_category:
                # Define subcategories based on selected category
                subcategory_map = {
                    "Skincare": ["Moisturizers", "Cleansers", "Serums", "Masks", "Sunscreen"],
                    "Makeup": ["Foundation", "Lipstick", "Eyeshadow", "Mascara", "Blush"],
                    "Hair": ["Shampoo", "Conditioner", "Styling", "Treatment", "Tools"],
                    "Fragrance": ["Perfume", "Cologne", "Body Mist", "Rollerballs"],
                    "Bath & Body": ["Body Wash", "Lotion", "Scrubs", "Bath Salts"],
                    "Tools & Brushes": ["Makeup Brushes", "Applicators", "Sponges", "Tools"],
                    "Men": ["Grooming", "Skincare", "Fragrance", "Hair Care"],
                    "Gifts": ["Gift Sets", "Value Sets", "Limited Edition"],
                    "Mini Size": ["Travel Size", "Deluxe Samples", "Minis"]
                }
                subcategories = subcategory_map.get(selected_category, ["N/A"])
                selected_subcategory = st.selectbox(
                    "Select subcategory",
                    subcategories,
                    key=f"perf_subcategory_{trend['id']}",
                    label_visibility="collapsed"
                )
            else:
                st.selectbox(
                    "Select category first",
                    [""],
                    disabled=True,
                    key=f"perf_subcategory_disabled_{trend['id']}",
                    label_visibility="collapsed"
                )

        st.markdown("")
        st.markdown("")

        # Category Performance Metrics
        st.markdown("#### Category Performance")
        st.markdown("")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                """
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                    <div style="color: #888; font-size: 14px; margin-bottom: 8px;">Sales Volume YTD</div>
                    <div style="color: #000; font-size: 36px; font-weight: 700;">1.2M</div>
                    <div style="color: #666; font-size: 13px; margin-top: 8px;">Units sold year-to-date</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                """
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                    <div style="color: #888; font-size: 14px; margin-bottom: 8px;">Sales (Dollars) YTD</div>
                    <div style="color: #000; font-size: 36px; font-weight: 700;">$24.8M</div>
                    <div style="color: #666; font-size: 13px; margin-top: 8px;">Revenue year-to-date</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("")

    # Top Categories and Sub-Categories
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Top Categories")
        categories = trend.get("categories", [])
        if categories:
            cats_html = '<div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px;">'
            for cat in categories[:4]:
                cats_html += f'<span style="background: white; border: 1px solid #ddd; padding: 8px 16px; border-radius: 16px; font-size: 14px; color: #000;">{cat}</span>'
            cats_html += '</div>'
            st.markdown(cats_html, unsafe_allow_html=True)
        else:
            st.write("No categories available")

    with col2:
        st.markdown("### Top Sub-Categories")
        # Use performance top products as subcategories if available
        subcats = trend.get("performance", {}).get("top_products", trend.get("categories", []))
        if subcats:
            subcats_html = '<div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px;">'
            for subcat in subcats[:4]:
                subcats_html += f'<span style="background: white; border: 1px solid #ddd; padding: 8px 16px; border-radius: 16px; font-size: 14px; color: #000;">{subcat}</span>'
            subcats_html += '</div>'
            st.markdown(subcats_html, unsafe_allow_html=True)
        else:
            st.write("No sub-categories available")


def render_trends_view() -> None:
    render_header("Sephora Trends Dashboard")

    trends = st.session_state["all_trends"]

    # Category tabs using pills layout
    st.markdown("### ")
    tab_cols = st.columns([1, 1, 1, 1, 1, 1, 1, 1, 1, 1])

    categories = ["All", "Skincare", "Makeup", "Hair", "Fragrance", "Bath & Body", "Tools & Brushes", "Men", "Gifts", "Mini Size"]

    if "selected_category" not in st.session_state:
        st.session_state["selected_category"] = "All"

    for idx, cat in enumerate(categories):
        with tab_cols[idx]:
            if st.button(cat, key=f"cat_{cat}", use_container_width=True):
                st.session_state["selected_category"] = cat

    selected_world = st.session_state["selected_category"]

    if selected_world == "All":
        filtered = trends
    else:
        filtered = [trend for trend in trends if trend["world"] == selected_world]

    sorted_trends = sorted(filtered, key=lambda t: t["viralityScore"], reverse=True)

    # Header
    st.markdown(f"### All Trends")
    st.markdown(f"<p style='color: #888; margin-bottom: 20px;'>{len(sorted_trends)} trends found</p>", unsafe_allow_html=True)

    # Render trends in 3-column grid
    num_trends = len(sorted_trends)
    rows = (num_trends + 2) // 3  # Calculate number of rows needed

    idx = 0
    for row in range(rows):
        cols = st.columns(3)
        for col_idx in range(3):
            if idx < num_trends:
                with cols[col_idx]:
                    render_trend_card_compact(sorted_trends[idx])
                idx += 1


def handle_search(query: str) -> None:
    query_lower = query.strip().lower()
    if not query_lower:
        st.warning("Please enter a trend name or description.")
        return

    st.session_state["pending_query"] = query
    st.session_state["web_search_loading"] = False

    match = next(
        (trend for trend in st.session_state["all_trends"] if trend["name"].lower() == query_lower),
        None,
    )

    if match:
        st.session_state["search_result"] = match
        st.success(f"Found existing trend: {match['name']}")
    else:
        st.session_state["search_result"] = None
        st.info("Trend not found in local database. You can search the open web for more insights.")


def handle_web_search() -> None:
    query = st.session_state.get("pending_query")
    if not query:
        return

    if not st.session_state.get("backend_connected"):
        st.error("Backend AI is not connected. Using mock data instead.")
        # Fallback to mock data
        new_trend = {
            "id": str(datetime.now().timestamp()),
            "name": query,
            "summary": (
                f"Emerging beauty trend discovered through web search. {query} is gaining attention online "
                "across beauty communities."
            ),
            "viralityScore": random.randint(70, 100),
            "world": "Trending",
            "categories": ["New Discovery", "Web Search"],
            "sentiment": random.choice(["Positive", "Neutral"]),
            "sources": ["Web Search", "Social Listening", "Editorial Mentions"],
            "views": "N/A",
            "engagement": "N/A",
        }
        st.session_state["all_trends"].insert(0, new_trend)
        st.session_state["search_result"] = new_trend
        st.session_state["web_search_loading"] = False
        st.success(f"Discovered new trend via web search: {query}")
        return

    st.session_state["web_search_loading"] = True

    # Call backend API for AI-powered trend discovery
    try:
        session_id = str(uuid.uuid4())
        payload = {
            "session_id": session_id,
            "user_id": st.session_state["user_id"],
            "trend_query": query,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        with st.spinner(f"🤖 AI is researching '{query}'... This may take 2-3 minutes..."):
            response = requests.post(
                f"{API_BASE_URL}/analysis/",
                json=payload,
                timeout=API_TIMEOUT
            )

            if response.status_code == 200:
                result_data = response.json()

                # Parse the AI-discovered trends
                if result_data.get("status") == "success" and result_data.get("trends"):
                    discovered_trends = []
                    for trend_data in result_data["trends"]:
                        new_trend = {
                            "id": str(datetime.now().timestamp()) + f"_{len(discovered_trends)}",
                            "name": trend_data.get("trend_name", query),
                            "summary": trend_data.get("summary", ""),
                            "viralityScore": trend_data.get("virality_score", random.randint(70, 95)),
                            "world": trend_data.get("category", "Trending"),
                            "categories": trend_data.get("subcategories", ["AI Discovery"]),
                            "sentiment": "Positive",
                            "sources": trend_data.get("sources", ["AI Research", "Web Discovery"]),
                            "views": trend_data.get("estimated_reach", "N/A"),
                            "engagement": "N/A",
                            "insights": trend_data.get("insights", ""),
                            "expertNotes": trend_data.get("expert_notes", ""),
                        }
                        discovered_trends.append(new_trend)
                        st.session_state["all_trends"].insert(0, new_trend)

                    st.session_state["search_result"] = discovered_trends[0] if discovered_trends else None
                    st.session_state["web_search_loading"] = False
                    st.success(f"✨ AI discovered {len(discovered_trends)} trend(s) for '{query}'!")
                else:
                    st.error("AI research completed but no trends were found.")
                    st.session_state["web_search_loading"] = False
            else:
                # Check if it's a rate limit error
                error_msg = f"Backend API error: {response.status_code}"
                try:
                    error_detail = response.json().get("detail", "")
                    if "429" in str(response.status_code) or "RESOURCE_EXHAUSTED" in str(error_detail):
                        # Extract retry delay from error message
                        retry_match = re.search(r'retry in ([\d.]+)s', str(error_detail))
                        if retry_match:
                            retry_seconds = float(retry_match.group(1))
                            st.session_state["rate_limit_until"] = datetime.now() + timedelta(seconds=retry_seconds)
                            st.error(f"⏱️ Rate limit reached. Please wait {int(retry_seconds)} seconds before trying again.")
                        else:
                            st.session_state["rate_limit_until"] = datetime.now() + timedelta(seconds=60)
                            st.error("⏱️ Rate limit reached. Please wait 60 seconds before trying again.")
                    elif response.status_code == 500:
                        # Use mock data for 500 errors
                        st.warning(f"⚠️ Backend API error ({response.status_code}). Showing sample trends data.")
                        discovered_trends = []

                        # Convert mock data to display format
                        all_trends = []
                        for category_key, trends_list in MOCK_TRENDS_DATA["trends"].items():
                            all_trends.extend(trends_list)

                        for trend_data in all_trends[:5]:  # Limit to first 5 trends
                            new_trend = {
                                "id": trend_data.get("id", str(datetime.now().timestamp())),
                                "name": trend_data.get("trend_name", "Unknown Trend"),
                                "summary": trend_data.get("trend_summary", trend_data.get("trend_description", "")),
                                "viralityScore": random.randint(75, 95),
                                "world": "/".join(trend_data.get("category_associations", ["Beauty"])),
                                "categories": trend_data.get("keywords", ["Trending"]),
                                "sentiment": "Positive",
                                "sources": ["Sample Data"],
                                "views": "N/A",
                                "engagement": "N/A",
                                "insights": trend_data.get("trend_description", ""),
                            }
                            discovered_trends.append(new_trend)
                            st.session_state["all_trends"].insert(0, new_trend)

                        if discovered_trends:
                            st.session_state["search_result"] = discovered_trends[0]
                            st.info(f"📊 Showing {len(discovered_trends)} sample trends. Enable the API to get live data.")
                    else:
                        st.error(error_msg)
                except:
                    st.error(error_msg)
                st.session_state["web_search_loading"] = False

    except requests.Timeout:
        st.error("⏱️ Request timed out. AI research is taking longer than expected.")
        st.session_state["web_search_loading"] = False
    except Exception as e:
        st.error(f"Error connecting to AI backend: {str(e)}")
        st.session_state["web_search_loading"] = False


def render_discover_view() -> None:
    render_header("Trend Discovery")
    st.write("Search for emerging beauty trends or discover what's next in the industry")

    st.markdown("")  # Add spacing

    query = st.text_input("Enter Trend Name or Description", st.session_state.get("pending_query", ""))
    search_clicked = st.button("Search", use_container_width=True)

    if search_clicked:
        handle_search(query)

    st.markdown("")  # Add spacing

    # Display countdown timer if rate limited
    if st.session_state.get("rate_limit_until"):
        rate_limit_time = st.session_state["rate_limit_until"]
        now = datetime.now()

        if now < rate_limit_time:
            seconds_left = int((rate_limit_time - now).total_seconds())

            # Create a placeholder for the countdown
            countdown_placeholder = st.empty()

            # Display countdown
            countdown_placeholder.warning(
                f"⏱️ **Rate Limit Active** - You can try again in **{seconds_left}** seconds"
            )

            # Auto-refresh to update countdown
            time.sleep(1)
            st.rerun()
        else:
            # Rate limit expired, clear it
            st.session_state["rate_limit_until"] = None
            st.rerun()

    # How it works section
    st.markdown("**How it works:**")
    st.markdown(
        """
        - **Case 1:** If the trend exists in our database, we'll show you the existing card with an option to update it.
        - **Case 2:** If it's a new trend, we'll run our discovery pipeline to gather insights from social media, beauty publications, and trending data.
        """
    )

    st.markdown("")  # Add spacing

    # Example Searches
    st.markdown("**Example Searches:**")
    examples = ["Glass Skin", "Blush Hacking", "Latte Makeup", "Sunset Eyes", "Skin Cycling", "Dopamine Makeup"]
    cols = st.columns(6)
    for idx, example in enumerate(examples):
        with cols[idx]:
            st.markdown(f"**{example}**")

    if st.session_state.get("web_search_loading"):
        st.info("🤖 AI is researching trends... This may take 2-3 minutes...")

    result = st.session_state.get("search_result")
    if result:
        st.markdown("---")
        st.subheader("Search Result")
        render_trend_card_compact(result)
    elif st.session_state.get("pending_query") and result is None:
        st.markdown("---")
        button_text = "✨ Discover with AI" if st.session_state.get("backend_connected") else "🔍 Search Web (Mock Data)"

        # Check if rate limited
        is_rate_limited = False
        if st.session_state.get("rate_limit_until"):
            is_rate_limited = datetime.now() < st.session_state["rate_limit_until"]

        if st.button(button_text, use_container_width=True, type="primary", disabled=is_rate_limited):
            handle_web_search()


def main() -> None:
    st.set_page_config(
        page_title="Sephora Trends Dashboard",
        page_icon="✨",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    init_state()

    # Sephora branding in sidebar
    st.sidebar.markdown("""
        <div style="text-align: left; padding: 10px 0 20px 0;">
            <h1 style="font-size: 32px; font-weight: 700; color: #000; margin: 0; font-family: sans-serif;">SEPHORA</h1>
        </div>
    """, unsafe_allow_html=True)

    # Check if we're in detail view mode
    if st.session_state.get("detail_view_trend") is not None:
        render_full_detail_view(st.session_state["detail_view_trend"])
    else:
        view = st.sidebar.radio("View", ("Sephora Trends Dashboard", "Trend Discovery"), index=0)

        st.sidebar.markdown("---")
        st.sidebar.caption(f"Total Trends: {len(st.session_state.get('all_trends', []))}")

        if view == "Sephora Trends Dashboard":
            render_trends_view()
        else:
            render_discover_view()


if __name__ == "__main__":
    main()

