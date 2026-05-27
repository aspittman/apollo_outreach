import os
import requests
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()


def get_domain(url: str) -> str | None:
    if not url:
        return None

    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path
    return domain.replace("www.", "").lower().strip("/")


def save_domain_lead_to_crm(lead, domain_offer, score, reasons, subject, body):
    crm_api_url = os.getenv("CRM_API_URL")
    crm_api_secret = os.getenv("CRM_API_SECRET")

    if not crm_api_url or not crm_api_secret:
        print("CRM not configured. Missing CRM_API_URL or CRM_API_SECRET.")
        return None

    company_name = lead.get("company") or lead.get("Company") or lead.get("organization_name") or ""
    website = lead.get("website") or lead.get("Website") or lead.get("company_website") or ""
    email = lead.get("email") or lead.get("Email") or ""
    first_name = lead.get("first_name") or lead.get("First Name") or ""
    last_name = lead.get("last_name") or lead.get("Last Name") or ""
    title = lead.get("title") or lead.get("Title") or lead.get("job_title") or ""

    payload = {
        "source_bot": "domain",
        "company": {
            "name": company_name,
            "website": website,
            "domain": get_domain(website),
            "industry": lead.get("industry") or lead.get("Industry") or "loans",
        },
        "contact": {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "title": title,
        } if email else None,
        "lead": {
            "lead_type": "domain_outreach",
            "score": int(score),
            "summary": f"Possible buyer for domain {domain_offer.get('domain')}",
            "pain_points": reasons,
        },
        "metadata": {
            "domain_for_sale": domain_offer.get("domain"),
            "domain_angle": domain_offer.get("domain_angle"),
            "ask_price": domain_offer.get("ask_price"),
            "email_subject": subject,
            "email_body": body,
            "reasons": reasons,
            "raw_lead": lead,
        }
    }

    response = requests.post(
        crm_api_url,
        json=payload,
        headers={
            "Authorization": f"Bearer {crm_api_secret}",
            "Content-Type": "application/json",
        },
        timeout=20,
    )

    if response.status_code >= 400:
        print(f"CRM save failed: {response.status_code} {response.text}")
        return None

    data = response.json()
    print(f"Saved domain lead to CRM: {data}")
    return data