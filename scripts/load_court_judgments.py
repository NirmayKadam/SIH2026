"""
Loads real, publicly published court judgment files from data/raw/court_judgments/
(or data/samples/court_sample.pdf) into the system via the REST ingestion API.

Prerequisites:
  1. Source 3-5 real judgments from indiankanoon.org (organized crime, financial fraud)
  2. Save as PDF or TXT in data/raw/court_judgments/
  3. Record their exact citations/URLs in docs/data-provenance.md
  4. Ensure the API is running (make up)

Usage:
  python scripts/load_court_judgments.py [path_to_judgments_dir]
"""
import os
import sys
import time
import json
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

API_BASE = os.environ.get("API_BASE_URL", "http://localhost:8000")
INGEST_ENDPOINT = f"{API_BASE}/api/ingestion/documents"

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


def ingest_file(source_path: str) -> dict:
    """Call the ingestion API to submit a single court judgment file."""
    payload = json.dumps({
        "source_type": "court_judgment",
        "source_path": source_path,
    }).encode("utf-8")

    request = Request(
        INGEST_ENDPOINT,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode())
    except HTTPError as exc:
        print(f"  HTTP {exc.code}: {exc.read().decode()[:200]}")
        return {"error": str(exc)}
    except URLError as exc:
        print(f"  Connection error: {exc.reason}")
        return {"error": str(exc)}


def collect_judgment_files(base_path: Path) -> list[Path]:
    """Collect PDF/TXT court judgment files."""
    if base_path.is_file():
        if base_path.suffix in SUPPORTED_EXTENSIONS:
            return [base_path]
        print(f"Unsupported file type: {base_path.suffix}")
        return []

    if not base_path.is_dir():
        print(f"Path not found: {base_path}")
        return []

    files = sorted(
        f for f in base_path.rglob("*")
        if f.is_file() and f.suffix in SUPPORTED_EXTENSIONS
    )
    return files


def main() -> None:
    if len(sys.argv) > 1:
        source_path = Path(sys.argv[1])
    else:
        raw_path = Path("data/raw/court_judgments")
        sample_path = Path("data/samples/court_sample.pdf")

        if raw_path.exists() and any(raw_path.iterdir()):
            source_path = raw_path
        elif sample_path.exists():
            print("No raw court judgment data found. Using sample PDF for demo.")
            source_path = sample_path
        else:
            print(
                "No court judgment files found.\n"
                "Source real judgments from: https://indiankanoon.org\n"
                "Save to: data/raw/court_judgments/\n"
                "Or provide a path: python scripts/load_court_judgments.py /path/to/judgments"
            )
            sys.exit(1)

    print(f"Scanning: {source_path}")
    files = collect_judgment_files(source_path)

    if not files:
        print("No judgment files found.")
        sys.exit(1)

    print(f"Found {len(files)} judgment files to ingest")
    print(f"API endpoint: {INGEST_ENDPOINT}")
    print()

    success_count = 0
    error_count = 0

    for idx, judgment_file in enumerate(files, 1):
        print(f"[{idx}/{len(files)}] Ingesting: {judgment_file.name} ... ", end="", flush=True)
        result = ingest_file(str(judgment_file))

        if "error" in result:
            error_count += 1
            print("FAILED")
        else:
            success_count += 1
            job_id = result.get("job_id", "unknown")
            print(f"OK (job: {job_id})")

        # Court judgments are typically larger — give Gemini more time
        time.sleep(2.0)

    print()
    print(f"Done. {success_count} succeeded, {error_count} failed out of {len(files)} total.")


if __name__ == "__main__":
    main()
