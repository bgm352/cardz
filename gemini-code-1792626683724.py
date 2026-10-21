# config.py

PSA_TIERS = {
    "Standard": {"fee": 59.99, "tat_bus_days": 95, "cal_days": 147},
    "Priority": {"fee": 79.99, "tat_bus_days": 75, "cal_days": 119},
    "Express": {"fee": 199.00, "tat_bus_days": 25, "cal_days": 49},
}

MIN_ROTI_DOLLARS_PER_HR = 800.0
TOUCH_TIME_HOURS_PER_CARD = 0.20
MIN_GEM_RATE_FLOOR = 0.40
UNICORN_MIN_GEM_RATE = 0.25
MAX_SELLER_SLAB_RATIO = 0.15
MAX_PSA10_POP_CEILING = 150

NEGATIVE_EBAY_KEYWORDS = (
    '-PSA -BGS -SGC -CGC -lot -reprint -digital -break -"you pick" '
    '-"read" -"damage" -"damaged" -"crease" -"ding" -"peeling" -"off center"'
)

RED_FLAG_DESCRIPTION_PHRASES = [
    "not a professional grader",
    "not a grader",
    "grade ready",
    "psa 10?",
    "sold as is",
    "sold as-is",
    "no returns",
    "see pics for condition",
    "light surface",
    "minor print",
    "pack fresh condition",
    "judge for yourself",
]

WATCHLIST = [
    {
        "query": "Shohei Ohtani 2021 Topps Game Within The Game",
        "tier": "Standard",
        "gem_rate": 0.744,
        "psa10_pop": 163,
        "last_3_psa9": [265.00, 280.00, 285.00],
        "last_3_psa10": [510.00, 540.00, 555.00],
        "is_offseason_dip": True,
    },
    {
        "query": "Shohei Ohtani 2025 Bowman's Best Pixel Portraits",
        "tier": "Express",
        "gem_rate": 0.654,
        "psa10_pop": 120,
        "last_3_psa9": [650.00, 700.00, 715.00],
        "last_3_psa10": [720.00, 766.85, 790.00],
        "is_offseason_dip": True,
    },
    {
        "query": "Patrick Mahomes 2026 Topps 97 Gold /50 -2026",
        "tier": "Priority",
        "gem_rate": 0.520,
        "psa10_pop": 24,
        "last_3_psa9": [240.00, 265.00, 285.00],
        "last_3_psa10": [650.00, 725.00, 780.00],
        "is_offseason_dip": False,
    },
]