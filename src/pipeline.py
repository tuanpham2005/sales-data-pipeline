"""Small-file demonstration pipeline; all monetary values use Decimal."""
import csv
import io
import re
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation

FIELDS = ["order_id", "line_id", "order_date", "product", "category",
          "quantity", "unit_price", "city", "currency"]
CLEAN_FIELDS = FIELDS + ["total_amount"]
REJECT_FIELDS = ["source_row", "raw_record", "error"]


def process_csv(text):
    reader = csv.reader(io.StringIO(text.lstrip("\ufeff")), strict=True)
    header = next(reader, None)
    if header is None or len(header) != len(FIELDS) or set(header) != set(FIELDS):
        raise ValueError("CSV header must contain each required column exactly once: "
                         + ",".join(FIELDS))
    clean, rejected, seen = [], [], set()
    for values in reader:
        source_row = reader.line_num
        if not values:
            continue
        try:
            if len(values) != len(header):
                raise ValueError("column_count_mismatch")
            row = dict(zip(header, (value.strip() for value in values)))
            if any(not row[field] for field in FIELDS):
                raise ValueError("missing_required_value")
            # Athena OpenCSVSerde reads physical lines, not multiline CSV records.
            if any("\n" in value or "\r" in value for value in row.values()):
                raise ValueError("embedded_newline_not_supported_by_athena_csv")
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", row["order_date"]):
                raise ValueError("invalid_order_date")
            try:
                date.fromisoformat(row["order_date"])
            except ValueError:
                raise ValueError("invalid_order_date") from None
            if not re.fullmatch(r"[0-9]+", row["quantity"]):
                raise ValueError("quantity_must_be_positive_integer")
            quantity = int(row["quantity"])
            if not 1 <= quantity <= 1_000_000:
                raise ValueError("quantity_out_of_range")
            try:
                price = Decimal(row["unit_price"])
            except InvalidOperation:
                raise ValueError("invalid_unit_price") from None
            if not price.is_finite() or price < 0 or price > Decimal("1000000000000"):
                raise ValueError("unit_price_out_of_range")
            if price.as_tuple().exponent < -2:
                raise ValueError("unit_price_more_than_two_decimal_places")
            if row["currency"] != "VND":
                raise ValueError("unsupported_currency_expected_VND")
            identity = (row["order_id"], row["line_id"])
            if identity in seen:
                raise ValueError("duplicate_order_line")
            seen.add(identity)
            clean.append({**row, "quantity": str(quantity),
                          "unit_price": format(price, ".2f"),
                          "total_amount": format(quantity * price, ".2f")})
        except ValueError as error:
            import json
            rejected.append({"source_row": source_row,
                             "raw_record": json.dumps(values, ensure_ascii=False),
                             "error": str(error)})
    return clean, rejected


def group_revenue(clean, field):
    groups = defaultdict(lambda: {"lines": 0, "quantity": 0, "revenue": Decimal(0)})
    for row in clean:
        group = groups[row[field]]
        group["lines"] += 1
        group["quantity"] += int(row["quantity"])
        group["revenue"] += Decimal(row["total_amount"])
    return [{field: key, "valid_lines": value["lines"],
             "total_quantity": value["quantity"],
             "revenue": format(value["revenue"], ".2f")}
            for key, value in sorted(groups.items())]


def summarize(clean, rejected):
    total = len(clean) + len(rejected)
    return {"input_rows": total, "valid_rows": len(clean),
            "rejected_rows": len(rejected),
            "rejection_rate_percent": round(100 * len(rejected) / total, 2) if total else 0,
            "distinct_valid_orders": len({row["order_id"] for row in clean}),
            "total_quantity": sum(int(row["quantity"]) for row in clean),
            "total_revenue": format(sum((Decimal(row["total_amount"]) for row in clean),
                                        Decimal(0)), ".2f"),
            "currency": "VND"}


def write_csv(path, rows, fields):
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
