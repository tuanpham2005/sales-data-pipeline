"""Run from Kiro Terminal: python run_local.py"""
import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from src.pipeline import (CLEAN_FIELDS, REJECT_FIELDS, group_revenue,
                          process_csv, summarize, write_csv)

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description="Process a small sales CSV locally.")
    parser.add_argument("--input", type=Path, default=ROOT / "data/raw/sales_sample.csv")
    args = parser.parse_args()
    try:
        if args.input.stat().st_size > 5 * 1024 * 1024:
            raise ValueError("Demo input limit is 5 MiB; use a small sample.")
        clean, rejected = process_csv(args.input.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, ValueError, csv.Error) as error:
        parser.exit(1, f"ERROR: {error}\n")

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    output = ROOT / "data/output" / run_id
    output.mkdir(parents=True, exist_ok=False)
    write_csv(output / "cleaned.csv", clean, CLEAN_FIELDS)
    write_csv(output / "rejected.csv", rejected, REJECT_FIELDS)
    for field, name in [("order_date", "revenue_by_date"),
                        ("product", "revenue_by_product"),
                        ("category", "revenue_by_category"),
                        ("city", "revenue_by_city")]:
        write_csv(output / f"{name}.csv", group_revenue(clean, field),
                  [field, "valid_lines", "total_quantity", "revenue"])
    summary = summarize(clean, rejected)
    summary.update({"run_id": run_id, "source_file": args.input.name})
    (output / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Output folder: {output}")


if __name__ == "__main__":
    main()
