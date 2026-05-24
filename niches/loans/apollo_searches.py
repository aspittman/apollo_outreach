from core.domain_analyzer import detect_domain_angle
from niches.loans.buyer_profiles import BUYER_PROFILES
from niches.loans.config import TARGET_TITLES, LOCATIONS


def build_apollo_search_plan(domain_offer):
    domain = domain_offer["domain"]
    angle = detect_domain_angle(domain)
    profile = BUYER_PROFILES[angle]

    rows = []

    for buyer_type in profile["buyer_types"]:
        rows.append({
            "domain": domain,
            "domain_angle": angle,
            "apollo_keywords": buyer_type,
            "titles": ", ".join(TARGET_TITLES),
            "locations": ", ".join(LOCATIONS),
            "company_size": "1-50, 51-200",
            "instructions": (
                f"In Apollo, search for '{buyer_type}', then filter for decision-makers "
                f"with titles like Founder, Owner, CEO, Marketing Director, or Business Development."
            ),
        })

    return rows