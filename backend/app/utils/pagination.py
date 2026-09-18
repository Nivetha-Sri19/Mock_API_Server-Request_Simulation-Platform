from math import ceil

def calculate_offset(page: int, page_size: int) -> int:
    return (page - 1) * page_size

def calculate_total_pages(total: int, page_size: int) -> int:
    return ceil(total / page_size) if total else 0
