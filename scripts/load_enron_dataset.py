"""
Loads real Enron email files from data/raw/enron_emails/ (or data/samples/enron_sample.mbox)
into the system via the REST ingestion API.

Prerequisites:
  1. Download the Enron Maildir from https://www.cs.cmu.edu/~enron/
  2. Extract to data/raw/enron_emails/
  3. Ensure the API is running (make up)

Usage:
  python scripts/load_enron_dataset.py [path_to_enron_data]
  
If no path is given, defaults to data/raw/enron_emails/ or falls back to
data/samples/enron_sample.mbox for demo purposes.
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

# Default custodians with dense executive email traffic for demo-sized graphs
DEFAULT_CUSTODIANS = ["lay-k", "skilling-j", "delainey-d", "dasovich-j", "kaminski-v"]
MAX_EMAILS_PER_CUSTODIAN = 50


def ingest_file(source_path: str) -> dict:
    """Call the ingestion API to submit a single source file."""
    payload = json.dumps({
        "source_type": "enron_emails",
        "source_path": source_path,
    }).encode("utf-8")

    request = Request(
        INGEST_ENDPOINT,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode())
    except HTTPError as exc:
        print(f"  HTTP {exc.code}: {exc.read().decode()[:200]}")
        return {"error": str(exc)}
    except URLError as exc:
        print(f"  Connection error: {exc.reason}")
        return {"error": str(exc)}


def collect_email_files(base_path: Path) -> list[Path]:
    """Collect email files from maildir structure or mbox files."""
    files: list[Path] = []

    if base_path.is_file():
        if base_path.suffix in (".mbox", ".txt", ".eml"):
            return [base_path]
        print(f"Unsupported file type: {base_path.suffix}")
        return []

    if not base_path.is_dir():
        print(f"Path not found: {base_path}")
        return []

    # Check if this is a standard Enron maildir with custodian folders
    custodian_dirs = [
        d for d in base_path.iterdir()
        if d.is_dir() and d.name in DEFAULT_CUSTODIANS
    ]

    if custodian_dirs:
        print(f"Found {len(custodian_dirs)} target custodian directories")
        for custodian_dir in custodian_dirs:
            count = 0
            for email_file in sorted(custodian_dir.rglob("*")):
                if email_file.is_file() and not email_file.name.startswith("."):
                    files.append(email_file)
                    count += 1
                    if count >= MAX_EMAILS_PER_CUSTODIAN:
                        break
            print(f"  {custodian_dir.name}: {count} emails")
    else:
        # Flat directory or non-standard structure — take all email-like files
        for email_file in sorted(base_path.rglob("*")):
            if email_file.is_file() and email_file.suffix in ("", ".txt", ".eml", ".mbox"):
                files.append(email_file)
                if len(files) >= MAX_EMAILS_PER_CUSTODIAN * len(DEFAULT_CUSTODIANS):
                    break

    return files


def main() -> None:
    if len(sys.argv) > 1:
        source_path = Path(sys.argv[1])
    else:
        # Try raw data first, fall back to sample
        raw_path = Path("data/raw/enron_emails")
        sample_path = Path("data/samples/enron_sample.mbox")

        if raw_path.exists() and any(raw_path.iterdir()):
            source_path = raw_path
        elif sample_path.exists():
            print("No raw Enron data found. Using sample mbox for demo.")
            source_path = sample_path
        else:
            print(
                "No Enron data found.\n"
                "Download from: https://www.cs.cmu.edu/~enron/\n"
                "Extract to: data/raw/enron_emails/\n"
                "Or provide a path: python scripts/load_enron_dataset.py /path/to/emails"
            )
            sys.exit(1)

    print(f"Scanning: {source_path}")
    files = collect_email_files(source_path)

    if not files:
        print("No email files found.")
        sys.exit(1)

    print(f"Found {len(files)} email files to ingest")
    print(f"API endpoint: {INGEST_ENDPOINT}")
    print()

    success_count = 0
    error_count = 0

    for idx, email_file in enumerate(files, 1):
        print(f"[{idx}/{len(files)}] Ingesting: {email_file.name} ... ", end="", flush=True)
        result = ingest_file(str(email_file))

        if "error" in result:
            error_count += 1
            print("FAILED")
        else:
            success_count += 1
            job_id = result.get("job_id", "unknown")
            print(f"OK (job: {job_id})")

        # Rate limit: avoid overwhelming the API and Gemini free tier
        time.sleep(1.0)

    print()
    print(f"Done. {success_count} succeeded, {error_count} failed out of {len(files)} total.")


if __name__ == "__main__":
    main()
