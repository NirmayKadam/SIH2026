"""
Loads the subsampled India ICIJ dataset into the pipeline.
Requires the API to be running (e.g. via `make up` or `uvicorn`).
"""
import sys
import time
import requests
from pathlib import Path

def main() -> None:
    subsampled_dir = Path("data/raw/icij_offshore_leaks/subsampled")
    
    if not subsampled_dir.exists() or not list(subsampled_dir.glob("*.csv")):
        print(f"Subsampled data not found at {subsampled_dir}.")
        print("Please run `python scripts/subsample_icij.py` first.")
        sys.exit(1)
        
    print(f"Submitting ICIJ subsample from {subsampled_dir} to ingestion API...")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/ingestion/documents",
            json={
                "source_type": "icij_offshore_leaks",
                "source_path": f"/app/{subsampled_dir.as_posix()}"
            },
            timeout=10
        )
        response.raise_for_status()
        
        job_data = response.json()
        job_id = job_data.get("job_id")
        print(f"Success! Job queued with ID: {job_id}")
        
        print("\nChecking status...")
        for _ in range(30):
            status_resp = requests.get(f"http://localhost:8000/api/ingestion/documents/{job_id}", timeout=5)
            if status_resp.ok:
                status_data = status_resp.json()
                status = status_data.get("status")
                print(f"Status: {status}")
                if status in ["parsed", "failed"]:
                    if status == "failed":
                        print(f"Error: {status_data.get('error_message')}")
                    break
            time.sleep(2)
            
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        print("Make sure the API is running (e.g., `make up`)")
        sys.exit(1)

if __name__ == "__main__":
    main()
