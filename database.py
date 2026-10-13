
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne


# Load environment variables from the project root
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv(
    "MONGODB_DATABASE", "darkweb_crawler"
)

if not MONGODB_URI:
    raise ValueError(
        "MONGODB_URI is missing. Configure it in your .env file."
    )


# Expected identifier fields from crawler.py
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
        raise ValueError("Each page record must be a dictionary.")

    url = data.get("url")

    if not isinstance(url, str) or not url.strip():
        raise ValueError("Page URL is required.")

    identifiers = data.get("identifiers") or {}

    if not isinstance(identifiers, dict):
        raise ValueError("Identifiers must be a dictionary.")

    normalized_identifiers = {}

    for field in IDENTIFIER_FIELDS:
        normalized_identifiers[field] = identifiers.get(
            field, []
        )

    # Support the alternate wallet key if present
    if not normalized_identifiers["bitcoin_wallets"]:
        normalized_identifiers["bitcoin_wallets"] = (
            identifiers.get("bitcoin_addresses", [])
        )

    for field, values in normalized_identifiers.items():
        if not isinstance(values, list):
            raise ValueError(
                f"Identifier '{field}' must be a list."
            )

    internal_links = data.get("internal_links", [])

    if not isinstance(internal_links, list):
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
        "internal_links": internal_links,
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


def import_crawl_results(json_file=None):
    """Import crawler output into MongoDB using URL-based upserts."""

    if json_file is None:
        json_file = BASE_DIR / "crawl_results.json"
    else:
        json_file = Path(json_file)

        if not json_file.is_absolute():
            json_file = BASE_DIR / json_file

    if not json_file.exists():
        raise FileNotFoundError(
            f"Crawl results file not found: {json_file}"
        )

    with json_file.open("r", encoding="utf-8") as file:
        results = json.load(file)

    if not isinstance(results, list):
        raise ValueError(
            "Crawl results must be a JSON array."
        )

    client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=10000
    )

    try:
        client.admin.command("ping")
        print("MongoDB connected successfully!")

        db = client[DATABASE_NAME]
        pages = db["pages"]

        # One document per URL
        pages.create_index("url", unique=True)

        operations = []
        errors = 0

        for result in results:
            try:
                document = create_page_document(result)

                operations.append(
                    UpdateOne(
                        {"url": document["url"]},
                        {"$set": document},
                        upsert=True
                    )
                )

            except (ValueError, TypeError, KeyError) as error:
                errors += 1
                print("Skipping invalid record:", error)

        inserted = 0
        modified = 0

        if operations:
            outcome = pages.bulk_write(
                operations,
                ordered=False
            )

            inserted = outcome.upserted_count
            modified = outcome.modified_count

        print("\nImport completed.")
        print("Records processed:", len(operations))
        print("Documents inserted:", inserted)
        print("Documents modified:", modified)
        print("Invalid records:", errors)
        print(
            "Total documents in collection:",
            pages.count_documents({})
        )

    finally:
        client.close()


if __name__ == "__main__":
    try:
        import_crawl_results()
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as error:
        print("Import error:", error)
    except Exception as error:
        print("Database operation failed:", error)
