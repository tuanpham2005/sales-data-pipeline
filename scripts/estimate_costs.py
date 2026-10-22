"""Conservative monthly scenario; no free allowances, credits, tax, or egress."""
import csv
import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/evidence/2026-10-22"


def price(filename, group, sku, begin="0"):
    products = json.loads((EVIDENCE / filename).read_text(encoding="utf-8"))["return_value"][group]
    product = next(item for item in products if item["sku"] == sku)
    dimension = next(item for item in product["price_dimensions"] if item["beginRange"] == begin)
    return Decimal(dimension["pricePerUnit"]["USD"])


def main():
    d = Decimal
    rows = [
        ("S3 Standard storage", d("0.25"), "GB-month", price("pricing.json", "s3", "5QVJMK36NJC9G6DC")),
        ("S3 PUT/LIST", d("1000"), "request", price("pricing_extra.json", "s3_requests", "U4DFWUZRRJK76GFK")),
        ("S3 GET", d("10200"), "request", price("pricing_extra.json", "s3_requests", "ZE67FX933AEQ43H2")),
        ("Lambda requests", d("100"), "request", price("pricing_extra.json", "lambda_requests", "ZW6UHD4Q6EPUCZWU")),
        ("Lambda 256 MiB x 1s x 100", d(256) / d(1024) * d(100), "GB-second", price("pricing.json", "lambda", "4NX7CSSF3DVPXWBT")),
        ("Athena 100 queries x 100 MiB", d(100) * d(100) / d(1024 ** 2), "TB scanned", price("pricing.json", "athena", "55T4EWW7D53ERNFG")),
        ("CloudWatch standard alarms", d(2), "alarm-month", price("pricing_extra.json", "alarms", "9FZA8ZKS9CGQBUTK")),
        ("CloudWatch log ingestion", d("0.01"), "GB", price("pricing_final.json", "cw_ingestion", "VSJ57WXDQXM2VKQK")),
        ("CloudWatch log storage", d("0.01"), "GB-month", price("pricing_final.json", "cw_storage", "SXS5MH23MB3SHA9C")),
        ("Glue catalog metadata", d(10), "object-month", price("pricing_final.json", "glue", "GR6BUK2D8AMYADSU")),
        ("Glue catalog requests", d(2000), "request", price("pricing_final.json", "glue", "6PDFTXNWT277TXP4")),
    ]
    result = [{"component": name, "quantity": str(quantity), "unit": unit,
               "unit_price_usd": str(rate), "estimate_usd": str(quantity * rate)}
              for name, quantity, unit, rate in rows]
    total = sum((Decimal(row["estimate_usd"]) for row in result), Decimal(0))
    with (ROOT / "docs/cost-estimate.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result[0])); writer.writeheader(); writer.writerows(result)
    print(json.dumps({"monthly_scenario_estimate_usd": str(total.quantize(d('0.000001'))),
                      "pricing_snapshot": "2026-10-22", "region": "ap-southeast-2",
                      "excludes": ["allowances and credits", "tax", "data transfer out", "Power BI licensing", "additional queries"]}))


if __name__ == "__main__":
    main()
