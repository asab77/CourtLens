"""Extract page-by-page text from Supreme Court case PDFs."""

import re
import unicodedata
from pathlib import Path

from pypdf import PdfReader


PROJECT_DIR = Path(__file__).resolve().parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"

REPORTS_TITLE = re.compile(
    r"^U\.S\. Reports:\s*(.+?),\s*\d+\s+U\.S\.", re.IGNORECASE
)
CAPTION = re.compile(r"^(.+?)\s+v\.\s+(.+?)(?:,|$)", re.IGNORECASE)


def normalize_case_name(name: str) -> str:
    """Normalize spacing and the versus abbreviation in a case caption."""
    name = " ".join(name.split())
    name = re.sub(r"\s+v\.\s+", " v. ", name, flags=re.IGNORECASE)
    return name.strip()


def case_name_from_reader(reader: PdfReader) -> str:
    """Read a reliable short case name from metadata or the first page caption."""
    title = (reader.metadata.title or "").strip() if reader.metadata else ""
    title_match = REPORTS_TITLE.match(title)
    if title_match:
        return normalize_case_name(title_match.group(1))

    first_page = reader.pages[0].extract_text() or ""
    caption_match = next(
        (
            CAPTION.match(" ".join(line.split()))
            for line in first_page.splitlines()
            if " v. " in line.lower()
        ),
        None,
    )
    if not caption_match:
        raise ValueError("could not determine a reliable case name")

    petitioner = re.sub(
        r"\s+(?:et\s+al\.?|petitioner(?:s)?)$",
        "",
        caption_match.group(1),
        flags=re.IGNORECASE,
    )
    respondent = caption_match.group(2)
    return normalize_case_name(f"{petitioner.title()} v. {respondent.title()}")


def safe_case_stem(case_name: str) -> str:
    """Convert a human-readable case name to a filesystem-safe stem."""
    ascii_name = unicodedata.normalize("NFKD", case_name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", ascii_name.lower()).strip("_")


def extract_pdf(
    pdf_path: Path, output_path: Path, reader: PdfReader, case_name: str, safe_stem: str
) -> tuple[int, int]:
    """Extract one PDF and return its page count and empty-page count."""
    reader = PdfReader(pdf_path)
    empty_pages = 0

    with output_path.open("w", encoding="utf-8") as output_file:
        output_file.write(f"Case name: {case_name}\n")
        output_file.write(f"Source file: {pdf_path.name}\n")
        output_file.write(f"Descriptive source file: {safe_stem}.pdf\n")
        output_file.write(f"Total PDF pages: {len(reader.pages)}\n")

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            text = text.strip()

            if not text:
                empty_pages += 1

            output_file.write(f"\n\n===== PAGE {page_number} =====\n\n")
            output_file.write(text)

    return len(reader.pages), empty_pages


def main() -> None:
    """Extract every PDF in data/raw into a matching text file."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    pdf_paths = sorted(RAW_DIR.glob("*.pdf"))

    if not pdf_paths:
        print(f"No PDF files found in {RAW_DIR}")
        return

    print(f"Found {len(pdf_paths)} PDF file(s).")

    for pdf_path in pdf_paths:
        try:
            reader = PdfReader(pdf_path)
            case_name = case_name_from_reader(reader)
            safe_stem = safe_case_stem(case_name)
            output_path = PROCESSED_DIR / f"{safe_stem}.txt"
            page_count, empty_pages = extract_pdf(
                pdf_path, output_path, reader, case_name, safe_stem
            )
            warning = f" ({empty_pages} page(s) had no extractable text)" if empty_pages else ""
            print(
                f"Extracted {pdf_path.name} -> {output_path.name}: "
                f"{case_name}, {page_count} pages{warning}"
            )
        except Exception as error:
            print(f"Could not extract {pdf_path.name}: {error}")


if __name__ == "__main__":
    main()
