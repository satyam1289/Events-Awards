
from extractor import EventExtractor

extractor = EventExtractor()

test_cases = [
    ("No specific event identified", "This is an article about nothing."),
    ("Unknown Summit", "Some text."),
    ("N/A", "More text."),
    ("FICCI Tech Summit 2026", "Big event in Delhi.")
]

for title, content in test_cases:
    result = extractor.extract_event_info(title, content)
    is_event = result.get('is_event', False)
    name = result.get('event_name', 'N/A')
    print(f"Title: {title} | Result: {'ACCEPTED' if is_event else 'REJECTED'} | Extracted: {name}")
