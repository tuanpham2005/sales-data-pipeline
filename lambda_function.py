"""S3 adapter for the small-file sales pipeline (lab, maximum 5 MiB)."""
import csv
import hashlib
import io
import json
import logging
import os
from urllib.parse import unquote_plus

from src.pipeline import CLEAN_FIELDS, REJECT_FIELDS, group_revenue, process_csv, summarize

MAX_BYTES = 5 * 1024 * 1024
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def get_s3_client():
    # Lambda's Python runtime includes boto3; local tests inject a fake S3 client.
    import boto3
    return boto3.client("s3")


def csv_bytes(rows, fields):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def inputs_from_event(event):
    if not isinstance(event, dict):
        raise ValueError("Expected a JSON object")
    if event.get("Event") == "s3:TestEvent":
        return []
    if "Records" in event:
        inputs = []
        for record in event["Records"]:
            if (record.get("eventSource") == "aws:s3" and
                    record.get("eventName", "").startswith("ObjectCreated:")):
                obj = record["s3"]["object"]
                inputs.append((record["s3"]["bucket"]["name"],
                               unquote_plus(obj["key"]), obj.get("eTag")))
        return inputs
    if "bucket" in event and "key" in event:
        # Manual events use the literal key, not URL encoding.
        return [(event["bucket"], event["key"], None)]
    raise ValueError("Use an S3 ObjectCreated event or a manual {bucket, key} event")


def process_object(s3, bucket, key, expected_etag=None):
    request = {"Bucket": bucket, "Key": key}
    if expected_etag:
        request["IfMatch"] = '"' + expected_etag.strip('"') + '"'
    try:
        response = s3.get_object(**request)
    except Exception as error:
        # An older notification must not process a replacement object.
        code = getattr(error, "response", {}).get("Error", {}).get("Code")
        if expected_etag and code in ("PreconditionFailed", "412"):
            LOGGER.info("Skipping stale notification for %s", key)
            return {"status": "skipped_stale_event", "source_key": key}
        raise
    body = response["Body"]
    try:
        if response["ContentLength"] > MAX_BYTES:
            raise ValueError("Input exceeds the demo limit of 5 MiB")
        payload = body.read(MAX_BYTES + 1)
        if len(payload) > MAX_BYTES:
            raise ValueError("Input exceeds the demo limit of 5 MiB")
    finally:
        body.close()
    clean, rejected = process_csv(payload.decode("utf-8-sig"))

    # Same source key always writes the same output keys. Do not use a random run
    # folder: S3 notifications may be delivered more than once.
    file_id = hashlib.sha256(key.encode("utf-8")).hexdigest()
    destinations = {
        "cleaned": f"processed/cleaned/{file_id}.csv",
        "rejected": f"rejected/{file_id}.csv",
        "summary": f"processed/summaries/{file_id}.json",
    }
    outputs = [(destinations["cleaned"], csv_bytes(clean, CLEAN_FIELDS), "text/csv"),
               (destinations["rejected"], csv_bytes(rejected, REJECT_FIELDS), "text/csv")]
    for field, name in [("order_date", "date"), ("product", "product"),
                        ("category", "category"), ("city", "city")]:
        output_key = f"processed/aggregates/{name}/{file_id}.csv"
        destinations[f"revenue_by_{name}"] = output_key
        fields = [field, "valid_lines", "total_quantity", "revenue"]
        outputs.append((output_key, csv_bytes(group_revenue(clean, field), fields), "text/csv"))

    summary = summarize(clean, rejected)
    summary.update({"status": "processed", "source_bucket": bucket, "source_key": key,
                    "source_etag": response.get("ETag", "").strip('"'),
                    "outputs": destinations})
    # Write the summary last. Multi-object output is not a transaction.
    outputs.append((destinations["summary"],
                    json.dumps(summary, ensure_ascii=False, indent=2).encode("utf-8"),
                    "application/json"))
    for output_key, content, content_type in outputs:
        s3.put_object(Bucket=bucket, Key=output_key, Body=content,
                      ContentType=content_type + "; charset=utf-8")
    LOGGER.info("Processed source=%s valid=%s rejected=%s revenue=%s %s", key,
                summary["valid_rows"], summary["rejected_rows"],
                summary["total_revenue"], summary["currency"])
    return summary


def lambda_handler(event, context):
    allowed_bucket = os.environ.get("SALES_BUCKET")
    if not allowed_bucket:
        raise ValueError("Set the SALES_BUCKET environment variable")
    results, s3 = [], None
    for bucket, key, etag in inputs_from_event(event):
        if bucket != allowed_bucket:
            raise ValueError("Event bucket does not match SALES_BUCKET")
        if not isinstance(key, str):
            raise ValueError("Object key must be text")
        if not key.startswith("raw/") or not key.endswith(".csv"):
            results.append({"status": "skipped_non_raw_csv", "source_key": key})
            continue
        if s3 is None:
            s3 = get_s3_client()
        results.append(process_object(s3, bucket, key, etag))
    return {"results": results}
