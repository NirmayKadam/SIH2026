"""
Places real, publicly published court judgment text/PDF files into
data/raw/court_judgments/.

NOT YET RUNNABLE AS-IS: which specific judgments to use is not yet decided. These
must be manually sourced from a public repository (e.g. indiankanoon.org publishes
judgments openly) and their exact citations recorded in docs/data-provenance.md —
this one isn't a bulk-downloadable dataset, so treat selection as a deliberate step,
not something to automate blindly.
"""
import sys

def main() -> None:
    print(
        "Judgment selection not yet decided — see docs/data-provenance.md.\n"
        "Manually source 3-5 real, public judgments relevant to organized crime, "
        "record their exact citations/URLs, place the text files in this folder, "
        "then remove this message and implement the parser adapter."
    )
    sys.exit(1)

if __name__ == "__main__":
    main()
