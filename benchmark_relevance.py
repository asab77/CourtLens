"""Reusable page-range handling for CourtLens benchmark relevance labels."""


def normalize_relevant_ranges(value: list) -> list[list[int]]:
    """Normalize one range or a list of ranges into inclusive [start, end] pairs."""
    if (
        isinstance(value, list)
        and len(value) == 2
        and all(type(page) is int for page in value)
    ):
        ranges = [value]
    elif isinstance(value, list):
        ranges = value
    else:
        raise ValueError("Relevant ranges must be a page pair or a list of page pairs")

    if not ranges:
        raise ValueError("At least one relevant page range is required")
    normalized = []
    for interval in ranges:
        if (
            not isinstance(interval, list)
            or len(interval) != 2
            or any(type(page) is not int for page in interval)
            or interval[0] < 1
            or interval[0] > interval[1]
        ):
            raise ValueError(f"Invalid relevant page range: {interval!r}")
        normalized.append([interval[0], interval[1]])
    return normalized


def relevant_ranges_for_item(item: dict) -> list[list[int]]:
    """Read proposed relevant_ranges or the existing relevant_pages field."""
    if "relevant_ranges" in item:
        return normalize_relevant_ranges(item["relevant_ranges"])
    if "relevant_pages" in item:
        return normalize_relevant_ranges(item["relevant_pages"])
    raise ValueError("Benchmark item has no relevant_ranges or relevant_pages field")


def page_range_overlaps(
    page_start: int | None,
    page_end: int | None,
    relevant_ranges: list[list[int]],
) -> bool:
    """Return whether an inclusive chunk page span intersects any labeled range."""
    if page_start is None or page_end is None:
        return False
    return any(
        page_start <= range_end and page_end >= range_start
        for range_start, range_end in normalize_relevant_ranges(relevant_ranges)
    )
