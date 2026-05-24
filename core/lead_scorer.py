from core.domain_analyzer import detect_domain_angle
from niches.loans.buyer_profiles import BUYER_PROFILES


GOOD_TITLES = [
    "founder",
    "owner",
    "ceo",
    "president",
    "marketing",
    "business development",
    "growth",
]

BAD_TERMS = [
    "payday",
    "student loan forgiveness",
    "debt settlement",
    "credit repair",
]


def clean(value):
    return str(value or "").lower().strip()


def get_field(row, *names):
    for name in names:
        if name in row and row[name]:
            return row[name]
    return ""


def score_lead(lead, domain_offer):
    domain = domain_offer["domain"]
    angle = detect_domain_angle(domain)
    profile = BUYER_PROFILES[angle]

    company = get_field(lead, "company", "Company", "organization_name", "Organization")
    title = get_field(lead, "title", "Title", "job_title")
    email = get_field(lead, "email", "Email")
    website = get_field(lead, "website", "Website", "company_website")
    industry = get_field(lead, "industry", "Industry")
    keywords = get_field(lead, "keywords", "Keywords", "description", "Description")

    blob = " ".join([
        clean(company),
        clean(title),
        clean(website),
        clean(industry),
        clean(keywords),
    ])

    score = 0
    reasons = []

    for term in profile["good_terms"]:
        if term in blob:
            score += 15
            reasons.append(f"matches {term}")

    for good_title in GOOD_TITLES:
        if good_title in clean(title):
            score += 18
            reasons.append(f"decision-maker title: {good_title}")

    for bad in BAD_TERMS:
        if bad in blob:
            score -= 40
            reasons.append(f"bad fit: {bad}")

    if email:
        score += 20
        reasons.append("email available")

    if website:
        score += 8
        reasons.append("has website")

    if angle == "commercial_loans" and "commercial" in blob:
        score += 20
        reasons.append("commercial finance match")

    if angle == "equipment_financing" and "equipment" in blob:
        score += 25
        reasons.append("equipment financing match")

    if angle == "business_funding" and ("business funding" in blob or "small business" in blob):
        score += 25
        reasons.append("business funding match")

    return max(0, min(100, score)), reasons