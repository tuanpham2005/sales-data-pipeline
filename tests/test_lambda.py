import csv
import io
import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch

import lambda_function as adapter

BUCKET = "tuan-fcj-sales-pipeline-20261006-a7k9"
SAMPLE = (Path(__file__).resolve().parents[1] / "data/raw/sales_sample.csv").read_bytes()


class FakeS3:
    def __init__(self, payload=SAMPLE):
        self.payload = payload
        self.objects = {}
        self.requests = []

    def get_object(self, **kwargs):
        self.requests.append(kwargs)
        self.body = io.BytesIO(self.payload)
        return {"Body": self.body, "ContentLength": len(self.payload), "ETag": '"sample"'}

    def put_object(self, **kwargs):
        self.objects[kwargs["Key"]] = kwargs["Body"]


def s3_event(key="raw/sales_sample.csv", etag="sample"):
    return {"Records": [{"eventSource": "aws:s3", "eventName": "ObjectCreated:Put",
                         "s3": {"bucket": {"name": BUCKET},
                                "object": {"key": key, "eTag": etag}}}]}


class LambdaTests(unittest.TestCase):
    def invoke(self, event, s3):
        with patch.dict(os.environ, {"SALES_BUCKET": BUCKET}), \
                patch.object(adapter, "get_s3_client", return_value=s3):
            return adapter.lambda_handler(event, None)

    def test_manual_event_writes_seven_outputs_with_expected_totals(self):
        s3 = FakeS3()
        result = self.invoke({"bucket": BUCKET, "key": "raw/sales_sample.csv"}, s3)["results"][0]
        self.assertEqual((result["valid_rows"], result["rejected_rows"]), (6, 4))
        self.assertEqual(result["total_revenue"], "670000.00")
        self.assertEqual(len(s3.objects), 7)
        self.assertIn("revenue_by_category", result["outputs"])
        cleaned = list(csv.DictReader(io.StringIO(s3.objects[result["outputs"]["cleaned"]].decode())))
        self.assertEqual(len(cleaned), 6)
        summary = json.loads(s3.objects[result["outputs"]["summary"]])
        self.assertEqual(summary["source_key"], "raw/sales_sample.csv")
        self.assertTrue(s3.body.closed)

    def test_repeat_event_does_not_append_new_output_objects(self):
        s3 = FakeS3()
        self.invoke(s3_event(), s3)
        previous = dict(s3.objects)
        self.invoke(s3_event(), s3)
        self.assertEqual(s3.objects, previous)

    def test_s3_event_decodes_key_and_uses_etag(self):
        s3 = FakeS3()
        result = self.invoke(s3_event("raw/sales+sample%2B1.csv"), s3)
        self.assertEqual(result["results"][0]["source_key"], "raw/sales sample+1.csv")
        self.assertEqual(s3.requests[0]["IfMatch"], '"sample"')

    def test_output_notification_is_ignored_without_s3_access(self):
        s3 = FakeS3()
        result = self.invoke(s3_event("processed/cleaned/test.csv"), s3)
        self.assertEqual(result["results"][0]["status"], "skipped_non_raw_csv")
        self.assertFalse(s3.requests)
        self.assertFalse(s3.objects)

    def test_wrong_bucket_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "does not match"):
            self.invoke({"bucket": "other-bucket", "key": "raw/sales.csv"}, FakeS3())

    def test_oversized_file_is_rejected_and_closed(self):
        s3 = FakeS3(b"a" * (adapter.MAX_BYTES + 1))
        with self.assertRaisesRegex(ValueError, "5 MiB"):
            self.invoke({"bucket": BUCKET, "key": "raw/sales.csv"}, s3)
        self.assertFalse(s3.objects)
        self.assertTrue(s3.body.closed)

    def test_invalid_schema_creates_no_output(self):
        s3 = FakeS3(b"wrong,header\n1,2\n")
        with self.assertRaises(ValueError):
            self.invoke({"bucket": BUCKET, "key": "raw/sales.csv"}, s3)
        self.assertFalse(s3.objects)

    def test_missing_environment_variable_fails(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "SALES_BUCKET"):
                adapter.lambda_handler({}, None)

    def test_s3_configuration_test_event_is_noop(self):
        s3 = FakeS3()
        self.assertEqual(self.invoke({"Event": "s3:TestEvent"}, s3), {"results": []})
        self.assertFalse(s3.requests)

    def test_stale_event_is_skipped(self):
        class StaleEventError(Exception):
            response = {"Error": {"Code": "PreconditionFailed"}}
        s3 = FakeS3()
        with patch.object(s3, "get_object", side_effect=StaleEventError()):
            result = self.invoke(s3_event(), s3)
        self.assertEqual(result["results"][0]["status"], "skipped_stale_event")
        self.assertFalse(s3.objects)


if __name__ == "__main__":
    unittest.main()
