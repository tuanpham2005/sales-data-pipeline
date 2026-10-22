let
    CsvPath = "D:\AWS\sales-data-pipeline\dashboard\data\sales_from_athena.csv",
    Source = Csv.Document(File.Contents(CsvPath),
        [Delimiter=",", Columns=11, Encoding=65001, QuoteStyle=QuoteStyle.Csv, ExtraValues=ExtraValues.Error]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Expected = {"order_id", "line_id", "order_date", "product", "category", "quantity",
                "unit_price", "city", "currency", "total_amount", "source_path"},
    SchemaChecked = if Table.ColumnNames(Headers) <> Expected
                    then error "CSV schema differs from the verified Athena export" else Headers,
    Typed = Table.TransformColumnTypes(SchemaChecked,
        {{"order_id", type text}, {"line_id", type text}, {"order_date", type date},
         {"product", type text}, {"category", type text}, {"quantity", Int64.Type},
         {"unit_price", Currency.Type}, {"city", type text}, {"currency", type text},
         {"total_amount", Currency.Type}, {"source_path", type text}}, "en-US"),
    Errors = Table.SelectRowsWithErrors(Typed),
    Result = if Table.RowCount(Errors) > 0
             then error "Conversion error: inspect the CSV; do not replace errors with null" else Typed
in
    Result
