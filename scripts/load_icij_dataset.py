"""
Downloads the real ICIJ Offshore Leaks Database CSV export into data/raw/icij_offshore_leaks/.

NOT YET RUNNABLE AS-IS: the exact subsample scope (which jurisdiction, which leak —
Panama/Paradise/Pandora/Bahamas/Offshore Leaks — and which entity/officer subset) is
not yet decided (see ARCHITECTURE.md open question). Decide that first and record it
in docs/data-provenance.md, then fill in the download + filter logic below.

Full dataset download: https://offshoreleaks.icij.org/pages/database (archive.zip)
"""
import sys

def main() -> None:
    print(
        "Subsample scope not yet decided — see docs/data-provenance.md.\n"
        "1. Pick a jurisdiction/firm subset (recommend: filter nodes-officers.csv / "
        "nodes-entities.csv by a single country_codes value to keep the demo graph "
        "small, e.g. a few hundred nodes).\n"
        "2. Download the archive from https://offshoreleaks.icij.org/pages/database\n"
        "3. Fill in the real download + filter logic here, then remove this message."
    )
    sys.exit(1)

if __name__ == "__main__":
    main()
