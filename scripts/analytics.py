"""Reproduce the Glue/Athena setup and validated Power BI CSV export.

Requires requirements-cloud.txt. Uses the named browser-login profile; no keys.
"""
import argparse
import csv
import json
import sys
import time
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import boto3
from botocore.config import Config

ROOT = Path(__file__).resolve().parents[1]
BUCKET = "tuan-fcj-sales-pipeline-20261006-a7k9"
REGION = "ap-southeast-2"
WORKGROUP = "fcj-sales-workgroup"
ACCOUNT = "988079434036"
OUTPUT = f"s3://{BUCKET}/athena-results/"


def query(client, sql, workgroup=WORKGROUP):
    started = client.start_query_execution(
        QueryString=sql, WorkGroup=workgroup,
        ResultConfiguration={"OutputLocation": OUTPUT,
                             "EncryptionConfiguration": {"EncryptionOption": "SSE_S3"},
                             "ExpectedBucketOwner": ACCOUNT},
        ResultReuseConfiguration={"ResultReuseByAgeConfiguration": {"Enabled": False}})
    query_id = started["QueryExecutionId"]
    deadline = time.monotonic() + 180
    while True:
        execution = client.get_query_execution(QueryExecutionId=query_id)["QueryExecution"]
        state = execution["Status"]["State"]
        if state in {"SUCCEEDED", "FAILED", "CANCELLED"}:
            break
        if time.monotonic() > deadline:
            client.stop_query_execution(QueryExecutionId=query_id)
            raise TimeoutError(f"Query {query_id} exceeded 180 seconds and was cancelled")
        time.sleep(1)
    if state != "SUCCEEDED":
        raise RuntimeError(f"Query {query_id}: {execution['Status']}")
    records, columns = [], None
    for page in client.get_paginator("get_query_results").paginate(QueryExecutionId=query_id):
        info = page["ResultSet"]
        if columns is None:
            columns = [column["Name"] for column in info["ResultSetMetadata"]["ColumnInfo"]]
        for row in info.get("Rows", []):
            values = [item.get("VarCharValue") for item in row["Data"]]
            if not records and values == columns:
                continue
            records.append(dict(zip(columns, values)))
    evidence = {"query_id": query_id, "state": state,
                "statistics": execution.get("Statistics", {}),
                "output_location": execution["ResultConfiguration"].get("OutputLocation"),
                "rows": records}
    return evidence


def setup(client):
    groups = [group for page in client.get_paginator("list_work_groups").paginate()
              for group in page.get("WorkGroups", [])]
    if not any(group["Name"] == WORKGROUP for group in groups):
        client.create_work_group(Name=WORKGROUP, Description="FCJ small-file sales lab",
            Configuration={"EnforceWorkGroupConfiguration": True,
                "BytesScannedCutoffPerQuery": 10 * 1024 * 1024,
                "PublishCloudWatchMetricsEnabled": True,
                "ResultConfiguration": {"OutputLocation": OUTPUT,
                    "EncryptionConfiguration": {"EncryptionOption": "SSE_S3"},
                    "ExpectedBucketOwner": ACCOUNT}},
            Tags=[{"Key": "Project", "Value": "fcj-sales-data-pipeline"}])
    config = client.get_work_group(WorkGroup=WORKGROUP)["WorkGroup"]["Configuration"]
    if config.get("ResultConfiguration", {}).get("OutputLocation") != OUTPUT:
        raise ValueError("Existing workgroup has a different output location; review before changing")
    for name in ["00_database.sql", "01_cleaned_table.sql", "02_typed_view.sql"]:
        evidence = query(client, (ROOT / "sql" / name).read_text(encoding="utf-8"))
        print(f"{name}: {evidence['query_id']} SUCCEEDED")


def validate(client, expect_sample=False):
    evidence = {}
    names = ["03_quality_gate.sql", "13_profile.sql", "04_kpis.sql"]
    names += [p.name for p in sorted((ROOT / "sql").glob("0[5-9]_*.sql"))]
    names += ["10_reconciliation.sql", "11_duplicate_line_keys.sql", "12_dashboard_export.sql"]
    for name in names:
        record = query(client, (ROOT / "sql" / name).read_text(encoding="utf-8"))
        evidence[name] = record
        if name == "03_quality_gate.sql":
            gate = record["rows"][0]
            if int(gate["invalid_rows"]) or int(gate["duplicate_line_keys"]):
                raise ValueError(f"Quality gate failed; do not publish dashboard: {gate}")
        print(f"{name}: {record['query_id']} SUCCEEDED")
    if expect_sample:
        kpis = evidence["04_kpis.sql"]["rows"][0]
        assert (int(kpis["valid_line_items"]), int(kpis["distinct_orders"]),
                int(kpis["total_quantity"]), Decimal(kpis["total_revenue"])) == (6, 5, 17, Decimal("670000.00"))
        days = {row["order_date"]: Decimal(row["revenue"]) for row in evidence["05_revenue_by_date.sql"]["rows"]}
        assert days == {"2026-09-01": Decimal("150000.00"), "2026-09-02": Decimal("340000.00"), "2026-09-03": Decimal("180000.00")}
    assert all(Decimal(row["difference"]) == 0 for row in evidence["10_reconciliation.sql"]["rows"])
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["setup", "validate", "export"])
    parser.add_argument("--profile", default="codex-aws")
    parser.add_argument("--expect-sample", action="store_true")
    args = parser.parse_args()
    session = boto3.Session(profile_name=args.profile, region_name=REGION)
    config = Config(retries={"total_max_attempts": 3, "mode": "standard"}, connect_timeout=10, read_timeout=30)
    identity = session.client("sts", config=config).get_caller_identity()
    if identity["Account"] != ACCOUNT:
        raise ValueError("Wrong AWS project; expected " + ACCOUNT)
    athena = session.client("athena", config=config)
    if args.command == "setup":
        setup(athena)
        return 0
    evidence = validate(athena, args.expect_sample)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination = ROOT / "docs/evidence" / stamp
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "athena-validation.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    if args.command == "export":
        rows = evidence["12_dashboard_export.sql"]["rows"]
        if not rows:
            raise ValueError("No rows to export; existing dashboard CSV left unchanged")
        target = ROOT / "dashboard/data/sales_from_athena.csv"
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
        (target.parent / "export-metadata.json").write_text(json.dumps({
            "exported_at_utc": stamp, "query_id": evidence["12_dashboard_export.sql"]["query_id"],
            "row_count": len(rows), "source": "Athena", "refresh": "manual",
            "synthetic_dataset": True}, indent=2), encoding="utf-8")
        print("Exported verified Athena rows to " + str(target))
    return 0


if __name__ == "__main__":
    sys.exit(main())
