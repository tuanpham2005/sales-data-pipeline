import csv
import io
import unittest
from pathlib import Path
from src.pipeline import FIELDS, group_revenue, process_csv, summarize

SAMPLE = Path(__file__).resolve().parents[1] / "data/raw/sales_sample.csv"


def fixture(**changes):
    row = dict(zip(FIELDS, ["A", "1", "2026-09-01", "Pen", "Stationery",
                            "2", "0.10", "Ha Noi", "VND"]))
    row.update(changes)
    text = io.StringIO()
    writer = csv.DictWriter(text, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerow(row)
    return text.getvalue()


class PipelineTests(unittest.TestCase):
    def test_sample_totals_and_daily_reconciliation(self):
        clean, rejected = process_csv(SAMPLE.read_text(encoding="utf-8-sig"))
        result = summarize(clean, rejected)
        self.assertEqual((result["input_rows"], result["valid_rows"],
                          result["rejected_rows"]), (10, 6, 4))
        self.assertEqual(result["distinct_valid_orders"], 5)
        self.assertEqual(result["total_quantity"], 17)
        self.assertEqual(result["total_revenue"], "670000.00")
        self.assertEqual([r["revenue"] for r in group_revenue(clean, "order_date")],
                         ["150000.00", "340000.00", "180000.00"])

    def test_money_is_exact(self):
        clean, rejected = process_csv(fixture())
        self.assertEqual(clean[0]["total_amount"], "0.20")
        self.assertFalse(rejected)

    def test_invalid_values(self):
        for changes in [dict(quantity="-1"), dict(quantity="1.5"),
                        dict(unit_price="NaN"), dict(unit_price="Infinity"),
                        dict(unit_price="abc"), dict(unit_price="-2"),
                        dict(unit_price="0.001"), dict(order_date="2026-02-30"),
                        dict(product=" "), dict(currency="USD")]:
            with self.subTest(changes=changes):
                clean, rejected = process_csv(fixture(**changes))
                self.assertFalse(clean)
                self.assertEqual(len(rejected), 1)

    def test_duplicate_line_rejected(self):
        text = fixture()
        clean, rejected = process_csv(text + text.splitlines()[1] + "\n")
        self.assertEqual(len(clean), 1)
        self.assertEqual(rejected[0]["error"], "duplicate_order_line")

    def test_two_lines_of_same_order_allowed(self):
        text = fixture()
        other = fixture(line_id="2").splitlines()[1]
        clean, rejected = process_csv(text + other + "\n")
        self.assertEqual(len(clean), 2)
        self.assertFalse(rejected)

    def test_extra_column_preserved_in_rejection(self):
        text = fixture().rstrip() + ",unexpected\n"
        clean, rejected = process_csv(text)
        self.assertFalse(clean)
        self.assertIn("unexpected", rejected[0]["raw_record"])

    def test_schema_error_is_file_error(self):
        with self.assertRaises(ValueError):
            process_csv("order_id,quantity\nA,2\n")

    def test_bom_and_reordered_header(self):
        text = io.StringIO()
        rows = list(csv.reader(io.StringIO(fixture())))
        csv.writer(text).writerows([list(reversed(row)) for row in rows])
        clean, rejected = process_csv("\ufeff" + text.getvalue())
        self.assertEqual(len(clean), 1)
        self.assertFalse(rejected)


if __name__ == "__main__":
    unittest.main()
