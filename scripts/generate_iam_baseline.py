"""Generate audit candidates with AWS IAM Policy Autopilot; never attach them."""
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    uvx = shutil.which("uvx") or r"C:/Users/ASUS/AppData/Local/Microsoft/WinGet/Links/uvx.exe"
    output = ROOT / "iam/generated-candidates"; output.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "DISABLE_IAM_POLICY_AUTOPILOT_TELEMETRY": "true"}
    for name, source, hints in [("lambda", ROOT / "lambda_function.py", ["s3"]),
                                ("analytics", ROOT / "scripts/analytics.py", ["athena", "sts"])]:
        command = [uvx, "iam-policy-autopilot@latest", "generate-policies", str(source),
                   "--region", "ap-southeast-2", "--account", "988079434036", "--service-hints", *hints, "--pretty"]
        response = subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8", env=env)
        raw = response.stdout
        decoded, _ = json.JSONDecoder().raw_decode(raw[raw.index('{'):])
        (output / f"{name}.json").write_text(json.dumps(decoded, indent=2), encoding="utf-8")
        print(name + ": audit candidate saved; NOT applied")


if __name__ == "__main__":
    main()
