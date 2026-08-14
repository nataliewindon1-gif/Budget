"""Shared parsing/categorization logic for the spending tracker.

Used by both tracker.py (command-line) and app.py (web UI).
"""
import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

RULES_PATH = Path(__file__).parent / "rules.json"
DEFAULT_CATEGORY = "Spending/Misc"
CATEGORIES = [
    "Subscriptions",
    "Eating out",
    "Taxis/Transport",
    "Tithing",
    "Giving/Generosity",
    "Spending/Misc",
]


def load_rules():
    with open(RULES_PATH) as f:
        data = json.load(f)
    return data["categories"], data.get("tags", {})


def categorize(description, categories):
    """Return (category, matched) — matched is False when nothing in
    rules.json matched and the transaction fell through to the default."""
    desc = description.upper()
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword.upper() in desc:
                return category, True
    return DEFAULT_CATEGORY, False


def tag_of(description, tags):
    """Return the first matching tag name for a description, or None.
    Tags are informal sub-labels layered on top of a category (e.g.
    "Groceries" within Spending/Misc) — they don't affect categorization."""
    desc = description.upper()
    for tag, keywords in tags.items():
        for keyword in keywords:
            if keyword.upper() in desc:
                return tag
    return None


def parse_rows(reader):
    transactions = []
    for row in reader:
        transactions.append({
            "date": datetime.strptime(row["Transaction Date"], "%m/%d/%y"),
            "description": row["Transaction Description"].strip(),
            "amount": float(row["Transaction Amount"]),
            "type": row["Transaction Type"].strip(),
        })
    return transactions


def parse_transactions(csv_path):
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        return parse_rows(csv.DictReader(f))


def month_key(date):
    return date.strftime("%Y-%m")


def summarize(transactions, categories, tags):
    months = defaultdict(lambda: {
        "money_in": 0.0,
        "money_out": 0.0,
        "categories": defaultdict(float),
        "tags": defaultdict(float),
        "defaulted": [],
    })

    for txn in transactions:
        m = months[month_key(txn["date"])]
        if txn["type"] == "Credit":
            m["money_in"] += txn["amount"]
        else:
            m["money_out"] += txn["amount"]
            category, matched = categorize(txn["description"], categories)
            m["categories"][category] += txn["amount"]
            if not matched:
                m["defaulted"].append((txn["description"], txn["amount"]))
            tag = tag_of(txn["description"], tags)
            if tag:
                m["tags"][tag] += txn["amount"]
    return months
