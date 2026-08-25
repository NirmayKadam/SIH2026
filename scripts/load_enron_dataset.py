"""
Downloads the real Enron email corpus into data/raw/enron_emails/.

NOT YET RUNNABLE AS-IS: exact custodian/date-range subsample not yet decided — see
docs/data-provenance.md. The classic dataset is available from CMU:
https://www.cs.cmu.edu/~enron/
"""
import sys

def main() -> None:
    print(
        "Subsample scope not yet decided — see docs/data-provenance.md.\n"
        "1. Pick a small set of custodians (recommend: a known cluster of executives "
        "with dense mutual email traffic, to keep the demo graph readable).\n"
        "2. Download from https://www.cs.cmu.edu/~enron/\n"
        "3. Fill in the real download + filter logic here, then remove this message."
    )
    sys.exit(1)

if __name__ == "__main__":
    main()
