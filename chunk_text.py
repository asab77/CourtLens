"""Split extracted Supreme Court text into token-sized JSONL chunks."""

import json
import re
from pathlib import Path

import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter


PROJECT_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
CHUNKS_DIR = PROJECT_DIR / "data" / "chunks"

CHUNK_SIZE = 1_200
CHUNK_OVERLAP = 200
SEPARATORS = ["\n\n", "\n", ". ", " "]
ENCODING_NAME = "cl100k_base"
PAGE_MARKER = re.compile(r"^===== PAGE (\d+) =====$", re.MULTILINE)


def read_extracted_case(text_path: Path) -> tuple[str, str, str, str]:
    """Return case metadata and the page-marked case text."""
    text = text_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    expected_headers = (
        "Case name: ",
        "Source file: ",
        "Descriptive source file: ",
        "Total PDF pages: ",
    )
    if len(lines) < 4 or any(
        not lines[index].startswith(header)
        for index, header in enumerate(expected_headers)
    ):
        raise ValueError("missing expected extraction metadata headers")

    case_name = lines[0].removeprefix("Case name: ").strip()
    original_source_file = lines[1].removeprefix("Source file: ").strip()
    source_file = lines[2].removeprefix("Descriptive source file: ").strip()
    body = "".join(lines[4:]).strip()
    return case_name, source_file, original_source_file, body


def page_spans(text: str) -> list[tuple[int, int, int]]:
    """Map character ranges in the extracted text to PDF page numbers."""
    markers = list(PAGE_MARKER.finditer(text))
    spans = []

    for index, marker in enumerate(markers):
        start = marker.start()
        end = markers[index + 1].start() if index + 1 < len(markers) else len(text)
        spans.append((start, end, int(marker.group(1))))

    return spans


def pages_for_chunk(
    chunk_start: int, chunk_text: str, spans: list[tuple[int, int, int]]
) -> tuple[int | None, int | None]:
    """Find the first and last PDF pages touched by a chunk."""
    chunk_end = chunk_start + len(chunk_text)
    pages = [
        page_number
        for page_start, page_end, page_number in spans
        if chunk_start < page_end and chunk_end > page_start
    ]
    return (min(pages), max(pages)) if pages else (None, None)


def main() -> None:
    """Chunk every extracted text file into a matching JSONL file."""
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    text_paths = sorted(PROCESSED_DIR.glob("*.txt"))

    if not text_paths:
        print(f"No extracted text files found in {PROCESSED_DIR}")
        return

    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name=ENCODING_NAME,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=SEPARATORS,
        keep_separator=True,
        add_start_index=True,
    )
    encoding = tiktoken.get_encoding(ENCODING_NAME)

    print(f"Found {len(text_paths)} extracted case(s).")

    for text_path in text_paths:
        try:
            case_name, source_file, original_source_file, case_text = read_extracted_case(
                text_path
            )
            spans = page_spans(case_text)
            documents = splitter.create_documents([case_text])
            output_path = CHUNKS_DIR / f"{text_path.stem}.jsonl"

            with output_path.open("w", encoding="utf-8") as output_file:
                for chunk_index, document in enumerate(documents):
                    start_index = document.metadata["start_index"]
                    page_start, page_end = pages_for_chunk(
                        start_index, document.page_content, spans
                    )
                    record = {
                        "text": document.page_content,
                        "metadata": {
                            "case_name": case_name,
                            "source_file": source_file,
                            "original_source_file": original_source_file,
                            "page_start": page_start,
                            "page_end": page_end,
                            "chunk_index": chunk_index,
                            "token_count": len(encoding.encode(document.page_content)),
                        },
                    }
                    output_file.write(json.dumps(record, ensure_ascii=False) + "\n")

            print(f"Chunked {text_path.name} -> {output_path.name}: {len(documents)} chunks")
        except Exception as error:
            print(f"Could not chunk {text_path.name}: {error}")


if __name__ == "__main__":
    main()
