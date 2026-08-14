#!/usr/bin/env python3
"""Personal spending tracker for Capital One CSV exports.

Usage: python3 tracker.py <path-to-capital-one-export.csv>
"""
import csv
import json
import sys
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
        return json.load(f)


def categorize(description, rules):
    """Return (category, matched) — matched is False when nothing in
    rules.json matched and the transaction fell through to the default."""
    desc = description.upper()
    for category, keywords in rules.items():
        for keyword in keywords:
            if keyword.upper() in desc:
                return category, True
    return DEFAULT_CATEGORY, False


def parse_transactions(csv_path):
    transactions = []
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            transactions.append({
                "date": datetime.strptime(row["Transaction Date"], "%m/%d/%y"),
                "description": row["Transaction Description"].strip(),
                "amount": float(row["Transaction Amount"]),
                "type": row["Transaction Type"].strip(),
            })
    return transactions


def month_key(date):
    return date.strftime("%Y-%m")


def summarize(transactions, rules):
    months = defaultdict(lambda: {
        "money_in": 0.0,
        "money_out": 0.0,
        "categories": defaultdict(float),
        "defaulted": [],
    })

    for txn in transactions:
        m = months[month_key(txn["date"])]
        if txn["type"] == "Credit":
            m["money_in"] += txn["amount"]
        else:
            m["money_out"] += txn["amount"]
            category, matched = categorize(txn["description"], rules)
            m["categories"][category] += txn["amount"]
            if not matched:
                m["defaulted"].append((txn["description"], txn["amount"]))
    return months


def print_report(months):
    for key in sorted(months):
        m = months[key]
        print(f"\n=== {key} ===")
        print(f"Money in:  ${m['money_in']:>10.2f}")
        print(f"Money out: ${m['money_out']:>10.2f}")
        print(f"Net:       ${m['money_in'] - m['money_out']:>10.2f}")
        print("\nBy category:")
        for cat in CATEGORIES:
            amt = m["categories"].get(cat, 0.0)
            pct = (amt / m["money_out"] * 100) if m["money_out"] else 0
            print(f"  {cat:<18} ${amt:>9.2f}  ({pct:4.1f}%)")

        if m["defaulted"]:
            print("\n  Landed in Spending/Misc with no rule match (review rules.json if any should move):")
            for desc, amt in sorted(m["defaulted"], key=lambda x: -x[1]):
                print(f"    ${amt:>7.2f}  {desc}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 tracker.py <path-to-capital-one-export.csv>")
        sys.exit(1)

    rules = load_rules()
    transactions = parse_transactions(sys.argv[1])
    months = summarize(transactions, rules)
    print_report(months)


if __name__ == "__main__":
    main()
