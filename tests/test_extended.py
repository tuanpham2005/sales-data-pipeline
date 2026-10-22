"""Business boundaries and CSV interoperability; no AWS calls."""
import csv
import io
import json
import unittest
from decimal import Decimal
from unittest.mock import patch

import lambda_function as adapter
from src.pipeline import CLEAN_FIELDS, group_revenue, process_csv, summarize
from tests.test_pipeline import fixture
from tests.test_lambda import BUCKET, SAMPLE, FakeS3, s3_event


class CsvAndBusinessTests(unittest.TestCase):
    def test_quoted_comma_quotes_and_vietnamese_roundtrip(self):
        product = 'Bút, "đỏ" – Việt Nam'
        clean, rejected = process_csv(fixture(product=product, city="TP. Hồ Chí Minh"))
        self.assertFalse(rejected)
        output = adapter.csv_bytes(clean, CLEAN_FIELDS).decode("utf-8")
        self.assertEqual(list(csv.DictReader(io.StringIO(output)))[0]["product"], product)

    def test_embedded_newline_is_rejected_for_athena_csv(self):
        clean, rejected = process_csv(fixture(product="Product\nsecond line"))
        self.assertFalse(clean)
        self.assertIn("embedded_newline", rejected[0]["error"])

    def test_all_required_fields(self):
        for field in CLEAN_FIELDS[:-1]:
            with self.subTest(field=field):
                clean, rejected = process_csv(fixture(**{field: " "}))
                self.assertEqual((len(clean), len(rejected)), (0, 1))

    def test_price_three_places_including_zero_is_rejected(self):
        clean, rejected = process_csv(fixture(unit_price="1.230"))
        self.assertFalse(clean)
        self.assertEqual(rejected[0]["error"], "unit_price_more_than_two_decimal_places")

    def test_numeric_limits_and_zero_price(self):
        clean, rejected = process_csv(fixture(quantity="1000000", unit_price="1000000000000.00"))
        self.assertFalse(rejected)
        self.assertEqual(clean[0]["total_amount"], "1000000000000000000.00")
        for change in [dict(quantity="1000001"), dict(quantity="0"), dict(unit_price="1000000000000.01")]:
            self.assertTrue(process_csv(fixture(**change))[1])
        self.assertEqual(process_csv(fixture(unit_price="0.00"))[0][0]["total_amount"], "0.00")

    def test_every_dimension_reconciles(self):
        clean, rejected = process_csv(SAMPLE.decode("utf-8-sig"))
        for field in ["order_date", "product", "category", "city"]:
            with self.subTest(field=field):
                total = sum((Decimal(row["revenue"]) for row in group_revenue(clean, field)), Decimal(0))
                self.assertEqual(total, Decimal("670000.00"))

    def test_duplicate_transactions_across_files_are_not_deduplicated(self):
        first, _ = process_csv(fixture())
        second, _ = process_csv(fixture())
        self.assertEqual(summarize(first + second, [])['total_revenue'], "0.40")
        self.assertEqual(summarize(first + second, [])['distinct_valid_orders'], 1)

    def test_duplicate_header_and_malformed_csv_fail_file(self):
        with self.assertRaises(ValueError):
            process_csv("order_id,order_id\nA,A\n")
        with self.assertRaises(csv.Error):
            process_csv(fixture().splitlines()[0] + '\n"unterminated')


class LambdaBoundaryTests(unittest.TestCase):
    def invoke(self, s3, event=None):
        with patch.dict("os.environ", {"SALES_BUCKET": BUCKET}), patch.object(adapter, "get_s3_client", return_value=s3):
            return adapter.lambda_handler(event or s3_event(), None)

    def test_same_key_updated_content_replaces_output(self):
        s3 = FakeS3()
        self.invoke(s3)
        old_keys = set(s3.objects)
        rows = list(csv.DictReader(io.StringIO(SAMPLE.decode("utf-8-sig"))))
        rows[0]["quantity"] = "3"
        source = io.StringIO(newline="")
        writer = csv.DictWriter(source, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
        s3.payload = source.getvalue().encode("utf-8")
        response = self.invoke(s3)["results"][0]
        self.assertEqual(set(s3.objects), old_keys)
        self.assertEqual(response["total_revenue"], "720000.00")

    def test_actual_body_limit_even_if_content_length_is_wrong(self):
        s3 = FakeS3(b"a" * (adapter.MAX_BYTES + 1))
        original = s3.get_object
        def misleading(**kwargs):
            response = original(**kwargs); response["ContentLength"] = 1; return response
        s3.get_object = misleading
        with self.assertRaisesRegex(ValueError, "5 MiB"):
            self.invoke(s3)
        self.assertTrue(s3.body.closed)

    def test_bad_utf8_writes_nothing(self):
        s3 = FakeS3(b"\xff\xfe")
        with self.assertRaises(UnicodeDecodeError):
            self.invoke(s3)
        self.assertFalse(s3.objects)
        self.assertTrue(s3.body.closed)

    def test_partial_write_is_not_an_atomic_transaction(self):
        s3 = FakeS3()
        original = s3.put_object
        def fail_on_second(**kwargs):
            if s3.objects:
                raise RuntimeError("simulated storage failure")
            return original(**kwargs)
        s3.put_object = fail_on_second
        with self.assertRaisesRegex(RuntimeError, "storage failure"):
            self.invoke(s3)
        self.assertEqual(len(s3.objects), 1)
        self.assertFalse(any(key.endswith(".json") for key in s3.objects))


if __name__ == "__main__":
    unittest.main()
