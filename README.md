# Spending Tracker

Reads a Capital One transaction CSV export and prints money-in vs.
money-out per month, plus a breakdown by category.

## Usage

```
python3 tracker.py path/to/export.csv
```

No dependencies beyond a standard Python 3 install.

## How it works

- **Money in / money out** comes straight from the CSV's `Transaction Type`
  column (`Credit` = in, `Debit` = out). Interest payments and transfers
  from savings back into checking are counted as money in too — worth
  keeping in mind since that's not new income.
- **Categories** (`Subscriptions`, `Eating out`, `Taxis/Transport`,
  `Tithing`, `Giving/Generosity`, `Spending/Misc`) are assigned by matching
  keywords in the transaction description against `rules.json`. Anything
  that doesn't match a rule falls into `Spending/Misc` by default, and is
  listed separately at the end of each month's report so you can decide
  whether to add a rule for it.
- **Wise transfers** are treated as spending (matched to `Spending/Misc`
  via the `"WISE"` keyword) rather than a separate category, per how you
  use them.
- Savings is intentionally left out — it's an automatic transfer, not
  something this tool tracks as spending.

## Tuning categories

Edit `rules.json` any time. Each category maps to a list of keywords
(case-insensitive, substring match against the transaction description).
Example — to route grocery-store purchases into `Spending/Misc`
explicitly instead of the default fallback:

```json
"Spending/Misc": ["WISE", "SUPERCENTER"]
```

Re-run the script after editing — no other changes needed.

## Workflow

1. Export transactions as CSV from Capital One.
2. Run `python3 tracker.py <file>.csv`.
3. Review the per-month summary. If merchants keep landing in the
   "no rule match" list under a category they don't belong in, add a
   keyword for them in `rules.json`.
