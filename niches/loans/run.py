from pathlib import Path

from core.csv_loader import read_csv, write_csv
from core.lead_scorer import score_lead
from core.email_writer import build_subject, build_email
from niches.loans.apollo_searches import build_apollo_search_plan
from niches.loans.config import (
    DOMAINS_FILE,
    APOLLO_EXPORT_FILE,
    SEARCH_PLAN_OUTPUT,
    SCORED_LEADS_OUTPUT,
    EMAIL_DRAFTS_OUTPUT,
)


def load_loan_domains():
    rows = read_csv(DOMAINS_FILE)

    return [
        row for row in rows
        if row.get("niche", "").strip().lower() == "loans"
    ]


def generate_search_plan(domains):
    rows = []

    for domain_offer in domains:
        rows.extend(build_apollo_search_plan(domain_offer))

    write_csv(
        SEARCH_PLAN_OUTPUT,
        rows,
        [
            "domain",
            "domain_angle",
            "apollo_keywords",
            "titles",
            "locations",
            "company_size",
            "instructions",
        ],
    )

    print(f"Saved Apollo search plan to {SEARCH_PLAN_OUTPUT}")


def best_domain_match(lead, domains):
    best_domain = None
    best_score = -1
    best_reasons = []

    for domain_offer in domains:
        score, reasons = score_lead(lead, domain_offer)

        if score > best_score:
            best_domain = domain_offer
            best_score = score
            best_reasons = reasons

    return best_domain, best_score, best_reasons


def process_apollo_export(domains):
    if not Path(APOLLO_EXPORT_FILE).exists():
        print(f"No Apollo export found at {APOLLO_EXPORT_FILE}")
        print("Use the search plan in Apollo, export leads, then save the CSV there.")
        return

    leads = read_csv(APOLLO_EXPORT_FILE)

    scored_rows = []
    draft_rows = []

    for lead in leads:
        domain_offer, score, reasons = best_domain_match(lead, domains)

        if not domain_offer:
            continue

        subject = build_subject(domain_offer)
        body = build_email(lead, domain_offer)

        scored_rows.append({
            "score": score,
            "domain": domain_offer["domain"],
            "company": lead.get("company", lead.get("Company", "")),
            "first_name": lead.get("first_name", lead.get("First Name", "")),
            "last_name": lead.get("last_name", lead.get("Last Name", "")),
            "title": lead.get("title", lead.get("Title", "")),
            "email": lead.get("email", lead.get("Email", "")),
            "website": lead.get("website", lead.get("Website", "")),
            "reasons": "; ".join(reasons),
        })

        draft_rows.append({
            "score": score,
            "domain": domain_offer["domain"],
            "to_email": lead.get("email", lead.get("Email", "")),
            "company": lead.get("company", lead.get("Company", "")),
            "subject": subject,
            "body": body,
        })

    scored_rows.sort(key=lambda row: int(row["score"]), reverse=True)
    draft_rows.sort(key=lambda row: int(row["score"]), reverse=True)

    write_csv(
        SCORED_LEADS_OUTPUT,
        scored_rows,
        [
            "score",
            "domain",
            "company",
            "first_name",
            "last_name",
            "title",
            "email",
            "website",
            "reasons",
        ],
    )

    write_csv(
        EMAIL_DRAFTS_OUTPUT,
        draft_rows,
        [
            "score",
            "domain",
            "to_email",
            "company",
            "subject",
            "body",
        ],
    )

    print(f"Saved scored leads to {SCORED_LEADS_OUTPUT}")
    print(f"Saved email drafts to {EMAIL_DRAFTS_OUTPUT}")


def main():
    domains = load_loan_domains()

    if not domains:
        print(f"No loan domains found in {DOMAINS_FILE}")
        return

    generate_search_plan(domains)
    process_apollo_export(domains)


if __name__ == "__main__":
    main()