#!/usr/bin/env python3
"""Personal spending tracker for Capital One CSV exports.

Usage: python3 tracker.py <path-to-capital-one-export.csv>
"""
import sys

from core import CATEGORIES, load_rules, parse_transactions, summarize


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

        if m["tags"]:
            print("\nTags (sub-labels within categories above):")
            for tag, amt in sorted(m["tags"].items(), key=lambda x: -x[1]):
                print(f"  {tag:<18} ${amt:>9.2f}")

        if m["defaulted"]:
            print("\n  Landed in Spending/Misc with no rule match (review rules.json if any should move):")
            for desc, amt in sorted(m["defaulted"], key=lambda x: -x[1]):
                print(f"    ${amt:>7.2f}  {desc}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 tracker.py <path-to-capital-one-export.csv>")
        sys.exit(1)

    categories, tags = load_rules()
    transactions = parse_transactions(sys.argv[1])
    months = summarize(transactions, categories, tags)
    print_report(months)


if __name__ == "__main__":
    main()
