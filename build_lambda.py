"""Build the lab deployment ZIP with the handler at the archive root."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parent


def main():
    target = ROOT / "dist/fcj-sales-lambda.zip"
    target.parent.mkdir(exist_ok=True)
    sources = [ROOT / "lambda_function.py", ROOT / "src/__init__.py", ROOT / "src/pipeline.py"]
    with ZipFile(target, "w", compression=ZIP_DEFLATED) as archive:
        for path in sources:
            archive.write(path, path.relative_to(ROOT).as_posix())
    print(f"Ready: {target}")
    print("Handler: lambda_function.lambda_handler")
    print("SDK: lab uses boto3 included in the Lambda Python runtime")


if __name__ == "__main__":
    main()
