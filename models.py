
from datetime import datetime, timezone


IDENTIFIER_FIELDS = [
    "emails",
    "telegram",
    "twitter_x",
    "phone_numbers",
    "bitcoin_wallets",
]


def create_page_document(data):
    """Validate and normalize one crawler result."""

    if not isinstance(data, dict):
        raise ValueError("Each page must be a dictionary.")

    url = data.get("url")
    if not isinstance(url, str) or not url.strip():
        raise ValueError("Page URL is required.")

    identifiers = data.get("identifiers") or {}

    normalized_identifiers = {
        field: identifiers.get(field, [])
        for field in IDENTIFIER_FIELDS
    }

    # Support the crawler's alternate wallet key if present.
    if not normalized_identifiers["bitcoin_wallets"]:
        normalized_identifiers["bitcoin_wallets"] = (
            identifiers.get("bitcoin_addresses", [])
        )

    for field, values in normalized_identifiers.items():
        if not isinstance(values, list):
            raise ValueError(
                f"identifiers.{field} must be a list."
            )

    links = data.get("internal_links", [])
    if not isinstance(links, list):
        raise ValueError("internal_links must be a list.")

    return {
        "url": url.strip(),
        "title": data.get("title", ""),
        "status": data.get("status"),
        "content_type": data.get(
            "content-type",
            data.get("content_type", "")
        ),
        "identifiers": normalized_identifiers,
        "internal_links": links,
        "crawled_at": datetime.now(timezone.utc),
        "processing_status": "pending",
        "classification": {
            "label": None,
            "confidence": None,
            "model": None,
        },
        "knowledge_graph": {
            "processed": False,
        },
    }
